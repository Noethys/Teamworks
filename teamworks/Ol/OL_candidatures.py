#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import datetime
import wx
from Utils import UTILS_Adaptations
import GestionDB
import operator
import FonctionsPerso
import os
import sys
DLG_Saisie_candidature = UTILS_Adaptations.Import("Dlg.DLG_Saisie_candidature")
from Dlg import DLG_Selection_candidat
from Utils import UTILS_Fichiers
from ObjectListView import ObjectListView, ColumnDefn


DICT_FONCTIONS = {}
DICT_AFFECTATIONS = {}
DICT_EMPLOIS = {}
DICT_DISPONIBILITES = {}
DICT_CAND_FONCTIONS = {}
DICT_CAND_AFFECTATIONS = {}
NOMS_CANDIDATS = {}
NOMS_PERSONNES = {}

# Liste sans nom du candidat
LISTE_COLONNES_1 = [
            [_(u"ID"), "left", 0, "IDcandidature", "", _(u"ID de la candidature"), True, 1 ],
            [_(u"Dépôt"), "left", 90, _(u"depot"), "image_type_depot", _(u"Caractéristiques du dépôt"), True, 2 ],
            [_(u"Offre d'emploi"), "left", 160, "offre_emploi", "", _(u"Intitulé de l'offre d'emploi"), True, 3 ],
            [_(u"Disponibilités"), "left", 140, "disponibilites", "", _(u"Disponibilités indiquées par le candidat"), True, 4 ],
            [_(u"Fonction(s)"), "left", 100, "fonctions", "", _(u"Fonction(s) souhaitée(s) par le candidat"), True, 5 ],
            [_(u"Affectation(s)"), "left", 100, "affectations", "" , _(u"Affectation(s) souhaitée(s) par le candidat"), True, 6 ],
            [_(u"Décision"), "left", 60, "decision", "image_decision", _(u"Décision prise par le recruteur"), True, 7 ],
            [_(u"Réponse"), "left", 90, "texte_reponse", "image_type_reponse", _(u"Réponse communiquée au candidat"), True, 8 ],
            ] # nom Colonne, alignement, largeur, nom Champ, Args pour OLV, Description, Affiché ?, Ordre

# Liste avec nom du candidat
LISTE_COLONNES_2 = [
            [_(u"ID"), "left", 0, "IDcandidature", "", _(u"ID de la candidature"), True, 1 ],
            [_(u"Dépôt"), "left", 90, _(u"depot"), "image_type_depot", _(u"Caractéristiques du dépôt"), True, 2 ],
            [_(u"Nom"), "left", 120, _(u"nom_candidat"), "", _(u"Nom du candidat"), True, 3 ],
            [_(u"Offre d'emploi"), "left", 160, "offre_emploi", "", _(u"Intitulé de l'offre d'emploi"), True, 4 ],
            [_(u"Disponibilités"), "left", 140, "disponibilites", "", _(u"Disponibilités indiquées par le candidat"), True, 5 ],
            [_(u"Fonction(s)"), "left", 100, "fonctions", "", _(u"Fonction(s) souhaitée(s) par le candidat"), True, 6 ],
            [_(u"Affectation(s)"), "left", 100, "affectations", "" , _(u"Affectation(s) souhaitée(s) par le candidat"), True, 7 ],
            [_(u"Décision"), "left", 60, "decision", "image_decision", _(u"Décision prise par le recruteur"), True, 8 ],
            [_(u"Réponse"), "left", 90, "texte_reponse", "image_type_reponse", _(u"Réponse communiquée au candidat"), True, 9 ],
            ] # nom Colonne, alignement, largeur, nom Champ, Args pour OLV, Description, Affiché ?, Ordre

# Liste avec groupement par offre d'emploi
LISTE_COLONNES_3 = [
            [_(u"Nom"), "left", 200, _(u"nom_candidat"), "", _(u"Nom du candidat"), True, 1 ],
            [_(u"ID"), "left", 0, "IDcandidature", "", _(u"ID de la candidature"), True, 2 ],
            [_(u"Dépôt"), "left", 90, _(u"depot"), "image_type_depot", _(u"Caractéristiques du dépôt"), True, 3 ],
            [_(u"Offre d'emploi"), "left", 0, "offre_emploi", "groupe_emploi", _(u"Intitulé de l'offre d'emploi"), True, 4 ],
            [_(u"Disponibilités"), "left", 140, "disponibilites", "", _(u"Disponibilités indiquées par le candidat"), True, 5 ],
            [_(u"Fonction(s)"), "left", 100, "fonctions", "", _(u"Fonction(s) souhaitée(s) par le candidat"), True, 6 ],
            [_(u"Affectation(s)"), "left", 100, "affectations", "" , _(u"Affectation(s) souhaitée(s) par le candidat"), True, 7 ],
            [_(u"Décision"), "left", 60, "decision", "image_decision", _(u"Décision prise par le recruteur"), True, 8 ],
            [_(u"Réponse"), "left", 90, "texte_reponse", "image_type_reponse", _(u"Réponse communiquée au candidat"), True, 9 ],
            ] # nom Colonne, alignement, largeur, nom Champ, Args pour OLV, Description, Affiché ?, Ordre

# ---------------------------------------- LISTVIEW PERSONNES  -----------------------------------------------------------------------


class Track(object):
    def __init__(self, donnees):
        self.IDcandidature = donnees[0]
        self.IDcandidat = donnees[1]
        self.date_depot = donnees[2]
        self.IDtype = donnees[3] 
        self.acte_remarques = donnees[4]
        self.IDemploi = donnees[5]
        self.periodes_remarques = donnees[6]
        self.IDdecision = donnees[7]
        self.decision_remarques = donnees[8]
        self.reponse_obligatoire = donnees[9]
        self.reponse = donnees[10]
        self.date_reponse = donnees[11]
        self.IDtype_reponse = donnees[12]
        self.IDpersonne = donnees[13]
        
        if self.IDpersonne == 0 or self.IDpersonne == None :
            civilite, nom, prenom = NOMS_CANDIDATS[self.IDcandidat]
            self.nom_candidat = u"%s %s" % (nom, prenom)
        else:
            civilite, nom, prenom = NOMS_PERSONNES[self.IDpersonne]
            self.nom_candidat = u"%s %s" % (nom, prenom)
        
        # Dépôt
        date1 = datetime.date(year=int(self.date_depot[:4]), month=int(self.date_depot[5:7]), day=int(self.date_depot[8:10]))
        self.depot = date1.strftime("%d/%m/%Y")
        self.depot_long = date1.strftime("%A %d %B %Y")
        
        # Offre d'emploi
        if self.IDemploi == 0 :
            self.offre_emploi = _(u"Candidature spontanée")
        else:
            self.offre_emploi = DICT_EMPLOIS[self.IDemploi][2]
        
        # Disponibilites
        if self.IDcandidature in DICT_DISPONIBILITES :
            texteDispo = ""
            for IDdisponibilite, date_debut, date_fin in DICT_DISPONIBILITES[self.IDcandidature] :
                texteDispo += _(u"du %s au %s; \n") % (date_debut.strftime("%d/%m/%Y"), date_fin.strftime("%d/%m/%Y"))
            if len(texteDispo) > 0 : texteDispo = texteDispo[:-3]
            self.disponibilites = texteDispo
        else:
            self.disponibilites = _(u"Inconnu")
        
        # Fonctions
        if self.IDcandidature in DICT_CAND_FONCTIONS :
            texteDispo = ""
            for IDfonction in DICT_CAND_FONCTIONS[self.IDcandidature] :
                texteDispo += u"%s; \n" % DICT_FONCTIONS[IDfonction]
            if len(texteDispo) > 0 : texteDispo = texteDispo[:-3]
            self.fonctions = texteDispo
        else:
            self.fonctions = _(u"Inconnu")
        
        # Affectations
        if self.IDcandidature in DICT_CAND_AFFECTATIONS :
            texteDispo = ""
            for IDfonction in DICT_CAND_AFFECTATIONS[self.IDcandidature] :
                texteDispo += u"%s; \n" % DICT_AFFECTATIONS[IDfonction]
            if len(texteDispo) > 0 : texteDispo = texteDispo[:-3]
            self.affectations = texteDispo
        else:
            self.affectations = _(u"Inconnu")
        
        # Décision
        self.decision = self.decision_remarques
        
        # Reponse
        if self.reponse == 1 :
            date2 = datetime.date(year=int(self.date_reponse[:4]), month=int(self.date_reponse[5:7]), day=int(self.date_reponse[8:10]))
            self.texte_reponse = date2.strftime("%d/%m/%Y")
            self.texte_reponse_long = date2.strftime("%A %d %B %Y")
        else:
            self.texte_reponse = ""
            self.texte_reponse_long = ""

    
class ListView(ObjectListView):
    def __init__(self, *args, **kwds):
        wx.Locale(wx.LANGUAGE_FRENCH)
        # Récupération des paramètres perso
        self.IDcandidat = kwds.pop("IDcandidat", None)
        self.IDpersonne = kwds.pop("IDpersonne", None)
        self.IDemploi = kwds.pop("IDemploi", None)
        self.modeAffichage = kwds.pop("modeAffichage", None)
        self.colorerSalaries = kwds.pop("colorerSalaries", True)
        self.activeCheckBoxes = kwds.pop("activeCheckBoxes", False)
        self.activeDoubleClic = kwds.pop("activeDoubleClic", True)
        self.activeMenuContextuel = kwds.pop("activeMenuContextuel", True)
        self.activePopup = kwds.pop("activePopup", True)
        self.selectionID = None
        self.selectionTrack = None
        self.presents = False
        self.criteres = ""
        self.listeFiltres = []
        self.itemSelected = False
        self.popupIndex = -1
        # Initialisation du listCtrl
        ObjectListView.__init__(self, *args, **kwds)
        if self.modeAffichage == None or self.modeAffichage == "sans_nom" : 
            self.listeColonnes = LISTE_COLONNES_1
        if self.modeAffichage == "avec_nom" : 
            self.listeColonnes = LISTE_COLONNES_2
        if self.modeAffichage == "groupe_emplois" : 
            self.listeColonnes = LISTE_COLONNES_3
        self.listeColonnesOriginale = list(self.listeColonnes)
##        self.InitModel()
##        self.InitObjectListView()

        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        if self.activeMenuContextuel == True :
            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        if self.activeMenuContextuel == True :
            self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        
        if "linux" not in sys.platform and self.activePopup == True :
            # Désactive la fenetre popup sous Linux
            self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        
    def OnItemActivated(self,event):
        self.DestroyPopup()
        self.Modifier()
        
    def OnItemSelected(self, event):
        self.DestroyPopup()
        self.itemSelected = True
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                self.GetGrandParent().GetParent().bouton_modifier.Enable(True)
                self.GetGrandParent().GetParent().bouton_supprimer.Enable(True)
                if len(self.Selection()) == 0:
                    return False
                IDcandidat = self.Selection()[0].IDcandidat
                IDpersonne = self.Selection()[0].IDpersonne
                # Met à jour le cadre Résumé
                self.GetGrandParent().GetParent().panel_resume.MAJ(IDcandidat=IDcandidat, IDpersonne=IDpersonne)
                self.GetGrandParent().GetParent().AffichePanelResume(True)
        except : 
            pass
        
    def OnItemDeselected(self, event):
        self.itemSelected = False
        wx.FutureCall(100, self.DeselectionneItem)
    
    def DeselectionneItem(self) :
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                if self.itemSelected == False :
                    self.GetGrandParent().GetParent().bouton_modifier.Enable(False)
                    self.GetGrandParent().GetParent().bouton_supprimer.Enable(False)
                    self.GetGrandParent().GetParent().AffichePanelResume(False)
        except : 
            pass
        self.itemSelected = False
        
    def InitModel(self):
        self.Importation_fonctions()
        self.Importation_affectations()
        self.Importation_emplois()
        self.Importation_disponibilites()
        self.Importation_cand_fonctions()
        self.Importation_cand_affectations()
        self.Importation_candidats()
        self.Importation_personnes() 
        self.donnees = self.GetTracks()

    def GetListeFiltres(self, listeFiltres=[]):
                
        # ------------------------------------------------------------------------------------------------------------------------
        
        def GetListeDisponibilites(dictFiltres):
            """ Recherche des disponibilités """
            listeTemp = []
            for IDcandidature, disponibilites in DICT_DISPONIBILITES.items() :
                for IDdisponibilite, date_debut, date_fin in disponibilites :
                    if date_fin>=dictFiltres["valeur"][0] and date_debut<=dictFiltres["valeur"][1] :
                        listeTemp.append(IDcandidature)
            return listeTemp
        
        def GetListeFonctions(dictFiltres):
            """ Recherche des fonctions """
            listeTemp = []
            for IDcandidature, listeFonctions in DICT_CAND_FONCTIONS.items() :
                for ID, label in dictFiltres["valeur"] :
                    if ID in listeFonctions :
                        if IDcandidature not in listeTemp :
                            listeTemp.append(IDcandidature)
            return listeTemp
        
        def GetListeAffectations(dictFiltres):
            """ Recherche des affectations """
            listeTemp = []
            for IDcandidature, listeAffectations in DICT_CAND_AFFECTATIONS.items() :
                for ID, label in dictFiltres["valeur"] :
                    if ID in listeAffectations :
                        if IDcandidature not in listeTemp :
                            listeTemp.append(IDcandidature)
            return listeTemp
        
        # ------------------------------------------------------------------------------------------------------------------------
        nbreFiltres = 0
        criteresSQL = ""
        listeListes = []
        for dictFiltres in listeFiltres :
            
            if dictFiltres["nomControle"] == "candidature_dispo" : 
                listeListes.append(GetListeDisponibilites(dictFiltres))
            elif dictFiltres["nomControle"] == "candidature_fonctions" : 
                listeListes.append(GetListeFonctions(dictFiltres))
            elif dictFiltres["nomControle"] == "candidature_affectations" : 
                listeListes.append(GetListeAffectations(dictFiltres))
            else:
                criteresSQL += dictFiltres["sql"] + " AND "
                nbreFiltres += 1
                
        # Recherche des ID communs aux listes
        nbreListes = len(listeListes)
        if nbreListes == 0 :
            listeID = None
        elif nbreListes == 1 :
            listeID = listeListes[0]
        else :
            # Si plusieurs listes 
            texteFonction = ""
            index = 0
            for liste in listeListes :
                texteFonction += "set(listeListes[%d]) & " % index
                index += 1
            texteFonction = texteFonction[:-3]
            exec("listeID=%s" % texteFonction)
            listeID = list(listeID)
            
        # Traitement des requetes SQL
        if nbreFiltres > 0 :
            criteresSQL = criteresSQL[:-5]

        return listeID, criteresSQL
            
        
    def GetTracks(self):
        """ Récupération des données """
        # Critères
        listeID = None
        self.criteres = ""
        if self.IDcandidat != None and self.IDcandidat != 0 :
            self.criteres = "WHERE IDcandidat=%d" % self.IDcandidat
        if self.IDpersonne != None and self.IDpersonne != 0 :
            self.criteres = "WHERE IDpersonne=%d" % self.IDpersonne
        if self.IDemploi != None :
            self.criteres = "WHERE IDemploi=%d" % self.IDemploi
        # Liste de filtres
        if len(self.listeFiltres) > 0 :
            listeID, criteres = self.GetListeFiltres(self.listeFiltres)
            if criteres != "" :
                if self.criteres == "" :
                    self.criteres = "WHERE " + criteres
                else:
                    self.criteres += " AND " + criteres
        
        # Req
        DB = GestionDB.DB()
        req = """SELECT IDcandidature, IDcandidat, date_depot, IDtype, acte_remarques, IDemploi, periodes_remarques, IDdecision, 
        decision_remarques, reponse_obligatoire, reponse, date_reponse, IDtype_reponse, IDpersonne 
        FROM candidatures %s ORDER BY date_depot; """ % self.criteres
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeListeView = []
        for item in listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView

    def Importation_fonctions(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDfonction, fonction
        FROM fonctions; """
        DB.ExecuterReq(req)
        listeFonctions = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global DICT_FONCTIONS
        DICT_FONCTIONS = {}
        for IDfonction, fonction in listeFonctions :
            DICT_FONCTIONS[IDfonction] = fonction

    def Importation_affectations(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDaffectation, affectation
        FROM affectations; """
        DB.ExecuterReq(req)
        listeAffectations = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global DICT_AFFECTATIONS
        DICT_AFFECTATIONS = {}
        for IDaffectation, affectation in listeAffectations :
            DICT_AFFECTATIONS[IDaffectation] = affectation        
                                    
    def Importation_emplois(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDemploi, date_debut, date_fin, intitule, detail
        FROM emplois; """
        DB.ExecuterReq(req)
        listeEmplois = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global DICT_EMPLOIS
        DICT_EMPLOIS = {}
        for IDemploi, date_debut, date_fin, intitule, detail in listeEmplois :
            DICT_EMPLOIS[IDemploi] = (date_debut, date_fin, intitule, detail)         

    def Importation_disponibilites(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDdisponibilite, IDcandidature, date_debut, date_fin
        FROM disponibilites; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global DICT_DISPONIBILITES
        DICT_DISPONIBILITES = {}
        for IDdisponibilite, IDcandidature, date_debut, date_fin in listeDonnees :
            date_debut = datetime.date(year=int(date_debut[:4]), month=int(date_debut[5:7]), day=int(date_debut[8:10]))
            date_fin = datetime.date(year=int(date_fin[:4]), month=int(date_fin[5:7]), day=int(date_fin[8:10]))
            if IDcandidature in DICT_DISPONIBILITES :
                DICT_DISPONIBILITES[IDcandidature].append((IDdisponibilite, date_debut, date_fin))
            else:
                DICT_DISPONIBILITES[IDcandidature] = [(IDdisponibilite, date_debut, date_fin),]

    def Importation_cand_fonctions(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDcand_fonction, IDcandidature, IDfonction
        FROM cand_fonctions; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global DICT_CAND_FONCTIONS
        DICT_CAND_FONCTIONS = {}
        for IDcand_fonction, IDcandidature, IDfonction in listeDonnees :
            if IDcandidature in DICT_CAND_FONCTIONS :
                DICT_CAND_FONCTIONS[IDcandidature].append(IDfonction)
            else:
                DICT_CAND_FONCTIONS[IDcandidature] = [IDfonction,]

    def Importation_cand_affectations(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDcand_affectation, IDcandidature, IDaffectation
        FROM cand_affectations; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global DICT_CAND_AFFECTATIONS
        DICT_CAND_AFFECTATIONS = {}
        for IDcand_affectation, IDcandidature, IDaffectation in listeDonnees :
            if IDcandidature in DICT_CAND_AFFECTATIONS :
                DICT_CAND_AFFECTATIONS[IDcandidature].append(IDaffectation)
            else:
                DICT_CAND_AFFECTATIONS[IDcandidature] = [IDaffectation,]

    def Importation_candidats(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDcandidat, civilite, nom, prenom
        FROM candidats ORDER BY nom, prenom; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global NOMS_CANDIDATS
        NOMS_CANDIDATS = {}
        for IDcandidat, civilite, nom, prenom in listeDonnees :
            NOMS_CANDIDATS[IDcandidat] = (civilite, nom, prenom)

    def Importation_personnes(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDpersonne, civilite, nom, prenom
        FROM personnes ORDER BY nom, prenom; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global NOMS_PERSONNES
        NOMS_PERSONNES = {}
        for IDpersonne, civilite, nom, prenom in listeDonnees :
            NOMS_PERSONNES[IDpersonne] = (civilite, nom, prenom)
                        
    def InitObjectListView(self):
        # Images
        self.imgVivevoix = self.AddNamedImages("vivevoix", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Dialogue.png"), wx.BITMAP_TYPE_PNG))
        self.imgCourrier = self.AddNamedImages("courrier", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mail.png"), wx.BITMAP_TYPE_PNG))
        self.imgTelephone = self.AddNamedImages("telephone", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mobile.png"), wx.BITMAP_TYPE_PNG))
        self.imgMain = self.AddNamedImages("main", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mainamain.png"), wx.BITMAP_TYPE_PNG))
        self.imgEmail = self.AddNamedImages("email", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mail2.png"), wx.BITMAP_TYPE_PNG))
        self.imgPole_emploi = self.AddNamedImages("pole_emploi", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Pole_emploi.png"), wx.BITMAP_TYPE_PNG))
        self.imgAutre = self.AddNamedImages("autre", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Etoile.png"), wx.BITMAP_TYPE_PNG))
        self.imgVide = self.AddNamedImages("vide", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Vide.png"), wx.BITMAP_TYPE_PNG))
        self.imgQuestion = self.AddNamedImages("question", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Question.png"), wx.BITMAP_TYPE_PNG))
        self.imgOui = self.AddNamedImages("oui", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))
        self.imgNon = self.AddNamedImages("non", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        
        # Formatage des données
        def ImageGetter_type_depot(track):
            if track.IDtype == 0 : return self.imgVivevoix
            elif track.IDtype == 1 : return self.imgCourrier
            elif track.IDtype == 2 : return self.imgTelephone
            elif track.IDtype == 3 : return self.imgMain
            elif track.IDtype == 4 : return self.imgEmail
            elif track.IDtype == 5 : return self.imgPole_emploi
            else: return self.imgAutre
        
        def ImageGetter_decision(track):
            if track.IDdecision == 0 : return self.imgQuestion
            elif track.IDdecision == 1 : return self.imgOui
            elif track.IDdecision == 2 : return self.imgNon
            else: return self.imgQuestion
        
        def ImageGetter_type_reponse(track):
            if track.reponse == 1 :
                if track.IDtype_reponse == 0 : return self.imgVivevoix
                elif track.IDtype_reponse == 1 : return self.imgCourrier
                elif track.IDtype_reponse == 2 : return self.imgTelephone
                elif track.IDtype_reponse == 3 : return self.imgMain
                elif track.IDtype_reponse == 4 : return self.imgEmail
                else: return self.imgAutre
            else: return self.imgVide
        
##        def emploiGroupKey(track):
##            return track.IDemploi
##        
##        def emploiGroupKeyConverter(groupKey):
##            if groupKey == 0 :
##                nomEmploi = _(u"Candidature spontanée")
##            else:
##                nomEmploi = DICT_EMPLOIS[groupKey][2]
##            return nomEmploi
            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#EEF4FB" # wx.Colour(255, 255, 255) #"#EEF4FB" # Bleu
        self.evenRowsBackColor = wx.Colour(255, 255, 255) #"#F0FBED" # Vert
        self.useExpansionColumn = True
        
        def FormateDate(dateStr):
            if dateStr == "" or dateStr == None : return ""
            date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text
        
        def rowFormatter(listItem, track):
            if track.IDpersonne != None and track.IDpersonne != 0 :
                listItem.SetTextColour(wx.RED)
        
        if self.colorerSalaries == True :
            self.rowFormatter = rowFormatter

        # Création des colonnes
        liste_ColonnesTmp = self.listeColonnes
        # Tri par ordre
        liste_ColonnesTmp.sort(key=operator.itemgetter(7))
        
        liste_Colonnes = []
        for labelCol, alignement, largeur, nomChamp, args, description, affiche, ordre in liste_ColonnesTmp :
            if affiche == True :
                if args == "date" :
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp, stringConverter=FormateDate)
                elif args == "image_type_depot" :
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp, imageGetter=ImageGetter_type_depot)
                elif args == "image_decision" :
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp, imageGetter=ImageGetter_decision)
                elif args == "image_type_reponse" :
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp, imageGetter=ImageGetter_type_reponse)
                else:
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp)
                liste_Colonnes.append(colonne)
        
        self.SetColumns(liste_Colonnes)
        
        self.SetEmptyListMsg(_(u"Aucune candidature"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        if self.activeCheckBoxes == True :
            self.CreateCheckStateColumn(1)
            self.SetSortColumn(self.columns[2])
        else:
            self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
        
        
       
    def MAJ(self, IDpersonne=None, presents=None):
        if IDpersonne != None :
            self.selectionID = IDpersonne
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        if presents != None :
            self.presents = presents
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if self.selectionTrack != None :
            self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
        self.selectionID = None
        self.selectionTrack = None
        self.SetLabelSelection() 
    
    def Selection(self):
        return self.GetSelectedObjects()
    
    def SetListeColonnes(self, listeColonnes):
        self.listeColonnes = listeColonnes










# --------------------------------------------------------------------------------------------------------------------------------------------------











    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        self.DestroyPopup()
        
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDcandidature
                
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        menuPop.AppendSeparator()
            
        # Item Modifier
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()
        
        # Item Publipostage
        item = wx.MenuItem(menuPop, 140, _(u"Créer un courrier ou un mail par publipostage"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mail.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Courrier, id=140)
        if noSelection == True : item.Enable(False)

        menuPop.AppendSeparator()
        
        # Item Rechercher
        item = wx.MenuItem(menuPop, 80, _(u"Rechercher"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Rechercher, id=80)

        # Item Afficher tout
        item = wx.MenuItem(menuPop, 50, _(u"Afficher tout"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_AfficherTout, id=50)
        
        # Item Options
        item = wx.MenuItem(menuPop, 60, _(u"Options de liste"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Options, id=60)
        
        menuPop.AppendSeparator()
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 90, _(u"Imprimer la liste"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuImprimer, id=90)
        
        # Item Export Texte
        item = wx.MenuItem(menuPop, 100, _(u"Exporter la liste au format Texte"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuExportTexte, id=100)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 110, _(u"Exporter la liste au format Excel"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuExportExcel, id=110)
        
        menuPop.AppendSeparator()

        # Item Aide
        item = wx.MenuItem(menuPop, 70, _(u"Aide"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Aide.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Aide, id=70)
                
        self.PopupMenu(menuPop)
        menuPop.Destroy()


    def Menu_Ajouter(self, event):
        self.Ajouter()
        
    def Menu_Modifier(self, event):
        self.Modifier()
        return

    def Menu_Supprimer(self, event):
        self.Supprimer()
        
    def Menu_AfficherTout(self, event):
        self.AfficherTout()
    
    def Menu_Rechercher(self, event):
        self.Rechercher()
    
    def Menu_Courrier(self, event):
        self.CourrierPublipostage()
        
    def Menu_Options(self, event):
        self.Options()

    def Menu_Aide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")
        
    def Menu_Mail(self, event):
        FonctionsPerso.EnvoyerMail(adresses = (self.adresseMail,))

    def AfficherTout(self):
        """ Réafficher toute la liste """
        self.criteres = ""
        self.listeFiltres = []
        self.MAJ()
            
    def Options(self):
        """ Choix et ordre des colonnes """
        from Dlg import DLG_Config_liste_personnes
        dlg = DLG_Config_liste_personnes.Dialog(self, self.listeColonnes)
        dlg.ShowModal()
        dlg.Destroy()

    def MenuImprimer(self, event):
        self.Imprimer()
        
    def MenuExportTexte(self, event):
        self.ExportTexte()
        
    def MenuExportExcel(self, event):
        self.ExportExcel()

    def Rechercher(self):
        # Récupération des filtres souhaités
        from Dlg import DLG_Filtre_recrutement
        dlg = DLG_Filtre_recrutement.MyDialog(self, categorie="candidatures", listeValeursDefaut=self.listeFiltres, title=_(u"Sélection de filtres de liste"))
        if dlg.ShowModal() == wx.ID_OK:
            listeFiltres = dlg.GetListeFiltres()
            dlg.Destroy()
            # Application des filtres
            self.listeFiltres = listeFiltres
            self.MAJ()
        else:
            dlg.Destroy()

    def SetLabelSelection(self):
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                if len(self.listeFiltres) > 0 :
                    texte = _(u"Filtres de sélection : ")
                    for dictFiltre in self.listeFiltres :
                        texte += u"%s (%s), " % (dictFiltre["labelControle"], dictFiltre["label"])
                    texte = texte[:-2]
                    self.GetGrandParent().GetParent().AfficheLabelSelection(True)
                    self.GetGrandParent().GetParent().label_selection.SetLabel(texte)
                else:
                    self.GetGrandParent().GetParent().AfficheLabelSelection(False)
                    self.GetGrandParent().GetParent().label_selection.SetLabel("")
        except : 
            pass
        
    def Ajouter(self):
        
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                self.GetGrandParent().GetParent().AffichePanelResume(False)
        except : 
            pass
            
        # Si aucun candidat sélectionné
        if (self.IDcandidat == None or self.IDcandidat == 0) and (self.IDpersonne == None or self.IDpersonne == 0 ):
            dlg = DLG_Selection_candidat.MyDialog(self)
            if dlg.ShowModal() == wx.ID_OK:
                IDcandidat = dlg.GetIDcandidat()
                IDpersonne = dlg.GetIDpersonne()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return False
        else:
            IDcandidat = self.IDcandidat
            IDpersonne = self.IDpersonne
            
        # Ouverture de la saisie d'un candidature
        dlg = DLG_Saisie_candidature.Dialog(self, IDcandidat=IDcandidat, IDpersonne=IDpersonne, IDcandidature=None)
        dlg.ShowModal()
        dlg.Destroy()

    def Modifier(self):
        
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                self.GetGrandParent().GetParent().AffichePanelResume(False)
        except : 
            pass
            
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une candidature à modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        IDcandidature = self.Selection()[0].IDcandidature
        IDcandidat = self.Selection()[0].IDcandidat
        IDpersonne = self.Selection()[0].IDpersonne
        dlg = DLG_Saisie_candidature.Dialog(self, IDcandidat=IDcandidat, IDpersonne=IDpersonne, IDcandidature=IDcandidature)
        dlg.ShowModal()
        dlg.Destroy()
                
    def Supprimer(self):
        
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                self.GetGrandParent().GetParent().AffichePanelResume(False)
        except : 
            pass
            
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une candidature à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        IDcandidature = self.Selection()[0].IDcandidature
                
        # Demande de confirmation
        date_depot = self.Selection()[0].depot
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer la candidature du %s ?") % date_depot))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Suppression
        DB = GestionDB.DB()
        
        # Suppression
        DB.ReqDEL("candidatures", "IDcandidature", IDcandidature)
        DB.ReqDEL("disponibilites", "IDcandidature", IDcandidature)
        DB.ReqDEL("cand_fonctions", "IDcandidature", IDcandidature)
        DB.ReqDEL("cand_affectations", "IDcandidature", IDcandidature)
        
        DB.Close()
        # MàJ du ListCtrl
        self.MAJ()
        
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" : 
                self.GetGrandParent().GetParent().gadget_entretiens.MAJ()
                self.GetGrandParent().GetParent().gadget_informations.MAJ()
        except :
            pass
        
        try :
            if self.GetGrandParent().GetName() == "panel_resume" :
                panelRecrutement = self.GetGrandParent().GetGrandParent().GetParent()
                panelRecrutement.MAJpanel(MAJpanelResume=False)
                self.GetGrandParent().MAJlabelsPages("candidatures")
        except :
            pass
            
    def GetValeurs(self):
        """ Récupère les valeurs affichées sous forme de liste """
        # Récupère les labels de colonnes
        liste_ColonnesTmp = self.listeColonnes
        liste_ColonnesTmp.sort(key=operator.itemgetter(7))
        liste_labelsColonnes = []
        for labelCol, alignement, largeur, nomChamp, args, description, affiche, ordre in liste_ColonnesTmp :
            if affiche == True :
                liste_labelsColonnes.append( (labelCol, alignement, largeur, nomChamp) )

        # Récupère les valeurs
        listeValeurs = []
        listeObjects = self.GetFilteredObjects()
        for object in listeObjects :
            valeursLigne = []
            for indexCol in range(0, self.GetColumnCount() ) :
                valeur = self.GetStringValueAt(object, indexCol)
                valeursLigne.append(valeur)
            listeValeurs.append(valeursLigne)
        
        return liste_labelsColonnes, listeValeurs
    
    def GetNbreItems(self):
        return len(self.donnees)

    def CourrierPublipostage(self, mode="unique"):
        if mode == "unique" :
            if len(self.Selection()) == 0:
                dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une candidature dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            listeID = [self.Selection()[0].IDcandidature,]
        else:
            if self.GetNbreItems() == 0 :
                dlg = wx.MessageDialog(self, _(u"Il n'y a aucune candidature dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            # Récupération des valeurs
            liste_labelsColonnes, listeValeurs = self.GetValeurs()
            # Selection des lignes
            from Dlg import DLG_Selection_liste
            dlg = DLG_Selection_liste.Dialog(self, liste_labelsColonnes, listeValeurs, type="exportTexte")
            if dlg.ShowModal() == wx.ID_OK:
                listeSelections = dlg.GetSelections()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return False
            listeID = listeSelections
        
        # Récupère les données pour le publipostage
        from Utils import UTILS_Publipostage_donnees
        dictDonnees = UTILS_Publipostage_donnees.GetDictDonnees(categorie="candidature", listeID=listeID)
        # Ouvre le publiposteur
        from Dlg import DLG_Publiposteur
        frm = DLG_Publiposteur.MyWizard(self, "", dictDonnees=dictDonnees)
        frm.Show()
        
        
    def ExportTexte(self):
        """ Export de la liste au format texte """
        if self.GetNbreItems() == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune candidature dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Récupération des valeurs
        liste_labelsColonnes, listeValeurs = self.GetValeurs()
        
        # Selection des lignes
        from Dlg import DLG_Selection_liste
        dlg = DLG_Selection_liste.Dialog(self, liste_labelsColonnes, listeValeurs, type="exportTexte")
        if dlg.ShowModal() == wx.ID_OK:
            listeSelections = dlg.GetSelections()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        
        nomFichier = "ExportTexte.txt"
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        wildcard = "Fichier texte (*.txt)|*.txt|" \
                        "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            self, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut, 
            defaultFile = nomFichier, 
            wildcard = wildcard, 
            style = wx.FD_SAVE
            )
        dlg.SetFilterIndex(2)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # Le fichier de destination existe déjà :
        if os.path.isfile(cheminFichier) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        # Création du fichier texte
        texte = ""
        separateur = ";"
        for labelCol, alignement, largeur, nomChamp in liste_labelsColonnes :
            texte += nomChamp + separateur
        texte = texte[:-1] + "\n"

        for valeurs in listeValeurs :
            if int(valeurs[0]) in listeSelections :
                for valeur in valeurs :
                    texte += valeur + separateur
                texte = texte[:-1] + "\n"
        
        # Elimination du dernier saut à la ligne
        texte = texte[:-1]

        # Création du fichier texte
        f = open(cheminFichier, "w")
        f.write(texte.encode("iso-8859-15"))
        f.close()
        
        # Confirmation de création du fichier et demande d'ouverture directe dans Excel
        txtMessage = _(u"Le fichier Texte a été créé avec succès. Souhaitez-vous l'ouvrir dès maintenant ?")
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)
            
            
    def ExportExcel(self):
        """ Export de la liste au format Excel """
        if "linux" in sys.platform :
            dlg = wx.MessageDialog(self, _(u"Désolé, cette fonction n'est pas disponible dans la version LINUX de Teamworks."), "Fonction indisponible", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if self.GetNbreItems() == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune personne dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Récupération des valeurs
        labels_colonnes, liste_valeurs = self.GetValeurs()
        from Utils import UTILS_Excel
        UTILS_Excel.Excel(self, labels_colonnes, liste_valeurs)

    def Imprimer(self):
        """ Imprimer la liste au format PDF """
        if self.GetNbreItems() == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune personne dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        # Récupération des valeurs
        liste_labelsColonnes, listeValeurs = self.GetValeurs()

        # Selection des lignes
        from Dlg import DLG_Selection_liste
        dlg = DLG_Selection_liste.Dialog(self, liste_labelsColonnes, listeValeurs, type="imprimerListePersonnes")
        if dlg.ShowModal() == wx.ID_OK:
            listeSelections = dlg.GetSelections()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False

        Impression(liste_labelsColonnes, listeValeurs, listeSelections)


    def OnMouseMotion(self, event):
        # Panel flottant
        index = self.HitTest(event.GetPosition())[0]
        if index == -1:
            if self.popupIndex != -1 :
                self.DestroyPopup()
            return
            
        item = self.GetItem(index, 0)
        
        pos = self.ClientToScreen(event.GetPosition()) # Position du curseur sur l'écran
        decalage = (15, 15)

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
            self.Popup = Popup(self, key=key)
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
            



class Popup(wx.PopupWindow):
    def __init__(self, parent, style=wx.SIMPLE_BORDER, key=0):
        wx.PopupWindow.__init__(self, parent, style)
        self.panel = wx.Panel(self, -1)
        listView = self.GetParent()
        track = listView.GetObjectAt(key)
        imageList = listView.smallImageList.imageList
        
        # Récupération des images
        img_depot = imageList.GetBitmap(listView.GetImageAt(track, 1))
        img_decision = imageList.GetBitmap(listView.GetImageAt(track, 6))
        img_reponse = imageList.GetBitmap(listView.GetImageAt(track, 7))
        
        # Récupération des données
        listeColonnes = [
            ( 1, _(u"Dépôt"), img_depot, track.depot_long ),
            ( 1, _(u"Nom"), None, track.nom_candidat ),
            ( 2, _(u"Emploi"), None, track.offre_emploi ),
            ( 3, _(u"Disponibilités"), None, track.disponibilites ),
            ( 4, _(u"Fonctions"), None, track.fonctions ),
            ( 5, _(u"Affectations"), None, track.affectations ),
            ( 6, _(u"Décision"), img_decision, track.decision ),
            ( 7, _(u"Réponse"), img_reponse, track.texte_reponse_long ),
            ] # IndexColonne, Label, Image, Donnée
        
        
        # Création du popup
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base_2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=9, cols=2, vgap=5, hgap=5)
        
        index = 0
        for indexCol, label, img, donnee in listeColonnes :
            # Label
            exec("self.label_" + str(index) + " = wx.StaticText(self.panel, -1, u'%s :' % label)")
            exec("self.label_" + str(index) + ".SetForegroundColour(wx.Colour(127, 0, 255))")
            exec("grid_sizer_base.Add(self.label_" + str(index) + ", 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)")
            # Détail : Image et valeur
            if img != None : exec("self.image_" + str(index) + " = wx.StaticBitmap(self.panel, -1, img)")
            exec("self.ctrl_" + str(index) + " = wx.StaticText(self.panel, -1, donnee)")
            # Sizer détail
            if img != None : 
                exec("grid_sizer_" + str(index) + " = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)")
                exec("grid_sizer_" + str(index) + ".Add(self.image_" + str(index) + ", 0, wx.ALIGN_CENTER_VERTICAL, 0)")
                exec("grid_sizer_" + str(index) + ".Add(self.ctrl_" + str(index) + ", 0, wx.ALIGN_CENTER_VERTICAL, 0)")
                exec("grid_sizer_" + str(index) + ".AddGrowableCol(1)")
                exec("grid_sizer_base.Add(grid_sizer_" + str(index) + ", 1, wx.EXPAND, 0)")
            else:
                exec("grid_sizer_base.Add(self.ctrl_" + str(index) + ", 1, wx.EXPAND, 0)")
            index += 1
            
        grid_sizer_base.AddGrowableCol(1)
        sizer_base_2.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.panel.SetSizer(sizer_base_2)
        sizer_base.Add(self.panel, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()        
        
        wx.CallAfter(self.Refresh)
        
        
        
        

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

class Impression():
    def __init__(self, liste_labelsColonnes=[], listeValeurs=[], listeSelections=[]):
        """ Imprime la liste de personnes """
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.units import inch, cm
        from reportlab.lib.pagesizes import A4, portrait, landscape
        from reportlab.lib import colors
        
        hauteur_page = defaultPageSize[0]
        largeur_page = defaultPageSize[1]
        largeur_ligne = largeur_page - (75 * 2)

        # Initialisation du PDF
        nomDoc = UTILS_Fichiers.GetRepTemp("liste_candidatures.pdf")
        if "win" in sys.platform : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=landscape(A4))
        story = []

        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (620, 100) )
        dateDuJour = DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Liste des candidatures"), _(u"Edité le %s") % dateDuJour )  )
        style = TableStyle([
                            ('BOX', (0,0), (-1,-1), 0.25, colors.black), 
                            ('VALIGN', (0,0), (-1,-1), 'TOP'), 
                            ('ALIGN', (0,0), (0,0), 'LEFT'), 
                            ('FONT',(0,0),(0,0), "Helvetica-Bold", 16), 
                            ('ALIGN', (1,0), (1,0), 'RIGHT'), 
                            ('FONT',(1,0),(1,0), "Helvetica", 6), 
                            ])
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(style)
        story.append(tableau)
        story.append(Spacer(0,20))       
        
        # Tableau de données
        dataTableau = []
        
        # Création des colonnes
        largeursColonnes = []
        labelsColonnes = []

        index = 0
        for labelCol, alignement, largeur, nomChamp in liste_labelsColonnes :
            if largeur == 0 : largeur = 30
            largeursColonnes.append(largeur/2*1.6)
            labelsColonnes.append(labelCol)
            index += 1
        dataTableau.append(labelsColonnes)
        
        # Création des lignes
        for valeurs in listeValeurs :
            ligne = []
            if int(valeurs[0]) in listeSelections :
                for valeur in valeurs :
                    ligne.append(valeur)
                dataTableau.append(ligne)
    
        # Style du tableau
        style = TableStyle([
                            ('GRID', (0,0), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
                            ('ALIGN', (0,0), (-1,-1), 'CENTRE'), # Titre du groupe à gauche
                            ('VALIGN', (0,0), (-1,-1), 'TOP'),
                            ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police 
                            ])
            
           
        # Création du tableau
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(style)
        story.append(tableau)
        story.append(Spacer(0,20))
            
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)
        


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, modeAffichage="avec_nom", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL candidatures")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
