#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import sys
import sqlite3
import wx
from Utils import UTILS_Fichiers
import os
import MySQLdb

from Data import DATA_Tables as Tables


class DB:
    def __init__(self, suffixe="DATA", nomFichier="", modeCreation=False):
        """ Utiliser GestionDB.DB(suffixe="PHOTOS") pour accéder à un fichier utilisateur """
        """ Utiliser GestionDB.DB(nomFichier="Geographie.dat", suffixe=None) pour ouvrir un autre type de fichier """
        self.nomFichier = nomFichier
        self.nomFichierCourt = nomFichier
        self.modeCreation = modeCreation
        
        # Si aucun nom de fichier n'est spécifié, on recherche celui par défaut dans le Config.dat
        if self.nomFichier == "" :
            self.nomFichier = self.GetNomFichierDefaut()
        
        # On ajoute le préfixe de type de fichier et l'extension du fichier
        if suffixe != "" and suffixe != None :
            if suffixe[0] != "T" :
                suffixe = _(u"T%s") % suffixe
            if suffixe != None :
                self.nomFichier += u"_%s" % suffixe
        
        # Est-ce une connexion réseau ?
        if "[RESEAU]" in self.nomFichier :
            self.isNetwork = True
        else:
            self.isNetwork = False
            if suffixe != None :
                self.nomFichier = UTILS_Fichiers.GetRepData(u"%s.dat" % self.nomFichier)
        
        # Ouverture de la base de données
        if self.isNetwork == True :
            self.OuvertureFichierReseau(self.nomFichier)
        else:
            self.OuvertureFichierLocal(self.nomFichier)
            
        
    def OuvertureFichierLocal(self, nomFichier):
        """ Version LOCALE avec SQLITE """
        # Vérifie que le fichier sqlite existe bien
        if self.modeCreation == False :
            if os.path.isfile(nomFichier)  == False :
                # Teste si c'est une ancienne version de fichier
                if os.path.isfile(UTILS_Fichiers.GetRepData(u"%s.twk" % self.nomFichierCourt))  == False :
                    print "Le fichier SQLITE demande n'est pas present sur le disque dur."
                    self.echec = 1
                    return
        # Initialisation de la connexion
        try :
            self.connexion = sqlite3.connect(nomFichier.encode('utf-8'))
            self.cursor = self.connexion.cursor()
        except Exception, err:
            print "La connexion avec la base de donnees SQLITE a echouee : \nErreur detectee :%s" % err
            self.erreur = err
            self.echec = 1
        else:
            self.echec = 0
    
    def GetParamConnexionReseau(self):
        """ Récupération des paramètres de connexion si fichier MySQL """
        pos = self.nomFichier.index("[RESEAU]")
        paramConnexions = self.nomFichier[:pos]
        port, host, user, passwd = paramConnexions.split(";")
        nomFichier = self.nomFichier[pos:].replace("[RESEAU]", "")
        nomFichier = nomFichier.lower() 
        dictDonnees = {"port":int(port), "hote":host, "host":host, "user":user, "utilisateur":user, "mdp":passwd, "password":passwd, "fichier":nomFichier}
        return dictDonnees


    def OuvertureFichierReseau(self, nomFichier):
        """ Version RESEAU avec MYSQL """
        try :
            from MySQLdb.constants import FIELD_TYPE
            from MySQLdb.converters import conversions

            # Récupération des paramètres de connexion
            pos = nomFichier.index("[RESEAU]")
            paramConnexions = nomFichier[:pos]
            port, host, user, passwd = paramConnexions.split(";")
            nomFichier = nomFichier[pos:].replace("[RESEAU]", "")
            nomFichier = nomFichier.lower() 
            
            # Connexion MySQL
            my_conv = conversions
            my_conv[FIELD_TYPE.LONG] = int
            self.connexion = MySQLdb.connect(host=host,user=user, passwd=passwd, port=int(port), use_unicode=True, conv=my_conv) # db=dbParam, 
            self.connexion.set_character_set('utf8')
            self.cursor = self.connexion.cursor()
            
            # Ouverture ou création de la base MySQL
            listeDatabases = self.GetListeDatabasesMySQL()
            if nomFichier in listeDatabases :
                # Ouverture Database
                self.cursor.execute("USE %s;" % nomFichier)
            else:
                # Création Database
                self.cursor.execute("CREATE DATABASE IF NOT EXISTS %s CHARSET utf8 COLLATE utf8_unicode_ci;" % nomFichier)
                self.cursor.execute("USE %s;" % nomFichier)
                
        except Exception, err:
            print "La connexion avec la base de donnees MYSQL a echouee : \nErreur detectee :%s" % err
            self.erreur = err
            self.echec = 1
        else:
            self.echec = 0

    def GetNomFichierDefaut(self):
        nomFichier = ""
        try :
            topWindow = wx.GetApp().GetTopWindow()
            nomWindow = topWindow.GetName()
        except :
            nomWindow = None
        if nomWindow == "general" :
            # Si la frame 'General' est chargée, on y récupère le dict de config
            nomFichier = topWindow.userConfig["nomFichier"]
        else:
            # Récupération du nom de la DB directement dans le fichier de config sur le disque dur
            from Utils import UTILS_Config
            cfg = UTILS_Config.FichierConfig()
            nomFichier = cfg.GetItemConfig("nomFichier")
        return nomFichier

    def GetListeDatabasesMySQL(self):
        # Récupère la liste des databases présentes
        listeDatabases = []
        self.cursor.execute("SHOW DATABASES;")
        listeValeurs = self.cursor.fetchall()
        for valeurs in listeValeurs :
            listeDatabases.append(valeurs[0])
        return listeDatabases

    def CreationTables(self, dicoDB={}, fenetreParente=None):
        for table in dicoDB:
            # Affichage dans la StatusBar
            if fenetreParente != None :
                fenetreParente.SetStatusText(_(u"Création de la table de données %s...") % table)
            req = "CREATE TABLE %s (" % table
            pk = ""
            for descr in dicoDB[table]:
                nomChamp = descr[0]
                typeChamp = descr[1]
                # Adaptation à Sqlite
                if self.isNetwork == False and typeChamp == "LONGBLOB" : typeChamp = "BLOB"
                # Adaptation à MySQL :
                if self.isNetwork == True and typeChamp == "INTEGER PRIMARY KEY AUTOINCREMENT" : typeChamp = "INTEGER PRIMARY KEY AUTO_INCREMENT"
                if self.isNetwork == True and typeChamp == "FLOAT" : typeChamp = "REAL"
                if self.isNetwork == True and typeChamp == "DATE" : typeChamp = "VARCHAR(10)"
                if self.isNetwork == True and typeChamp.startswith("VARCHAR") :
                    nbreCaract = int(typeChamp[typeChamp.find("(")+1:typeChamp.find(")")])
                    if nbreCaract > 255 :
                        typeChamp = "TEXT(%d)" % nbreCaract
                # ------------------------------
                req = req + "%s %s, " % (nomChamp, typeChamp)
            req = req[:-2] + ")"
            self.cursor.execute(req)

    def CreationTable(self, nomTable="", dicoDB={}):
        req = "CREATE TABLE %s (" % nomTable
        pk = ""
        for descr in dicoDB[nomTable]:
            nomChamp = descr[0]
            typeChamp = descr[1]
            # Adaptation à Sqlite
            if self.isNetwork == False and typeChamp == "LONGBLOB" : typeChamp = "BLOB"
            # Adaptation à MySQL :
            if self.isNetwork == True and typeChamp == "INTEGER PRIMARY KEY AUTOINCREMENT" : typeChamp = "INTEGER PRIMARY KEY AUTO_INCREMENT"
            if self.isNetwork == True and typeChamp == "FLOAT" : typeChamp = "REAL"
            if self.isNetwork == True and typeChamp == "DATE" : typeChamp = "VARCHAR(10)"
            # ------------------------------
            req = req + "%s %s, " % (nomChamp, typeChamp)
        req = req[:-2] + ")"
        self.cursor.execute(req)
            
    def ExecuterReq(self, req):
        if self.echec == 1 : return False
        # Pour parer le pb des () avec MySQL
        if self.isNetwork == True :
            req = req.replace("()", "(10000000, 10000001)")
        try:
            self.cursor.execute(req)
        except Exception, err:
            print _(u"Requete SQL incorrecte :\n%s\nErreur detectee:\n%s") % (req, err)
            return 0
        else:
            return 1

    def ResultatReq(self):
        if self.echec == 1 : return []
        resultat = self.cursor.fetchall()
        try :
            # Pour contrer MySQL qui fournit des tuples alors que SQLITE fournit des listes
            if self.isNetwork == True and type(resultat) == tuple : 
                resultat = list(resultat)
        except : 
            pass
        return resultat

    def Commit(self):
        if self.connexion:
            self.connexion.commit()

    def Close(self):
        if self.echec == 1 : return
        if self.connexion:
            self.connexion.close()

    def Ajouter(self, table, champs, valeurs):
        # champs et valeurs sont des tuples
        req = "INSERT INTO %s %s VALUES %s" % (table, champs, valeurs)
        self.cursor.execute(req)
        self.connexion.commit()

    def ReqInsert(self, nomTable, listeDonnees):
        """ Permet d'insérer des données dans une table """
        # Préparation des données
        champs = "("
        interr = "("
        valeurs = []
        for donnee in listeDonnees:
            champs = champs + donnee[0] + ", "
            if self.isNetwork == True :
                # Version MySQL
                interr = interr + "%s, "
            else:
                # Version Sqlite
                interr = interr + "?, "
            valeurs.append(donnee[1])
        champs = champs[:-2] + ")"
        interr = interr[:-2] + ")"
        req = "INSERT INTO %s %s VALUES %s" % (nomTable, champs, interr)
        # Enregistrement
        try:
            self.cursor.execute(req, tuple(valeurs))
            self.Commit()
            if self.isNetwork == True :
                # Version MySQL
                self.cursor.execute("SELECT LAST_INSERT_ID();")
            else:
                # Version Sqlite
                self.cursor.execute("SELECT last_insert_rowid() FROM %s" % nomTable)
            newID = self.cursor.fetchall()[0][0]
        except Exception, err:
            print "Requete sql d'INSERT incorrecte :\n%s\nErreur detectee:\n%s" % (req, err)
        # Retourne l'ID de l'enregistrement créé
        return newID
    
    def InsertPhoto(self, IDindividu=None, blobPhoto=None):
        if self.isNetwork == True :
            # Version MySQL
            sql = "INSERT INTO photos (IDindividu, photo) VALUES (%d, '%s')" % (IDindividu, MySQLdb.escape_string(blobPhoto))
            self.cursor.execute(sql)
            self.connexion.commit()
            self.cursor.execute("SELECT LAST_INSERT_ID();")
        else:
            # Version Sqlite
            sql = "INSERT INTO photos (IDindividu, photo) VALUES (?, ?)"
            self.cursor.execute(sql, [IDindividu, sqlite3.Binary(blobPhoto)])
            self.connexion.commit()
            self.cursor.execute("SELECT last_insert_rowid() FROM Photos")
        newID = self.cursor.fetchall()[0][0]
        return newID

    def Executermany(self, req="", listeDonnees=[], commit=True):
        """ Executemany pour local ou réseau """    
        """ Exemple de req : "INSERT INTO table (IDtable, nom) VALUES (?, ?)" """  
        """ Exemple de listeDonnees : [(1, 2), (3, 4), (5, 6)] """     
        # Adaptation réseau/local
        if self.isNetwork == True :
            # Version MySQL
            req = req.replace("?", "%s")
        else:
            # Version Sqlite
            req = req.replace("%s", "?")
        # Executemany
        self.cursor.executemany(req, listeDonnees)
        if commit == True :
            self.connexion.commit()

    def MAJPhoto(self, IDphoto=None, IDindividu=None, blobPhoto=None):
        if self.isNetwork == True :
            # Version MySQL
            sql = "UPDATE photos SET IDindividu=%d, photo='%s' WHERE IDphoto=%d" % (IDindividu, MySQLdb.escape_string(blobPhoto), IDphoto)
            self.cursor.execute(sql)
            self.connexion.commit()
        else:
            # Version Sqlite
            sql = "UPDATE photos SET IDindividu=?, photo=? WHERE IDphoto=%d" % IDphoto
            self.cursor.execute(sql, [IDindividu, sqlite3.Binary(blobPhoto)])
            self.connexion.commit()
        return IDphoto

    def MAJimage(self, table=None, key=None, IDkey=None, blobImage=None, nomChampBlob="image"):
        """ Enregistre une image dans les modes de règlement ou emetteurs """
        if self.isNetwork == True :
            # Version MySQL
            sql = "UPDATE %s SET %s='%s' WHERE %s=%d" % (table, nomChampBlob, MySQLdb.escape_string(blobImage), key, IDkey)
            self.cursor.execute(sql)
            self.connexion.commit()
        else:
            # Version Sqlite
            sql = "UPDATE %s SET %s=? WHERE %s=%d" % (table, nomChampBlob, key, IDkey)
            self.cursor.execute(sql, [sqlite3.Binary(blobImage),])
            self.connexion.commit()

    def ReqMAJ(self, nomTable, listeDonnees, nomChampID, ID, IDestChaine=False):
        """ Permet d'insérer des données dans une table """
        # Préparation des données
        champs = ""
        valeurs = []
        for donnee in listeDonnees:
            if self.isNetwork == True :
                # Version MySQL
                champs = champs + donnee[0] + "=%s, "
            else:
                # Version Sqlite
                champs = champs + donnee[0] + "=?, "
            valeurs.append(donnee[1])
        champs = champs[:-2]
        if IDestChaine == False :
            req = "UPDATE %s SET %s WHERE %s=%d" % (nomTable, champs, nomChampID, ID)
        else:
            req = "UPDATE %s SET %s WHERE %s='%s'" % (nomTable, champs, nomChampID, ID)

        # Enregistrement
        try:
            self.cursor.execute(req, tuple(valeurs))
            self.Commit()
        except Exception, err:
            print _(u"Requete sql de mise a jour incorrecte :\n%s\nErreur detectee:\n%s") % (req, err)
        
    def ReqDEL(self, nomTable, nomChampID, ID):
        """ Suppression d'un enregistrement """
        req = "DELETE FROM %s WHERE %s=%d" % (nomTable, nomChampID, ID)
        try:
            self.cursor.execute(req)
            self.Commit()
        except Exception, err:
            print _(u"Requete sql de suppression incorrecte :\n%s\nErreur detectee:\n%s") % (req, err)
        
    def Modifier(self, table, ID, champs, valeurs, dicoDB):
        # champs et valeurs sont des tuples

        # Recherche du nom de champ ID de la table
        nomID = dicoDB[table][0][0]

        # Creation du détail champs/valeurs à modifier
        detail = ""

        # Vérifie s'il y a plusieurs champs à modifier
        if isinstance(champs, tuple):
            x = 0
            while x < len(champs):
                detail = detail + champs[x] + "='" + valeurs[x] + "', "
                x += 1
            detail = detail[:-2]
        else:
            detail = champs + "='" + valeurs + "'"

        req = "UPDATE %s SET %s WHERE %s=%d" % (table, detail, nomID, ID)
        self.cursor.execute(req)
        self.connexion.commit()

    def Dupliquer(self, nomTable="", nomChampCle="", conditions="", dictModifications={}, renvoieCorrespondances=False, IDmanuel=False):
        """ Dulpliquer un enregistrement d'une table :
             Ex : nomTable="modeles", nomChampCle="IDmodele", ID=22,
             conditions = "IDmodele=12 AND IDtruc>34",
             dictModifications={"nom" : _(u"Copie de modele"), etc...}
             renvoieCorrespondance = renvoie un dict de type {ancienID : newID, etc...}
             IDmanuel = Attribue le IDprécédent de la table + 1 (pour parer au bug de la table tarifs_ligne
        """
        listeNewID = []
        # Recherche des noms de champs
        listeChamps = []
        for nom, type, info in Tables.DB_DATA[nomTable] :
            listeChamps.append(nom)
            
        # Importation des données
        texteConditions = ""
        if len(conditions) > 0 : 
            texteConditions = "WHERE %s" % conditions
        req = "SELECT * FROM %s %s;" % (nomTable, texteConditions)
        self.ExecuterReq(req)
        listeDonnees = self.ResultatReq()
        if len(listeDonnees) == 0 : 
            return None
            
        # Copie des données
        dictCorrespondances = {}
        for enregistrement in listeDonnees :
            listeTemp = []
            index = 0
            ID = None
            for nomChamp in listeChamps :
                valeur = enregistrement[index]
                if dictModifications.has_key(nomChamp):
                    valeur = dictModifications[nomChamp]
                if nomChamp != nomChampCle :
                    listeTemp.append((nomChamp, valeur))
                else:
                    ID = valeur # C'est la clé originale
                    
                    # Si saisie manuelle du nouvel ID
                    if IDmanuel == True :
                        req = """SELECT max(%s) FROM %s;""" % (nomChampCle, nomTable)
                        self.ExecuterReq(req)
                        temp = self.ResultatReq()
                        if temp[0][0] == None : 
                            newIDmanuel = 1
                        else:
                            newIDmanuel = temp[0][0] + 1
                        listeTemp.append((nomChampCle, newIDmanuel))
                        
                index += 1
            newID = self.ReqInsert(nomTable, listeTemp)
            if IDmanuel == True :
                newID = newIDmanuel
            listeNewID.append(newID)
            dictCorrespondances[ID] = newID
            
        # Renvoie les correspondances
        if renvoieCorrespondances == True :
            return dictCorrespondances
        
        # Renvoie les newID
        if len(listeNewID) == 1 :
            return listeNewID[0]
        else:
            return listeNewID

    def GetProchainID(self, nomTable=""):
        if self.isNetwork == False :
            # Version Sqlite
            req = "SELECT seq FROM sqlite_sequence WHERE name='%s';" % nomTable
            self.ExecuterReq(req)
            donnees = self.ResultatReq()
        else:
            # Version MySQL
            self.ExecuterReq("USE information_schema;")
            pos = self.nomFichier.index("[RESEAU]")
            nomFichier = self.nomFichier[pos:].replace("[RESEAU]", "")
            req = "SELECT auto_increment FROM tables WHERE table_schema='%s' and table_name='%s' ;" % (nomFichier, nomTable)
            self.ExecuterReq(req)
            donnees = self.ResultatReq()
        if len(donnees) > 0 :
            ID = donnees[0][0] + 1
            return ID
        else:
            return None
    
    def IsTableExists(self, nomTable=""):
        """ Vérifie si une table donnée existe dans la base """
        tableExists = False
        for (nomTableTmp,) in self.GetListeTables() :
            if nomTableTmp == nomTable :
                tableExists = True
        return tableExists
                        
    def GetListeTables(self):
        if self.isNetwork == False :
            # Version Sqlite
            req = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
            self.ExecuterReq(req)
            listeTables = self.ResultatReq()
        else:
            # Version MySQL
            req = "SHOW TABLES;"
            self.ExecuterReq(req)
            listeTables = self.ResultatReq()
        return listeTables

    def GetListeChamps(self):
        """ Affiche la liste des champs de la précédente requête effectuée """
        liste = []
        for fieldDesc in self.cursor.description:
            liste.append(fieldDesc[0])
        return liste

    def GetListeChamps2(self, nomTable=""):
        """ Affiche la liste des champs de la table donnée """
        listeChamps = []
        if self.isNetwork == False :
            # Version Sqlite
            req = "PRAGMA table_info('%s');" % nomTable
            self.ExecuterReq(req)
            listeTmpChamps = self.ResultatReq()
            for valeurs in listeTmpChamps :
                listeChamps.append( (valeurs[1], valeurs[2]) )
        else:
            # Version MySQL
            req = "SHOW COLUMNS FROM %s;" % nomTable
            self.ExecuterReq(req)
            listeTmpChamps = self.ResultatReq()
            for valeurs in listeTmpChamps :
                listeChamps.append( (valeurs[0], valeurs[1]) )
        return listeChamps
    
    def SupprChamp(self, nomTable="", nomChamp = ""):
        """ Suppression d'une colonne dans une table """
        if self.isNetwork == False :
            # Version Sqlite

            # Recherche des noms de champs de la table
    ##        req = """
    ##        SELECT sql FROM sqlite_master
    ##        WHERE name='%s'
    ##        """ % nomTable
    ##        self.ExecuterReq(req)
    ##        reqCreate = self.ResultatReq()[0][0]
    ##        posDebut = reqCreate.index("(")+1
    ##        champs = reqCreate[posDebut:-1]
    ##        listeChamps = champs.split(", ")
            
            listeChamps = self.GetListeChamps2(nomTable)
        
            index = 0
            varChamps = ""
            varNomsChamps = ""
            for nomTmp, typeTmp in listeChamps :
                if nomTmp == nomChamp :
                    listeChamps.pop(index)
                    break
                else:
                    varChamps += "%s %s, " % (nomTmp, typeTmp)
                    varNomsChamps += nomTmp + ", "
                index += 1
            varChamps = varChamps[:-2]
            varNomsChamps = varNomsChamps[:-2]
        
            # Procédure de mise à jour de la table                
            req = ""
            req += "BEGIN TRANSACTION;"
            req += "CREATE TEMPORARY TABLE %s_backup(%s);" % (nomTable, varChamps)
            req += "INSERT INTO %s_backup SELECT %s FROM %s;" % (nomTable, varNomsChamps, nomTable)
            req += "DROP TABLE %s;" % nomTable
            req += "CREATE TABLE %s(%s);" % (nomTable, varChamps)
            req += "INSERT INTO %s SELECT %s FROM %s_backup;" % (nomTable, varNomsChamps, nomTable)
            req += "DROP TABLE %s_backup;" % nomTable
            req += "COMMIT;"
            self.cursor.executescript(req)
        
        else:
            # Version MySQL
            req = "ALTER TABLE %s DROP %s;" % (nomTable, nomChamp)
            self.ExecuterReq(req)
            self.Commit()
            
    def AjoutChamp(self, nomTable = "", nomChamp = "", typeChamp = ""):
        req = "ALTER TABLE %s ADD %s %s;" % (nomTable, nomChamp, typeChamp)
        self.ExecuterReq(req)
        self.Commit()
        
    def Importation_table(self, nomTable="", nomFichierdefault="Defaut.dat"):
        """ Importe toutes les données d'une table donnée """
        # Ouverture de la base par défaut
        try:
            connexionDefaut = sqlite3.connect(nomFichierdefault.encode('utf-8'))
        except Exception, err:
            print "Echec Importation table. Erreur detectee :%s" % err
            echec = 1
        else:
            cursor = connexionDefaut.cursor()
            echec = 0

        # Recherche des noms de champs de la table
        req = "SELECT * FROM %s" % nomTable
        cursor.execute(req)
        listeDonneesTmp = cursor.fetchall()
        listeChamps = []
        for fieldDesc in cursor.description:
            listeChamps.append(fieldDesc[0])
            
        # Préparation des noms de champs pour le transfert
        txtChamps = "("
        txtQMarks = "("
        for nomChamp in listeChamps[0:] :
            txtChamps += nomChamp + ", "
            if self.isNetwork == True :
                # Version MySQL
                txtQMarks += "%s, "
            else:
                # Version Sqlite
                txtQMarks += "?, "
        txtChamps = txtChamps[:-2] + ")"
        txtQMarks = txtQMarks[:-2] + ")"

        # Récupération des données
        listeDonnees = []
        for donnees in listeDonneesTmp :
            listeDonnees.append(donnees[0:])
        
        # Importation des données vers la nouvelle table
        req = "INSERT INTO %s %s VALUES %s" % (nomTable, txtChamps, txtQMarks)
        self.cursor.executemany(req, listeDonnees)
        self.connexion.commit()

    def Importation_table_reseau(self, nomTable="", nomFichier="", dictTables={}):
        """ Importe toutes les données d'une table donnée dans un fichier réseau """
        import cStringIO
        
        # Ouverture de la base réseau
        try :
            from MySQLdb.constants import FIELD_TYPE
            from MySQLdb.converters import conversions

            # Récupération des paramètres de connexion
            pos = nomFichier.index("[RESEAU]")
            paramConnexions = nomFichier[:pos]
            port, host, user, passwd = paramConnexions.split(";")
            nomFichier = nomFichier[pos:].replace("[RESEAU]", "")
            nomFichier = nomFichier.lower() 
            
            # Connexion MySQL
            my_conv = conversions
            my_conv[FIELD_TYPE.LONG] = int
            connexionDefaut = MySQLdb.connect(host=host,user=user, passwd=passwd, port=int(port), use_unicode=True, conv=my_conv) # db=dbParam, 
            connexionDefaut.set_character_set('utf8')
            cursor = connexionDefaut.cursor()
            
            # Ouverture Database
            cursor.execute("USE %s;" % nomFichier)
            
        except Exception, err:
            print "La connexion avec la base de donnees MYSQL a importer a echouee : \nErreur detectee :%s" % err
            erreur = err
            echec = 1
        else:
            echec = 0

        # Recherche des noms de champs de la table
        req = "SELECT * FROM %s" % nomTable
        cursor.execute(req)
        listeDonneesTmp = cursor.fetchall()
        listeChamps = []
        for fieldDesc in cursor.description:
            listeChamps.append(fieldDesc[0])
        
        # Préparation des noms de champs pour le transfert
        txtChamps = "("
        txtQMarks = "("
        for nomChamp in listeChamps[0:] :
            txtChamps += nomChamp + ", "
            txtQMarks += "?, "
        txtChamps = txtChamps[:-2] + ")"
        txtQMarks = txtQMarks[:-2] + ")"

        # Récupération des données
        listeDonnees = []
        for donnees in listeDonneesTmp :
            # Analyse des données pour trouver les champs BLOB
            numColonne = 0
            listeValeurs = []
            for donnee in donnees[0:] :
                typeChamp = dictTables[nomTable][numColonne][1]
                if typeChamp == "BLOB" :
                    if donnee != None :
                        donnee = sqlite3.Binary(donnee)
                listeValeurs.append(donnee)
                numColonne += 1
            listeDonnees.append(tuple(listeValeurs))
        
        # Importation des données vers la nouvelle table
        req = "INSERT INTO %s %s VALUES %s" % (nomTable, txtChamps, txtQMarks)
        self.cursor.executemany(req, listeDonnees)
        self.connexion.commit()

    def Importation_valeurs_defaut(self, listeDonnees=[]):
        """ Importe dans la base de données chargée toutes les valeurs de la base des valeurs par défaut """
        # Récupération du dictionnaire des tables Optionnelles pour l'importation
        if len(listeDonnees) == 0 :
            listeTablesOptionnelles = Tables.TABLES_IMPORTATION_OPTIONNELLES # DICT_TABLES_IMPORTATION
        else:
            listeTablesOptionnelles = listeDonnees
        
        # Importation des tables optionnelles
        for nomCategorie, listeTables, selection in listeTablesOptionnelles :
            if selection == True :
                for nomTable in listeTables :
                    self.Importation_table(nomTable)
        
        # Importation des tables obligatoires
        for nomTable in Tables.TABLES_IMPORTATION_OBLIGATOIRES :
            self.Importation_table(nomTable)

        return True

    def Exportation_vers_base_defaut(self, nomTable="", nomFichierdefault="Defaut.dat"):
        """ Exporte toutes les données d'une table donnée vers la base défaut """
        # Ouverture de la base par défaut
        connexionDefaut = sqlite3.connect(nomFichierdefault.encode('utf-8'))
        cursorDefaut = connexionDefaut.cursor()
        
        # Création de la table dans la base DEFAUT si elle n'existe pas
        req = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';" % nomTable
        cursorDefaut.execute(req)
        listeTemp = cursorDefaut.fetchall()
        if len(listeTemp) == 0 :
            req = "CREATE TABLE %s (" % nomTable
            pk = ""
            for descr in Tables.DB_DATA[nomTable]:
                nomChamp = descr[0]
                typeChamp = descr[1]
                if self.isNetwork == False and typeChamp == "LONGBLOB" : typeChamp = "BLOB"
                req = req + "%s %s, " % (nomChamp, typeChamp)
            req = req[:-2] + ")"
            cursorDefaut.execute(req)
        
        # Recherche des noms de champs de la table
        listeChamps = self.GetListeChamps2(nomTable)
        
        # Récupération des données à exporter
        req = "SELECT * FROM %s" % nomTable
        self.ExecuterReq(req)
        listeDonnees = self.ResultatReq()
            
        # Préparation des noms de champs pour le transfert
        txtChamps = "("
        txtQMarks = "("
        for nomChamp, typeChamp in listeChamps :
            txtChamps += nomChamp + ", "
            txtQMarks += "?, "
        txtChamps = txtChamps[:-2] + ")"
        txtQMarks = txtQMarks[:-2] + ")"

        # Récupération des données
        listeDonnees2 = []
        for donnees in listeDonnees :
            listeDonnees2.append(donnees[0:])
        
        # Importation des données vers la nouvelle table
        req = "INSERT INTO %s %s VALUES %s" % (nomTable, txtChamps, txtQMarks)
        cursorDefaut.executemany(req, listeDonnees2)
        connexionDefaut.commit()


# ------------- Fonctions de MAJ de la base de données ---------------------------------------------------------------
        
    def ConversionDB(self, versionFichier=(0, 0, 0, 0) ) :
        """ Adapte un fichier obsolète à la version actuelle du logiciel """
        
        # Filtres de conversion
        
        # =============================================================
        
        # Filtre pour passer de la version 1 à la version 2 de Teamworks
        versionFiltre = (2, 0, 0, 0)
        if versionFichier < versionFiltre :   
            try :
                from Utils import UTILS_Procedures
                UTILS_Procedures.A2000(nomFichier=self.nomFichierCourt)
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================
        
        versionFiltre = (2, 0, 0, 1)
        if versionFichier < versionFiltre :   
            try :
                if self.IsTableExists("questionnaire_questions") == False : self.CreationTable("questionnaire_questions", Tables.DB_DATA)
                if self.IsTableExists("questionnaire_categories") == False : self.CreationTable("questionnaire_categories", Tables.DB_DATA)
                if self.IsTableExists("questionnaire_choix") == False : self.CreationTable("questionnaire_choix", Tables.DB_DATA)
                if self.IsTableExists("questionnaire_reponses") == False : self.CreationTable("questionnaire_reponses", Tables.DB_DATA)
                from Utils import UTILS_Procedures
                UTILS_Procedures.D1051(nomFichier=self.nomFichierCourt)
            except Exception, err :
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)
        
        # =============================================================

        versionFiltre = (2, 1, 0, 1)
        if versionFichier < versionFiltre:
            try:
                if self.IsTableExists("profils") == False: self.CreationTable("profils", Tables.DB_DATA)
                if self.IsTableExists("profils_parametres") == False: self.CreationTable("profils_parametres", Tables.DB_DATA)
            except Exception, err:
                return " filtre de conversion %s | " % ".".join([str(x) for x in versionFiltre]) + str(err)

        # =============================================================


        return True

def ConversionLocalReseau(nomFichier="", nouveauFichier="", fenetreParente=None):
    """ Convertit une DB locale en version RESEAU MySQL """
    print "Lancement de la procedure de conversion local->reseau :"
    
    for suffixe, dictTables in ( ("TDATA", Tables.DB_DATA), ("TPHOTOS", Tables.DB_PHOTOS), ("TDOCUMENTS", Tables.DB_DOCUMENTS) ) :
        
        nomFichierActif = UTILS_Fichiers.GetRepData(u"%s_%s.dat" % (nomFichier, suffixe))
        nouveauNom = nouveauFichier[nouveauFichier.index("[RESEAU]"):].replace("[RESEAU]", "")
        
        dictResultats = TestConnexionMySQL(typeTest="fichier", nomFichier=u"%s_%s" % (nouveauFichier, suffixe) )
        # Vérifie la connexion au réseau
        if dictResultats["connexion"][0] == False :
            erreur = dictResultats["connexion"][1]
            dlg = wx.MessageDialog(None, _(u"La connexion au réseau MySQL est impossible. \n\nErreur : %s") % erreur, "Erreur de connexion", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            print "connexion reseau MySQL impossible."
            return False
        # Vérifie que le fichier n'est pas déjà utilisé
        if dictResultats["fichier"][0] == True :
            dlg = wx.MessageDialog(None, _(u"Le fichier existe déjà."), "Erreur de création de fichier", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            print "le nom existe deja."
            return False
        
        # Création de la base de données
        if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Création du fichier réseau..."))
        db = DB(suffixe=suffixe, nomFichier=nouveauFichier, modeCreation=True)
        if db.echec == 1 :
            erreur = db.erreur
            dlg = wx.MessageDialog(None, _(u"Erreur dans la création du fichier.\n\nErreur : %s") % erreur, _(u"Erreur de création de fichier"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        print "  > Nouveau fichier reseau %s cree..." % suffixe
        
        # Création des tables
        if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Création des tables de données %s...") % suffixe)
        db.CreationTables(dicoDB=dictTables)
        print "  > Nouvelles tables %s creees..." % suffixe
        
        # Importation des valeurs
        listeTables = dictTables.keys()
        index = 1
        for nomTable in listeTables :
            print "  > Importation de la table '%s' (%d/%d)" % (nomTable, index, len(listeTables))
            if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Importation de la table %d sur %s...") % (index, len(listeTables)))
            db.Importation_table(nomTable, nomFichierActif)
            print "     -> ok"
            index += 1
        
        db.Close() 
    
    print "  > Conversion terminee avec succes."
            

def ConversionReseauLocal(nomFichier="", nouveauFichier="", fenetreParente=None):
    """ Convertit une DB RESEAU MySQL en version LOCALE SQLITE """
    print "Lancement de la procedure de conversion reseau->local :"
    
    for suffixe, dictTables in ( ("TDATA", Tables.DB_DATA), ("TPHOTOS", Tables.DB_PHOTOS), ("TDOCUMENTS", Tables.DB_DOCUMENTS) ) :
        
        nomFichierActif = nomFichier[nomFichier.index("[RESEAU]"):].replace("[RESEAU]", "") 
        nouveauNom = UTILS_Fichiers.GetRepData(u"%s_%s.dat" % (nomFichier, suffixe))
        
        # Vérifie que le fichier n'est pas déjà utilisé
        if os.path.isfile(nouveauNom)  == True :
            dlg = wx.MessageDialog(None, _(u"Le fichier existe déjà."), "Erreur de création de fichier", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            print "le nom existe deja."
            return False
        
        # Création de la base de données
        if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Création du fichier local..."))
        db = DB(suffixe=suffixe, nomFichier=nouveauFichier, modeCreation=True)
        if db.echec == 1 :
            erreur = db.erreur
            dlg = wx.MessageDialog(None, _(u"Erreur dans la création du fichier.\n\nErreur : %s") % erreur, _(u"Erreur de création de fichier"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        print "  > Nouveau fichier local %s cree..." % suffixe
        
        # Création des tables
        if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Création des tables de données %s...") % suffixe)
        db.CreationTables(dicoDB=dictTables)
        print "  > Nouvelles tables %s creees..." % suffixe
        
        # Importation des valeurs
        listeTables = dictTables.keys()
        index = 1
        for nomTable in listeTables :
            print "  > Importation de la table '%s' (%d/%d)" % (nomTable, index, len(listeTables))
            if fenetreParente != None : fenetreParente.SetStatusText(_(u"Conversion du fichier en cours... Importation de la table %d sur %s...") % (index, len(listeTables)))
            db.Importation_table_reseau(nomTable, u"%s_%s" % (nomFichier, suffixe), dictTables)
            print "     -> ok"
            index += 1
        
        db.Close() 
    
    print "  > Conversion reseau->local terminee avec succes."


def TestConnexionMySQL(typeTest="fichier", nomFichier=""):
    """ typeTest=fichier ou reseau """
    dictResultats = {}
    # Récupération du nom de fichier court
    pos = nomFichier.index("[RESEAU]")
    paramConnexions = nomFichier[:pos]
    port, host, user, passwd = paramConnexions.split(";")
    nomFichier = nomFichier[pos+8:]
    nomFichier = nomFichier.lower() 
    
    # Test de connexion au réseau MySQL
    try :
        connexion = MySQLdb.connect(host=host,user=user, passwd=passwd, port=int(port), use_unicode=True) # db=dbParam, 
        connexion.set_character_set('utf8')
        cursor = connexion.cursor()
        dictResultats["connexion"] =  (True, None)
        etatConnexion = True
    except Exception, err :
        dictResultats["connexion"] =  (False, err)
        etatConnexion = False
    
    # Test de connexion à une base de données
    if typeTest == "fichier" and etatConnexion == True :
        try :
            listeDatabases = []
            cursor.execute("SHOW DATABASES;")
            listeValeurs = cursor.fetchall()
            for valeurs in listeValeurs :
                listeDatabases.append(valeurs[0])
            if nomFichier in listeDatabases :
                # Ouverture Database
                cursor.execute("USE %s;" % nomFichier)
                dictResultats["fichier"] =  (True, None)
            else:
                dictResultats["fichier"] =  (False, _(u"Accès au fichier impossible."))
        except Exception, err :
            dictResultats["fichier"] =  (False, err)
    
    try :
        connexion.close() 
    except :
        pass
    
    return dictResultats


# ----------------------------------------------------------------------------------------------------------------------------------------
        
##import MySQLdb
##base = MySQLdb.connect(host="localhost",user="root", passwd="motdepasse", port=3306, use_unicode=True) # db=dbParam, 
##cursor = base.cursor()
##cursor.execute("USE testsql;")
##cursor.execute("SHOW VARIABLES like 'character_set_%';")
##base.set_character_set('utf8')
##print cursor.fetchall()
##valeur = _(u"2 euros > 2€")
##cursor.execute("INSERT INTO t1 (champ1) VALUES ('%s');" % valeur.encode("utf-8") ) 
##base.commit()
##base.close()


##db = DB()
##db.Importation_valeurs_defaut()
##print "valeurs par defaut importees."
##db.Close()


##if __name__ == "__main__":
##    #blobtestMYSQL()
##    blobtestSQLITE()
    
##    db = DB()
##    db.AjoutChamp(nomTable = "modeles_planning", nomChamp = "inclureferies", typeChamp = "INTEGER")
##    db.Close()
                        
def ImporterFichierDonnees() :
    db = DB(nomFichier="Prenoms.dat", suffixe=None, modeCreation=True)
    db.CreationTable("prenoms", DB_DATA2)
    db.Close()
    
    txt = open("prenoms.txt", 'r').readlines()
    db = DB(nomFichier="Prenoms.dat", suffixe=None)
    index = 0
    for ligne in txt :
        ID, prenom, genre = ligne.split(";")
        listeDonnees = [("prenom", prenom.decode("iso-8859-15") ), ("genre", genre.decode("iso-8859-15")),]
        IDprenom = db.ReqInsert("prenoms", listeDonnees)
        index += 1
    db.Close()



# Création des tables tests pour le module RECRUTEMENT
if __name__ == "__main__":
                    
    # Création d'une table données
    db = DB(suffixe="DATA")
    listeTables = ("questionnaire_questions", "questionnaire_categories", "questionnaire_choix", "questionnaire_reponses")
    for nomTable in listeTables :
        db.CreationTable(nomTable, Tables.DB_DATA)
    db.Close()
    print "creation tables ok."         
           
## ----------------------------------------------------------------------

##    # Création de toutes les tables
##    db = DB(suffixe="DATA", modeCreation=True)
##    import Tables
##    dicoDB = Tables.DB_DATA
##    db.CreationTables(dicoDB)
##    db.Close()
##    print "creation des tables DATA ok."
##    db = DB(suffixe="PHOTOS", modeCreation=True)
##    import Tables
##    dicoDB = Tables.DB_PHOTOS
##    db.CreationTables(dicoDB)
##    db.Close()
##    print "creation des tables PHOTOS ok."
    
##    db = DB(nomFichier="Prenoms.dat", suffixe=None)
##    for IDprenom in range(1, 12555):
##        req = """SELECT prenom, genre FROM prenoms WHERE IDprenom=%d;""" % IDprenom
##        db.ExecuterReq(req)
##        listePrenoms = db.ResultatReq()
##        genre = listePrenoms[0][1]
##        if genre.endswith("\n") :
##            listeDonnees = [ ("genre", genre[:-1]),]
##            db.ReqMAJ("prenoms", listeDonnees, "IDprenom", IDprenom)
##    db.Close()
        
    
##    db = DB() 
##    db.AjoutChamp("tarifs", "groupes", "VARCHAR(300)")
##    db.Close()
