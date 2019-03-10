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
if 'phoenix' in wx.PlatformInfo:
    from wx.adv import BitmapComboBox
else :
    from wx.combo import BitmapComboBox
if 'phoenix' in wx.PlatformInfo:
    from wx.adv import DatePickerCtrl, DP_DROPDOWN
else :
    from wx import DatePickerCtrl, DP_DROPDOWN
from Dlg import DLG_Selection_periode
from Dlg import DLG_Config_fonctions
from Dlg import DLG_Config_affectations
from Dlg import DLG_Config_diffuseurs
from Utils import UTILS_Adaptations


class Panel(wx.Panel):
    def __init__(self, parent, IDemploi=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_emploi", style=wx.TAB_TRAVERSAL)
        self.IDemploi = IDemploi
        self.listeDisponibilites = []
        
        # Général
        self.sizer_generalites_staticbox = wx.StaticBox(self, -1, _(u"1. Généralités"))
        self.label_introduction = wx.StaticText(self, -1, _(u"Vous pouvez ici saisir les informations concernant l'offre d'emploi."))
        self.label_date_debut = wx.StaticText(self, -1, _(u"Lancement :"))
        self.ctrl_date_debut = DatePickerCtrl(self, -1, style=DP_DROPDOWN)
        self.label_date_fin = wx.StaticText(self, -1, _(u"Clôture :"))
        self.ctrl_date_fin = DatePickerCtrl(self, -1, style=DP_DROPDOWN)
        self.label_intitule = wx.StaticText(self, -1, _(u"Intitulé :"))
        self.ctrl_intitule = wx.TextCtrl(self, -1, "")
        self.label_detail = wx.StaticText(self, -1, _(u"Détail :"))
        self.ctrl_detail = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        self.ctrl_detail.SetMinSize((-1, 100))
        self.label_reference = wx.StaticText(self, -1, _(u"N° ANPE :"))
        self.ctrl_reference = wx.TextCtrl(self, -1, "")
                
        # Disponibilités
        self.sizer_disponibilites_staticbox = wx.StaticBox(self, -1, _(u"2. Disponibilités"))
        self.label_periodes = wx.StaticText(self, -1, _(u"Périodes :"))
        self.ctrl_periodes = ListBoxDisponibilites(self)
        self.ctrl_periodes.SetMinSize((20, 20))
        self.bouton_ajouter_periode = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_periode = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_periode = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.label_periodes_remarques = wx.StaticText(self, -1, _(u"Remarques :"))
        self.ctrl_periodes_remarques = wx.TextCtrl(self, -1, u"")
        
        # Poste
        self.sizer_poste_staticbox = wx.StaticBox(self, -1, _(u"3. Poste"))
        self.label_fonction = wx.StaticText(self, -1, _(u"Fonction :"))
        self.ctrl_fonction = CheckListBox(self)
        self.ctrl_fonction.SetMinSize((20, 20))
        self.ctrl_fonction.Remplissage(self.Importation_fonctions())
        self.bouton_fonctions = wx.Button(self, -1, "...", size=(20, 20))
        self.label_affectation = wx.StaticText(self, -1, _(u"Affectation :"))
        self.ctrl_affectations = CheckListBox(self)
        self.ctrl_affectations.SetMinSize((20, 20))
        self.ctrl_affectations.Remplissage(self.Importation_affectations())
        self.bouton_affectations = wx.Button(self, -1, "...", size=(20, 20))
        self.label_poste_remarques = wx.StaticText(self, -1, _(u"Remarques :"))
        self.ctrl_poste_remarques = wx.TextCtrl(self, -1, "")
        
        # Diffuseurs
        self.sizer_diffusion_staticbox = wx.StaticBox(self, -1, _(u"4. Diffusion de l'offre"))
        self.label_diffuseurs = wx.StaticText(self, -1, _(u"  Diffuseurs :"))
        self.ctrl_diffuseurs = CheckListBox(self)
        self.ctrl_diffuseurs.SetMinSize((20, 20))
        self.ctrl_diffuseurs.Remplissage(self.Importation_diffuseurs())
        self.bouton_diffuseurs = wx.Button(self, -1, "...", size=(20, 20))
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler et fermer")))
        
        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_BUTTON, self.OnAjouterPeriode, self.bouton_ajouter_periode)
        self.Bind(wx.EVT_BUTTON, self.OnModifierPeriode, self.bouton_modifier_periode)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimerPeriode, self.bouton_supprimer_periode)
        self.Bind(wx.EVT_BUTTON, self.OnGestionFonctions, self.bouton_fonctions)
        self.Bind(wx.EVT_BUTTON, self.OnGestionAffectations, self.bouton_affectations)
        self.Bind(wx.EVT_BUTTON, self.OnGestionDiffuseurs, self.bouton_diffuseurs)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
        # Importation des données
        if self.IDemploi != None :
            self.Importation()
        
        
    def __set_properties(self):
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de lancement de l'offre d'emploi")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Sélectionnez la date de clôture du recrutement pour cette offre d'emploi")))
        self.ctrl_intitule.SetToolTip(wx.ToolTip(_(u"Saisissez l'intitulé (nom) de l'offre. Ex : Animateur Mercredis et vacances Saison 2009-10")))
        self.ctrl_detail.SetToolTip(wx.ToolTip(_(u"Saisissez le texte détaillé de l'offre d'emploi")))
        self.ctrl_reference.SetToolTip(wx.ToolTip(_(u"Saisissez le numéro de l'annonce déposé à l'ANPE. Ex : X455676E")))
        self.ctrl_periodes.SetToolTip(wx.ToolTip(_(u"Sélectionnez un ou plusieurs périodes de disponibilités")))
        self.ctrl_periodes_remarques.SetToolTip(wx.ToolTip(_(u"Saisissez un complement d'information sur les disponibilités")))
        self.ctrl_fonction.SetToolTip(wx.ToolTip(_(u"Cochez la ou les fonctions du poste")))
        self.ctrl_affectations.SetToolTip(wx.ToolTip(_(u"Cochez la ou les affectations pour le poste")))
        self.ctrl_poste_remarques.SetToolTip(wx.ToolTip(_(u"Saisissez un complément d'information sur le poste")))
        self.bouton_ajouter_periode.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une période")))
        self.bouton_modifier_periode.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la période sélectionnée")))
        self.bouton_supprimer_periode.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la période sélectionnée")))
        self.bouton_fonctions.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter, modifier ou supprimer des fonctions")))
        self.bouton_affectations.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter, modifier ou supprimer des affectations")))
        self.bouton_diffuseurs.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter, modifier ou supprimer des diffuseurs")))
        self.ctrl_diffuseurs.SetToolTip(wx.ToolTip(_(u"Cochez ici les organismes ou moyens de communication utilisés pour diffuser cette offre d'emploi. Ex : ANPE, Presse, fédération, etc...")))
        

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_droite = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        sizer_diffusion = wx.StaticBoxSizer(self.sizer_diffusion_staticbox, wx.VERTICAL)
        grid_sizer_diffusion = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=10)
        sizer_poste = wx.StaticBoxSizer(self.sizer_poste_staticbox, wx.VERTICAL)
        grid_sizer_poste = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_affectation = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_fonction = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_gauche = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        sizer_disponibilites = wx.StaticBoxSizer(self.sizer_disponibilites_staticbox, wx.VERTICAL)
        grid_sizer_disponibilites = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_periodes = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_periodes = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        sizer_generalites = wx.StaticBoxSizer(self.sizer_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=10)
        grid_sizer_type = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        grid_sizer_base.Add(self.label_introduction, 0, wx.ALL, 10)
        
        grid_sizer_generalites.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_dates.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_dates.Add((5, 5), 0, wx.EXPAND, 0)
        grid_sizer_dates.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_dates.AddGrowableCol(1)
        grid_sizer_generalites.Add(grid_sizer_dates, 0, wx.EXPAND, 0)
        
        grid_sizer_generalites.Add(self.label_intitule, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_intitule, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_detail, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_generalites.Add(self.ctrl_detail, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_reference, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_reference, 0, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        sizer_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_gauche.Add(sizer_generalites, 1, wx.EXPAND, 0)
        
        grid_sizer_disponibilites.Add(self.label_periodes, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_periodes.Add(self.ctrl_periodes, 0, wx.EXPAND, 0)
        grid_sizer_boutons_periodes.Add(self.bouton_ajouter_periode, 0, 0, 0)
        grid_sizer_boutons_periodes.Add(self.bouton_modifier_periode, 0, 0, 0)
        grid_sizer_boutons_periodes.Add(self.bouton_supprimer_periode, 0, 0, 0)
        grid_sizer_periodes.Add(grid_sizer_boutons_periodes, 1, wx.EXPAND, 0)
        grid_sizer_periodes.AddGrowableRow(0)
        grid_sizer_periodes.AddGrowableCol(0)
        grid_sizer_disponibilites.Add(grid_sizer_periodes, 1, wx.EXPAND, 0)
        grid_sizer_disponibilites.Add(self.label_periodes_remarques, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_disponibilites.Add(self.ctrl_periodes_remarques, 0, wx.EXPAND, 0)
        grid_sizer_disponibilites.AddGrowableRow(0)
        grid_sizer_disponibilites.AddGrowableCol(1)
        sizer_disponibilites.Add(grid_sizer_disponibilites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(sizer_disponibilites, 1, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(1)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        grid_sizer_poste.Add(self.label_fonction, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_fonction.Add(self.ctrl_fonction, 0, wx.EXPAND, 0)
        grid_sizer_fonction.Add(self.bouton_fonctions, 0, 0, 0)
        grid_sizer_fonction.AddGrowableRow(0)
        grid_sizer_fonction.AddGrowableCol(0)
        grid_sizer_poste.Add(grid_sizer_fonction, 1, wx.EXPAND, 0)
        grid_sizer_poste.Add(self.label_affectation, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_affectation.Add(self.ctrl_affectations, 0, wx.EXPAND, 0)
        grid_sizer_affectation.Add(self.bouton_affectations, 0, 0, 0)
        grid_sizer_affectation.AddGrowableRow(0)
        grid_sizer_affectation.AddGrowableCol(0)
        grid_sizer_poste.Add(grid_sizer_affectation, 1, wx.EXPAND, 0)
        grid_sizer_poste.Add(self.label_poste_remarques, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_poste.Add(self.ctrl_poste_remarques, 0, wx.EXPAND, 0)
        grid_sizer_poste.AddGrowableRow(0)
        grid_sizer_poste.AddGrowableRow(1)
        grid_sizer_poste.AddGrowableCol(1)
        sizer_poste.Add(grid_sizer_poste, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_droite.Add(sizer_poste, 1, wx.EXPAND, 0)
        
        grid_sizer_diffuseurs = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_diffusion.Add(self.label_diffuseurs, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_diffuseurs.Add(self.ctrl_diffuseurs, 0, wx.EXPAND, 0)
        grid_sizer_diffuseurs.Add(self.bouton_diffuseurs, 0, 0, 0)
        grid_sizer_diffuseurs.AddGrowableRow(0)
        grid_sizer_diffuseurs.AddGrowableCol(0)
        grid_sizer_diffusion.Add(grid_sizer_diffuseurs, 1, wx.ALL|wx.EXPAND, 0)
        grid_sizer_diffusion.AddGrowableRow(0)
        grid_sizer_diffusion.AddGrowableCol(1)
        sizer_diffusion.Add(grid_sizer_diffusion, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_droite.Add(sizer_diffusion, 1, wx.EXPAND, 0)
        
        grid_sizer_droite.AddGrowableRow(0)
        grid_sizer_droite.AddGrowableRow(1)
        grid_sizer_droite.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_droite, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        
        # Spacer
        grid_sizer_base.Add((5, 5), 0, wx.EXPAND, 0)
        
        # Commandes
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
                

    def OnContextMenu(self, event):
        pass
        
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

    def Importation_diffuseurs(self):
        # Importation des diffuseurs
        DB = GestionDB.DB()        
        req = """SELECT IDdiffuseur, diffuseur
        FROM diffuseurs ORDER BY diffuseur; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        return listeDonnees
                                        
    def Importation_fonctions(self):
        # Importation des fonctions disponibles
        DB = GestionDB.DB()        
        req = """SELECT IDfonction, fonction
        FROM fonctions ORDER BY fonction; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        return listeDonnees

    def Importation_affectations(self):
        # Importation des affectations disponibles
        DB = GestionDB.DB()        
        req = """SELECT IDaffectation, affectation
        FROM affectations ORDER BY affectation; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        return listeDonnees
                                        
    def Importation(self):
        # Importation des données de la candidature
        DB = GestionDB.DB()        
        req = """SELECT IDemploi, date_debut, date_fin, intitule, detail, reference_anpe, periodes_remarques, poste_remarques 
        FROM emplois WHERE IDemploi=%d; """ % self.IDemploi
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        IDemploi, date_debut, date_fin, intitule, detail, reference_anpe, periodes_remarques, poste_remarques  = listeDonnees[0]
        
        self.SetDatePicker(self.ctrl_date_debut, datetime.date(year=int(date_debut[:4]), month=int(date_debut[5:7]), day=int(date_debut[8:10])))
        self.SetDatePicker(self.ctrl_date_fin, datetime.date(year=int(date_fin[:4]), month=int(date_fin[5:7]), day=int(date_fin[8:10])))
        self.ctrl_intitule.SetValue(intitule)
        self.ctrl_detail.SetValue(detail)
        self.ctrl_reference.SetValue(reference_anpe)
        self.ctrl_periodes_remarques.SetValue(periodes_remarques)
        self.ctrl_poste_remarques.SetValue(poste_remarques)
        
        # Importation des disponibilités
        DB = GestionDB.DB()        
        req = """SELECT IDdisponibilite, date_debut, date_fin
        FROM emplois_dispo WHERE IDemploi=%d ORDER BY date_debut; """ % self.IDemploi
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.listeDisponibilites = []
        for IDdisponibilite, date_debut, date_fin in listeDonnees :
            date_debut = datetime.date(year=int(date_debut[:4]), month=int(date_debut[5:7]), day=int(date_debut[8:10]))
            date_fin = datetime.date(year=int(date_fin[:4]), month=int(date_fin[5:7]), day=int(date_fin[8:10]))
            self.listeDisponibilites.append((IDdisponibilite, date_debut, date_fin))
        self.ctrl_periodes.Remplissage(self.listeDisponibilites)
        
        # Importation des fonctions
        DB = GestionDB.DB()        
        req = """SELECT IDemploi_fonction, IDfonction
        FROM emplois_fonctions WHERE IDemploi=%d; """ % self.IDemploi
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeFonctions = []
        for IDemploi_fonction, IDfonction in listeDonnees :
            listeFonctions.append(IDfonction)
        self.ctrl_fonction.CocheListe(listeFonctions)
        
        # Importation des affectations
        DB = GestionDB.DB()        
        req = """SELECT IDemploi_affectation, IDaffectation
        FROM emplois_affectations WHERE IDemploi=%d; """ % self.IDemploi
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeAffectations = []
        for IDemploi_affectation, IDaffectation in listeDonnees :
            listeAffectations.append(IDaffectation)
        self.ctrl_affectations.CocheListe(listeAffectations)
        
        # Importation des diffuseurs
        DB = GestionDB.DB()        
        req = """SELECT IDemploi_diffuseur, IDdiffuseur
        FROM emplois_diffuseurs WHERE IDemploi=%d; """ % self.IDemploi
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeDiffuseurs = []
        for IDemploi_diffuseur, IDdiffuseur in listeDonnees :
            listeDiffuseurs.append(IDdiffuseur)
        self.ctrl_diffuseurs.CocheListe(listeDiffuseurs)
    
    def MAJ_fonctions(self) :
        # Récupère liste des fonctions disponibles
        self.ctrl_fonction.Remplissage(self.Importation_fonctions())
        self.ctrl_fonction.CocheListe()
        
    def MAJ_affectations(self):
        # Récupère liste des fonctions disponibles
        self.ctrl_affectations.Remplissage(self.Importation_affectations())
        self.ctrl_affectations.CocheListe()

    def MAJ_diffuseurs(self):
        # Récupère liste des fonctions disponibles
        self.ctrl_diffuseurs.Remplissage(self.Importation_diffuseurs())
        self.ctrl_diffuseurs.CocheListe()
        
    def OnAjouterPeriode(self, event):
        # Ajout d'une période de disponibilités
        dlg = DLG_Selection_periode.SelectionPeriode(self)
        if dlg.ShowModal() == wx.ID_OK:
            date_debut, date_fin = dlg.GetDates()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        # Modification de la liste
        self.listeDisponibilites.append((None, date_debut, date_fin))
        self.ctrl_periodes.Remplissage(self.listeDisponibilites)
        
    def OnModifierPeriode(self, event):
        # Modification d'une période de disponibilité
        index = self.ctrl_periodes.GetSelection()
        if index == -1 : 
            dlg = wx.MessageDialog(self, _(u"Vous devez déjà sélectionner une période dans la liste"), _(u"Erreur"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDdisponibilite, date_debut, date_fin = self.listeDisponibilites[index]
        dlg = DLG_Selection_periode.SelectionPeriode(self)
        dlg.SetDates(date_debut=date_debut, date_fin=date_fin)
        if dlg.ShowModal() == wx.ID_OK:
            date_debut, date_fin = dlg.GetDates()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        # Modification de la liste
        self.listeDisponibilites[index] = (IDdisponibilite, date_debut, date_fin)
        self.ctrl_periodes.Remplissage(self.listeDisponibilites)
        
    def OnSupprimerPeriode(self, event):
        # Suppression d'une période de disponibilité
        index = self.ctrl_periodes.GetSelection()
        if index == -1 : 
            dlg = wx.MessageDialog(self, _(u"Vous devez déjà sélectionner une période dans la liste"), _(u"Erreur"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDdisponibilite, date_debut, date_fin = self.listeDisponibilites[index]
        
        # Demande de confirmation
        formatDate = "%d/%m/%Y"
        texteDates = _(u"Du %s au %s") % (date_debut.strftime(formatDate), date_fin.strftime(formatDate))
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer cette période de disponibilité ? \n\n> %s") % texteDates))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Modification de la liste
        self.listeDisponibilites.pop(index)
        self.ctrl_periodes.Remplissage(self.listeDisponibilites)
    
    def OnGestionFonctions(self, event):
        frm = DLG_Config_fonctions.MyFrame(self, "")
        frm.Show()
    
    def OnGestionAffectations(self, event):
        frm = DLG_Config_affectations.MyFrame(self, "")
        frm.Show()

    def OnGestionDiffuseurs(self, event):
        frm = DLG_Config_diffuseurs.MyFrame(self, "")
        frm.Show()
    
    def OnClose(self, event):
        self.GetParent().Fermer()
        
    def Onbouton_aide(self, event):
##        FonctionsPerso.Aide(38)
        dlg = wx.MessageDialog(self, _(u"L'aide du module Recrutement est en cours de rédaction.\nElle sera disponible lors d'une mise à jour ultérieure."), "Aide indisponible", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
            
    def Onbouton_annuler(self, event):
##        # Si frame Creation_contrats ouverte, on met à jour le listCtrl Classification
##        self.MAJparents()
        # Fermeture
        self.GetParent().Fermer()
        
    def Onbouton_ok(self, event):
        """ Validation des données saisies """
        
        # Type du dépôt
        valeur = self.ctrl_intitule.GetValue()
        if valeur == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement un intitulé pour cette offre d'emploi."), "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_intitule.SetFocus()
            return

        # Disponibilités
        if len(self.listeDisponibilites) == 0 :
            dlgConfirm = wx.MessageDialog(self, _(u"Vous n'avez saisi aucune période de disponibilité. Confirmez-vous ce choix ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            reponse = dlgConfirm.ShowModal()
            dlgConfirm.Destroy()
            if reponse == wx.ID_NO:
                return
        
        # Fonctions
        if len(self.ctrl_fonction.listeIDcoches) == 0 :
            dlgConfirm = wx.MessageDialog(self, _(u"Vous n'avez saisi aucune demande de fonction. Confirmez-vous ce choix ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            reponse = dlgConfirm.ShowModal()
            dlgConfirm.Destroy()
            if reponse == wx.ID_NO:
                return
        
        # Affectations
        if len(self.ctrl_affectations.listeIDcoches) == 0 :
            dlgConfirm = wx.MessageDialog(self, _(u"Vous n'avez saisi aucune demande d'affectation. Confirmez-vous ce choix ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            reponse = dlgConfirm.ShowModal()
            dlgConfirm.Destroy()
            if reponse == wx.ID_NO:
                return
                
        # Sauvegarde des données
        self.Sauvegarde()
        
        # Fermeture
        self.GetParent().Fermer()
    
    def Sauvegarde(self):
        # Sauvegarde des données
                                    
        # Généralités
        date_debut = str(self.GetDatePickerValue(self.ctrl_date_debut))
        date_fin = str(self.GetDatePickerValue(self.ctrl_date_fin))
        intitule = self.ctrl_intitule.GetValue()
        detail = self.ctrl_detail.GetValue()
        reference_anpe = self.ctrl_reference.GetValue()
        
        # Disponibilités
        listeDisponibilites = self.listeDisponibilites
        remarques_periodes = self.ctrl_periodes_remarques.GetValue()
        
        # Poste
        listeFonctions = self.ctrl_fonction.listeIDcoches
        listeAffectations = self.ctrl_affectations.listeIDcoches
        remarques_poste = self.ctrl_poste_remarques.GetValue()
        
        # Diffuseurs
        listeDiffuseurs = self.ctrl_diffuseurs.listeIDcoches
                
        DB = GestionDB.DB()
        
        # Sauvegarde de la candidature
        listeDonnees = [    ("IDemploi",   self.IDemploi),  
                                    ("date_debut",   date_debut),  
                                    ("date_fin",    date_fin),
                                    ("intitule",    intitule),
                                    ("detail",    detail),
                                    ("reference_anpe",    reference_anpe), 
                                    ("periodes_remarques",    remarques_periodes),
                                    ("poste_remarques",    remarques_poste), 
                                    ]
        if self.IDemploi == None :
            newID = DB.ReqInsert("emplois", listeDonnees)
            self.IDemploi = newID
            nouvelEmploi = True
        else:
            DB.ReqMAJ("emplois", listeDonnees, "IDemploi", self.IDemploi)
            nouvelEmploi = False
        DB.Commit()
        
        # Sauvegarde des disponibilités
        listeID = []
        for IDdisponibilite, date_debut, date_fin in listeDisponibilites :
            listeDonnees = [    ("IDemploi",   self.IDemploi),  
                                    ("date_debut",   date_debut),  
                                    ("date_fin",    date_fin),
                                    ]
            if IDdisponibilite == None :
                newID = DB.ReqInsert("emplois_dispo", listeDonnees)
                IDdisponibilite = newID
            else:
                DB.ReqMAJ("emplois_dispo", listeDonnees, "IDdisponibilite", IDdisponibilite)
            DB.Commit()
            listeID.append(IDdisponibilite)
            
        # Effacement des disponibilités supprimées
        if nouvelEmploi == False :
            req = """SELECT IDdisponibilite, date_debut, date_fin
            FROM emplois_dispo WHERE IDemploi=%d; """ % self.IDemploi
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            for IDdisponibilite, date_debut, date_fin in listeDonnees :
                if IDdisponibilite not in listeID :
                    DB.ReqDEL("emplois_dispo", "IDdisponibilite", IDdisponibilite)
        
        # Sauvegarde des fonctions
        listeIDexistantes = []
        listeIDemploi_fonction = []
        req = """SELECT IDemploi_fonction, IDfonction
        FROM emplois_fonctions WHERE IDemploi=%d; """ % self.IDemploi
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDemploi_fonction, IDfonction in listeDonnees :
            listeIDexistantes.append(IDfonction)
            listeIDemploi_fonction.append((IDemploi_fonction, IDfonction))
        
        for IDfonction in listeFonctions :
            if IDfonction not in listeIDexistantes :
                # Si n'existe pas :
                listeDonnees = [    ("IDemploi",   self.IDemploi),  
                                        ("IDfonction",   IDfonction),  
                                        ]
                newID = DB.ReqInsert("emplois_fonctions", listeDonnees)
                DB.Commit()
            
        # Effacement des fonctions supprimées
        if nouvelEmploi == False :
            for IDemploi_fonction, IDfonction in listeIDemploi_fonction :
                if IDfonction not in listeFonctions :
                    DB.ReqDEL("emplois_fonctions", "IDemploi_fonction", IDemploi_fonction)
            
        # Sauvegarde des affectations
        listeIDexistantes = []
        listeIDemploi_affectation = []
        req = """SELECT IDemploi_affectation, IDaffectation
        FROM emplois_affectations WHERE IDemploi=%d; """ % self.IDemploi
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDemploi_affectation, IDaffectation in listeDonnees :
            listeIDexistantes.append(IDaffectation)
            listeIDemploi_affectation.append((IDemploi_affectation, IDaffectation))
        
        for IDaffectation in listeAffectations :
            if IDaffectation not in listeIDexistantes :
                # Si n'existe pas :
                listeDonnees = [    ("IDemploi",   self.IDemploi),  
                                        ("IDaffectation",   IDaffectation),  
                                        ]
                newID = DB.ReqInsert("emplois_affectations", listeDonnees)
                DB.Commit()
            
        # Effacement des affectations supprimées
        if nouvelEmploi == False :
            for IDemploi_affectation, IDaffectation in listeIDemploi_affectation :
                if IDaffectation not in listeAffectations :
                    DB.ReqDEL("emplois_affectations", "IDemploi_affectation", IDemploi_affectation)
        
        # Sauvegarde des diffuseurs
        listeIDexistantes = []
        listeIDemploi_diffuseur = []
        req = """SELECT IDemploi_diffuseur, IDdiffuseur
        FROM emplois_diffuseurs WHERE IDemploi=%d; """ % self.IDemploi
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDemploi_diffuseur, IDdiffuseur in listeDonnees :
            listeIDexistantes.append(IDdiffuseur)
            listeIDemploi_diffuseur.append((IDemploi_diffuseur, IDdiffuseur))
        
        for IDdiffuseur in listeDiffuseurs :
            if IDdiffuseur not in listeIDexistantes :
                # Si n'existe pas :
                listeDonnees = [    ("IDemploi",   self.IDemploi),  
                                        ("IDdiffuseur",   IDdiffuseur),  
                                        ]
                newID = DB.ReqInsert("emplois_diffuseurs", listeDonnees)
                DB.Commit()
            
        # Effacement des diffuseur supprimés
        if nouvelEmploi == False :
            for IDemploi_diffuseur, IDdiffuseur in listeIDemploi_diffuseur :
                if IDdiffuseur not in listeDiffuseurs :
                    DB.ReqDEL("emplois_diffuseurs", "IDemploi_diffuseur", IDemploi_diffuseur)
        
        # Fin de la sauvegarde
        DB.Close()
        
        
        
        
        


class BitmapComboBox(BitmapComboBox):
    def __init__(self, parent, listeImages=[], size=(-1,  -1) ):
        BitmapComboBox.__init__(self, parent, size=size, style=wx.CB_READONLY)
        # Remplissage des items avec les images
        for texte, nomImage in listeImages :
            img = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % nomImage), wx.BITMAP_TYPE_ANY)
            self.Append(texte, img, texte)


class ListBoxDisponibilites(wx.ListBox):
    def __init__(self, parent):
        wx.ListBox.__init__(self, parent, choices=[])
        self.dictIndexes = {}
        
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)
        
    def Remplissage(self, listeDisponibilites=[]) :
        # Remplissage
        self.dictIndexes = {}
        self.Clear()
        index = 0
        for IDdisponibilite, date_debut, date_fin in listeDisponibilites :
            formatDate = "%d/%m/%Y"
            texte = _(u"Du %s au %s") % (date_debut.strftime(formatDate), date_fin.strftime(formatDate))
            self.Append(texte)
            self.dictIndexes[index] = IDdisponibilite
            index += 1
    
    def GetIDselection(self):
        print(self.GetSelection())
    
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        index = self.HitTest(event.GetPosition())
        if index != -1 :
            self.SetSelection(index)
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        if index != -1 :
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
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Menu_Ajouter(self, event):
        self.GetParent().OnAjouterPeriode(None)
        
    def Menu_Modifier(self, event):
        self.GetParent().OnModifierPeriode(None)

    def Menu_Supprimer(self, event):
        self.GetParent().OnSupprimerPeriode(None)

    
class CheckListBox(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, choices=[])
        self.listeDonnees = []
        self.listeIDcoches = []
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck, self)

    def Remplissage(self, liste=None) :
        if liste != None :
            self.listeDonnees = liste
        # Remplissage
        self.dictIndexes = {}
        self.Clear()
        index = 0
        for ID, texte in self.listeDonnees :
            self.Append(texte)
            self.dictIndexes[index] = ID
            index += 1

    def CocheListe(self, liste=None):
        if liste != None :
            self.listeIDcoches = liste
        # Coche les ID donnés
        for index in range(0, self.GetCount()) :
            if self.dictIndexes[index] in self.listeIDcoches :
                self.Check(index, True)
            else:
                self.Check(index, False)
    
    def GetIDcoches(self):
        # Récupère la liste des ID cochés :
        listeIDcoches = []
        for index in range(0, self.GetCount()) :
            if self.IsChecked(index) == True :
                listeIDcoches.append(self.dictIndexes[index])
        return listeIDcoches

    def OnCheck(self, event):
        self.listeIDcoches = self.GetIDcoches()


class MyFrame(wx.Frame):
    def __init__(self, parent, IDemploi=None):
        wx.Frame.__init__(self, parent, -1, title="", style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.panel = Panel(self, IDemploi=IDemploi)
                
        # Propriétés
        if IDemploi == None :
            self.SetTitle(_(u"Saisie d'une offre d'emploi"))
        else:
            self.SetTitle(_(u"Modification d'une offre d'emploi"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        
        # Layout
        self.SetMinSize((770, 550))
        self.SetSize((770, 550))
        self.CentreOnScreen()
    
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    
    def OnClose(self, event):
        self.Fermer() 
    
    def Fermer(self):
        self.MAJparents() 
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()
    
    def MAJparents(self):
        if self.GetParent().GetName() == "config_emploi" :
            self.GetParent().MAJpanel()
        if self.GetParent().GetName() == "OL_emplois" :
            self.GetParent().MAJ()

        
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, IDemploi=1)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()