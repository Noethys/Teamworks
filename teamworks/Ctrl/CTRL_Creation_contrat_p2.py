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
from Dlg import DLG_Config_modeles_contrats as ConfigModeles
import GestionDB


class Page(wx.Panel):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.sizer_choix_modele_staticbox = wx.StaticBox(self, -1, _(u"Choix du modèle"))
        self.label_titre = wx.StaticText(self, -1, _(u"1. Importation d'un modèle de contrat"))
        self.label_intro = wx.StaticText(self, -1, _(u"Souhaitez-vous utiliser un modèle de contrat pour faciliter votre saisie ?"))
        self.radio_non = wx.RadioButton(self, -1, "Non", style=wx.RB_GROUP)
        self.radio_oui = wx.RadioButton(self, -1, "Oui")
        self.listCtrl_modeles = ListCtrl(self)
        self.bouton_modeles = wx.Button(self, -1, "...", style=wx.BU_EXACTFIT)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioNon, self.radio_non )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioOui, self.radio_oui )
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModeles, self.bouton_modeles)
        
        self.Init_radio(position="non")
        

    def __set_properties(self):
        self.label_titre.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.bouton_modeles.SetMinSize((20, 20))
        self.bouton_modeles.SetToolTipString(_(u"Cliquez ici pour ajouter, modifier ou supprimer des modèles de contrat"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_question = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        sizer_choix_modele = wx.StaticBoxSizer(self.sizer_choix_modele_staticbox, wx.VERTICAL)
        grid_sizer_choix = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_titre, 0, 0, 0)
        grid_sizer_base.Add(self.label_intro, 0, wx.LEFT, 20)
        grid_sizer_question.Add(self.radio_non, 0, 0)
        grid_sizer_question.Add(self.radio_oui, 0, 0)
        grid_sizer_choix.Add(self.listCtrl_modeles, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_modeles, 0, 0, 0)
        grid_sizer_choix.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        grid_sizer_choix.AddGrowableRow(0)
        grid_sizer_choix.AddGrowableCol(0)
        sizer_choix_modele.Add(grid_sizer_choix, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_question.Add(sizer_choix_modele, 1, wx.LEFT|wx.EXPAND, 18)
        grid_sizer_question.AddGrowableRow(2)
        grid_sizer_question.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_question, 1, wx.EXPAND|wx.LEFT, 35)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)

    def OnRadioNon(self, event):
        self.Init_radio(position="non")

    def OnRadioOui(self, event):
        self.Init_radio(position="oui")
        self.listCtrl_modeles.SetFocus()
        if self.listCtrl_modeles.GetItemCount() > 0 :
            self.listCtrl_modeles.Select(0)

    def OnBoutonModeles(self, event):
        frmModeles = ConfigModeles.MyFrame(self, "")
        frmModeles.Show()
                        
    def Init_radio(self, position="non"):
        if position == "non" :
            self.radio_non.SetValue(True)
            self.listCtrl_modeles.Enable(False)
            self.bouton_modeles.Enable(False)     
        else :
            self.radio_oui.SetValue(True)
            self.listCtrl_modeles.Enable(True)
            self.bouton_modeles.Enable(True)         

    def MAJ_ListCtrl(self):
        self.listCtrl_modeles.MAJListeCtrl()    



    def Validation(self):
        
        # Si "non", on passe à la page suivante
        if self.radio_oui.GetValue() == False : return True
        
        # Si "oui", on valide le choix dans le ListCtrl
        index = self.listCtrl_modeles.GetFirstSelected()
        # Vérifie qu'un item a bien été sélectionné dans la liste
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un modèle dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Transmission des données
        IDmodele = int(self.listCtrl_modeles.GetItem(index, 0).GetText())
        
        # Récupération des données du MODELE
        DB = GestionDB.DB()        
        req = """SELECT IDclassification, IDtype
        FROM contrats_modeles WHERE IDmodele=%d; """ % IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()[0]
        

        self.GetGrandParent().dictContrats["IDclassification"] = listeDonnees[0]
        self.GetGrandParent().dictContrats["IDtype"] = listeDonnees[1]
        
        # Récupération des données CHAMPS du MODELE
        req = "SELECT IDchamp, valeur FROM contrats_valchamps WHERE (IDmodele=%d AND type='modele')  ;" % IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        
        for item in listeDonnees :
            self.GetGrandParent().dictChamps[item[0]] = item[1]
            
        DB.Close()
        
        # MAJ des contrôles des pages suivantes avec les données importées des modèles
        self.GetGrandParent().page3.Importation() 
        self.GetGrandParent().page4.MAJ_ListCtrl()
        
        return True





# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
        self.Remplissage()
        
        #events
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
##        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        #self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, event):
        self.Refresh()
        event.Skip()

    def Remplissage(self):
        
        # Récupération des données dans la base de données
        self.Importation()
        
        # Création des colonnes
        self.nbreColonnes =2
        self.InsertColumn(0, _(u"     ID"))
        self.SetColumnWidth(0, 0)
        self.InsertColumn(1, _(u"Nom"))
        self.SetColumnWidth(1, 200)  
        self.InsertColumn(2, _(u"Description"))
        self.SetColumnWidth(2, 100)  
        
        #These two should probably be passed to init more cleanly
        #setting the numbers of items = number of elements in the dictionary
        self.itemDataMap = self.donnees
        self.itemIndexMap = self.donnees.keys()
        self.SetItemCount(self.nbreLignes)
        
        #mixins
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

        #sort by genre (column 1), A->Z ascending order (1)
        self.SortListItems(1, 1)

    def OnItemSelected(self, event):
        pass
        
    def OnItemDeselected(self, event):
        pass
        
    def Importation(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDmodele, nom, description
        FROM contrats_modeles ORDER BY nom; """
        DB.ExecuterReq(req)
        liste = DB.ResultatReq()
        DB.Close()
        self.nbreLignes = len(liste)
        # Création du dictionnaire de données
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
            index = x # Donne un entier comme clé
            dictio[index] = ligne
            x += 1
        return dictio
           
    def OnItemActivated(self, event):
        self.parent.OnBoutonModeles(None)
        
    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    #---------------------------------------------------
    # These methods are callbacks for implementing the
    # "virtualness" of the list...

    def OnGetItemText(self, item, col):
        """ Affichage des valeurs dans chaque case du ListCtrl """
        index=self.itemIndexMap[item]
        valeur = unicode(self.itemDataMap[index][col])       
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

    def SortItems(self,sorter=cmp):
        items = list(self.itemDataMap.keys())
        items.sort(sorter)
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
        menuPop = wx.Menu()

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