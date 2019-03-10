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
from Ctrl import CTRL_Bouton_image
import wx.lib.mixins.listctrl  as  listmix
import GestionDB
import FonctionsPerso
from Dlg import DLG_Saisie_emploi
from Utils import UTILS_Adaptations


class Panel(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="config_emploi", style=wx.TAB_TRAVERSAL)
        
        self.barreTitre = FonctionsPerso.BarreTitre(self,  _(u"Les offres d'emploi"), u"")
        texteIntro = _(u"Vous pouvez ici créer, modifier ou supprimer des offres d'emploi.")
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        self.listCtrl = ListCtrl(self)
        self.listCtrl.SetMinSize((20, 20)) 
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Aide.png"), wx.BITMAP_TYPE_ANY))
        if parent.GetName() != "treebook_configuration" :
            self.bouton_aide.Show(False)

##        self.label_conclusion = wx.StaticText(self, -1, "Remarques...")

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
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer une nouvelle offre d'emploi")))
        self.bouton_ajouter.SetSize(self.bouton_ajouter.GetBestSize())
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'offre d'emploi sélectionnée dans la liste")))
        self.bouton_modifier.SetSize(self.bouton_modifier.GetBestSize())
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'offre d'emploi sélectionnée dans la liste")))
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

    def OnBoutonAjouter(self, event):
        self.Ajouter()

    def Ajouter(self):
        frm = DLG_Saisie_emploi.MyFrame(self, IDemploi=None)
        frm.Show()
        
##        self.listCtrl.MAJListeCtrl()

    def OnBoutonModifier(self, event):
        self.Modifier()

    def Modifier(self):
        index = self.listCtrl.GetFirstSelected()
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une offre d'emploi à modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        varID = int(self.listCtrl.GetItem(index, 0).GetText())
        varNom = self.listCtrl.GetItem(index, 1).GetText()

        # Vérifie que l'offre n'est pas attribuée à une candidature
        DB = GestionDB.DB()
        req = "SELECT IDcandidature FROM candidatures WHERE IDemploi=%d;" % varID
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) != 0 :
            dlg = wx.MessageDialog(self, _(u"Cette offre d'emploi a déjà été attribué à ") + str(len(listeDonnees)) + _(u" candidature(s).\nEtes-vous sûr de vouloir la modifier ?"), "Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            if reponse == wx.ID_NO:
                dlg.Destroy()
                return
            else: dlg.Destroy()
        
        frm = DLG_Saisie_emploi.MyFrame(self, IDemploi=varID)
        frm.Show()
        
    def OnBoutonSupprimer(self, event):
        self.Supprimer()

    def Supprimer(self):
        index = self.listCtrl.GetFirstSelected()

        # Vérifie qu'un item a bien été sélectionné
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une offre d'emploi à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        ID = int(self.listCtrl.GetItem(index, 0).GetText())
        Nom = self.listCtrl.GetItem(index, 1).GetText()
        
        # Vérifie que cette offre d'emploi n'est pas attribuée à une candidature
        DB = GestionDB.DB()
        req = "SELECT IDcandidature FROM candidatures WHERE IDemploi=%d;" % ID
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) != 0 :
            dlg = wx.MessageDialog(self, _(u"Vous avez déjà enregistré ") + str(len(listeDonnees)) + _(u" candidature(s) rattachée(s) à cette offre d'emploi. \nVous ne pouvez donc pas la supprimer."), "Information", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer cette offre d'emploi ? \n\n> ") + Nom))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Suppression du type de pièce
        DB = GestionDB.DB()
        DB.ReqDEL("emplois", "IDemploi", ID)
        DB.ReqDEL("emplois_dispo", "IDemploi", ID)
        DB.ReqDEL("emplois_fonctions", "IDemploi", ID)
        DB.ReqDEL("emplois_affectations", "IDemploi", ID) 
        DB.ReqDEL("emplois_diffuseurs", "IDemploi", ID)

        # MàJ du ListCtrl
        self.listCtrl.MAJListeCtrl()

    def MAJpanel(self):
        self.listCtrl.MAJListeCtrl() 

    def OnBoutonAide(self, event):
##        affectationsPerso.Aide(38)
        dlg = wx.MessageDialog(self, _(u"L'aide du module Recrutement est en cours de rédaction.\nElle sera disponible lors d'une mise à jour ultérieure."), "Aide indisponible", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        

class ListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__( self, parent, -1, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        self.criteres = ""
        self.parent = parent

        # Initialisation des images
        tailleIcones = 16
        self.il = wx.ImageList(tailleIcones, tailleIcones)
        self.imgTriAz= self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Tri_az.png"), wx.BITMAP_TYPE_PNG))
        self.imgTriZa= self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Tri_za.png"), wx.BITMAP_TYPE_PNG))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

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

    def OnSize(self, event):
        self.Refresh()
        event.Skip()

    def Remplissage(self):
        
        # Récupération des données dans la base de données
        self.dictNbTitulaires = self.GetNbTitulaires()
        self.Importation()
        
        # Création des colonnes
        self.nbreColonnes = 3
        self.InsertColumn(0, _(u"     ID"))
        self.SetColumnWidth(0, 0)
        self.InsertColumn(1, _(u"Nom"))
        self.SetColumnWidth(1, 350)
        self.InsertColumn(2, _(u"Détail"))
        self.SetColumnWidth(2, 300)
        self.InsertColumn(3, _(u"Nb candidatures associées"))
        self.SetColumnWidth(3, 150)        

        #These two should probably be passed to init more cleanly
        #setting the numbers of items = number of elements in the dictionary
        self.itemDataMap = self.donnees
        self.itemIndexMap = list(self.donnees.keys())
        self.SetItemCount(self.nbreLignes)
        
        #mixins
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

        #sort by genre (column 1), A->Z ascending order (1)
        self.SortListItems(1, 1)

    def OnItemSelected(self, event):
        self.parent.bouton_modifier.Enable(True)
        self.parent.bouton_supprimer.Enable(True)
        
    def OnItemDeselected(self, event):
        self.parent.bouton_modifier.Enable(False)
        self.parent.bouton_supprimer.Enable(False)
        
    def Importation(self):
      
        # Récupération des données de la table
        DB = GestionDB.DB()
        req = """SELECT IDemploi, intitule, detail
        FROM emplois %s;
        """ % self.criteres
        DB.ExecuterReq(req)
        liste = DB.ResultatReq()
        DB.Close()

        self.nbreLignes = len(liste)

        # Création du dictionnaire de données
        self.donnees = self.listeEnDict(liste)

    def GetNbTitulaires(self):
        # Recherche le nombre de titulaires
        DB = GestionDB.DB()
        req = """SELECT IDcandidature, Count(IDemploi) AS CompteDeIDemploi
        FROM candidatures 
        GROUP BY IDemploi;
        """
        DB.ExecuterReq(req)
        listeNbTitulaires = DB.ResultatReq()
        DB.Close()
        # Transformation en dictionnaire
        dict = {}
        for IDemploi, nbrePersonne in listeNbTitulaires :
            dict[IDemploi] = nbrePersonne
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
        return -1

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




class MyFrame(wx.Frame):
    def __init__(self, parent, title="" ):
        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.MakeModal(True)
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
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.SetMinSize((700, 500))
        self.SetSize((700, 500))

    def __set_properties(self):
        self.SetTitle(_(u"Gestion des offres d'emploi"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler et fermer")))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        

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
        self.Layout()
        self.Centre()
        self.sizer_pages = sizer_pages

    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def Onbouton_aide(self, event):
##        FonctionsPerso.Aide(38)
        dlg = wx.MessageDialog(self, _(u"L'aide du module Recrutement est en cours de rédaction.\nElle sera disponible lors d'une mise à jour ultérieure."), "Aide indisponible", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
            
    def Onbouton_annuler(self, event):
        # Si frame Creation_contrats ouverte, on met à jour le listCtrl affectations
        self.MAJparents()
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()
        
    def Onbouton_ok(self, event):
        # Si frame Creation_contrats ouverte, on met à jour le listCtrl affectations
        self.MAJparents()
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()     

    def MAJparents(self):
        if FonctionsPerso.FrameOuverte("panel_candidature") != None :
            self.GetParent().MAJ_emplois()
##        if FonctionsPerso.FrameOuverte("frm_creation_modele_contrats") != None :
##            self.GetParent().MAJ_choice_Class()    
        
        
        
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()