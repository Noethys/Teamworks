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
import GestionDB
import FonctionsPerso
from Dlg import DLG_Saisie_pays
from Utils import UTILS_Adaptations


class Panel(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, style=wx.TAB_TRAVERSAL, name="panel_config_pays")
        
        self.barreTitre = FonctionsPerso.BarreTitre(self,  _(u"Les pays et nationalités"), u"")
        texteIntro = _(u"Vous pouvez ici ajouter, modifier ou supprimer des pays et les nationalités correspondantes :")
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        
        self.listCtrl = ListCtrl(self)
        self.listCtrl.SetMinSize((20, 20)) 
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Aide.png"), wx.BITMAP_TYPE_ANY))
        if parent.GetName() != "treebook_configuration" :
            self.bouton_aide.Show(False)


        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        self.bouton_modifier.Enable(False)
        self.bouton_supprimer.Enable(False)
        
    def __set_properties(self):
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un nouveau pays")))
        self.bouton_ajouter.SetSize(self.bouton_ajouter.GetBestSize())
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier un pays sélectionné dans la liste")))
        self.bouton_modifier.SetSize(self.bouton_modifier.GetBestSize())
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le pays sélectionné dans la liste")))
        self.bouton_supprimer.SetSize(self.bouton_supprimer.GetBestSize())
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base2 = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=10)
        grid_sizer_base.Add(self.barreTitre, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.label_introduction, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        grid_sizer_base2.Add(self.listCtrl, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add((5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.AddGrowableRow(3)
        grid_sizer_base2.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        grid_sizer_base2.AddGrowableRow(0)
        grid_sizer_base2.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_base2, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
##        grid_sizer_base.Add(self.label_conclusion, 0, 0, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.SetAutoLayout(True)
        self.Layout()

    def OnBoutonAjouter(self, event):
        self.Ajouter()

    def Ajouter(self):
        dlg = DLG_Saisie_pays.Dialog(self, "", IDpays=0)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonModifier(self, event):
        self.Modifier()

    def Modifier(self):
        index = self.listCtrl.GetFirstSelected()
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un pays à modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        ID = int(self.listCtrl.GetItem(index, 0).GetText())
        dlg = DLG_Saisie_pays.Dialog(self, "", IDpays=ID)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonSupprimer(self, event):
        self.Supprimer()

    def Supprimer(self):
        index = self.listCtrl.GetFirstSelected()
        
        # Vérifie qu'un item a bien été sélectionné
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un pays à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Vérifie que cet item n'est attribuée à aucune personne
        nbreTitulaires = int(self.listCtrl.GetItem(index, 4).GetText())
        if nbreTitulaires != 0:
            dlg = wx.MessageDialog(self, _(u"Pour des raisons de sécurité des données, vous ne pouvez pas supprimer un pays qui a déjà été attribué à des personnes.\n\nSi vous voulez vraiment le supprimer, vous devez d'abord supprimer ce pays sur chaque fiche individuelle concernée."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        
        ID = int(self.listCtrl.GetItem(index, 0).GetText())

        # Vérifie que ce n'est pas un pays prédéfini
        if ID <= 230 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer un pays pré-enregistré."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return      
        
        # Demande de confirmation
        Nom = self.listCtrl.GetItem(index, 2).GetText()
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer ce pays ? \n\n> ") + Nom))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return

        # Suppression du type de pièce
        DB = GestionDB.DB()
        DB.ReqDEL("pays", "IDpays", ID)
        DB.Close()

        # MàJ du ListCtrl
        self.listCtrl.MAJListeCtrl()
        
    def MAJ_ListCtrl(self):
        self.listCtrl.MAJListeCtrl() 
        
    def MAJpanel(self):
        self.listCtrl.MAJListeCtrl() 

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Lespaysetnationalits")



class ListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__( self, parent, -1, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        self.criteres = ""
        self.parent = parent
        self.selection = None

        #adding some attributes (colourful background for each item rows)
        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour("#EEF4FB") # Vert = #F0FBED

        # Remplissage du ListCtrl
        if self.GetGrandParent().GetName() != "treebook_configuration" :
            self.Remplissage()
        
        #events
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        #self.Bind(wx.EVT_SIZE, self.OnSize)

    def InitImageList(self):
        # Initialisation des images
        tailleIcones = 22
        self.il = wx.ImageList(tailleIcones, tailleIcones)
        # Images AZ et ZA
        self.imgTriAz= self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/22x22/Tri_az.png"), wx.BITMAP_TYPE_PNG))
        self.imgTriZa= self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/22x22/Tri_za.png"), wx.BITMAP_TYPE_PNG))
        # Images drapeaux
        self.imgDrapeauAutre = self.il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/Drapeaux/autre.png'), wx.BITMAP_TYPE_PNG))
        listeDrapeaux = self.Importation_drapeaux()
        for ID, code_drapeau in listeDrapeaux :
            setattr(self, "imgDrapeau" + str(ID), self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/Drapeaux/" + code_drapeau + ".png"), wx.BITMAP_TYPE_PNG)))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

    def OnSize(self, event):
        self.Refresh()
        event.Skip()

    def Remplissage(self):
        
        # Initialisation des images
        self.InitImageList()
        
        # Récupération des données dans la base de données
        self.dictNbTitulaires = self.GetNbTitulaires()
        self.Importation()
        
        # Création des colonnes
        self.nbreColonnes = 4
        self.InsertColumn(0, u"")
        self.SetColumnWidth(0, 29)
        self.InsertColumn(1, _(u"Code drapeau"))
        self.SetColumnWidth(1, 0)
        self.InsertColumn(2, _(u"Nom"))
        self.SetColumnWidth(2, 180)
        self.InsertColumn(3, _(u"Nationalité"))
        self.SetColumnWidth(3, 120)
        self.InsertColumn(4, _(u"Nb titulaires"))
        self.SetColumnWidth(4, 80)   


        #These two should probably be passed to init more cleanly
        #setting the numbers of items = number of elements in the dictionary
        self.itemDataMap = self.donnees
        self.itemIndexMap = list(self.donnees.keys())
        self.SetItemCount(self.nbreLignes)
        
        #mixins
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

        #sort by genre (column 1), A->Z ascending order (1)
        self.SortListItems(2, 1)

    def OnItemSelected(self, event):
        self.parent.bouton_modifier.Enable(True)
        self.parent.bouton_supprimer.Enable(True)
        if self.GetFirstSelected() == -1: return False
        index = self.GetFirstSelected()
        key = int(self.getColumnText(index, 0))
        self.selection = key
        
    def OnItemDeselected(self, event):
        self.parent.bouton_modifier.Enable(False)
        self.parent.bouton_supprimer.Enable(False)
        self.selection = None
        
    def SetSelection(self, IDpays=0) :
        self.selection = IDpays
        # Recherche de l'index du pays dans le listCtrl
        for key, valeurs in self.donnees.items() :
            if valeurs[0] == IDpays : 
                self.Focus(key-1)
                self.Select(key-1)
                return
        
    def Importation(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDpays, code_drapeau, nom, nationalite
        FROM pays ORDER BY nom; """
        DB.ExecuterReq(req)
        liste = DB.ResultatReq()
        DB.Close()
        self.nbreLignes = len(liste)
        # Création du dictionnaire de données
        self.donnees = self.listeEnDict(liste)

    def Importation_drapeaux(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDpays, code_drapeau
        FROM pays ORDER BY nom; """
        DB.ExecuterReq(req)
        listeDrapeaux = DB.ResultatReq()
        DB.Close()
        return listeDrapeaux
    
    def GetNbTitulaires(self):
        # Recherche le nombre de titulaires
        DB = GestionDB.DB()
        req = """SELECT pays_naiss, Count(IDpersonne) AS CompteDeIDpersonne
        FROM personnes 
        GROUP BY pays_naiss;
        """
        DB.ExecuterReq(req)
        listeNbTitulaires = DB.ResultatReq()
        DB.Close()
        # Transformation en dictionnaire
        dict = {}
        for IDpays, nbrePersonne in listeNbTitulaires :
            dict[IDpays] = nbrePersonne
        return dict
        
    def MAJListeCtrl(self):
        self.ClearAll()
        self.Remplissage()
        self.resizeLastColumn(0)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

    def listeEnDict(self, liste):
        dictio = {}
        x = 1
        for ligne in liste:
            index = x # Donne un entier comme clé
            # Rajoute le nb de titulaires
            ligne = list(ligne)
            ID = ligne[0]
            if ID in self.dictNbTitulaires:
                ligne.append(self.dictNbTitulaires[ID])
            else:
                ligne.append(0)
            dictio[index] = ligne
            x += 1
        return dictio
           
    def OnItemActivated(self, event):
        self.parent.Modifier()
        
    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

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
        index=self.itemIndexMap[item]
        IDvaleur =self.itemDataMap[index][0]
        try :
            imgDrapeau = eval("self.imgDrapeau" + str(IDvaleur))
        except :
            imgDrapeau = self.imgDrapeauAutre
        return imgDrapeau

    def OnGetItemAttr(self, item):
        """ Application d'une couleur de fond pour une ligne sur deux """
        # Création d'une ligne de couleur 1 ligne sur 2
        if item % 2 == 1:
            return self.attr1
        else:
            return None
       
    #-----------------------------------------------------------
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

    # ---------------------------------------------------------

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        
        if self.GetFirstSelected() == -1:
            return False
        index = self.GetFirstSelected()
        key = int(self.getColumnText(index, 0))
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Modifier, id=20)

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Menu_Ajouter(self, event):
        self.parent.Ajouter()
        
    def Menu_Modifier(self, event):
        self.parent.Modifier()

    def Menu_Supprimer(self, event):
        self.parent.Supprimer()



class Dialog(wx.Dialog):
    def __init__(self, parent, title="", IDpays=0, saisie=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.saisie = saisie
        self.panel_base = wx.Panel(self, -1)
        self.panel_contenu = Panel(self.panel_base)
        self.panel_contenu.barreTitre.Show(False)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)

        if IDpays != 0 : 
            self.panel_contenu.listCtrl.SetSelection(IDpays=IDpays)
        if self.saisie == "FicheIndiv_pays_naiss" : 
            self.panel_contenu.label_introduction.SetLabel(_(u"Sélectionnez un pays de naissance dans la liste :"))
        if self.saisie == "FicheIndiv_nationalite" : 
            self.panel_contenu.label_introduction.SetLabel(_(u"Sélectionnez une nationalité dans la liste :"))

    def __set_properties(self):
        self.SetTitle(_(u"Gestion des pays"))
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler et fermer")))
        self.SetMinSize((550, 500))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.ALL|wx.EXPAND, 0)
        sizer_pages.Add(self.panel_contenu, 1, wx.EXPAND | wx.TOP, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()
        self.sizer_pages = sizer_pages

    def Onbouton_aide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Lespaysetnationalits")
            
    def Onbouton_annuler(self, event):
        self.EndModal(wx.ID_CANCEL)
        
    def Onbouton_ok(self, event):
        # On vérifie qu'un pays a été sélectionné
        if self.saisie == "FicheIndiv_nationalite" or self.saisie == "FicheIndiv_nationalite" :
            if self.panel_contenu.listCtrl.selection == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un pays dans la liste."), "Erreur", wx.OK)  
                dlg.ShowModal()
                dlg.Destroy()
                return
        # Si c'est un sélection de nationalité, on vérifie qu'elle existe bien pour le pays sélectionné
        if self.saisie == "FicheIndiv_nationalite" :
            listCtrl = self.panel_contenu.listCtrl
            index = listCtrl.GetFirstSelected()
            nationalite = listCtrl.getColumnText(index, 3)
            if nationalite == "" :
                dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné un pays dont la nationalité n'a pas encore été précisée. \nCliquez sur le bouton 'Modifier' pour saisir le nom de la nationalité."), "Erreur", wx.OK)  
                dlg.ShowModal()
                dlg.Destroy()
                return
        # Si frame Creation_contrats ouverte, on met à jour le listCtrl Valeurs de points
        if self.saisie == "FicheIndiv_pays_naiss" : 
            self.parent.SetPaysNaiss(IDpays=self.panel_contenu.listCtrl.selection)
        if self.saisie == "FicheIndiv_nationalite" :
            self.parent.SetNationalite(IDpays=self.panel_contenu.listCtrl.selection)

        # Fermeture
        self.EndModal(wx.ID_OK)



if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()