#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

from UTILS_Traduction import _
import os
import GestionDB
import time

# Procédure automatisée de recherche des codes

listeCodes = []
listeNoms = []
listeComplete = []

def Recherche_images():
    nbre = 0
    texte = ""
    global listeCodes
    for fichier in os.listdir("Images/Drapeaux/") :
        if fichier[:-4] == "autre" : continue
        if fichier[-4:] == ".png" :
            nom = fichier[:-4].replace("_", " ")
            texte += nom + ", "
            listeCodes.append(fichier[:-4])
            nbre += 1
    print ">>>>>>", nbre, "fichiers."
    return texte

def Ecriture_fichier(txt):
    file = open("TexteCodesPays.txt", "w")
    file.write(txt)
    file.close()
    print "Fichier ecrit."

def Creation_Liste_Codes() :
    # Recherche des codes            
    texte = Recherche_images()
    # Ecriture des codes dans un fichier
    #Ecriture_fichier(texte)

# --------------------------------------------------------------

# Récupération des noms des pays

def Lecture_fichier_noms():
    file = open("TexteNomsPays.txt", "r")
    texteNoms = file.read()
    liste = texteNoms.split(", ")
    global listeNoms
    listeNoms = liste

def Creation_liste_complete():
    global listeComplete
    for index in range(len(listeCodes)) :
        listeComplete.append((listeCodes[index], listeNoms[index]))
    print listeComplete
    
def Procedure_Recuperation():
    Creation_Liste_Codes()
    Lecture_fichier_noms()
    Creation_liste_complete()
    
def Enregistrement_base() :
    DB = GestionDB.DB()
    for code, nom in listeComplete :
        listeDonnees = [("code_drapea_(u",  code), (")nom",  unicode(nom, "iso-8859-15")), ("nationalite", u"")]
        newID = DB.ReqInsert("pays", listeDonnees)
        time.sleep(0.1)
        print code
    DB.Close()
    print "Enregistrement dans la base fini !"


Procedure_Recuperation()
Enregistrement_base()