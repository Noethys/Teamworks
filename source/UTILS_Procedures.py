#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Teamworks
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB

DICT_PROCEDURES = {
    "A2000" : _(u"Conversion de la version 1 à la version 2 de Teamworks"),
    }

# -------------------------------------------------------------------------------------------------------------------------

def Procedure(code=""):
    # Recherche si procédure existe
    if DICT_PROCEDURES.has_key(code) == False :
        dlg = wx.MessageDialog(None, _(u"Désolé, cette procédure n'existe pas..."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return
    titre = DICT_PROCEDURES[code]
    # Demande de confirmation de lancement
    dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment lancer la procédure suivante ?\n\n   -> %s   ") % titre, _(u"Lancement de la procédure"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
    reponse = dlg.ShowModal() 
    dlg.Destroy()
    if reponse != wx.ID_YES :
        return
    # Lancement
    print "Lancement de la procedure '%s'..." % code
    try :
        exec("%s()" % code)
    except Exception, err :
        dlg = wx.MessageDialog(None, _(u"Désolé, une erreur a été rencontrée :\n\n-> %s  ") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return
    # Fin
    dlg = wx.MessageDialog(None, _(u"La procédure s'est terminée avec succès."), _(u"Procédure terminée"), wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()
    print "Fin de la procedure '%s'." % code
    return

# -------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------

##def A3687():
##    """
##    Vérifie que le montant du QF dans la table tarifs_lignes est un float et non un unicode
##    """
##    DB = GestionDB.DB()
##    req = """SELECT IDligne, qf_min, qf_max
##    FROM tarifs_lignes; """ 
##    DB.ExecuterReq(req)
##    listeLignes = DB.ResultatReq()
##    for IDligne, qf_min, qf_max in listeLignes :
##        if type(qf_min) == unicode or type(qf_min) == str : DB.ReqMAJ("tarifs_lignes", [("qf_min", float(qf_min.replace(",","."))),], "IDligne", IDligne)
##        if type(qf_max) == unicode or type(qf_max) == str : DB.ReqMAJ("tarifs_lignes", [("qf_max", float(qf_max.replace(",","."))),], "IDligne", IDligne)
##    DB.Close()
##
##def A3688():
##    DB = GestionDB.DB()
##    DB.ReqDEL("ouvertures", "IDunite", 5)
##    DB.Close()
##
##def X1234():
##    """ Exportation des données d'une table vers la table DEFAUT """
##    # Demande le nom de la table à exporter
##    DB = GestionDB.DB()
##    listeTablesTemp = DB.GetListeTables() 
##    listeTables = []
##    for donnees in listeTablesTemp :
##        listeTables.append(donnees[0])
##    dlg = wx.MultiChoiceDialog(None, _(u"Cochez les tables à exporter :"), _(u"Exportation vers la table DEFAUT"), listeTables)
##    if dlg.ShowModal() == wx.ID_OK :
##        selections = dlg.GetSelections()
##        nomsTable = [listeTables[x] for x in selections]
##        for nomTable in nomsTable :
##            DB.Exportation_vers_base_defaut(nomTable)
##    dlg.Destroy()
##    DB.Close()
##
##def S1290():
##    """
##    Récupère le IDcategorie_tarif pour le mettre dans le nouveau champ 
##    "categories_tarifs" de la table "tarifs"
##    """
##    DB = GestionDB.DB()
##    
##    # Déplace le champ IDcategorie_tarif dans la table tarifs
##    req = """SELECT IDtarif, IDcategorie_tarif, IDnom_tarif FROM tarifs; """ 
##    DB.ExecuterReq(req)
##    listeTarifs = DB.ResultatReq()
##    for IDtarif, IDcategorie_tarif, IDnom_tarif in listeTarifs :
##        if IDcategorie_tarif != None :
##            # Remplit le nouveau champ categories_tarifs de la table Tarifs
##            DB.ReqMAJ("tarifs", [("categories_tarifs", str(IDcategorie_tarif)),], "IDtarif", IDtarif)
##            
##            # Vide le champ IDcategorie_tarif de la table Tarifs
##            DB.ReqMAJ("tarifs", [("IDcategorie_tarif", None),], "IDtarif", IDtarif)
##            
##            # Remplit le nouveau champ IDcategorie_tarif de la table Prestations
##            DB.ReqMAJ("prestations", [("IDcategorie_tarif", IDcategorie_tarif),], "IDtarif", IDtarif)
##            
##    # Recherche des noms de tarifs
##    req = """SELECT IDnom_tarif, IDactivite, IDcategorie_tarif, nom FROM noms_tarifs ORDER BY IDnom_tarif; """ 
##    DB.ExecuterReq(req)
##    listeNomsTarifs = DB.ResultatReq()
##    
##    dictDonnees = {}
##    for IDnom_tarif, IDactivite, IDcategorie_tarif, nom in listeNomsTarifs :
##
##        # Vidage du champ IDcategorie_tarif de la table noms_tarifs
##        DB.ReqMAJ("noms_tarifs", [("IDcategorie_tarif", None),], "IDnom_tarif", IDnom_tarif)
##
##        # Regroupement par activité
##        if dictDonnees.has_key(IDactivite) == False :
##            dictDonnees[IDactivite] = {}
##        
##        # Regroupement par nom de tarif
##        if dictDonnees[IDactivite].has_key(nom) == False :
##            dictDonnees[IDactivite][nom] = []
##        dictDonnees[IDactivite][nom].append(IDnom_tarif)
##    
##    # Regroupement par activités et noms de tarifs
##    for IDactivite, dictNoms in dictDonnees.iteritems() :
##        for nom, listeIDnom_tarif in dictNoms.iteritems() :
##            # Conservation du premier IDnom_tarif
##            newIDnom_tarif = listeIDnom_tarif[0]
##            
##            if len(listeIDnom_tarif) > 1 :
##                for IDnom_tarif in listeIDnom_tarif[1:] :
##                    # Suppression des IDnom_tarifs suivants
##                    DB.ReqDEL("noms_tarifs", "IDnom_tarif", IDnom_tarif)
##                    # Ré-attribution du nouvel IDnom_tarif aux tarifs
##                    DB.ReqMAJ("tarifs", [("IDnom_tarif", newIDnom_tarif),], "IDnom_tarif", IDnom_tarif)
##    
##    DB.Close()


def A2000(nomFichier):
    """ Conversion vers version 2 de Teamworks """
    import os 
    import cStringIO
    import DATA_Tables as Tables
    print "Conversion A2000 : TW1 -> TW2..."
    
    DB = GestionDB.DB(nomFichier=nomFichier)
    
    # Récupération du nom du fichier
    nomFichier = DB.nomFichierCourt
    
    # Récupération de l'IDfichier
    req = """SELECT codeIDfichier
    FROM divers WHERE IDdivers=1;"""
    DB.ExecuterReq(req)
    listeTemp = DB.ResultatReq()
    IDfichier = listeTemp[0][0]
    DB.Close()
    
    # Création du fichier PHOTOS
    print "Creation table Photos..."
    DB = GestionDB.DB(suffixe="PHOTOS", nomFichier=nomFichier, modeCreation=True)
    DB.CreationTables(Tables.DB_PHOTOS)
    DB.Close()
    
    # Création de la base DOCUMENTS
    print "Creation table Documents..."
    DB = GestionDB.DB(suffixe="DOCUMENTS", nomFichier=nomFichier, modeCreation=True)
    DB.CreationTables(Tables.DB_DOCUMENTS)
    DB.Close()

    # Récupération des photos du répertoire pour les mettre dans la table PHOTOS
    listeFichiersPhotos = os.listdir("Photos")
    DB = GestionDB.DB(suffixe="PHOTOS", nomFichier=nomFichier)
    print "Recherche et transfert des photos existantes..."
    for nomPhoto in listeFichiersPhotos :
        if IDfichier in nomPhoto and nomPhoto.endswith(".jpg") :
            IDpersonne = int(nomPhoto[len(IDfichier):-4])
            # Récupération de la photo
            img = wx.Image("Photos/%s" % nomPhoto)
            buffer = cStringIO.StringIO()
            img.SaveStream(buffer, wx.BITMAP_TYPE_JPEG)
            buffer.seek(0)
            blob = buffer.read()
            # Insertion de la photo dans la table PHOTOS
            IDphoto = DB.InsertPhoto(IDindividu=IDpersonne, blobPhoto=blob)
    DB.Close()

    print "Fin de la conversion A2000."
    
def D1051(nomFichier):
    """ Création des champs dans la table DOCUMENTS """
    DB = GestionDB.DB(suffixe="DOCUMENTS", nomFichier=nomFichier) 
    DB.AjoutChamp("documents", "type", "VARCHAR(50)")
    DB.AjoutChamp("documents", "label", "VARCHAR(400)")
    DB.AjoutChamp("documents", "IDreponse", "INTEGER")
    DB.Close()





if __name__ == _(u"__main__"):
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    # TEST D'UNE PROCEDURE :
    D1051()
    app.MainLoop()
    
    