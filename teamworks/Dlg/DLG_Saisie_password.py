#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import Chemins
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
import FonctionsPerso


class MyFrame(wx.Frame):
    def __init__(self, parent, title=""):
        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)
        
        self.typeJour = type
        
        self.panel_base = wx.Panel(self, -1)
        self.staticBox_staticbox = wx.StaticBox(self.panel_base, -1, "")
        self.label_password1 = wx.StaticText(self.panel_base, -1, "Mot de passe :")
        self.text_password1 = wx.TextCtrl(self.panel_base, -1, "", style=wx.TE_PASSWORD)
        self.label_password2 = wx.StaticText(self.panel_base, -1, "Confirmation :")
        self.text_password2 = wx.TextCtrl(self.panel_base, -1, "", style=wx.TE_PASSWORD)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un mot de passe"))
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cadenas.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.text_password1.SetToolTipString(_(u"Saisissez ici votre mot de passe"))
        self.text_password2.SetToolTipString(_(u"Saisissez ici une deuxième fois votre mot de passe pour confirmation"))
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler la saisie"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base_2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        staticBox = wx.StaticBoxSizer(self.staticBox_staticbox, wx.VERTICAL)
        
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
        
        sizer_base_2.Add(grid_sizer_base, 1, wx.EXPAND, 0)
        self.panel_base.SetSizer(sizer_base_2)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)        
        sizer_base.Fit(self)
        self.Layout()
        self.Centre()


    def Sauvegarde(self):
        """ Sauvegarde des données dans la base de données """
        
        # Récupération ds valeurs saisies
        varPassword = self.text_password1.GetValue()
        
        # Enregistrement dans la base
        DB = GestionDB.DB()
        listeDonnees = [ ("motdepasse",   varPassword),]
        DB.ReqMAJ("divers", listeDonnees, "IDdivers", 1)
        DB.Commit()
        DB.Close()

    def OnClose(self, event):
        self.MakeModal(False)
        self.GetParent().checkBox.SetValue(False)
        event.Skip()
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(7)

    def OnBoutonAnnuler(self, event):
        self.MakeModal(False)
        self.GetParent().checkBox.SetValue(False)
        self.Destroy()

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        
        varPassword1 = self.text_password1.GetValue()
        if varPassword1 == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un mot de passe valide !"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_password1.SetFocus()
            return
        
        varPassword2 = self.text_password2.GetValue()
        if varPassword2 == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez confirmer le mot de passe !"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_password2.SetFocus()
            return
        
        if varPassword1 != varPassword2 :
            dlg = wx.MessageDialog(self, _(u"Vous avez saisi deux mots de passe différents ! \n\nVeuillez recommencer votre saisie."), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_password1.SetFocus()
            return
    
        # Sauvegarde
        self.Sauvegarde()
        
        # MAJ du panel Password
        if FonctionsPerso.FrameOuverte("panel_config_password") != None :
            self.GetParent().MAJpanel()

        # Fermeture
        self.MakeModal(False)
        self.Destroy()

    
    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
