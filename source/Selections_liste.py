#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import FonctionsPerso
import os
import wx.lib.hyperlink as hl
import GestionDB
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import sys
import datetime


class MyFrame(wx.Dialog):
    def __init__(self, parent, liste_labelsColonnes=[], listeValeurs=[], type=None):
        wx.Dialog.__init__(self, parent, -1, title=u"Sélection d'éléments", size=(800, 460))
        self.parent = parent
        self.type = type
        self.liste_labelsColonnes = liste_labelsColonnes
        self.listeValeurs = listeValeurs
        
        self.label_intro = wx.StaticText(self, -1, u"Veuillez sélectionner les éléments de votre choix :")
        
        # ListCtrl
        self.listCtrl = ListCtrl(self, self.liste_labelsColonnes, self.listeValeurs)
        
        # Hyperlinks
        self.hyperlink_select = self.Build_Hyperlink_select()
        self.label_separation = wx.StaticText(self, -1, u"|")
        self.hyperlink_deselect = self.Build_Hyperlink_deselect()

        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def __set_properties(self):
##        self.SetTitle(u"Sélection d'éléments")
##        _icon = wx.EmptyIcon()
##        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
##        self.SetIcon(_icon)
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString("Cliquez ici pour valider")
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString("Cliquez ici pour annuler la saisie")
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.SetMinSize((710, 380))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 1, wx.LEFT|wx.TOP|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.listCtrl, 1, wx.EXPAND | wx.LEFT|wx.RIGHT|wx.TOP, 10)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=4, vgap=2, hgap=2)
        grid_sizer_commandes.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.hyperlink_select, 1, wx.EXPAND, 10)
        grid_sizer_commandes.Add(self.label_separation, 1, wx.EXPAND, 10)
        grid_sizer_commandes.Add(self.hyperlink_deselect, 1, wx.EXPAND, 10)
        grid_sizer_commandes.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_commandes, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM | wx.ALIGN_RIGHT, 10)
        
        grid_sizer_base.Add((10, 10), 1, wx.EXPAND | wx.ALL, 0)
        
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)

        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        sizer_base.Add(self, 1, wx.EXPAND, 0)
        self.Layout()
        self.CentreOnScreen()       

    
    def Build_Hyperlink_select(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self, -1, u"Tout sélectionner", URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink_select)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLACK", "BLACK", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(u"Tout sélectionner"))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink_select(self, event):
        """ Sélectionner tout """
        self.listCtrl.MAJListeCtrl(action="select")

    def Build_Hyperlink_deselect(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self, -1, u"Tout dé-sélectionner", URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink_deselect)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLACK", "BLACK", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(u"Tout dé-sélectionner"))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink_deselect(self, event):
        """ dé-Sélectionner tout """
        self.listCtrl.MAJListeCtrl(action="deselect")
        
    def OnClose(self, event):
        self.MakeModal(False)
        event.Skip()
        
    def OnBoutonAide(self, event):
        if self.type == "exportTexte" :
            FonctionsPerso.Aide(55)
        if self.type == "exportExcel" :
            FonctionsPerso.Aide(55)
        if self.type == "imprimerListePersonnes" :
            FonctionsPerso.Aide(56)

    def OnBoutonAnnuler(self, event):
        self.MakeModal(False)
        self.Destroy()

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        selections = self.listCtrl.ListeItemsCoches()
        
        # Validation de la sélection
        if len(selections) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez fait aucune sélection", u"Erreur de saisie", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Ferme la boîte de dialogue
        self.EndModal(wx.ID_OK)        

    def GetSelections(self):
        return self.listCtrl.ListeItemsCoches()


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class ListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent, liste_labelsColonnes, listeValeurs):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        CheckListCtrlMixin.__init__(self)
        self.parent = parent
        self.liste_labelsColonnes = liste_labelsColonnes
        self.listeValeurs = listeValeurs
        
        self.Remplissage()
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)


    def Remplissage(self, select=None, action=None):

        # Création des colonnes
        index = 0
        for labelCol, alignement, largeur, nomChamp in self.liste_labelsColonnes :
            self.InsertColumn(index, labelCol)
            if index == 0 and largeur == 0 : largeur = 50
            self.SetColumnWidth(index, largeur)
            index += 1
                
        # Remplissage avec les valeurs
        self.remplissage = True
        for valeurs in self.listeValeurs :
            ID = int(valeurs[0])
            index = self.InsertStringItem(sys.maxint, str(ID))
            x = 1
            for valeur in valeurs[1:] :
                self.SetStringItem(index, x, valeur)
                x += 1

            self.SetItemData(index, ID)
                
            # Check
            if action == None or action == "select" :
                self.CheckItem(index) 
    
        self.remplissage = False

    def MAJListeCtrl(self, select=None, action=None):
        self.ClearAll()
        self.Remplissage(select, action)
        
    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)

    def ListeItemsCoches(self):
        """ Récupère la liste des IDdeplacements cochés """
        listeIDcoches = []
        nbreItems = self.GetItemCount()
        for index in range(0, nbreItems) :
            ID = int(self.GetItem(index, 0).GetText())
            # Vérifie si l'item est coché
            if self.IsChecked(index) :
                listeIDcoches.append(ID)
        return listeIDcoches
        


    
    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    liste_labelsColonnes=[(u"COL1", "left", 50, "col1"), (u"COL2", "left", 200, "col2"),]
    listeValeurs=[ (1, u"ligne1-col2"), (2, u"ligne2-col2"),]
    frm = MyFrame(None, liste_labelsColonnes, listeValeurs)
    frm.ShowModal()
    app.MainLoop()
