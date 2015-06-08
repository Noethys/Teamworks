#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Teamworks Gestion d'�quipes
# Site internet :  teamworks.forumactif.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

TABLES_IMPORTATION_OPTIONNELLES = [ # [Nom Categorie, (liste des tables...,), Selectionn�]
        [u"dipl�mes et pi�ces", ("types_pieces", "types_diplomes", "diplomes_pieces"), True],
        [u"P�riodes de vacances", ("periodes_vacances",), True],
        [u"Jours f�ri�s", ("jours_feries",), True],
        [u"Cat�gories de pr�sences", ("cat_presences",), True],
        [u"Situations professionelles", ("situations",), True],
        [u"Donn�es de contrats", ("contrats_champs", "contrats_class", "contrats_modeles", "contrats_types", "contrats_valchamps", "valeurs_point"), True],
        #[u"Pays", ("pays",), True],
        ]

TABLES_IMPORTATION_OBLIGATOIRES = ["gadgets", "pays"]


DB_DATA = {

    "personnes":[           ("IDpersonne", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la personne"),
                                    ("civilite", "VARCHAR(5)", u"Civilit�", u"Civilit� de la personne"),
                                    ("nom", "VARCHAR(100)", u"Nom", u"Nom de famille de la personne"),
                                    ("nom_jfille", "VARCHAR(100)", u"Nom de jeune fille", u"Nom de jeune fille de la personne"),
                                    ("prenom", "VARCHAR(100)", u"Pr�nom", u"Pr�nom de la personne"),
                                    ("date_naiss", "DATE", "Date de naissance", u"Date de naissance de la personne"),
                                    ("cp_naiss", "INTEGER", u"CP naissance", u"Code postal du lieu de naissance de la personne"),
                                    ("ville_naiss", "VARCHAR(100)", u"Ville naissance", u"Ville du lieu de naissance de la personne"),
                                    ("pays_naiss", "INTEGER", u"Pays naissance", u"ID du Pays de naissance de la personne"),
                                    ("nationalite", "INTEGER", u"Nationalit�", u"Nationalit� de la personne"),
                                    ("num_secu", "VARCHAR(21)", u"Num S�cu", u"Num�ro de s�curit� sociale de la personne"),
                                    ("adresse_resid", "VARCHAR(200)", "Adresse", u"Adresse de la personne"),
                                    ("cp_resid", "INTEGER", u"Code postal", u"Code postal de la personne"),
                                    ("ville_resid", "VARCHAR(100)", u"Ville", u"Ville de la personne"),
                                    ("memo", "VARCHAR(800)", u"M�mo", u"M�mo sur la personne"),
                                    ("IDsituation", "INTEGER", u"ID", u"ID de la situation sociale"),
                                    ("cadre_photo", "VARCHAR(200)", u"Cadre", u"Cadre photo rattach�"),
                                    ("texte_photo", "VARCHAR(300)", u"Texte", u"Texte de la photo rattach�e"),
                                    ], # Donn�es sur les personnes

    "situations":[          ("IDsituation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la situation sociale"),
                                    ("situation", "VARCHAR(400)", u"Situation", u"Situation sociale"),
                                    ], # Liste des situations sociales possibles

    "coordonnees":[         ("IDcoord", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la coordonn�e"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID de la personne"),
                                    ("categorie", "VARCHAR(100)", u"Cat�gorie", u"Cat�gorie"),
                                    ("texte", "VARCHAR(50)", u"Texte", u"Texte"),
                                    ("intitule", "VARCHAR(300)", u"Intitul�", u"Intitul�"),
                                    ], # Liste des coordonn�es de la personne

    "diplomes":[            ("IDdiplome", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du diplome"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID de la personne"),
                                    ("IDtype_diplome", "INTEGER", u"IDtype_diplome", u"ID du type de diplome"),
                                    ], # Liste des diplomes saisis pour chaque personne

    "types_diplomes":[      ("IDtype_diplome", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du type de diplome"),
                                    ("nom_diplome", "VARCHAR(200)", u"Dipl�me", u"Nom du type de dipl�me"),
                                    ], # Types de diplomes des personnes. Apparait dans Diplomes.

    "pieces":[              ("IDpiece", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la pi�ce"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID de la personne"),
                                    ("IDtype_piece", "INTEGER", u"IDtype_piece", u"ID du type de pi�ce"),
                                    ("date_debut", "DATE", u"D�but validit�", u"Date de d�but de validit�"),
                                    ("date_fin", "DATE", u"Fin validit�", u"Date de fin de validit�"),
                                    ], # Liste des pi�ces saisies pour chaque personne

    "types_pieces":[        ("IDtype_piece", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du type de pi�ce"),
                                    ("nom_piece", "VARCHAR(200)", u"Pi�ce", u"Nom de la pi�ce"),
                                    ("duree_validite", "VARCHAR(100)", u"Dur�e validit�", u"Dur�e par d�faut de la validit� de la pi�ce"),
                                    ], # Liste des types de pi�ces possibles. Apparait dans Pieces et diplomes_pieces.

    "diplomes_pieces":[     ("IDdiplome_piece", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du type de pi�ce"),
                                    ("IDtype_diplome", "INTEGER", u"IDdiplome", u"ID du diplome"),
                                    ("IDtype_piece", "INTEGER", u"IDtype_piece", u"ID du type de pi�ce"),
                                    ], # Table des liaisons entre les tables Diplomes et Types_pieces. Permet d'attribuer des types de pi�ces � des diplomes.

    "contrats":[                ("IDcontrat", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du contrat"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID de la personne"),
                                    ("IDclassification", "INTEGER", u"IDclassification", u"Classification du contrat"),
                                    ("IDtype", "INTEGER", u"IDtype", u"ID du type de contrat"),
                                    ("valeur_point", "INTEGER", u"ID Valeur du point", u"ID de la valeur du point"),
                                    ("date_debut", "DATE", u"D�but validit�", u"Date de d�but du contrat"),
                                    ("date_fin", "DATE", u"Fin validit�", u"Date de fin du contrat"),
                                    ("date_rupture", "DATE", u"Date Rupture", u"Date de rupture anticip�e du contrat"),
                                    ("essai", "INTEGER", u"P�riode d'essai", u"Nombre de jours de p�riode d'essai"),
                                    ("signature", "VARCHAR(3)", u"Sign�?", u"Contrat sign� ? (oui/non)"),
                                    ("due", "VARCHAR(3)", u"DUE", u"DUE faite ? (oui/non)"),
                                    ], # Contrats = postes occup�s par la personne sur la structure

    "contrats_class":       [("IDclassification", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la classification du poste"),
                                    ("nom", "VARCHAR(200)", u"Classification", u"Nom de la classification du poste"),
                                    ], # Classification du poste. Ex : "personnel de service", "Animateur BAFA", "Directeur Permanent CVL"...

    "contrats_types":       [("IDtype", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du type de contrat"),
                                    ("nom", "VARCHAR(300)", u"Type de contrat", u"Nom du type de contrat"),
                                    ("nom_abrege", "VARCHAR(10)", u"Type de contrat", u"Nom abr�g� du type de contrat"),
                                    ("duree_indeterminee", "VARCHAR(3)", u"Dur�e ind�termin�e", u"Type de contrat � dur�e ind�termin�e (oui/non)"),
                                    ], # Type de contrat = "CEE", "CDD", "CDI", "Convention de b�n�volat"...

    "valeurs_point":        [("IDvaleur_point", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la valeur du point"),
                                    ("valeur", "REAL", u"Valeur du point", u"Valeur du point"),
                                    ("date_debut", "DATE", u"Date de d�but de validit�", u"Date de d�but de validit� de la valeur du point"),
                                    ], # Valeur actuel du point... Apparait dans Contrats

    "contrats_modeles": [ ("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du mod�le de contrat"),
                                    ("nom", "VARCHAR(300)", u"Nom", u"Nom du mod�le de contrat"),
                                    ("description", "VARCHAR(400)", u"Description", u"Description du mod�le de contrat"),
                                    ("IDclassification", "INTEGER", u"IDclassification", u"Classification du contrat"),
                                    ("IDtype", "INTEGER", u"IDtype", u"ID du type de contrat"),
                                    ], # Mod�les de contrats.

    "contrats_champs":  [ ("IDchamp", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du champ"),
                                    ("nom", "VARCHAR(300)", u"Nom", u"Nom du champ"),
                                    ("description", "VARCHAR(400)", u"Description", u"Description du champ"),
                                    ("mot_cle", "VARCHAR(50)", u"Mot-cl�", u"Mot-cl� pour le publipostage"),
                                    ("defaut", "VARCHAR(800)", u"Valeur par d�faut", u"Valeur par d�faut du champ"),
                                    ("exemple", "VARCHAR(200)", u"Exemple", u"Exemple de valeur pour ce champ"),
                                    ], # Champs personnalis�s pour les contrats.

    "contrats_valchamps":  [ ("IDval_champ", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la valeur du champ"),
                                    ("IDchamp", "INTEGER", u"IDchamp", u"ID du champ"),
                                    ("type", "VARCHAR(10)", u"Type de champ", u"Type de champ (contrat ou modele)"),
                                    ("IDcontrat", "INTEGER", u"IDcontrat", u"ID du contrat"),
                                    ("IDmodele", "INTEGER", u"IDmodele", u"ID du modele"),
                                    ("valeur", "VARCHAR(800)", u"Description", u"Description du champ"),
                                    ], # Valeurs des champs pour les contrats et les mod�les de contrats.
                                                                        
    "presences":[           ("IDpresence", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la presence"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID de la personne"),
                                    ("date", "DATE", u"DATE", u"Date de la pr�sence"),
                                    ("heure_debut", "DATE", u"Heure de d�but", u"Heure de d�but"),
                                    ("heure_fin", "DATE", u"Heure de fin", u"Heure de fin"),
                                    ("IDcategorie", "INTEGER", u"Cat�gorie", u"Cat�gorie du travail effectu�"),
                                    ("intitule", "VARCHAR(200)", u"Intitul�", u"Intitul� du travail effectu�"),
                                    ], # Pr�sences du personnel

    "cat_presences":[       ("IDcategorie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la cat�gorie de pr�sence"),
                                    ("nom_categorie", "VARCHAR(200)", u"Cat�gorie", u"Nom de la cat�gorie de la pr�sence"),
                                    ("IDcat_parent", "INTEGER", u"ID de la cat�gorie parente", u"ID de la cat�gorie parente"),
                                    ("ordre", "INTEGER", u"Ordre", u"Ordre dans l'arborescence des cat�gories"),
                                    ("couleur", "VARCHAR(30)", u"Couleur", u"Couleur de la cat�gorie"),
                                    ], # Cat�gories de pr�sences. Ex : "R�union", "Cong�s pay�s"... Apparait dans Pr�sences

    "periodes_vacances":[     ("IDperiode", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID periode vacances"),
                                    ("nom", "VARCHAR(100)", "Nom de la p�riode", u"Nom de la p�riode de vacances"),
                                    ("annee", "VARCHAR(4)", "Ann�e de la p�riode", u"Ann�e de la p�riode de vacances"),
                                    ("date_debut", "DATE", "Date de d�but", u"Date de d�but"),
                                    ("date_fin", "DATE", "Date de fin", u"Date de fin"),
                                    ], # Calendrier des jours de vacances

    "jours_feries":[             ("IDferie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID jour f�ri�"),
                                    ("type", "VARCHAR(10)", "Type", u"Type de jour f�ri� : fixe ou variable"),
                                    ("nom", "VARCHAR(100)", "Nom du jour f�ri�", u"Nom du jour f�ri�"),
                                    ("jour", "INTEGER", "Jour de la date", u"Jour de la date"),
                                    ("mois", "INTEGER", "Mois de la date", u"Mois de la date"),
                                    ("annee", "INTEGER", "Ann�e de la date", u"Ann�e de la date"),
                                    ], # Calendrier des jours f�ri�s variables et fixes

    "modeles_planning":[    ("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID mod�le de planning"),
                                    ("nom", "VARCHAR(300)", u"Nom", u"Nom du mod�le"),
                                    ("type", "VARCHAR(5)", u"Type", u"Type de mod�le"),
                                    ("description", "VARCHAR(400)", u"Description", u"Description du mod�le"),
                                    ("periodes", "VARCHAR(3)", u"P�riodes", u"P�riodes d'application du mod�le"),
                                    ("inclureferies", "INTEGER", u"Inclure F�ri�s", u"Inclure les jours f�ri�s"),
                                    ], # Mod�les de planning

    "modeles_taches":[      ("IDtache", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID t�che mod�le"),
                                    ("IDmodele", "INTEGER", u"IDmod�le", u"ID mod�le rattach�"),
                                    ("type", "VARCHAR(5)", u"Type", u"Type de mod�le"),
                                    ("periode", "INTEGER", u"P�riode", u"P�riode d'application de la t�che"),
                                    ("jour", "INTEGER", u"Jour", u"Jour d'application"),
                                    ("heure_debut", "DATE", u"Heure de d�but", u"Heure de d�but"),
                                    ("heure_fin", "DATE", u"Heure de fin", u"Heure de fin"),
                                    ("IDcategorie", "INTEGER", u"Cat�gorie", u"Cat�gorie de la t�che"),
                                    ("intitule", "VARCHAR(200)", u"Intitul�", u"Intitul� de la t�che"),
                                    ], # T�ches pour les Mod�les de planning

    "due_valeurs":[          ("IDvaleur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"IDvaleur"),
                                    ("code", "VARCHAR(50)", u"Code", u"Code d'identification du champ"),
                                    ("valeur", "VARCHAR(200)", u"Valeur", u"Valeur du champ"),
                                    ], # Valeurs sauvegard�es pour le document DUE.

    "pays":[                    ("IDpays", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID pays"),
                                    ("code_drapeau", "VARCHAR(50)", u"Code drapeau", u"Code drapeau associ�"),
                                    ("nom", "VARCHAR(100)", u"Nom", u"Nom du pays"),
                                    ("nationalite", "VARCHAR(100)", u"Nationalit�", u"Nationalit� correspondante"),
                                    ], # Liste des pays, drapeaux et nationalit�s
                                    
    "divers":[                   ("IDdivers", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID divers"),
                                    ("motdepasse", "VARCHAR(50)", u"Mot de passe", u"Mot de passe du fichier"),
                                    ("date_derniere_ouverture", "DATE", u"Date", u"Date de derni�re ouverture du fichier"),
                                    ("date_creation_fichier", "DATE", u"Date", u"Date de cr�ation du fichier"),
                                    ("version_DB", "INTEGER", u"Version", u"Version de la base de donn�es"),
                                    ("save_active", "INTEGER", u"Activation", u"Sauvegarde autom. activ�e (1/0)"),
                                    ("save_frequence", "INTEGER", u"Fr�quence", u"Fr�quence des sauvegardes auto."),
                                    ("save_elements", "VARCHAR(500)", u"Elements", u"Elements des sauvegardes auto."),
                                    ("save_destination", "VARCHAR(500)", u"Destination", u"R�pertoire de destination des sauvegardes auto."),
                                    ("save_conservation", "INTEGER", u"Conservation", u"Nbre exemplaires conserv�s des sauvegardes auto."),
                                    ("save_date_derniere", "DATE", u"Date derni�re", u"Date de la derni�re sauvegarde"),
                                    ("codeIDfichier", "VARCHAR(20)", u"ID fichier", u"Identifiant unique de fichier"),
                                    ], # Donn�es diverses


    "gadgets":[                ("IDgadget", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID gadget"),
                                    ("nom", "VARCHAR(50)", u"Nom", u"Nom du gadget"),
                                    ("label", "VARCHAR(50)", u"Label", u"Label du gadget"),
                                    ("description", "VARCHAR(400)", u"Description", u"Description du gadget"),
                                    ("taille", "VARCHAR(50)", u"Taille", u"Taille du gadget"),
                                    ("affichage", "VARCHAR(5)", u"Affichage(True/False)", u"Affichage du gadget"),
                                    ("ordre", "INTEGER", u"Ordre", u"Num�ro d'ordre d'affichage"),
                                    ("config", "VARCHAR(5)", u"config(True/False)", u"config(True/False)"),
                                    ("parametres", "VARCHAR(500)", u"Param�tres", u"Param�tres du gadget"),
                                    ], # Param�tres des gadgets de la page d'accueil


    "parametres":[           ("IDparametre", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID parametre"),
                                    ("categorie", "VARCHAR(100)", u"Cat�gorie", u"Cat�gorie"),
                                    ("nom", "VARCHAR(100)", u"Nom", u"Nom"),
                                    ("parametre", "VARCHAR(300)", u"Parametre", u"Parametre"),
                                    ], # Param�tres divers


    "distances":[              ("IDdistance", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID distance"),
                                    ("cp_depart", "VARCHAR(5)", u"CP d�part", u"CP de la ville de d�part"),
                                    ("ville_depart", "VARCHAR(200)", u"Ville d�part", u"Nom de la ville de d�part"),
                                    ("cp_arrivee", "VARCHAR(5)", u"CP arriv�e", u"CP de la ville d'arriv�e"),
                                    ("ville_arrivee", "VARCHAR(200)", u"Ville arriv�e", u"Nom de la ville d'arriv�e"),
                                    ("distance", "FLOAT", u"Distance", u"Distance en Km"),
                                    ], # Liste des distances entre les villes pour les frais de d�placements

    "deplacements":[       ("IDdeplacement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID d�placement"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID de la personne"),
                                    ("date", "DATE", u"Date", u"Date du d�placement"),
                                    ("objet", "VARCHAR(100)", u"Objet", u"Objet du d�placement"),
                                    ("cp_depart", "VARCHAR(5)", u"CP d�part", u"CP de la ville de d�part"),
                                    ("ville_depart", "VARCHAR(200)", u"Ville d�part", u"Nom de la ville de d�part"),
                                    ("cp_arrivee", "VARCHAR(5)", u"CP arriv�e", u"CP de la ville d'arriv�e"),
                                    ("ville_arrivee", "VARCHAR(200)", u"Ville arriv�e", u"Nom de la ville d'arriv�e"),
                                    ("distance", "FLOAT", u"Distance", u"Distance en Km"),
                                    ("aller_retour", "VARCHAR(5)", u"Aller_retour(True/False)", u"Aller_retour(True/False)"),
                                    ("tarif_km", "FLOAT", u"Tarif du Km", u"Tarif du Km en euros"),
                                    ("IDremboursement", "INTEGER", u"IDremboursement", u"ID du remboursement"),
                                    ], # Liste des d�placements

    "remboursements":[    ("IDremboursement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDremboursement", u"ID remboursement"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID de la personne"),
                                    ("date", "DATE", u"Date", u"Date du remboursement"),
                                    ("montant", "FLOAT", u"Montant", u"Montant total du remboursement"),
                                    ("listeIDdeplacement", "VARCHAR(300)", u"D�placements", u"Liste des IDdeplacements"),
                                    ], # Liste des remboursements de frais de d�placements

    "scenarios":[             ("IDscenario", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDscenario", u"ID scenario"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID de la personne"),
                                    ("nom", "VARCHAR(200)", u"Nom", u"Nom du sc�nario"),
                                    ("description", "VARCHAR(400)", u"Description", u"Description du sc�nario"),
                                    ("mode_heure", "INTEGER", u"Mode", u"Mode (heure/d�cimal)"),
                                    ("detail_mois", "INTEGER", u"D�tail mois", u"D�tail r�partition par mois"),
                                    ("date_debut", "DATE", u"Date d�but", u"Date de d�but de p�riode"),
                                    ("date_fin", "DATE", u"Date fin", u"Date de fin de p�riode"),
                                    ("toutes_categories", "INTEGER", u"Inclure toutes cat�gories", u"Inclure toutes cat�gories"),
                                    ], # Liste des sc�narios

    "scenarios_cat":[       ("IDscenario_cat", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDscenario_cat", u"ID scenario cat�gorie"),
                                    ("IDscenario", "INTEGER", u"IDscenario", u"IDscenario"),
                                    ("IDcategorie", "INTEGER", u"IDcategorie", u"IDcategorie"),
                                    ("prevision", "VARCHAR(50)", u"Pr�vision", u"Pr�vision"),
                                    ("report", "VARCHAR(50)", u"Report", u"Report"),
                                    ("date_debut_realise", "DATE", u"Date d�but R�alis�", u"Date de d�but de p�riode R�alis�"),
                                    ("date_fin_realise", "DATE", u"Date fin R�alis�", u"Date de fin de p�riode R�alis�"),
                                    ], # Liste des cat�gories de sc�narios

    "candidats":[             ("IDcandidat", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du candidat"),
                                    ("civilite", "VARCHAR(5)", u"Civilit�", u"Civilit� du candidat"),
                                    ("nom", "VARCHAR(100)", u"Nom", u"Nom de famille de la candidate"),
                                    ("prenom", "VARCHAR(100)", u"Pr�nom", u"Pr�nom du candidat"),
                                    ("date_naiss", "DATE", u"Date de naissance", u"Date de naissance du candidat"),
                                    ("age", "INTEGER", u"Age", u"Age du candidat si date de naissance inconnue"),
                                    ("adresse_resid", "VARCHAR(200)", "Adresse", u"Adresse du candidat"),
                                    ("cp_resid", "INTEGER", u"Code postal", u"Code postal du candidat"),
                                    ("ville_resid", "VARCHAR(200)", u"Ville", u"Ville du candidat"),
                                    ("memo", "VARCHAR(300)", u"M�mo", u"M�mo sur la personne"),
                                    ], # Donn�es sur les candidats

    "coords_candidats":[  ("IDcoord", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la coordonn�e"),
                                    ("IDcandidat", "INTEGER", u"IDcandidat", u"ID du candidat"),
                                    ("categorie", "VARCHAR(50)", u"Cat�gorie", u"Cat�gorie"),
                                    ("texte", "VARCHAR(50)", u"Texte", u"Texte"),
                                    ("intitule", "VARCHAR(200)", u"Intitul�", u"Intitul�"),
                                    ], # Liste des coordonn�es du candidat

    "diplomes_candidats":[("IDdiplome", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du diplome"),
                                    ("IDcandidat", "INTEGER", u"IDcandidat", u"ID du candidat"),
                                    ("IDtype_diplome", "INTEGER", u"IDtype_diplome", u"ID du type de diplome"),
                                    ], # Liste des diplomes saisis pour les candidats

    "entretiens":[             ("IDentretien", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de l'entretien"),
                                    ("IDcandidat", "INTEGER", u"IDcandidat", u"ID du candidat"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID du salari�"),
                                    ("date", "DATE", u"Date de l'entretien", u"Date de l'entretien"),
                                    ("heure", "DATE", u"Heure", u"Heure de l'entretien"),
                                    ("avis", "INTEGER", u"Avis", u"Avis sur l'entretien"),
                                    ("remarques", "VARCHAR(500)", u"Remarques", u"Remarques sur l'entretien"),
                                    ], # Liste des entretiens du candidat

    "disponibilites":[         ("IDdisponibilite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la disponibilite"),
                                    ("IDcandidature", "INTEGER", u"IDcandidature", u"ID de la candidature"),
                                    ("date_debut", "DATE", u"DATE", u"Date de d�but"),
                                    ("date_fin", "DATE", u"DATE", u"Date de fin"),
                                    ], # Liste des disponibilit�s du candidat
                                    
    "fonctions":[              ("IDfonction", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la fonction"),
                                    ("fonction", "VARCHAR(500)", u"Fonction", u"Fonction candidat"),
                                    ], # Liste des fonctions demand�es par les candidats

    "affectations":[          ("IDaffectation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de l'affectation"),
                                    ("affectation", "VARCHAR(500)", u"Affectation", u"Affectation candidat"),
                                    ], # Liste des affectations demand�es par les candidats

    "candidatures":[         ("IDcandidature", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la candidature"),
                                    ("IDcandidat", "INTEGER", u"IDcandidat", u"ID du candidat"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID du salari�"),
                                    ("date_depot", "DATE", u"Date de la candidature", u"Date de la candidature"),
                                    ("IDtype", "INTEGER", u"IDtype", u"ID du type de candidature"),
                                    ("acte_remarques", "VARCHAR(500)", u"Remarques", u"Remarques sur le d�p�t de candidature"),
                                    ("IDemploi", "INTEGER", u"IDemploi", u"ID de l'emploi"),
                                    ("periodes_remarques", "VARCHAR(500)", u"Remarques", u"Remarques sur les disponibilit�s"),
                                    ("poste_remarques", "VARCHAR(500)", u"Remarques", u"Remarques sur le poste de la candidature"),
                                    ("IDdecision", "INTEGER", u"IDdecision", u"ID de la d�cision"),
                                    ("decision_remarques", "VARCHAR(500)", u"Remarques", u"Remarques sur la d�cision"),
                                    ("reponse_obligatoire", "INTEGER", u"Reponse obligatoire", u"R�ponse obligatoire (0 ou 1)"),
                                    ("reponse", "INTEGER", u"Reponse", u"R�ponse de la candidature (0 ou 1)"),
                                    ("date_reponse", "DATE", u"Date de la r�ponse", u"Date de la r�ponse"),
                                    ("IDtype_reponse", "INTEGER", u"IDtype", u"ID du type de r�ponse"),
                                    ], # Liste des candidatures du candidat
                                    
    "cand_fonctions":[      ("IDcand_fonction", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID"),
                                    ("IDcandidature", "INTEGER", u"ID", u"ID de la candidature"),
                                    ("IDfonction", "INTEGER", u"ID", u"ID de la fonction"),
                                    ], # Liste des fonctions demand�es par les candidats

    "cand_affectations":[  ("IDcand_affectation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID"),
                                    ("IDcandidature", "INTEGER", u"ID", u"ID de la candidature"),
                                    ("IDaffectation", "INTEGER", u"ID", u"ID de l'affectation"),
                                    ], # Liste des affectations demand�es par les candidats

    "emplois":[                ("IDemploi", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de l'emploi"),
                                    ("date_debut", "DATE", u"Date d�but", u"Date de d�but de recrutement"),
                                    ("date_fin", "DATE", u"Date fin", u"Date de fin de recrutement"),
                                    ("intitule", "VARCHAR(300)", u"Intitul�", u"Intitul� de l'offre d'emploi"),
                                    ("detail", "VARCHAR(800)", u"D�tail", u"D�tail de l'offre d'emploi"),
                                    ("reference_anpe", "VARCHAR(100)", u"R�f�rence", u"R�f�rence ANPE"),
                                    ("periodes_remarques", "VARCHAR(300)", u"Remarques", u"Remarques sur les disponibilit�s"),
                                    ("poste_remarques", "VARCHAR(300)", u"Remarques", u"Remarques sur le poste"),
                                    ], # Liste des offres d'emploi

    "emplois_dispo":[       ("IDdisponibilite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la disponibilite"),
                                    ("IDemploi", "INTEGER", u"IDemploi", u"ID de l'emploi"),
                                    ("date_debut", "DATE", u"DATE", u"Date de d�but"),
                                    ("date_fin", "DATE", u"DATE", u"Date de fin"),
                                    ], # Liste des disponibilit�s d'une offre d'emploi

    "emplois_fonctions":[  ("IDemploi_fonction", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID"),
                                    ("IDemploi", "INTEGER", u"IDemploi", u"ID de l'emploi"),
                                    ("IDfonction", "INTEGER", u"ID", u"ID de la fonction"),
                                    ], # Liste des fonctions de l'offre d'emploi

    "emplois_affectations":[("IDemploi_affectation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID"),
                                    ("IDemploi", "INTEGER", u"IDemploi", u"ID de l'emploi"),
                                    ("IDaffectation", "INTEGER", u"ID", u"ID de l'affectation"),
                                    ], # Liste des affectations de l'offre d'emploi
                                    
    "emplois_diffuseurs":[ ("IDemploi_diffuseur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID"),
                                    ("IDemploi", "INTEGER", u"IDemploi", u"ID de l'emploi"),
                                    ("IDdiffuseur", "INTEGER", u"ID", u"ID du diffuseur"),
                                    ], # Liste des diffuseurs utilis�s pour un offre d'emploi

    "diffuseurs":[              ("IDdiffuseur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du diffuseur"),
                                    ("diffuseur", "VARCHAR(400)", u"Diffuseur", u"Diffuseur"),
                                    ], # Liste des diffuseurs d'offres d'emploi

    "publipostage_champs":  [ ("IDchamp", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du champ"),
                                    ("categorie", "VARCHAR(200)", u"Cat�gorie", u"Cat�gorie du champ"),
                                    ("nom", "VARCHAR(200)", u"Nom", u"Nom du champ"),
                                    ("description", "VARCHAR(400)", u"Description", u"Description du champ"),
                                    ("mot_cle", "VARCHAR(50)", u"Mot-cl�", u"Mot-cl� pour le publipostage"),
                                    ("defaut", "VARCHAR(400)", u"Valeur par d�faut", u"Valeur par d�faut du champ"),
                                    ("exemple", "VARCHAR(100)", u"Exemple", u"Exemple de valeur pour ce champ"),
                                    ], # Champs personnalis�s pour le publipostage.

    "adresses_mail":  [ ("IDadresse", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID"),
                                    ("adresse", "VARCHAR(100)", u"Adresse de messagerie", u"Adresse"),
                                    ("motdepasse", "VARCHAR(100)", u"Mot de passe si SSL", u"mdp"),
                                    ("smtp", "VARCHAR(100)", u"Adresse SMTP", u"Smtp"),
                                    ("port", "INTEGER", u"Num�ro du port", "num port"),
                                    ("connexionssl", "INTEGER", u"Connexion ssl (1/0)", "connexionssl"),
                                    ("defaut", "INTEGER", u"Adresse utilis�e par d�faut (1/0)", "defaut"),
                                    ], # Adresses d'exp�diteur de mail

    "questionnaire_categories": [("IDcategorie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("visible", "INTEGER", u"Visible (0/1)"),
                                    ("type", "VARCHAR(100)", u"Individu ou Famille"),
                                    ("couleur", "VARCHAR(100)", u"Couleur de la cat�gorie"),
                                    ("label", "VARCHAR(400)", u"Label de la question"),
                                    ], # Cat�gories des questionnaires

    "questionnaire_questions": [("IDquestion", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDcategorie", "INTEGER", u"ID de la cat�gorie"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("visible", "INTEGER", u"Visible (0/1)"),
                                    ("label", "VARCHAR(400)", u"Label de la question"),
                                    ("controle", "VARCHAR(200)", u"Nom du contr�le"),
                                    ("defaut", "VARCHAR(400)", u"Valeur par d�faut"),
                                    ("options", "VARCHAR(400)", u"Options de la question"),
                                    ], # Questions des questionnaires

    "questionnaire_choix": [("IDchoix", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDquestion", "INTEGER", u"ID de la question rattach�e"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("visible", "INTEGER", u"Visible (0/1)"),
                                    ("label", "VARCHAR(400)", u"Label de la question"),
                                    ], # Choix de r�ponses des questionnaires

    "questionnaire_reponses": [("IDreponse", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDquestion", "INTEGER", u"ID de la question rattach�e"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu rattach�"),
                                    ("reponse", "VARCHAR(400)", u"R�ponse"),
                                    ], # R�ponses des questionnaires

    }

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

DB_PHOTOS = {

    "photos":[                  ("IDphoto", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID de la photo"),
                                    ("IDindividu", "INTEGER", u"ID de la personne"),
                                    ("photo", "BLOB", u"Photo individu en binaire"),
                                    ], # BLOB photos
    }

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

DB_DOCUMENTS = {

    "documents":[            ("IDdocument", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID du document"),
                                    ("IDpiece", "INTEGER", u"ID de la pi�ce"),
                                    ("IDreponse", "INTEGER", u"ID de la r�ponse du Questionnaire"),
                                    ("document", "LONGBLOB", u"Document converti en binaire"),
                                    ("type", "VARCHAR(50)", u"Type de document : jpeg, pdf..."),
                                    ("label", "VARCHAR(400)", u"Label du document"),
                                    ], # BLOB documents
                                    
    }