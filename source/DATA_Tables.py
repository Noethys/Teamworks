#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Teamworks Gestion d'équipes
# Site internet :  teamworks.forumactif.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

TABLES_IMPORTATION_OPTIONNELLES = [ # [Nom Categorie, (liste des tables...,), Selectionné]
        [u"diplômes et pièces", ("types_pieces", "types_diplomes", "diplomes_pieces"), True],
        [u"Périodes de vacances", ("periodes_vacances",), True],
        [u"Jours fériés", ("jours_feries",), True],
        [u"Catégories de présences", ("cat_presences",), True],
        [u"Situations professionelles", ("situations",), True],
        [u"Données de contrats", ("contrats_champs", "contrats_class", "contrats_modeles", "contrats_types", "contrats_valchamps", "valeurs_point"), True],
        #[u"Pays", ("pays",), True],
        ]

TABLES_IMPORTATION_OBLIGATOIRES = ["gadgets", "pays"]


DB_DATA = {

    "personnes":[           ("IDpersonne", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la personne"),
                                    ("civilite", "VARCHAR(5)", u"Civilité", u"Civilité de la personne"),
                                    ("nom", "VARCHAR(100)", u"Nom", u"Nom de famille de la personne"),
                                    ("nom_jfille", "VARCHAR(100)", u"Nom de jeune fille", u"Nom de jeune fille de la personne"),
                                    ("prenom", "VARCHAR(100)", u"Prénom", u"Prénom de la personne"),
                                    ("date_naiss", "DATE", "Date de naissance", u"Date de naissance de la personne"),
                                    ("cp_naiss", "INTEGER", u"CP naissance", u"Code postal du lieu de naissance de la personne"),
                                    ("ville_naiss", "VARCHAR(100)", u"Ville naissance", u"Ville du lieu de naissance de la personne"),
                                    ("pays_naiss", "INTEGER", u"Pays naissance", u"ID du Pays de naissance de la personne"),
                                    ("nationalite", "INTEGER", u"Nationalité", u"Nationalité de la personne"),
                                    ("num_secu", "VARCHAR(21)", u"Num Sécu", u"Numéro de sécurité sociale de la personne"),
                                    ("adresse_resid", "VARCHAR(200)", "Adresse", u"Adresse de la personne"),
                                    ("cp_resid", "INTEGER", u"Code postal", u"Code postal de la personne"),
                                    ("ville_resid", "VARCHAR(100)", u"Ville", u"Ville de la personne"),
                                    ("memo", "VARCHAR(800)", u"Mémo", u"Mémo sur la personne"),
                                    ("IDsituation", "INTEGER", u"ID", u"ID de la situation sociale"),
                                    ("cadre_photo", "VARCHAR(200)", u"Cadre", u"Cadre photo rattaché"),
                                    ("texte_photo", "VARCHAR(300)", u"Texte", u"Texte de la photo rattachée"),
                                    ], # Données sur les personnes

    "situations":[          ("IDsituation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la situation sociale"),
                                    ("situation", "VARCHAR(400)", u"Situation", u"Situation sociale"),
                                    ], # Liste des situations sociales possibles

    "coordonnees":[         ("IDcoord", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la coordonnée"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID de la personne"),
                                    ("categorie", "VARCHAR(100)", u"Catégorie", u"Catégorie"),
                                    ("texte", "VARCHAR(50)", u"Texte", u"Texte"),
                                    ("intitule", "VARCHAR(300)", u"Intitulé", u"Intitulé"),
                                    ], # Liste des coordonnées de la personne

    "diplomes":[            ("IDdiplome", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du diplome"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID de la personne"),
                                    ("IDtype_diplome", "INTEGER", u"IDtype_diplome", u"ID du type de diplome"),
                                    ], # Liste des diplomes saisis pour chaque personne

    "types_diplomes":[      ("IDtype_diplome", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du type de diplome"),
                                    ("nom_diplome", "VARCHAR(200)", u"Diplôme", u"Nom du type de diplôme"),
                                    ], # Types de diplomes des personnes. Apparait dans Diplomes.

    "pieces":[              ("IDpiece", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la pièce"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID de la personne"),
                                    ("IDtype_piece", "INTEGER", u"IDtype_piece", u"ID du type de pièce"),
                                    ("date_debut", "DATE", u"Début validité", u"Date de début de validité"),
                                    ("date_fin", "DATE", u"Fin validité", u"Date de fin de validité"),
                                    ], # Liste des pièces saisies pour chaque personne

    "types_pieces":[        ("IDtype_piece", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du type de pièce"),
                                    ("nom_piece", "VARCHAR(200)", u"Pièce", u"Nom de la pièce"),
                                    ("duree_validite", "VARCHAR(100)", u"Durée validité", u"Durée par défaut de la validité de la pièce"),
                                    ], # Liste des types de pièces possibles. Apparait dans Pieces et diplomes_pieces.

    "diplomes_pieces":[     ("IDdiplome_piece", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du type de pièce"),
                                    ("IDtype_diplome", "INTEGER", u"IDdiplome", u"ID du diplome"),
                                    ("IDtype_piece", "INTEGER", u"IDtype_piece", u"ID du type de pièce"),
                                    ], # Table des liaisons entre les tables Diplomes et Types_pieces. Permet d'attribuer des types de pièces à des diplomes.

    "contrats":[                ("IDcontrat", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du contrat"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID de la personne"),
                                    ("IDclassification", "INTEGER", u"IDclassification", u"Classification du contrat"),
                                    ("IDtype", "INTEGER", u"IDtype", u"ID du type de contrat"),
                                    ("valeur_point", "INTEGER", u"ID Valeur du point", u"ID de la valeur du point"),
                                    ("date_debut", "DATE", u"Début validité", u"Date de début du contrat"),
                                    ("date_fin", "DATE", u"Fin validité", u"Date de fin du contrat"),
                                    ("date_rupture", "DATE", u"Date Rupture", u"Date de rupture anticipée du contrat"),
                                    ("essai", "INTEGER", u"Période d'essai", u"Nombre de jours de période d'essai"),
                                    ("signature", "VARCHAR(3)", u"Signé?", u"Contrat signé ? (oui/non)"),
                                    ("due", "VARCHAR(3)", u"DUE", u"DUE faite ? (oui/non)"),
                                    ], # Contrats = postes occupés par la personne sur la structure

    "contrats_class":       [("IDclassification", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la classification du poste"),
                                    ("nom", "VARCHAR(200)", u"Classification", u"Nom de la classification du poste"),
                                    ], # Classification du poste. Ex : "personnel de service", "Animateur BAFA", "Directeur Permanent CVL"...

    "contrats_types":       [("IDtype", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du type de contrat"),
                                    ("nom", "VARCHAR(300)", u"Type de contrat", u"Nom du type de contrat"),
                                    ("nom_abrege", "VARCHAR(10)", u"Type de contrat", u"Nom abrégé du type de contrat"),
                                    ("duree_indeterminee", "VARCHAR(3)", u"Durée indéterminée", u"Type de contrat à durée indéterminée (oui/non)"),
                                    ], # Type de contrat = "CEE", "CDD", "CDI", "Convention de bénévolat"...

    "valeurs_point":        [("IDvaleur_point", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la valeur du point"),
                                    ("valeur", "REAL", u"Valeur du point", u"Valeur du point"),
                                    ("date_debut", "DATE", u"Date de début de validité", u"Date de début de validité de la valeur du point"),
                                    ], # Valeur actuel du point... Apparait dans Contrats

    "contrats_modeles": [ ("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du modèle de contrat"),
                                    ("nom", "VARCHAR(300)", u"Nom", u"Nom du modèle de contrat"),
                                    ("description", "VARCHAR(400)", u"Description", u"Description du modèle de contrat"),
                                    ("IDclassification", "INTEGER", u"IDclassification", u"Classification du contrat"),
                                    ("IDtype", "INTEGER", u"IDtype", u"ID du type de contrat"),
                                    ], # Modèles de contrats.

    "contrats_champs":  [ ("IDchamp", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du champ"),
                                    ("nom", "VARCHAR(300)", u"Nom", u"Nom du champ"),
                                    ("description", "VARCHAR(400)", u"Description", u"Description du champ"),
                                    ("mot_cle", "VARCHAR(50)", u"Mot-clé", u"Mot-clé pour le publipostage"),
                                    ("defaut", "VARCHAR(800)", u"Valeur par défaut", u"Valeur par défaut du champ"),
                                    ("exemple", "VARCHAR(200)", u"Exemple", u"Exemple de valeur pour ce champ"),
                                    ], # Champs personnalisés pour les contrats.

    "contrats_valchamps":  [ ("IDval_champ", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la valeur du champ"),
                                    ("IDchamp", "INTEGER", u"IDchamp", u"ID du champ"),
                                    ("type", "VARCHAR(10)", u"Type de champ", u"Type de champ (contrat ou modele)"),
                                    ("IDcontrat", "INTEGER", u"IDcontrat", u"ID du contrat"),
                                    ("IDmodele", "INTEGER", u"IDmodele", u"ID du modele"),
                                    ("valeur", "VARCHAR(800)", u"Description", u"Description du champ"),
                                    ], # Valeurs des champs pour les contrats et les modèles de contrats.
                                                                        
    "presences":[           ("IDpresence", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la presence"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID de la personne"),
                                    ("date", "DATE", u"DATE", u"Date de la présence"),
                                    ("heure_debut", "DATE", u"Heure de début", u"Heure de début"),
                                    ("heure_fin", "DATE", u"Heure de fin", u"Heure de fin"),
                                    ("IDcategorie", "INTEGER", u"Catégorie", u"Catégorie du travail effectué"),
                                    ("intitule", "VARCHAR(200)", u"Intitulé", u"Intitulé du travail effectué"),
                                    ], # Présences du personnel

    "cat_presences":[       ("IDcategorie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la catégorie de présence"),
                                    ("nom_categorie", "VARCHAR(200)", u"Catégorie", u"Nom de la catégorie de la présence"),
                                    ("IDcat_parent", "INTEGER", u"ID de la catégorie parente", u"ID de la catégorie parente"),
                                    ("ordre", "INTEGER", u"Ordre", u"Ordre dans l'arborescence des catégories"),
                                    ("couleur", "VARCHAR(30)", u"Couleur", u"Couleur de la catégorie"),
                                    ], # Catégories de présences. Ex : "Réunion", "Congés payés"... Apparait dans Présences

    "periodes_vacances":[     ("IDperiode", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID periode vacances"),
                                    ("nom", "VARCHAR(100)", "Nom de la période", u"Nom de la période de vacances"),
                                    ("annee", "VARCHAR(4)", "Année de la période", u"Année de la période de vacances"),
                                    ("date_debut", "DATE", "Date de début", u"Date de début"),
                                    ("date_fin", "DATE", "Date de fin", u"Date de fin"),
                                    ], # Calendrier des jours de vacances

    "jours_feries":[             ("IDferie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID jour férié"),
                                    ("type", "VARCHAR(10)", "Type", u"Type de jour férié : fixe ou variable"),
                                    ("nom", "VARCHAR(100)", "Nom du jour férié", u"Nom du jour férié"),
                                    ("jour", "INTEGER", "Jour de la date", u"Jour de la date"),
                                    ("mois", "INTEGER", "Mois de la date", u"Mois de la date"),
                                    ("annee", "INTEGER", "Année de la date", u"Année de la date"),
                                    ], # Calendrier des jours fériés variables et fixes

    "modeles_planning":[    ("IDmodele", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID modèle de planning"),
                                    ("nom", "VARCHAR(300)", u"Nom", u"Nom du modèle"),
                                    ("type", "VARCHAR(5)", u"Type", u"Type de modèle"),
                                    ("description", "VARCHAR(400)", u"Description", u"Description du modèle"),
                                    ("periodes", "VARCHAR(3)", u"Périodes", u"Périodes d'application du modèle"),
                                    ("inclureferies", "INTEGER", u"Inclure Fériés", u"Inclure les jours fériés"),
                                    ], # Modèles de planning

    "modeles_taches":[      ("IDtache", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID tâche modèle"),
                                    ("IDmodele", "INTEGER", u"IDmodèle", u"ID modèle rattaché"),
                                    ("type", "VARCHAR(5)", u"Type", u"Type de modèle"),
                                    ("periode", "INTEGER", u"Période", u"Période d'application de la tâche"),
                                    ("jour", "INTEGER", u"Jour", u"Jour d'application"),
                                    ("heure_debut", "DATE", u"Heure de début", u"Heure de début"),
                                    ("heure_fin", "DATE", u"Heure de fin", u"Heure de fin"),
                                    ("IDcategorie", "INTEGER", u"Catégorie", u"Catégorie de la tâche"),
                                    ("intitule", "VARCHAR(200)", u"Intitulé", u"Intitulé de la tâche"),
                                    ], # Tâches pour les Modèles de planning

    "due_valeurs":[          ("IDvaleur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"IDvaleur"),
                                    ("code", "VARCHAR(50)", u"Code", u"Code d'identification du champ"),
                                    ("valeur", "VARCHAR(200)", u"Valeur", u"Valeur du champ"),
                                    ], # Valeurs sauvegardées pour le document DUE.

    "pays":[                    ("IDpays", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID pays"),
                                    ("code_drapeau", "VARCHAR(50)", u"Code drapeau", u"Code drapeau associé"),
                                    ("nom", "VARCHAR(100)", u"Nom", u"Nom du pays"),
                                    ("nationalite", "VARCHAR(100)", u"Nationalité", u"Nationalité correspondante"),
                                    ], # Liste des pays, drapeaux et nationalités
                                    
    "divers":[                   ("IDdivers", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID divers"),
                                    ("motdepasse", "VARCHAR(50)", u"Mot de passe", u"Mot de passe du fichier"),
                                    ("date_derniere_ouverture", "DATE", u"Date", u"Date de dernière ouverture du fichier"),
                                    ("date_creation_fichier", "DATE", u"Date", u"Date de création du fichier"),
                                    ("version_DB", "INTEGER", u"Version", u"Version de la base de données"),
                                    ("save_active", "INTEGER", u"Activation", u"Sauvegarde autom. activée (1/0)"),
                                    ("save_frequence", "INTEGER", u"Fréquence", u"Fréquence des sauvegardes auto."),
                                    ("save_elements", "VARCHAR(500)", u"Elements", u"Elements des sauvegardes auto."),
                                    ("save_destination", "VARCHAR(500)", u"Destination", u"Répertoire de destination des sauvegardes auto."),
                                    ("save_conservation", "INTEGER", u"Conservation", u"Nbre exemplaires conservés des sauvegardes auto."),
                                    ("save_date_derniere", "DATE", u"Date dernière", u"Date de la dernière sauvegarde"),
                                    ("codeIDfichier", "VARCHAR(20)", u"ID fichier", u"Identifiant unique de fichier"),
                                    ], # Données diverses


    "gadgets":[                ("IDgadget", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID gadget"),
                                    ("nom", "VARCHAR(50)", u"Nom", u"Nom du gadget"),
                                    ("label", "VARCHAR(50)", u"Label", u"Label du gadget"),
                                    ("description", "VARCHAR(400)", u"Description", u"Description du gadget"),
                                    ("taille", "VARCHAR(50)", u"Taille", u"Taille du gadget"),
                                    ("affichage", "VARCHAR(5)", u"Affichage(True/False)", u"Affichage du gadget"),
                                    ("ordre", "INTEGER", u"Ordre", u"Numéro d'ordre d'affichage"),
                                    ("config", "VARCHAR(5)", u"config(True/False)", u"config(True/False)"),
                                    ("parametres", "VARCHAR(500)", u"Paramètres", u"Paramètres du gadget"),
                                    ], # Paramètres des gadgets de la page d'accueil


    "parametres":[           ("IDparametre", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID parametre"),
                                    ("categorie", "VARCHAR(100)", u"Catégorie", u"Catégorie"),
                                    ("nom", "VARCHAR(100)", u"Nom", u"Nom"),
                                    ("parametre", "VARCHAR(300)", u"Parametre", u"Parametre"),
                                    ], # Paramètres divers


    "distances":[              ("IDdistance", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID distance"),
                                    ("cp_depart", "VARCHAR(5)", u"CP départ", u"CP de la ville de départ"),
                                    ("ville_depart", "VARCHAR(200)", u"Ville départ", u"Nom de la ville de départ"),
                                    ("cp_arrivee", "VARCHAR(5)", u"CP arrivée", u"CP de la ville d'arrivée"),
                                    ("ville_arrivee", "VARCHAR(200)", u"Ville arrivée", u"Nom de la ville d'arrivée"),
                                    ("distance", "FLOAT", u"Distance", u"Distance en Km"),
                                    ], # Liste des distances entre les villes pour les frais de déplacements

    "deplacements":[       ("IDdeplacement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID déplacement"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID de la personne"),
                                    ("date", "DATE", u"Date", u"Date du déplacement"),
                                    ("objet", "VARCHAR(100)", u"Objet", u"Objet du déplacement"),
                                    ("cp_depart", "VARCHAR(5)", u"CP départ", u"CP de la ville de départ"),
                                    ("ville_depart", "VARCHAR(200)", u"Ville départ", u"Nom de la ville de départ"),
                                    ("cp_arrivee", "VARCHAR(5)", u"CP arrivée", u"CP de la ville d'arrivée"),
                                    ("ville_arrivee", "VARCHAR(200)", u"Ville arrivée", u"Nom de la ville d'arrivée"),
                                    ("distance", "FLOAT", u"Distance", u"Distance en Km"),
                                    ("aller_retour", "VARCHAR(5)", u"Aller_retour(True/False)", u"Aller_retour(True/False)"),
                                    ("tarif_km", "FLOAT", u"Tarif du Km", u"Tarif du Km en euros"),
                                    ("IDremboursement", "INTEGER", u"IDremboursement", u"ID du remboursement"),
                                    ], # Liste des déplacements

    "remboursements":[    ("IDremboursement", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDremboursement", u"ID remboursement"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID de la personne"),
                                    ("date", "DATE", u"Date", u"Date du remboursement"),
                                    ("montant", "FLOAT", u"Montant", u"Montant total du remboursement"),
                                    ("listeIDdeplacement", "VARCHAR(300)", u"Déplacements", u"Liste des IDdeplacements"),
                                    ], # Liste des remboursements de frais de déplacements

    "scenarios":[             ("IDscenario", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDscenario", u"ID scenario"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID de la personne"),
                                    ("nom", "VARCHAR(200)", u"Nom", u"Nom du scénario"),
                                    ("description", "VARCHAR(400)", u"Description", u"Description du scénario"),
                                    ("mode_heure", "INTEGER", u"Mode", u"Mode (heure/décimal)"),
                                    ("detail_mois", "INTEGER", u"Détail mois", u"Détail répartition par mois"),
                                    ("date_debut", "DATE", u"Date début", u"Date de début de période"),
                                    ("date_fin", "DATE", u"Date fin", u"Date de fin de période"),
                                    ("toutes_categories", "INTEGER", u"Inclure toutes catégories", u"Inclure toutes catégories"),
                                    ], # Liste des scénarios

    "scenarios_cat":[       ("IDscenario_cat", "INTEGER PRIMARY KEY AUTOINCREMENT", u"IDscenario_cat", u"ID scenario catégorie"),
                                    ("IDscenario", "INTEGER", u"IDscenario", u"IDscenario"),
                                    ("IDcategorie", "INTEGER", u"IDcategorie", u"IDcategorie"),
                                    ("prevision", "VARCHAR(50)", u"Prévision", u"Prévision"),
                                    ("report", "VARCHAR(50)", u"Report", u"Report"),
                                    ("date_debut_realise", "DATE", u"Date début Réalisé", u"Date de début de période Réalisé"),
                                    ("date_fin_realise", "DATE", u"Date fin Réalisé", u"Date de fin de période Réalisé"),
                                    ], # Liste des catégories de scénarios

    "candidats":[             ("IDcandidat", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du candidat"),
                                    ("civilite", "VARCHAR(5)", u"Civilité", u"Civilité du candidat"),
                                    ("nom", "VARCHAR(100)", u"Nom", u"Nom de famille de la candidate"),
                                    ("prenom", "VARCHAR(100)", u"Prénom", u"Prénom du candidat"),
                                    ("date_naiss", "DATE", u"Date de naissance", u"Date de naissance du candidat"),
                                    ("age", "INTEGER", u"Age", u"Age du candidat si date de naissance inconnue"),
                                    ("adresse_resid", "VARCHAR(200)", "Adresse", u"Adresse du candidat"),
                                    ("cp_resid", "INTEGER", u"Code postal", u"Code postal du candidat"),
                                    ("ville_resid", "VARCHAR(200)", u"Ville", u"Ville du candidat"),
                                    ("memo", "VARCHAR(300)", u"Mémo", u"Mémo sur la personne"),
                                    ], # Données sur les candidats

    "coords_candidats":[  ("IDcoord", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la coordonnée"),
                                    ("IDcandidat", "INTEGER", u"IDcandidat", u"ID du candidat"),
                                    ("categorie", "VARCHAR(50)", u"Catégorie", u"Catégorie"),
                                    ("texte", "VARCHAR(50)", u"Texte", u"Texte"),
                                    ("intitule", "VARCHAR(200)", u"Intitulé", u"Intitulé"),
                                    ], # Liste des coordonnées du candidat

    "diplomes_candidats":[("IDdiplome", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du diplome"),
                                    ("IDcandidat", "INTEGER", u"IDcandidat", u"ID du candidat"),
                                    ("IDtype_diplome", "INTEGER", u"IDtype_diplome", u"ID du type de diplome"),
                                    ], # Liste des diplomes saisis pour les candidats

    "entretiens":[             ("IDentretien", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de l'entretien"),
                                    ("IDcandidat", "INTEGER", u"IDcandidat", u"ID du candidat"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID du salarié"),
                                    ("date", "DATE", u"Date de l'entretien", u"Date de l'entretien"),
                                    ("heure", "DATE", u"Heure", u"Heure de l'entretien"),
                                    ("avis", "INTEGER", u"Avis", u"Avis sur l'entretien"),
                                    ("remarques", "VARCHAR(500)", u"Remarques", u"Remarques sur l'entretien"),
                                    ], # Liste des entretiens du candidat

    "disponibilites":[         ("IDdisponibilite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la disponibilite"),
                                    ("IDcandidature", "INTEGER", u"IDcandidature", u"ID de la candidature"),
                                    ("date_debut", "DATE", u"DATE", u"Date de début"),
                                    ("date_fin", "DATE", u"DATE", u"Date de fin"),
                                    ], # Liste des disponibilités du candidat
                                    
    "fonctions":[              ("IDfonction", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la fonction"),
                                    ("fonction", "VARCHAR(500)", u"Fonction", u"Fonction candidat"),
                                    ], # Liste des fonctions demandées par les candidats

    "affectations":[          ("IDaffectation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de l'affectation"),
                                    ("affectation", "VARCHAR(500)", u"Affectation", u"Affectation candidat"),
                                    ], # Liste des affectations demandées par les candidats

    "candidatures":[         ("IDcandidature", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la candidature"),
                                    ("IDcandidat", "INTEGER", u"IDcandidat", u"ID du candidat"),
                                    ("IDpersonne", "INTEGER", u"IDpersonne", u"ID du salarié"),
                                    ("date_depot", "DATE", u"Date de la candidature", u"Date de la candidature"),
                                    ("IDtype", "INTEGER", u"IDtype", u"ID du type de candidature"),
                                    ("acte_remarques", "VARCHAR(500)", u"Remarques", u"Remarques sur le dépôt de candidature"),
                                    ("IDemploi", "INTEGER", u"IDemploi", u"ID de l'emploi"),
                                    ("periodes_remarques", "VARCHAR(500)", u"Remarques", u"Remarques sur les disponibilités"),
                                    ("poste_remarques", "VARCHAR(500)", u"Remarques", u"Remarques sur le poste de la candidature"),
                                    ("IDdecision", "INTEGER", u"IDdecision", u"ID de la décision"),
                                    ("decision_remarques", "VARCHAR(500)", u"Remarques", u"Remarques sur la décision"),
                                    ("reponse_obligatoire", "INTEGER", u"Reponse obligatoire", u"Réponse obligatoire (0 ou 1)"),
                                    ("reponse", "INTEGER", u"Reponse", u"Réponse de la candidature (0 ou 1)"),
                                    ("date_reponse", "DATE", u"Date de la réponse", u"Date de la réponse"),
                                    ("IDtype_reponse", "INTEGER", u"IDtype", u"ID du type de réponse"),
                                    ], # Liste des candidatures du candidat
                                    
    "cand_fonctions":[      ("IDcand_fonction", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID"),
                                    ("IDcandidature", "INTEGER", u"ID", u"ID de la candidature"),
                                    ("IDfonction", "INTEGER", u"ID", u"ID de la fonction"),
                                    ], # Liste des fonctions demandées par les candidats

    "cand_affectations":[  ("IDcand_affectation", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID"),
                                    ("IDcandidature", "INTEGER", u"ID", u"ID de la candidature"),
                                    ("IDaffectation", "INTEGER", u"ID", u"ID de l'affectation"),
                                    ], # Liste des affectations demandées par les candidats

    "emplois":[                ("IDemploi", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de l'emploi"),
                                    ("date_debut", "DATE", u"Date début", u"Date de début de recrutement"),
                                    ("date_fin", "DATE", u"Date fin", u"Date de fin de recrutement"),
                                    ("intitule", "VARCHAR(300)", u"Intitulé", u"Intitulé de l'offre d'emploi"),
                                    ("detail", "VARCHAR(800)", u"Détail", u"Détail de l'offre d'emploi"),
                                    ("reference_anpe", "VARCHAR(100)", u"Référence", u"Référence ANPE"),
                                    ("periodes_remarques", "VARCHAR(300)", u"Remarques", u"Remarques sur les disponibilités"),
                                    ("poste_remarques", "VARCHAR(300)", u"Remarques", u"Remarques sur le poste"),
                                    ], # Liste des offres d'emploi

    "emplois_dispo":[       ("IDdisponibilite", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID de la disponibilite"),
                                    ("IDemploi", "INTEGER", u"IDemploi", u"ID de l'emploi"),
                                    ("date_debut", "DATE", u"DATE", u"Date de début"),
                                    ("date_fin", "DATE", u"DATE", u"Date de fin"),
                                    ], # Liste des disponibilités d'une offre d'emploi

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
                                    ], # Liste des diffuseurs utilisés pour un offre d'emploi

    "diffuseurs":[              ("IDdiffuseur", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du diffuseur"),
                                    ("diffuseur", "VARCHAR(400)", u"Diffuseur", u"Diffuseur"),
                                    ], # Liste des diffuseurs d'offres d'emploi

    "publipostage_champs":  [ ("IDchamp", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID du champ"),
                                    ("categorie", "VARCHAR(200)", u"Catégorie", u"Catégorie du champ"),
                                    ("nom", "VARCHAR(200)", u"Nom", u"Nom du champ"),
                                    ("description", "VARCHAR(400)", u"Description", u"Description du champ"),
                                    ("mot_cle", "VARCHAR(50)", u"Mot-clé", u"Mot-clé pour le publipostage"),
                                    ("defaut", "VARCHAR(400)", u"Valeur par défaut", u"Valeur par défaut du champ"),
                                    ("exemple", "VARCHAR(100)", u"Exemple", u"Exemple de valeur pour ce champ"),
                                    ], # Champs personnalisés pour le publipostage.

    "adresses_mail":  [ ("IDadresse", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID", u"ID"),
                                    ("adresse", "VARCHAR(100)", u"Adresse de messagerie", u"Adresse"),
                                    ("motdepasse", "VARCHAR(100)", u"Mot de passe si SSL", u"mdp"),
                                    ("smtp", "VARCHAR(100)", u"Adresse SMTP", u"Smtp"),
                                    ("port", "INTEGER", u"Numéro du port", "num port"),
                                    ("connexionssl", "INTEGER", u"Connexion ssl (1/0)", "connexionssl"),
                                    ("defaut", "INTEGER", u"Adresse utilisée par défaut (1/0)", "defaut"),
                                    ], # Adresses d'expéditeur de mail

    "questionnaire_categories": [("IDcategorie", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("visible", "INTEGER", u"Visible (0/1)"),
                                    ("type", "VARCHAR(100)", u"Individu ou Famille"),
                                    ("couleur", "VARCHAR(100)", u"Couleur de la catégorie"),
                                    ("label", "VARCHAR(400)", u"Label de la question"),
                                    ], # Catégories des questionnaires

    "questionnaire_questions": [("IDquestion", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDcategorie", "INTEGER", u"ID de la catégorie"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("visible", "INTEGER", u"Visible (0/1)"),
                                    ("label", "VARCHAR(400)", u"Label de la question"),
                                    ("controle", "VARCHAR(200)", u"Nom du contrôle"),
                                    ("defaut", "VARCHAR(400)", u"Valeur par défaut"),
                                    ("options", "VARCHAR(400)", u"Options de la question"),
                                    ], # Questions des questionnaires

    "questionnaire_choix": [("IDchoix", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDquestion", "INTEGER", u"ID de la question rattachée"),
                                    ("ordre", "INTEGER", u"Ordre"),
                                    ("visible", "INTEGER", u"Visible (0/1)"),
                                    ("label", "VARCHAR(400)", u"Label de la question"),
                                    ], # Choix de réponses des questionnaires

    "questionnaire_reponses": [("IDreponse", "INTEGER PRIMARY KEY AUTOINCREMENT", u"ID"),
                                    ("IDquestion", "INTEGER", u"ID de la question rattachée"),
                                    ("IDindividu", "INTEGER", u"ID de l'individu rattaché"),
                                    ("reponse", "VARCHAR(400)", u"Réponse"),
                                    ], # Réponses des questionnaires

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
                                    ("IDpiece", "INTEGER", u"ID de la pièce"),
                                    ("IDreponse", "INTEGER", u"ID de la réponse du Questionnaire"),
                                    ("document", "LONGBLOB", u"Document converti en binaire"),
                                    ("type", "VARCHAR(50)", u"Type de document : jpeg, pdf..."),
                                    ("label", "VARCHAR(400)", u"Label du document"),
                                    ], # BLOB documents
                                    
    }