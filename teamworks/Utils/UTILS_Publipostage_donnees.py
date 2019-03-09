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
import FonctionsPerso
import datetime



NOMS_EDITION = {
    "personne" : "NOM_PRENOM*1",
    "contrat" : "NOM_PRENOM*1_DATEDEBUT_DATEFIN",
    "candidat" : "NOM_PRENOM*1",
    "candidature" : "NOM_PRENOM*1_DATEDEPOT",
    } # EXEMPLE -> "candidature" : "NOM_PRENOM*2_IDdocument_datedujour",


def GetDictDonnees(categorie=None, listeID=[]):
    # Paramètres standards
    dict_donnees = {}
    dict_donnees["CATEGORIE"] = categorie
    dict_donnees["NBREDOCUMENTS"] = len(listeID)
    dict_donnees["NOMEDITION"] = NOMS_EDITION[categorie]
    
    # Importe les données uniques pour chaque document
    numDoc = 1
    for ID in listeID :
        listeMotscles, dictDonneesDocument = GetDonneesDocument(categorie, ID)
        dict_donnees[numDoc] = dictDonneesDocument
        numDoc += 1
    
    # Préparation de la liste des mots-clés
    listeMotsclesTemp = []
    for motcle in listeMotscles :
        listeMotsclesTemp.append( (motcle, "base") )
    dict_donnees["MOTSCLES"] = listeMotsclesTemp
    
    return dict_donnees



def GetDonneesDocument(categorie=None, ID=None):
    """ categorie = candidat, candidature, personne... """
    
    if categorie == "personne" :
        listeMotscles, dictDonnees = Importation_personne(IDpersonne=ID)
        return listeMotscles, dictDonnees

    if categorie == "contrat" :
        listeMotsclesContrat, dictDonneesContrat = Importation_contrat(IDcontrat=ID)
        IDpersonne = dictDonneesContrat["_IDPERSONNE"]
        listeMotsclesPersonne, dictDonneesPersonne = Importation_personne(IDpersonne=IDpersonne)
        
        listeMotscles = []
        for motcle in listeMotsclesPersonne :
            if not motcle.startswith("_") :
                listeMotscles.append(motcle)
        for motcle in listeMotsclesContrat :
            if not motcle.startswith("_") :
                listeMotscles.append(motcle)
        
        dictDonnees = {}
        for motcle, valeur in dictDonneesPersonne.iteritems() :
            if not motcle.startswith("_") :
                dictDonnees[motcle] = valeur
        for motcle, valeur in dictDonneesContrat.iteritems() :
            if not motcle.startswith("_") :
                dictDonnees[motcle] = valeur
        
        return listeMotscles, dictDonnees
            
    if categorie == "candidat" :
        listeMotscles, dictDonnees = Importation_candidat(IDcandidat=ID)
        return listeMotscles, dictDonnees
    
    if categorie == "candidature" :
        listeMotsclesCandidature, dictDonneesCandidature = Importation_candidature(IDcandidature=ID)
        IDpersonne = dictDonneesCandidature["_IDPERSONNE"]
        IDcandidat = dictDonneesCandidature["_IDCANDIDAT"]
        if IDpersonne == 0 or IDpersonne == None :
            listeMotsclesPersonne, dictDonneesPersonne = Importation_candidat(IDcandidat=IDcandidat)
        else:
            listeMotsclesPersonne, dictDonneesPersonne = Importation_personne(IDpersonne=IDpersonne)
        
        listeMotscles = []
        for motcle in listeMotsclesPersonne :
            if not motcle.startswith("_") :
                listeMotscles.append(motcle)
        for motcle in listeMotsclesCandidature :
            if not motcle.startswith("_") :
                listeMotscles.append(motcle)
        
        dictDonnees = {}
        for motcle, valeur in dictDonneesPersonne.iteritems() :
            if not motcle.startswith("_") :
                dictDonnees[motcle] = valeur
        for motcle, valeur in dictDonneesCandidature.iteritems() :
            if not motcle.startswith("_") :
                dictDonnees[motcle] = valeur
        
        return listeMotscles, dictDonnees
    
    

    
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

def Importation_candidat(IDcandidat=None):
    # Données CANDIDAT
    dictDonnees = {}
    
    DB = GestionDB.DB()        
    req = """SELECT IDcandidat, civilite, nom, prenom, date_naiss, age, adresse_resid, cp_resid, ville_resid, memo 
    FROM candidats WHERE IDcandidat=%d; """ % IDcandidat
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    if len(listeDonnees) == 0 : return {}
    
    IDcandidat, civilite, nom, prenom, date_naiss, age, adresse_resid, cp_resid, ville_resid, memo = listeDonnees[0]
    
    dictDonnees["_IDCANDIDAT"] = IDcandidat
    dictDonnees["CIVILITE"] = civilite
    dictDonnees["NOM"] = nom
    dictDonnees["PRENOM"] = prenom
    dictDonnees["ADRESSERESID"] = adresse_resid
    dictDonnees["VILLERESID"] = ville_resid
    dictDonnees["MEMO"] = memo
    
    # Champs spéciaux
    dictDonnees["CPRESID"] = ""
    try :
        if cp_resid != "" and cp_resid != None and cp_resid != "     " :
            if type(cp_resid) == unicode : cp_resid = int(cp_resid)
            dictDonnees["CPRESID"] = "%05d" % cp_resid
        if cp_naiss != "" and cp_naiss != None and cp_naiss != "     " :
            if type(cp_naiss) == unicode : cp_naiss = int(cp_naiss)
            dictDonnees["CPRESID"] = "%05d" % cp_resid
    except : 
        pass

    # Date de naissance
    dictDonnees["DATENAISS"] = ""
    temp = date_naiss
    if temp == "  /  /    " or temp == '' or temp == None:
        temp = ""
    else:
        temp = FonctionsPerso.DateEngFr(temp)
    dictDonnees["DATENAISS"] = temp
    
    # Age
    dictDonnees["AGE"] = ""
    if age != "" and age != None and age != 0 :
        dictDonnees["AGE"] = str(age)
    else:
        if dictDonnees["DATENAISS"] != "" :
            # Calcul de l'age de la personne
            datenaissanceTmp = dictDonnees["DATENAISS"]
            jour = int(datenaissanceTmp[:2])
            mois = int(datenaissanceTmp[3:5])
            annee = int(datenaissanceTmp[6:10])
            bday = datetime.date(annee, mois, jour)
            datedujour = datetime.date.today()
            age = (datedujour.year - bday.year) - int((datedujour.month, datedujour.day) < (bday.month, bday.day))
            dictDonnees["AGE"] = str(age)
        
    # Qualifications
    dictDonnees["QUALIFICATIONS"] = ""
    DB = GestionDB.DB()       
    req = """
    SELECT types_diplomes.nom_diplome, types_diplomes.IDtype_diplome
    FROM types_diplomes LEFT JOIN diplomes_candidats ON types_diplomes.IDtype_diplome = diplomes_candidats.IDtype_diplome
    WHERE diplomes_candidats.IDcandidat=%d
    """ % IDcandidat
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    if len(listeDonnees) > 0 :
        texteTemp = ""
        for nom_diplome, IDtype_diplome in listeDonnees :
            texteTemp += nom_diplome + "; "
        dictDonnees["QUALIFICATIONS"] = texteTemp[:-2]
    
    # Coordonnées
    dictDonnees["TELEPHONES"] = ""
    dictDonnees["FAX"] = ""
    dictDonnees["EMAILS"] = ""
    DB = GestionDB.DB()        
    req = """SELECT IDcoord, categorie, texte, intitule
    FROM coords_candidats
    WHERE IDcandidat=%d; """ % IDcandidat
    DB.ExecuterReq(req)
    listeCoords = DB.ResultatReq()
    DB.Close()
    texteTel = ""
    texteFax = ""
    texteEmails = ""
    nbreTel = 0
    nbreFax = 0
    nbreEmails = 0
    if len(listeCoords) > 0 :
        for IDcoord, categorie, texte, intitule in listeCoords :
            if categorie == "Fixe" or categorie == "Mobile" :
                texteTel += texte + ", "
                nbreTel += 1
            if categorie == "Email" :
                texteEmails += texte + ", "
                nbreEmails += 1
            if categorie == "Fax" :
                texteFax += texte + ", "
                nbreFax += 1
        if nbreTel > 0 : dictDonnees["TELEPHONES"] = texteTel[:-2]
        if nbreEmails > 0 : dictDonnees["EMAILS"] = texteEmails[:-2]
        if nbreFax > 0 : dictDonnees["FAX"] = texteFax[:-2]
    
    # Liste des mots-clés
    listeMotscles = [ "CIVILITE", "NOM", "PRENOM", "DATENAISS", "AGE", "ADRESSERESID", "CPRESID", "VILLERESID", "QUALIFICATIONS", "TELEPHONES", "FAX", "EMAILS", "MEMO"]
    
    return listeMotscles, dictDonnees
    

def Importation_candidature(IDcandidature=None):
    # Importation des données de la candidature
    dictDonnees = {}
    
    DB = GestionDB.DB()        
    req = """SELECT IDcandidat, IDpersonne, date_depot, IDtype, acte_remarques, IDemploi, periodes_remarques, poste_remarques,
    IDdecision, decision_remarques, reponse_obligatoire, reponse, date_reponse, IDtype_reponse 
    FROM candidatures WHERE IDcandidature=%d; """ % IDcandidature
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    if len(listeDonnees) == 0 : return {}
    IDcandidat, IDpersonne, date_depot, IDtype, acte_remarques, IDemploi, periodes_remarques, poste_remarques, IDdecision, decision_remarques, reponse_obligatoire, reponse, date_reponse, IDtype_reponse  = listeDonnees[0]
    
    dictDonnees["_IDCANDIDAT"] = IDcandidat
    dictDonnees["_IDPERSONNE"] = IDpersonne
    
    # Date de dépôt
    dictDonnees["DATEDEPOT"] = FonctionsPerso.DateEngFr(date_depot)
    
    # Type dépôt
    listeTypes = [_(u"De vive voix"), _(u"Courrier"), _(u"Téléphone"), _(u"Main à main"), _(u"Email"), _(u"Pôle Emploi"), _(u"Organisateur"), _(u"Fédération"), _(u"Autre")]
    dictDonnees["TYPEDEPOT"] = listeTypes[IDtype]
    
    # Offre d'emploi
    dictDonnees["OFFREDEMPLOI"] = ""
    if IDemploi == 0 :
        dictDonnees["OFFREDEMPLOI"] = _(u"Candidature spontanée")
    else:
        listeMotsclesEmmplois, dictDonneesEmplois = Importation_offre_emploi(IDemploi=IDemploi)
        dictDonnees["OFFREDEMPLOI"] = dictDonneesEmplois["OFFRE_INTITULE"]
    
    # Disponibilités
    dictDonnees["DISPONIBILITES"] = ""
    DB = GestionDB.DB()        
    req = """SELECT IDdisponibilite, date_debut, date_fin
    FROM disponibilites WHERE IDcandidature=%d ORDER BY date_debut; """ % IDcandidature
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    if len(listeDonnees) > 0 :
        texteTemp = ""
        for IDdisponibilite, date_debut, date_fin in listeDonnees :
            texteTemp += _(u"du %s au %s") % (FonctionsPerso.DateEngFr(date_debut), FonctionsPerso.DateEngFr(date_fin)) + "; "
        dictDonnees["DISPONIBILITES"] = texteTemp[:-2]
        
    # Fonctions
    dictDonnees["FONCTIONS"] = ""
    DB = GestionDB.DB()        
    req = """
    SELECT fonctions.IDfonction, fonctions.fonction
    FROM fonctions LEFT JOIN cand_fonctions ON fonctions.IDfonction = cand_fonctions.IDfonction
    WHERE cand_fonctions.IDcandidature=%d
    """ % IDcandidature
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    if len(listeDonnees) > 0 :
        texteTemp = ""
        for IDfonction, nomFonction in listeDonnees :
            texteTemp += nomFonction + "; "
        dictDonnees["FONCTIONS"] = texteTemp[:-2]
    
    # Fonctions
    dictDonnees["AFFECTATIONS"] = ""
    DB = GestionDB.DB()        
    req = """
    SELECT affectations.IDaffectation, affectations.affectation
    FROM affectations LEFT JOIN cand_affectations ON affectations.IDaffectation = cand_affectations.IDaffectation
    WHERE cand_affectations.IDcandidature=%d
    """ % IDcandidature
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    if len(listeDonnees) > 0 :
        texteTemp = ""
        for IDfonction, nomAffectation in listeDonnees :
            texteTemp += nomAffectation + "; "
        dictDonnees["AFFECTATIONS"] = texteTemp[:-2]
    
    # Décision
    typesDecision = [_(u"Décision non prise"), _(u"Oui"), _(u"Non")]
    dictDonnees["DECISION"] = typesDecision[IDdecision]
    
    # Réponse
    listeTypesReponses = [_(u"De vive voix"), _(u"Courrier"), _(u"Téléphone"), _(u"Main à main"), _(u"Email"), _(u"Autre")] 
    if reponse == 1 :
        dictDonnees["DATEREPONSE"] = FonctionsPerso.DateEngFr(date_reponse)
        dictDonnees["TYPEREPONSE"] = listeTypesReponses(IDtype_reponse)
    
    # Liste des mots-clés
    listeMotscles = [ "DATEDEPOT", "TYPEDEPOT", "OFFREDEMPLOI",  "DISPONIBILITES", "FONCTIONS", "AFFECTATIONS", "DECISION", "DATEREPONSE", "TYPEREPONSE"]
    
    return listeMotscles, dictDonnees


def Importation_offre_emploi(IDemploi=None):
    # Importation des données d'une offre d'emploi
    dictDonnees = {}

    dictDonnees["OFFREDEMPLOI"] = ""
    DB = GestionDB.DB()
    req = """
    SELECT IDemploi, date_debut, date_fin, intitule, detail, reference_anpe
    FROM emplois
    WHERE IDemploi=%d
    """ % IDemploi
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    if len(listeDonnees) == 0 : return {}
    IDemploi, date_debut, date_fin, intitule, detail, reference_anpe = listeDonnees[0]
    
    dictDonnees["OFFRE_DATEDEBUT"] = date_debut
    dictDonnees["OFFRE_DATEFIN"] = date_fin
    dictDonnees["OFFRE_INTITULE"] = intitule
    dictDonnees["OFFRE_DETAIL"] = detail
    dictDonnees["OFFRE_REFERENCE_ANPE"] = reference_anpe
    
    # Liste des mots-clés
    listeMotscles = [ "OFFRE_INTITULE", "OFFRE_DETAIL", "OFFRE_DATEDEBUT", "OFFRE_DATEFIN", "OFFRE_REFERENCE_ANPE"]
    
    return listeMotscles, dictDonnees
                                        
                                    
def Importation_personne(IDpersonne=None):
    # Importation des données d'une personne
    dictDonnees = {}
    
    DB = GestionDB.DB()
    req = """
    SELECT civilite, nom, nom_jfille, prenom, date_naiss, cp_naiss, ville_naiss, nationalite, num_secu, adresse_resid, cp_resid, ville_resid, IDsituation, pays_naiss
    FROM personnes WHERE IDpersonne=%d;
    """ % IDpersonne
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    if len(listeDonnees) == 0 : return {}
    
    civilite, nom, nom_jfille, prenom, date_naiss, cp_naiss, ville_naiss, nationalite, num_secu, adresse_resid, cp_resid, ville_resid, IDsituation, pays_naiss = listeDonnees[0]
    
    dictDonnees["CIVILITE"] = civilite
    dictDonnees["NOM"] = nom
    dictDonnees["NOMJFILLE"] = nom_jfille
    dictDonnees["PRENOM"] = prenom
    
    # Date de naissance
    dictDonnees["DATENAISS"] = ""
    if date_naiss != "" : dictDonnees["DATENAISS"] = FonctionsPerso.DateEngFr(date_naiss)
    
    # Age
    dictDonnees["AGE"] = ""
    if dictDonnees["DATENAISS"] != "" :
        # Calcul de l'age de la personne
        datenaissanceTmp = dictDonnees["DATENAISS"]
        jour = int(datenaissanceTmp[:2])
        mois = int(datenaissanceTmp[3:5])
        annee = int(datenaissanceTmp[6:10])
        bday = datetime.date(annee, mois, jour)
        datedujour = datetime.date.today()
        age = (datedujour.year - bday.year) - int((datedujour.month, datedujour.day) < (bday.month, bday.day))
        dictDonnees["AGE"] = str(age)
            
    # CP naissance
    dictDonnees["CPNAISS"] = ""
    try :
        if cp_naiss != "" and cp_naiss != None and cp_naiss != "     " :
            if type(cp_naiss) == unicode : cp_naiss = int(cp_naiss)
            dictDonnees["CPNAISS"] = "%05d" % cp_naiss
        if cp_naiss != "" and cp_naiss != None and cp_naiss != "     " :
            if type(cp_naiss) == unicode : cp_naiss = int(cp_naiss)
            dictDonnees["CPNAISS"] = "%05d" % cp_naiss
    except : 
        pass
    
    # Ville de naissance
    dictDonnees["VILLENAISS"] = ville_naiss
    
    # Nationalité
    DB = GestionDB.DB()
    req = """
    SELECT nationalite
    FROM pays WHERE IDpays=%d;
    """ % nationalite
    DB.ExecuterReq(req)
    listePays = DB.ResultatReq()
    DB.Close()
    dictDonnees["NATIONALITE"] = listePays[0][0]
    
    # Pays de naissance
    DB = GestionDB.DB()
    req = """
    SELECT nom
    FROM pays WHERE IDpays=%d;
    """ % pays_naiss
    DB.ExecuterReq(req)
    listePays = DB.ResultatReq()
    DB.Close()
    dictDonnees["PAYSNAISS"] = listePays[0][0]
    
    # Num sécu
    dictDonnees["NUMSECU"] = num_secu
    
    # Adresse
    dictDonnees["ADRESSERESID"] = adresse_resid
    
    # CP
    dictDonnees["CPRESID"] = ""
    try :
        if cp_resid != "" and cp_resid != None and cp_resid != "     " :
            if type(cp_resid) == unicode : cp_resid = int(cp_resid)
            dictDonnees["CPRESID"] = "%05d" % cp_resid
        if cp_resid != "" and cp_resid != None and cp_resid != "     " :
            if type(cp_resid) == unicode : cp_resid = int(cp_resid)
            dictDonnees["CPRESID"] = "%05d" % cp_resid
    except : 
        pass
        
    # Ville
    dictDonnees["VILLERESID"] = ville_resid
    
    # Situation
    dictDonnees["SITUATION"] = ""
    DB = GestionDB.DB()
    req = """
    SELECT situation
    FROM situations WHERE IDsituation=%d;
    """ % IDsituation
    DB.ExecuterReq(req)
    listeSituations = DB.ResultatReq()
    DB.Close()
    if len(listeSituations) > 0 :
        dictDonnees["SITUATION"] = listeSituations[0][0]

    
    # Coordonnées
    dictDonnees["TELEPHONES"] = ""
    dictDonnees["FAX"] = ""
    dictDonnees["EMAILS"] = ""
    DB = GestionDB.DB()        
    req = """SELECT IDcoord, categorie, texte, intitule
    FROM coordonnees
    WHERE IDpersonne=%d; """ % IDpersonne
    DB.ExecuterReq(req)
    listeCoords = DB.ResultatReq()
    DB.Close()
    texteTel = ""
    texteFax = ""
    texteEmails = ""
    nbreTel = 0
    nbreFax = 0
    nbreEmails = 0
    if len(listeCoords) > 0 :
        for IDcoord, categorie, texte, intitule in listeCoords :
            if categorie == "Fixe" or categorie == "Mobile" :
                texteTel += texte + ", "
                nbreTel += 1
            if categorie == "Email" :
                texteEmails += texte + ", "
                nbreEmails += 1
            if categorie == "Fax" :
                texteFax += texte + ", "
                nbreFax += 1
        if nbreTel > 0 : dictDonnees["TELEPHONES"] = texteTel[:-2]
        if nbreEmails > 0 : dictDonnees["EMAILS"] = texteEmails[:-2]
        if nbreFax > 0 : dictDonnees["FAX"] = texteFax[:-2]

    # Liste des mots-clés
    listeMotscles = [ "CIVILITE", "NOM", "NOMJFILLE", "PRENOM", "DATENAISS", "AGE", "CPNAISS", "VILLENAISS",
    "PAYSNAISS", "NATIONALITE", "NUMSECU", "ADRESSERESID", "CPRESID", "VILLERESID", "SITUATION",
    "TELEPHONES", "EMAILS", "FAX"]

    return listeMotscles, dictDonnees

def Importation_contrat(IDcontrat=None):
    # Importation des données d'un contrat
    dictDonnees = {}
    
    DB = GestionDB.DB()
    req = """
    SELECT IDpersonne, IDclassification, IDtype, valeur_point, date_debut, date_fin, essai
    FROM contrats WHERE IDcontrat=%d;
    """ % IDcontrat
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    if len(listeDonnees) == 0 : 
        DB.Close()
        return {}
    
    IDpersonne, IDclassification, IDtype, valeur_point, date_debut, date_fin, essai = listeDonnees[0]
    
    dictDonnees["_IDPERSONNE"] = IDpersonne
    
    # Dates du contrat
    dictDonnees["DATEDEBUT"] = ""
    if date_debut != "" : dictDonnees["DATEDEBUT"] = FonctionsPerso.DateEngFr(date_debut)
    dictDonnees["DATEFIN"] = ""
    if date_fin != "" : dictDonnees["DATEFIN"] = FonctionsPerso.DateEngFr(date_fin)
    
    # Essai
    dictDonnees["ESSAI"] = str(essai)
    
    # Classification
    req = """
    SELECT nom
    FROM contrats_class WHERE IDclassification=%d;
    """ % IDclassification
    DB.ExecuterReq(req)
    dictDonnees["CLASSIFICATION"] = DB.ResultatReq()[0][0]
            
    # Type contrat
    req = """
    SELECT nom, nom_abrege, duree_indeterminee
    FROM contrats_types WHERE IDtype=%d;
    """ % IDtype
    DB.ExecuterReq(req)
    dictDonnees["TYPECONTRAT"] = DB.ResultatReq()[0][0]
            
    # Valeur du point
    req = """
    SELECT valeur, date_debut
    FROM valeurs_point WHERE IDvaleur_point=%d;
    """ % valeur_point
    DB.ExecuterReq(req)
    dictDonnees["VALEURPOINT"] = u"%s €" % DB.ResultatReq()[0][0]
    
    # Liste des mots-clés
    listeMotscles = [ "DATEDEBUT", "DATEFIN", "CLASSIFICATION", "TYPECONTRAT", "VALEURPOINT", "ESSAI"]
    
    # Champs personnalisés des contrats
    req = """
    SELECT IDchamp, mot_cle
    FROM contrats_champs;
    """
    DB.ExecuterReq(req)
    listeChamps = DB.ResultatReq()
    dictChamps = {}
    for IDchamp, mot_cle in listeChamps :
        dictChamps[IDchamp] = mot_cle
        listeMotscles.append(mot_cle)
    
    # Valeurs des champs personnalisés
    req = """
    SELECT IDchamp, valeur
    FROM contrats_valchamps WHERE IDcontrat=%d AND type='contrat';
    """ % IDcontrat
    DB.ExecuterReq(req)
    listeChamps = DB.ResultatReq()
    for IDchamp, valeur in listeChamps :
        mot_cle = dictChamps[IDchamp]
        dictDonnees[mot_cle] = valeur
        
    DB.Close() 
    return listeMotscles, dictDonnees

# --------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print GetDictDonnees(categorie="candidat", listeID=[2, 5])
    
    
    