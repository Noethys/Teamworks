#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
import six
from Ctrl import CTRL_Bouton_image
import wx.lib.mixins.listctrl  as  listmix
import sqlite3
from Utils import UTILS_Phonex
import string
import wx.lib.masked as masked
import FonctionsPerso
from Utils import UTILS_Adaptations


def PhonexPerso(word):
    resultat = UTILS_Phonex.phonex(word.encode("iso-8859-15"))
    return resultat


class Dialog(wx.Dialog):
    def __init__(self, parent, title, exportCP=None, exportVille=None, exportChamp=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.panel_base = wx.Panel(self, -1)
        self.parent = parent
        self.sizer_SaisieManuelle_staticbox = wx.StaticBox(self.panel_base, -1, "Saisie manuelle")
        self.sizer_Recherche_staticbox = wx.StaticBox(self.panel_base, -1, "Recherche")
        self.label_Intro = wx.StaticText(self.panel_base, -1, _(u"Ce logiciel possède une base de données de villes et de codes de la France."))
        self.exportCP = exportCP
        self.exportVille = exportVille
        
        # Création du ListCtrl
        listeChamps = [("cp", _(u"Code postal"), 80, True), ("ville", _(u"Nom de la ville"), 200, True), ]
        self.list_ctrl_1 = VirtualList(self.panel_base, "villes", listeChamps)
        self.list_ctrl_1.SetMinSize((20, 20)) 
        
        self.label_Recherche1 = wx.StaticText(self.panel_base, -1, "Saisissez ici un nom de ville \nou un code postal :")
        self.text_recherche_ville = wx.TextCtrl(self.panel_base, -1, "")
        self.bouton_Rechercher = wx.BitmapButton(self.panel_base, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Rechercher.png"), wx.BITMAP_TYPE_PNG))
        self.radio_box_recherche = wx.RadioBox(self.panel_base, -1, "Type de recherche", choices=[_(u"Une partie du nom"), _(u"Recherche phonétique")], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.bouton_AfficherTout = wx.BitmapButton(self.panel_base, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Reafficher_Liste.png"), wx.BITMAP_TYPE_PNG))
        self.label_SaisieManuelle = wx.StaticText(self.panel_base, -1, _(u"Vous pouvez ici saisir manuellement un nom de ville et son code postal. \n\nCeux-ci seront automatiquement insérés dans la fiche individuelle :"))
        self.label_SaisieCode = wx.StaticText(self.panel_base, -1, "Code postal :", style=wx.ALIGN_RIGHT)
        self.text_SaisieCode = masked.TextCtrl(self.panel_base, -1, "", style=wx.TE_CENTRE, mask = "#####")
        self.label_SaisieVille = wx.StaticText(self.panel_base, -1, "Nom de la ville :", style=wx.ALIGN_RIGHT)
        self.text_SaisieVille = wx.TextCtrl(self.panel_base, -1, "")
        self.bouton_Aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_Ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_Annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        if self.exportCP == None and self.exportVille == None:
            # Si la fenêtre n'a as été appelée à partir de la fiche individuelle, on désactive le sizer SAISIE MANUELLE
            self.sizer_SaisieManuelle_staticbox.Hide()
            self.sizer_SaisieManuelle.Hide(False)
            self.sizer_principal.Layout()

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("Gestion des villes")
        self.SetMinSize((540, 550))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.text_recherche_ville.SetToolTip(wx.ToolTip(_(u"Saisissez ici un nom de ville")))
        self.bouton_Rechercher.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer la recherche")))
        self.bouton_AfficherTout.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ré-afficher la liste complète")))
        self.bouton_AfficherTout.Hide()
        self.radio_box_recherche.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici un type de recherche")))
        self.radio_box_recherche.SetSelection(0)
        self.text_SaisieCode.SetMinSize((70, -1))
        self.text_SaisieCode.SetToolTip(wx.ToolTip(_(u"Saisissez ici un code postal")))
        self.text_SaisieVille.SetToolTip(wx.ToolTip(_(u"Saisissez ici un nom de ville")))
        self.bouton_Aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_Ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pou valider et fermer cette fenêtre")))
        self.bouton_Annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer cette fenêtre")))
        self.list_ctrl_1.SetMinSize((300, -1))
        # end wxGlade

        # Binds
        self.bouton_Rechercher.Bind(wx.EVT_BUTTON, self.OnBoutonRechercher)
        self.bouton_Ok.Bind(wx.EVT_BUTTON, self.OnBoutonOk)
        self.bouton_Annuler.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler)
        self.bouton_Aide.Bind(wx.EVT_BUTTON, self.OnBoutonAide)
        self.bouton_AfficherTout.Bind(wx.EVT_BUTTON, self.OnAfficherTout)

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_principal = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        sizer_Boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        sizer_SaisieManuelle = wx.StaticBoxSizer(self.sizer_SaisieManuelle_staticbox, wx.VERTICAL)
        grid_sizer_Saisie = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_Saisies = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        sizer_Recherche = wx.StaticBoxSizer(self.sizer_Recherche_staticbox, wx.VERTICAL)
        grid_sizer_Recherche = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_3 = wx.FlexGridSizer(rows=6, cols=1, vgap=10, hgap=10)
        sizer_principal.Add(self.label_Intro, 0, wx.ALL|wx.EXPAND, 10)
        grid_sizer_Recherche.Add(self.list_ctrl_1, 1, wx.EXPAND, 0)
        grid_sizer_3.Add(self.label_Recherche1, 0, 0, 0)
        grid_sizer_3.Add(self.text_recherche_ville, 0, wx.EXPAND, 0)
        grid_sizer_3.Add(self.bouton_Rechercher, 0, wx.EXPAND, 0)
        grid_sizer_3.Add(self.radio_box_recherche, 0, wx.EXPAND, 0)
        grid_sizer_3.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_3.Add(self.bouton_AfficherTout, 0, wx.EXPAND, 0)
        grid_sizer_3.AddGrowableRow(4)
        grid_sizer_Recherche.Add(grid_sizer_3, 1, wx.EXPAND, 0)
        grid_sizer_Recherche.AddGrowableRow(0)
        grid_sizer_Recherche.AddGrowableCol(0)
        sizer_Recherche.Add(grid_sizer_Recherche, 1, wx.ALL|wx.EXPAND, 10)
        sizer_principal.Add(sizer_Recherche, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_Saisie.Add(self.label_SaisieManuelle, 0, wx.EXPAND, 0)
        grid_sizer_Saisies.Add(self.label_SaisieCode, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_Saisies.Add(self.text_SaisieCode, 0, 0, 0)
        grid_sizer_Saisies.Add(self.label_SaisieVille, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_Saisies.Add(self.text_SaisieVille, 0, wx.EXPAND, 0)
        grid_sizer_Saisies.AddGrowableCol(3)
        grid_sizer_Saisie.Add(grid_sizer_Saisies, 1, wx.EXPAND, 0)
        grid_sizer_Saisie.AddGrowableRow(0)
        grid_sizer_Saisie.AddGrowableCol(0)
        sizer_SaisieManuelle.Add(grid_sizer_Saisie, 1, wx.ALL|wx.EXPAND, 10)
        sizer_principal.Add(sizer_SaisieManuelle, 1, wx.ALL|wx.EXPAND, 10)
        sizer_Boutons.Add(self.bouton_Aide, 0, 0, 0)
        sizer_Boutons.Add((20, 20), 0, wx.EXPAND, 0)
        sizer_Boutons.Add(self.bouton_Ok, 0, 0, 0)
        sizer_Boutons.Add(self.bouton_Annuler, 0, 0, 0)
        sizer_Boutons.AddGrowableCol(1)
        sizer_principal.Add(sizer_Boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.panel_base.SetSizer(sizer_principal)
        sizer_principal.AddGrowableRow(1)
        sizer_principal.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()
        self.grid_sizer_3 = grid_sizer_3
        self.sizer_SaisieManuelle = sizer_SaisieManuelle
        self.sizer_principal = sizer_principal

    def OnBoutonRechercher(self, event):
        """ Bouton de lancement de la recherche """
        
        # Récupération du texte recherché
        textRecherche = self.text_recherche_ville.GetValue()
        
        # Appel de la fonction de recherche en fonction du type de recherche
        if self.radio_box_recherche.GetSelection() == 0:
            resultats = self.list_ctrl_1.RechercheBase(textRecherche)

        if self.radio_box_recherche.GetSelection() == 1:
            resultats = self.list_ctrl_1.RechercheSoundex(textRecherche)

        # Ceci permet de recalculer le sizer après l'affichage du bouton Afficher Tout
        if resultats == True and textRecherche != "":
            self.bouton_AfficherTout.Show()
            self.grid_sizer_3.Layout()
        elif resultats == False and textRecherche != "":
            self.bouton_AfficherTout.Show()
            self.grid_sizer_3.Layout()
            dlg = wx.MessageDialog(self, _(u"Aucun résultat n'a été trouvé pour votre recherche"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord saisir un nom de ville ou un code postal dans le champ de recherche."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
       
        event.Skip()

    def OnAfficherTout(self, event):
        self.bouton_AfficherTout.Hide()
        self.list_ctrl_1.comAfficherTout()
        event.Skip()

    def OnBoutonOk(self, event):
        if self.text_SaisieCode.GetValue().strip() != "" or self.text_SaisieVille.GetValue().strip() != "":
            export = self.ExportManuelVille()
            if export == True:
                self.EndModal(wx.ID_OK)
        else:
            self.EndModal(wx.ID_OK)

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Ladresse")

    def ExportManuelVille(self):
        """ Commande d'export manuel de ville + code postal """
        code = self.text_SaisieCode.GetValue()
        ville = self.text_SaisieVille.GetValue()

        # Validation des champs de saisie manuelle
        if code.strip() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous avez saisi un nom de ville. Vous devez également saisir un code postal pour exporter cette ville"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        if ville.strip() == "":
            dlg = wx.MessageDialog(self, _(u"Vous avez saisi un code postal. Vous devez également saisir un un nom de ville pour exporter cette ville"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Export dans la Fiche individuelle
        self.parent.autoComplete = False
        if self.exportCP == "text_cp_naiss" and self.exportVille == "text_ville_naiss":
            self.parent.text_cp_naiss.SetValue(code)
            self.parent.text_ville_naiss.SetValue(ville.upper())
        elif self.exportCP == "text_cp" and self.exportVille == "text_ville":
            self.parent.text_cp.SetValue(code)
            self.parent.text_ville.SetValue(ville.upper())
        self.parent.autoComplete = True
    
        return True

    def ExportListeVille(self, code, ville):
        # Export d'une ville de la liste dans la Fiche individuelle
        self.parent.autoComplete = False
        if self.exportCP == "text_cp_naiss" and self.exportVille == "text_ville_naiss":
            self.parent.text_cp_naiss.SetValue(str(code))
            self.parent.text_ville_naiss.SetValue(ville.upper())
        elif self.exportCP == "text_cp" and self.exportVille == "text_ville":
            self.parent.text_cp.SetValue(str(code))
            self.parent.text_ville.SetValue(ville.upper())
        self.parent.autoComplete = True

        dlg = wx.MessageDialog(self, _(u"La ville ") + ville + _(u" a bien été importée dans la fiche individuelle."), "Information", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        

class VirtualList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent, nomTable, listeChamps):
        wx.ListCtrl.__init__( self, parent, -1, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        self.nomTable = nomTable
        self.listeChamps = listeChamps
        self.criteres = ""
        self.parent = parent

        # Initialisation des images
        tailleIcones = 16
        self.il = wx.ImageList(tailleIcones, tailleIcones)
        a={"sm_up":"GO_UP","sm_dn":"GO_DOWN","w_idx":"WARNING","e_idx":"ERROR","i_idx":"QUESTION"}
        for k,v in list(a.items()):
            img = getattr(wx, "ART_%s" % v)
            if 'phoenix' in wx.PlatformInfo:
                setattr(self, k, self.il.Add(wx.ArtProvider.GetBitmap(img, wx.ART_TOOLBAR, (16, 16))))
            else:
                setattr(self, k, self.il.Add(wx.ArtProvider_GetBitmap(img, wx.ART_TOOLBAR, (16,16))))
        self.imgTriAz= self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Tri_az.png"), wx.BITMAP_TYPE_PNG))
        self.imgTriZa= self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Tri_za.png"), wx.BITMAP_TYPE_PNG))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        #adding some attributes (colourful background for each item rows)
        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour("#EEF4FB") # Vert = #F0FBED

        # Création de la liste des colonnes initiale
        self.CreationListeColonnes()

        # Remplissage du ListCtrl
        self.InitListCtrl()

    def InitListCtrl(self):
        
        # Récupération des données dans la base de données
        self.ImportationDonnees(self.nomTable, self.listeChamps)
        
        # Création des colonnes
        x = 0
        for colonne in self.listeColonnes:
            for champ in self.listeChamps:
                if colonne == champ[0] :
                    self.InsertColumn(x, champ[1])
                    self.SetColumnWidth(x, champ[2])
            x += 1

        #These two should probably be passed to init more cleanly
        #setting the numbers of items = number of elements in the dictionary
        self.itemDataMap = self.donnees
        self.itemIndexMap = list(self.donnees.keys())
        self.SetItemCount(self.nbreLignes)
        
        #mixins
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

        #sort by genre (column 2), A->Z ascending order (1)
        self.SortListItems(1, 1)

        #events
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def CreationListeColonnes(self):
        # Récupération des champs à partir de listeChamps
        self.listeColonnes = []
        for champ in self.listeChamps:
            if champ[3] == True :
                self.listeColonnes.append(champ[0])

    def ImportationDonnees(self, nomTable, listeChamps):

        # listeChamps = nom Champ | Titre colonne | Taille colonne | Affichée (True/False)

        # Liste des champs pour la requete de récupération
        champs = ""
        for champ in self.listeColonnes:
            champs = champs + champ + ", "
        champs = champs[:-2]
        
        # Requete de récupération des données
        con = sqlite3.connect(Chemins.GetStaticPath("Databases/Villes.db3"))
        con.create_function("phonex", 1, PhonexPerso)
        cur = con.cursor()
        cur.execute("SELECT %s FROM %s %s" % (champs, nomTable, self.criteres))
        listeValeurs = cur.fetchall()
        con.close()

        self.nbreColonnes = len(self.listeColonnes)
        self.nbreLignes = len(listeValeurs)

        # Création du dictionnaire de données
        self.donnees = self.listeEnDict(listeValeurs)



    def MAJListeCtrl(self):
        self.ClearAll()
        self.InitListCtrl()
        self.resizeLastColumn(0)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

    def listeEnDict(self, liste):
        dictio = {}
        x = 1
        for ligne in liste:
            index = x # Donne un entier comme clé
            dictio[index] = ligne
            x += 1
        return dictio
    
    def OnColClick(self,event):
        item = self.GetColumn(event.GetColumn())
        event.Skip()

    def OnItemSelected(self, event):
        self.currentItem = event.m_itemIndex
        #print ('OnItemSelected: "%s", "%s", "%s"' %(self.currentItem, self.GetItemText(self.currentItem), self.getColumnText(self.currentItem, 1)))
        event.Skip()
        
    def OnItemActivated(self, event):
        self.currentItem = event.m_itemIndex
        #print ("OnItemActivated: %s\nTopItem: %s\n" % (self.GetItemText(self.currentItem), self.GetTopItem()))
        event.Skip()
        
    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    def OnItemDeselected(self, evt):
        print(("OnItemDeselected: %s" % evt.m_itemIndex))


    #---------------------------------------------------
    # These methods are callbacks for implementing the
    # "virtualness" of the list...

    def OnGetItemText(self, item, col):
        """ Affichage des valeurs dans chaque case du ListCtrl """
        index=self.itemIndexMap[item]
        valeur = six.text_type(self.itemDataMap[index][col])
        return valeur

    def OnGetItemImage(self, item):
        """ Affichage des images en début de ligne """
        return -1

    def OnGetItemAttr(self, item):
        """ Application d'une couleur de fond pour une ligne sur deux """
        # Création d'une ligne de couleur 1 ligne sur 2
        if item % 2 == 1:
            return self.attr1
        else:
            return None
       
    #---------------------------------------------------
    # Matt C, 2006/02/22
    # Here's a better SortItems() method --
    # the ColumnSorterMixin.__ColumnSorter() method already handles the ascending/descending,
    # and it knows to sort on another column if the chosen columns have the same value.

    def SortItems(self,sorter=FonctionsPerso.cmp):
        items = list(self.itemDataMap.keys())
        items = FonctionsPerso.SortItems(items, sorter)
        self.itemIndexMap = items
        # redraw the list
        self.Refresh()

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.imgTriAz, self.imgTriZa)

    # ---------------------------------------------------
    # FONCTIONS DE RECHERCHE

    def comAfficherTout(self):
        self.criteres = ""
        self.MAJListeCtrl()
        
    def RechercheBase(self, textRecherche):
        """ Recherche dans la liste sur tout ou une partie du nom """
        textRecherche = textRecherche.encode("iso-8859-15")
        table = string.maketrans('àâäãéèêëìîïòôöõùûüñÀÂÄÃÉÈÊËÌÎÏÒÔÖÕÙÛÜÑ', 'AAAAEEEEIIIOOOOUUUNAAAAEEEEIIIOOOOUUUN');
        textRecherche = textRecherche.translate(table)
        textRecherche = textRecherche.upper()

        # Boite de dialogue de recherche
        if textRecherche != "":
            # Recherche dans tous les champs affichés
            strCriteres = "WHERE "
            for champ in self.listeColonnes :
                strCriteres = strCriteres + champ + " like '%" + textRecherche + "%' or "

            # MàJ du listCtrl
            self.criteres = strCriteres[:-4]
            self.MAJListeCtrl()

        # Renvoie si résultats ou non
        if self.GetItemCount() == 0:
            resultats = False
        else:
            resultats = True
        return resultats

    def RechercheSoundex(self, textRecherche):
        """ Recherche dans la liste avec méthode SOUNDEX"""
        textRecherche = textRecherche.encode("iso-8859-15")
        table = string.maketrans('àâäãéèêëìîïòôöõùûüñÀÂÄÃÉÈÊËÌÎÏÒÔÖÕÙÛÜÑ', 'AAAAEEEEIIIOOOOUUUNAAAAEEEEIIIOOOOUUUN');
        textRecherche = textRecherche.translate(table)
        textRecherche = textRecherche.upper()

        # Boite de dialogue de recherche
        if textRecherche != "":
            self.criteres = "WHERE phonex(ville)=phonex('%s')" % textRecherche
            self.MAJListeCtrl()

        # Renvoie si résultats ou non
        if self.GetItemCount() == 0:
            resultats = False
        else:
            resultats = True

        return resultats

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel du ListCtrl."""       
        if self.GetFirstSelected() == -1:
            return False
        index = self.GetFirstSelected()
        self.selection = (int(self.getColumnText(index, 0)), self.getColumnText(index, 1))
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item avec image
        item = wx.MenuItem(menuPop, 10, _(u"Insérer cette ville dans la fiche individuelle"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        
        self.Bind(wx.EVT_MENU, self.Menu_Inserer, id=10)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Menu_Inserer(self, event):
        code = self.selection[0]
        ville = self.selection[1]

        grandParent = self.GetGrandParent()
        grandParent.ExportListeVille(code, ville)
        
            

if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None, "")
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
