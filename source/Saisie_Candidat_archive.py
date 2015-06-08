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


class Panel(wx.Panel):
    def __init__(self, parent, IDcandidat=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_candidat", style=wx.TAB_TRAVERSAL)
        self.IDcandidat = IDcandidat
        
        # Acte
        self.sizer_acte_staticbox = wx.StaticBox(self, -1, u"1. Dépôt de candidature")
        self.label_introduction = wx.StaticText(self, -1, u"Vous pouvez ici saisir les informations concernant le dépôt de candidature.")
        self.label_date = wx.StaticText(self, -1, u"Date :")
        self.ctrl_date = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN)
        self.label_type = wx.StaticText(self, -1, u"Type :")
        listeImages = [ (u"Courrier", "Mail.png"), (u"Téléphone", "Mobile.png") ]
        self.ctrl_type = BitmapComboBox(self, listeImages)
        self.label_acte_remarques = wx.StaticText(self, -1, u"Remarques :")
        largeurTmp = self.label_acte_remarques.GetSize()[0]
        self.ctrl_acte_remarques = wx.TextCtrl(self, -1, u"")
        
        # Offre d'emploi
        self.sizer_emploi_staticbox = wx.StaticBox(self, -1, u"2. Offre d'emploi")
        self.label_emploi = wx.StaticText(self, -1, u"         Offre :")
        self.ctrl_emploi= ChoiceEmploi(self)
        self.ctrl_emploi.Remplissage(self.Importation_emplois())
        
        # Disponibilités
        self.sizer_disponibilites_staticbox = wx.StaticBox(self, -1, u"3. Disponibilités")
        self.label_periodes = wx.StaticText(self, -1, u"Périodes :")
        self.ctrl_periodes = ListBoxDisponibilites(self)
        self.ctrl_periodes.SetMinSize((200, -1))
        self.bouton_ajouter_periode = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_periode = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_periode = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.label_periodes_remarques = wx.StaticText(self, -1, u"Remarques :")
        self.ctrl_periodes_remarques = wx.TextCtrl(self, -1, u"")
        
        # Poste
        self.sizer_poste_staticbox = wx.StaticBox(self, -1, u"4. Poste souhaité")
        self.label_fonction = wx.StaticText(self, -1, u"Fonction :")
        self.ctrl_fonction = CheckListBox(self)
        self.ctrl_fonction.Remplissage(self.Importation_fonctions())
        self.bouton_fonctions = wx.Button(self, -1, "...", size=(20, 20))
        self.label_affectation = wx.StaticText(self, -1, u"Affectation :")
        self.ctrl_affectations = CheckListBox(self)
        self.ctrl_affectations.Remplissage(self.Importation_affectations())
        self.bouton_affectations = wx.Button(self, -1, "...", size=(20, 20))
        self.label_poste_remarques = wx.StaticText(self, -1, u"Remarques :")
        self.ctrl_poste_remarques = wx.TextCtrl(self, -1, "")
        
        # Réponse
        self.sizer_reponse_staticbox = wx.StaticBox(self, -1, u"5. Réponse")
        self.label_decision = wx.StaticText(self, -1, u"Décision :")
        listeImages = [ (u"Oui", "Ok_2.png"), (u"Non", "Supprimer_2.png") ]
        self.ctrl_decision = BitmapComboBox(self, listeImages=listeImages)
        self.label_reponse_remarques = wx.StaticText(self, -1, u"Remarques :")
        self.ctrl_reponse_remarques = wx.TextCtrl(self, -1, "")
        self.label_reponse = wx.StaticText(self, -1, u"Réponse :")
        self.ctrl_reponse_obligatoire = wx.CheckBox(self, -1, u"Réponse obligatoire")
        self.ctrl_reponse_communiquee = wx.CheckBox(self, -1, u"Réponse communiquée au candidat")
        self.label_reponse1 = wx.StaticText(self, -1, u"le")
        self.date_envoi_reponse = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN)
        self.label_reponse2 = wx.StaticText(self, -1, u"par")
        listeImages = [ (u"Courrier", "Mail.png"), (u"Téléphone", "Mobile.png") ]
        self.ctrl_type_reponse = BitmapComboBox(self, listeImages, size=(140, -1))
        
        self.label_reponse1.Enable(False)
        self.date_envoi_reponse.Enable(False)
        self.label_reponse2.Enable(False)
        self.ctrl_type_reponse.Enable(False)

        # Commandes
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez pour annuler et fermer")
        
        self.__set_properties()
        self.__do_layout()
        
##        # Binds
##        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
##        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
##        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)
##        self.Bind(wx.EVT_CLOSE, self.OnClose)
##        self.Bind(wx.EVT_BUTTON, self.OnAjouterPeriode, self.bouton_ajouter_periode)
##        self.Bind(wx.EVT_BUTTON, self.OnModifierPeriode, self.bouton_modifier_periode)
##        self.Bind(wx.EVT_BUTTON, self.OnSupprimerPeriode, self.bouton_supprimer_periode)
##        self.Bind(wx.EVT_BUTTON, self.OnGestionFonctions, self.bouton_fonctions)
##        self.Bind(wx.EVT_BUTTON, self.OnGestionAffectations, self.bouton_affectations)
##        self.Bind(wx.EVT_CHECKBOX, self.OnCheckReponse, self.ctrl_reponse_obligatoire)
##        self.Bind(wx.EVT_CHECKBOX, self.OnCheckReponseCommuniquee, self.ctrl_reponse_communiquee)
##        
##        # Importation des données
##        if self.IDcandidature != None :
##            self.Importation()
        
    def __set_properties(self):
        pass
##        self.ctrl_date.SetToolTipString(u"Saisissez la date de l'acte de candidature")
##        self.ctrl_type.SetToolTipString(u"Sélectionnez un type d'acte dans la liste proposée")
##        self.ctrl_acte_remarques.SetToolTipString(u"Saisissez des remarques sur l'acte de candidature")
##        self.ctrl_emploi.SetToolTipString(u"Sélectionnez une offre d'emploi dans la liste proposée")
##        self.ctrl_periodes.SetToolTipString(u"Sélectionnez un ou plusieurs périodes de disponibilités")
##        self.ctrl_periodes_remarques.SetToolTipString(u"Saisissez un complement d'information sur les disponibilités")
##        self.ctrl_fonction.SetToolTipString(u"Cochez la ou les fonctions recherchées par le candidat")
##        self.ctrl_affectations.SetToolTipString(u"Cochez la ou les affectations recherchées par le candidat")
##        self.ctrl_poste_remarques.SetToolTipString(u"Saisissez un complément d'information sur le poste souhaité")
##        self.ctrl_decision.SetToolTipString(u"Selectionnez votre decision concernant cet acte de candidature dans la liste proposee")
##        self.ctrl_reponse_remarques.SetToolTipString(u"Vous pouvez saisir un complément d'information à propos de la décision")
##        self.ctrl_reponse_obligatoire.SetToolTipString(u"Cochez cette case si une réponse doit être communiqué au candidat")
##        self.ctrl_reponse_communiquee.SetToolTipString(u"Cochez cette case si vous avez communiqué votre réponse au candidat")
##        self.date_envoi_reponse.SetToolTipString(u"Saisissez la date à laquelle vous avez informé le candidat de la réponse")
##        self.ctrl_type_reponse.SetToolTipString(u"Sélectionnez le type de communication utilisé")
##        self.bouton_ajouter_periode.SetToolTipString(u"Cliquez ici pour ajouter une période")
##        self.bouton_modifier_periode.SetToolTipString(u"Cliquez ici pour modifier la période sélectionnée")
##        self.bouton_supprimer_periode.SetToolTipString(u"Cliquez ici pour supprimer la période sélectionnée")
##        self.bouton_fonctions.SetToolTipString(u"Cliquez ici pour ajouter, modifier ou supprimer des fonctions")
##        self.bouton_affectations.SetToolTipString(u"Cliquez ici pour ajouter, modifier ou supprimer des affectations")
        

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_droite = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        sizer_reponse = wx.StaticBoxSizer(self.sizer_reponse_staticbox, wx.VERTICAL)
        grid_sizer_reponse = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=10)
        grid_sizer_reponse2 = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_type_reponse = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        sizer_poste = wx.StaticBoxSizer(self.sizer_poste_staticbox, wx.VERTICAL)
        grid_sizer_poste = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_affectation = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_fonction = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_gauche = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        sizer_disponibilites = wx.StaticBoxSizer(self.sizer_disponibilites_staticbox, wx.VERTICAL)
        grid_sizer_disponibilites = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_periodes = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_periodes = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        sizer_acte = wx.StaticBoxSizer(self.sizer_acte_staticbox, wx.VERTICAL)
        grid_sizer_acte = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=10)
        grid_sizer_type = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        sizer_emploi = wx.StaticBoxSizer(self.sizer_emploi_staticbox, wx.VERTICAL)
        grid_sizer_emploi = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        grid_sizer_base.Add(self.label_introduction, 0, wx.ALL, 10)
        
        grid_sizer_acte.Add(self.label_date, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_acte.Add(self.ctrl_date, 0, 0, 0)
        grid_sizer_acte.Add(self.label_type, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_type.Add(self.ctrl_type, 0, wx.EXPAND, 0)
        grid_sizer_type.AddGrowableCol(0)
        grid_sizer_acte.Add(grid_sizer_type, 1, wx.EXPAND, 0)
        
        grid_sizer_acte.Add(self.label_acte_remarques, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_acte.Add(self.ctrl_acte_remarques, 0, wx.EXPAND, 0)
        grid_sizer_acte.AddGrowableCol(1)
        sizer_acte.Add(grid_sizer_acte, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_gauche.Add(sizer_acte, 1, wx.EXPAND, 0)
        
        grid_sizer_emploi.Add(self.label_emploi, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_emploi.Add(self.ctrl_emploi, 0, wx.EXPAND, 0)
        grid_sizer_emploi.AddGrowableCol(1)
        sizer_emploi.Add(grid_sizer_emploi, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(sizer_emploi, 1, wx.EXPAND, 0)
        
        
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
        grid_sizer_gauche.AddGrowableRow(2)
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
        grid_sizer_reponse.Add(self.label_decision, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_reponse.Add(self.ctrl_decision, 0, wx.EXPAND, 0)
        grid_sizer_reponse.Add(self.label_reponse_remarques, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_reponse.Add(self.ctrl_reponse_remarques, 0, wx.EXPAND|wx.BOTTOM, 5)
        grid_sizer_reponse.Add(self.label_reponse, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_reponse2.Add(self.ctrl_reponse_obligatoire, 0, 0, 0)
        grid_sizer_reponse2.Add(self.ctrl_reponse_communiquee, 0, 0, 0)
        grid_sizer_type_reponse.Add((20, 20), 0, 0, 0)
        grid_sizer_type_reponse.Add(self.label_reponse1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_type_reponse.Add(self.date_envoi_reponse, 0, 0, 0)
        grid_sizer_type_reponse.Add(self.label_reponse2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_type_reponse.Add(self.ctrl_type_reponse, 0, 0, 0)
        grid_sizer_reponse2.Add(grid_sizer_type_reponse, 1, wx.EXPAND, 0)
        grid_sizer_reponse.Add(grid_sizer_reponse2, 1, wx.EXPAND, 0)
        grid_sizer_reponse.AddGrowableCol(1)
        sizer_reponse.Add(grid_sizer_reponse, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_droite.Add(sizer_reponse, 1, wx.EXPAND, 0)
        grid_sizer_droite.AddGrowableRow(0)
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
        

    def OnCheckReponse(self, event):
        if self.ctrl_reponse_obligatoire.GetValue() == True :
            etat = True
        else:
            etat = False
        self.ctrl_reponse_communiquee.Enable(etat)

    def OnCheckReponseCommuniquee(self, event):
        if self.ctrl_reponse_communiquee.GetValue() == True :
            etat = True
            self.ctrl_reponse_obligatoire.Enable(False)
        else:
            etat = False
            self.ctrl_reponse_obligatoire.Enable(True)
        self.label_reponse1.Enable(etat)
        self.date_envoi_reponse.Enable(etat)
        self.label_reponse2.Enable(etat)
        self.ctrl_type_reponse.Enable(etat)
        
        
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

    def Importation_emplois(self):
        # Importation des offres d'emploi
        DB = GestionDB.DB()        
        req = """SELECT IDemploi, intitule, date_debut, date_fin
        FROM emplois ORDER BY date_debut; """
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
        req = """SELECT date_depot, IDtype, acte_remarques, IDemploi, periodes_remarques, poste_remarques, 
        IDdecision, decision_remarques, reponse_obligatoire, reponse, date_reponse, IDtype_reponse 
        FROM candidatures WHERE IDcandidature=%d; """ % self.IDcandidature
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        date_depot, IDtype, acte_remarques, IDemploi, periodes_remarques, poste_remarques, IDdecision, decision_remarques, reponse_obligatoire, reponse, date_reponse, IDtype_reponse = listeDonnees[0]
        
        self.SetDatePicker(self.ctrl_date, datetime.date(year=int(date_depot[:4]), month=int(date_depot[5:7]), day=int(date_depot[8:10])))
        self.ctrl_type.SetSelection(IDtype)
        self.ctrl_acte_remarques.SetValue(acte_remarques)
        self.ctrl_emploi.SetSelection(IDemploi)
        self.ctrl_periodes_remarques.SetValue(periodes_remarques)
        self.ctrl_poste_remarques.SetValue(poste_remarques)
        self.ctrl_decision.SetSelection(IDdecision)
        self.ctrl_reponse_remarques.SetValue(decision_remarques)
        self.ctrl_reponse_obligatoire.SetValue(reponse_obligatoire)
        self.ctrl_reponse_communiquee.SetValue(reponse)
        self.SetDatePicker(self.date_envoi_reponse, datetime.date(year=int(date_reponse[:4]), month=int(date_reponse[5:7]), day=int(date_reponse[8:10])))
        self.ctrl_type_reponse.SetSelection(IDtype_reponse)
        
        self.OnCheckReponse(None)
        self.OnCheckReponseCommuniquee(None)
        
        # Importation des disponibilités
        DB = GestionDB.DB()        
        req = """SELECT IDdisponibilite, date_debut, date_fin
        FROM disponibilites WHERE IDcandidature=%d ORDER BY date_debut; """ % self.IDcandidature
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
        req = """SELECT IDcand_fonction, IDfonction
        FROM cand_fonctions WHERE IDcandidature=%d; """ % self.IDcandidature
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeFonctions = []
        for IDcand_fonction, IDfonction in listeDonnees :
            listeFonctions.append(IDfonction)
        self.ctrl_fonction.CocheListe(listeFonctions)
        
        # Importation des affectations
        DB = GestionDB.DB()        
        req = """SELECT IDcand_affectation, IDaffectation
        FROM cand_affectations WHERE IDcandidature=%d; """ % self.IDcandidature
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeAffectations = []
        for IDcand_affectation, IDaffectation in listeDonnees :
            listeAffectations.append(IDaffectation)
        self.ctrl_affectations.CocheListe(listeAffectations)
    
    def MAJ_fonctions(self) :
        # Récupère liste des fonctions disponibles
        self.ctrl_fonction.Remplissage(self.Importation_fonctions())
        self.ctrl_fonction.CocheListe()
        
    def MAJ_affectations(self):
        # Récupère liste des fonctions disponibles
        self.ctrl_affectations.Remplissage(self.Importation_affectations())
        self.ctrl_affectations.CocheListe()
        
    def OnAjouterPeriode(self, event):
        # Ajout d'une période de disponibilités
        dlg = Selection_periode.SelectionPeriode(self)  
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
            dlg = wx.MessageDialog(self, u"Vous devez déjà sélectionner une période dans la liste", u"Erreur", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDdisponibilite, date_debut, date_fin = self.listeDisponibilites[index]
        dlg = Selection_periode.SelectionPeriode(self)  
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
            dlg = wx.MessageDialog(self, u"Vous devez déjà sélectionner une période dans la liste", u"Erreur", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDdisponibilite, date_debut, date_fin = self.listeDisponibilites[index]
        
        # Demande de confirmation
        formatDate = "%d/%m/%Y"
        texteDates = u"Du %s au %s" % (date_debut.strftime(formatDate), date_fin.strftime(formatDate))
        txtMessage = unicode((u"Voulez-vous vraiment supprimer cette période de disponibilité ? \n\n> %s" % texteDates))
        dlgConfirm = wx.MessageDialog(self, txtMessage, u"Confirmation de suppression", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Modification de la liste
        self.listeDisponibilites.pop(index)
        self.ctrl_periodes.Remplissage(self.listeDisponibilites)
    
    def OnGestionFonctions(self, event):
        frm = Config_Fonctions.MyFrame(self, "")
        frm.Show()
    
    def OnGestionAffectations(self, event):
        frm = Config_Affectations.MyFrame(self, "")
        frm.Show()

    
    def OnClose(self, event):
        self.GetParent().Fermer()
        
    def Onbouton_aide(self, event):
        FonctionsPerso.Aide(38)
            
    def Onbouton_annuler(self, event):
##        # Si frame Creation_contrats ouverte, on met à jour le listCtrl Classification
##        self.MAJparents()
        # Fermeture
        self.GetParent().Fermer()
        
    def Onbouton_ok(self, event):
        """ Validation des données saisies """
        
        # Type du dépôt
        valeur = self.ctrl_type.GetSelection()
        if valeur == -1 :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner un type de dépôt de candidature", "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_type.SetFocus()
            return

        # Disponibilités
        if len(self.listeDisponibilites) == 0 :
            dlgConfirm = wx.MessageDialog(self, u"Vous n'avez saisi aucune période de disponibilité. Confirmez-vous ce choix ?", u"Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            reponse = dlgConfirm.ShowModal()
            dlgConfirm.Destroy()
            if reponse == wx.ID_NO:
                return
        
        # Fonctions
        if len(self.ctrl_fonction.listeIDcoches) == 0 :
            dlgConfirm = wx.MessageDialog(self, u"Vous n'avez saisi aucune demande de fonction. Confirmez-vous ce choix ?", u"Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            reponse = dlgConfirm.ShowModal()
            dlgConfirm.Destroy()
            if reponse == wx.ID_NO:
                return
        
        # Affectations
        if len(self.ctrl_affectations.listeIDcoches) == 0 :
            dlgConfirm = wx.MessageDialog(self, u"Vous n'avez saisi aucune demande d'affectation. Confirmez-vous ce choix ?", u"Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            reponse = dlgConfirm.ShowModal()
            dlgConfirm.Destroy()
            if reponse == wx.ID_NO:
                return
        
        # Mode envoi de la réponse
        if self.ctrl_reponse_communiquee.GetValue() == True :
            valeur = self.ctrl_type_reponse.GetSelection()
            if valeur == -1 :
                dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner un mode d'envoi pour la réponse", "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_type_reponse.SetFocus()
                return
        
        # Sauvegarde des données
        self.Sauvegarde()
        
        # Fermeture
        self.GetParent().Fermer()
    
    def Sauvegarde(self):
        # Sauvegarde des données
        
        # Dépôt
        date = str(self.GetDatePickerValue(self.ctrl_date))
        type_depot = self.ctrl_type.GetSelection()
        remarques_depot = self.ctrl_acte_remarques.GetValue()
        
        # Offre d'emploi
        emploi = self.ctrl_emploi.GetIDselection()
        
        # Disponibilités
        listeDisponibilites = self.listeDisponibilites
        remarques_periodes = self.ctrl_periodes_remarques.GetValue()
        
        # Poste
        listeFonctions = self.ctrl_fonction.listeIDcoches
        listeAffectations = self.ctrl_affectations.listeIDcoches
        remarques_poste = self.ctrl_poste_remarques.GetValue()
        
        # Reponse
        decision = self.ctrl_decision.GetSelection()
        remarques_decision = self.ctrl_reponse_remarques.GetValue()
        reponse_obligatoire = int(self.ctrl_reponse_obligatoire.GetValue())
        reponse_communique = int(self.ctrl_reponse_communiquee.GetValue())
        date_reponse = str(self.GetDatePickerValue(self.date_envoi_reponse))
        type_reponse = self.ctrl_type_reponse.GetSelection()
                
        DB = GestionDB.DB()
        
        # Sauvegarde de la candidature
        listeDonnees = [    ("IDcandidat",   self.IDcandidat),  
                                    ("date_depot",   date),  
                                    ("IDtype",    type_depot),
                                    ("acte_remarques",    remarques_depot),
                                    ("IDemploi",    emploi),
                                    ("periodes_remarques",    remarques_periodes), 
                                    ("poste_remarques",    remarques_poste),
                                    ("IDdecision",    decision), 
                                    ("decision_remarques",    remarques_decision), 
                                    ("reponse_obligatoire",    reponse_obligatoire), 
                                    ("reponse",    reponse_communique), 
                                    ("date_reponse",    date_reponse), 
                                    ("IDtype_reponse",    type_reponse),
                                    ]
        if self.IDcandidature == None :
            newID = DB.ReqInsert("candidatures", listeDonnees)
            self.IDcandidature = newID
            nouvelleCandidature = True
        else:
            DB.ReqMAJ("candidatures", listeDonnees, "IDcandidature", self.IDcandidature)
            nouvelleCandidature = False
        DB.Commit()
        
        # Sauvegarde des disponibilités
        listeID = []
        for IDdisponibilite, date_debut, date_fin in listeDisponibilites :
            listeDonnees = [    ("IDcandidature",   self.IDcandidature),  
                                    ("date_debut",   date_debut),  
                                    ("date_fin",    date_fin),
                                    ]
            if IDdisponibilite == None :
                newID = DB.ReqInsert("disponibilites", listeDonnees)
                IDdisponibilite = newID
            else:
                DB.ReqMAJ("disponibilites", listeDonnees, "IDdisponibilite", IDdisponibilite)
            DB.Commit()
            listeID.append(IDdisponibilite)
            
        # Effacement des disponibilités supprimées
        if nouvelleCandidature == False :
            req = """SELECT IDdisponibilite, date_debut, date_fin
            FROM disponibilites WHERE IDcandidature=%d; """ % self.IDcandidature
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            for IDdisponibilite, date_debut, date_fin in listeDonnees :
                if IDdisponibilite not in listeID :
                    DB.ReqDEL("disponibilites", "IDdisponibilite", IDdisponibilite)
        
        # Sauvegarde des fonctions
        listeIDexistantes = []
        listeIDcand_fonction = []
        req = """SELECT IDcand_fonction, IDfonction
        FROM cand_fonctions WHERE IDcandidature=%d; """ % self.IDcandidature
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDcand_fonction, IDfonction in listeDonnees :
            listeIDexistantes.append(IDfonction)
            listeIDcand_fonction.append((IDcand_fonction, IDfonction))
        
        for IDfonction in listeFonctions :
            if IDfonction not in listeIDexistantes :
                # Si n'existe pas :
                listeDonnees = [    ("IDcandidature",   self.IDcandidature),  
                                        ("IDfonction",   IDfonction),  
                                        ]
                newID = DB.ReqInsert("cand_fonctions", listeDonnees)
                DB.Commit()
            
        # Effacement des fonctions supprimées
        if nouvelleCandidature == False :
            for IDcand_fonction, IDfonction in listeIDcand_fonction :
                if IDfonction not in listeFonctions :
                    DB.ReqDEL("cand_fonctions", "IDcand_fonction", IDcand_fonction)
            
        # Sauvegarde des affectations
        listeIDexistantes = []
        listeIDcand_affectation = []
        req = """SELECT IDcand_affectation, IDaffectation
        FROM cand_affectations WHERE IDcandidature=%d; """ % self.IDcandidature
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDcand_affectation, IDaffectation in listeDonnees :
            listeIDexistantes.append(IDaffectation)
            listeIDcand_affectation.append((IDcand_affectation, IDaffectation))
        
        for IDaffectation in listeAffectations :
            if IDaffectation not in listeIDexistantes :
                # Si n'existe pas :
                listeDonnees = [    ("IDcandidature",   self.IDcandidature),  
                                        ("IDaffectation",   IDaffectation),  
                                        ]
                newID = DB.ReqInsert("cand_affectations", listeDonnees)
                DB.Commit()
            
        # Effacement des affectations supprimées
        if nouvelleCandidature == False :
            for IDcand_affectation, IDaffectation in listeIDcand_affectation :
                if IDaffectation not in listeAffectations :
                    DB.ReqDEL("cand_affectations", "IDcand_affectation", IDcand_fonction)
        
        
        # Fin de la sauvegarde
        DB.Close()
        
        
        
        
        





class MyFrame(wx.Frame):
    def __init__(self, parent, IDcandidat=None):
        wx.Frame.__init__(self, parent, -1, title="", style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.panel = Panel(self, IDcandidat=IDcandidat)
                
        # Propriétés
        if IDcandidature == None :
            self.SetTitle(u"Saisie d'un candidat")
        else:
            self.SetTitle(u"Modification d'un candidat")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        
        # Layout
        self.SetMinSize((770, 550))
        self.SetSize((770, 550))
        self.CentreOnScreen()
        
    
    def Fermer(self):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

        
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, IDcandidat=None)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()