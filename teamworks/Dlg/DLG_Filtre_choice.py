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
import FonctionsPerso
import GestionDB

import datetime


class MyDialog(wx.Dialog):
    """ Choix possibles : None pour 'sans importance' ou une LISTE de choix pour la checkListBox """
    def __init__(self, parent, nom_filtre=u"", titre_frame = u"", selection=None, listeChoix = []):
        wx.Dialog.__init__(self, parent, id=-1, title=u"", size=(350, 250))
        
        # Paramètres personnalisables
        self.nom_filtre = nom_filtre # _(u"les fonctions")
        self.titre_frame = titre_frame # _(u"Filtre des fonctions")
        self.selection = selection #None
        self.listeChoix = listeChoix # [ (1, "BAFA"), (2, _(u"BAFD")), (3, _(u"BEATEP")) ]
        
        # Label
        self.label = wx.StaticText(self, -1, _(u"Veuillez définir un filtre pour %s :") % self.nom_filtre)
        
        # Controles
        self.staticbox = wx.StaticBox(self, -1, self.nom_filtre.capitalize())
        self.radio1 = wx.RadioButton(self, -1, _(u"Sans importance"), style = wx.RB_GROUP )
        self.radio2 = wx.RadioButton(self, -1, _(u"Uniquement l'élément sélectionné :"))
        self.myChoice = MyChoice(self)
        self.myChoice.Remplissage(self.listeChoix)
                
        # Boutons
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio2)
        
        if self.selection != None :
            self.myChoice.SetIDselection(self.selection)
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
        grid_sizer_contenu.Add(self.myChoice, 1, wx.EXPAND|wx.LEFT, 20)
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
        self.Layout()
    
    def OnRadio(self, event):
        if self.radio1.GetValue() == True :
            self.myChoice.Enable(False)
        else:
            self.myChoice.Enable(True)

    def GetSelection(self):
        """ Renvoie les sélection """
        if self.radio1.GetValue() == True :
            return None
        else:
            return self.myChoice.GetIDselection()
        
    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        self.EndModal(wx.ID_OK)
        


class MyChoice(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, size=(-1, -1), choices=[])
        self.dictIndexes = {}
        self.Select(0)
        
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
        self.Select(0)
                
    def GetIDselection(self):
        index = self.GetSelection()
        return self.dictIndexes[index], self.GetStringSelection()
    
    def SetIDselection(self, ID):
        for index, IDtemp in self.dictIndexes.items():
            if ID == IDtemp :
                self.Select(index)
                return        
    

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = MyDialog(None, nom_filtre=_(u"les offres"), titre_frame = _(u"Filtre des offres"), selection=None, listeChoix = [(1, "offre 1"), (2, "offre 2")])
    frm.ShowModal()
    app.MainLoop()