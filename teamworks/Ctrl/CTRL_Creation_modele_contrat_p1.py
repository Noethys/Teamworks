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
import GestionDB
from Dlg import DLG_Config_classifications
from Dlg import DLG_Config_types_contrats
from wx.lib.mixins.listctrl import CheckListCtrlMixin
from Dlg import DLG_Config_champs_contrats
from Utils import UTILS_Adaptations


class Page(wx.Panel):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        
        self.dictTypes = {}
        
        self.sizer_champs_staticbox = wx.StaticBox(self, -1, _(u"Champs personnalisés"))
        self.sizer_caract_staticbox = wx.StaticBox(self, -1, _(u"Caractéristiques générales"))
        self.label_titre = wx.StaticText(self, -1, _(u"Création d'un modèle de contrat"))
        self.label_intro = wx.StaticText(self, -1, _(u"Saisissez les caractéristiques générales du contrat :"))
        
        self.label_type = wx.StaticText(self, -1, "Type de contrat :")
        self.choice_type = wx.Choice(self, -1, choices=[])
        self.Importation_Type()
        self.bouton_type = wx.Button(self, -1, "...", style=wx.BU_EXACTFIT)
        
        self.label_class = wx.StaticText(self, -1, "Classification :")
        self.choice_class = wx.Choice(self, -1, choices=[])
        self.Importation_classifications()
        self.bouton_class = wx.Button(self, -1, "...", style=wx.BU_EXACTFIT)

        self.listCtrl_champs = ListCtrl_champs(self)
        self.bouton_champs = wx.Button(self, -1, "...", style=wx.BU_EXACTFIT)
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonClassifications, self.bouton_class)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonType, self.bouton_type)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonChamps, self.bouton_champs)

        
        # Importation des données
        self.Importation()

    def __set_properties(self):
        self.label_titre.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.bouton_type.SetMinSize((20, 20))
        self.bouton_type.SetToolTip(wx.ToolTip("Cliquez ici pour ajouter, modifier ou supprimer des types de contrat"))
        self.bouton_class.SetMinSize((20, 20))
        self.bouton_class.SetToolTip(wx.ToolTip("Cliquez ici pour ajouter, modifier ou supprimer des classifications"))
        self.bouton_champs.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer, modifier ou supprimer des champs personnalisés.")))
        self.bouton_champs.SetMinSize((20, 20))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        sizer_champs = wx.StaticBoxSizer(self.sizer_champs_staticbox, wx.VERTICAL)
        grid_sizer_champs = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        sizer_caract = wx.StaticBoxSizer(self.sizer_caract_staticbox, wx.VERTICAL)
        grid_sizer_caract = wx.FlexGridSizer(rows=3, cols=3, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_titre, 0, 0, 0)
        grid_sizer_base.Add(self.label_intro, 0, wx.LEFT, 20)
        
        grid_sizer_caract.Add(self.label_type, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caract.Add(self.choice_type, 0, wx.EXPAND, 0)
        grid_sizer_caract.Add(self.bouton_type, 0, 0, 0)
        grid_sizer_caract.Add(self.label_class, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caract.Add(self.choice_class, 0, wx.EXPAND, 0)
        grid_sizer_caract.Add(self.bouton_class, 0, 0, 0)
        grid_sizer_caract.AddGrowableCol(1)
        sizer_caract.Add(grid_sizer_caract, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(sizer_caract, 1, wx.LEFT|wx.EXPAND, 20)
        
        grid_sizer_champs.Add(self.listCtrl_champs, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_champs, 0, 0, 0)
        grid_sizer_champs.Add(grid_sizer_boutons, 1, 0, 0)
        grid_sizer_champs.AddGrowableRow(0)
        grid_sizer_champs.AddGrowableCol(0)
        sizer_champs.Add(grid_sizer_champs, 1, wx.ALL|wx.EXPAND, 5)
        
        grid_sizer_base.Add(sizer_champs, 1, wx.LEFT|wx.EXPAND, 20)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(3)
        
    
    def Importation(self):
        """ Remplit les controles avec les données importées si c'est une modification """
        dictModeles = self.GetGrandParent().dictModeles
        
        # Controles Choice
        type = dictModeles["IDtype"]
        self.SelectChoice(self.choice_type, data=type )
        classification = dictModeles["IDclassification"]
        self.SelectChoice(self.choice_class, data=classification )
        
    def OnBoutonChamps(self, event):
        frmChamps = DLG_Config_champs_contrats.MyFrame(self, "")
        frmChamps.Show()
                
    def OnBoutonClassifications(self, event):
        frmClassification = DLG_Config_classifications.MyFrame(self, "")
        frmClassification.Show()
        
    def OnBoutonType(self, event):
        frmTypes = DLG_Config_types_contrats.MyFrame(self, "")
        frmTypes.Show()

    def MAJ_ListCtrl(self):
        self.listCtrl_champs.MAJListeCtrl()   
                
    def MAJ_choice_Class(self):
        self.Importation_classifications()
        
    def Importation_classifications(self):
        controle = self.choice_class
        selection = controle.GetSelection()
        IDselection = None
        if selection != -1 : IDselection = controle.GetClientData(selection)
        # Récupération des données
        DB = GestionDB.DB()
        req = """SELECT * FROM contrats_class """
        DB.ExecuterReq(req)
        liste = DB.ResultatReq()
        DB.Close()
        # Placement de la liste dans le Choice
        controle.Clear()
        x = 0
        for key, valeur in liste :
            controle.Append(valeur, key) 
            if IDselection == key : controle.SetSelection(x)
            x += 1
            
    def MAJ_choice_Type(self):
        self.Importation_Type()
        
    def Importation_Type(self):
        controle = self.choice_type
        selection = controle.GetSelection()
        IDselection = None
        if selection != -1 : IDselection = controle.GetClientData(selection)
        # Récupération des données
        DB = GestionDB.DB()
        req = """SELECT * FROM contrats_types """
        DB.ExecuterReq(req)
        liste = DB.ResultatReq()
        DB.Close()
        # Placement de la liste dans le Choice
        controle.Clear()
        self.dictTypes = {}
        x = 0
        for key, nom, nom_abrege, duree_indeterminee in liste :
            self.dictTypes[key] = duree_indeterminee
            controle.Append(nom, key) 
            if IDselection == key : controle.SetSelection(x)
            x += 1

    def GetChoiceData(self, controle):
        selection = controle.GetSelection()
        if selection != -1 : 
            IDselection = controle.GetClientData(selection)
        else:
            IDselection = None
        return IDselection

    def SelectChoice(self, controle, data):
        nbreItems = controle.GetCount()
        index = 0
        for item in range(nbreItems) :
            if controle.GetClientData(index) == data :
                controle.SetSelection(index)
                return
            index += 1
                    
                    
                        
    def Validation(self):
        
        # Récupération des valeurs saisies
        type = self.GetChoiceData(self.choice_type)
        classification = self.GetChoiceData(self.choice_class)
        
        # Vérifie que des valeurs ont été saisies
        if type == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un type de contrat dans la liste proposée."), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.choice_type.SetFocus()
            return False

        if classification == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner une classification dans la liste proposée."), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.choice_class.SetFocus()
            return False
        
        # Mémorisation des données
        dictModeles = self.GetGrandParent().dictModeles
        dictModeles["IDtype"] = type
        dictModeles["IDclassification"] = classification      
        
        # Vérifie qu'un champ a été coché   
        if len(self.listCtrl_champs.selections) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun champ. \n\nVoulez-vous tout de même continuer ?"),  _(u"Vérification"), wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_NO :
                dlg.Destroy() 
                return False
            dlg.Destroy()
        
        # Mise à jour du listCtrl_Champs de la page suivante
        self.GetGrandParent().page2.MAJ_panelDefilant()
        
        return True
    



# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class ListCtrl_champs(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.LC_NO_HEADER)
        CheckListCtrlMixin.__init__(self)
        self.parent = parent
        
        listeIDchamps = list(self.GetGrandParent().GetParent().dictChamps.keys())
        if len(listeIDchamps) != 0 :
            self.selections = listeIDchamps
        else:
            self.selections = []
            
        self.Remplissage()
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)


    def Remplissage(self):
        """ Remplissage du listCtrl """
        self.dictChamps = self.Import_Donnees()
        self.ClearAll()
        # Création des colonnes
        self.InsertColumn(0, "Nom")
##        self.InsertColumn(1, "Description")

        # Remplissage avec les valeurs
        for key, valeurs in self.dictChamps.items():
                index = self.InsertStringItem(six.MAXSIZE, valeurs[1])
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
        menuPop = UTILS_Adaptations.Menu()
        
        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Créer un nouveau champ"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        if mode == "deselected" :
            
            menuPop.AppendSeparator()
            
            # Item Modifier
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
        self.parent.OnBoutonAjouter(None)
        
    def Menu_Modifier(self, event):
        self.parent.OnBoutonModifier(None)

    def Menu_Supprimer(self, event):
        self.parent.OnBoutonSupprimer(None)
        
        
        
        