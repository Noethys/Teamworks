#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import GestionDB
import FonctionsPerso


class MyDialog(wx.Dialog):
    def __init__(self, parent, title="", texteIntro="", ):
        wx.Dialog.__init__(self, parent, id=-1, title=title, size=(-1, -1))
        
        self.staticBox_staticbox = wx.StaticBox(self, -1, "")
        self.label_label = wx.StaticText(self, -1, u"Label :")
        self.ctrl_label = wx.TextCtrl(self, -1, "", size=(300, -1))
        self.label_url = wx.StaticText(self, -1, u"URL :")
        self.ctrl_url = wx.TextCtrl(self, -1, "")
        
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
    def __set_properties(self):
        self.SetTitle(u"Saisie d'une URL")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.ctrl_label.SetToolTipString(u"Saisissez ici le label")
        self.ctrl_url.SetToolTipString(u"Saisissez ici l'URL")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler la saisie")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        staticBox = wx.StaticBoxSizer(self.staticBox_staticbox, wx.VERTICAL)
        
        grid_sizer = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer.Add(self.label_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer.Add(self.ctrl_label, 0, wx.EXPAND, 0)
        grid_sizer.Add(self.label_url, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer.Add(self.ctrl_url, 0, wx.EXPAND, 0)
        grid_sizer.AddGrowableCol(1)
        staticBox.Add(grid_sizer, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticBox, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()

    def GetLabel(self):
        """ R�cup�ration ds valeurs saisies """
        return self.ctrl_label.GetValue()
    
    def GetURL(self):
        """ R�cup�ration ds valeurs saisies """
        return self.ctrl_url.GetValue()
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(7)

    def OnBoutonOk(self, event):
        """ Validation des donn�es saisies """
        
        label = self.ctrl_label.GetValue()
        if label == "" :
            dlg = wx.MessageDialog(self, u"Vous devez saisir un label !", "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_label.SetFocus()
            return
        
        URL = self.ctrl_url.GetValue()
        if URL == "" :
            dlg = wx.MessageDialog(self, u"Vous devez saisir une URL !", "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_url.SetFocus()
            return
                    
        self.EndModal(wx.ID_OK)

    
    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = MyDialog(None)
    frm.ShowModal()
    app.MainLoop()
