#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import GestionDB
import sys
import Config_ChampsContrats


class Page(wx.Panel):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.sizer_champs_staticbox = wx.StaticBox(self, -1, u"Champs")
        self.label_titre = wx.StaticText(self, -1, u"3. Choix des champs personnalisés")
        self.label_intro = wx.StaticText(self, -1, u"Sélectionnez les données personnalisées que vous souhaitez ajouter aux\ncaractérististiques de ce contrat :")
        self.listCtrl_champs = ListCtrl_champs(self)
        self.bouton_champs = wx.Button(self, -1, "...", style=wx.BU_EXACTFIT)

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonChamps, self.bouton_champs)

    def __set_properties(self):
        self.label_titre.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.bouton_champs.SetToolTipString(u"Cliquez ici pour créer, modifier ou supprimer des champs personnalisés.")
        self.bouton_champs.SetMinSize((20, 20))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        sizer_champs = wx.StaticBoxSizer(self.sizer_champs_staticbox, wx.VERTICAL)
        grid_sizer_champs = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_titre, 0, 0, 0)
        grid_sizer_base.Add(self.label_intro, 0, wx.LEFT, 20)
        grid_sizer_champs.Add(self.listCtrl_champs, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_champs, 0, 0, 0)
        grid_sizer_champs.Add(grid_sizer_boutons, 1, 0, 0)
        grid_sizer_champs.AddGrowableRow(0)
        grid_sizer_champs.AddGrowableCol(0)
        sizer_champs.Add(grid_sizer_champs, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(sizer_champs, 1, wx.LEFT|wx.EXPAND, 20)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)

    def OnBoutonChamps(self, event):
        frmChamps = Config_ChampsContrats.MyFrame(self, "")
        frmChamps.Show()

    def MAJ_ListCtrl(self):
        self.listCtrl_champs.MAJListeCtrl()   
                
    def Validation(self):
        
        # Vérifie qu'un champ a été coché   
        if len(self.listCtrl_champs.selections) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun champ. \n\nVoulez-vous tout de même continuer ?",  u"Vérification", wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_NO :
                dlg.Destroy() 
                return False
            dlg.Destroy()
        
        # Mise à jour du listCtrl_Champs de la page suivante
        self.GetGrandParent().page5.MAJ_panelDefilant()
        
        return True
    
    


# -----------------------------------------------------------------------------------------------------------------------------------------------------------

class ListCtrl_champs(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.LC_NO_HEADER)
        CheckListCtrlMixin.__init__(self)
        self.parent = parent
            
        self.Remplissage()
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
##        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
##        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)


    def Remplissage(self):
        
        listeIDchamps = self.GetGrandParent().GetParent().dictChamps.keys()
        if len(listeIDchamps) != 0 :
            self.selections = listeIDchamps
        else:
            self.selections = []
            
        """ Remplissage du listCtrl """
        self.dictChamps = self.Import_Donnees()
        self.ClearAll()
        # Création des colonnes
        self.InsertColumn(0, "Nom")
##        self.InsertColumn(1, "Description")

        # Remplissage avec les valeurs
        for key, valeurs in self.dictChamps.iteritems():
                index = self.InsertStringItem(sys.maxint, valeurs[1])
##                self.SetStringItem(index, 1, valeurs[1])
                self.SetItemData(index, key)
                # Sélection
                if key in self.selections :
                    self.CheckItem(index)                    

        # Ajustement tailles colonnes
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
##        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)

        # Tri
        self.SortItems(self.columnSorter)

    def MAJListeCtrl(self):
        self.ClearAll()
        self.Remplissage()
        
    def Import_Donnees(self):
        """ Importe les champs de la base de données """
        
        req = """
            SELECT IDchamp, nom, description, mot_cle, defaut, exemple
            FROM contrats_champs 
            ORDER BY nom;
        """
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Transformation de la liste en dict
        dictChamps = {}
        for ID, nom, description, mot_cle, defaut, exemple in listeDonnees :
            dictChamps[ID] = (ID, nom, description, mot_cle, defaut, exemple)
        
        return dictChamps
        
                
    def columnSorter(self, key1, key2):
        item1 = self.dictChamps[key1][1] 
        item2 = self.dictChamps[key2][1] 
        if item1 == item2:  
            return 0
        elif item1 < item2: 
            return -1
        else:           
            return 1

    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)

    # this is called by the base class when an item is checked/unchecked
    def OnCheckItem(self, index, flag):
        ID = self.GetItemData(index)
        if flag:
            if ID not in self.selections :
                self.selections.append(ID)            
        else:
            if ID in self.selections :
                self.selections.remove(ID) 
    
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """

        # Recherche et sélection de l'item pointé avec la souris
        index = self.GetFirstSelected()
        if index == -1 :
            mode = "selected"
        else:
            mode = "deselected"
        
        # Création du menu contextuel
        menuPop = wx.Menu()
        
        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, u"Créer un nouveau champ")
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        if mode == "deselected" :
            
            menuPop.AppendSeparator()
            
            # Item Modifier
            item = wx.MenuItem(menuPop, 20, u"Modifier")
            bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Menu_Modifier, id=20)

            # Item Supprimer
            item = wx.MenuItem(menuPop, 30, u"Supprimer")
            bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def Menu_Ajouter(self, event):
        self.parent.OnBoutonAjouter(None)
        
    def Menu_Modifier(self, event):
        self.parent.OnBoutonModifier(None)

    def Menu_Supprimer(self, event):
        self.parent.OnBoutonSupprimer(None)
        
        
        