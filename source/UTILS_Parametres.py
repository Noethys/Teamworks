#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Teamworks
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import GestionDB


def Parametres(mode="get", categorie="", nom="", valeur=None, nomFichier=""):
    """ Mémorise ou récupère un paramètre quelconque dans la base de données """
    """ Le paramètre doit être str ou unicode obligatoirement """
    """ si mode = 'get' : valeur est la valeur par défaut | si mode = 'set' : valeur est la valeur à donner au paramètre """
   
    # Préparation de la valeur par défaut
    type_parametre = type(valeur)
    if type_parametre == int : valeurTmp = str(valeur)
    elif type_parametre == float : valeurTmp = str(valeur)
    elif type_parametre == str : valeurTmp = valeur
    elif type_parametre == unicode : valeurTmp = valeur
    elif type_parametre == tuple : valeurTmp = str(valeur)
    elif type_parametre == list : valeurTmp = str(valeur)
    elif type_parametre == dict : valeurTmp = str(valeur)
    elif type_parametre == bool : valeurTmp = str(valeur)
    else : valeurTmp = ""
    
    # Recherche du parametre
    DB = GestionDB.DB(nomFichier=nomFichier)
    
    # Si aucun fichier n'est chargé dans Teamworks, on renvoie la valeur par défaut :
    if DB.echec == 1 :
        return valeur

    req = u"""SELECT IDparametre, parametre FROM parametres WHERE categorie="%s" AND nom="%s" ;""" % (categorie, nom)
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    if len(listeDonnees) != 0 :
        if mode == "get" :
            # Un parametre existe :
            valeurTmp = listeDonnees[0][1]
            # On le formate pour le récupérer sous son vrai format
            if type_parametre == int : valeurTmp = int(valeurTmp)
            if type_parametre == float : valeurTmp = float(valeurTmp)
            if type_parametre == str : valeurTmp = valeurTmp
            if type_parametre == unicode : valeurTmp = valeurTmp
            if type_parametre == tuple : exec("valeurTmp = " + valeurTmp)
            if type_parametre == list : exec("valeurTmp = " + valeurTmp)
            if type_parametre == dict : exec("valeurTmp = " + valeurTmp)
            if type_parametre == bool : exec("valeurTmp = " + valeurTmp)
        else:
            # On modifie la valeur du paramètre
            IDparametre = listeDonnees[0][0]
            listeDonnees = [("categorie",  categorie), ("nom",  nom), ("parametre",  valeurTmp),]
            DB.ReqMAJ("parametres", listeDonnees, "IDparametre", IDparametre)
            valeurTmp = valeur
    else:
        # Le parametre n'existe pas, on le créé :
        listeDonnees = [("categorie",  categorie), ("nom",  nom), ("parametre",  valeurTmp),]
        newID = DB.ReqInsert("parametres", listeDonnees)
        valeurTmp = valeur
    DB.Close()
    return valeurTmp


def TestParametre(categorie="", nom="", valeur=None, nomFichier=""):
    """ Vérifie si un paramètre existe dans le fichier """
    DB = GestionDB.DB(nomFichier=nomFichier)
    req = u"""SELECT IDparametre, parametre FROM parametres WHERE categorie="%s" AND nom="%s" ;""" % (categorie, nom)
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close() 
    if len(listeDonnees) == 0 :
        return False
    else:
        return True
