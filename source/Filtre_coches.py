#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import FonctionsPerso
import GestionDB
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import datetime


class MyDialog(wx.Dialog):
    """ Choix possibles : None pour 'sans importance' ou une LISTE de choix pour la checkListBox """
    def __init__(self, parent, nom_filtre=u"", titre_frame = u"", listeSelection=None, listeChoix = []):
        wx.Dialog.__init__(self, parent, id=-1, title=u"", size=(350, 400))
        
        # Paramètres personnalisables
        self.nom_filtre = nom_filtre # u"les fonctions"
        self.titre_frame = titre_frame # u"Filtre des fonctions"
        self.listeSelection = listeSelection #None
        self.listeChoix = listeChoix # [ (1, "BAFA"), (2, u"BAFD"), (3, u"BEATEP") ]
        
        # Label
        self.label = wx.StaticText(self, -1, u"Veuillez définir un filtre pour le champ '%s' :" % self.nom_filtre)
        
        # Controles
        self.staticbox = wx.StaticBox(self, -1, self.nom_filtre.capitalize())
        self.radio1 = wx.RadioButton(self, -1, u"Sans importance", style = wx.RB_GROUP )
        self.radio2 = wx.RadioButton(self, -1, u"Uniquement les éléments sélectionnés :")
        self.checkListBox = CheckListBox(self)
        self.checkListBox.Remplissage(self.listeChoix)
                
        # Boutons
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio2)
        
        if self.listeSelection != None :
            self.checkListBox.CocheListe(self.listeSelection)
            self.radio2.SetValue(True)
        self.OnRadio(None)

    def __set_properties(self):
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.SetTitle(self.titre_frame)

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label, 0, wx.ALL, 10)
        
        sizerStaticBox = wx.StaticBoxSizer(self.staticbox, wx.HORIZONTAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_contenu.Add(self.radio1, 1, wx.EXPAND|wx.ALL, 2)
        grid_sizer_contenu.Add(self.radio2, 1, wx.EXPAND|wx.ALL, 2)
        grid_sizer_contenu.Add(self.checkListBox, 1, wx.EXPAND|wx.LEFT, 20)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_contenu.AddGrowableRow(2)
        sizerStaticBox.Add(grid_sizer_contenu, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(sizerStaticBox, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.SetMinSize((300, 250))
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()
    
    def OnRadio(self, event):
        if self.radio1.GetValue() == True :
            self.checkListBox.Enable(False)
        else:
            self.checkListBox.Enable(True)

    def GetListeSelections(self):
        """ Renvoie les sélection """
        if self.radio1.GetValue() == True :
            return None
        else:
            return self.checkListBox.GetIDetLabels()
        
    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        self.EndModal(wx.ID_OK)
        
        


class CheckListBox(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, choices=[])
        self.listeDonnees = []
        self.listeIDcoches = []
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck, self)

    def Remplissage(self, liste=None) :
        if liste != None :
            self.listeDonnees = liste
        # Remplissage
        self.dictIndexes = {}
        self.Clear()
        index = 0
        for ID, texte in self.listeDonnees :
            self.Append(texte)
            self.dictIndexes[index] = ID
            index += 1

    def CocheListe(self, liste=None):
        if liste != None :
            self.listeIDcoches = liste
        # Coche les ID donnés
        for index in range(0, self.GetCount()) :
            if self.dictIndexes[index] in self.listeIDcoches :
                self.Check(index, True)
            else:
                self.Check(index, False)
    
    def GetIDcoches(self):
        # Récupère la liste des ID cochés :
        listeIDcoches = []
        for index in range(0, self.GetCount()) :
            if self.IsChecked(index) == True :
                listeIDcoches.append(self.dictIndexes[index])
        return listeIDcoches
    
    def GetIDetLabels(self):  	
        # Récupère la liste des ID et des labels cochés :
        liste = []
        for index in range(0, self.GetCount()) :
            if self.IsChecked(index) == True :
                liste.append((self.dictIndexes[index], self.GetString(index)))
        return liste

    def OnCheck(self, event):
        self.listeIDcoches = self.GetIDcoches()
    
    

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = MyDialog(None)
    frm.ShowModal()
    app.MainLoop()