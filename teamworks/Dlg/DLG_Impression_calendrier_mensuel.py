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
import datetime
import time
import calendar
import FonctionsPerso
import GestionDB
from Utils import UTILS_Fichiers

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import A4, portrait, landscape
from reportlab.lib import colors
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas
from reportlab.lib.styles import PropertySet, getSampleStyleSheet, ParagraphStyle

import os
import sys


DICT_CATEGORIES = {}
LISTE_VACANCES = {}
LISTE_FERIES = {}

COULEUR_WE = (230, 230, 230)  
COULEUR_VACANCES = (255, 255, 220)
COULEUR_FERIES = (180, 180, 180)

AFFICHER_WE = True
AFFICHER_VACANCES = True
AFFICHER_FERIES = True
AFFICHER_HEURES = True
AFFICHER_COULEUR_CATEGORIES = True
AFFICHER_LEGENDE = True
AFFICHER_HEURES_MOIS = True


def StrEnDatetimeDate(texteDate):
    annee = texteDate[:4]
    mois = texteDate[5:7]
    jour = texteDate[8:10]
    date = datetime.date(int(annee), int(mois), int(jour))
    return date

def HeureStrEnDatetime(texteHeure):
    texteHeure = texteHeure[:5]
    posTemp = texteHeure.index(":")
    heuresTemp = int(texteHeure[:posTemp])
    minutesTemp =  int(texteHeure[posTemp+1:])
    heure = datetime.time(heuresTemp, minutesTemp)
    return heure

def DatetimeDateEnStr(date):
    """ Transforme un datetime.date en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = ("Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche")
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateStr = listeJours[date.weekday()] + " " + str(date.day) + " " + listeMois[date.month-1] + " " + str(date.year)
    return dateStr

def FormateCouleur(texte):
    pos1 = texte.index(",")
    pos2 = texte.index(",", pos1+1)
    r = int(texte[1:pos1])
    v = int(texte[pos1+2:pos2])
    b = int(texte[pos2+2:-1])
    return (r, v, b)
    
def ConvertCouleur(couleur):
    r, g, b = couleur
    return r/255.0, g/255.0, b/255.0

def minutesEnHeures(dureeMinutes) :
    if dureeMinutes != 0 :
        nbreHeures = dureeMinutes/60
        nbreMinutes = dureeMinutes-(nbreHeures*60)
        if len(str(nbreMinutes))==1 : nbreMinutes = str("0") + str(nbreMinutes)
        duree = str(nbreHeures) + "h" + str(nbreMinutes)
    else:
        duree = ""
    return duree

def ImportPersonnes(annee, mois):
    date_debut = "%d-%02d-01" % (annee, mois)
    date_fin = "%d-%02d-31" % (annee, mois)
    DB = GestionDB.DB()
    req = """
    SELECT Count(presences.date) AS nbreDates, presences.IDpersonne, personnes.nom, personnes.prenom
    FROM presences INNER JOIN personnes ON presences.IDpersonne = personnes.IDpersonne
    WHERE date>='%s' AND date<='%s'
    GROUP BY presences.IDpersonne
    ORDER BY nom, prenom;""" % (date_debut, date_fin)
    DB.ExecuterReq(req)
    listePersonnes = DB.ResultatReq()
    DB.Close()
    dictPersonnes = {}
    for nbreDates, IDpersonne, nom, prenom in listePersonnes :
        dictPersonnes[IDpersonne] = { "nom" : nom, "prenom" : prenom, "nbreDates" : nbreDates }
    return dictPersonnes
        

        
class Impression():
    def __init__(self, annee=2009, mois=12, listeIDpersonnes = [], dictPersonnes = {},
                            afficher_we=True, afficher_vacances=True, afficher_feries=True,
                            afficher_heures=True, afficher_couleurs_categories=True, 
                            afficher_legende=True, afficher_heures_mois=True):
        
        self.annee = annee
        self.mois = mois
        self.listeIDpersonnes = listeIDpersonnes
        self.dictPersonnes = dictPersonnes

        listeMois = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))
        listeJours = (u"L", u"M", u"M", u"J", u"V", u"S", u"D")
        
        global AFFICHER_WE, AFFICHER_VACANCES, AFFICHER_FERIES, AFFICHER_HEURES, AFFICHER_COULEUR_CATEGORIES, AFFICHER_LEGENDE, AFFICHER_HEURES_MOIS
        AFFICHER_WE = afficher_we
        AFFICHER_VACANCES = afficher_vacances
        AFFICHER_FERIES = afficher_feries
        AFFICHER_HEURES = afficher_heures
        AFFICHER_COULEUR_CATEGORIES = afficher_couleurs_categories
        AFFICHER_LEGENDE = afficher_legende
        AFFICHER_HEURES_MOIS = afficher_heures_mois
        
        # Paramètres du PDF
        nomDoc = UTILS_Fichiers.GetRepTemp("Impression_calendrier_mensuel.pdf")
        if "win" in sys.platform : nomDoc = nomDoc.replace("/", "\\")        
        taillePage = landscape(A4)
        HAUTEUR_PAGE = defaultPageSize[0]
        LARGEUR_PAGE = defaultPageSize[1]
        
        doc = SimpleDocTemplate(nomDoc, pagesize=taillePage, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
        story = []
        
        # Création du titre du document
        largeursColonnesTitre = ( (630, 100) )
        dateDuJour = DatetimeDateEnStr(datetime.date.today())
        dataTableauTitre = [(_(u"Planning de %s %d") % (listeMois[self.mois-1], self.annee), _(u"Edité le %s") % dateDuJour ),]
        styleTitre = TableStyle([
                            ('BOX', (0,0), (-1,-1), 0.25, colors.black), 
                            ('VALIGN', (0,0), (-1,-1), 'TOP'), 
                            ('ALIGN', (0,0), (0,0), 'LEFT'), 
                            ('FONT',(0,0),(0,0), "Helvetica-Bold", 16), 
                            ('ALIGN', (1,0), (1,0), 'RIGHT'), 
                            ('FONT',(1,0),(1,0), "Helvetica", 6), 
                            ])
        tableauTitre = Table(dataTableauTitre, largeursColonnesTitre)
        tableauTitre.setStyle(styleTitre)
        story.append(tableauTitre)
        story.append(Spacer(0,20))  
        
        # Récupération des données
##        self.dictPersonnes = ImportPersonnes(annee, mois)
        self.dictPresences, self.dictTotauxCategories = self.ImportPresences(self.annee, self.mois) 
        nbrePersonnes = len(self.listeIDpersonnes)
        
        global DICT_CATEGORIES, LISTE_VACANCES, LISTE_FERIES
        DICT_CATEGORIES = self.ImportCategories()
        LISTE_VACANCES = self.Importation_Vacances()
        LISTE_FERIES = self.Importation_Feries()
        
        # Création du tableau
        dataTableau = []
        enteteTableau = []
        largeursColonnes = []
        styleTableau = []
        
        # Création de l'entete du tableau
        numWeekDay, nbreJoursMois = calendar.monthrange(self.annee, self.mois)
        numJourSemaine = numWeekDay
        
        largeurColonnes = 19
        largeurColonneTotal = 25
        largeurColonneNom = 730-(largeurColonnes*nbreJoursMois+1)-largeurColonneTotal
        
        # Colonne Nom personne
        largeursColonnes.append(largeurColonneNom)
        enteteTableau.append(u"")
        # Colonnes Dates
        for numJour in range(1, nbreJoursMois+1):
            largeursColonnes.append(largeurColonnes)
            labelColonne = u"%s %d" % (listeJours[numJourSemaine], numJour)
            dateDD = datetime.date(year=self.annee, month=self.mois, day=numJour)
            case = CaseDate(xoffset=0, hauteurCase=12, largeurCase=largeurColonnes, dateDD=dateDD, dictBarres={}, labelDate=labelColonne )
            enteteTableau.append(case)
            numJourSemaine += 1
            if numJourSemaine == 7 : 
                numJourSemaine = 0
        # Colonne Total mois
        largeursColonnes.append(largeurColonneTotal)
        enteteTableau.append(_(u"Total"))
            
        dataTableau.append(enteteTableau)
        styleTableau.append(('ALIGN', (0, 0), (-1, 0), 'CENTRE')) 
        styleTableau.append(('FONT', (0, 0), (-1, 0), "Helvetica-Bold", 8))
        
        # Création des lignes vides
        for IDpersonne in self.listeIDpersonnes :
            # Entete ligne
            nom = self.dictPersonnes[IDpersonne]["nom"]
            prenom = self.dictPersonnes[IDpersonne]["prenom"]
            nomComplet = u"%s %s  " % (nom, prenom)
            ligne = [nomComplet,]
            # Cases dates
            totalMinutesMois = 0
            for numJour in range(1, nbreJoursMois+1) :
                dateDD = datetime.date(year=self.annee, month=self.mois, day=numJour)
                if self.dictPresences[IDpersonne].has_key(dateDD) :
                    totalMinutesMois += self.dictPresences[IDpersonne][dateDD]["totalJour"]
                    dictBarres = self.dictPresences[IDpersonne][dateDD]
                    case = CaseDate(xoffset=0, hauteurCase=12, largeurCase=largeurColonnes, dateDD=dateDD, dictBarres=dictBarres )
                    ligne.append(case)
                else:
                    ligne.append(None)
            # Colonne Total Mois
            if AFFICHER_HEURES_MOIS == True and totalMinutesMois != 0 :
                total = minutesEnHeures(totalMinutesMois)
                ligne.append(total)
            dataTableau.append(ligne)
        
        # Style général du tableau
        styleTableau.append(('FONT', (0, 1), (-1, -1), "Helvetica", 6))
        styleTableau.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
        styleTableau.append(('RIGHTPADDING', (0, 0), (-1, -1), 0))
        styleTableau.append(('TOPPADDING', (0, 0), (-1, -1), 0))
        styleTableau.append(('BOTTOMPADDING', (0, 0), (-1, -1), 0))
        styleTableau.append(('ALIGN', (0, 0), (0, -1), "RIGHT"))
        styleTableau.append(('VALIGN', (0, 0), (0, -1), "MIDDLE"))
        styleTableau.append(('GRID', (1, 0), (-1, 0), 0.25, colors.black))
        styleTableau.append(('GRID', (0, 1), (-1, -1), 0.25, colors.black))
        
        styleTableau.append(('ALIGN', (-1, 0), (-1, -1), "CENTRE"))
        styleTableau.append(('VALIGN', (-1, 0), (-1, -1), "MIDDLE"))
        styleTableau.append(('FONT', (-1, 0), (-1, -1), "Helvetica", 5))
        
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(TableStyle(styleTableau))
        story.append(tableau)
        story.append(Spacer(0, 25))


        #------------------LEGENDE-------------------
        
        # Légendes des catégories
        dataTableauLegende = []
        largeursColonnesLegende = []
        styleTableauLegende = []
        
        # Création des lignes vides du tableau des légendes
        nbreLignesLegendes = 5
        nbreColonnesLegendes = 4
        largeurColonneLegende = 178.75
        
        for numLigne in range(0, nbreLignesLegendes) :
            ligne = []
            for numCol in range (0, nbreColonnesLegendes):
                ligne.append(None)
            dataTableauLegende.append(ligne)
        
        # Création de la liste des largeurs des colonnes
        for x in range(0, nbreColonnesLegendes):
            largeursColonnesLegende.append(largeurColonneLegende)
            
        # Remplissage du tableau des légendes
        nbre_legendes = 0
        total_heures = 0
        numLigne = 0
        numCol = 0
        
        if AFFICHER_VACANCES == True :
            dataTableauLegende[numLigne][numCol] = CaseLegende(0, 10, _(u"Vacances"), COULEUR_VACANCES, None)
            numLigne += 1
        if AFFICHER_WE == True :
            dataTableauLegende[numLigne][numCol] = CaseLegende(0, 10, _(u"Week-ends"), COULEUR_WE, None)
            numLigne += 1
        if AFFICHER_FERIES == True :
            dataTableauLegende[numLigne][numCol] = CaseLegende(0, 10, _(u"Jours fériés"), COULEUR_FERIES, None)
            numLigne += 1
        
        for IDcategorie, nbreHeures in self.dictTotauxCategories.iteritems() :
            if IDcategorie != "totalMois" :
                nom_categorie, ordre, couleur = DICT_CATEGORIES[IDcategorie]
                legende = CaseLegende(0, 10, nom_categorie, couleur, nbreHeures)
                dataTableauLegende[numLigne][numCol] = legende
                nbre_legendes += 1
                total_heures += nbreHeures
                
                numLigne += 1
                if numLigne == nbreLignesLegendes :
                    numLigne = 0
                    numCol += 1

        if nbre_legendes > 1 :
            # Ajoute un total d'heures pour l'année
            legende = CaseLegende(0, 10, _(u"Total pour le mois"), None, total_heures)
            dataTableauLegende[numLigne][numCol] = legende
        
        styleTableauLegende.append(('FONT', (0, 1), (-1, -1), "Helvetica", 6))
        styleTableauLegende.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
        styleTableauLegende.append(('RIGHTPADDING', (0, 0), (-1, -1), 0))
        styleTableauLegende.append(('TOPPADDING', (0, 0), (-1, -1), 0))
        styleTableauLegende.append(('BOTTOMPADDING', (0, 0), (-1, -1), 0))
        
        tableauLegende = Table(dataTableauLegende, largeursColonnesLegende)
        tableauLegende.setStyle(TableStyle(styleTableauLegende))
        if AFFICHER_LEGENDE == True :
            story.append(tableauLegende)
        
        
        # Enregistrement du PDF
        doc.build(story)
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)
        
        
    def ImportPresences(self, annee, mois):
        date_debut = "%d-%02d-01" % (annee, mois)
        date_fin = "%d-%02d-31" % (annee, mois)
        DB = GestionDB.DB()
        if len(self.listeIDpersonnes) == 1 : cond = "(%d)" % self.listeIDpersonnes[0]
        else : cond = str(tuple(self.listeIDpersonnes))
        req = """
        SELECT IDpersonne, IDpresence, date, heure_debut, heure_fin, IDcategorie 
        FROM presences 
        WHERE date>='%s' AND date<='%s' AND IDpersonne IN %s
        ORDER BY date;""" % (date_debut, date_fin, cond)
        DB.ExecuterReq(req)
        listePresences = DB.ResultatReq()
        DB.Close()
        # Création des dict de données
        dictPresences = {}
        dictTotalHeures = {}
        for IDpersonne, IDpresence, date, heure_debut, heure_fin, IDcategorie in listePresences :
            # Formatage des données
            dateDD = StrEnDatetimeDate(date)
            heure_debut = HeureStrEnDatetime(heure_debut)
            heure_fin = HeureStrEnDatetime(heure_fin)
            HMin = datetime.timedelta(hours=heure_debut.hour, minutes=heure_debut.minute)
            HMax = datetime.timedelta(hours=heure_fin.hour, minutes=heure_fin.minute)
            duree = ((HMax - HMin).seconds)/60
            # Création du dict des présences
            if dictPresences.has_key(IDpersonne) == False :
                dictPresences[IDpersonne] = {}
            if dictPresences[IDpersonne].has_key(dateDD) == False :
                dictPresences[IDpersonne][dateDD] = {"totalJour" : 0}
            if dictPresences[IDpersonne][dateDD].has_key(IDcategorie):
                dictPresences[IDpersonne][dateDD][IDcategorie] = dictPresences[IDpersonne][dateDD][IDcategorie] + duree
            else:
                dictPresences[IDpersonne][dateDD][IDcategorie] = duree
            dictPresences[IDpersonne][dateDD]["totalJour"] = dictPresences[IDpersonne][dateDD]["totalJour"] + duree

            # Création du dict des totaux par categories
            if dictTotalHeures.has_key(IDcategorie):
                dictTotalHeures[IDcategorie] = dictTotalHeures[IDcategorie] + duree
            else:
                dictTotalHeures[IDcategorie] = duree
            if dictTotalHeures.has_key("totalMois"):
                dictTotalHeures["totalMois"] = dictTotalHeures["totalMois"] + duree
            else:
                dictTotalHeures["totalMois"] = duree
            
        return dictPresences, dictTotalHeures
    
    def ImportCategories(self):
        DB = GestionDB.DB()
        req = "SELECT IDcategorie, nom_categorie, ordre, couleur FROM cat_presences"
        DB.ExecuterReq(req)
        listecategories = DB.ResultatReq()
        DB.Close()
        dictCategories = {}
        for IDcategorie, nom_categorie, ordre, couleur in listecategories :
            dictCategories[IDcategorie] = (nom_categorie, ordre, couleur) 
        return dictCategories

    def Importation_Vacances(self):
        """ Importation des dates de vacances """
        req = "SELECT * FROM periodes_vacances ORDER BY date_debut;"
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeVacances1 = DB.ResultatReq()
        DB.Close()
        listeVacances2 = []
        for id, nom, annee, date_debut, date_fin in listeVacances1 :
            datedebut = datetime.date(int(date_debut[:4]), int(date_debut[5:7]), int(date_debut[8:10]))
            datefin = datetime.date(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]))
            listeVacances2.append(datedebut)
            for x in range((datefin-datedebut).days) :
                datedebut = datedebut + datetime.timedelta(days=1) 
                listeVacances2.append(datedebut)
        return listeVacances2
    
    def Importation_Feries(self):
        """ Importation des dates de vacances """
        req = "SELECT * FROM jours_feries WHERE (annee=0 OR annee=%d);" % self.annee
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeFeriesTmp = DB.ResultatReq()
        DB.Close()
        listeFeries = []
        for ID, type, nom, jour, mois, annee in listeFeriesTmp :
            if type =="fixe" :
                date = datetime.date(self.annee, mois, jour)
            else:
                date = datetime.date(annee, mois, jour)
            listeFeries.append(date)
        return listeFeries




class CaseDate(Flowable) :
    """ Flowable Case d'une date """
    def __init__(self, xoffset=0, hauteurCase=None, largeurCase=0, dateDD=None, dictBarres={}, labelDate="" ):
        self.xoffset = xoffset
        self.size = hauteurCase
        self.hauteurCase = hauteurCase
        self.largeurCase = largeurCase
        self.dateDD = dateDD
        self.dictBarres = dictBarres
        self.labelDate = labelDate
        
    def wrap(self, *args):
        return (self.xoffset, self.size)
    
    def draw(self):
        canvas = self.canv
        couleurDate = None
        
        if self.dateDD != None :
            # Couleur de la case Date de la journée
            if AFFICHER_VACANCES == True and self.dateDD in LISTE_VACANCES : couleurDate = COULEUR_VACANCES
            if AFFICHER_WE == True and (self.dateDD.weekday() == 5 or self.dateDD.weekday() == 6) : couleurDate = COULEUR_WE
            if AFFICHER_FERIES == True and self.dateDD in LISTE_FERIES : couleurDate = COULEUR_FERIES
            if couleurDate != None and len(self.dictBarres) == 0 :
                r, g, b = ConvertCouleur(couleurDate)
                canvas.setFillColorRGB(r, g, b)
                canvas.rect(-9.5, 0, self.largeurCase, self.hauteurCase, fill=1, stroke=False)
        
        # Texte date
        if self.labelDate != "" :
            canvas.setFillColorRGB(0, 0, 0)
            canvas.setFont("Helvetica", 7)
            canvas.drawCentredString( 0, 3, self.labelDate)
                
        # Si aucune présence ce jour -là
        if len(self.dictBarres) == 0 : return

        # Récup du nbre total d'heure de la journée
        totalJour = self.dictBarres["totalJour"]
        
        # Transformation du nombre d'heures par catégorie en pourcentage
        listeCategories = []
        for IDcategorie, nbreHeures in self.dictBarres.iteritems():
            if IDcategorie != "totalJour" :
                largeurBarre = nbreHeures * 1.0 * self.largeurCase / totalJour
                listeCategories.append( (largeurBarre, IDcategorie) )
        listeCategories.sort()
        
        # Création des graphes
        if AFFICHER_COULEUR_CATEGORIES == True :
            positionTemp = 0
            for largeurBarre, IDcategorie in listeCategories :
                r, g, b = ConvertCouleur(FormateCouleur(DICT_CATEGORIES[IDcategorie][2]))
                canvas.setFillColorRGB(r, g, b)
                canvas.rect(positionTemp, 0, largeurBarre, self.hauteurCase, fill=1, stroke=False)
                positionTemp += largeurBarre
        
        # Label Total Heure de la journée
        if AFFICHER_HEURES == True :
            canvas.setFillColorRGB(0, 0, 0)
            canvas.setFont("Helvetica", 5)
            canvas.drawRightString(self.largeurCase-2, 3.6, "%s" % minutesEnHeures(totalJour))


class CaseLegende(Flowable) :
    """ Flowable Ligne de légende """
    def __init__(self, xoffset=0, hauteurCase=None, label="", couleur=None, totalHeures=0):
        self.xoffset = xoffset
        self.size = hauteurCase
        self.hauteurCase = hauteurCase
        self.label = label
        self.couleur = couleur
        self.totalHeures = totalHeures
    def wrap(self, *args):
        return (self.xoffset, self.size)
    def draw(self):
        canvas = self.canv
        # Texte label
        canvas.setFillColorRGB(0, 0, 0)
        canvas.setFont("Helvetica", 8)
        if self.totalHeures == None :
            canvas.drawString(15, 2, self.label)
        else:
            canvas.drawString(15, 2, "%s : %s" % (self.label, minutesEnHeures(self.totalHeures)))
        # Carré de couleur
        if self.couleur != None :
            if type(self.couleur) == tuple :
                r, g, b = ConvertCouleur(self.couleur)
            else:
                r, g, b = ConvertCouleur(FormateCouleur(self.couleur))
            canvas.setLineWidth(0.25)
            canvas.setFillColorRGB(r, g, b)
            canvas.rect(0, 0, 10, 10, fill=1)

        
# ----------------------------------------------------------------------------------------------------------------------


class MyDialog(wx.Dialog):
    """ Permet de sélectionner les paramètres d'affichage du calendrier mensuel """
    def __init__(self, parent, IDpersonne=None, annee=None, mois=None, autoriser_choix_personne=True):
        wx.Dialog.__init__(self, parent, id=-1, title=_(u"Edition d'un planning mensuel"), size=(350, 300))
                
        # Label
        self.label = wx.StaticText(self, -1, _(u"Veuillez renseigner les paramètres de votre choix :"))
        
        # Controles
        self.staticbox1 = wx.StaticBox(self, -1, _(u"Paramètres principaux"))
        self.label_nom = wx.StaticText(self, -1, _(u"Mois :"))
        self.ctrl_mois = MyChoice(self)
        if mois == None : mois = datetime.date.today().month
        self.ctrl_mois.SetSelection(mois-1)
        self.label_annee = wx.StaticText(self, -1, _(u"Année :"))
        self.ctrl_annee = wx.SpinCtrl(self, -1, "", size=(60, -1))
        self.ctrl_annee.SetRange(1970, 2099)
        if annee == None : annee = datetime.date.today().year
        self.ctrl_annee.SetValue(annee)
        self.ctrl_personnes = MyCheckListBox(self, size=(-1, 90))
        
        self.staticbox2 = wx.StaticBox(self, -1, _(u"Options d'affichage"))
        self.ctrl_afficher_we = wx.CheckBox(self, -1, _(u"Activer la coloration des week-ends"))
        self.ctrl_afficher_vacances = wx.CheckBox(self, -1, _(u"Activer la coloration des vacances"))
        self.ctrl_afficher_feries = wx.CheckBox(self, -1, _(u"Activer la coloration des jours fériés"))
        self.ctrl_afficher_heures = wx.CheckBox(self, -1, _(u"Afficher le total d'heures journalier"))
        self.ctrl_afficher_heures_mois = wx.CheckBox(self, -1, _(u"Afficher le total d'heures mensuel"))
        self.ctrl_afficher_couleurs_categories = wx.CheckBox(self, -1, _(u"Activer la coloration des catégories de présence"))
        self.ctrl_afficher_legende = wx.CheckBox(self, -1, _(u"Afficher la légende des couleurs"))
        self.ctrl_afficher_we.SetValue(True)
        self.ctrl_afficher_vacances.SetValue(True)
        self.ctrl_afficher_feries.SetValue(True)
        self.ctrl_afficher_heures.SetValue(True)
        self.ctrl_afficher_heures_mois.SetValue(True)
        self.ctrl_afficher_couleurs_categories.SetValue(True)
        self.ctrl_afficher_legende.SetValue(True)
        
        # Boutons
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage=Chemins.GetStaticPath("Images/32x32/Apercu.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CHOICE, self.OnChoixAnnee, self.ctrl_mois)
        self.Bind(wx.EVT_SPINCTRL, self.OnChoixMois, self.ctrl_annee)
        
        self.MAJCtrlPersonnes()
        

    def __set_properties(self):
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.ctrl_mois.SetToolTipString(_(u"Sélectionnez un mois de référence dans cette liste"))
        self.ctrl_annee.SetToolTipString(_(u"Saisissez une année de référence"))
        self.ctrl_afficher_we.SetToolTipString(_(u"Cette option colore les week-ends"))
        self.ctrl_afficher_vacances.SetToolTipString(_(u"Cette option colore les périodes de vacances"))
        self.ctrl_afficher_feries.SetToolTipString(_(u"Cette option colore les jours fériés"))
        self.ctrl_afficher_heures.SetToolTipString(_(u"Cette option affiche le total d'heures journalier"))
        self.ctrl_afficher_heures_mois.SetToolTipString(_(u"Cette option affiche le total d'heures mensuel"))
        self.ctrl_afficher_couleurs_categories.SetToolTipString(_(u"Cette option affiche les catégories de tâches"))
        self.ctrl_afficher_legende.SetToolTipString(_(u"Cette option affiche la légende des couleurs"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label, 0, wx.ALL, 10)
        
        sizerStaticBox1 = wx.StaticBoxSizer(self.staticbox1, wx.HORIZONTAL)
        grid_sizer_contenu1 = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        
        grid_sizer_contenu21 = wx.FlexGridSizer(rows=2, cols=4, vgap=5, hgap=5)
        grid_sizer_contenu21.Add(self.label_nom, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_contenu21.Add(self.ctrl_mois, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_contenu21.Add(self.label_annee, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 0)
        grid_sizer_contenu21.Add(self.ctrl_annee, 0, wx.ALL, 0)
        grid_sizer_contenu21.AddGrowableCol(1)
        
        grid_sizer_contenu1.Add(grid_sizer_contenu21, 0, wx.ALL, 2)
        grid_sizer_contenu1.Add(self.ctrl_personnes, 0, wx.EXPAND|wx.ALL, 2)
        grid_sizer_contenu1.AddGrowableCol(0)
        
        sizerStaticBox1.Add(grid_sizer_contenu1, 1, wx.EXPAND|wx.ALL, 5)
        
        
        grid_sizer_base.Add(sizerStaticBox1, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
        sizerStaticBox2 = wx.StaticBoxSizer(self.staticbox2, wx.HORIZONTAL)
        grid_sizer_contenu2 = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_contenu2.Add(self.ctrl_afficher_we, 1, wx.EXPAND|wx.ALL, 2)
        grid_sizer_contenu2.Add(self.ctrl_afficher_vacances, 1, wx.EXPAND|wx.ALL, 2)
        grid_sizer_contenu2.Add(self.ctrl_afficher_feries, 1, wx.EXPAND|wx.ALL, 2)
        grid_sizer_contenu2.Add(self.ctrl_afficher_heures, 1, wx.EXPAND|wx.ALL, 2)
        grid_sizer_contenu2.Add(self.ctrl_afficher_heures_mois, 1, wx.EXPAND|wx.ALL, 2) 
        grid_sizer_contenu2.Add(self.ctrl_afficher_couleurs_categories, 1, wx.EXPAND|wx.ALL, 2)
        grid_sizer_contenu2.Add(self.ctrl_afficher_legende, 1, wx.EXPAND|wx.ALL, 2)
        grid_sizer_contenu2.AddGrowableCol(0)
        sizerStaticBox2.Add(grid_sizer_contenu2, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(sizerStaticBox2, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()
    
    def OnChoixAnnee(self, event):
        self.MAJCtrlPersonnes() 
        
    def OnChoixMois(self, event):
        self.MAJCtrlPersonnes()     

    def MAJCtrlPersonnes(self):
        annee = self.GetAnnee()
        mois = self.GetMois()
        self.ctrl_personnes.RemplitCtrlPersonnes(annee, mois)
    
    def GetMois(self):
        return self.ctrl_mois.GetSelection()+1
    
    def GetAnnee(self):
        return self.ctrl_annee.GetValue()
        
    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        annee = self.GetAnnee()
        mois = self.GetMois()
        listeIDpersonnes = self.ctrl_personnes.GetListIDpersonnes()
        dictPersonnes = self.ctrl_personnes.dictPersonnes
        if len(listeIDpersonnes) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins une personne présente durant ce mois !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return   
        Impression( annee=annee, mois=mois, listeIDpersonnes=listeIDpersonnes, dictPersonnes=dictPersonnes,
                        afficher_we=self.ctrl_afficher_we.GetValue(), 
                        afficher_vacances=self.ctrl_afficher_vacances.GetValue(), 
                        afficher_feries=self.ctrl_afficher_feries.GetValue(),
                        afficher_heures=self.ctrl_afficher_heures.GetValue(), 
                        afficher_couleurs_categories=self.ctrl_afficher_couleurs_categories.GetValue(), 
                        afficher_legende=self.ctrl_afficher_legende.GetValue(),
                        afficher_heures_mois=self.ctrl_afficher_heures_mois.GetValue()
                        )
        #self.EndModal(wx.ID_OK)
    



class MyChoice(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, size=(-1, -1), choices=(_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre")))
        self.dictIndexes = {}
        self.Select(0)
        
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
        self.Select(0)
                
    def GetIDselection(self):
        index = self.GetSelection()
        return self.dictIndexes[index], self.GetStringSelection()
    
    def SetIDselection(self, ID):
        for index, IDtemp in self.dictIndexes.iteritems():
            if ID == IDtemp :
                self.Select(index)
                return        
    

class MyCheckListBox(wx.CheckListBox):
    def __init__(self, parent, size=(-1, -1)):
        wx.CheckListBox.__init__(self, parent, size=size)
        self.listePersonnes = []

    def GetListePersonnes(self, annee, mois):
        dictPersonnes = ImportPersonnes(annee, mois)
        listePersonnes = []
        for IDpersonne, dictData in dictPersonnes.iteritems() :
            nomPersonne = u"%s %s" % (dictData["nom"], dictData["prenom"])
            listePersonnes.append((nomPersonne, IDpersonne))
        listePersonnes.sort()
        return listePersonnes, dictPersonnes
        
    def RemplitCtrlPersonnes(self, annee, mois):
        self.listePersonnes, self.dictPersonnes = self.GetListePersonnes(annee, mois)
        self.Clear()
        index = 0
        for nomPersonne, IDpersonne in self.listePersonnes :
            self.Append(nomPersonne)
            self.Check(index, True)
            index += 1
    
    def GetListIDpersonnes(self):
        listeID = []
        for index in self.GetChecked() :
            nomPersonne, IDpersonne = self.listePersonnes[index]
            listeID.append(IDpersonne)
        return listeID


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = MyDialog(None)
    frm.ShowModal()
    app.MainLoop()

    
    
    
