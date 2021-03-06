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
import wx.lib.mixins.listctrl as listmix
import GestionDB
import FonctionsPerso
from Dlg import DLG_Saisie_champs_contrats
from Utils import UTILS_Adaptations

class Panel(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="panel_config_champsContrats", style=wx.TAB_TRAVERSAL)
        
        self.barreTitre = FonctionsPerso.BarreTitre(self,  _(u"Les champs de contrats"), u"")
        texteIntro = _(u"Vous pouvez ici cr�er, modifier ou supprimer les champs personnalis�s qui sont utilis�s dans la cr�ation des contrats.\nIls vous permettent de personnaliser librement vos contrats en fonction de vos besoins.")
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
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour cr�er un nouveau champ personnalis�")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le champ s�lectionn� dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le champ s�lectionn� dans la liste")))
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
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.SetAutoLayout(True)

    def OnBoutonAjouter(self, event):
        self.Ajouter()

    def Ajouter(self):
        dlg = DLG_Saisie_champs_contrats.Dialog(self, "", IDchamp=0)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonModifier(self, event):
        self.Modifier()

    def Modifier(self):
        index = self.listCtrl.GetFirstSelected()
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord s�lectionner un champ � modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        ID = int(self.listCtrl.GetItem(index, 0).GetText())
        
        # V�rifie que ce champ n'est pas attribu� � un contrat
        DB = GestionDB.DB()
        req = "SELECT IDval_champ FROM contrats_valchamps WHERE IDchamp=%d AND type='contrat'" % ID
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) != 0 :
            dlg = wx.MessageDialog(self, _(u"Ce champ a d�j� �t� attribu� � ") + str(len(listeDonnees)) + _(u" contrat(s). \nEtes-vous s�r de vouloir le modifier ?"), "Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            if reponse == wx.ID_NO:
                dlg.Destroy()
                return
            else: dlg.Destroy()
        
        # V�rifie que ce champ n'est pas attribu� � un mod�le de contrat
        DB = GestionDB.DB()
        req = "SELECT IDval_champ FROM contrats_valchamps WHERE IDchamp=%d AND type='modele'" % ID
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) != 0 :
            dlg = wx.MessageDialog(self, _(u"Ce champ a d�j� �t� attribu� � ") + str(len(listeDonnees)) + _(u" mod�le(s) de contrat.\nEtes-vous s�r de vouloir le modifier ?"), "Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            if reponse == wx.ID_NO:
                dlg.Destroy()
                return
            else: dlg.Destroy()
        
        dlg = DLG_Saisie_champs_contrats.Dialog(self, "", IDchamp=ID)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonSupprimer(self, event):
        self.Supprimer()

    def Supprimer(self):
        index = self.listCtrl.GetFirstSelected()

        # V�rifie qu'un item a bien �t� s�lectionn�
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord s�lectionner un champ � supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        ID = int(self.listCtrl.GetItem(index, 0).GetText())
        Nom = self.listCtrl.GetItem(index, 2).GetText()
        
        # V�rifie que ce champ n'est pas attribu� � un contrat
        DB = GestionDB.DB()
        req = "SELECT IDval_champ FROM contrats_valchamps WHERE IDchamp=%d AND type='contrat'" % ID
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) != 0 :
            dlg = wx.MessageDialog(self, _(u"Vous avez d�j� enregistr� ") + str(len(listeDonnees)) + _(u" contrat(s) avec ce champ. \nVous ne pouvez donc pas le supprimer."), "Information", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # V�rifie que ce champ n'est pas attribu� � un mod�le de contrat
        DB = GestionDB.DB()
        req = "SELECT IDval_champ FROM contrats_valchamps WHERE IDchamp=%d AND type='modele'" % ID
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) != 0 :
            dlg = wx.MessageDialog(self, _(u"Vous avez d�j� enregistr� ") + str(len(listeDonnees)) + _(u" mod�le(s) de contrat avec ce champ. \nVous ne pouvez donc pas le supprimer."), "Information", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer ce champ ? \n\n> ") + Nom))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Suppression du type de pi�ce
        DB = GestionDB.DB()
        DB.ReqDEL("contrats_champs", "IDchamp", ID)
        DB.Close()

        # M�J du ListCtrl
        self.listCtrl.MAJListeCtrl()
        
    def MAJ_ListCtrl(self):
        self.listCtrl.MAJListeCtrl()    

    def MAJpanel(self):
        self.listCtrl.MAJListeCtrl() 

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Leschampsdecontrats")


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
        self.imgActuel = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))
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
        
        # R�cup�ration des donn�es dans la base de donn�es
        self.Importation()
        
        # Cr�ation des colonnes
        self.nbreColonnes = 6
        self.InsertColumn(0, _(u"     ID"))
        self.SetColumnWidth(0, 0)
        self.InsertColumn(1, _(u"Nom"))
        self.SetColumnWidth(1, 190)  
        self.InsertColumn(2, _(u"Mot-cl�"))
        self.SetColumnWidth(2, 110)
        self.InsertColumn(3, _(u"Description"))
        self.SetColumnWidth(3, 200)        
        self.InsertColumn(4, _(u"Valeur par d�faut"))
        self.SetColumnWidth(4, 200)  
        self.InsertColumn(5, _(u"Valeur exemple"))
        self.SetColumnWidth(5, 200)

        
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
        # R�cup�ration des donn�es
        DB = GestionDB.DB()        
        req = """SELECT IDchamp, nom, mot_cle, description, defaut, exemple
        FROM contrats_champs ORDER BY nom; """
        DB.ExecuterReq(req)
        liste = DB.ResultatReq()
        DB.Close()
        self.nbreLignes = len(liste)
        # Cr�ation du dictionnaire de donn�es
        self.donnees = self.listeEnDict(liste)
            
    def MAJListeCtrl(self):
        self.ClearAll()
        self.Remplissage()
        self.resizeLastColumn(0)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

    def listeEnDict(self, liste):
        dictio = {}
        x = 1
        for ligne in liste:
            index = x # Donne un entier comme cl�
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
        """ Affichage des images en d�but de ligne """
        return -1

    def OnGetItemAttr(self, item):
        """ Application d'une couleur de fond pour une ligne sur deux """
        # Cr�ation d'une ligne de couleur 1 ligne sur 2
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
        
        # Cr�ation du menu contextuel
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
    def __init__(self, parent, title=""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        self.panel_base = wx.Panel(self, -1)
        self.panel_contenu = Panel(self.panel_base)
        self.panel_contenu.barreTitre.Show(False)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Fermer"), cheminImage=Chemins.GetStaticPath("Images/32x32/Fermer.png"))
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_fermer)

    def __set_properties(self):
        self.SetTitle(_(u"Gestion des champs personnalis�s de contrats"))
        self.SetMinSize((800, 600))
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler et fermer")))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.ALL|wx.EXPAND, 0)
        sizer_pages.Add(self.panel_contenu, 1, wx.EXPAND | wx.TOP, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
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
        UTILS_Aide.Aide("Leschampsdecontrats")

    def Onbouton_annuler(self, event):
        self.EndModal(wx.ID_CANCEL)


if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None, "")
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()