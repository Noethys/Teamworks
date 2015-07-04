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
import wx.lib.mixins.listctrl  as  listmix
import GestionDB
import FonctionsPerso
import Saisie_password
       
        


class Panel(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="panel_config_password", style=wx.TAB_TRAVERSAL)
        
        self.barreTitre = FonctionsPerso.BarreTitre(self,  _(u"Protection par mot de passe"), u"")
        texteIntro = _(u"Vous pouvez protéger l'accès à ce fichier par un mot de passe. L'utilisateur de ce fichier devra\nainsi saisir le mot de passe à son ouverture. Cochez la case et saisissez le mot de passe souhaité\nà deux reprises. Pour désactiver la protection, il vous suffit de décocher cette case.")
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        
        self.staticbox = wx.StaticBox(self, -1, _(u"Protection"))
        self.checkBox = wx.CheckBox(self, -1, _(u"Activer la protection par mot de passe"))
        self.MAJ_checkBox() 
        
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Aide.png", wx.BITMAP_TYPE_ANY))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        if parent.GetName() != "treebook_configuration" :
            self.bouton_aide.Show(False)

        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.checkBox)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        # Layout
        grid_sizer_principal = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        grid_sizer_principal.Add(self.barreTitre, 1, wx.EXPAND, 0)
        grid_sizer_principal.Add(self.label_introduction, 1, wx.ALL|wx.EXPAND, 10)
        
        staticbox = wx.StaticBoxSizer(self.staticbox, wx.VERTICAL)
        staticbox.Add(self.checkBox, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_principal.Add(staticbox, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_principal.Add((20, 20), 0, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=10)
        grid_sizer_boutons.Add((5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_principal.Add(grid_sizer_boutons, 1, wx.EXPAND|wx.ALL, 10)
        
        grid_sizer_principal.AddGrowableRow(3)
        grid_sizer_principal.AddGrowableCol(0)
        self.SetSizer(grid_sizer_principal)
        grid_sizer_principal.Fit(self)

               

    def MAJpanel(self):
        self.MAJ_checkBox() 
        
        
    def MAJ_checkBox(self):
        """ Recherche le mot de passe dans la base """
        DB = GestionDB.DB()        
        req = "SELECT motdepasse FROM divers WHERE IDdivers=1;"
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        DB.Close()
        if len(donnees) == 0 : return
        password = donnees[0][0]

        # Création du dictionnaire de données
        if password == "" or password == None :
            self.checkBox.SetValue(False)
        else:
            self.checkBox.SetValue(True)
            
    def OnCheck(self, event):
        
        # Enleve le mot de passe
        if self.checkBox.GetValue() == False :
            dlg = wx.MessageDialog(self, _(u"Voulez-vous vraiment annuler la protection par mot de passe ?"), "Confirmation", wx.YES_NO | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                # Enregistrement dans la base
                DB = GestionDB.DB()
                varPassword = ""
                listeDonnees = [ ("motdepasse",   varPassword),]
                DB.ReqMAJ("divers", listeDonnees, "IDdivers", 1)
                DB.Commit()
                DB.Close()
                dlg.Destroy()
                self.checkBox.SetValue(False)
            else:
                self.checkBox.SetValue(True)
                dlg.Destroy()
        
        # On demande la création d'un mot de passe
        else:
            frmSaisie = Saisie_password.MyFrame(self)
            frmSaisie.Show()
            
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(26)        
        
        

class MyFrame(wx.Frame):
    def __init__(self, parent, title="" ):
        wx.Frame.__init__(self, parent, -1, title=title, name="frm_config_password", style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.MakeModal(True)
        
        self.panel_base = wx.Panel(self, -1)
        self.panel_contenu = Panel(self.panel_base)
        self.panel_contenu.barreTitre.Show(False)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.SetMinSize((550, 450))
        self.SetSize((550, 450))

    def __set_properties(self):
        self.SetTitle(_(u"Protection par mot de passe"))
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString(_(u"Cliquez pour annuler et fermer"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.ALL|wx.EXPAND, 0)
        sizer_pages.Add(self.panel_contenu, 1, wx.EXPAND | wx.TOP, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        self.Centre()
        self.sizer_pages = sizer_pages


        
        
    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def Onbouton_aide(self, event):
        FonctionsPerso.Aide(26)
            
    def Onbouton_annuler(self, event):
        # Si frame Creation_contrats ouverte, on met à jour le listCtrl Valeurs de points
        self.MAJparents()
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()
        
    def Onbouton_ok(self, event):
        # Si frame Creation_contrats ouverte, on met à jour le listCtrl Valeurs de points
        self.MAJparents()
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()     
        
    def MAJparents(self):
        if FonctionsPerso.FrameOuverte("frm_creation_contrats") != None :
            self.GetParent().MAJ_ListCtrl()
        if FonctionsPerso.FrameOuverte("frm_creation_modele_contrats") != None :
            self.GetParent().MAJ_ListCtrl()            
            
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
