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
import wx.html as html
import FonctionsPerso


TEXTE_ACCUEIL = u"""
<CENTER><IMG SRC="Images/80x80/Logo_tw.png">
<BR>
<FONT SIZE=2>
<B>Bienvenue dans TeamWorks</B>
<BR><BR>
Teamworks est un logiciel libre et gratuit de gestion d'équipes qui a nécessité 3 ans 
de développement pour un résultat de 80 000 lignes de code !
<BR><BR>
Si vous jugez que ce logiciel vous apporte un service appréciable au quotidien et 
que vous souhaitez participez au développement du logiciel, vous pouvez apporter 
votre soutien financier au projet : 
<BR>
<A HREF="Saisie">Cliquez ici pour en savoir plus sur les dons</A>.
</FONT>
</CENTER>
"""


class MyHtml(html.HtmlWindow):
    def __init__(self, parent, texte="", hauteur=25):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.SetBorders(0)
        self.SetMinSize((-1, hauteur))
        self.SetPage(texte)
        couleurFond = wx.SystemSettings.GetColour(30)
        self.SetBackgroundColour(couleurFond)
    
    def OnLinkClicked(self, link):
        FonctionsPerso.LanceFichierExterne(_(u"http://teamworks.forumactif.com/faire-un-don-de-soutien-f2/pourquoi-et-comment-faire-un-don-de-soutien-t129.htm"))
        
class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=-1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
            
        # Txt HTML
        texte = TEXTE_ACCUEIL
        self.ctrl_html = MyHtml(self, texte=texte, hauteur=30)
        
        # Boutons de commande
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Demarrer.png", wx.BITMAP_TYPE_ANY), size=(200, -1))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CLOSE, self.OnClose)


    def __set_properties(self):
        self.SetTitle(_(u"Bienvenue"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour fermer cette fenêtre et utiliser Teamworks"))
        self.SetMinSize((300, 370))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_html, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.bouton_ok, 1, wx.BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 20)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen() 
    
    
    def OnClose(self, event):
        self.EndModal(wx.ID_OK)

    def OnBoutonOk(self, event):
        self.EndModal(wx.ID_OK)
    


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()