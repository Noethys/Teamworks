#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
import os
import sys
import shutil
import platform
import subprocess
from Utils import UTILS_Customize
import appdirs
import six


def GetRepData(fichier=""):
    # V�rifie si un r�pertoire 'Portable' existe
    chemin = Chemins.GetMainPath("Portable")
    if os.path.isdir(chemin):
        chemin = os.path.join(chemin, "Data")
        if not os.path.isdir(chemin):
            os.mkdir(chemin)
        return os.path.join(chemin, fichier)

    # Recherche s'il existe un chemin personnalis� dans le Customize.ini
    chemin = UTILS_Customize.GetValeur("repertoire_donnees", "chemin", "")
    #chemin = chemin.decode("iso-8859-15")
    if chemin != "" and os.path.isdir(chemin):
        return os.path.join(chemin, fichier)

    # Recherche le chemin du r�pertoire des donn�es
    if sys.platform == "win32" and platform.release() != "Vista" :

        chemin = appdirs.site_data_dir(appname=None, appauthor=False)
        #chemin = chemin.decode("iso-8859-15")

        chemin = os.path.join(chemin, "teamworks")
        if not os.path.isdir(chemin):
            os.mkdir(chemin)

    else :

        chemin = appdirs.user_data_dir(appname=None, appauthor=False)
        #chemin = chemin.decode("iso-8859-15")

        chemin = os.path.join(chemin, "teamworks")
        if not os.path.isdir(chemin):
            os.mkdir(chemin)

        chemin = os.path.join(chemin, "Data")
        if not os.path.isdir(chemin):
            os.mkdir(chemin)

    # Ajoute le dirname si besoin
    return os.path.join(chemin, fichier)


def GetRepTemp(fichier=""):
    chemin = GetRepUtilisateur("Temp")
    return os.path.join(chemin, fichier)

def GetRepUpdates(fichier=""):
    chemin = GetRepUtilisateur("Updates")
    return os.path.join(chemin, fichier)

def GetRepLang(fichier=""):
    chemin = GetRepUtilisateur("Lang")
    return os.path.join(chemin, fichier)

def GetRepSync(fichier=""):
    chemin = GetRepUtilisateur("Sync")
    return os.path.join(chemin, fichier)

def GetRepModeles(fichier=""):
    chemin = GetRepUtilisateur("Modeles")
    return os.path.join(chemin, fichier)

def GetRepEditions(fichier=""):
    chemin = GetRepUtilisateur("Editions")
    return os.path.join(chemin, fichier)

def GetRepUtilisateur(fichier=""):
    """ Recherche le r�pertoire Utilisateur pour stockage des fichiers de config et provisoires """
    chemin = None

    # V�rifie si un r�pertoire 'Portable' existe
    chemin = Chemins.GetMainPath("Portable")
    if os.path.isdir(chemin):
        return os.path.join(chemin, fichier)

    # Recherche le chemin du r�pertoire de l'utilisateur
    chemin = appdirs.user_config_dir(appname=None, appauthor=False, roaming=True)
    #chemin = chemin.decode("iso-8859-15")

    # Ajoute 'teamworks' dans le chemin et cr�ation du r�pertoire
    chemin = os.path.join(chemin, "teamworks")
    if not os.path.isdir(chemin):
        os.mkdir(chemin)

    # Ajoute le dirname si besoin
    return os.path.join(chemin, fichier)

def DeplaceFichiers():
    """ V�rifie si des fichiers du r�pertoire Data ou du r�pertoire Utilisateur sont � d�placer vers le r�pertoire Utilisateur>AppData>Roaming """

    # D�place les fichiers de config et le journal
    for nom in ("journal.log", "Config.dat", "Config.json", "Customize.ini") :
        for rep in ("", Chemins.GetMainPath("Data"), os.path.join(os.path.expanduser("~"), "teamworks")) :
            fichier = os.path.join(rep, nom)
            if os.path.isfile(fichier) :
                print(["deplacement fichier config :", fichier, " > ", GetRepUtilisateur(nom)])
                shutil.move(fichier, GetRepUtilisateur(nom))

    # D�place les fichiers xlang
    if os.path.isdir(Chemins.GetMainPath("Lang")) :
        for nomFichier in os.listdir(Chemins.GetMainPath("Lang")) :
            if nomFichier.endswith(".xlang") :
                print(["deplacement fichier xlang :", fichier, " > ", GetRepLang(nomFichier)])
                shutil.move(u"Lang/%s" % nomFichier, GetRepLang(nomFichier))

    # D�place les fichiers du r�pertoire Sync
    if os.path.isdir(Chemins.GetMainPath("Sync")) :
        for nomFichier in os.listdir(Chemins.GetMainPath("Sync")) :
            shutil.move(Chemins.GetMainPath("Sync/%s" % nomFichier), GetRepSync(nomFichier))

    # D�place les fichiers de donn�es du r�pertoire Data
    if GetRepData() != "Data/" and os.path.isdir(Chemins.GetMainPath("Data")) :
        for nomFichier in os.listdir(Chemins.GetMainPath("Data")) :
            if six.PY2:
                nomFichier = nomFichier.decode("iso-8859-15")
            if nomFichier.endswith(".dat") and "_" in nomFichier and "EXEMPLE_" not in nomFichier and "_archive.dat" not in nomFichier :
                # D�place le fichier vers le r�pertoire des fichiers de donn�es
                print(["copie base de donnees :", nomFichier, " > ", GetRepData(nomFichier)])
                shutil.copy(Chemins.GetMainPath(u"Data/%s" % nomFichier), GetRepData(nomFichier))
                # Renomme le fichier de donn�es en archive (par s�curit�)
                try :
                    os.rename(Chemins.GetMainPath(u"Data/%s" % nomFichier), Chemins.GetMainPath(u"Data/%s" % nomFichier.replace(".dat", "_archive.dat")))
                except :
                    pass

def DeplaceExemples():
    """ D�place les fichiers exemples vers le r�pertoire des fichiers de donn�es """
    # D�placement des fichiers exemples
    if GetRepData() != "Data/" :
        chemin = Chemins.GetStaticPath("Exemples")
        for nomFichier in os.listdir(chemin) :
            if nomFichier.endswith(".dat") and "Exemple_" in nomFichier :
                # D�place le fichier vers le r�pertoire des fichiers de donn�es
                shutil.copy(os.path.join(chemin, nomFichier), GetRepData(nomFichier))

    # D�placement des mod�les de documents
    chemin = Chemins.GetStaticPath("Documents")
    for nomFichier in os.listdir(chemin):
        if os.path.isfile(GetRepModeles(nomFichier)) == False:
            # Si le mod�le n'existe pas, on l'importe dans le r�pertoire Mod�les de l'utilisateur
            shutil.copy(os.path.join(chemin, nomFichier), GetRepModeles(nomFichier))




def OuvrirRepertoire(rep):
    if platform.system() == "Windows":
        subprocess.Popen(["explorer", rep])
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", rep])
    else:
        subprocess.Popen(["xdg-open", rep])



if __name__ == "__main__":
    # Teste les d�placements de fichiers
    # DeplaceFichiers()

    # R�pertoire utilisateur
    # print((GetRepUtilisateur()))

    # R�pertoire des donn�es
    # chemin = GetRepData()
    # print((1, os.path.join(chemin, u"Test�.pdf")))
    # print((2, os.path.join(chemin, "Test.pdf")))

    DeplaceExemples()