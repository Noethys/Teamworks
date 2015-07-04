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
import GestionDB
import FonctionsPerso


class MyFrame(wx.Frame):
    def __init__(self, parent, title="", nomFichier="", password = ""):
        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)
        self.parent = parent
        self.password = password
        self.panel_base = wx.Panel(self, -1)
        if "[RESEAU]" in nomFichier :
            nomFichierTmp = nomFichier[nomFichier.index("[RESEAU]"):]
        else:
            nomFichierTmp = nomFichier
        self.label_intro = wx.StaticText(self.panel_base, -1, _(u"Le fichier '") + nomFichierTmp + _(u"' nécessite un mot de passe :"))
        self.sizer_contenu_staticbox = wx.StaticBox(self.panel_base, -1, "")
        self.label_pwd = wx.StaticText(self.panel_base, -1, _(u"Mot de passe :"))
        self.text_pwd = wx.TextCtrl(self.panel_base, -1, "", size=(200, -1), style=wx.TE_PASSWORD)
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def __set_properties(self):
        self.SetTitle(_(u"Saisie du mot de passe"))
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Cadenas.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.text_pwd.SetToolTipString("Saisissez ici le mot de passe du fichier")
        self.bouton_ok.SetToolTipString("Cliquez ici pour valider")
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString("Cliquez ici pour annuler la saisie")
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 1, wx.LEFT|wx.TOP|wx.RIGHT|wx.EXPAND, 10)
        sizer_contenu = wx.StaticBoxSizer(self.sizer_contenu_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_pwd, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.text_pwd, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        sizer_contenu.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.AddGrowableCol(0)
        #grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.Centre()


    def OnClose(self, event):
        self.MakeModal(False)
        event.Skip()
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(32)

    def OnBoutonAnnuler(self, event):
        self.GetParent().pwd_tmp = False
        self.MakeModal(False)
        self.Destroy()

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        if self.text_pwd.GetValue() != self.password :
            dlg = wx.MessageDialog(self, _(u"Votre mot de passe est erroné."), _(u"Mot de passe erroné"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.text_pwd.SetValue("")
            self.text_pwd.SetFocus()
            return
        
        else:
            self.GetParent().pwd_tmp = True
        
        # Fermeture
        self.MakeModal(False)
        self.Destroy()

    
    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "", nomFichier="test", password="test")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
