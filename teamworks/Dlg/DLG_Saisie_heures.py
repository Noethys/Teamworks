#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import wx.lib.masked as masked
import datetime


class MyDialog(wx.Dialog):
    def __init__(self, parent, heureMin=None, heureMax=None):
        wx.Dialog.__init__(self, parent, -1, title=_(u"Amplitude horaire affichée"))
        self.heureMin = heureMin
        self.heureMax = heureMax
        
        self.static_sizer_staticbox = wx.StaticBox(self, -1, _(u"Amplitude horaire"))
        self.label_intro = wx.StaticText(self, -1, _(u"Veuillez saisir l'amplitude horaire à afficher par défaut\ndans le planning (Min=0:00 / max=23:55) :"))
        self.label_de = wx.StaticText(self, -1, _(u"De"))
        self.ctrl_heure_min = masked.TextCtrl(self, -1, "", style=wx.TE_CENTRE, mask = "##:##", validRegex   = "[0-2][0-9]:[0-5][0-9]")
        self.label_a = wx.StaticText(self, -1, u"à")
        self.ctrl_heure_max = masked.TextCtrl(self, -1, "", style=wx.TE_CENTRE, mask = "##:##", validRegex   = "[0-2][0-9]:[0-5][0-9]")
        
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_TEXT, self.OnTextHeureDebutText, self.ctrl_heure_min)
        self.Bind(wx.EVT_TEXT, self.OnTextHeureFinText, self.ctrl_heure_max)
        
        # Données par défaut
        if heureMin != None :
            heureMinStr = "%02d:%02d" % (self.heureMin.hour, self.heureMin.minute)
            self.ctrl_heure_min.SetValue(heureMinStr)
        if heureMax != None :
            heureMaxStr = "%02d:%02d" % (self.heureMax.hour, self.heureMax.minute)
            self.ctrl_heure_max.SetValue(heureMaxStr)
        
        
    def __set_properties(self):
        self.ctrl_heure_min.SetToolTip(wx.ToolTip(_(u"Saisissez ici l'heure minimale")))
        self.ctrl_heure_max.SetToolTip(wx.ToolTip(_(u"Saisissez ici l'heure maximale")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.ctrl_heure_min.SetMinSize((65, -1))
        self.ctrl_heure_min.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.ctrl_heure_min.SetCtrlParameters(invalidBackgroundColour = "PINK")
        self.ctrl_heure_max.SetMinSize((65, -1))
        self.ctrl_heure_max.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.ctrl_heure_max.SetCtrlParameters(invalidBackgroundColour = "PINK")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        static_sizer = wx.StaticBoxSizer(self.static_sizer_staticbox, wx.HORIZONTAL)
        grid_sizer_horaires = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 0, wx.LEFT|wx.RIGHT|wx.TOP, 10)
        grid_sizer_horaires.Add(self.label_de, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_horaires.Add(self.ctrl_heure_min, 0, 0, 0)
        grid_sizer_horaires.Add(self.label_a, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_horaires.Add(self.ctrl_heure_max, 0, 0, 0)
        static_sizer.Add(grid_sizer_horaires, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(static_sizer, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add((5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CentreOnScreen()

    def OnTextHeureDebutText(self, event):
        texte = event.GetString()
        controle = self.ctrl_heure_min

        validation = True
        texteBrut = controle.GetPlainValue()

        if texteBrut == "":
            validation = False

        # Vérifie chaque chiffre
        for chiffre in texteBrut:
            if chiffre != " ":
                if not (0 <= int(chiffre) <=9):
                    validation = False
            else:
                validation = False

        # Vérification de l'ensemble de la date
        if validation == True and len(texteBrut)==4:
            if not (0<= int(texteBrut[:2]) <=24):
                validation = False
            if not (0<= int(texteBrut[2:]) <=59):
                validation = False

            # Vérifie que heure_Fin est supérieure à Heure_Debut    
            if self.ctrl_heure_min.GetPlainValue() != "" and self.ctrl_heure_max.GetPlainValue() != "":
                delta = int(self.ctrl_heure_max.GetPlainValue()) - int(self.ctrl_heure_min.GetPlainValue())
                if delta < 1:
                    validation = False
                    dlg = wx.MessageDialog(self, _(u"L'heure de fin doit être supérieure à l'heure de début !"), "Information", wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
        
        # Si l'heure est valide, on passe à DATE_FIN
        if len(texteBrut)==4 and validation == True:
            self.ctrl_heure_max.SetFocus()

    def OnTextHeureFinText(self, event):
        texte = event.GetString()
        controle = self.ctrl_heure_max

        validation = True
        texteBrut = controle.GetPlainValue()

        if texteBrut == "":
            validation = False

        # Vérifie chaque chiffre
        for chiffre in texteBrut:
            if chiffre != " ":
                if not (0 <= int(chiffre) <=9):
                    validation = False
            else:
                validation = False

        # Vérification de l'ensemble de la date
        if validation == True and len(texteBrut)==4:
            if not (0<= int(texteBrut[:2]) <=24):
                validation = False
            if not (0<= int(texteBrut[2:]) <=59):
                validation = False
                
            # Vérifie que heure_Fin est supérieure à Heure_Debut    
            if self.ctrl_heure_min.GetPlainValue() != "" and self.ctrl_heure_max.GetPlainValue() != "":
                delta = int(self.ctrl_heure_max.GetPlainValue()) - int(self.ctrl_heure_min.GetPlainValue())
                if delta < 1:
                    validation = False
                    dlg = wx.MessageDialog(self, _(u"L'heure de fin doit être supérieure à l'heure de début !"), "Information", wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                
        # Si l'heure est valide, on passe à DATE_FIN
        if len(texteBrut)==4 and validation == True:
            self.bouton_ok.SetFocus()
            
    def ValidationDonnees(self):
        """ Validation des données """
        # Vérifie la validité des heures
        heureDebut = self.ctrl_heure_min.GetValue()
        heureFin = self.ctrl_heure_max.GetValue()
        if heureDebut == "  :  " :
            message = _(u"Vous devez saisir une heure de début.")
            wx.MessageBox(message, "Erreur de saisie")
            self.ctrl_heure_min.SetFocus()
            return False
        if heureDebut[3:] >= "60" or heureDebut[3] == " " or heureDebut[4] == " ":
            message = _(u"L'heure de début n'est pas valide.")
            wx.MessageBox(message, "Erreur de saisie")
            self.ctrl_heure_min.SetFocus()
            return False
        if heureDebut[4] != "5" and heureDebut[4] != "0" :
            message = _(u"Vous ne pouvez saisir qu'un horaire terminant par 0 ou 5. \nEx.: 10:05 ou 10:10 ou 10:15, etc... mais pas 10:02 !")
            wx.MessageBox(message, "Erreur de saisie")
            self.ctrl_heure_min.SetFocus()
            return False
        if heureFin == "  :  " :
            message = _(u"Vous devez saisir une heure de fin.")
            wx.MessageBox(message, "Erreur de saisie")
            self.ctrl_heure_max.SetFocus()
            return False
        if heureDebut < "00:00" or heureDebut > "24:00" :
            message = _(u"L'heure de début n'est pas valide")
            wx.MessageBox(message, "Erreur de saisie")
            self.ctrl_heure_min.SetFocus()
            return False
        if heureFin[3:] >= "60" or heureFin[3] == " " or heureFin[4] == " ":
            message = _(u"L'heure de fin n'est pas valide.")
            wx.MessageBox(message, "Erreur de saisie")
            self.ctrl_heure_max.SetFocus()
            return False
        if heureFin < "00:00" or heureFin > "24:00" :
            message = _(u"L'heure de fin n'est pas valide")
            wx.MessageBox(message, "Erreur de saisie")
            self.ctrl_heure_max.SetFocus()
            return False
        if heureFin[4] != "5" and heureFin[4] != "0" :
            message = _(u"Vous ne pouvez saisir qu'un horaire terminant par 0 ou 5. \nEx.: 10:05 ou 10:10 ou 10:15, etc... mais pas 10:02 !")
            wx.MessageBox(message, "Erreur de saisie")
            self.ctrl_heure_max.SetFocus()
            return False
        if heureDebut > heureFin :
            message = _(u"L'heure de fin doit être supérieure à l'heure de début !")
            wx.MessageBox(message, "Erreur de saisie")
            self.ctrl_heure_min.SetFocus()
            return False

        # Vérifie qu'il y a un delta de 15min entre l'heure de début et de fin
        HMin = datetime.timedelta(hours=int(heureDebut[:2]), minutes=int(heureDebut[3:]))
        HMax = datetime.timedelta(hours=int(heureFin[:2]), minutes=int(heureFin[3:]))
        delta = ((HMax - HMin).seconds)//60.0
        if delta < 60 :
            message = _(u"L'amplitude horaire doit être au minimum de 1 heure !")
            wx.MessageBox(message, "Erreur de saisie")
            self.ctrl_heure_min.SetFocus()
            return False
        
    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        # Validation des données
        validation = self.ValidationDonnees()
        if validation == False : return
        
        # Ferme la boîte de dialogue
        self.EndModal(wx.ID_OK) 
    
    def GetHeureMin(self):
        heureStr = self.ctrl_heure_min.GetValue()
        heureTuple = heureStr.split(":")
        heureDD = datetime.time(int(heureTuple[0]), int(heureTuple[1]))
        return heureDD

    def GetHeureMax(self):
        heureStr = self.ctrl_heure_max.GetValue()
        heureTuple = heureStr.split(":")
        heureDD = datetime.time(int(heureTuple[0]), int(heureTuple[1]))
        return heureDD
    

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = MyDialog(None, heureMin=datetime.time(8, 0), heureMax=datetime.time(20, 5))
    frm.ShowModal()
    app.MainLoop()
