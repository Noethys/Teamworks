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
import os
import GestionDB
import sys
import datetime


class Dialog(wx.Dialog):
    def __init__(self, parent, size=(550, 335), listeBoutons=[], type=None):
        wx.Dialog.__init__(self, parent, -1, title=_(u"Sélection du type de document"))
        self.parent = parent
        self.choix = None
        self.type = type
        self.listeBoutons = listeBoutons
        self.label_intro = wx.StaticText(self, -1, _(u"Veuillez sélectionner le type de document à éditer :"))
                
        # Création des boutons de commandes
        index = 1
        for image, infobulle in self.listeBoutons :
            exec("self.bouton_" + str(index) + " = wx.BitmapButton(self, " + str(index) + ", wx.Bitmap(image, wx.BITMAP_TYPE_ANY))")
            exec("self.bouton_" + str(index) + ".SetToolTip(wx.ToolTip(infobulle))")
            exec("self.Bind(wx.EVT_BUTTON, self.OnBoutonClic, self.bouton_" + str(index) + ")")
            index += 1
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))


        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.bouton_annuler.SetToolTip(wx.ToolTip("Cliquez ici pour annuler"))
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
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        sizer_base.Add(self, 1, wx.EXPAND, 0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()       

    def OnBoutonAide(self, event):
        # Si impression présences :
        if self.type == "presences" :
            from Utils import UTILS_Aide
            UTILS_Aide.Aide("Imprimerunelistedeprsences")
        # Si impression contrat ou DUE :
        if self.type == "contrats" :
            from Utils import UTILS_Aide
            UTILS_Aide.Aide("Lescontrats")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonClic(self, event):
        self.choix = event.GetId()
        self.EndModal(wx.ID_OK)    
        
    def GetChoix(self):
        return self.choix


    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()

    listeBoutons = [
        (Chemins.GetStaticPath("Images/BoutonsImages/Imprimer_presences_texteB.png"), _(u"Cliquez ici pour imprimer au format texte")),
        (Chemins.GetStaticPath("Images/BoutonsImages/Imprimer_presences_graph1B.png"), _(u"Cliquez ici pour imprimer sous forme graphique au format portrait")),
        (Chemins.GetStaticPath("Images/BoutonsImages/Imprimer_presences_graph2B.png"), _(u"Cliquez ici pour imprimer sous forme graphique au format paysage")),
        ]

    dlg = Dialog(None, listeBoutons=listeBoutons)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
