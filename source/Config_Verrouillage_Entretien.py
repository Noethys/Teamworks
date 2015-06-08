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
import Saisie_password_dialog


class Panel(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="panel_config_verrouillage_entretien", style=wx.TAB_TRAVERSAL)
        
        self.barreTitre = FonctionsPerso.BarreTitre(self,  u"Verrouillage des informations des entretiens", u"")
        texteIntro = u"Vous pouvez protéger l'accès aux informations liées aux entretiens d'embauche (avis et commentaires). L'utilisateur devra ainsi saisir un mot de passe pour les afficher. Cochez la case et saisissez le mot de passe souhaité à deux reprises. Pour désactiver la protection, il vous suffit de décocher cette case."
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        
        self.staticbox = wx.StaticBox(self, -1, u"Protection")
        self.checkBox = wx.CheckBox(self, -1, u"Activer la protection par mot de passe")
        
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Aide.png", wx.BITMAP_TYPE_ANY))
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
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
        password = FonctionsPerso.Parametres(mode="get", categorie="recrutement", nom="password_entretien", valeur="")
        if password == "" or password == None :
            self.checkBox.SetValue(False)
        else:
            self.checkBox.SetValue(True)
            
    def OnCheck(self, event):
        # Enleve le mot de passe
        if self.checkBox.GetValue() == False :
            dlg = wx.MessageDialog(self, u"Voulez-vous vraiment annuler la protection par mot de passe ?", "Confirmation", wx.YES_NO | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                dlg.Destroy()
                # On vérifie que le mot de passe est connu de l'utilisateur
                password = FonctionsPerso.Parametres(mode="get", categorie="recrutement", nom="password_entretien", valeur="")
                dlg = SaisiePassword(self)  
                if dlg.ShowModal() == wx.ID_OK:
                    pwd = dlg.GetPassword()
                    if pwd != password :
                        dlg2 = wx.MessageDialog(self, u"Votre mot de passe est erroné.", u"Mot de passe erroné", wx.OK | wx.ICON_ERROR)
                        dlg2.ShowModal()
                        dlg2.Destroy()
                        self.checkBox.SetValue(True)
                        return
                    dlg.Destroy()
                else:
                    dlg.Destroy()
                    self.checkBox.SetValue(True)
                    return
                # Enregistrement dans la base
                password = FonctionsPerso.Parametres(mode="set", categorie="recrutement", nom="password_entretien", valeur="")
                self.checkBox.SetValue(False)
            else:
                self.checkBox.SetValue(True)
                dlg.Destroy()
        
        # On demande la création d'un mot de passe
        else:
            dlg = Saisie_password_dialog.MyDialog(self)
            if dlg.ShowModal() == wx.ID_OK:
                pwd = dlg.GetPassword()
                password = FonctionsPerso.Parametres(mode="set", categorie="recrutement", nom="password_entretien", valeur=pwd)
                dlg.Destroy()
                self.checkBox.SetValue(True)
            else:
                self.checkBox.SetValue(False)
                dlg.Destroy()
            
    def OnBoutonAide(self, event):
##        FonctionsPerso.Aide(26) 
        dlg = wx.MessageDialog(self, u"L'aide du module Recrutement est en cours de rédaction.\nElle sera disponible lors d'une mise à jour ultérieure.", "Aide indisponible", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()  
        
        
class SaisiePassword(wx.Dialog):
    def __init__(self, parent, id=-1, title=u"Saisie du code de déverrouillage"):
        wx.Dialog.__init__(self, parent, id, title)
            
        self.sizer_3_staticbox = wx.StaticBox(self, -1, "")
        self.label_2 = wx.StaticText(self, -1, u"Pour désactiver le mot de passe, vous devez déjà le saisir :")
        self.label_password = wx.StaticText(self, -1, "Mot de passe :")
        self.text_password = wx.TextCtrl(self, -1, "", size=(200, -1), style=wx.TE_PASSWORD)

        self.bouton_ok = wx.BitmapButton(self, wx.ID_OK, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        self.text_password.SetToolTipString(u"Saisissez votre mot de passe ici")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Cadenas.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.__do_layout()

    def __do_layout(self):
        grid_sizer_2 = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_4 = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.HORIZONTAL)
        grid_sizer_3 = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_2.Add(self.label_2, 0, wx.ALL, 10)
        grid_sizer_3.Add(self.label_password, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_3.Add(self.text_password, 0, wx.EXPAND, 0)
        
        grid_sizer_3.AddGrowableCol(1)
        sizer_3.Add(grid_sizer_3, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_2.Add(sizer_3, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_4.Add((20, 20), 0, 0, 0)
        grid_sizer_4.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_4.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_4.AddGrowableCol(0)
        grid_sizer_2.Add(grid_sizer_4, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_2)
        grid_sizer_2.AddGrowableCol(0)
        grid_sizer_2.Fit(self)
        self.Layout()
        self.CentreOnScreen()

    def GetPassword(self):
        return self.text_password.GetValue()
    
    
class MyFrame(wx.Frame):
    def __init__(self, parent, title="" ):
        wx.Frame.__init__(self, parent, -1, title=title, name="frm_config_verrouillage_entretien", style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.MakeModal(True)
        
        self.panel_base = wx.Panel(self, -1)
        self.panel_contenu = Panel(self.panel_base)
        self.panel_contenu.barreTitre.Show(False)
        self.bouton_aide = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self.panel_base, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler.Show(False)
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.SetMinSize((400, 300))
        self.SetSize((400, 300))

    def __set_properties(self):
        self.SetTitle(u"Verrouillage des informations des entretiens")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez pour annuler et fermer")

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
        self.MAJparents()
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def Onbouton_aide(self, event):
##        FonctionsPerso.Aide(26)
        dlg = wx.MessageDialog(self, u"L'aide du module Recrutement est en cours de rédaction.\nElle sera disponible lors d'une mise à jour ultérieure.", "Aide indisponible", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
            
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
        pass
##        if FonctionsPerso.FrameOuverte("frm_creation_contrats") != None :
##            self.GetParent().MAJ_ListCtrl()
##        if FonctionsPerso.FrameOuverte("frm_creation_modele_contrats") != None :
##            self.GetParent().MAJ_ListCtrl()            

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
