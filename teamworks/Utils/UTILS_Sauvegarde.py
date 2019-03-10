#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import os
import zipfile
import GestionDB
import subprocess
import shutil
import time

from Utils import UTILS_Config
from Utils import UTILS_Cryptage_fichier
from Utils import UTILS_Envoi_email
from Utils import UTILS_Fichiers


LISTE_CATEGORIES = [
    (_(u"Donn�es de base"), "TDATA"),
    (_(u"Photos individuelles"), "TPHOTOS"),
    (_(u"Documents"), "TDOCUMENTS"),
    ]

EXTENSIONS = {
    "decrypte" : "twd",
    "crypte" : "twc",
    }



def Sauvegarde(listeFichiersLocaux=[], listeFichiersReseau=[], nom="", repertoire=None, motdepasse=None, listeEmails=None, dictConnexion=None):
    """ Processus de de cr�ation du ZIP """
    # Si aucun fichier � sauvegarder
    if len(listeFichiersLocaux) == 0 and len(listeFichiersReseau) == 0 : 
        return False
    
    # Initialisation de la barre de progression
    nbreEtapes = 3
    nbreEtapes += len(listeFichiersLocaux)
    nbreEtapes += len(listeFichiersReseau)
    if motdepasse != None : nbreEtapes += 1
    if repertoire != None : nbreEtapes += 1
    if listeEmails != None : nbreEtapes += 2
    dlgprogress = wx.ProgressDialog(_(u"Sauvegarde"), _(u"Lancement de la sauvegarde..."), maximum=nbreEtapes, parent=None,
                                                 style= wx.PD_SMOOTH | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
    dlgprogress.SetSize((320, -1))
    
    # Cr�ation du fichier ZIP temporaire
    nomFichierTemp = u"%s.%s" % (nom, EXTENSIONS["decrypte"])
    fichierZip = zipfile.ZipFile(UTILS_Fichiers.GetRepTemp(nomFichierTemp), "w", compression=zipfile.ZIP_DEFLATED)
    numEtape = 1
    dlgprogress.Update(numEtape, _(u"Cr�ation du fichier de compression..."))
    numEtape += 1
    
    # Int�gration des fichiers locaux
    for nomFichier in listeFichiersLocaux :
        dlgprogress.Update(numEtape, _(u"R�cup�ration du fichier %s...") % nomFichier)
        numEtape += 1
        fichier = UTILS_Fichiers.GetRepData(nomFichier)
        fichierZip.write(fichier, nomFichier)
    
    # Int�gration des fichiers r�seau
    if len(listeFichiersReseau) > 0 and dictConnexion != None :
        
##        # R�cup�ration des infos de connexion MySQL
##        DB = GestionDB.DB()
##        dictConnexion = DB.GetParamConnexionReseau()
##        DB.Close() 
        
        # Cr�ation du r�pertoire temporaire
        repTemp = UTILS_Fichiers.GetRepTemp("savetemp")
        if os.path.isdir(repTemp) == True :
            shutil.rmtree(repTemp)
        os.mkdir(repTemp)
        
        # Recherche du r�pertoire d'installation de MySQL
        repMySQL = GetRepertoireMySQL(dictConnexion) 
        if repMySQL == None :
            dlgErreur = wx.MessageDialog(None, _(u"Teamworks n'a pas r�ussi � localiser MySQL sur votre ordinateur.\nNotez bien que MySQL doit �tre install� obligatoirement pour cr�er une sauvegarde r�seau."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErreur.ShowModal() 
            dlgErreur.Destroy()
            dlgprogress.Destroy()
            return False
        
        # Cr�ation du backup pour chaque fichier MySQL
        for nomFichier in listeFichiersReseau :
            dlgprogress.Update(numEtape, _(u"R�cup�ration du fichier %s...") % nomFichier)
            numEtape += 1
            fichierSave = _(u"%s/%s.sql") % (repTemp, nomFichier)
            try :
                sql = """"%(REP_MYSQL)sbin/mysqldump" --host=%(SQL_HOST)s --port=%(SQL_PORT)s --user=%(SQL_USER)s --password=%(SQL_PASS)s --single-transaction --opt --databases %(SQL_DB)s > %(DB_BACKUP)s""" % {
                                'REP_MYSQL' : repMySQL,
                                'SQL_HOST' : dictConnexion["host"],
                                'SQL_PORT' : dictConnexion["port"],
                                'SQL_USER' : dictConnexion["user"],
                                'SQL_PASS' : dictConnexion["password"],
                                'SQL_DB' : nomFichier,
                                'DB_BACKUP' : fichierSave,
                                }
                os.system(sql)
            except Exception as err:
                print(err)
                dlgErreur = wx.MessageDialog(None, _(u"L'erreur suivante a �t� d�tect�e dans la sauvegarde :\n%s.\n\n(Attention, notez bien que MySQL doit �tre install� sur votre poste)") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlgErreur.ShowModal() 
                dlgErreur.Destroy()
                dlgprogress.Destroy()
                return False
            
            # Ins�re le fichier Sql dans le ZIP
            try :
                fichierZip.write(fichierSave, _(u"%s.sql") % nomFichier) #.decode("iso-8859-15")
            except Exception as err:
                dlgErreur = wx.MessageDialog(None, _(u"Une erreur est survenue dans la restauration...\n\n(Attention, notez bien que MySQL doit �tre install� sur votre poste)") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                dlgErreur.ShowModal() 
                dlgErreur.Destroy()
                dlgprogress.Destroy()
                return False
            
        # Supprime le r�pertoire temp
        shutil.rmtree(repTemp)
        
    # Finalise le fichier ZIP
    fichierZip.close()
    
    # Cryptage du fichier
    if motdepasse != None :
        dlgprogress.Update(numEtape, _(u"Cryptage du fichier..."))
        numEtape += 1
        fichierCrypte = u"%s.%s" % (nom, EXTENSIONS["crypte"])
        UTILS_Cryptage_fichier.CrypterFichier(UTILS_Fichiers.GetRepTemp(nomFichierTemp), UTILS_Fichiers.GetRepTemp(fichierCrypte), motdepasse)
        nomFichierTemp = fichierCrypte
        extension = EXTENSIONS["crypte"]
    else:
        extension = EXTENSIONS["decrypte"]
    
    # Copie le fichier obtenu dans le r�pertoire donn�
    if repertoire != None :
        dlgprogress.Update(numEtape, _(u"Cr�ation du fichier dans le r�pertoire cible..."))
        numEtape += 1
        fichierDest = u"%s/%s.%s" % (repertoire, nom, extension)
        # Si le fichier de destination existe d�j� :
        if os.path.isfile(fichierDest) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier de sauvegarde portant ce nom existe d�j�. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                dlgprogress.Destroy()
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()
        # Copie
        shutil.copy2(UTILS_Fichiers.GetRepTemp(nomFichierTemp), fichierDest)
    
    # Envoi par Email
    if listeEmails != None :
        dlgprogress.Update(numEtape, _(u"R�cup�ration de l'adresse d'exp�dition par d�faut..."))
        numEtape += 1
        
        # R�cup�ration des param�tres de l'adresse d'exp�diteur par d�faut
        dictAdresse = UTILS_Envoi_email.GetAdresseExpDefaut()
        if dictAdresse == None :
            dlgErreur = wx.MessageDialog(None, _(u"Envoi par Email impossible :\n\nAucune adresse d'exp�diteur n'a �t� d�finie.\nVeuillez la saisir dans le menu Param�trage du logiciel..."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErreur.ShowModal() 
            dlgErreur.Destroy()
            dlgprogress.Destroy()
            return False
        
        dlgprogress.Update(numEtape, _(u"Exp�dition par Email... patientez..."))
        numEtape += 1
        
        # Envoi
        try :
            etat = UTILS_Envoi_email.Envoi_mail( 
                adresseExpediteur=dictAdresse["adresse"], 
                listeDestinataires=listeEmails, 
                #listeDestinatairesCCI=[], 
                sujetMail=_(u"Sauvegarde Teamworks : %s") % nom, 
                texteMail=_(u"Envoi de la sauvegarde de Teamworks"), 
                listeFichiersJoints=[UTILS_Fichiers.GetRepTemp(nomFichierTemp),],
                serveur=dictAdresse["smtp"], 
                port=dictAdresse["port"], 
                ssl=dictAdresse["connexionssl"], 
                #listeImages=listeImages,
                )
        except Exception as err:
            dlgErreur = wx.MessageDialog(None, _(u"L'erreur suivante a �t� d�tect�e dans l'envoi par Email :\n%s.") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErreur.ShowModal() 
            dlgErreur.Destroy()
            dlgprogress.Destroy()
            return False
    
    # Suppression des r�pertoires et fichiers temporaires
    dlgprogress.Update(numEtape, _(u"Suppression des fichiers temporaires..."))
    numEtape += 1
    fichier = UTILS_Fichiers.GetRepTemp(u"%s.%s" % (nom, EXTENSIONS["decrypte"]))
    if os.path.isfile(fichier) == True :
        os.remove(fichier)
    fichier = UTILS_Fichiers.GetRepTemp(u"%s.%s" % (nom, EXTENSIONS["crypte"]))
    if os.path.isfile(fichier) == True :
        os.remove(fichier)
    
    # Fin du processus
    dlgprogress.Update(numEtape, _(u"Sauvegarde termin�e avec succ�s."))
    dlgprogress.Destroy()
    
    return True

def VerificationZip(fichier=""):
    """ V�rifie que le fichier est une archive zip valide """
    return zipfile.is_zipfile(fichier)
    
def GetListeFichiersZIP(fichier):
    """ R�cup�re la liste des fichiers du ZIP """
    listeFichiers = []
    fichierZip = zipfile.ZipFile(fichier, "r")
    for fichier in fichierZip.namelist() :
        listeFichiers.append(fichier)
    return listeFichiers
    
def Restauration(fichier="", listeFichiersLocaux=[], listeFichiersReseau=[], dictConnexion=None):
    """ Restauration � partir des listes de fichiers locaux et r�seau """
    # Initialisation de la barre de progression
    nbreEtapes = 1
    nbreEtapes += len(listeFichiersLocaux) * 2
    if len(listeFichiersReseau) > 0 :
        nbreEtapes += 3
        nbreEtapes += len(listeFichiersReseau) * 3
    dlgprogress = wx.ProgressDialog(_(u"Restauration"), _(u"Lancement de la restauration..."), maximum=nbreEtapes, parent=None,
                                                 style= wx.PD_SMOOTH | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
    dlgprogress.SetSize((350, -1))
    numEtape = 1
    
    fichierZip = zipfile.ZipFile(fichier, "r")
    
    # Restauration des fichiers locaux Sqlite
    for fichier in listeFichiersLocaux :
        
        dlgprogress.Update(numEtape, _(u"Recherche si le fichier %s existe d�j�...") % fichier);numEtape += 1
    
        # On v�rifie que le fichier n'existe pas d�j� dans le r�pertoire de destination
        if os.path.isfile(UTILS_Fichiers.GetRepData(fichier)) == True :
            dlg = wx.MessageDialog(None, _(u"Le fichier '%s' existe d�j�. \n\nVoulez-vous le remplacer ?") % fichier, "Attention !", wx.YES_NO | wx.CANCEL |wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse == wx.ID_NO :
                validation = False                    
            elif reponse == wx.ID_YES :
                validation = True
            else :
                validation = "stop"
                dlg2 = wx.MessageDialog(None, _(u"Arr�t du processus de restauration."), _(u"Restauration"), wx.OK| wx.ICON_INFORMATION)  
                dlg2.ShowModal()
                dlg2.Destroy()
                fichierZip.close()
                dlgprogress.Destroy()
                return False
        else:
            validation = True               
        
        # On restaure le fichier
        if validation == True :
            dlgprogress.Update(numEtape, _(u"Restauration du fichier %s...") % fichier);numEtape += 1
            try :
                buffer = fichierZip.read(fichier)
                f = open(UTILS_Fichiers.GetRepData(fichier), "wb")
                f.write(buffer)
                f.close()
            except Exception as err:
                dlg = wx.MessageDialog(None, _(u"La restauration du fichier '") + nomFichier + _(u"' a rencontr� l'erreur suivante : \n") + err, "Erreur", wx.OK| wx.ICON_ERROR)  
                dlg.ShowModal()
                dlg.Destroy()
        else:
            dlgprogress.Update(numEtape, u"");numEtape += 1
        
    # Restauration des fichiers r�seau MySQL
    if len(listeFichiersReseau) > 0 :
        
##        DB = GestionDB.DB() 
##        if DB.echec == 1 :
##            dlg = wx.MessageDialog(None, _(u"Noethys n'arrive pas � acc�der � la base de donn�es. \n\nProc�dure de restauration interrompue."), "Erreur", wx.OK| wx.ICON_ERROR)  
##            dlg.ShowModal()
##            dlg.Destroy()
##            dlgprogress.Destroy()
##            return False
##        
##        if DB.isNetwork == False :
##            dlg = wx.MessageDialog(None, _(u"Vous devez obligatoirement . \n\nProc�dure de restauration interrompue."), "Erreur", wx.OK| wx.ICON_ERROR)  
##            dlg.ShowModal()
##            dlg.Destroy()
##            dlgprogress.Destroy()
##            return False
                
        # R�cup�ration de la liste des fichiers MySQL de l'ordinateur
        dlgprogress.Update(numEtape, _(u"Recherche les fichiers r�seau existants..."));numEtape += 1
        listeFichiersExistants = GetListeFichiersReseau(dictConnexion)

        # Recherche du r�pertoire d'installation de MySQL
        repMySQL = GetRepertoireMySQL(dictConnexion) 
        if repMySQL == None :
            dlgErreur = wx.MessageDialog(None, _(u"Teamworks n'a pas r�ussi � localiser MySQL sur votre ordinateur.\nNotez bien que MySQL doit �tre install� obligatoirement pour cr�er une restauration r�seau."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlgErreur.ShowModal() 
            dlgErreur.Destroy()
            dlgprogress.Destroy()
            return False

        # Cr�ation du r�pertoire temporaire
        dlgprogress.Update(numEtape, _(u"Cr�ation du r�pertoire temporaire..."));numEtape += 1
        repTemp = UTILS_Fichiers.GetRepTemp("restoretemp")
        if os.path.isdir(repTemp) == True :
            shutil.rmtree(repTemp)
        os.mkdir(repTemp)

        for fichier in listeFichiersReseau :
            fichier = fichier[:-4]
            
            # On v�rifie que le fichier n'existe pas d�j� dans le r�pertoire de destination
            dlgprogress.Update(numEtape, _(u"Recherche si le fichier %s existe d�j�...") % fichier);numEtape += 1
            if fichier in listeFichiersExistants :
                dlg = wx.MessageDialog(None, _(u"Le fichier '%s' existe d�j�. \n\nVoulez-vous le remplacer ?") % fichier, "Attention !", wx.YES_NO | wx.CANCEL |wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse == wx.ID_NO :
                    validation = False                    
                elif reponse == wx.ID_YES :
                    validation = True
                else :
                    validation = "stop"
                    dlg2 = wx.MessageDialog(None, _(u"Arr�t du processus de restauration."), _(u"Restauration"), wx.OK| wx.ICON_INFORMATION)  
                    dlg2.ShowModal()
                    dlg2.Destroy()
                    fichierZip.close()
                    dlgprogress.Destroy()
                    return False
            else:
                validation = True
                # Cr�ation de la base si elle n'existe pas
                nomFichier = _(u"%s;%s;%s;%s[RESEAU]%s") % (dictConnexion["port"], dictConnexion["host"], dictConnexion["user"], dictConnexion["password"], fichier)
                DB = GestionDB.DB(suffixe=None, nomFichier=nomFichier)
                DB.Close()
                
            # On restaure le fichier
            if validation == True :
                
                fichierRestore = _(u"%s/%s.sql") % (repTemp, fichier)
                
                # Copie du fichier SQL dans le r�pertoire Temp/restoretemp
                dlgprogress.Update(numEtape, _(u"Copie du fichier %s dans le r�pertoire temporaire...") % fichier);numEtape += 1
                buffer = fichierZip.read(_(u"%s.sql") % fichier)
                f = open(fichierRestore, "wb")
                f.write(buffer)
                f.close()
                
                # Importation du fichier SQL dans MySQL
                dlgprogress.Update(numEtape, _(u"Restauration du fichier %s... veuillez patienter...") % fichier);numEtape += 1
                try :
                    sql = """"%(REP_MYSQL)sbin/mysql" --host=%(SQL_HOST)s --port=%(SQL_PORT)s --user=%(SQL_USER)s --password=%(SQL_PASS)s %(SQL_DB)s < %(DB_BACKUP)s""" % {
                                    'REP_MYSQL' : repMySQL,
                                    'SQL_HOST' : dictConnexion["host"],
                                    'SQL_PORT' : dictConnexion["port"],
                                    'SQL_USER' : dictConnexion["user"],
                                    'SQL_PASS' : dictConnexion["password"],
                                    'SQL_DB' : fichier,
                                    'DB_BACKUP' : fichierRestore,
                                    }
                    os.system(sql)
                except Exception as err:
                    dlgErreur = wx.MessageDialog(None, _(u"L'erreur suivante a �t� d�tect�e dans la restauration :\n%s.\n\n(Attention, notez bien que MySQL doit �tre install� sur votre poste)") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                    dlgErreur.ShowModal() 
                    dlgErreur.Destroy()
                    dlgprogress.Destroy()
                    return False

            else:
                dlgprogress.Update(numEtape, u"");numEtape += 1
                dlgprogress.Update(numEtape, u"");numEtape += 1

        
        # Supprime le r�pertoire temp
        dlgprogress.Update(numEtape, _(u"Suppression du r�pertoire temporaire..."));numEtape += 1
        shutil.rmtree(repTemp)

    # Fin de la proc�dure
    dlgprogress.Update(numEtape, _(u"Fin de la restauration"))
    fichierZip.close()

def GetListeFichiersReseau(dictValeurs={}):
    """ R�cup�re la liste des fichiers MySQL existants 
         dictValeurs = valeurs de connexion
    """
    import MySQLdb
    connexion = MySQLdb.connect(host=dictValeurs["hote"],user=dictValeurs["utilisateur"], passwd=dictValeurs["mdp"], port=dictValeurs["port"], use_unicode=True) 
    connexion.set_character_set('utf8')
    cursor = connexion.cursor()
    listeDatabases = []
    cursor.execute("SHOW DATABASES;")
    listeValeurs = cursor.fetchall()
    for valeurs in listeValeurs :
        listeDatabases.append(valeurs[0])
    connexion.close()
    return listeDatabases

def GetRepertoireMySQL(dictValeurs={}):
    """ R�cup�re le r�pertoire d'installation MySQL 
         dictValeurs = valeurs de connexion
    """
    # R�cup�ration du chemin de MySQL � partir de la base de donn�es
##    import MySQLdb
##    connexion = MySQLdb.connect(host=dictValeurs["hote"],user=dictValeurs["utilisateur"], passwd=dictValeurs["mdp"], port=dictValeurs["port"], use_unicode=True) 
##    connexion.set_character_set('utf8')
##    cursor = connexion.cursor()
##    cursor.execute("SELECT @@basedir;")
##    donnees = cursor.fetchall()
##    if len(donnees) == 0 : 
##        return None
##    return donnees[0][0]

    # 1- Recherche automatique
    try :
        listeFichiers1 = os.listdir(_(u"C:/"))
        for fichier1 in listeFichiers1 :
            
            if "Program" in fichier1 :
                listeFichiers2 = os.listdir(_(u"C:/%s") % fichier1)
                for fichier2 in listeFichiers2 :
                    if "MySQL" in fichier2 :
                        listeFichiers3 = os.listdir(_(u"C:/%s/%s") % (fichier1, fichier2))
                        listeFichiers3.sort(reverse=True)
                        for fichier3 in listeFichiers3 :
                            if "MySQL Server" in fichier3 :
                                chemin = _(u"C:/%s/%s/%s/") % (fichier1, fichier2, fichier3)
                                if os.path.isdir(chemin) :
                                    return chemin
    except :
        pass
        
    # 2- Recherche dans le fichier Config
    try :
        chemin = UTILS_Config.GetParametre("sauvegarde_cheminmysql", defaut=None)
        if chemin != None :
            if os.path.isdir(nomFichier) :
                return chemin
    except :
        pass
        
    # 3- Demande le chemin � l'utilisateur
    try :
        message = _(u"Pour effectuer la sauvegarde de fichiers r�seau, Noethys \ndoit utiliser les outils de MySQL. S�lectionnez ici le r�pertoire qui se nomme 'MySQL Server...' sur votre ordinateur.")
        dlg = wx.DirDialog(None, message, style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            chemin = dlg.GetPath()
            dlg.Destroy()    
        else:
            dlg.Destroy()    
            return None
    except :
        pass
    
    try :
        if os.path.isdir(chemin + _(u"/bin/")) :
            UTILS_Config.SetParametre("sauvegarde_cheminmysql", chemin)
            return chemin
    except :
        pass
        
    return None



if __name__ == _(u"__main__"):
    app = wx.App(0)
    print(GetRepertoireMySQL())
