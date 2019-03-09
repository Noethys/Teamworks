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
import GestionDB
import datetime
import FonctionsPerso
from Ol import OL_candidatures
from Ol import OL_entretiens



class Panel(wx.Panel):
    def __init__(self, parent, id=-1, IDpersonne=0):
        wx.Panel.__init__(self, parent, id, name="page_candidatures", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDpersonne = IDpersonne

        # Widgets
        self.staticBox_candidatures = wx.StaticBox(self, -1, _(u"Candidatures"))
        self.ctrl_candidatures = OL_candidatures.ListView(self, id=-1,  name="OL_candidatures", IDpersonne=IDpersonne, colorerSalaries=False, modeAffichage = "sans_nom", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_candidatures.SetMinSize((20, 20))
        self.ctrl_candidatures.MAJ()
        self.bouton_candidatures_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_candidatures_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_candidatures_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
        
        self.staticBox_entretiens = wx.StaticBox(self, -1, _(u"Entretiens"))
        self.ctrl_entretiens = OL_entretiens.ListView(self, id=-1,  name="OL_entretiens", IDpersonne=IDpersonne, colorerSalaries=False, modeAffichage="sans_nom", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_entretiens.SetMinSize((20, 20))
        self.ctrl_entretiens.MAJ()
        self.bouton_entretiens_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_entretiens_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_entretiens_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
        
        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjoutCandidature, self.bouton_candidatures_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifCandidature, self.bouton_candidatures_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprCandidature, self.bouton_candidatures_supprimer)
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjoutEntretien, self.bouton_entretiens_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifEntretien, self.bouton_entretiens_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprEntretien, self.bouton_entretiens_supprimer)

    def __set_properties(self):
        self.bouton_candidatures_ajouter.SetToolTipString(_(u"Cliquez ici pour saisir uune nouvelle candidature"))
        self.bouton_candidatures_modifier.SetToolTipString(_(u"Cliquez ici pour modifier la candidature sélectionnée dans la liste"))
        self.bouton_candidatures_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer la candidature sélectionnée dans la liste"))
        self.bouton_entretiens_ajouter.SetToolTipString(_(u"Cliquez ici pour saisir un nouvel entretien"))
        self.bouton_entretiens_modifier.SetToolTipString(_(u"Cliquez ici pour modifier l'entretien sélectionné dans la liste"))
        self.bouton_entretiens_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer l'entretien sélectionné dans la liste"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        # --------------
        # Candidatures
        staticBox_candidatures = wx.StaticBoxSizer(self.staticBox_candidatures, wx.VERTICAL)
        grid_sizer_candidatures = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_candidatures.Add(self.ctrl_candidatures, 1, wx.EXPAND, 0)
        grid_sizer_boutons_candidatures = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_candidatures.Add(self.bouton_candidatures_ajouter, 0, 0, 0)
        grid_sizer_boutons_candidatures.Add(self.bouton_candidatures_modifier, 0, 0, 0)
        grid_sizer_boutons_candidatures.Add(self.bouton_candidatures_supprimer, 0, 0, 0)
        grid_sizer_candidatures.Add(grid_sizer_boutons_candidatures, 1, wx.EXPAND, 0)
        grid_sizer_candidatures.AddGrowableRow(0)
        grid_sizer_candidatures.AddGrowableCol(0)
        staticBox_candidatures.Add(grid_sizer_candidatures, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticBox_candidatures, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 5)
        
        # ---------------
        # entretiens
        staticBox_entretiens = wx.StaticBoxSizer(self.staticBox_entretiens, wx.VERTICAL)
        grid_sizer_entretiens = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_entretiens.Add(self.ctrl_entretiens, 1, wx.EXPAND, 0)
        grid_sizer_boutons_entretiens = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_entretiens.Add(self.bouton_entretiens_ajouter, 0, 0, 0)
        grid_sizer_boutons_entretiens.Add(self.bouton_entretiens_modifier, 0, 0, 0)
        grid_sizer_boutons_entretiens.Add(self.bouton_entretiens_supprimer, 0, 0, 0)
##        grid_sizer_boutons_entretiens.Add((10, 10), 0, 0, 0)
##        grid_sizer_boutons_entretiens.Add(self.bouton_entretiens_imprimer, 0, 0, 0) 
        grid_sizer_entretiens.Add(grid_sizer_boutons_entretiens, 1, wx.EXPAND, 0)
        grid_sizer_entretiens.AddGrowableRow(0)
        grid_sizer_entretiens.AddGrowableCol(0)
        staticBox_entretiens.Add(grid_sizer_entretiens, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticBox_entretiens, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 5)
        
        # ---------------
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        

    def OnBoutonAjoutCandidature(self, event):
        self.ctrl_candidatures.Ajouter()

    def OnBoutonModifCandidature(self, event):
        self.ctrl_candidatures.Modifier()

    def OnBoutonSupprCandidature(self, event):
        self.ctrl_candidatures.Supprimer()
        
    def OnBoutonAjoutEntretien(self, event):
        self.ctrl_entretiens.Ajouter()

    def OnBoutonModifEntretien(self, event):
        self.ctrl_entretiens.Modifier()
        
    def OnBoutonSupprEntretien(self, event):
        self.ctrl_entretiens.Supprimer()
        