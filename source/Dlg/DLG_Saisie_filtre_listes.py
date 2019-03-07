#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
import six
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_euros



class CTRL_Page_texte(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL) 
        self.radio_egal = wx.RadioButton(self, -1, _(u"Est égal à"), style=wx.RB_GROUP)
        self.ctrl_egal = wx.TextCtrl(self, -1, "", size=(200, -1))
        self.radio_different = wx.RadioButton(self, -1, _(u"Est différent de"))
        self.ctrl_different = wx.TextCtrl(self, -1, "", size=(200, -1))
        self.radio_contient = wx.RadioButton(self, -1, _(u"Contient"))
        self.ctrl_contient = wx.TextCtrl(self, -1, "", size=(200, -1))
        self.radio_contientpas = wx.RadioButton(self, -1, _(u"Ne contient pas"))
        self.ctrl_contientpas = wx.TextCtrl(self, -1, "", size=(200, -1))
        self.radio_vide = wx.RadioButton(self, -1, _(u"Est vide"))
        self.radio_pasvide = wx.RadioButton(self, -1, _(u"N'est pas vide"))
        
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_egal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_different)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_contient)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_contientpas)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_vide)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_pasvide)
        
        self.OnRadio(None) 
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=10, hgap=10)
        grid_sizer_egal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_egal.Add(self.radio_egal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_egal.Add(self.ctrl_egal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_egal, 1, wx.EXPAND, 0)
        grid_sizer_different = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_different.Add(self.radio_different, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_different.Add(self.ctrl_different, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_different, 1, wx.EXPAND, 0)
        grid_sizer_contient = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_contient.Add(self.radio_contient, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contient.Add(self.ctrl_contient, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_contient, 1, wx.EXPAND, 0)
        grid_sizer_contientpas = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_contientpas.Add(self.radio_contientpas, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contientpas.Add(self.ctrl_contientpas, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_contientpas, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.radio_vide, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.radio_pasvide, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnRadio(self, event): 
        self.ctrl_egal.Enable(self.radio_egal.GetValue())
        self.ctrl_different.Enable(self.radio_different.GetValue())
        self.ctrl_contient.Enable(self.radio_contient.GetValue())
        self.ctrl_contientpas.Enable(self.radio_contientpas.GetValue())
    
    def SetValeur(self, choix=None, criteres=None):
        if choix == "EGAL" : 
            self.radio_egal.SetValue(True)
            self.ctrl_egal.SetValue(criteres)
        if choix == "DIFFERENT" : 
            self.radio_different.SetValue(True)
            self.ctrl_different.SetValue(criteres)
        if choix == "CONTIENT" : 
            self.radio_contient.SetValue(True)
            self.ctrl_contient.SetValue(criteres)
        if choix == "CONTIENTPAS" : 
            self.radio_contientpas.SetValue(True)
            self.ctrl_contientpas.SetValue(criteres)
        if choix == "VIDE" : 
            self.radio_vide.SetValue(True)
        if choix == "PASVIDE" : 
            self.radio_pasvide.SetValue(True)
        self.OnRadio(None) 
    
    def GetValeur(self):
        choix, criteres = "", ""
        if self.radio_egal.GetValue() == True :
            choix = "EGAL"
            criteres = self.ctrl_egal.GetValue()
        if self.radio_different.GetValue() == True :
            choix = "DIFFERENT"
            criteres = self.ctrl_different.GetValue()
        if self.radio_contient.GetValue() == True :
            choix = "CONTIENT"
            criteres = self.ctrl_contient.GetValue()
        if self.radio_contientpas.GetValue() == True :
            choix = "CONTIENTPAS"
            criteres = self.ctrl_contientpas.GetValue()
        if self.radio_vide.GetValue() == True :
            choix = "VIDE"
        if self.radio_pasvide.GetValue() == True :
            choix = "PASVIDE"
        return choix, criteres

    def Validation(self):
        choix, criteres = self.GetValeur() 
        if choix not in ("VIDE", "PASVIDE") and criteres == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un texte !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True

    def Reinit(self):
        self.radio_egal.SetValue(True)
        self.ctrl_egal.SetValue("")
        self.ctrl_different.SetValue("")
        self.ctrl_contient.SetValue("")
        self.ctrl_contientpas.SetValue("")

# -------------------------------------------------------------------------------------------------------------------------------

class CTRL_Page_bool(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.radio_vrai = wx.RadioButton(self, -1, _(u"Est vrai"), style=wx.RB_GROUP)
        self.radio_faux = wx.RadioButton(self, -1, _(u"Est faux"))

        self.__do_layout()

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.radio_vrai, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.radio_faux, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def SetValeur(self, choix=None, criteres=None):
        if choix == "TRUE": self.radio_vrai.SetValue(True)
        if choix == "FALSE": self.radio_faux.SetValue(True)

    def GetValeur(self):
        choix, criteres = "", ""
        if self.radio_vrai.GetValue() == True:
            choix = "TRUE"
        if self.radio_faux.GetValue() == True:
            choix = "FALSE"
        return choix, criteres

    def Validation(self):
        return True

    def Reinit(self):
        self.radio_vrai.SetValue(True)


# -------------------------------------------------------------------------------------------------------------------------------


class CTRL_Page_entier(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL) 
        self.radio_egal = wx.RadioButton(self, -1, _(u"Est égal à"), style=wx.RB_GROUP)
        self.ctrl_egal = wx.SpinCtrl(self, -1, "", min=0, max=999999)
        self.radio_different = wx.RadioButton(self, -1, _(u"Est différent de"))
        self.ctrl_different = wx.SpinCtrl(self, -1, "", min=0, max=999999)
        self.radio_sup = wx.RadioButton(self, -1, _(u"Est supérieur à"))
        self.ctrl_sup = wx.SpinCtrl(self, -1, "", min=0, max=999999)
        self.radio_supegal = wx.RadioButton(self, -1, _(u"Est supérieur ou égal à"))
        self.ctrl_supegal = wx.SpinCtrl(self, -1, "", min=0, max=999999)
        self.radio_inf = wx.RadioButton(self, -1, _(u"Est inférieur à"))
        self.ctrl_inf = wx.SpinCtrl(self, -1, "", min=0, max=999999)
        self.radio_infegal = wx.RadioButton(self, -1, _(u"Est inférieur ou égal à"))
        self.ctrl_infegal = wx.SpinCtrl(self, -1, "", min=0, max=999999)
        self.radio_compris = wx.RadioButton(self, -1, _(u"Est compris entre"))
        self.ctrl_min = wx.SpinCtrl(self, -1, "", min=0, max=999999)
        self.label_et = wx.StaticText(self, -1, _(u"et"))
        self.ctrl_max = wx.SpinCtrl(self, -1, "", min=0, max=999999)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_egal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_different)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_sup)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_supegal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_inf)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_infegal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_compris)
        
        self.OnRadio(None) 
        
    def __set_properties(self):
        self.ctrl_egal.SetMinSize((80, -1))
        self.ctrl_different.SetMinSize((80, -1))
        self.ctrl_sup.SetMinSize((80, -1))
        self.ctrl_supegal.SetMinSize((80, -1))
        self.ctrl_inf.SetMinSize((80, -1))
        self.ctrl_infegal.SetMinSize((80, -1))
        self.ctrl_min.SetMinSize((80, -1))
        self.ctrl_max.SetMinSize((80, -1))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=10, hgap=10)
        grid_sizer_compris = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_infegal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_inf = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_supegal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_sup = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_different = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_egal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_egal.Add(self.radio_egal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_egal.Add(self.ctrl_egal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_egal, 1, wx.EXPAND, 0)
        grid_sizer_different.Add(self.radio_different, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_different.Add(self.ctrl_different, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_different, 1, wx.EXPAND, 0)
        grid_sizer_sup.Add(self.radio_sup, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_sup.Add(self.ctrl_sup, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_sup, 1, wx.EXPAND, 0)
        grid_sizer_supegal.Add(self.radio_supegal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_supegal.Add(self.ctrl_supegal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_supegal, 1, wx.EXPAND, 0)
        grid_sizer_inf.Add(self.radio_inf, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_inf.Add(self.ctrl_inf, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_inf, 1, wx.EXPAND, 0)
        grid_sizer_infegal.Add(self.radio_infegal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infegal.Add(self.ctrl_infegal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_infegal, 1, wx.EXPAND, 0)
        grid_sizer_compris.Add(self.radio_compris, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_compris.Add(self.ctrl_min, 0, 0, 0)
        grid_sizer_compris.Add(self.label_et, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_compris.Add(self.ctrl_max, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_compris, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnRadio(self, event): 
        self.ctrl_egal.Enable(self.radio_egal.GetValue())
        self.ctrl_different.Enable(self.radio_different.GetValue())
        self.ctrl_sup.Enable(self.radio_sup.GetValue())
        self.ctrl_supegal.Enable(self.radio_supegal.GetValue())
        self.ctrl_inf.Enable(self.radio_inf.GetValue())
        self.ctrl_infegal.Enable(self.radio_infegal.GetValue())
        self.ctrl_min.Enable(self.radio_compris.GetValue())
        self.ctrl_max.Enable(self.radio_compris.GetValue())
    
    def SetValeur(self, choix=None, criteres=None):
        if choix == "EGAL" : 
            self.radio_egal.SetValue(True)
            self.ctrl_egal.SetValue(int(criteres))
        if choix == "DIFFERENT" : 
            self.radio_different.SetValue(True)
            self.ctrl_different.SetValue(int(criteres))
        if choix == "SUP" : 
            self.radio_sup.SetValue(True)
            self.ctrl_sup.SetValue(int(criteres))
        if choix == "SUPEGAL" : 
            self.radio_supegal.SetValue(True)
            self.ctrl_supegal.SetValue(int(criteres))
        if choix == "INF" : 
            self.radio_inf.SetValue(True)
            self.ctrl_inf.SetValue(int(criteres))
        if choix == "INFEGAL" : 
            self.radio_infegal.SetValue(True)
            self.ctrl_infegal.SetValue(int(criteres))
        if choix == "COMPRIS" : 
            self.radio_compris.SetValue(True)
            min, max = criteres.split(";")
            self.ctrl_min.SetValue(int(min))
            self.ctrl_max.SetValue(int(max))
        self.OnRadio(None) 
    
    def GetValeur(self):
        choix, criteres = "", ""
        if self.radio_egal.GetValue() == True :
            choix = "EGAL"
            criteres = str(self.ctrl_egal.GetValue())
        if self.radio_different.GetValue() == True :
            choix = "DIFFERENT"
            criteres = str(self.ctrl_different.GetValue())
        if self.radio_sup.GetValue() == True :
            choix = "SUP"
            criteres = str(self.ctrl_sup.GetValue())
        if self.radio_supegal.GetValue() == True :
            choix = "SUPEGAL"
            criteres = str(self.ctrl_supegal.GetValue())
        if self.radio_inf.GetValue() == True :
            choix = "INF"
            criteres = str(self.ctrl_inf.GetValue())
        if self.radio_infegal.GetValue() == True :
            choix = "INFEGAL"
            criteres = str(self.ctrl_infegal.GetValue())
        if self.radio_compris.GetValue() == True :
            choix = "COMPRIS"
            criteres = "%d;%d" % (self.ctrl_min.GetValue(), self.ctrl_max.GetValue())
        return choix, criteres

    def Validation(self):
        return True

    def Reinit(self):
        self.radio_egal.SetValue(True)
        self.ctrl_egal.SetValue(0)
        self.ctrl_different.SetValue(0)
        self.ctrl_sup.SetValue(0)
        self.ctrl_supegal.SetValue(0)
        self.ctrl_inf.SetValue(0)
        self.ctrl_infegal.SetValue(0)
        self.ctrl_min.SetValue(0)
        self.ctrl_max.SetValue(0)

# -------------------------------------------------------------------------------------------------------------------------------

class CTRL_Page_montant(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL) 
        self.radio_egal = wx.RadioButton(self, -1, _(u"Est égal à"), style=wx.RB_GROUP)
        self.ctrl_egal = CTRL_Saisie_euros.CTRL(self)
        self.radio_different = wx.RadioButton(self, -1, _(u"Est différent de"))
        self.ctrl_different = CTRL_Saisie_euros.CTRL(self)
        self.radio_sup = wx.RadioButton(self, -1, _(u"Est supérieur à"))
        self.ctrl_sup = CTRL_Saisie_euros.CTRL(self)
        self.radio_supegal = wx.RadioButton(self, -1, _(u"Est supérieur ou égal à"))
        self.ctrl_supegal = CTRL_Saisie_euros.CTRL(self)
        self.radio_inf = wx.RadioButton(self, -1, _(u"Est inférieur à"))
        self.ctrl_inf = CTRL_Saisie_euros.CTRL(self)
        self.radio_infegal = wx.RadioButton(self, -1, _(u"Est inférieur ou égal à"))
        self.ctrl_infegal = CTRL_Saisie_euros.CTRL(self)
        self.radio_compris = wx.RadioButton(self, -1, _(u"Est compris entre"))
        self.ctrl_min = CTRL_Saisie_euros.CTRL(self)
        self.label_et = wx.StaticText(self, -1, _(u"et"))
        self.ctrl_max = CTRL_Saisie_euros.CTRL(self)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_egal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_different)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_sup)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_supegal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_inf)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_infegal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_compris)
        
        self.OnRadio(None) 
        
    def __set_properties(self):
        self.ctrl_egal.SetMinSize((80, -1))
        self.ctrl_different.SetMinSize((80, -1))
        self.ctrl_sup.SetMinSize((80, -1))
        self.ctrl_supegal.SetMinSize((80, -1))
        self.ctrl_inf.SetMinSize((80, -1))
        self.ctrl_infegal.SetMinSize((80, -1))
        self.ctrl_min.SetMinSize((80, -1))
        self.ctrl_max.SetMinSize((80, -1))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=10, hgap=10)
        grid_sizer_compris = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_infegal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_inf = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_supegal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_sup = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_different = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_egal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_egal.Add(self.radio_egal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_egal.Add(self.ctrl_egal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_egal, 1, wx.EXPAND, 0)
        grid_sizer_different.Add(self.radio_different, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_different.Add(self.ctrl_different, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_different, 1, wx.EXPAND, 0)
        grid_sizer_sup.Add(self.radio_sup, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_sup.Add(self.ctrl_sup, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_sup, 1, wx.EXPAND, 0)
        grid_sizer_supegal.Add(self.radio_supegal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_supegal.Add(self.ctrl_supegal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_supegal, 1, wx.EXPAND, 0)
        grid_sizer_inf.Add(self.radio_inf, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_inf.Add(self.ctrl_inf, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_inf, 1, wx.EXPAND, 0)
        grid_sizer_infegal.Add(self.radio_infegal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infegal.Add(self.ctrl_infegal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_infegal, 1, wx.EXPAND, 0)
        grid_sizer_compris.Add(self.radio_compris, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_compris.Add(self.ctrl_min, 0, 0, 0)
        grid_sizer_compris.Add(self.label_et, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_compris.Add(self.ctrl_max, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_compris, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnRadio(self, event): 
        self.ctrl_egal.Enable(self.radio_egal.GetValue())
        self.ctrl_different.Enable(self.radio_different.GetValue())
        self.ctrl_sup.Enable(self.radio_sup.GetValue())
        self.ctrl_supegal.Enable(self.radio_supegal.GetValue())
        self.ctrl_inf.Enable(self.radio_inf.GetValue())
        self.ctrl_infegal.Enable(self.radio_infegal.GetValue())
        self.ctrl_min.Enable(self.radio_compris.GetValue())
        self.ctrl_max.Enable(self.radio_compris.GetValue())
    
    def SetValeur(self, choix=None, criteres=None):
        if choix == "EGAL" : 
            self.radio_egal.SetValue(True)
            self.ctrl_egal.SetMontant(float(criteres))
        if choix == "DIFFERENT" : 
            self.radio_different.SetValue(True)
            self.ctrl_different.SetMontant(float(criteres))
        if choix == "SUP" : 
            self.radio_sup.SetValue(True)
            self.ctrl_sup.SetMontant(float(criteres))
        if choix == "SUPEGAL" : 
            self.radio_supegal.SetValue(True)
            self.ctrl_supegal.SetMontant(float(criteres))
        if choix == "INF" : 
            self.radio_inf.SetValue(True)
            self.ctrl_inf.SetMontant(float(criteres))
        if choix == "INFEGAL" : 
            self.radio_infegal.SetValue(True)
            self.ctrl_infegal.SetMontant(float(criteres))
        if choix == "COMPRIS" : 
            self.radio_compris.SetValue(True)
            min, max = criteres.split(";")
            self.ctrl_min.SetMontant(float(min))
            self.ctrl_max.SetMontant(float(max))
        self.OnRadio(None) 
    
    def GetValeur(self):
        choix, criteres = "", ""
        if self.radio_egal.GetValue() == True :
            choix = "EGAL"
            criteres = str(self.ctrl_egal.GetMontant())
        if self.radio_different.GetValue() == True :
            choix = "DIFFERENT"
            criteres = str(self.ctrl_different.GetMontant())
        if self.radio_sup.GetValue() == True :
            choix = "SUP"
            criteres = str(self.ctrl_sup.GetMontant())
        if self.radio_supegal.GetValue() == True :
            choix = "SUPEGAL"
            criteres = str(self.ctrl_supegal.GetMontant())
        if self.radio_inf.GetValue() == True :
            choix = "INF"
            criteres = str(self.ctrl_inf.GetMontant())
        if self.radio_infegal.GetValue() == True :
            choix = "INFEGAL"
            criteres = str(self.ctrl_infegal.GetMontant())
        if self.radio_compris.GetValue() == True :
            choix = "COMPRIS"
            criteres = "%d;%d" % (self.ctrl_min.GetMontant(), self.ctrl_max.GetMontant())
        return choix, criteres

    def Validation(self):
        return True

    def Reinit(self):
        self.radio_egal.SetValue(True)
        self.ctrl_egal.SetValue("0.0")
        self.ctrl_different.SetValue("0.0")
        self.ctrl_sup.SetValue("0.0")
        self.ctrl_supegal.SetValue("0.0")
        self.ctrl_inf.SetValue("0.0")
        self.ctrl_infegal.SetValue("0.0")
        self.ctrl_min.SetValue("0.0")
        self.ctrl_max.SetValue("0.0")

# -------------------------------------------------------------------------------------------------------------------------------


class CTRL_Page_date(wx.Panel):
    def __init__(self, parent, heure=False):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.heure = heure
        self.radio_egal = wx.RadioButton(self, -1, _(u"Est égal à"), style=wx.RB_GROUP)
        self.ctrl_egal = CTRL_Saisie_date.Date2(self, heure=heure)
        self.radio_different = wx.RadioButton(self, -1, _(u"Est différent de"))
        self.ctrl_different = CTRL_Saisie_date.Date2(self, heure=heure)
        self.radio_sup = wx.RadioButton(self, -1, _(u"Est supérieur à"))
        self.ctrl_sup = CTRL_Saisie_date.Date2(self, heure=heure)
        self.radio_supegal = wx.RadioButton(self, -1, _(u"Est supérieur ou égal à"))
        self.ctrl_supegal = CTRL_Saisie_date.Date2(self, heure=heure)
        self.radio_inf = wx.RadioButton(self, -1, _(u"Est inférieur à"))
        self.ctrl_inf = CTRL_Saisie_date.Date2(self, heure=heure)
        self.radio_infegal = wx.RadioButton(self, -1, _(u"Est inférieur ou égal à"))
        self.ctrl_infegal = CTRL_Saisie_date.Date2(self, heure=heure)
        self.radio_compris = wx.RadioButton(self, -1, _(u"Est compris entre"))
        self.ctrl_min = CTRL_Saisie_date.Date2(self, heure=heure)
        self.label_et = wx.StaticText(self, -1, _(u"et"))
        self.ctrl_max = CTRL_Saisie_date.Date2(self, heure=heure)

        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_egal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_different)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_sup)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_supegal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_inf)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_infegal)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_compris)
        
        self.OnRadio(None)

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=1, vgap=10, hgap=10)
        grid_sizer_compris = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_infegal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_inf = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_supegal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_sup = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_different = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_egal = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_egal.Add(self.radio_egal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_egal.Add(self.ctrl_egal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_egal, 1, wx.EXPAND, 0)
        grid_sizer_different.Add(self.radio_different, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_different.Add(self.ctrl_different, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_different, 1, wx.EXPAND, 0)
        grid_sizer_sup.Add(self.radio_sup, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_sup.Add(self.ctrl_sup, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_sup, 1, wx.EXPAND, 0)
        grid_sizer_supegal.Add(self.radio_supegal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_supegal.Add(self.ctrl_supegal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_supegal, 1, wx.EXPAND, 0)
        grid_sizer_inf.Add(self.radio_inf, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_inf.Add(self.ctrl_inf, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_inf, 1, wx.EXPAND, 0)
        grid_sizer_infegal.Add(self.radio_infegal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infegal.Add(self.ctrl_infegal, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_infegal, 1, wx.EXPAND, 0)
        grid_sizer_compris.Add(self.radio_compris, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_compris.Add(self.ctrl_min, 0, 0, 0)
        grid_sizer_compris.Add(self.label_et, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_compris.Add(self.ctrl_max, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_compris, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnRadio(self, event): 
        self.ctrl_egal.Enable(self.radio_egal.GetValue())
        self.ctrl_different.Enable(self.radio_different.GetValue())
        self.ctrl_sup.Enable(self.radio_sup.GetValue())
        self.ctrl_supegal.Enable(self.radio_supegal.GetValue())
        self.ctrl_inf.Enable(self.radio_inf.GetValue())
        self.ctrl_infegal.Enable(self.radio_infegal.GetValue())
        self.ctrl_min.Enable(self.radio_compris.GetValue())
        self.ctrl_max.Enable(self.radio_compris.GetValue())
    
    def SetValeur(self, choix=None, criteres=None):
        if choix == "EGAL" : 
            self.radio_egal.SetValue(True)
            self.ctrl_egal.SetDate(criteres)
        if choix == "DIFFERENT" : 
            self.radio_different.SetValue(True)
            self.ctrl_different.SetDate(criteres)
        if choix == "SUP" : 
            self.radio_sup.SetValue(True)
            self.ctrl_sup.SetDate(criteres)
        if choix == "SUPEGAL" : 
            self.radio_supegal.SetValue(True)
            self.ctrl_supegal.SetDate(criteres)
        if choix == "INF" : 
            self.radio_inf.SetValue(True)
            self.ctrl_inf.SetDate(criteres)
        if choix == "INFEGAL" : 
            self.radio_infegal.SetValue(True)
            self.ctrl_infegal.SetDate(criteres)
        if choix == "COMPRIS" : 
            self.radio_compris.SetValue(True)
            min, max = criteres.split(";")
            self.ctrl_min.SetDate(min)
            self.ctrl_max.SetDate(max)
        self.OnRadio(None) 
    
    def GetValeur(self):
        choix, criteres = "", ""
        if self.radio_egal.GetValue() == True :
            choix = "EGAL"
            criteres = (self.ctrl_egal.GetDate())
        if self.radio_different.GetValue() == True :
            choix = "DIFFERENT"
            criteres = str(self.ctrl_different.GetDate())
        if self.radio_sup.GetValue() == True :
            choix = "SUP"
            criteres = str(self.ctrl_sup.GetDate())
        if self.radio_supegal.GetValue() == True :
            choix = "SUPEGAL"
            criteres = str(self.ctrl_supegal.GetDate())
        if self.radio_inf.GetValue() == True :
            choix = "INF"
            criteres = str(self.ctrl_inf.GetDate())
        if self.radio_infegal.GetValue() == True :
            choix = "INFEGAL"
            criteres = str(self.ctrl_infegal.GetDate())
        if self.radio_compris.GetValue() == True :
            choix = "COMPRIS"
            criteres = "%s;%s" % (self.ctrl_min.GetDate(), self.ctrl_max.GetDate())
        return choix, criteres

    def Validation(self):
        choix, criteres = self.GetValeur() 
        if criteres == None :
            if self.heure == False :
                message = _(u"Vous devez obligatoirement saisir une date !")
            else :
                message = _(u"Vous devez obligatoirement saisir une date et une heure !")
            dlg = wx.MessageDialog(self, message, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return True

    def Reinit(self):
        self.radio_egal.SetValue(True)
        self.ctrl_egal.SetDate(None)
        self.ctrl_different.SetDate(None)
        self.ctrl_sup.SetDate(None)
        self.ctrl_supegal.SetDate(None)
        self.ctrl_inf.SetDate(None)
        self.ctrl_infegal.SetDate(None)
        self.ctrl_min.SetDate(None)
        self.ctrl_max.SetDate(None)


# -------------------------------------------------------------------------------------------------------------------------------

class CTRL_Page_vide(wx.Panel):
    def __init__(self, parent, texte=u""):
        wx.Panel.__init__(self, parent, id=-1) 
        self.label_titre = wx.StaticText(self, -1, texte)
        grid_sizer = wx.FlexGridSizer(rows=1, cols=1, vgap=5, hgap=5)
        grid_sizer.Add(self.label_titre, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer.AddGrowableRow(0)
        grid_sizer.AddGrowableCol(0)
        self.SetSizer(grid_sizer)
        grid_sizer.Fit(self)

    def GetValeur(self):
        return None

    def Validation(self):
        dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun champ à filtrer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return False

    def Reinit(self):
        pass

# ------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Titre(wx.Panel):
    def __init__(self, parent, titre=u"", image=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.SIMPLE_BORDER) 
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.ctrl_image = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/32x32/%s" % image), wx.BITMAP_TYPE_ANY))
        if len(titre) > 40 :
            titre = titre[:40] + "..."
        self.label_titre = wx.StaticText(self, -1, titre)
        self.label_titre.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        grid_sizer = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer.Add(self.ctrl_image, 0, wx.LEFT|wx.TOP|wx.BOTTOM, 5)
        grid_sizer.Add(self.label_titre, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer.AddGrowableCol(1)
        self.SetSizer(grid_sizer)
        grid_sizer.Fit(self)

    def SetTitre(self, titre=""):
        self.label_titre.SetLabel(titre)
        
# ------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Page(wx.Panel):
    def __init__(self, parent, typeDonnee=None, titre=u""):
        wx.Panel.__init__(self, parent, id=-1, style=wx.SIMPLE_BORDER) 
        self.titre = titre
        
        # Titre
        if typeDonnee == "texte" : image = "Texte_ligne.png"
        elif typeDonnee == "bool": image = "Ctrl_coche.png"
        elif typeDonnee == "entier" : image = "Ctrl_nombre.png"
        elif typeDonnee == "montant" : image = "Euro.png"
        elif typeDonnee == "date" : image = "Jour.png"
        elif typeDonnee == "dateheure" : image = "Jour.png"
        else : image = None
        
        if typeDonnee != "vide" :
            self.ctrl_titre = CTRL_Titre(self, titre, image)
        else :
            self.ctrl_titre = (0, 0)
        self.typeDonnee = typeDonnee
        
        # Contenu
        if typeDonnee == "texte" : 
            self.ctrl_contenu = CTRL_Page_texte(self)
        elif typeDonnee == "bool" :
            self.ctrl_contenu = CTRL_Page_bool(self)
        elif typeDonnee == "entier" : 
            self.ctrl_contenu = CTRL_Page_entier(self)
        elif typeDonnee == "montant" : 
            self.ctrl_contenu = CTRL_Page_montant(self)
        elif typeDonnee == "date" : 
            self.ctrl_contenu = CTRL_Page_date(self)
        elif typeDonnee == "dateheure" :
            self.ctrl_contenu = CTRL_Page_date(self, heure=True)
        else :
            self.ctrl_contenu = CTRL_Page_vide(self, texte=_(u"Veuillez sélectionner un champ disponible dans la liste !"))

        grid_sizer = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer.Add(self.ctrl_titre, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer.Add(self.ctrl_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer.AddGrowableCol(0)
        grid_sizer.AddGrowableRow(1)
        self.SetSizer(grid_sizer)
        grid_sizer.Fit(self)
    
    def SetTitre(self, titre=""):
        if self.typeDonnee != "vide" :
            self.ctrl_titre.SetTitre(titre)        
        
    def SetValeur(self, choix="", criteres=""):
        self.ctrl_contenu.SetValeur(choix, criteres)
    
    def GetValeur(self):
        return self.ctrl_contenu.GetValeur() 
    
    def Validation(self):
        return self.ctrl_contenu.Validation() 
    
    def GetTypeDonnee(self):
        return self.typeDonnee
    
    def GetCode(self):
        return self.code
    
    def Reinit(self):
        self.ctrl_contenu.Reinit() 

# -------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Champs(wx.TreeCtrl):
    def __init__(self, parent, ctrl_listview=None):
        wx.TreeCtrl.__init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.TR_HIDE_ROOT | wx.TR_NO_BUTTONS)
        self.parent = parent
        self.ctrl_listview = ctrl_listview
        self.SetMinSize((320, 50))

        # Création de l'ImageList
        il = wx.ImageList(16, 16)
        self.dictImages = {}
        
        liste_images = [
            ("categorie", "Dossier.png"),
            ("texte", "Texte_ligne.png"),
            ("bool", "Ctrl_coche.png"),
            ("entier", "Ctrl_nombre.png"),
            ("montant", "Euro.png"),
            ("date", "Jour.png"),
            ("dateheure", "Jour.png"),
            ]
        self.dictImages = {}
        self.il = wx.ImageList(32, 32)
        for typeDonnee, image in liste_images :
            self.dictImages[typeDonnee] = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/32x32/%s" % image), wx.BITMAP_TYPE_ANY))
        self.AssignImageList(self.il)

        # Création de la racine
        self.root = self.AddRoot("Racine")

        # Récupération des champs disponibles
        self.listeCategories = [
            ("speciaux", _(u"Filtres spéciaux")),
            ("colonnes", _(u"Filtres de colonnes")),
            ]
            
        self.dictChamps = {}
        for codeCategorie, labelCategorie in self.listeCategories :
            self.dictChamps[codeCategorie] = []
        
        # -------- Champs spéciaux -----------
        
        # Champ Inscrits/Présents
        code = None
        if self.ctrl_listview != None :
            for colonne in self.ctrl_listview.listeColonnes :
                if colonne.valueGetter == "IDfamille" :
                    code = "famille"
                    break
                if colonne.valueGetter == "IDindividu" :
                    code = "individu"
                    break
        if code != None :
            titre = _(u"Inscrits/Présents")
            self.dictChamps["speciaux"].append({"code" : code, "typeDonnee" : "inscrits", "titre" : titre})

        # Champ Cotisations
        # code = None
        # if self.ctrl_listview != None:
        #     for colonne in self.ctrl_listview.listeColonnes:
        #         if colonne.valueGetter == "IDfamille":
        #             code = "famille"
        #             break
        #         if colonne.valueGetter == "IDindividu":
        #             code = "individu"
        #             break
        # if code != None:
        #     titre = _(u"Cotisations")
        #     self.dictChamps["speciaux"].append({"code": code, "typeDonnee": "cotisations", "titre": titre})

        # --------------- Champs des colonnes --------------
        if self.ctrl_listview != None :
            for colonne in self.ctrl_listview.listeColonnes :
                codeColonne = colonne.valueGetter
                if hasattr(colonne, "typeDonnee"):
                    typeDonnee = colonne.typeDonnee
                else :
                    typeDonnee = None
                titre = colonne.title
                if titre == "" :
                    titre = codeColonne
                if type(titre) in (str, six.text_type) :
                    self.dictChamps["colonnes"].append({"code" : codeColonne, "typeDonnee" : typeDonnee, "titre" : titre})

        # Remplissage
        self.dictItems = {}
        for codeCategorie, labelCategorie in self.listeCategories :
            if len(self.dictChamps[codeCategorie]) > 0 :
                
                # Création de la branche Catégorie
                categorie = self.AppendItem(self.root, labelCategorie)
                self.SetItemImage(categorie, self.dictImages["categorie"], which=wx.TreeItemIcon_Normal)
                self.SetItemBold(categorie, True)
                
                # Création des branches champs
                for dictChamp in self.dictChamps[codeCategorie] :
                    item = self.AppendItem(categorie, dictChamp["titre"])
                    if 'phoenix' in wx.PlatformInfo:
                        self.SetItemData(item, dictChamp)
                    else :
                        self.SetPyData(item, dictChamp)
                    if dictChamp["typeDonnee"] != None :
                        self.SetItemImage(item, self.dictImages[dictChamp["typeDonnee"]], which=wx.TreeItemIcon_Normal)
                    self.dictItems[dictChamp["code"]] = item
        
        wx.CallAfter(self.Init)
    
    def Init(self):
        self.ExpandAll()
        self.EnsureVisible(self.GetFirstChild(self.root)[0])
        
    def GetDonnees(self):
        item = self.GetSelection()
        if 'phoenix' in wx.PlatformInfo:
            dictChamp = self.GetItemData(item)
        else:
            dictChamp = self.GetPyData(item)
        return dictChamp
    
    def GetCode(self):
        dictChamp = self.GetDonnees() 
        if dictChamp == None :
            return None
        else :
            return dictChamp["code"]
        
    def SetCode(self, code=""):
        if code in self.dictItems :
            self.SelectItem(self.dictItems[code])
    
    def GetTitre(self):
        dictChamp = self.GetDonnees() 
        if dictChamp == None :
            return None
        else :
            return dictChamp["titre"]

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Filtres(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1) 
        
        self.listeTypesDonnees = ["vide", "texte", "bool", "entier", "montant", "date", "dateheure"]
        
        # Création des pages
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.listePages = []
        for typeDonnee in self.listeTypesDonnees :
            page = CTRL_Page(self, typeDonnee=typeDonnee)
            page.Show(False)
            sizer.Add(page, 1, wx.EXPAND, 0)
            self.listePages.append((typeDonnee, page))
        self.SetSizer(sizer)
        sizer.Fit(self)
        
        # Affiche la page vide
        self.SetSelection(typeDonnee="vide")

    def SetSelection(self, code="", typeDonnee="", titre=""):
        for typePage, page in self.listePages :
            if typePage == typeDonnee :
                page.Reinit()
                page.Show(True)
                page.SetTitre(titre)
            else :
                page.Show(False)
        self.Layout() 
            
    def GetPage(self):
        for codePage, page in self.listePages :
            if page.IsShown() :
                return page
        return None
    
    def SetValeur(self, choix="", criteres=""):
        page = self.GetPage()
        page.SetValeur(choix, criteres)
    
    def GetValeur(self):
        page = self.GetPage()
        return page.GetValeur() 
    
    def GetTypeDonnee(self):
        page = self.GetPage()
        return page.GetTypeDonnee() 
    
    def GetTitre(self):
        page = self.GetPage()
        return page.titre
    
    def Validation(self):
        page = self.GetPage()
        return page.Validation() 

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, ctrl_listview=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent      
        self.ctrl_listview = ctrl_listview
        self.SetTitle(_(u"Saisie d'un filtre"))  
        
        self.ctrl_champs = CTRL_Champs(self, ctrl_listview=ctrl_listview)
        self.ctrl_filtres = CTRL_Filtres(self)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnChoixChamp, self.ctrl_champs)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.SetMinSize((820, 550))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.ctrl_champs, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.ctrl_filtres, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((15, 15), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()
            
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOk(self, event):
        # Vérification des données saisies
        if self.ctrl_filtres.Validation() == False :
            return
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def OnChoixChamp(self, event):
        donnees = self.ctrl_champs.GetDonnees()
        if donnees == None :
            code = None
            typeDonnee = "vide"
            titre = None
        else :
            code = donnees["code"]
            typeDonnee = donnees["typeDonnee"]
            titre = donnees["titre"]
        self.ctrl_filtres.SetSelection(code=code, typeDonnee=typeDonnee, titre=titre)
        
    def GetValeur(self):
        # Récupération des valeurs
        return self.ctrl_filtres.GetValeur() 
    
    def SetValeur(self, choix="", criteres=""):
        self.ctrl_filtres.SetValeur(choix, criteres)
        
    def GetCode(self):
        code = self.ctrl_champs.GetCode() 
        return code

    def SetCode(self, code=""):
        self.SetTitle(_(u"Modification d'un filtre"))  
        self.ctrl_champs.SetCode(code) 
        self.OnChoixChamp(None)

    def GetTypeDonnee(self):
        return self.ctrl_filtres.GetTypeDonnee() 
    
    def GetTitre(self):
        return self.ctrl_champs.GetTitre() 



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    # Test d'importation
    #dlg.SetCode("famille")
    #dlg.SetValeur("CONTIENT", _(u"Ceci est un test  !"))

    if dlg.ShowModal() == wx.ID_OK :
        print("Code =", dlg.GetCode())
        print("Valeur =", dlg.GetValeur())
    app.MainLoop()
