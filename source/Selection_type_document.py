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
import GestionDB
import sys
import datetime


class MyFrame(wx.Dialog):
    def __init__(self, parent, size=(550, 335), listeBoutons=[], type=None):
        wx.Dialog.__init__(self, parent, -1, title=u"Sélection du type de document")
        self.parent = parent
        self.choix = None
        self.type = type
        self.listeBoutons = listeBoutons
        self.label_intro = wx.StaticText(self, -1, u"Veuillez sélectionner le type de document à éditer :")
                
        # Création des boutons de commandes
        index = 1
        for image, infobulle in self.listeBoutons :
            exec("self.bouton_" + str(index) + " = wx.BitmapButton(self, " + str(index) + ", wx.Bitmap(image, wx.BITMAP_TYPE_ANY))")
            exec("self.bouton_" + str(index) + ".SetToolTipString(infobulle)")
            exec("self.Bind(wx.EVT_BUTTON, self.OnBoutonClic, self.bouton_" + str(index) + ")")
            index += 1
        
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))


        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def __set_properties(self):
        self.bouton_annuler.SetToolTipString("Cliquez ici pour annuler")
        self.SetMinSize((500, -1))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        
        grid_sizer_base.Add(self.label_intro, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_commandes = wx.FlexGridSizer(1, len(self.listeBoutons), 2, 2)
        for index in range(1, len(self.listeBoutons)+1) :
            exec("grid_sizer_commandes.Add(self.bouton_" + str(index) + ", 0, wx.EXPAND, 10)")
        grid_sizer_commandes.AddGrowableCol(0)
        grid_sizer_commandes.AddGrowableCol(1)
        if len(self.listeBoutons) > 2 :
            grid_sizer_commandes.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_commandes, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        grid_sizer_base.Add((10, 10), 1, wx.EXPAND | wx.ALL, 0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)

        grid_sizer_base.AddGrowableCol(0)
##        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        sizer_base.Add(self, 1, wx.EXPAND, 0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()       

    def OnClose(self, event):
        self.MakeModal(False)
        event.Skip()
        
    def OnBoutonAide(self, event):
        # Si impression présences :
        if self.type == "presences" :
            FonctionsPerso.Aide(5)
        # Si impression contrat ou DUE :
        if self.type == "contrats" :
            FonctionsPerso.Aide(6)

    def OnBoutonAnnuler(self, event):
        self.MakeModal(False)
        self.Destroy()

    def OnBoutonClic(self, event):
        self.choix = event.GetId()
        self.EndModal(wx.ID_OK)    
        
    def GetChoix(self):
        return self.choix


    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()

    listeBoutons = [
        ("Images/BoutonsImages/Imprimer_presences_texteB.png", u"Cliquez ici pour imprimer au format texte"),
        ("Images/BoutonsImages/Imprimer_presences_graph1B.png", u"Cliquez ici pour imprimer sous forme graphique au format portrait"),
        ("Images/BoutonsImages/Imprimer_presences_graph2B.png", u"Cliquez ici pour imprimer sous forme graphique au format paysage"),
        ]

    frm = MyFrame(None, listeBoutons=listeBoutons)
    frm.ShowModal()
    app.MainLoop()
