#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import FonctionsPerso
from Utils import UTILS_Fichiers
import six
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

HAUTEUR_PAGE = 0
LARGEUR_PAGE = 0
DICT_CATEGORIES = {}
COORD_LIGNE = ()
HAUTEUR_BARRE = 15 # 15 #26
ECART_LIGNES = 5
MODE_TEXTE = 1 #2 #1

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

class Impression():
    def __init__(self, orientation, dictCategories, dictGroupes, dictLignes, listePresences, dictPresences, coordLigne, hauteur_barre, ecart_lignes, mode_texte):
        # Paramètres du PDF
        nomDoc = UTILS_Fichiers.GetRepTemp("Impression_presences_graph.pdf")
        if "win" in sys.platform : nomDoc = nomDoc.replace("/", "\\")
        
        # Initialisation des valeurs
        global DICT_CATEGORIES, HAUTEUR_BARRE, ECART_LIGNES, MODE_TEXTE, COORD_LIGNE
        DICT_CATEGORIES = dictCategories
        HAUTEUR_BARRE = hauteur_barre
        ECART_LIGNES = ecart_lignes
        MODE_TEXTE = mode_texte
        COORD_LIGNE =  coordLigne
        
        # Initialisation du PDF
        global HAUTEUR_PAGE, LARGEUR_PAGE
        if orientation == "portrait" : 
            taillePage = portrait(A4)
            HAUTEUR_PAGE = defaultPageSize[1]
            LARGEUR_PAGE = defaultPageSize[0]
        else:
            taillePage = landscape(A4)
            HAUTEUR_PAGE = defaultPageSize[0]
            LARGEUR_PAGE = defaultPageSize[1]
        
        doc = SimpleDocTemplate(nomDoc, pagesize=taillePage)
        story = []
        
        # Création des lignes        
        for IDgroupe, valeurs in dictGroupes.items() :
            titreGroupe, posY_debut, posY_fin, nbreLignes, listeLignes = valeurs
            
            # Création du titre du groupe
            styleSheet = getSampleStyleSheet()
            labelGroupe = LabelGroupe(0, 30, titreGroupe)
            story.append(labelGroupe)
            story.append(Spacer(0,10))
            
            # Création des lignes du groupe
            for IDpersonneLigne, dateLigne, xxx, labelLigne in listeLignes :
                # Recherche des barres de la ligne
                listeBarresLigne = []
                for IDpresence, IDpersonne, date, heureDebut, heureFin, IDcategorie, intitule, posG, posD, posYhaut, posYbas in listePresences :
                    if (IDpersonne == IDpersonneLigne) and (date == dateLigne) :
                        # Création de la barre
                        listeBarresLigne.append((IDpresence, IDpersonne, date, heureDebut, heureFin, IDcategorie, intitule, posG, posD, posYhaut, posYbas))
                
                ligne = Ligne(0, HAUTEUR_BARRE -3 + ECART_LIGNES, labelLigne, listeBarresLigne)
                story.append(ligne)
            
            # Espace après le groupe
            story.append(Spacer(0,20))
            
        # Légendes des catégories
        story.append(Spacer(0,10))
        nbre_legendes = 0
        total_heures = 0
        for key, valeurs in dictCategories.items() :
            nom, IDcat_parent, ordre, couleur, nbreHeures = valeurs
            if nbreHeures != 0 :
                legende = Legende(0, 15, nom, couleur, nbreHeures)
                story.append(legende)
                nbre_legendes += 1
                total_heures += nbreHeures
        if nbre_legendes > 1 :
            # Ajoute un total d'heures
            legende = Legende(0, 15, _(u"Total"), None, total_heures)
            story.append(legende)
        
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)


class Ligne(Flowable) :
    """ Flowable LIGNE qui peut rassembler plusieurs barres """
    def __init__(self, xoffset=0, size=None, labelLigne="", listeBarresLigne=[]):
        # size = hauteur du flowable
        self.xoffset = xoffset
        self.size = size
        self.labelLigne = labelLigne
        self.listeBarresLigne = listeBarresLigne
    
    def wrap(self, *args):
        return (self.xoffset, self.size)
    
    def draw(self):
        canvas = self.canv
        if type(self.labelLigne) != six.text_type :
            self.labelLigne = self.labelLigne.decode("iso-8859-15")
        canvas.setFont("Helvetica", 9)
        # Dessin du label de la ligne
        xRightLabel = COORD_LIGNE[0] - 10
        yBasLabel = 0
        if MODE_TEXTE == 2 : yBasLabel = yBasLabel + 6
        canvas.drawRightString(xRightLabel, yBasLabel + 3, self.labelLigne)
        
        # Dessin test de la ligne totale
##        canvas.rect(COORD_LIGNE[0], 0, COORD_LIGNE[1]-COORD_LIGNE[0], 10)
        tailleVirtuelleLigne = COORD_LIGNE[1]-COORD_LIGNE[0]
        largeurMargesFeuille = 75
        posXGaucheLigne = COORD_LIGNE[0]
        taillePapierLigne = LARGEUR_PAGE- (largeurMargesFeuille*2) - posXGaucheLigne
        facteurAgrandissement = (taillePapierLigne *1.0) / tailleVirtuelleLigne
        # Dessine la ligne
##        canvas.setFillColorRGB(0.9, 0.9, 0.5)
##        canvas.rect(COORD_LIGNE[0], 0, taillePapierLigne, HAUTEUR_BARRE, fill=0)
        
        # Dessin de toutes les barres de la ligne
        for barre in self.listeBarresLigne :
            IDpresence, IDpersonne, date, heureDebut, heureFin, IDcategorie, intitule, posG, posD, posYhaut, posYbas = barre
            x = posG
            y = 0
            largeur = posD - posG
            hauteur = HAUTEUR_BARRE - 3
            label = intitule
            self.Barre(canvas, x, y, largeur, hauteur, label, heureDebut, heureFin, IDcategorie, facteurAgrandissement)
    
    def Barre(self, canvas, x, y, largeur, hauteur, label, heureDebut, heureFin, IDcategorie, facteurAgrandissement):
        # Dessin d'une barre       
        x = ((x-COORD_LIGNE[0]) * facteurAgrandissement) + COORD_LIGNE[0]
        largeur = largeur * facteurAgrandissement
        paddingTexte = 3
        nom, IDcat_parent, ordre, couleur, totalHeures = DICT_CATEGORIES[IDcategorie]
        r, g, b = ConvertCouleur(FormateCouleur(couleur))
        canvas.setFillColorRGB(r, g, b)
        canvas.rect(x, y, largeur, hauteur, fill=1)
        canvas.setFillColorRGB(0, 0, 0)
        canvas.setFont("Helvetica", 8)
        # Dessin des heures
        if MODE_TEXTE == 2 : y = y + 10
        heureDebut = str(heureDebut)[0:2] + "h" + str(heureDebut)[3:5]
        canvas.drawString(x + paddingTexte, y + paddingTexte, heureDebut)
        heureFin = str(heureFin)[0:2] + "h" + str(heureFin)[3:5]
        canvas.drawRightString(largeur + x - paddingTexte, y + paddingTexte, heureFin)
        # Dessin de l'intitulé
        if MODE_TEXTE == 2 and label != "" :
            canvas.drawString(x + paddingTexte, y + paddingTexte - 10, label)


class Legende(Flowable) :
    """ Flowable Ligne de légende """
    def __init__(self, xoffset=0, size=None, label="", couleur=None, totalHeures=0):
        self.xoffset = xoffset
        self.size = size
        self.label = label
        self.couleur = couleur
        self.totalHeures = totalHeures
    def wrap(self, *args):
        return (self.xoffset, self.size)
    def draw(self):
        canvas = self.canv
        # Texte label
        canvas.setFillColorRGB(0, 0, 0)
        canvas.setFont("Helvetica", 9)
        canvas.drawString(15, 1, "%s : %s" % (self.label, minutesEnHeures(self.totalHeures)))
        # Carré de couleur
        if self.couleur != None :
            r, g, b = ConvertCouleur(FormateCouleur(self.couleur))
            canvas.setFillColorRGB(r, g, b)
            canvas.rect(0, 0, 10, 10, fill=1)
        

class LabelGroupe(Flowable) :
    """ Flowable Titre de groupe """
    def __init__(self, xoffset=0, size=None, label=""):
        self.xoffset = xoffset
        self.size = size
        self.label = label
    def wrap(self, *args):
        return (self.xoffset, self.size)
    def draw(self):
        canvas = self.canv
        if type(self.label) != six.text_type :
            self.label = self.label.decode("iso-8859-15")
        # Texte label
        canvas.setFillColorRGB(0, 0, 0)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(35, 0, self.label)
        # Ligne noire
        tailleLigne = LARGEUR_PAGE- (75*2)
        largeurLabel =  canvas.stringWidth(self.label, "Helvetica-Bold", 11)
        canvas.line(0, 3, 30, 3)
        canvas.line(largeurLabel + 10 + 30, 3, tailleLigne, 3)
        canvas.rect(30, -3, largeurLabel+10, 13, fill=0)
        canvas.line(0, 3.5, 0, -8)
        
        