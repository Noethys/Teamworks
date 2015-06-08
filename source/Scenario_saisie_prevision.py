#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import FonctionsPerso
import GestionDB


class MyDialog(wx.Dialog):
    """ Saisie d'une prévision pour un scénario """
    def __init__(self, parent, prevision=None, mode_heure=0):
        wx.Dialog.__init__(self, parent, id=-1, title=u"Saisie d'une prévision")
        self.prevision = prevision
        self.mode_heure = mode_heure

        # Label
        self.label_intro = wx.StaticText(self, -1, u"Saisissez une prévision :")
        
        self.staticbox_periode = wx.StaticBox(self, -1, u"")
                
        # Type
        self.label_type = wx.StaticText(self, -1, u"Type :")
        self.ctrl_type = wx.Choice(self, -1, choices = [u"Heures à réaliser (+)", u"Heures déjà réalisées (-)"])
        self.ctrl_type.SetSelection(0)
        
        # Temps
        self.label_temps = wx.StaticText(self, -1, u"Temps :")
        self.ctrl_temps_heures = wx.TextCtrl(self, -1, u"0", size=(50, -1), style=wx.TE_RIGHT)
        self.label_temps_signe = wx.StaticText(self, -1, u"h")
        self.ctrl_temps_minutes = wx.TextCtrl(self, -1, u"00", size=(30, -1))
        
        # Mode Heure/décimal
        self.label_mode = wx.StaticText(self, -1, u"Mode :")
        self.ctrl_modeHeure = wx.Choice(self, -1, choices = [u"Heure", u"Décimal"])
        self.ctrl_modeHeure.SetSelection(self.mode_heure)
        
        # Boutons
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CHOICE, self.OnChoiceModeHeure, self.ctrl_modeHeure)
        self.ctrl_temps_heures.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusHeures)
        self.ctrl_temps_minutes.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusMinutes)
        
        if self.prevision != None :
            self.SetPrevision(self.prevision)
        
        if self.mode_heure == 1 :
            self.ConvertModeHeure(self.ctrl_temps_minutes.GetValue(), 1)
            self.ctrl_modeHeure.SetSelection(1)
            self.ctrl_temps_minutes.SetToolTipString(u"Saisissez un nombre de minutes au format décimal (entre 0 et 99)")

    def __set_properties(self):
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        
        self.ctrl_temps_heures.SetToolTipString(u"Saisissez un nombre d'heures")
        self.ctrl_temps_minutes.SetToolTipString(u"Saisissez un nombre de minutes (entre 0 et 59)")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 0, wx.TOP|wx.RIGHT|wx.LEFT, 10)

        sizerStaticBox = wx.StaticBoxSizer(self.staticbox_periode, wx.HORIZONTAL)
        
        grid_sizer_box = wx.FlexGridSizer(rows=5, cols=2, vgap=0, hgap=0)
        
        grid_sizer_box.Add(self.label_type, 0, wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_box.Add(self.ctrl_type, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        grid_sizer_box.Add(self.label_temps, 0, wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        grid_sizer_1 = wx.FlexGridSizer(rows=1, cols=6, vgap=0, hgap=0)
        grid_sizer_1.Add(self.ctrl_temps_heures, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_1.Add(self.label_temps_signe, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_1.Add(self.ctrl_temps_minutes, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_1.Add( (10, 5), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_1.Add(self.label_mode, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_1.Add(self.ctrl_modeHeure, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_box.Add(grid_sizer_1, 0, wx.ALL, 0)
        
        sizerStaticBox.Add(grid_sizer_box, 0, wx.ALL, 5)
        grid_sizer_base.Add(sizerStaticBox, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.Fit(self)
        self.Layout()
    
    def OnKillFocusHeures(self, event):
        heures = self.ctrl_temps_heures.GetValue()
        erreur = False
        try:
            heures = int(heures)
        except :
            erreur = True
        
        if heures < 0 :
            erreur = True
        
        if erreur == True :
            self.ctrl_temps_heures.SetValue("0")
##            dlg = wx.MessageDialog(self, u"Le nombre d'heures semble inexact. Veuillez vérifier votre saisie.", u"Erreur de saisie", wx.OK | wx.ICON_ERROR)
##            dlg.ShowModal()
##            dlg.Destroy()
##            self.ctrl_temps_heures.SetFocus()
##            return
            

    def OnKillFocusMinutes(self, event):
        minutes = self.ctrl_temps_minutes.GetValue()
        erreur = False
        try:
            minutes = int(minutes)
        except :
            erreur = True
                
        if self.mode_heure == 0 :
            if minutes < 0 or minutes > 59 :
                erreur = True
        
        if self.mode_heure == 1 :
            if minutes < 0 or minutes > 99 :
                erreur = True
        
        if erreur == True :
            self.ctrl_temps_minutes.SetValue("00")
            minutes = 0
##            dlg = wx.MessageDialog(self, u"Le nombre de minutes semble inexact. Veuillez vérifier votre saisie.", u"Erreur de saisie", wx.OK | wx.ICON_ERROR)
##            dlg.ShowModal()
##            dlg.Destroy()
##            self.ctrl_temps_minutes.SetFocus()
##            return
        
        if self.mode_heure == 0 :
            self.ctrl_temps_minutes.SetValue( "%02d" % minutes)


    def SetPrevision(self, prevision):
        """ Renvoie la prévision """
        if prevision[0] == "+" :
            self.ctrl_type.SetSelection(0)
        else:
            self.ctrl_type.SetSelection(1)
        heures, minutes = prevision[1:].split(":")
        self.ctrl_temps_heures.SetValue(str(heures))
        self.ctrl_temps_minutes.SetValue(str(minutes))
    
    def OnChoiceModeHeure(self, event):
        if self.ctrl_modeHeure.GetSelection() == self.mode_heure : return
        self.ConvertModeHeure(self.ctrl_temps_minutes.GetValue(), self.ctrl_modeHeure.GetSelection())
        
    def ConvertModeHeure(self, min="", mode=0):
        try :
            min = int(min)
        except :
            return
        if mode == 0 :
            resultat = min * 60 / 100
            self.label_temps_signe.SetLabel(u"h")
            self.ctrl_temps_minutes.SetValue( "%02d" % resultat)
            self.ctrl_temps_minutes.SetToolTipString(u"Saisissez un nombre de minutes (entre 0 et 59)")
        if mode == 1 :
            resultat = min * 100 / 60 
            self.label_temps_signe.SetLabel(u".")
            self.ctrl_temps_minutes.SetValue(str(resultat))
            self.ctrl_temps_minutes.SetToolTipString(u"Saisissez un nombre de minutes au format décimal (entre 0 et 99)")
        self.mode_heure = mode

    def GetPrevision(self):
        """ Renvoie la prévision """
        if self.ctrl_type.GetSelection() == 0 :
            signe = "+"
        else:
            signe = "-"
        heures = int(self.ctrl_temps_heures.GetValue())
        minutes = int(self.ctrl_temps_minutes.GetValue())
        if self.mode_heure == 1 : 
            minutes = minutes * 60 / 100
        prevision = u"%s%02d:%02d" % (signe, heures, minutes)
        return prevision
    
    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        self.EndModal(wx.ID_OK)
        



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = MyDialog(None, prevision="+10:30", mode_heure=0)
    frm.ShowModal()
    app.MainLoop()