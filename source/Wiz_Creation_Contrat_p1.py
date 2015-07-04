#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import FonctionsPerso


def getRGB(winColor):
    b = winColor >> 16
    g = winColor >> 8 & 255
    r = winColor & 255
    return (r,g,b)

class Page(wx.Panel):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.parent = self.GetGrandParent()
        
        self.imgBandeau = wx.StaticBitmap(self, -1, wx.Bitmap("Images/Bandeaux/Contrat.png", wx.BITMAP_TYPE_ANY) )
        
        self.label_titre = wx.StaticText(self, -1, _(u"Bienvenue dans l'assistant de création de contrat"))
        
        # Label Html
        txtIntro = u"""
        <FONT face="Arial" color="#000000" size=2>
        <P>Grâce à cet assistant, vous pouvez créer ou modifier des contrats. Cette étape est essentielle pour permettre au logiciel de savoir si tel salarié doit travailler sur une période donnée.</P>
        <p>Vous devrez donc saisir dans cet assistant les caractéristiques de son contrat. Vous avez ensuite la possibilité d'imprimer le contrat et une D.U.E. </p>
        <p><b><u>Remarque :</u></b> Si vous avez l'occasion d'établir des contrats souvent identiques (pour les saisonniers par exemple), vous pouvez utiliser les modèles de contrats qui faciliteront fortement la saisie des données.</p>
        </FONT>
        """ 
        self.label_intro = FonctionsPerso.TexteHtml(self, texte=txtIntro, Enabled=False)
        
        self.__set_properties()
        self.__do_layout()
        
    def __set_properties(self):
        self.label_titre.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_titre, 0, 0, 0)
        grid_sizer_base.Add(self.imgBandeau, 0, wx.LEFT|wx.RIGHT, 30)
        grid_sizer_base.Add(self.label_intro, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 20)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(2)
        

    def Validation(self):
        return True

