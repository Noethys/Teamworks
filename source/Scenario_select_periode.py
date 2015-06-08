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
import datetime


def DateEngEnDateDD(dateEng):
    """ Tranforme une date anglaise en datetime.date """
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


class MyDialog(wx.Dialog):
    """ Sélection d'une période pour un scénario """
    def __init__(self, parent, date_debut=None, date_fin=None):
        wx.Dialog.__init__(self, parent, id=-1, title=u"Sélection d'une période de référence")
        self.date_debut = date_debut
        self.date_fin = date_fin

        # Label
        self.label = wx.StaticText(self, -1, u"Sélectionnez une période :")
        
        self.staticbox_periode = wx.StaticBox(self, -1, u"")
        
        self.radio_1 = wx.RadioButton(self, -1, u"", size=(-1, 20), style = wx.RB_GROUP )
        self.radio_2 = wx.RadioButton(self, -1, u"", size=(-1, 20))
        self.radio_3 = wx.RadioButton(self, -1, u"", size=(-1, 20))
        self.radio_4 = wx.RadioButton(self, -1, u"", size=(-1, 20))
        self.radio_5 = wx.RadioButton(self, -1, u"", size=(-1, 20))
        
        # Période : Début et Fin
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN)
        self.label_date_fin = wx.StaticText(self, -1, "au")
        self.ctrl_date_fin = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN)
        self.ctrl_date_debut.Enable(False)
        self.ctrl_date_fin.Enable(False)
        
        # Période : A partir
        self.label_date_aPartir = wx.StaticText(self, -1, u"A partir du")
        self.ctrl_date_aPartir = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN)
        self.ctrl_date_aPartir.Enable(False)
        
        # Période : Jusq'au
        self.label_date_jusque = wx.StaticText(self, -1, u"Jusqu'au")
        self.ctrl_date_jusque = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN)
        self.ctrl_date_jusque.Enable(False)
        
        # Période : Tout
        self.label_date_tout= wx.StaticText(self, -1, u"Tout")
        
        # Période : Rien
        self.label_date_rien= wx.StaticText(self, -1, u"Rien")
        
        # Boutons
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton, self.radio_1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton, self.radio_2)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton, self.radio_3)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton, self.radio_4)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton, self.radio_5)
        
        self.SetRadioChoix(0)
               

    def __set_properties(self):
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label, 0, wx.TOP|wx.RIGHT|wx.LEFT, 10)
        
        # Vacances
        sizerStaticBox = wx.StaticBoxSizer(self.staticbox_periode, wx.HORIZONTAL)
        
        grid_sizer_box = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        
        grid_sizer_1 = wx.FlexGridSizer(rows=1, cols=6, vgap=0, hgap=0)
        grid_sizer_1.Add(self.radio_1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_1.Add(self.label_date_debut, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_1.Add(self.ctrl_date_debut, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_1.Add(self.label_date_fin, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_1.Add(self.ctrl_date_fin, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_box.Add(grid_sizer_1, 0, wx.ALL, 0)
        
        grid_sizer_2 = wx.FlexGridSizer(rows=1, cols=6, vgap=0, hgap=0)
        grid_sizer_2.Add(self.radio_2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_2.Add(self.label_date_aPartir, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_2.Add(self.ctrl_date_aPartir, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_box.Add(grid_sizer_2, 0, wx.ALL, 0)
        
        grid_sizer_3 = wx.FlexGridSizer(rows=1, cols=6, vgap=0, hgap=0)
        grid_sizer_3.Add(self.radio_3, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_3.Add(self.label_date_jusque, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_3.Add(self.ctrl_date_jusque, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_box.Add(grid_sizer_3, 0, wx.ALL, 0)
        
        grid_sizer_4 = wx.FlexGridSizer(rows=1, cols=6, vgap=0, hgap=0)
        grid_sizer_4.Add(self.radio_4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_4.Add(self.label_date_tout, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_box.Add(grid_sizer_4, 0, wx.ALL, 0)
        
        grid_sizer_5 = wx.FlexGridSizer(rows=1, cols=6, vgap=0, hgap=0)
        grid_sizer_5.Add(self.radio_5, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_5.Add(self.label_date_rien, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_box.Add(grid_sizer_5, 0, wx.ALL, 0)
        
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

    def OnRadioButton(self, event):
        self.DisableAllRadio()
        if self.radio_1.GetValue() == True :
            self.ctrl_date_debut.Enable(True)
            self.ctrl_date_fin.Enable(True)
        if self.radio_2.GetValue() == True :
            self.ctrl_date_aPartir.Enable(True)
        if self.radio_3.GetValue() == True :
            self.ctrl_date_jusque.Enable(True)
    
    def DisableAllRadio(self):
        self.ctrl_date_debut.Enable(False)
        self.ctrl_date_fin.Enable(False)
        self.ctrl_date_aPartir.Enable(False)
        self.ctrl_date_jusque.Enable(False)
    
    def SetRadioChoix(self, numRadio):
        if numRadio == 1 : self.radio_1.SetValue(True)
        if numRadio == 2 : self.radio_2.SetValue(True)
        if numRadio == 3 : self.radio_3.SetValue(True)
        if numRadio == 4 : self.radio_4.SetValue(True)
        if numRadio == 5 : self.radio_5.SetValue(True)
        self.OnRadioButton(None)
        
    def SetDates(self, date_debut, date_fin):
        if str(date_debut) == "3000-01-01" and str(date_fin) == "3000-01-01" :
            self.SetRadioChoix(5)
            return
        if date_debut != None and date_fin != None :
            self.SetDatePicker(self.ctrl_date_debut, date_debut)
            self.SetDatePicker(self.ctrl_date_fin, date_fin)
            self.SetRadioChoix(1)
        if date_debut != None and date_fin == None :
            self.SetDatePicker(self.ctrl_date_aPartir, date_debut)
            self.SetRadioChoix(2)
        if date_debut == None and date_fin != None :
            self.SetDatePicker(self.ctrl_date_jusque, date_fin)
            self.SetRadioChoix(3)
        if date_debut == None and date_fin == None :
            self.SetRadioChoix(4)
        

    def SetDatePicker(self, controle, date) :
        """ Met une date au format datetime dans un datePicker donné """
        annee = int(date.year)
        mois = int(date.month)-1
        jour = int(date.day)
        date = wx.DateTime()
        date.Set(jour, mois, annee)
        controle.SetValue(date)
        
    def GetDatePickerValue(self, controle):
        """ Renvoie la date au format datetime d'un datePicker """
        date_tmp = controle.GetValue()
        return datetime.date(date_tmp.GetYear(), date_tmp.GetMonth()+1, date_tmp.GetDay())

    def GetDates(self):
        """ Renvoie les dates des deux datepickers au format datetime """
        if self.radio_1.GetValue() == True :
            date_debut = self.GetDatePickerValue(self.ctrl_date_debut)
            date_fin = self.GetDatePickerValue(self.ctrl_date_fin)
        if self.radio_2.GetValue() == True :
            date_debut = self.GetDatePickerValue(self.ctrl_date_aPartir)
            date_fin = None
        if self.radio_3.GetValue() == True :
            date_debut = None
            date_fin = self.GetDatePickerValue(self.ctrl_date_jusque)
        if self.radio_4.GetValue() == True :
            date_debut = None
            date_fin = None
        if self.radio_5.GetValue() == True :
            date_debut = "3000-01-01"
            date_fin = "3000-01-01"
        return (date_debut, date_fin)
    
    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        if self.radio_1.GetValue() == True :
            date_debut = self.GetDatePickerValue(self.ctrl_date_debut)
            date_fin = self.GetDatePickerValue(self.ctrl_date_fin)
            if date_debut > date_fin :
                dlg = wx.MessageDialog(self, u"La date de début ne peut pas être supérieure à la date de fin !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            
        self.EndModal(wx.ID_OK)
        



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = MyDialog(None, date_debut=None, date_fin=None)
    frm.ShowModal()
    app.MainLoop()