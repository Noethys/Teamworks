#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import GestionDB
import datetime
import FonctionsPerso
import wx.lib.masked as masked
import sqlite3
import SaisieCoords
import OL_candidatures
import sys
import OL_entretiens


try: import psyco; psyco.full()
except: pass


class Panel(wx.Panel):
    def __init__(self, parent, IDcandidat=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_candidat", style=wx.TAB_TRAVERSAL)
        self.IDcandidat = IDcandidat
        
        # Création d'une fiche
        if self.IDcandidat == None :
            self.IDcandidat = self.CreationIDfiche()
            self.nouvelleFiche = True
        else:
            self.nouvelleFiche = False
        
        # Création d'une liste des villes et codes postaux
        con = sqlite3.connect("Villes.db3")
        cur = con.cursor()
        cur.execute("SELECT ville, cp FROM villes")
        self.listeVillesTmp = cur.fetchall()
        con.close()
        
        # Création d'une liste de noms de villes
        self.listeNomsVilles = []
        self.listeVilles = []
        for nom, cp in self.listeVillesTmp:
            self.listeVilles.append((nom, "%05d" % cp))
            self.listeNomsVilles.append(nom)
        
        # Identite
        self.sizer_identite_staticbox = wx.StaticBox(self, -1, u"Identité")
        self.label_civilite = wx.StaticText(self, -1, u"Civilité :")
        self.ctrl_civilite = wx.Choice(self, -1, choices=[u"Mr", u"Melle", u"Mme"])
        self.label_nom = wx.StaticText(self, -1, u"Nom :")
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.label_prenom = wx.StaticText(self, -1, u"Prénom :")
        self.ctrl_prenom = wx.TextCtrl(self, -1, u"")
        self.label_date_naiss = wx.StaticText(self, -1, u"Date naiss. :")
        self.ctrl_radio_1 = wx.RadioButton(self, -1, u"", style=wx.RB_GROUP)
        self.ctrl_date_naiss = masked.TextCtrl(self, -1, "", style=wx.TE_CENTRE, mask = "##/##/####") 
        self.ctrl_age_1 = wx.TextCtrl(self, -1, "", style=wx.TE_CENTRE, size=(46,-1))
        self.ctrl_radio_2 = wx.RadioButton(self, -1, u"")
        self.label_age = wx.StaticText(self, -1, u"ou âge :")
        self.ctrl_age_2 = wx.TextCtrl(self, -1, "", style=wx.TE_CENTRE, size=(30,-1))
        self.label_ans = wx.StaticText(self, -1, u"ans")
        
        # Adresse
        self.sizer_adresse_staticbox = wx.StaticBox(self, -1, u"Adresse")
        self.label_adresse = wx.StaticText(self, -1, u"     Adresse :")
        self.ctrl_adresse = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        self.label_cp = wx.StaticText(self, -1, u"C.P. :")
        self.ctrl_cp = TextCtrlCp(self, value="", listeVilles=self.listeVilles, size=(55, -1), style=wx.TE_CENTRE, mask = "#####") 
        self.label_ville = wx.StaticText(self, -1, u"Ville :")
        self.ctrl_ville = TextCtrlVille(self, value="", ctrlCp=self.ctrl_cp, listeVilles=self.listeVilles, listeNomsVilles=self.listeNomsVilles)
        self.ctrl_cp.ctrlVille = self.ctrl_ville
        self.bouton_villes = wx.Button(self, -1, u"...")
        
        # Coords
        self.sizer_coords_staticbox = wx.StaticBox(self, -1, u"Coordonnées")
        self.ctrl_coords = ListCtrlCoords(self, -1)
        self.ctrl_coords.SetMinSize((20, 20))
        self.bouton_ajouter_coord = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_coord = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_coord = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))

        # Qualifications
        self.sizer_qualifications_staticbox = wx.StaticBox(self, -1, u"Qualifications")
        self.ctrl_qualifications = ListCtrl_Diplomes(self, -1)
        self.ctrl_qualifications.SetMinSize((20, 20))
        self.ctrl_qualifications.SetBackgroundColour((236, 233, 216))
        self.bouton_qualifications = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))

        # Candidatures
        self.sizer_candidatures_staticbox = wx.StaticBox(self, -1, u"Candidatures")
        self.ctrl_candidatures = OL_candidatures.ListView(self, id=-1, name="OL_candidatures", IDcandidat=self.IDcandidat, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_candidatures.SetMinSize((20, 20))
        self.ctrl_candidatures.MAJ(IDpersonne=self.IDcandidat)
        self.bouton_ajouter_cand = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_cand = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_cand = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        
        # Entretiens
        self.sizer_entretiens_staticbox = wx.StaticBox(self, -1, u"Entretiens")
        self.ctrl_entretiens = OL_entretiens.ListView(self, id=-1, name="OL_entretiens", IDcandidat=self.IDcandidat, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_entretiens.SetMinSize((20, 20))
        self.ctrl_entretiens.MAJ(IDcandidat=self.IDcandidat)
        self.bouton_ajouter_entretien = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_entretien = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_entretien = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        
        # Memo
        self.sizer_memo_staticbox = wx.StaticBox(self, -1, u"Mémo")
        self.ctrl_memo = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        self.ctrl_memo.SetMinSize((200, 30))
        
        # Boutons de commande
        self.bouton_convertir = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Convertir_candidat.png", wx.BITMAP_TYPE_ANY))
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_courrier = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Envoyer_courrier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
            
        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.AjouterCoord, self.bouton_ajouter_coord)
        self.Bind(wx.EVT_BUTTON, self.ModifierCoord, self.bouton_modifier_coord)
        self.Bind(wx.EVT_BUTTON, self.SupprimerCoord, self.bouton_supprimer_coord)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonQualifications, self.bouton_qualifications)
        self.Bind(wx.EVT_BUTTON, self.AjouterCand, self.bouton_ajouter_cand)
        self.Bind(wx.EVT_BUTTON, self.ModifierCand, self.bouton_modifier_cand)
        self.Bind(wx.EVT_BUTTON, self.SupprimerCand, self.bouton_supprimer_cand)
        self.Bind(wx.EVT_BUTTON, self.AjouterEntretien, self.bouton_ajouter_entretien)
        self.Bind(wx.EVT_BUTTON, self.ModifierEntretien, self.bouton_modifier_entretien)
        self.Bind(wx.EVT_BUTTON, self.SupprimerEntretien, self.bouton_supprimer_entretien)
        self.ctrl_nom.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusNom)
        self.ctrl_date_naiss.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusDateNaiss)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDateNaiss, self.ctrl_radio_1 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDateNaiss, self.ctrl_radio_2 )
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_courrier, self.bouton_courrier)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonConvertir, self.bouton_convertir)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
        # Appel de l'importation des données
        if self.IDcandidat != None and self.nouvelleFiche != True :
            self.Importation()
            self.MaJ_DateNaiss()
        self.OnRadioDateNaiss(None)
        
        if self.nouvelleFiche == True :
            self.ctrl_nom.SetFocus()
        else:
            self.bouton_ok.SetFocus()
        
    def __set_properties(self):
        self.ctrl_civilite.SetToolTipString(u"Sélectionnez la civilité du candidat")
        self.ctrl_civilite.SetSelection(0)
        self.ctrl_nom.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.ctrl_nom.SetToolTipString(u"Saisissez le nom de famille du candidat")
        self.ctrl_prenom.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.ctrl_prenom.SetToolTipString(u"Saisissez le prénom du candidat")
        self.ctrl_date_naiss.SetToolTipString(u"Saisissez la date de naissance du candidat")
        self.ctrl_age_1.Enable(False)
        self.ctrl_age_2.SetToolTipString(u"Saisissez l'âge du candidat si vous ne connaissez pas sa date de naissance")
        self.ctrl_adresse.SetToolTipString(u"Saisissez l'adresse du candidat")
        self.ctrl_cp.SetMinSize((60, -1))
        self.ctrl_cp.SetToolTipString(u"Saisissez le code postal")
        self.ctrl_ville.SetToolTipString(u"Saisissez la ville")
        self.bouton_villes.SetMinSize((20, 20))
        self.bouton_villes.SetToolTipString(u"Cliquez ici pour la gestion des villes")
        self.bouton_ajouter_coord.SetToolTipString(u"Cliquez ici pour ajouter une coordonnée")
        self.bouton_modifier_coord.SetToolTipString(u"Cliquez ici pour modifier la coordonnée selectionnée")
        self.bouton_supprimer_coord.SetToolTipString(u"Cliquez ici pour supprimer la coordonnée selectionnée")
        self.bouton_qualifications.SetToolTipString(u"Cliquez ici pour sélectionner des qualifications pour ce candidat")
        self.bouton_ajouter_cand.SetToolTipString(u"Cliquez ici pour créer une candidature pour ce candidat")
        self.bouton_modifier_cand.SetToolTipString(u"Cliquez ici pour modifier la candidature sélectionnée dans la liste")
        self.bouton_supprimer_cand.SetToolTipString(u"Cliquez ici pour supprimer la candidature sélectionnée dans la liste")
        self.bouton_ajouter_entretien.SetToolTipString(u"Cliquez ici pour créer un entretien")
        self.bouton_modifier_entretien.SetToolTipString(u"Cliquez ici pour modifier l'entretien selectionné dans la liste")
        self.bouton_supprimer_entretien.SetToolTipString(u"Cliquez ici pour supprimer l'entretien selectionné dans la liste")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_convertir.SetToolTipString(u"Cliquez ici pour convertir la fiche de ce candidat en fiche individuelle d'employé")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider la fiche")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.bouton_courrier.SetToolTipString(u"Cliquez ici pour créer un courrier ou un mail par publipostage")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=8, vgap=10, hgap=10)
        grid_sizer_bas = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        sizer_memo = wx.StaticBoxSizer(self.sizer_memo_staticbox, wx.VERTICAL)
        sizer_entretiens = wx.StaticBoxSizer(self.sizer_entretiens_staticbox, wx.VERTICAL)
        grid_sizer_entretiens = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        sizer_candidatures = wx.StaticBoxSizer(self.sizer_candidatures_staticbox, wx.VERTICAL)
        grid_sizer_candidatures = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_candidatures = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_haut_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        sizer_qualifications = wx.StaticBoxSizer(self.sizer_qualifications_staticbox, wx.VERTICAL)
        grid_sizer_qualifications = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_qualifications = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        sizer_coords = wx.StaticBoxSizer(self.sizer_coords_staticbox, wx.VERTICAL)
        grid_sizer_coords = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_coords = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_haut_gauche = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        sizer_adresse = wx.StaticBoxSizer(self.sizer_adresse_staticbox, wx.VERTICAL)
        grid_sizer_adresse = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_ville = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        sizer_identite = wx.StaticBoxSizer(self.sizer_identite_staticbox, wx.VERTICAL)
        grid_sizer_identite = wx.FlexGridSizer(rows=6, cols=2, vgap=5, hgap=5)
        grid_sizer_date_naiss = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_age = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_naiss = wx.FlexGridSizer(rows=1, cols=10, vgap=5, hgap=5)
        grid_sizer_identite.Add(self.label_civilite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.ctrl_civilite, 0, 0, 0)
        grid_sizer_identite.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_identite.Add(self.label_prenom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.ctrl_prenom, 0, wx.EXPAND, 0)
        grid_sizer_identite.Add((5, 5), 0, wx.EXPAND, 0)
        grid_sizer_identite.Add((5, 5), 0, wx.EXPAND, 0)
        grid_sizer_identite.Add(self.label_date_naiss, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_naiss.Add(self.ctrl_radio_1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_naiss.Add(self.ctrl_date_naiss, 0, 0, 0)
        grid_sizer_naiss.Add(self.ctrl_age_1, 0, 0, 0)
        grid_sizer_naiss.Add((10, 10), 0, 0, 0)
        grid_sizer_naiss.Add(self.ctrl_radio_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_naiss.Add(self.label_age, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_naiss.Add(self.ctrl_age_2, 0, 0, 0)
        grid_sizer_naiss.Add(self.label_ans, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_date_naiss.Add(grid_sizer_naiss, 1, wx.EXPAND, 0)

        grid_sizer_date_naiss.Add(grid_sizer_age, 1, wx.EXPAND, 0)
        grid_sizer_identite.Add(grid_sizer_date_naiss, 1, wx.EXPAND, 0)
        grid_sizer_identite.AddGrowableCol(1)
        sizer_identite.Add(grid_sizer_identite, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut_gauche.Add(sizer_identite, 1, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_adresse, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_adresse.Add(self.ctrl_adresse, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_cp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ville.Add(self.ctrl_cp, 0, 0, 0)
        grid_sizer_ville.Add(self.label_ville, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ville.Add(self.ctrl_ville, 0, wx.EXPAND, 0)
        grid_sizer_ville.Add(self.bouton_villes, 0, 0, 0)
        grid_sizer_ville.AddGrowableCol(2)
        grid_sizer_adresse.Add(grid_sizer_ville, 1, wx.EXPAND, 0)
        grid_sizer_adresse.AddGrowableCol(1)
        sizer_adresse.Add(grid_sizer_adresse, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut_gauche.Add(sizer_adresse, 1, wx.EXPAND, 0)
        grid_sizer_haut_gauche.AddGrowableCol(0)
        grid_sizer_haut.Add(grid_sizer_haut_gauche, 1, wx.EXPAND, 0)
        grid_sizer_coords.Add(self.ctrl_coords, 0, wx.EXPAND, 0)
        grid_sizer_boutons_coords.Add(self.bouton_ajouter_coord, 0, 0, 0)
        grid_sizer_boutons_coords.Add(self.bouton_modifier_coord, 0, 0, 0)
        grid_sizer_boutons_coords.Add(self.bouton_supprimer_coord, 0, 0, 0)
        grid_sizer_coords.Add(grid_sizer_boutons_coords, 1, wx.EXPAND, 0)
        grid_sizer_coords.AddGrowableRow(0)
        grid_sizer_coords.AddGrowableCol(0)
        sizer_coords.Add(grid_sizer_coords, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut_droit.Add(sizer_coords, 1, wx.EXPAND, 0)
        grid_sizer_qualifications.Add(self.ctrl_qualifications, 0, wx.EXPAND, 0)
        grid_sizer_boutons_qualifications.Add(self.bouton_qualifications, 0, 0, 0)
        grid_sizer_qualifications.Add(grid_sizer_boutons_qualifications, 1, wx.EXPAND, 0)
        grid_sizer_qualifications.AddGrowableRow(0)
        grid_sizer_qualifications.AddGrowableCol(0)
        sizer_qualifications.Add(grid_sizer_qualifications, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut_droit.Add(sizer_qualifications, 1, wx.EXPAND, 0)
        grid_sizer_haut_droit.AddGrowableRow(0)
        grid_sizer_haut_droit.AddGrowableRow(1)
        grid_sizer_haut_droit.AddGrowableCol(0)
        grid_sizer_haut.Add(grid_sizer_haut_droit, 1, wx.EXPAND, 0)
        grid_sizer_haut.AddGrowableCol(0)
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_candidatures.Add(self.ctrl_candidatures, 0, wx.EXPAND, 0)
        grid_sizer_boutons_candidatures.Add(self.bouton_ajouter_cand, 0, 0, 0)
        grid_sizer_boutons_candidatures.Add(self.bouton_modifier_cand, 0, 0, 0)
        grid_sizer_boutons_candidatures.Add(self.bouton_supprimer_cand, 0, 0, 0)
        grid_sizer_candidatures.Add(grid_sizer_boutons_candidatures, 1, wx.EXPAND, 0)
        grid_sizer_candidatures.AddGrowableRow(0)
        grid_sizer_candidatures.AddGrowableCol(0)
        sizer_candidatures.Add(grid_sizer_candidatures, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(sizer_candidatures, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_entretiens.Add(self.ctrl_entretiens, 0, wx.EXPAND, 0)
        grid_sizer_boutons_entretiens = wx.GridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_entretiens.Add(self.bouton_ajouter_entretien, 0, 0, 0)
        grid_sizer_boutons_entretiens.Add(self.bouton_modifier_entretien, 0, 0, 0)
        grid_sizer_boutons_entretiens.Add(self.bouton_supprimer_entretien, 0, 0, 0)
        grid_sizer_entretiens.Add(grid_sizer_boutons_entretiens, 0, wx.EXPAND, 0)
        grid_sizer_entretiens.AddGrowableRow(0)
        grid_sizer_entretiens.AddGrowableCol(0)
        sizer_entretiens.Add(grid_sizer_entretiens, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_bas.Add(sizer_entretiens, 1, wx.EXPAND, 0)
        sizer_memo.Add(self.ctrl_memo, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_bas.Add(sizer_memo, 1, wx.EXPAND, 0)
        grid_sizer_bas.AddGrowableRow(0)
        grid_sizer_bas.AddGrowableCol(0)
##        grid_sizer_bas.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_bas, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_courrier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_convertir, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(3)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
    
    def Onbouton_courrier(self, event):
        """ Imprime un document par publipostage """
        
        # Civilité
        civilite = self.ctrl_civilite.GetSelection()
        if civilite == -1 :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner une civilité", "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_civilite.SetFocus()
            return False

        # Nom et prénom
        nom = self.ctrl_nom.GetValue()
        prenom = self.ctrl_prenom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un nom", "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False
        if prenom == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un prénom", "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_prenom.SetFocus()
            return False
        
        # Confirmation de la sauvegarde
        dlg = wx.MessageDialog(self, u"Avant d'ouvrir l'assistant publipostage, il est nécessaire\nde sauvegarder les données de cette fiche. Confirmez-vous ?", "Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        if reponse == wx.ID_NO:
            dlg.Destroy()
            return
        else: dlg.Destroy()
        
        # Sauvegarde
        self.Sauvegarde()
        
        self.bouton_annuler.Enable(False)
        self.GetParent().EnableCloseButton(False)
        
        # Récupère les données pour le publipostage
        import Publipostage_donnees
        dictDonnees = Publipostage_donnees.GetDictDonnees(categorie="candidat", listeID=[self.IDcandidat,])
        # Ouvre le publiposteur
        import Publiposteur
        frm = Publiposteur.MyWizard(self, "", dictDonnees=dictDonnees)
        frm.Show()
        
    def OnContextMenu(self, event):
        pass
        
    def OnKillFocusNom(self, event):
        texte = self.ctrl_nom.GetValue()
        if len(texte) != 0 :
            self.ctrl_nom.SetValue(texte.upper())
        
    def Importation(self,):
        """ Importation des donnees de la base """
        DB = GestionDB.DB()
        req = """SELECT civilite, nom, prenom, date_naiss, age, adresse_resid, cp_resid, ville_resid, memo
        FROM candidats WHERE IDcandidat = %d""" % self.IDcandidat
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()[0]
        DB.Close()
        
        civilite, nom, prenom, date_naiss, age, adresse_resid, cp_resid, ville_resid, memo = listeDonnees
        
        # Placement des données dans les contrôles
        self.autoComplete = False
        
        self.ctrl_civilite.SetStringSelection(civilite)
        self.ctrl_nom.SetValue(nom)
        self.ctrl_prenom.SetValue(prenom)
        self.ctrl_adresse.SetValue(adresse_resid)
        if ville_resid != "" :
            self.ctrl_ville.SetValue(ville_resid)
        self.ctrl_memo.SetValue(memo)

        # Champs spéciaux
        try :
            if cp_resid != "" and cp_resid != None and cp_resid != "     " :
                if type(cp_resid) == unicode : cp_resid = int(cp_resid)
                self.ctrl_cp.SetValue("%05d" % cp_resid)
            if cp_naiss != "" and cp_naiss != None and cp_naiss != "     " :
                if type(cp_naiss) == unicode : cp_naiss = int(cp_naiss)
                self.ctrl_cp.SetValue("%05d" % cp_naiss)
        except : 
            pass

        # Date de naissance
        temp = date_naiss
        if temp == "  /  /    " or temp == '' or temp == None:
            temp = "  /  /    "
        else:
            jour = str(temp[8:10])
            mois = str(temp[5:7])
            annee = str(temp[:4])
            temp = jour + "/" + mois + "/" + annee
        self.ctrl_date_naiss.SetValue(temp)
        
        # Age
        if age != "" and age != None and age != 0 :
            self.ctrl_age_2.SetValue(str(age))
            self.ctrl_radio_2.SetValue(True)
                
        # Fin de l'importation
        self.autoComplete = True
    
    def OnRadioDateNaiss(self, event):
        if self.ctrl_radio_2.GetValue() == True :
            self.ctrl_date_naiss.Enable(False)
            self.ctrl_age_2.Enable(True)
            self.ctrl_age_2.SetFocus()
        else:
            self.ctrl_date_naiss.Enable(True)
            self.ctrl_age_2.Enable(False)
            self.ctrl_date_naiss.SetFocus()

    def OnKillFocusDateNaiss(self, event):
        self.MaJ_DateNaiss()
        
    def MaJ_DateNaiss(self):
        # Verifie la validite de la date
        if self.ctrl_date_naiss.GetValue() == "  /  /    ":
            self.ctrl_age_1.SetValue("")
            return
        validation = ValideDate(texte=self.ctrl_date_naiss.GetValue(), date_min="01/01/1910", date_max="01/01/2030")
        if validation == False:
            self.ctrl_date_naiss.SetFocus()
            return
            
        # Calcul de l'age de la personne
        valeurDate = self.ctrl_date_naiss.GetValue()
        jour = int(valeurDate[:2])
        mois = int(valeurDate[3:5])
        annee = int(valeurDate[6:10])
        bday = datetime.date(annee, mois, jour)
        datedujour = datetime.date.today()
        age = (datedujour.year - bday.year) - int((datedujour.month, datedujour.day) < (bday.month, bday.day))
        self.ctrl_age_1.SetValue(str(age) + " ans")
                
        
    def AjouterCoord(self, event):
        frameCoords = SaisieCoords.FrameCoords(self, -1, u"Coordonnées", size=(280, 290), IDcoord=0, IDpersonne=self.IDcandidat)
        frameCoords.Show()

    def ModifierCoord(self, event):
        """ Modification de coordonnées """
        index = self.ctrl_coords.GetFirstSelected()
        if index == -1:
            dlg = wx.MessageDialog(self, u"Vous devez d'abord sélectionner un item à modifier dans la liste des coordonnées", "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        varIDcoord = self.ctrl_coords.GetItemData(index)
        frameCoords = SaisieCoords.FrameCoords(self, -1, u"Coordonnées", size=(280, 290), IDcoord=varIDcoord, IDpersonne=self.IDcandidat)
        frameCoords.Show()

    def SupprimerCoord(self, event):
        """ Suppression d'une coordonnée """
        index = self.ctrl_coords.GetFirstSelected()

        # Vérifie qu'un item a bien été sélectionné
        if index == -1:
            dlg = wx.MessageDialog(self, u"Vous devez d'abord sélectionner un item à supprimer dans la liste des coordonnées", "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation
        texteCoord = self.ctrl_coords.GetItemText(index)
        txtMessage = unicode((u"Voulez-vous vraiment supprimer cette coordonnée ? \n\n> " + texteCoord))
        dlgConfirm = wx.MessageDialog(self, txtMessage, u"Confirmation de suppression", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        varIDcoord = self.ctrl_coords.GetItemData(index)

        # Suppression
        DB = GestionDB.DB()
        DB.ReqDEL("coords_candidats", "IDcoord", varIDcoord)

        # MàJ du listCtrl Coords de la fiche individuelle
        self.ctrl_coords.Remplissage()

    def OnBoutonQualifications(self, event):
        """ Boîte de dialogue pour choisir les diplômes """
        resultat = ""
        titre = u"Sélection des qualifications"

        # Récupération de la liste de tous les diplomes
        DB = GestionDB.DB()
        req = "SELECT IDtype_diplome, nom_diplome FROM types_diplomes ORDER BY nom_diplome"
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        DB.Close()

        # Création d'un dictionnaire diplomes et d'une liste pour la boîte de dialogue
        dictDiplomes = {}
        listeNoms = []
        preSelection = []
        TypesDiplomesPerso = []
        index = 0
        for diplome in donnees:
            ID = diplome[0]
            nom = diplome[1]
            dictDiplomes[index] = ID
            listeNoms.append(nom)
            # Recherche si est dans la liste de la personne
            if ID in self.ctrl_qualifications.listeDiplomes:
                preSelection.append(index)
                TypesDiplomesPerso.append(ID)
            index += 1
        message = u"Sélectionnez les qualifications que possède le candidat dans la liste proposée :"
        dlg = wx.MultiChoiceDialog(self, message, titre, listeNoms, wx.CHOICEDLG_STYLE)
        
        # Coche ceux qui doivent être déjà sélectionnés dans la liste
        dlg.SetSelections(preSelection)
        
        # Résultats
        if dlg.ShowModal() == wx.ID_OK:
            resultat = dlg.GetSelections()
        else:
            return
        dlg.Destroy()
        
        # On cherche les nouveaux diplomes saisis
        listeAEnregistrer = []
        for diplome in resultat:
            IDtype_diplome = dictDiplomes[diplome]
            # On regarde si l'ID est déjà dans la liste des diplomes de la personne
            if IDtype_diplome in TypesDiplomesPerso:
                # On passe et on l'efface de la liste
                TypesDiplomesPerso.remove(IDtype_diplome)
            else:
                listeAEnregistrer.append(IDtype_diplome)

        # On enregistre les nouveaux
        if len(listeAEnregistrer) != 0:
            DB = GestionDB.DB()
            for IDtype in listeAEnregistrer:
                DB.ExecuterReq("INSERT INTO diplomes_candidats (IDcandidat, IDtype_diplome) VALUES (%d, %d)" % (self.IDcandidat, IDtype))
            DB.Commit()
            DB.Close()

        # On voit si certains ont été enlevés de la liste
        if len(TypesDiplomesPerso) != 0:
            DB = GestionDB.DB()
            for IDtype in TypesDiplomesPerso:
                DB.ExecuterReq("DELETE FROM diplomes_candidats WHERE IDcandidat=%d AND IDtype_diplome=%d" % (self.IDcandidat, IDtype))
            DB.Commit()
            DB.Close()

        # MAJ du ListCtrl des Diplomes
        self.ctrl_qualifications.Remplissage()

    def AjouterCand(self, event):
        self.ctrl_candidatures.Ajouter()

    def ModifierCand(self, event):
        self.ctrl_candidatures.Modifier()

    def SupprimerCand(self, event):
        self.ctrl_candidatures.Supprimer()

    def AjouterEntretien(self, event):
        self.ctrl_entretiens.Ajouter()
        
    def ModifierEntretien(self, event):
        self.ctrl_entretiens.Modifier()

    def SupprimerEntretien(self, event):
        self.ctrl_entretiens.Supprimer()


    def Onbouton_aide(self, event):
##        FonctionsPerso.Aide(38)
        dlg = wx.MessageDialog(self, u"L'aide du module Recrutement est en cours de rédaction.\nElle sera disponible lors d'une mise à jour ultérieure.", "Aide indisponible", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
            
    def Onbouton_annuler(self, event):
        # Effacement des données si c'est une nouvelle fiche annulée
        if self.nouvelleFiche == True :
            DB = GestionDB.DB()
            DB.ReqDEL("candidats", "IDcandidat", self.IDcandidat)
            DB.ReqDEL("coords_candidats", "IDcandidat", self.IDcandidat)
            DB.ReqDEL("diplomes_candidats", "IDcandidat", self.IDcandidat)
            DB.ReqDEL("candidatures", "IDcandidat", self.IDcandidat)
            DB.ReqDEL("entretiens", "IDcandidat", self.IDcandidat)
            DB.Close()
            
        # Fermeture
        self.GetParent().Fermer()
        
    def Onbouton_ok(self, event):
        """ Validation des données saisies """
        
        # Civilité
        civilite = self.ctrl_civilite.GetSelection()
        if civilite == -1 :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner une civilité", "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_civilite.SetFocus()
            return False

        # Nom et prénom
        nom = self.ctrl_nom.GetValue()
        prenom = self.ctrl_prenom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un nom", "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False
        if prenom == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un prénom", "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_prenom.SetFocus()
            return False
        
        # Sauvegarde des données
        self.Sauvegarde()
                
        # Fermeture
        self.GetParent().Fermer()
    
    def Sauvegarde(self):
        # Sauvegarde des données
        civilite = self.ctrl_civilite.GetStringSelection()
        nom = self.ctrl_nom.GetValue()
        prenom = self.ctrl_prenom.GetValue()
        
        if self.ctrl_radio_1.GetValue() :
            temp = self.ctrl_date_naiss.GetValue() 
            if temp == "  /  /    ":
                date_naiss = ""
            else:
                jour = int(temp[:2])
                mois = int(temp[3:5])
                annee = int(temp[6:10])
                date_naiss = datetime.date(annee, mois, jour)
            age = 0
        else:
            date_naiss = ""
            try :
                age = int(age)
            except : age = 0
            age = self.ctrl_age_2.GetValue()
            
        adresse = self.ctrl_adresse.GetValue() 
        cp = self.ctrl_cp.GetValue() 
        if cp == "     " : cp = None
        ville = self.ctrl_ville.GetValue() 
        memo = self.ctrl_memo.GetValue()
        
        DB = GestionDB.DB()
        # Sauvegarde de la candidature
        listeDonnees = [    ("civilite",   civilite),  
                                    ("nom",   nom),  
                                    ("prenom",    prenom),
                                    ("date_naiss",    date_naiss),
                                    ("age",    age),
                                    ("adresse_resid",    adresse),
                                    ("cp_resid",    cp), 
                                    ("ville_resid",    ville),
                                    ("memo",    memo), 
                                    ]
        if self.IDcandidat == None :
            newID = DB.ReqInsert("candidats", listeDonnees)
            self.IDcandidat = newID
            nouvelleCandidat = True
        else:
            DB.ReqMAJ("candidats", listeDonnees, "IDcandidat", self.IDcandidat)
            nouvelleCandidat = False
        DB.Commit()
        
        # Fin de la sauvegarde
        DB.Close()
        

    def CreationIDfiche(self):
        # Sauvegarde la fiche
        DB = GestionDB.DB()
        # Sauvegarde de la candidature
        listeDonnees = [("nom",   ""),]
        if self.IDcandidat == None :
            newID = DB.ReqInsert("candidats", listeDonnees)
        DB.Commit()
        # Fin de la sauvegarde
        DB.Close()
        return newID

    def OnBoutonConvertir(self, event):
        """ Convertir en fiche individuelle """
        # Demande de confirmation
        txtMessage = u"Cette fonction vous permet de convertir une fiche CANDIDAT en fiche INDIVIDUELLE (fiche salarié). \nAttention, cette action est irreversible !\n\nConfirmez-vous la conversion ?"
        dlgConfirm = wx.MessageDialog(self, txtMessage, u"Conversion de fiche", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Sauvegarde
        self.Sauvegarde()
        
        # Conversion dans l'OL_candidats
        self.GetGrandParent().ConvertirFiche(IDcandidat=self.IDcandidat)
        
        # Fermer
        self.GetParent().Fermer()
        
        

def ValideDate(texte, date_min="01/01/1900", date_max="01/01/2090"):
    """ Verificateur de validite de date """
    listeErreurs = []
    # On vérifie si les cases ne sont pas vides
    if texte[0] == " " or texte[1] == " ":
        listeErreurs.append(u"le jour")
    if texte[3] == " " or texte[4] == " ":
        listeErreurs.append(u"le mois")
    if texte[6] == " " or texte[7] == " " or texte[8] == " " or texte[9] == " ":
        listeErreurs.append(u"l'année")
    
    if texte != "  /  /    ":

        # On vérifie que les chiffres existent
        if u"le jour" not in listeErreurs:
            jour = int(texte[:2])
            if jour == 0 or jour > 31:
                listeErreurs.append(u"le jour")

        if u"le mois" not in listeErreurs:
            mois = int(texte[3:5])
            if mois == 0 or mois > 12:
                listeErreurs.append(u"le mois")
                
        if u"l'année" not in listeErreurs:
            annee = int(texte[6:10])
            if annee < 1900 or annee > 2999:
                listeErreurs.append(u"l'année")
              
        # Affichage du message d'erreur
        
        if len(listeErreurs) != 0:
            # Message en cas de date incomplète
            if len(listeErreurs) == 1:
                message = u"Une incohérence a été détectée dans " + listeErreurs[0]
            if len(listeErreurs) == 2:
                message = u"Des incohérences ont été détectées dans " + listeErreurs[0] + " et " + listeErreurs[1]
            if len(listeErreurs) == 3:
                message = u"Des incohérences ont été détectées dans " + listeErreurs[0]  + ", " + listeErreurs[1]  + " et " + listeErreurs[2]
            message = message + u" de la date que vous venez de saisir. Veuillez la vérifier."

            wx.MessageBox(message, "Erreur de date")
            return False
        else:
            # On vérifie que les dates sont comprises dans l'intervalle donné en paramètre
            date_min = int(str(date_min[6:10]) + str(date_min[3:5]) + str(date_min[:2]))
            date_max = int(str(date_max[6:10]) + str(date_max[3:5]) + str(date_max[:2]))
            date_sel = int(str(texte[6:10]) + str(texte[3:5]) + str(texte[:2]))

            if date_sel < date_min:
                message = u"La date que vous venez de saisir semble trop ancienne. Veuillez la vérifier."
                wx.MessageBox(message, "Erreur de date")
                return False
            if date_sel > date_max:
                message = u"La date que vous venez de saisir semble trop élevée. Veuillez la vérifier."
                wx.MessageBox(message, "Erreur de date")
                return False
            
    else:
        return True



class ListCtrl_Diplomes(wx.ListCtrl):
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, id, size=(80, -1), style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_NO_HEADER|wx.LC_SINGLE_SEL|wx.SUNKEN_BORDER)
        self.parent = parent
        self.IDcandidat = self.GetParent().IDcandidat
        
        # Création de la Colonne
        self.InsertColumn(0, "Qualification")
        self.SetColumnWidth(0, 75)

        # Création des items
        self.Remplissage()
        
        # Binds
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def Remplissage(self):
        """ Remplissage du ListCtrl """
        # Importation des données
        self.Importation()

        # S'il existe des items, on les efface d'abord
        if self.GetItemCount() != 0:
            self.DeleteAllItems()
            
        # Création des items
        index = 0
        for key, valeurs in self.DictDiplomes.iteritems():
            IDdiplome = key
            IDtype_diplome = valeurs[0]
            self.listeDiplomes.append(IDtype_diplome)
            nom_diplome = valeurs[1]
            # Création de l'item
            self.InsertStringItem(index, nom_diplome)
            # Intégration du data ID
            self.SetItemData(index, key)
            index += 1

        # Tri dans l'ordre alphabétique
        self.SortItems(self.ColumnSorter)

    def ColumnSorter(self, key1, key2):
        item1 = self.DictDiplomes[key1][1]
        item2 = self.DictDiplomes[key2][1]
        if item1 < item2:    
               return -1
        else:                   
               return 1

    def Importation(self):
        """ Importe les données des diplomes """
        self.DictDiplomes = {}
        self.listeDiplomes = [] # Pour la boîte de dialogue de choix des diplomes

        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        req = "SELECT IDdiplome, diplomes_candidats.IDtype_diplome, nom_diplome FROM diplomes_candidats, types_diplomes WHERE diplomes_candidats.IDtype_diplome=types_diplomes.IDtype_diplome and IDcandidat=%d" % self.IDcandidat
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        DB.Close()
        
        for ligne in donnees:
            index = ligne[0]
            self.DictDiplomes[index] = (ligne[1], ligne[2])
        
    def OnItemSelected(self, event):
        """ Item cliqué """
        index = self.GetFirstSelected()
        key = self.GetItemData(index)
        event.Skip()

    def OnItemActivated(self, event):
        """ Item double-cliqué """
        index = self.GetFirstSelected()
        key = self.GetItemData(index)
        event.Skip()
        
    def OnSize(self, event):
        # La largeur de la colonne s'adapte à la largeur du listCtrl
        size = self.GetSize()
        self.SetColumnWidth(0, size.x-5)
        event.Skip()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel du ListCtrl Diplomes."""
        
        if self.GetFirstSelected() == -1:
            return False
        index = self.GetFirstSelected()
        key = self.GetItemData(index)
        
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, u"Modifier")
        bmp = wx.Bitmap("Images/16x16/Edit.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Modifier, id=10)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    
    def Menu_Modifier(self, event):
        index = self.GetFirstSelected()
        key = self.GetItemData(index)
        print "Modifier le num : ", key




class TextCtrlCp(masked.TextCtrl):
    def __init__(self, parent, id=-1, value=None, ctrlVille=None, listeVilles=None, **par):
        masked.TextCtrl.__init__(self, parent, id, value, **par)
        self.parent = parent
        self.ctrlVille = ctrlVille
        self.listeVilles = listeVilles
        self.autoComplete = True
        
        # Binds
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

    def OnKillFocus(self, event):
        """ Quand le contrôle Code perd le focus """
        if self.autoComplete == False :
            return
        textCode = self.GetValue()
        # On vérifie que la ville n'est pas déjà dans la case ville
        villeSelect = self.ctrlVille.GetValue()
        if villeSelect != '':
            for ville, cp in self.listeVilles:
                if ville == villeSelect and cp == textCode :
                    return
                
        # On recherche si plusieurs villes ont ce même code postal
        ReponsesVilles = []
        for ville, cp in self.listeVilles:
            if cp == textCode :
                ReponsesVilles.append(ville)
        nbreReponses = len(ReponsesVilles)

        # Code postal introuvable
        if nbreReponses == 0:
            if textCode.strip() != '':
                dlg = wx.MessageDialog(self, u"Ce code postal n'est pas répertorié dans la base de données. \nVérifiez que vous n'avez pas fait d'erreur de saisie.", "Information", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            return
        
        if nbreReponses == 1:
            resultat = ReponsesVilles[0]
            self.ctrlVille.SetValue(resultat)

        # Fenêtre de choix entre plusieurs codes postau
        if nbreReponses > 1:
            resultat = self.ChoixVilles(textCode, ReponsesVilles)
            if resultat != '':
                self.ctrlVille.SetValue(resultat)

        # Sélection du texte de la case ville pour l'autocomplete
        self.ctrlVille.SetSelection(0, len(resultat))
        
        event.Skip()

    def ChoixVilles(self, cp, listeReponses):
        """ Boîte de dialogue pour donner le choix entre plusieurs villes possédant un code postal identique """
        resultat = ""
        titre = u"Sélection d'une ville"
        nbreReponses = len(listeReponses)
        listeReponses.sort()
        message = str(nbreReponses) + u" villes possèdent le code postal " + str(cp) + u". Double-cliquez sur\nle nom d'une ville pour la sélectionner :"
        dlg = wx.SingleChoiceDialog(self, message, titre, listeReponses, wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            resultat = dlg.GetStringSelection()
        dlg.Destroy()
        return resultat


class TextCtrlVille(wx.TextCtrl):
    def __init__(self, parent, id=-1, value=None, ctrlCp=None, listeVilles=None, listeNomsVilles=None, **par):
        wx.TextCtrl.__init__(self, parent, id, value, **par)
        self.parent = parent
        self.ctrlCp = ctrlCp
        self.listeVilles = listeVilles
        self.listeNomsVilles = listeNomsVilles
        self.ignoreEvtText = False
        self.autoComplete = True
        
        # Binds
        self.Bind(wx.EVT_TEXT, self.OnText)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)


    def OnKillFocus(self, event):
        """ Quand le contrôle ville perd le focus """
        if self.autoComplete == False :
            return
        villeSelect = self.GetValue()
        if villeSelect == '':
            return

        # On recherche le nombre de villes ayant un nom identique
        nbreCodes = self.listeNomsVilles.count(villeSelect)

        if nbreCodes > 1:
            listeCodes = []
            for ville, cp in self.listeVilles :
                if villeSelect == ville:
                    listeCodes.append(cp)
                    
            # Chargement de la fenêtre de choix des codes
            resultat = self.ChoixCodes(villeSelect, listeCodes)
            if resultat != '':
                self.ctrlCp.SetValue(resultat)

        # Si la ville saisie n'existe pas
        if nbreCodes == 0:
            dlg = wx.MessageDialog(self, u"Cette ville n'est pas répertoriée dans la base de données. \nVérifiez que vous n'avez pas fait d'erreur de saisie.", "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        
        event.Skip()

    def OnChar(self, event):
        if event.GetKeyCode() == 8:
            self.ignoreEvtText = True
        event.Skip()

    def OnText(self, event):
        """ A chaque frappe de texte -> analyse """
        if self.autoComplete == False :
            return
        
        if self.ignoreEvtText:
            self.ignoreEvtText = False
            return
        currentText = event.GetString().upper()
        found = False
        for ville, cp in self.listeVilles :
            if ville.startswith(currentText):
                self.ignoreEvtText = True
                self.SetValue(ville)
                self.SetInsertionPoint(len(currentText))
                self.SetSelection(len(currentText), len(ville))
                self.ctrlCp.SetValue(cp)
                found = True
                break
        
        if not found:
            self.ctrlCp.SetValue('')
            event.Skip()

    def ChoixCodes(self, ville, listeReponses):
        """ Boîte de dialogue pour donner le choix entre plusieurs villes possédant le même nom """
        resultat = ""
        titre = u"Sélection d'une ville"
        nbreReponses = len(listeReponses)
        listeReponses.sort()
        message = str(nbreReponses) + u" villes portent le nom " + str(ville) + u". Double-cliquez sur\nle code postal d'une ville pour la sélectionner :"
        dlg = wx.SingleChoiceDialog(self, message, titre, listeReponses, wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            resultat = dlg.GetStringSelection()
        dlg.Destroy()
        return resultat




class ListCtrlCoords(wx.ListCtrl):
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, id, size=(140, -1), style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_SINGLE_SEL|wx.SUNKEN_BORDER)
        self.parent = parent
        self.popupIndex = -1

        self.Bind(wx.EVT_SIZE, self.OnSize)
        if "linux" not in sys.platform :
            # Désactive la fenetre popup sous Linux
            self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
       
        # ImageList
        self.il = wx.ImageList(16,16)
        self.imgMaison = self.il.Add(wx.Bitmap("Images/16x16/Maison.png", wx.BITMAP_TYPE_PNG))
        self.imgMobile = self.il.Add(wx.Bitmap("Images/16x16/Mobile.png", wx.BITMAP_TYPE_PNG))
        self.imgFax = self.il.Add(wx.Bitmap("Images/16x16/Fax.png", wx.BITMAP_TYPE_PNG))
        self.imgMail = self.il.Add(wx.Bitmap("Images/16x16/Mail.png", wx.BITMAP_TYPE_PNG))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
        
        self.InsertColumn(0, "")
        self.SetColumnWidth(0, 135)

        # Création des items
        self.Remplissage()

        # Binds
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def Remplissage(self):
        """ Remplissage du ListCtrl """
        # Importation des données
        self.Importation()

        # S'il existe des items, on les efface d'abord
        if self.GetItemCount() != 0:
            self.DeleteAllItems()
            
        # Création des items
        index = 0
        for key, valeurs in self.DictCoords.iteritems():
            categorie = valeurs[2]
            texte = valeurs[3]
            # Création de l'item
            self.InsertStringItem(index, texte)
            # Intégration de l'image
            if categorie == "Fixe":
                self.SetItemImage(index, self.imgMaison)
            if categorie == "Mobile":
                self.SetItemImage(index, self.imgMobile)
            if categorie == "Fax":
                self.SetItemImage(index, self.imgFax)
            if categorie == "Email":
                self.SetItemImage(index, self.imgMail)
            # Intégration du data ID
            self.SetItemData(index, key)
            index += 1
            
    def Importation(self):
        """ Importation des données depuis la base de données """
       
        # Initialisation de la connexion avec la Base de données
        IDcandidat = self.parent.IDcandidat
        if IDcandidat == None : IDcandidat = 0
        DB = GestionDB.DB()
        req = "SELECT * FROM coords_candidats WHERE IDcandidat = %d" % IDcandidat
        DB.ExecuterReq(req)
        listeCoords = DB.ResultatReq()
        DB.Close()

        self.DictCoords = self.listeEnDict(listeCoords)

    def listeEnDict(self, liste):
        dictio = {}
        for ligne in liste:
            index = ligne[0]
            dictio[index] = ligne
        return dictio
        
    def OnItemSelected(self, event):
        """ Item cliqué """
        # Désactivation de la capture de la souris pour le popup
        if self.HasCapture():
            self.ReleaseMouse()
        event.Skip()

    def OnItemActivated(self, event):
        """ Item double-cliqué """
        self.DestroyPopup()
        self.parent.ModifierCoord(None)
        event.Skip()
        
    def OnSize(self, event):
        # La largeur de la colonne s'adapte à la largeur du listCtrl
        size = self.GetSize()
        self.SetColumnWidth(0, size.x-5)
        event.Skip()

    def OnMouseMotion(self, event):
        index = self.HitTest(event.GetPosition())[0]
        if index == -1:
            if self.popupIndex != -1 :
                self.DestroyPopup()
            return
        
        item = self.GetItem(index, 0)
       
        pos = self.ClientToScreen(event.GetPosition()) # Position du curseur sur l'écran
        decalage = (-130, -70)

        tailleCtrl = self.GetSize()

        # Si le Popup est au bord du ListCtrl, on le ferme
        posInListCtrl = event.GetPosition() # Position du curseur dans le ListCtrl
        if self.popupIndex != -1:
            if posInListCtrl[0] < 4 or posInListCtrl[1] < 4 :
                self.DestroyPopup()
                return

        # Si on était déjà sur l'item , on ne fait que bouger le popup 
        if self.popupIndex == index :
            self.Popup.Position(pos, decalage)

        if self.popupIndex != index and self.popupIndex != -1:
            self.DestroyPopup()

        # Sinon, création d'un popup
        if self.popupIndex != index and posInListCtrl[0] > 3 and posInListCtrl[1] > 3:
            key = self.GetItemData(index)
            self.popupIndex = index
            self.Popup = TestPopup(self, key=key)
            self.Popup.Position(pos, decalage)
            self.Popup.Show(True)
            self.CaptureMouse()

            

    def DestroyPopup(self):
        """ Destruction de la fenêtre Popup """
        if self.HasCapture():
            self.ReleaseMouse()

        try:
            self.Popup
            self.Popup.Destroy()
            self.popupIndex = -1
        except:
            pass
            
            

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel du ListCtrl."""

        self.DestroyPopup()
        
        if self.GetFirstSelected() == -1:
            return False
        index = self.GetFirstSelected()
        key = self.GetItemData(index)
        
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, u"Ajouter")
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, u"Modifier")
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Modifier, id=20)

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, u"Supprimer")
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)

        # Si c'est un item Email, on ajoute "Envoyer Email"
        if self.DictCoords[key][2] == "Email" :
            menuPop.AppendSeparator()
            item = wx.MenuItem(menuPop, 40, u"Envoyer un E-mail")
            bmp = wx.Bitmap("Images/16x16/Mail.png", wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Menu_Envoyer_Email, id=40)

        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Menu_Ajouter(self, event):
        self.parent.AjouterCoord(None)
        
    def Menu_Modifier(self, event):
        self.parent.ModifierCoord(None)

    def Menu_Supprimer(self, event):
        self.parent.SupprimerCoord(None)

    def Menu_Envoyer_Email(self, event):
        """ Envoyer un mail """
        print "Envoi d'un mail perso."
        index = self.GetFirstSelected()
        key = self.GetItemData(index)
        FonctionsPerso.EnvoyerMail(adresses = (self.DictCoords[key][3],))



class TestPopup(wx.PopupWindow):
    """Adds a bit of text and mouse movement to the wx.PopupWindow"""
    def __init__(self, parent, style=wx.SIMPLE_BORDER, key=0):
        wx.PopupWindow.__init__(self, parent, style)

        # Récupération des données
        self.parent = parent
        valeurs = self.parent.DictCoords[key]
        categorie = valeurs[2]
        texte = valeurs[3]
        intitule = valeurs[4]
        
        # Intégration de l'image
        if categorie == "Fixe":
            img = wx.Bitmap("Images/32x32/Maison.png", wx.BITMAP_TYPE_PNG)
        if categorie == "Mobile":
            img = wx.Bitmap("Images/32x32/Mobile.png", wx.BITMAP_TYPE_PNG)
        if categorie == "Fax":
            img = wx.Bitmap("Images/32x32/Fax.png", wx.BITMAP_TYPE_PNG)
        if categorie == "Email":
            img = wx.Bitmap("Images/32x32/Mail.png", wx.BITMAP_TYPE_PNG)

        # Création des widgets
        self.panel_base = wx.Panel(self, -1)
        self.bitmap_1 = wx.StaticBitmap(self.panel_base, -1, img) #wx.Bitmap("Images/32x32/Mail.png", wx.BITMAP_TYPE_PNG)
        self.label_coords = wx.StaticText(self.panel_base, -1, texte)
        self.label_Intitu = wx.StaticText(self.panel_base, -1, intitule)

        self.label_coords.SetForegroundColour(wx.Colour(255, 0, 0))
        self.label_coords.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

        # Mise en page
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(rows=1, cols=2, vgap=0, hgap=0)
        grid_sizer_2 = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_1.Add(self.bitmap_1, 0, wx.ALL, 5)
        grid_sizer_2.Add(self.label_coords, 0, wx.TOP, 5)
        grid_sizer_2.Add(self.label_Intitu, 0, 0, 0)
        grid_sizer_2.AddGrowableCol(0)
        grid_sizer_1.Add(grid_sizer_2, 1, wx.RIGHT, 5)
        self.panel_base.SetSizer(grid_sizer_1)
        grid_sizer_1.AddGrowableRow(0)
        grid_sizer_1.AddGrowableCol(1)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        wx.CallAfter(self.Refresh)



class MyFrame(wx.Frame):
    def __init__(self, parent, IDcandidat=None):
        wx.Frame.__init__(self, parent, -1, title="", style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.panel = Panel(self, IDcandidat=IDcandidat)
                
        # Propriétés
        if IDcandidat == None :
            self.SetTitle(u"Saisie d'un candidat")
        else:
            self.SetTitle(u"Modification d'un candidat")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        
        # Layout
        self.SetMinSize((840, 670))
        self.SetSize((840, 670))
        self.CentreOnScreen()
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    
    def OnClose(self, event):
        self.panel.Onbouton_annuler(None)
    
    def Fermer(self):
        # MAJ
        parent = self.GetParent()
        if parent.GetName() == "OL_candidats" :
            parent.MAJ()
        
        try :
            if parent.GetGrandParent().GetParent().GetName() == "Recrutement" :
                parent.GetGrandParent().GetParent().gadget_entretiens.MAJ()
                parent.GetGrandParent().GetParent().gadget_informations.MAJ()
        except :
            pass

        self.MakeModal(False)
##        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

        
if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, IDcandidat=3)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()