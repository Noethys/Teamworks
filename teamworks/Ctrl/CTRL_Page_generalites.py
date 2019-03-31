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
import six
import wx.lib.masked as masked
import sqlite3
import datetime
from Dlg import DLG_Saisie_coords
import GestionDB
from Dlg import DLG_Config_situations
from Dlg import DLG_Config_pays
import FonctionsPerso
import sys
from Utils import UTILS_Adaptations


class Panel_general(wx.Panel):
    def __init__(self, parent, id, IDpersonne=0):
        wx.Panel.__init__(self, parent, id, name="panel_generalites", style=wx.TAB_TRAVERSAL)

        self.parent = parent
        self.IDpersonne = IDpersonne
        self.remplissageEnCours = True
        
        # Pays de naissance et nationalité
        self.IDpays_naiss = 0
        self.IDpays_nation = 0
        IDfrance = self.Recherche_Pays(nomPays="France")[0]
        if IDfrance != False :
            self.IDpays_naiss = IDfrance
            self.IDpays_nation = IDfrance

        # Sizers avec titre
        self.sizer_situation_sociale_staticbox = wx.StaticBox(self, -1, _(u"Situation sociale"))
        self.sizer_coords_staticbox = wx.StaticBox(self, -1, _(u"Coordonnées"))
        self.sizer_adresse_staticbox = wx.StaticBox(self, -1, "Adresse")
        self.sizer_memo_staticbox = wx.StaticBox(self, -1, _(u"Mémo"))
        self.sizer_identite_staticbox = wx.StaticBox(self, -1, _(u"Identité"))

        # Controles
        self.label_civilite = wx.StaticText(self, -1, _(u"Civilité :"))
        self.combo_box_civilite = wx.Choice(self, -1, choices=["Mr", "Melle", "Mme"])
        self.label_nomjf = wx.StaticText(self, -1, "Nom de jeune fille :")
        self.text_ctrl_nomjf = wx.TextCtrl(self, -1, "")
        self.label_nom = wx.StaticText(self, -1, "Nom :")
        self.text_nom = wx.TextCtrl(self, -1, "")
        self.label_prenom = wx.StaticText(self, -1, _(u"Prénom :"))
        self.text_prenom = wx.TextCtrl(self, -1, "")
        self.label_date_naiss = wx.StaticText(self, -1, _(u"Né(e) le :"))
        self.text_date_naiss = masked.TextCtrl(self, -1, "", style=wx.TE_CENTRE, mask = "##/##/####") 
        self.text_age = wx.TextCtrl(self, -1, "", style=wx.TE_CENTRE, size=(46,-1))
        self.label_pays = wx.StaticText(self, -1, _(u"Pays de naissance :"))
        self.bouton_pays = wx.Button(self, -1, "...", size=(20, 20))
        self.image_pays = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/Drapeaux/france.png"), wx.BITMAP_TYPE_PNG), size=(22, 10))
        
        self.label_cp_naiss = wx.StaticText(self, -1, _(u"à | C.P. :"))
        self.text_cp_naiss = masked.TextCtrl(self, 100, "", style=wx.TE_CENTRE, mask = "#####") 
        self.label_ville_naiss = wx.StaticText(self, -1, _(u"Ville :"))
        self.text_ville_naiss = wx.TextCtrl(self, 200)
        self.bouton_options_ville_naiss = wx.Button(self, -1, "...", size=(20, 20))
        self.label_numsecu = wx.StaticText(self, -1, _(u"Num Sécu :"))
        self.text_numsecu = masked.TextCtrl(self, -1, "", style=wx.TE_CENTRE, mask = "# ## ## ## ### ### ##") 
        self.image_numsecu = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG), size=(16, 16))
        
        self.label_nation = wx.StaticText(self, -1, _(u"Nationalité :"))
        self.bouton_nation = wx.Button(self, -1, "...", size=(20, 20))
        self.image_nation = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/Drapeaux/france.png"), wx.BITMAP_TYPE_PNG), size=(22, 10))

        self.bouton_situations = wx.Button(self, -1, "...", size=(20, 20))
        self.combo_box_situation = wx.Choice(self, -1, choices=[])
        # Remplissage du combo_box_situation
        self.ImportListeSituations()

        self.label_adresse = wx.StaticText(self, -1, "Adresse :")
        self.text_adresse = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        self.label_cp = wx.StaticText(self, -1, "C.P. :")
        self.text_cp = masked.TextCtrl(self, 300, "", style=wx.TE_CENTRE, mask = "#####") 
        self.label_ville = wx.StaticText(self, -1, "Ville :")
        self.text_ville = wx.TextCtrl(self, 400)
        self.bouton_options_ville = wx.Button(self, -1, "...", size=(20, 20))
        self.list_ctrl_coords = ListCtrlCoords(self, -1)
        self.list_ctrl_coords.SetMinSize((20, 20))

        self.button_coords_ajout = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        self.button_coords_modif = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
        self.button_coords_suppr = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
        self.text_memo = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        
        
        
        ##############################################################
        # Pour désactiver l'autocomplete du controle VILLE qui ne fonctionne pas sous Linux
        if "linux" in sys.platform :
            self.text_ville_naiss.Enable(False)
            self.text_ville.Enable(False)       
        
        ##############################################################
        
        self.__set_properties()
        self.__do_layout()

        # Evenements
        self.Bind(wx.EVT_BUTTON, self.OnOptionsVille, self.bouton_options_ville)
        self.Bind(wx.EVT_BUTTON, self.OnOptionsVilleNaiss, self.bouton_options_ville_naiss)
        self.Bind(wx.EVT_BUTTON, self.OnAjoutTel, self.button_coords_ajout)
        self.Bind(wx.EVT_BUTTON, self.OnModifTel, self.button_coords_modif)
        self.Bind(wx.EVT_BUTTON, self.OnSupprTel, self.button_coords_suppr)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSituations, self.bouton_situations)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonPays, self.bouton_pays)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonNation, self.bouton_nation) 
        
        self.image_numsecu.Bind(wx.EVT_LEFT_DOWN, self.OnImageNumSecu) 

        # Evenements perso
        self.Bind(wx.EVT_CHOICE, self.OnTextCivilite, self.combo_box_civilite)
        self.Bind(wx.EVT_TEXT, self.OnTextNomJF, self.text_ctrl_nomjf)
        self.Bind(wx.EVT_TEXT, self.OnTextNom, self.text_nom)
        self.Bind(wx.EVT_TEXT, self.OnTextPrenom, self.text_prenom)
        self.Bind(wx.EVT_TEXT, self.OnTextDateNaiss, self.text_date_naiss)
        self.Bind(wx.EVT_TEXT, self.OnTextNumSecu, self.text_numsecu)
        self.Bind(wx.EVT_TEXT, self.OnTextAdresse, self.text_adresse)

        
        self.Bind(wx.EVT_ACTIVATE, self.OnActivate)
        
        self.combo_box_civilite.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusCivilite)
        self.text_ctrl_nomjf.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusNomJFille)
        self.text_nom.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusNom)
        self.text_prenom.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusPrenom)
        self.text_date_naiss.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusDateNaiss)
        self.text_numsecu.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusNumSecu)
        self.text_adresse.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusAdresse)
        self.combo_box_situation.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusSituation)

        # ----------------------------------------------------------------------
        # Initialisation de la fonction autocomplete des controles cp et ville :
        self.text_ville_naiss.ignoreEvtText = False # Initialisation de variable
        self.text_ville.ignoreEvtText = False # Initialisation de variable
        self.autoComplete = True

        # Appel de la base de données des villes et codes postaux
        con = sqlite3.connect(Chemins.GetStaticPath("Databases/Villes.db3"))
        cur = con.cursor()
        cur.execute("SELECT ville, cp FROM villes")
        self.listeVillesTmp = cur.fetchall()
        cur.execute("SELECT num_dep, num_region, departement FROM departements")
        listeDepartements = cur.fetchall()
        cur.execute("SELECT num_region, region FROM regions")
        listeRegions = cur.fetchall()
        con.close()
        
        self.listeNomsVilles = []
        self.listeVilles = []
        for nom, cp in self.listeVillesTmp:
            self.listeVilles.append((nom, "%05d" % cp))
            self.listeNomsVilles.append(nom)
            
        self.dictRegions = {}
        for num_region, region in listeRegions :
            self.dictRegions[num_region] = region
        
        self.dictDepartements = {}
        for num_dep, num_region, departement in listeDepartements :
            self.dictDepartements[num_dep] = (departement, num_region)
        
        # Binds spéciaux pour l'autocomplete
        self.text_ville_naiss.Bind(wx.EVT_TEXT, self.VilleText1)
        self.text_ville_naiss.Bind(wx.EVT_CHAR, self.VilleChar1)
        self.text_ville_naiss.Bind(wx.EVT_KILL_FOCUS, self.Ville_KillFocus1)
        self.text_cp_naiss.Bind(wx.EVT_KILL_FOCUS, self.Code_KillFocus1)

        self.text_ville.Bind(wx.EVT_TEXT, self.VilleText2)
        self.text_ville.Bind(wx.EVT_CHAR, self.VilleChar2)
        self.text_ville.Bind(wx.EVT_KILL_FOCUS, self.Ville_KillFocus2)
        self.text_cp.Bind(wx.EVT_KILL_FOCUS, self.Code_KillFocus2)

        # ---------------------------------------------------------------------

        # Appel de l'importation des données
        if self.IDpersonne != 0:
            self.Importation()
        
        # MAJ de l'image de l'état du num de sécu
        self.SetEtatNumSecu()

        # MAJ du header de la fiche
        self.MAJ_Photo()
        self.MaJ_Adresse_Fiche()
        self.MaJ_DateNaiss_Fiche()
        
        
        self.remplissageEnCours = False
        
        
    def __set_properties(self):
        self.SetSize((962, 660))
        self.combo_box_civilite.SetToolTip(wx.ToolTip(_(u"Choisissez la civilité")))
        self.label_nomjf.Enable(False)
        self.text_ctrl_nomjf.SetToolTip(wx.ToolTip("Saisissez un nom de jeune fille"))
        self.text_ctrl_nomjf.Enable(False)
        self.text_nom.SetToolTip(wx.ToolTip("Saisissez le nom de famille"))
        self.text_prenom.SetToolTip(wx.ToolTip(_(u"Saisissez le prénom")))
        self.text_date_naiss.SetMinSize((95, -1))
        self.text_date_naiss.SetToolTip(wx.ToolTip("Saissez la date de naissance"))       
        self.text_numsecu.SetMinSize((170, -1))
        self.text_adresse.SetToolTip(wx.ToolTip("Saisissez l'adresse"))
##        self.label_age.Enable(False)
        self.text_age.Enable(False)
        self.text_cp_naiss.SetMinSize((50, -1))
        self.text_cp_naiss.SetToolTip(wx.ToolTip("Saisissez le code postal"))
        self.text_cp.SetMinSize((50, -1))
        self.text_cp.SetToolTip(wx.ToolTip("Saisissez le code postal"))
        self.text_ville_naiss.SetToolTip(wx.ToolTip(_(u"Choisissez une ville dans la liste proposée")))
        self.text_ville.SetToolTip(wx.ToolTip(_(u"Choisissez une ville dans la liste proposée")))
        self.bouton_options_ville_naiss.SetToolTip(wx.ToolTip("Cliquez ici pour configurer la liste des villes"))
        self.bouton_options_ville.SetToolTip(wx.ToolTip("Cliquez ici pour configurer la liste des villes"))
        self.button_coords_ajout.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un numéro de téléphone")))
        self.button_coords_ajout.SetSize(self.button_coords_ajout.GetBestSize())
        self.button_coords_modif.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier un numéro de téléphone")))
        self.button_coords_modif.SetSize(self.button_coords_modif.GetBestSize())
        self.button_coords_suppr.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le numéro de téléphone sélectionné")))
        self.button_coords_suppr.SetSize(self.button_coords_suppr.GetBestSize())
        self.bouton_situations.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer, modifier ou supprimer une situation sociale")))
        self.bouton_pays.SetSize(self.bouton_pays.GetBestSize())
        self.bouton_pays.SetToolTip(wx.ToolTip(_(u"Cliquez ici sélectionner un autre pays de naissance")))
        self.bouton_nation.SetSize(self.bouton_nation.GetBestSize())
        self.bouton_nation.SetToolTip(wx.ToolTip(_(u"Cliquez ici sélectionner une autre nationalité")))
        self.image_pays.SetToolTip(wx.ToolTip(_(u"Pays de naissance : France")))
        self.image_nation.SetToolTip(wx.ToolTip(_(u"Nationalité : Française")))
        self.image_numsecu.SetToolTip(wx.ToolTip(_(u"Etat du numéro de sécurité sociale\n\nCliquez sur cette image pour obtenir des informations \nsur la constitution d'un numéro de sécurité sociale")))
        
        texteNumSecu = u"""
        Numéro de sécurité sociale : A BB CC DD EEE FFF GG
        
        A : Sexe (1=homme | 2=femme)
        BB : Année de naissance
        CC : Mois de naissance
        DD : Département de naissance (99 si né à l'étranger)
        EEE : Code INSEE de la commune de naissance ou du pays si né à l'étranger
        FFF : Numéro d'ordre INSEE
        GG : Clé
        """
        self.text_numsecu.SetToolTip(wx.ToolTip(texteNumSecu))
        
        # Changement de couleur pour les champs text et combo
##        self.CouleurSiVide(self.combo_box_civilite, "combo")
##        self.CouleurSiVide(self.text_nom, "texte")
##        self.CouleurSiVide(self.text_prenom, "texte")
##        self.CouleurSiVide(self.text_adresse, "texte")
##        self.CouleurSiVide(self.text_ville_naiss, "texte")
##        self.CouleurSiVide(self.text_ville, "texte")

        # Changement de couleur pour les Champs masked
##        self.text_date_naiss.SetCtrlParameters(emptyBackgroundColour = "PINK")
##        self.text_numsecu.SetCtrlParameters(emptyBackgroundColour = "PINK")
##        self.text_cp_naiss.SetCtrlParameters(emptyBackgroundColour = "PINK")
##        self.text_cp.SetCtrlParameters(emptyBackgroundColour = "PINK")

        # Setfocus sur le 1er champ
        self.combo_box_civilite.SetFocus()


    def __do_layout(self):
        grid_sizer_1 = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        sizer_memo = wx.StaticBoxSizer(self.sizer_memo_staticbox, wx.VERTICAL)
        grid_sizer_memo = wx.FlexGridSizer(rows=1, cols=1, vgap=0, hgap=0)
        grid_sizer_2 = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        sizer_coords = wx.StaticBoxSizer(self.sizer_coords_staticbox, wx.VERTICAL)
        grid_sizer_coords = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        sizer_boutons_tel = wx.BoxSizer(wx.VERTICAL)
        sizer_situation_sociale = wx.StaticBoxSizer(self.sizer_situation_sociale_staticbox, wx.VERTICAL)
        sizer_adresse = wx.StaticBoxSizer(self.sizer_adresse_staticbox, wx.VERTICAL)
        grid_sizer_adresse = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_ville = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=0)
        
        # Sizer Identité
        sizer_identite = wx.StaticBoxSizer(self.sizer_identite_staticbox, wx.VERTICAL)
        grid_sizer_identite = wx.FlexGridSizer(rows=6, cols=2, vgap=5, hgap=5)
        sizer_naiss1 = wx.FlexGridSizer(rows=1, cols=6, vgap=0, hgap=0)
        sizer_naiss2 = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=0)
        sizer_civilite = wx.FlexGridSizer(rows=1, cols=4, vgap=0, hgap=0)
        
        grid_sizer_identite.Add(self.label_civilite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_civilite.Add(self.combo_box_civilite, 0, 0, 0)
        sizer_civilite.Add((15, 15), 0, 0, 0)
        sizer_civilite.Add(self.label_nomjf, 0, wx.RIGHT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_civilite.Add(self.text_ctrl_nomjf, 0, wx.EXPAND, 0)
        sizer_civilite.AddGrowableCol(3)
        grid_sizer_identite.Add(sizer_civilite, 1, wx.EXPAND, 0)
        grid_sizer_identite.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.text_nom, 0, wx.EXPAND, 0)
        grid_sizer_identite.Add(self.label_prenom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(self.text_prenom, 0, wx.EXPAND, 0)
        grid_sizer_identite.Add(self.label_date_naiss, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_naiss1.Add(self.text_date_naiss, 0, 0, 0)
        sizer_naiss1.Add(self.text_age, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_naiss1.Add((5, 5), 0, wx.EXPAND, 0)
        sizer_naiss1.Add(self.label_pays, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_naiss1.Add(self.image_pays, 0, wx.EXPAND, 0)
        sizer_naiss1.Add(self.bouton_pays, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_naiss1.AddGrowableCol(2)
        
        sizer_naiss2.Add(self.text_cp_naiss, 0, 0, 0)
        sizer_naiss2.Add(self.label_ville_naiss, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_naiss2.Add(self.text_ville_naiss, 0,  wx.EXPAND, 0)
        sizer_naiss2.Add(self.bouton_options_ville_naiss, 0, wx.LEFT, 5)
        sizer_naiss2.AddGrowableCol(2)
        grid_sizer_identite.Add(sizer_naiss1, 1, wx.EXPAND, 0)
        grid_sizer_identite.Add(self.label_cp_naiss, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_identite.Add(sizer_naiss2, 1, wx.EXPAND, 0)
        
        grid_sizer_identite.Add(self.label_numsecu, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        sizer_numsecu = wx.FlexGridSizer(rows=1, cols=6, vgap=0, hgap=0)
        sizer_numsecu.Add(self.text_numsecu, 0, 0, 0)
        sizer_numsecu.Add(self.image_numsecu, 0, wx.EXPAND, 0)
        sizer_numsecu.Add((5, 5), 0, wx.EXPAND, 0)
        sizer_numsecu.Add(self.label_nation, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_numsecu.Add(self.image_nation, 0, wx.EXPAND, 0)
        sizer_numsecu.Add(self.bouton_nation, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_numsecu.AddGrowableCol(2)
        grid_sizer_identite.Add(sizer_numsecu, 1, wx.EXPAND, 0)
        
        grid_sizer_identite.AddGrowableCol(1)
        sizer_identite.Add(grid_sizer_identite, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_1.Add(sizer_identite, 1, wx.LEFT|wx.TOP|wx.EXPAND, 5)
        
        # Sizer situation sociale + Coords
        sizer2_situation = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        sizer2_situation.Add(self.combo_box_situation, 0, wx.ALL|wx.EXPAND, 0)
        sizer2_situation.Add(self.bouton_situations, 0, wx.ALL|wx.EXPAND, 0)
        sizer_situation_sociale.Add(sizer2_situation, 0, wx.ALL|wx.EXPAND, 5)
        sizer2_situation.AddGrowableCol(0)
        
        grid_sizer_2.Add(sizer_situation_sociale, 1, wx.EXPAND, 0)
        grid_sizer_coords.Add(self.list_ctrl_coords, 0, wx.EXPAND, 0)
        sizer_boutons_tel.Add(self.button_coords_ajout, 0, 0)
        sizer_boutons_tel.Add(self.button_coords_modif, 0, wx.TOP, 5)
        sizer_boutons_tel.Add(self.button_coords_suppr, 0, wx.TOP, 5)
        grid_sizer_coords.Add(sizer_boutons_tel, 1, wx.EXPAND, 0)
        grid_sizer_coords.AddGrowableRow(0)
        grid_sizer_coords.AddGrowableCol(0)
        sizer_coords.Add(grid_sizer_coords, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_2.Add(sizer_coords, 1, wx.EXPAND, 0)
        grid_sizer_2.AddGrowableRow(1)
        grid_sizer_2.AddGrowableCol(0)
        grid_sizer_1.Add(grid_sizer_2, 1, wx.RIGHT|wx.TOP|wx.EXPAND, 5)
        
        # Sizer Adresse
        grid_sizer_adresse.Add(self.label_adresse, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.text_adresse, 0, wx.EXPAND, 0)
        grid_sizer_adresse.Add(self.label_cp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ville.Add(self.text_cp, 0, 0, 0)
        grid_sizer_ville.Add(self.label_ville, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_ville.Add(self.text_ville, 0, wx.EXPAND, 0)
        grid_sizer_ville.Add(self.bouton_options_ville, 0, wx.LEFT, 5)
        grid_sizer_ville.AddGrowableCol(2)
        grid_sizer_adresse.Add(grid_sizer_ville, 1, wx.EXPAND, 0)
        grid_sizer_adresse.AddGrowableCol(1)
        sizer_adresse.Add(grid_sizer_adresse, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_1.Add(sizer_adresse, 1, wx.LEFT|wx.BOTTOM|wx.EXPAND, 5)

        # Sizer Mémo
        grid_sizer_memo.Add(self.text_memo, 0, wx.ALL|wx.EXPAND, 5)
        grid_sizer_memo.AddGrowableRow(0)
        grid_sizer_memo.AddGrowableCol(0)
        sizer_memo.Add(grid_sizer_memo, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(sizer_memo, 1, wx.RIGHT|wx.BOTTOM|wx.EXPAND, 5)

        # Finalisation
        self.SetSizer(grid_sizer_1)
        grid_sizer_1.AddGrowableRow(0)
        grid_sizer_1.AddGrowableRow(1)
        grid_sizer_1.AddGrowableCol(0)
        grid_sizer_1.AddGrowableCol(1)
        
        self.grid_sizer_identite = grid_sizer_identite
        
    def MAJ_barre_problemes(self):
        self.parent.GetGrandParent().MAJ_barre_problemes()
    
    def OnImageNumSecu(self, event):
        """ Si on clique sur l'image d'état du num sécu """
        message = u"""
        Numéro de sécurité sociale : A BB CC DD EEE FFF GG
        
        A : Sexe (1=homme | 2=femme)
        BB : Année de naissance
        CC : Mois de naissance
        DD : Département de naissance (99 si né à l'étranger)
        EEE : Code INSEE de la commune de naissance ou du pays si né à l'étranger
        FFF : Numéro d'ordre INSEE
        GG : Clé
        """
        dlg = wx.MessageDialog(self, message, _(u"Constitution d'un numéro de sécurité sociale"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnBoutonPays(self, event):
        dlg = DLG_Config_pays.Dialog(self, "", IDpays=self.IDpays_naiss, saisie="FicheIndiv_pays_naiss")
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonNation(self, event):
        dlg = DLG_Config_pays.Dialog(self, "", IDpays=self.IDpays_nation, saisie="FicheIndiv_nationalite")
        dlg.ShowModal()
        dlg.Destroy()
                        
    def OnBoutonSituations(self, event):
        dlg = DLG_Config_situations.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnActivate(self, event):
        print("YAAAAAAAAAAAAAAAAAAAA... ", str(event.GetActive()))
        event.Skip()

    def OnOptionsVilleNaiss(self, event): 
        self.AppelGestionVilles("text_cp_naiss", "text_ville_naiss", "Lieu de naissance")
        event.Skip()

    def OnOptionsVille(self, event): 
        self.AppelGestionVilles("text_cp", "text_ville", _(u"Lieu de résidence"))
        event.Skip()

    def AppelGestionVilles(self, controleCP, controleVille, nomChamp):
        # Ouverture de la fenêtre Gestion des villes
        from Dlg import DLG_Gestion_villes
        dlg = DLG_Gestion_villes.Dialog(self, "Titre", exportCP=controleCP, exportVille=controleVille, exportChamp=nomChamp)
        dlg.ShowModal()
        dlg.Destroy()

    def OnAjoutTel(self, event): 
        self.AjouterCoord()
        event.Skip()

    def AjouterCoord(self):
        dlg = DLG_Saisie_coords.Dialog(self, IDcoord=0, IDpersonne=self.IDpersonne)
        dlg.ShowModal()
        dlg.Destroy()

    def OnModifTel(self, event):
        self.ModifierCoord()
        event.Skip()

    def ModifierCoord(self):
        """ Modification de coordonnées """
        index = self.list_ctrl_coords.GetFirstSelected()
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un item à modifier dans la liste des coordonnées"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        varIDcoord = self.list_ctrl_coords.GetItemData(index)
        dlg = DLG_Saisie_coords.Dialog(self, IDcoord=varIDcoord, IDpersonne=self.IDpersonne)
        dlg.ShowModal()
        dlg.Destroy()


    def OnSupprTel(self, event): # wxGlade: Panel_general.<event_handler>
        self.SupprimerCoord()
        event.Skip()

    def SupprimerCoord(self):
        """ Suppression d'une coordonnée """
        index = self.list_ctrl_coords.GetFirstSelected()

        # Vérifie qu'un item a bien été sélectionné
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un item à supprimer dans la liste des coordonnées"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation
        texteCoord = self.list_ctrl_coords.GetItemText(index)
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer cette coordonnée ? \n\n> ") + texteCoord))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        varIDcoord = self.list_ctrl_coords.GetItemData(index)

        # Suppression
        DB = GestionDB.DB()
        DB.ReqDEL("coordonnees", "IDcoord", varIDcoord)

        # MàJ du listCtrl Coords de la fiche individuelle
        self.list_ctrl_coords.Remplissage()
        self.MAJ_barre_problemes()
        

    def MaJ_Civilite(self):
        # Valide le texte saisi
##        self.CouleurSiVide(self.combo_box_civilite, "combo")
        valeur = self.combo_box_civilite.GetStringSelection()
        
        # Active ou non le controle Nom de jeunes fille
        if valeur == "Mr" or valeur == "Melle":
            self.label_nomjf.Enable(False)
            self.text_ctrl_nomjf.Enable(False)
            self.text_nom.SetFocus()
        elif valeur == "Mme" :
            self.label_nomjf.Enable(True)
            self.text_ctrl_nomjf.Enable(True)
##            self.CouleurSiVide(self.text_ctrl_nomjf, "texte")

    def MaJ_DateNaiss(self):
        # Verifie la validite de la date
        if self.text_date_naiss.GetValue() == "  /  /    ":
            self.text_age.SetValue("")
            self.MaJ_DateNaiss_Fiche()
            self.MAJ_barre_problemes()
            return
        validation = ValideDate(texte=self.text_date_naiss.GetValue(), date_min="01/01/1910", date_max="01/01/2030")
        if validation == False:
            self.text_date_naiss.SetFocus()
            return
            
        # Calcul de l'age de la personne
        valeurDate = self.text_date_naiss.GetValue()
        jour = int(valeurDate[:2])
        mois = int(valeurDate[3:5])
        annee = int(valeurDate[6:10])
        bday = datetime.date(annee, mois, jour)
        datedujour = datetime.date.today()
        age = (datedujour.year - bday.year) - int((datedujour.month, datedujour.day) < (bday.month, bday.day))
        self.text_age.SetValue(str(age) + " ans")
        
        self.MaJ_DateNaiss_Fiche()

# end of class Panel_general

    def OnTextCivilite(self, event):
        self.MaJ_Civilite()
        self.MaJ_DateNaiss_Fiche()
        self.MAJ_Photo()
        event.Skip()
    
    def MAJ_Photo(self):
        """ MAJ de la photo du header """
        if self.GetGrandParent().GetParent().photo != None : return
        valeur = self.combo_box_civilite.GetStringSelection()
        if valeur == "Mr" :
            img = "Homme.png"
        elif valeur == "Mme" or valeur == "Melle":
            img = "Femme.png"
        else :
            img = "Personne.png"
        
        # MAJ Photo
        nomFichier = Chemins.GetStaticPath("Images/128x128/" + img)
        self.GetGrandParent().GetParent().bitmap_photo.SetPhoto(self.IDpersonne, nomFichier, taillePhoto=(128, 128), qualite=100)

    def OnTextNomJF(self, event):
        # Valide le texte saisi
##        self.CouleurSiVide(self.text_ctrl_nomjf, "texte")
        event.Skip()

    def OnTextNom(self, event):
        # Valide le texte saisi
##        self.CouleurSiVide(self.text_nom, "texte")
        self.MaJ_NomPrenom_Fiche()
        event.Skip()

    def OnTextPrenom(self, event):
        # Valide le texte saisi
##        self.CouleurSiVide(self.text_prenom, "texte")
        self.MaJ_NomPrenom_Fiche()
        event.Skip()

    def OnTextDateNaiss(self, event):
        # Valide le texte saisi
        self.MaJ_DateNaiss_Fiche()
##        self.CouleurSiVide(self.text_date_naiss, "texte")
        event.Skip()

    def OnTextLieuNaiss(self, event):
        # Valide le texte saisi
        self.MaJ_DateNaiss_Fiche()
##        self.CouleurSiVide(self.text_ville_naiss, "combo")
        event.Skip()

    def OnTextNumSecu(self, event):
        # Valide le texte saisi
##        self.CouleurSiVide(self.text_numsecu, "texte")
        event.Skip()

    def OnTextAdresse(self, event):
        # Valide le texte saisi
        self.MaJ_Adresse_Fiche()
##        self.CouleurSiVide(self.text_adresse, "texte")
        event.Skip()

    def OnTextCP(self, event):
        # Valide le texte saisi
        self.MaJ_Adresse_Fiche()
##        self.CouleurSiVide(self.text_cp, "texte")
        event.Skip()

    def OnTextVille(self, event):
        # Valide le texte saisi
        self.MaJ_Adresse_Fiche()
##        self.CouleurSiVide(self.text_ville, "texte")
        event.Skip()
        
    def CouleurSiVide(self, controle, typeControle):
        """ Change la couleur du fond du controle s'il est vide """
        
        # Version texte
        if typeControle == "texte" :
            if len(controle.GetValue()) == 0:
                controleVide = True
            else:
                controleVide = False

        # Version combo
        if typeControle == "combo" :
            if len(controle.GetValue()) == 0:
                controleVide = True
            else:
                controleVide = False

        # Application du changement de couleur
        if controleVide == True:
            controle.SetBackgroundColour("PINK")
            controle.SetFocus()
            controle.Refresh()
            return False
        else:
            controle.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            controle.Refresh()
            return True
        
    def AfficheAutresPages(self):
        """ Affiches les autres page que Généralités si les contrôles sont remplis """
        try :
            if self.combo_box_civilite.GetStringSelection() != "" and self.text_nom.GetValue() != "" and self.text_prenom.GetValue() != "" :
                self.GetParent().AfficheAutresPages(True)
            else:
                self.GetParent().AfficheAutresPages(False)
        except : pass

    def OnKillFocusCivilite(self, event):
        valeur = self.combo_box_civilite.GetStringSelection()
        if valeur != "Mr" and valeur != "Mme" and valeur != "Melle" and valeur != "" :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez saisir ici que les valeur 'Mr', 'Melle' ou 'Mme'."), "Erreur de saisie", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.combo_box_civilite.SetFocus()
            event.Skip()
            return
        
        self.MAJ_barre_problemes()
        self.AfficheAutresPages()
        event.Skip()
            
    def OnKillFocusNom(self, event):
        texte = self.text_nom.GetValue()
        if len(texte) != 0 :
            self.text_nom.SetValue(texte.upper())
        self.MAJ_barre_problemes()
        self.AfficheAutresPages()
        event.Skip()

    def OnKillFocusNomJFille(self, event):
        nomJF = self.text_ctrl_nomjf.GetValue()
        if nomJF != "" :
            self.text_ctrl_nomjf.SetValue(nomJF.upper())
        self.MAJ_barre_problemes()
        event.Skip()
            
    def OnKillFocusPrenom(self, event):
        texte = self.text_prenom.GetValue()
        if len(texte) > 1 :
            texte = texte[:1].upper() + texte[1:]
            self.text_prenom.SetValue(texte)
        self.MAJ_barre_problemes()
        self.AfficheAutresPages()
        event.Skip()

    def OnKillFocusDateNaiss(self, event):
        self.MaJ_DateNaiss()
        self.MAJ_barre_problemes()
        event.Skip()

    def OnKillFocusNumSecu(self, event):
        """ Verifie la validite du numero de securite sociale """
        self.SetEtatNumSecu()
        self.MAJ_barre_problemes()
        event.Skip()
    
    def SetEtatNumSecu(self):
        validation, message = ValideNumSecu(self.text_numsecu.GetValue(), self.combo_box_civilite.GetStringSelection(), self.text_date_naiss.GetValue(), self.text_cp_naiss.GetValue())
        
        # Message si numéro de sécu erroné
        if validation == False :
            self.image_numsecu.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
            if self.remplissageEnCours == False :
                wx.MessageBox(message, _(u"Numéro de sécurité sociale erroné"))
            
        # Pas de num sécu saisi
        if validation == None : 
            self.image_numsecu.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        
        #Le numéro de sécu est bon
        if validation == True :
            self.image_numsecu.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))
        
        self.grid_sizer_identite.Layout()
        
        
    def OnKillFocusAdresse(self, event):
        # Vérifie qu'il n'y a pas un saut de ligne à la fin de l'adresse
        txtAdresse = self.text_adresse.GetValue()
        if txtAdresse != "" :
            if txtAdresse.endswith("\n") :
                txtAdresse = txtAdresse[:-1]
                self.text_adresse.SetValue(txtAdresse)
        self.MAJ_barre_problemes()

    def OnKillFocusSituation(self, event):
        self.MAJ_barre_problemes()
        event.Skip()

    def SetInfobulleVille(self, controle, nomControle):
        """ Créé une info-bulle pour les cp et villes pour indiquer les régions et départements """
        if nomControle == "cp" or nomControle == "cp_naiss" :
            cp = controle.GetValue()
        if nomControle == "ville" :
            cp = self.text_cp.GetValue()
        if nomControle == "ville_naiss" :
            cp = self.text_cp_naiss.GetValue()
        
        if cp == "" or cp == "     " :
            if nomControle == "cp" or nomControle == "cp_naiss" :
                controle.SetToolTip(wx.ToolTip(_(u"Saisissez un code postal")))
            else :
                controle.SetToolTip(wx.ToolTip(_(u"Saisissez un nom de ville")))
        else:
            try :
                num_dep = cp[:2]
                nomDepartement, num_region = self.dictDepartements[num_dep]
                nomRegion = self.dictRegions[num_region]
                texte = _(u"Département : %s (%s)\nRégion : %s") % (nomDepartement, num_dep, nomRegion)
                controle.SetToolTip(wx.ToolTip(texte))
            except :
                if nomControle == "cp" or nomControle == "cp_naiss" :
                    controle.SetToolTip(wx.ToolTip(_(u"Le code postal saisi ne figure pas dans la base de données de TeamWorks")))
                else :
                    controle.SetToolTip(wx.ToolTip(_(u"Le nom de ville saisi ne figure pas dans la base de données de TeamWorks")))
        
        
# Fonctions pour l'autocomplete des cp et villes NAISS---------------------------------------------------------------

    def Code_KillFocus1(self, event):
        """ Quand le contrôle Code perd le focus """
        self.MAJ_barre_problemes()
        
        if self.autoComplete == False :
            return
        
        textCode = self.text_cp_naiss.GetValue()
        # On vérifie que la ville n'est pas déjà dans la case ville
        villeSelect = self.text_ville_naiss.GetValue()
        if villeSelect != '':
            for ville, cp in self.listeVilles:
                if ville == villeSelect and cp == textCode :
                    self.SetInfobulleVille(self.text_cp_naiss, "cp_naiss")
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
                dlg = wx.MessageDialog(self, _(u"Ce code postal n'est pas répertorié dans la base de données. \nVérifiez que vous n'avez pas fait d'erreur de saisie."), "Information", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            self.SetInfobulleVille(self.text_cp_naiss, "cp_naiss")
            return
        
        if nbreReponses == 1:
            resultat = ReponsesVilles[0]
            self.text_ville_naiss.SetValue(resultat)

        # Fenêtre de choix entre plusieurs codes postau
        if nbreReponses > 1:
            resultat = self.ChoixVilles(textCode, ReponsesVilles)
            if resultat != '':
                self.text_ville_naiss.SetValue(resultat)

        # Sélection du texte de la case ville pour l'autocomplete
        self.text_ville_naiss.SetSelection(0, len(resultat))
        
        self.MaJ_DateNaiss_Fiche()
        self.SetInfobulleVille(self.text_cp_naiss, "cp_naiss")
        event.Skip()

    def Ville_KillFocus1(self, event):
        """ Quand le contrôle ville perd le focus """
        self.MAJ_barre_problemes()
        
        if self.autoComplete == False :
            return
        
        villeSelect = self.text_ville_naiss.GetValue()
        if villeSelect == '':
            self.MaJ_DateNaiss_Fiche()
            self.SetInfobulleVille(self.text_ville_naiss, "ville_naiss")
            self.SetInfobulleVille(self.text_cp_naiss, "cp_naiss")
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
                self.text_cp_naiss.SetValue(resultat)

        # Si la ville saisie n'existe pas
        if nbreCodes == 0:
            dlg = wx.MessageDialog(self, _(u"Cette ville n'est pas répertoriée dans la base de données. \nVérifiez que vous n'avez pas fait d'erreur de saisie."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        
        self.SetInfobulleVille(self.text_ville_naiss, "ville_naiss")
        self.SetInfobulleVille(self.text_cp_naiss, "cp_naiss")
        self.MaJ_DateNaiss_Fiche()
        event.Skip()

    def VilleChar1(self, event):
        if event.GetKeyCode() == 8:
            self.text_ville_naiss.ignoreEvtText = True
            self.MaJ_DateNaiss_Fiche()
        event.Skip()

    def VilleText1(self, event):
        """ A chaque frappe de texte -> analyse """
##        self.CouleurSiVide(self.text_ville_naiss, "texte")
        if self.autoComplete == False :
            return
        
        if self.text_ville_naiss.ignoreEvtText:
            self.text_ville_naiss.ignoreEvtText = False
            self.MaJ_DateNaiss_Fiche()
            return
        currentText = event.GetString().upper()
        found = False
        for ville, cp in self.listeVilles :
            if ville.startswith(currentText):
                self.text_ville_naiss.ignoreEvtText = True
                self.text_ville_naiss.SetValue(ville)
                self.text_ville_naiss.SetInsertionPoint(len(currentText))
                self.text_ville_naiss.SetSelection(len(currentText), len(ville))
                self.text_cp_naiss.SetValue(str(cp))
                self.MaJ_DateNaiss_Fiche()
                self.SetInfobulleVille(self.text_ville_naiss, "ville_naiss")
                self.SetInfobulleVille(self.text_cp_naiss, "cp_naiss")
                found = True
                break
        if not found:
            self.text_cp_naiss.SetValue('')
            self.MaJ_DateNaiss_Fiche()
            self.SetInfobulleVille(self.text_ville_naiss, "ville_naiss")
            self.SetInfobulleVille(self.text_cp_naiss, "cp_naiss")
            event.Skip()

        # FIN DES ------------- Fonctions pour l'autocomplete des cp et villes NAISS-----------------------------------------------


        # Fonctions pour l'autocomplete des cp et villes ---------------------------------------------------------------

    def Code_KillFocus2(self, event):
        """ Quand le contrôle Code perd le focus """
        self.MAJ_barre_problemes()
        
        if self.autoComplete == False :
            return
        
        textCode = self.text_cp.GetValue()
        self.MaJ_Adresse_Fiche()
        # On vérifie que la ville n'est pas déjà dans la case ville
        villeSelect = self.text_ville.GetValue()
        if villeSelect != '':
            for ville, cp in self.listeVilles:
                if ville == villeSelect and str(cp) == str(textCode) :
                    self.SetInfobulleVille(self.text_cp, "cp")
                    return
                
        # On recherche si plusieurs villes ont ce même code postal
        ReponsesVilles = []
        for ville, cp in self.listeVilles:
            if str(cp) == str(textCode):
                ReponsesVilles.append(ville)
        nbreReponses = len(ReponsesVilles)

        # Code postal introuvable
        if nbreReponses == 0:
            if textCode.strip() != '':
                dlg = wx.MessageDialog(self, _(u"Ce code postal n'est pas répertorié dans la base de données. \nVérifiez que vous n'avez pas fait d'erreur de saisie."), "Information", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            self.SetInfobulleVille(self.text_cp, "cp")
            return
        
        if nbreReponses == 1:
            resultat = ReponsesVilles[0]
            self.text_ville.SetValue(resultat)

        # Fenêtre de choix entre plusieurs codes postau
        if nbreReponses > 1:
            resultat = self.ChoixVilles(textCode, ReponsesVilles)
            if resultat != '':
                self.text_ville.SetValue(resultat)

        # Sélection du texte de la case ville pour l'autocomplete
        self.text_ville.SetSelection(0, len(resultat))
        
        self.MaJ_Adresse_Fiche()
        self.SetInfobulleVille(self.text_cp, "cp")
        event.Skip()

    def Ville_KillFocus2(self, event):
        """ Quand le contrôle ville perd le focus """
        self.MAJ_barre_problemes()
        
        if self.autoComplete == False :
            return
        
        villeSelect = self.text_ville.GetValue()
        if villeSelect == '':
            self.MaJ_Adresse_Fiche()
            self.SetInfobulleVille(self.text_ville, "ville")
            self.SetInfobulleVille(self.text_cp, "cp")
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
                self.text_cp.SetValue(resultat)

        # Si la ville saisie n'existe pas
        if nbreCodes == 0:
            dlg = wx.MessageDialog(self, _(u"Cette ville n'est pas répertoriée dans la base de données. \nVérifiez que vous n'avez pas fait d'erreur de saisie."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        
        self.SetInfobulleVille(self.text_ville, "ville")
        self.SetInfobulleVille(self.text_cp, "cp")
        self.MaJ_Adresse_Fiche()
        event.Skip()

    def VilleChar2(self, event):
        if event.GetKeyCode() == 8:
            self.text_ville.ignoreEvtText = True
            self.MaJ_Adresse_Fiche()
        event.Skip()

    def VilleText2(self, event):
        """ A chaque frappe de texte -> analyse """
##        self.CouleurSiVide(self.text_ville, "texte")

        if self.autoComplete == False :
            return
        
        if self.text_ville.ignoreEvtText:
            self.text_ville.ignoreEvtText = False
            self.MaJ_Adresse_Fiche()
            return
        currentText = event.GetString().upper()
        found = False
        try:
            for ville, cp in self.listeVilles :
                if ville.startswith(currentText):
                    self.text_ville.ignoreEvtText = True
                    self.text_ville.SetValue(ville)
                    self.text_ville.SetInsertionPoint(len(currentText))
                    self.text_ville.SetSelection(len(currentText), len(ville))
                    self.text_cp.SetValue(str(cp))
                    self.MaJ_Adresse_Fiche()
                    self.SetInfobulleVille(self.text_ville, "ville")
                    self.SetInfobulleVille(self.text_cp, "cp")
                    found = True
                    break
        except:
            pass
        if not found:
            self.text_cp.SetValue('')
            self.MaJ_Adresse_Fiche()
            self.SetInfobulleVille(self.text_ville, "ville")
            self.SetInfobulleVille(self.text_cp, "cp")
            event.Skip()

    def ChoixVilles(self, cp, listeReponses):
        """ Boîte de dialogue pour donner le choix entre plusieurs villes possédant un code postal identique """
        resultat = ""
        titre = _(u"Sélection d'une ville")
        nbreReponses = len(listeReponses)
        listeReponses.sort()
        message = str(nbreReponses) + _(u" villes possèdent le code postal ") + str(cp) + _(u". Double-cliquez sur\nle nom d'une ville pour la sélectionner :")
        dlg = wx.SingleChoiceDialog(self, message, titre, listeReponses, wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            resultat = dlg.GetStringSelection()
        dlg.Destroy()
        return resultat

    def ChoixCodes(self, ville, listeReponses):
        """ Boîte de dialogue pour donner le choix entre plusieurs villes possédant le même nom """
        resultat = ""
        titre = _(u"Sélection d'une ville")
        nbreReponses = len(listeReponses)
        listeReponses.sort()
        message = str(nbreReponses) + _(u" villes portent le nom ") + str(ville) + _(u". Double-cliquez sur\nle code postal d'une ville pour la sélectionner :")
        dlg = wx.SingleChoiceDialog(self, message, titre, listeReponses, wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            resultat = dlg.GetStringSelection()
        dlg.Destroy()
        return resultat


        # FIN DES ------------- Fonctions pour l'autocomplete des cp et villes -----------------------------------------------


        # --------------------------------------------------------------------------------------------------------------------
        # FONCTIONS DE SAUVEGARDE DES DONNEES DANS LA BASE DE DONNEES


    def Sauvegarde(self):
        """ Sauvegarde des donnees dans la base """

        varCivilite = self.combo_box_civilite.GetStringSelection()
        varNom = self.text_nom.GetValue()
        varNom_JFille = self.text_ctrl_nomjf.GetValue()
        varPrenom = self.text_prenom.GetValue()

        # Validation date de naissance
        temp = self.text_date_naiss.GetValue()
        if temp == "  /  /    ":
            varDate_Naiss = None
        else:
            jour = int(temp[:2])
            mois = int(temp[3:5])
            annee = int(temp[6:10])
            varDate_Naiss = datetime.date(annee, mois, jour)

        
        varCp_Naiss = self.text_cp_naiss.GetValue()
        if varCp_Naiss == "     " : varCp_Naiss = None
        varVille_Naiss = self.text_ville_naiss.GetValue()
        varPays_Naiss = self.IDpays_naiss
        varNationalite = self.IDpays_nation
        varNum_Secu = self.text_numsecu.GetValue()
        varAdresse_resid = self.text_adresse.GetValue()
        varCp_Resid = self.text_cp.GetValue()
        if varCp_Resid == "     " : varCp_Resid = None
        varVille_Resid = self.text_ville.GetValue()
        varMemo = self.text_memo.GetValue()

        # Validation IDSituation
        try:
            temp = self.combo_box_situation.GetClientData(self.combo_box_situation.GetSelection())
            if temp == None or temp == '':
                varIDSituation = 0
            else:
                varIDSituation = temp
        except:
            varIDSituation = 0

        listeDonnees = [    ("civilite",        varCivilite),
                            ("nom",             varNom),
                            ("nom_jfille",      varNom_JFille),
                            ("prenom",          varPrenom),
                            ("date_naiss",      varDate_Naiss),
                            ("cp_naiss",        varCp_Naiss),
                            ("ville_naiss",     varVille_Naiss),
                            ("pays_naiss",     varPays_Naiss),
                            ("nationalite",     varNationalite),
                            ("num_secu",        varNum_Secu),
                            ("adresse_resid",   varAdresse_resid),
                            ("cp_resid",        varCp_Resid),
                            ("ville_resid",     varVille_Resid),
                            ("memo",            varMemo),
                            ("IDsituation",     varIDSituation),

                        ]

        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        
        if self.IDpersonne == 0:
            # Si IDpersonne = 0, on créée un nouvel enregistrement
            newID = DB.ReqInsert("personnes", listeDonnees)
            self.IDpersonne = newID
            self.GetGrandParent().GetParent().IDpersonne = newID
            self.MaJ_Header_Fiche()
        else:
            # Si IDpersonne != 0, on modifie l'enregistrement
            DB.ReqMAJ("personnes", listeDonnees, "IDpersonne", self.IDpersonne)
            

    def MaJ_Header_Fiche(self):
        """ MàJ de la fiche individuelle """
        self.parent.GetGrandParent().label_hd_nomPrenom
        self.parent.GetGrandParent().MaJ_header()

    def MaJ_NomPrenom_Fiche(self):
        """ MàJ de la fiche individuelle """
        nom = self.text_nom.GetValue()
        prenom = self.text_prenom.GetValue()
        if nom == "":
            nom = "NOM"
        if prenom == "":
            prenom = _(u"Prénom")
        texte = nom + ", " + prenom
        self.GetParent().GetGrandParent().label_hd_nomPrenom.SetLabel(texte)

    def MaJ_Adresse_Fiche(self):
        """ MàJ de la fiche individuelle """
        adresse = self.text_adresse.GetValue()
        cp = self.text_cp.GetValue()
        ville = self.text_ville.GetValue()
        if adresse == "" and cp == "     " and ville == "" : 
            texte = _(u"Adresse inconnue")
        else :
            texte = _(u"Résidant ") + adresse + " " + cp + " " + ville
        self.GetParent().GetGrandParent().label_hd_adresse.SetLabel(texte)

    def MaJ_DateNaiss_Fiche(self):
        """ MàJ de la fiche individuelle """
        dateNaiss = self.text_date_naiss.GetValue()
        villeNaiss = self.text_ville_naiss.GetValue()
        civilite = self.combo_box_civilite.GetStringSelection()
        age = self.text_age.GetValue()
        if civilite == "Mr" : 
            txtCivilite = u"Né"
        elif civilite == "Mme" or civilite == "Melle" :
            txtCivilite = _(u"Née")
        else:
            return
        if dateNaiss == "  /  /    " and villeNaiss == "" : 
            texte = _(u"Date et lieu de naissance inconnus.")
        elif dateNaiss != "  /  /    " and villeNaiss == "" : 
            texte = txtCivilite + " le " + dateNaiss + ", " + age
        elif dateNaiss == "  /  /    " and villeNaiss != "" : 
            texte = txtCivilite + u" à " + villeNaiss + _(u" (date inconnue)")
        elif dateNaiss != "  /  /    " and villeNaiss != "" : 
            texte = txtCivilite + " le " + dateNaiss + u" à " + villeNaiss + ", " + age
        self.GetParent().GetGrandParent().label_hd_naiss.SetLabel(texte)        

    def Importation(self,):
        """ Importation des donnees de la base """

        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        req = "SELECT civilite, nom, nom_jfille, prenom, date_naiss, cp_naiss, ville_naiss, pays_naiss, nationalite, num_secu, adresse_resid, cp_resid, ville_resid, memo, IDsituation FROM personnes WHERE IDpersonne = %d" % self.IDpersonne
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()[0]
        DB.Close()
        
        civilite = donnees[0]
        nom = donnees[1]
        nom_jfille = donnees[2]
        prenom = donnees[3]
        date_naiss = donnees[4]
        cp_naiss = donnees[5]
        ville_naiss = donnees[6]
        pays_naiss = donnees[7]
        nationalite = donnees[8]
        num_secu = donnees[9]
        adresse_resid = donnees[10]
        cp_resid = donnees[11]
        ville_resid = donnees[12]
        memo = donnees[13]
        IDsituation = donnees[14]
        
        # Placement des données dans les contrôles
        self.autoComplete = False
        
        # TextCtrl
        self.text_ctrl_nomjf.SetValue(nom_jfille)
        self.text_nom.SetValue(nom)
        self.text_prenom.SetValue(prenom)
        self.text_ville_naiss.SetValue(ville_naiss)
        self.text_adresse.SetValue(adresse_resid)
        self.text_ville.SetValue(ville_resid)
        self.text_memo.SetValue(memo)

        # Champs spéciaux
        self.text_numsecu.SetValue(num_secu)
        try :
            if cp_resid != "" and cp_resid != None and cp_resid != "     " :
                if type(cp_resid) == six.text_type : cp_resid = int(cp_resid)
                self.text_cp.SetValue("%05d" % cp_resid)
            if cp_naiss != "" and cp_naiss != None and cp_naiss != "     " :
                if type(cp_naiss) == six.text_type : cp_naiss = int(cp_naiss)
                self.text_cp_naiss.SetValue("%05d" % cp_naiss)
        except :
            dlg = wx.MessageDialog(self, _(u"Erreur dans l'importation des codes postaux."), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

        # Date de naissance
        temp = date_naiss
        if temp == "  /  /    " or temp == '' or temp == None:
            temp = "  /  /    "
        else:
            jour = str(temp[8:10])
            mois = str(temp[5:7])
            annee = str(temp[:4])
            temp = jour + "/" + mois + "/" + annee
        self.text_date_naiss.SetValue(temp)

        # Civilité
        self.combo_box_civilite.SetStringSelection(civilite)

        # Situation sociale
        for IDsitu, situation in self.listeSituations:
            if int(IDsitu) == int(IDsituation) :
                self.combo_box_situation.SetStringSelection(situation)
                
        # Pays de naissance et nationalité
        self.SetPaysNaiss(IDpays=pays_naiss)
        self.SetNationalite(IDpays=nationalite)

        # Ajustements
        self.autoComplete = True
        self.MaJ_Civilite()
        self.MaJ_DateNaiss()
        
        # Règlages des info-bulles
        self.SetInfobulleVille(self.text_cp_naiss, "cp_naiss")
        self.SetInfobulleVille(self.text_cp, "cp")
        self.SetInfobulleVille(self.text_ville_naiss, "ville_naiss")
        self.SetInfobulleVille(self.text_ville, "ville")
        
    def SetPaysNaiss(self, IDpays) :
        pays = self.Recherche_Pays(IDpays=IDpays) 
        self.image_pays.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/Drapeaux/" + pays[1] + ".png"), wx.BITMAP_TYPE_PNG))
        self.image_pays.SetToolTip(wx.ToolTip(_(u"Pays de naissance : %s" % pays[2])))
        self.IDpays_naiss = IDpays
        
    def SetNationalite(self, IDpays) :
        pays = self.Recherche_Pays(IDpays=IDpays)
        self.image_nation.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/Drapeaux/" + pays[1] + ".png"), wx.BITMAP_TYPE_PNG))
        self.image_nation.SetToolTip(wx.ToolTip(_(u"Nationalité : %s" % pays[3])))
        self.IDpays_nation = IDpays

    def ImportListeSituations(self):
        """ Récupération de la liste des situations dans la base """
        
        # Récupération du IDSituation actuel
        try:
            temp = self.combo_box_situation.GetClientData(self.combo_box_situation.GetSelection())
            if temp == None or temp == '':
                IDSituation = 0
            else:
                IDSituation = temp
        except:
            IDSituation = 0

        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        req = "SELECT * FROM situations"
        DB.ExecuterReq(req)
        self.listeSituations = DB.ResultatReq()
        DB.Close()

        # Placement de la liste dans le ComboBox Situations
        self.combo_box_situation.Clear()
        for key, valeur in self.listeSituations :
            self.combo_box_situation.Append(valeur, key)
        
        # Choix de la valeur
        if IDSituation != 0 :
            try :
                for IDsitu, situation in self.listeSituations:
                    if int(IDsitu) == int(IDSituation) :
                        self.combo_box_situation.SetStringSelection(situation)
            except : pass
            

    def Recherche_Pays(self, IDpays=0, nomPays=""):
        """ Récupération de la liste des pays dans la base """
        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        if nomPays == "" :
            req = "SELECT IDpays, code_drapeau, nom, nationalite FROM pays WHERE IDpays=%d" % IDpays
        else:
            req = "SELECT IDpays, code_drapeau, nom, nationalite FROM pays WHERE nom='%s'" % nomPays
        DB.ExecuterReq(req)
        listePays = DB.ResultatReq()
        DB.Close()
        if len(listePays) == 0 : return
        return listePays[0]
       

# Fonctions à mettre dans un module séparé

def ValideNumSecu(texte, civilite, date_naiss, dep_naiss):

    # On vérifie que tous les chiffres ont été donnés
    texteSansEsp = ""
    for lettre in texte:
        if lettre != " ":
            texteSansEsp = texteSansEsp + lettre

    nbreChiffres = len(texteSansEsp)

    if nbreChiffres == 0 :
        return None, ""

    if nbreChiffres < 15 :
        message = _(u"Il manque ") + str(15 - nbreChiffres) + _(u" chiffre(s) au numéro de sécurité sociale que vous venez de saisir. Veuillez le vérifier.")
        return False, message

    if nbreChiffres == 15:

        # Vérification avec la civilite
        if civilite == "Mr":
            if int(texteSansEsp[0]) != 1:
                message = _(u"Le numéro de sécurité sociale ne correspond pas à la civilité de la personne (le premier chiffre devrait être 1).")
                return False, message

        if civilite == "Melle" or civilite == "Mme":
            if int(texteSansEsp[0]) != 2:
                message = _(u"Le numéro de sécurité sociale ne correspond pas à la civilité de la personne (le premier chiffre devrait être 2).")
                wx.MessageBox(message, _(u"Erreur de numéro de sécurité"))
                return False, message
                
        # Vérification avec la date de naissance
        if date_naiss != "  /  /    ":
            mois = str(date_naiss[3:5])
            annee = str(date_naiss[8:10])

            if annee != str(texteSansEsp[1:3]):
                message = _(u"Le numéro de sécurité sociale ne correspond pas à la date de naissance de la personne.")
                return False, message
            elif mois != str(texteSansEsp[3:5]):
                message = _(u"Le numéro de sécurité sociale ne correspond pas à la date de naissance de la personne.")
                return False, message
                    
        # Vérification avec le département de naissance
        if dep_naiss != "":
            dep = dep_naiss[0:2]
            if str(dep) != str(texteSansEsp[5:7]):
                message = _(u"Le numéro de sécurité sociale ne correspond pas au lieu de naissance de la personne.")
                return False, message
        
        # Vérification de la clé
        cle = int((texteSansEsp[13:15]))
        cle_calculee = 97 - (int(texteSansEsp[:13]) % 97)
        if cle != cle_calculee :
            message = _(u"La clé du numéro de sécurité sociale ne semble pas cohérente. \nD'après mes calculs, la bonne clé devrait être %02d. \n\nVeuillez vérifier votre saisie...") % cle_calculee
            return False, message
        
        # Le num de sécu est ok
        return True, ""
        

def ValideDate(texte, date_min="01/01/1900", date_max="01/01/2090"):
    """ Verificateur de validite de date """
    listeErreurs = []
    # On vérifie si les cases ne sont pas vides
    if texte[0] == " " or texte[1] == " ":
        listeErreurs.append(_(u"le jour"))
    if texte[3] == " " or texte[4] == " ":
        listeErreurs.append(_(u"le mois"))
    if texte[6] == " " or texte[7] == " " or texte[8] == " " or texte[9] == " ":
        listeErreurs.append(_(u"l'année"))
    
    if texte != "  /  /    ":

        # On vérifie que les chiffres existent
        if _(u"le jour") not in listeErreurs:
            jour = int(texte[:2])
            if jour == 0 or jour > 31:
                listeErreurs.append(_(u"le jour"))

        if _(u"le mois") not in listeErreurs:
            mois = int(texte[3:5])
            if mois == 0 or mois > 12:
                listeErreurs.append(_(u"le mois"))
                
        if _(u"l'année") not in listeErreurs:
            annee = int(texte[6:10])
            if annee < 1900 or annee > 2999:
                listeErreurs.append(_(u"l'année"))
              
        # Affichage du message d'erreur
        
        if len(listeErreurs) != 0:
            # Message en cas de date incomplète
            if len(listeErreurs) == 1:
                message = _(u"Une incohérence a été détectée dans ") + listeErreurs[0]
            if len(listeErreurs) == 2:
                message = _(u"Des incohérences ont été détectées dans ") + listeErreurs[0] + " et " + listeErreurs[1]
            if len(listeErreurs) == 3:
                message = _(u"Des incohérences ont été détectées dans ") + listeErreurs[0]  + ", " + listeErreurs[1]  + " et " + listeErreurs[2]
            message = message + _(u" de la date que vous venez de saisir. Veuillez la vérifier.")

            wx.MessageBox(message, "Erreur de date")
            return False
        else:
            # On vérifie que les dates sont comprises dans l'intervalle donné en paramètre
            date_min = int(str(date_min[6:10]) + str(date_min[3:5]) + str(date_min[:2]))
            date_max = int(str(date_max[6:10]) + str(date_max[3:5]) + str(date_max[:2]))
            date_sel = int(str(texte[6:10]) + str(texte[3:5]) + str(texte[:2]))

            if date_sel < date_min:
                message = _(u"La date que vous venez de saisir semble trop ancienne. Veuillez la vérifier.")
                wx.MessageBox(message, "Erreur de date")
                return False
            if date_sel > date_max:
                message = _(u"La date que vous venez de saisir semble trop élevée. Veuillez la vérifier.")
                wx.MessageBox(message, "Erreur de date")
                return False
            
    else:
        return True

        
class ListCtrlCoords(wx.ListCtrl):
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, id, size=(140, -1), style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_SINGLE_SEL|wx.SUNKEN_BORDER)
        self.parent = parent
        self.popupIndex = -1       

        self.Bind(wx.EVT_SIZE, self.OnSize)
        if 'phoenix' not in wx.PlatformInfo and "linux" not in sys.platform :
            # Désactive la fenetre popup sous Linux
            self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
       
        # ImageList
        self.il = wx.ImageList(16,16)
        self.imgMaison = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Maison.png"), wx.BITMAP_TYPE_PNG))
        self.imgMobile = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mobile.png"), wx.BITMAP_TYPE_PNG))
        self.imgFax = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fax.png"), wx.BITMAP_TYPE_PNG))
        self.imgMail = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mail.png"), wx.BITMAP_TYPE_PNG))
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
        for key, valeurs in self.DictCoords.items():
            categorie = valeurs[2]
            texte = valeurs[3]
            # Création de l'item
            if 'phoenix' in wx.PlatformInfo:
                self.InsertItem(index, texte)
            else:
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
        DB = GestionDB.DB()
        req = "SELECT * FROM coordonnees WHERE IDpersonne = %d" % self.parent.IDpersonne
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
        self.parent.ModifierCoord()
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
        menuPop = UTILS_Adaptations.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Modifier, id=20)

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)

        # Si c'est un item Email, on ajoute "Envoyer Email"
        if self.DictCoords[key][2] == "Email" :
            menuPop.AppendSeparator()
            item = wx.MenuItem(menuPop, 40, _(u"Envoyer un E-mail"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mail.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Menu_Envoyer_Email, id=40)

        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Menu_Ajouter(self, event):
        self.parent.AjouterCoord()
        
    def Menu_Modifier(self, event):
        self.parent.ModifierCoord()

    def Menu_Supprimer(self, event):
        self.parent.SupprimerCoord()

    def Menu_Envoyer_Email(self, event):
        """ Envoyer un mail """
        print("Envoi d'un mail perso.")
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
            img = wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Maison.png"), wx.BITMAP_TYPE_PNG)
        if categorie == "Mobile":
            img = wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Mobile.png"), wx.BITMAP_TYPE_PNG)
        if categorie == "Fax":
            img = wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Fax.png"), wx.BITMAP_TYPE_PNG)
        if categorie == "Email":
            img = wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Mail.png"), wx.BITMAP_TYPE_PNG)

        # Création des widgets
        self.panel_base = wx.Panel(self, -1)
        self.bitmap_1 = wx.StaticBitmap(self.panel_base, -1, img)
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
     

    
