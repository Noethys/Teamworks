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
        
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        if texteIntro == "" : self.label_introduction.Show(False)
        
        self.staticBox_staticbox = wx.StaticBox(self, -1, "")
        self.label_password1 = wx.StaticText(self, -1, "Mot de passe :")
        self.text_password1 = wx.TextCtrl(self, -1, "", style=wx.TE_PASSWORD)
        self.label_password2 = wx.StaticText(self, -1, "Confirmation :")
        self.text_password2 = wx.TextCtrl(self, -1, "", style=wx.TE_PASSWORD)
        
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
    def __set_properties(self):
        self.SetTitle(u"Saisie d'un mot de passe")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Cadenas.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.text_password1.SetToolTipString(u"Saisissez ici votre mot de passe")
        self.text_password2.SetToolTipString(u"Saisissez ici une deuxième fois votre mot de passe pour confirmation")
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler la saisie")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        staticBox = wx.StaticBoxSizer(self.staticBox_staticbox, wx.VERTICAL)
        
        grid_sizer_base.Add(self.label_introduction, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer.Add(self.label_password1, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer.Add(self.text_password1, 0, wx.EXPAND, 0)
        grid_sizer.Add(self.label_password2, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer.Add(self.text_password2, 0, wx.EXPAND, 0)
        grid_sizer.AddGrowableCol(1)
        staticBox.Add(grid_sizer, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticBox, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()

    def GetPassword(self):
        """ Récupération ds valeurs saisies """
        varPassword = self.text_password1.GetValue()
        return varPassword
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(7)

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        
        varPassword1 = self.text_password1.GetValue()
        if varPassword1 == "" :
            dlg = wx.MessageDialog(self, u"Vous devez saisir un mot de passe valide !", "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_password1.SetFocus()
            return
        
        varPassword2 = self.text_password2.GetValue()
        if varPassword2 == "" :
            dlg = wx.MessageDialog(self, u"Vous devez confirmer le mot de passe !", "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_password2.SetFocus()
            return
        
        if varPassword1 != varPassword2 :
            dlg = wx.MessageDialog(self, u"Vous avez saisi deux mots de passe différents ! \n\nVeuillez recommencer votre saisie.", "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_password1.SetFocus()
            return
            
        self.EndModal(wx.ID_OK)

    
    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = MyDialog(None, texteIntro=u"Bonjour !")
    frm.ShowModal()
    app.MainLoop()
