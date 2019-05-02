#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:       Ivan LUCAS
# Copyright:    (c) 2008-19 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
from Utils import UTILS_Traduction

from time import strftime
import time
HEUREDEBUT = time.time()

import six
import wx

from Ctrl import CTRL_Bouton_image

from Utils import UTILS_Config
from Utils import UTILS_Parametres
from Utils import UTILS_Fichiers
from Utils import UTILS_Customize
from Utils import UTILS_Adaptations
from Utils import UTILS_Rapport_bugs
from Utils import UTILS_Sauvegarde_auto

from Ctrl import CTRL_Accueil
from Ctrl import CTRL_Personnes
from Ctrl import CTRL_Presences
from Ctrl import CTRL_Recrutement

from Dlg import DLG_Config_sauvegarde
from Dlg import DLG_Enregistrement

import FonctionsPerso
import GestionDB
import UpgradeDB
import os
import datetime
#import locale
import random
import sys
import platform

from six.moves.urllib.request import urlopen

if six.PY2:
    import shelve
    import dbhash
    import anydbm

import wx.lib.agw.advancedsplash as AS
import wx.lib.agw.pybusyinfo as PBI

   

# Constantes
VERSION_APPLICATION = FonctionsPerso.GetVersionTeamworks()
MAIL_AUTEUR = ""
ADRESSE_FORUM = "https://www.teamworks.ovh"
ID_DERNIER_FICHIER = 700

            
            
class Toolbook(wx.Toolbook):
    def __init__(self, parent):
        wx.Toolbook.__init__(self, parent, -1, style= wx.BK_TOP)
        self.Build_Pages()
        
    def Build_Pages(self):
        """ Construit les pages du toolbook """
        # Images du ToolBook
        il = wx.ImageList(32, 32)
        self.img_accueil  = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Maison.png"), wx.BITMAP_TYPE_PNG))
        self.img_personnes  = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Personnes.png"), wx.BITMAP_TYPE_PNG))
        self.img_presences  = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Horloge.png"), wx.BITMAP_TYPE_PNG))
        self.img_recrutement  = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Recrutement.png"), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)
        
        # Création des pages
        self.AddPage(CTRL_Accueil.Panel(self), _(u"Accueil"), imageId=self.img_accueil)
        self.AddPage(CTRL_Personnes.PanelPersonnes(self), _(u"Individus"), imageId=self.img_personnes)
        self.AddPage(CTRL_Presences.PanelPresences(self), _(u"Présences"), imageId=self.img_presences)
        self.AddPage(CTRL_Recrutement.Panel(self), _(u"Recrutement"), imageId=self.img_recrutement)

        # Mémorise les index des pages
        self.dict_pages_by_index = {
            "accueil" : 0,
            "individus" : 1,
            "personnes" : 1,
            "presences" : 2,
            "recrutement" : 3,
            }

        # Met le texte à droite dans la toolbar
        tb = self.GetToolBar()        
        tb.SetWindowStyleFlag(wx.TB_HORZ_TEXT)
        # self.SetInternalBorder(0)
        
        self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGING, self.OnPageChanging)

    def MAJ_page_si_affichee(self, code=""):
        index = self.dict_pages_by_index[code]
        if index == self.GetSelection():
            self.MAJ_panel(index)

    def MAJ_panel(self, numPage=0):
        """ Test de MAJ des panels lors d'un changement d'onglet """
        self.Freeze() # Gèle l'affichage pour éviter des clignements
        self.GetPage(numPage).MAJpanel()
        self.Thaw() # Dégèle l'affichage

    def ActiveToolBook(self, etat=True):
        """ Active ou désactive les items du toolBook - en cas de fermeture d'un fichier par exemple """
        self.Freeze()
        # On se positionne sur la page d'accueil
        self.SetSelection(0)
        # On rend vierge la page d'accueil
        if etat == False : self.GetPage(0).html.Efface()

        # On désactive les autres pages du toolbook
        toolBar = self.GetToolBar()
        toolBar.EnableTool(2, etat) # Personnes
        toolBar.EnableTool(3, etat) # Présences
        toolBar.EnableTool(4, etat) # Recrutement

        self.Thaw()

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        if old !=-1 :
            self.MAJ_panel(new)
        event.Skip()





class MyFrame(wx.Frame):
    def __init__(self, parent, ID=-1, title=""):
        wx.Frame.__init__(self, parent, ID, title, style=wx.DEFAULT_FRAME_STYLE, name="general")

        theme = CUSTOMIZE.GetValeur("interface", "theme", "Bleu")
        
        # Ecrit la date et l'heure dans le journal.log
        dateDuJour = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        systeme = u"%s %s %s %s " % (sys.platform, platform.system(), platform.release(), platform.machine())
        if six.PY2:
            version_python = "2"
        else :
            version_python = "3"
        print(("-------- %s | %s | Python %s | wxPython %s | %s --------" % (dateDuJour, VERSION_APPLICATION, version_python, wx.version(), systeme)))

        # try : locale.setlocale(locale.LC_ALL, 'FR')
        # except : pass
        
        # Diminution de la taille de la police sous linux
        if "linux" in sys.platform :
            defaultFont = self.GetFont()
            defaultFont.SetPointSize(8)
            self.SetFont(defaultFont)
        
        # Recherche si une mise à jour internet existe
        self.MAJexiste = self.RechercheMAJinternet()

        # Vérifie que le fichier de configuration existe bien
        self.nouveauFichierConfig = False
        if UTILS_Config.IsFichierExists() == False :
            print("Generation d'un nouveau fichier de config")
            self.nouveauFichierConfig = UTILS_Config.GenerationFichierConfig()

        # Récupération des fichiers de configuration
        self.userConfig = self.GetFichierConfig()

        # Suppression du fichier Exemple ancien de TW1
        if os.path.isfile("Data/Exemple.twk") :
            os.remove("Data/Exemple.twk")

        # Récupération du nom du dernier fichier chargé
        self.nomDernierFichier = ""
        if "nomFichier" in self.userConfig:
            self.nomDernierFichier = self.userConfig["nomFichier"]
        self.userConfig["nomFichier"] = ""
                
        if "assistant_demarrage" in self.userConfig :
            if self.userConfig["assistant_demarrage"] == True :
                self.afficherAssistant = False
            else: self.afficherAssistant = True
        else:
            self.afficherAssistant = True

        # Sélection de l'interface MySQL
        if "interface_mysql" in self.userConfig:
            interface_mysql = self.userConfig["interface_mysql"]
            GestionDB.SetInterfaceMySQL(interface_mysql)
        if GestionDB.IMPORT_MYSQLDB_OK == False and GestionDB.IMPORT_MYSQLCONNECTOR_OK == True:
            GestionDB.SetInterfaceMySQL("mysql.connector")

        self.userConfig["interface_mysql"] = GestionDB.INTERFACE_MYSQL

        # Affiche le titre du fichier en haut de la frame
        self.SetTitleFrame(nomFichier="")
        
        # Création de la barre des menus
        self.CreationBarreMenus()

        # Construit la barre de status
        self.Build_Statusbar()

        # Construit le toolbool
        self.toolBook = Toolbook(self)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.__do_layout()
        
        # Désactive les commandes
        self.ActiveBarreMenus(False)
        self.toolBook.ActiveToolBook(False)

    def __do_layout(self):
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else:
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetMinSize((800, 600))
        sizer_base = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(self.toolBook, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        self.SetSize((800, 600))

        # Détermine la taille de la fenêtre
        if ("taille_fenetre" in self.userConfig) == False :
            self.userConfig["taille_fenetre"] = [0, 0]
        
        taille_fenetre = self.userConfig["taille_fenetre"]
        if taille_fenetre == [0, 0] :
            self.Maximize(True)
        else:
            self.SetSize(taille_fenetre)
        self.Centre()

    def GetCustomize(self):
        return CUSTOMIZE

    def Verif_Password(self, nomFichier):
        """ Vérifie s'il n'y a pas un mot de passe à saisir """
        # Recherche le mot de passe dans la base
        DB = GestionDB.DB(nomFichier = nomFichier)        
        req = "SELECT motdepasse FROM divers WHERE IDdivers=1;"
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        DB.Close()
        if len(donnees) == 0 : return True
        password = donnees[0][0]
        
        if password == "" or password == None : return True
        # Demande le mot de passe valide
        valide = False
        while valide == False :
            dlg = SaisiePassword(self, nomFichier=nomFichier)  
            if dlg.ShowModal() == wx.ID_OK:
                pwd = dlg.GetPassword()
                if pwd == password :
                    valide = True
                else:
                    dlg2 = wx.MessageDialog(self, _(u"Votre mot de passe est erroné."), _(u"Mot de passe erroné"), wx.OK | wx.ICON_ERROR)
                    dlg2.ShowModal()
                    dlg2.Destroy()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return False
        return True

    def SetTitleFrame(self, nomFichier=""):
        if "[RESEAU]" in nomFichier :
            port, hote, user, mdp = nomFichier.split(";")
            nomFichier = nomFichier[nomFichier.index("[RESEAU]") + 8:]
            nomFichier = _(u"Fichier réseau : %s | Utilisateur : %s") % (nomFichier, user)
        if nomFichier != "" :
            nomFichier = " - [" + nomFichier + "]"
        titreFrame = "Teamworks" + " v" + VERSION_APPLICATION + nomFichier
        self.SetTitle(titreFrame)

    def CreationBarreMenus(self):
        """ Construit la barre de menus """
        self.listeItemsMenu = [

            # Fichier
            {"code": "menu_fichier", "label": _(u"Fichier"), "items": [
                {"code": "assistant_demarrage", "label": _(u"Assistant Démarrage"), "infobulle": _(u"Ouvrir l'assistant démarrage"), "image": "Images/16x16/Assistant.png", "action": self.On_fichier_assistant},
                "-",
                {"code": "nouveau_fichier", "label": _(u"Créer un nouveau fichier"), "infobulle": _(u"Créer un nouveau fichier"), "image": "Images/16x16/Fichier_nouveau.png", "action": self.On_fichier_nouveau},
                {"code": "ouvrir_fichier", "label": _(u"Ouvrir un fichier"), "infobulle": _(u"Ouvrir un fichier existant"), "image": "Images/16x16/Fichier_ouvrir.png", "action": self.On_fichier_ouvrir},
                {"code": "fermer_fichier", "label": _(u"Fermer le fichier"), "infobulle": _(u"Fermer le fichier ouvert"), "image": "Images/16x16/Fichier_fermer.png", "action": self.On_fichier_fermer, "actif": False},
                "-",
                {"code": "creer_sauvegarde", "label": _(u"Créer une sauvegarde"), "infobulle": _(u"Créer une sauvegarde"), "image": "Images/16x16/Sauvegarder.png", "action": self.On_fichier_sauvegarder},
                {"code": "restaurer_sauvegarde", "label": _(u"Restaurer une sauvegarde"), "infobulle": _(u"Restaurer une sauvegarde"), "image": "Images/16x16/Restaurer.png", "action": self.On_fichier_restaurer},
                {"code": "sauvegardes_auto", "label": _(u"Sauvegardes automatiques"), "infobulle": _(u"Paramétrage des sauvegardes automatiques"), "image": "Images/16x16/Sauvegarder_param.png", "action": self.On_fichier_Sauvegardes_auto},

                "-",
                {"code": "convertir_fichier_reseau", "label": _(u"Convertir en fichier réseau"), "infobulle": _(u"Convertir le fichier en mode réseau"), "image": "Images/16x16/Conversion_reseau.png", "action": self.On_fichier_convertir_reseau, "actif": False},
                {"code": "convertir_fichier_local", "label": _(u"Convertir en fichier local"), "infobulle": _(u"Convertir le fichier en mode local"), "image": "Images/16x16/Conversion_local.png", "action": self.On_fichier_convertir_local, "actif": False},
                "-",
                {"code": "quitter", "label": _(u"Quitter"), "infobulle": _(u"Quitter Noethys"), "image": "Images/16x16/Quitter.png", "action": self.On_fichier_quitter},
            ],
             },

            # Paramétrage
            {"code": "menu_parametrage", "label": _(u"Paramétrage"), "items": [
                #{"code": "preferences", "label": _(u"Préférences"), "infobulle": _(u"Préférences"), "image": "Images/16x16/Mecanisme.png", "action": self.On_param_preferences},
                {"code": "enregistrement", "label": _(u"Enregistrement"), "infobulle": _(u"Enregistrement"), "image": "Images/16x16/Cle.png", "action": self.On_param_enregistrement},
                "-",
                {"code": "gadgets", "label": _(u"Gestion des Gadgets de la page d'accueil"), "infobulle": _(u"Gestion des Gadgets de la page d'accueil"), "image": "Images/16x16/Calendrier_ajout.png", "action": self.On_param_gadgets},
                "-",
                {"code": "acces_reseau", "label": _(u"Accès réseau"), "infobulle": _(u"Paramétrage des accès réseau"), "image": "Images/16x16/Utilisateur_reseau.png", "action": self.On_param_utilisateurs_reseau},
                {"code": "adresses_exp_mails", "label": _(u"Adresses d'expédition d'Emails"), "infobulle": _(u"Paramétrage des adresses d'expédition d'Emails"), "image": "Images/16x16/Emails_exp.png", "action": self.On_param_emails_exp},
                {"code": "protection_mdp", "label": _(u"Protection par mot de passe"), "infobulle": _(u"Paramétrage de la protection par mot de passe"), "image": "Images/16x16/Cadenas.png", "action": self.On_protection_mdp},
                "-",
                {"code": "menu_parametrage_individus", "label": _(u"Individus"), "items": [
                    {"code": "individus_questionnaire", "label": _(u"Le questionnaire"), "infobulle": _(u"Paramétrage des questionnaires"), "image": "Images/16x16/Questionnaire.png", "action": self.On_param_questionnaire},
                    {"code": "individus_qualifications", "label": _(u"Les types de qualifications"), "infobulle": _(u"Paramétrage des types de qualifications"), "image": "Images/16x16/Personnes.png", "action": self.On_param_qualifications},
                    {"code": "individus_pieces", "label": _(u"Les types de pièces"), "infobulle": _(u"Paramétrage des types de pièces"), "image": "Images/16x16/Personnes.png", "action": self.On_param_pieces},
                    {"code": "individus_situations", "label": _(u"Les types de situations"), "infobulle": _(u"Paramétrage des types de situations"), "image": "Images/16x16/Personnes.png", "action": self.On_param_situations},
                    {"code": "individus_pays", "label": _(u"Les pays et nationalités"), "infobulle": _(u"Paramétrage des pays et nationalités"), "image": "Images/16x16/Drapeau.png", "action": self.On_param_pays},
                    ],
                },
                {"code": "menu_parametrage_presences", "label": _(u"Planning"), "items": [
                    {"code": "individus_categories_presences", "label": _(u"Les catégories de présences"), "infobulle": _(u"Paramétrage des catégories de présence"), "image": "Images/16x16/Presences.png", "action": self.On_param_categories_presence},
                    ],
                },
                {"code": "menu_parametrage_contrats", "label": _(u"Contrats"), "items": [
                    {"code": "contrats_classifications", "label": _(u"Classifications"), "infobulle": _(u"Paramétrage des classifications"), "image": "Images/16x16/Document.png", "action": self.On_param_classifications},
                    {"code": "contrats_champs_", "label": _(u"Les champs de contrats"), "infobulle": _(u"Paramétrage des champs des contrats"), "image": "Images/16x16/Document.png", "action": self.On_param_champs_contrats},
                    {"code": "contrats_modeles", "label": _(u"Les modèles de contrats"), "infobulle": _(u"Paramétrage des modèles des contrats"), "image": "Images/16x16/Document.png", "action": self.On_param_modeles_contrats},
                    {"code": "contrats_types", "label": _(u"Les types de contrats"), "infobulle": _(u"Paramétrage des types de contrats"), "image": "Images/16x16/Document.png", "action": self.On_param_types_contrats},
                    {"code": "contrats_valeurs_points", "label": _(u"Les valeurs de points"), "infobulle": _(u"Paramétrage des valeurs de points"), "image": "Images/16x16/Document.png", "action": self.On_param_val_points},
                    ],
                 },
                {"code": "menu_parametrage_recrutement", "label": _(u"Recrutement"), "items": [
                    {"code": "recrutement_entretiens", "label": _(u"Protection des entretiens"), "infobulle": _(u"Paramétrage de la protection des entretiens"), "image": "Images/16x16/Mail.png", "action": self.On_param_entretiens},
                    {"code": "recrutement_fonctions", "label": _(u"Les fonctions"), "infobulle": _(u"Paramétrage fonctions"), "image": "Images/16x16/Mail.png", "action": self.On_param_fonctions},
                    {"code": "recrutement_affectations", "label": _(u"Les affectations"), "infobulle": _(u"Paramétrage des affectations"), "image": "Images/16x16/Mail.png", "action": self.On_param_affectations},
                    {"code": "recrutement_diffuseurs", "label": _(u"Les diffuseurs"), "infobulle": _(u"Paramétrage des diffuseurs"), "image": "Images/16x16/Mail.png", "action": self.On_param_diffuseurs},
                    {"code": "recrutement_offres", "label": _(u"Les offres d'emploi"), "infobulle": _(u"Paramétrage des offres d'emploi"), "image": "Images/16x16/Mail.png", "action": self.On_param_offres},
                    ],
                 },
                "-",
                {"code": "menu_parametrage_calendrier", "label": _(u"Calendrier"), "items": [
                    {"code": "vacances", "label": _(u"Vacances"), "infobulle": _(u"Paramétrage des vacances"), "image": "Images/16x16/Calendrier.png", "action": self.On_param_vacances},
                    {"code": "feries", "label": _(u"Jours fériés"), "infobulle": _(u"Paramétrage des jours fériés"), "image": "Images/16x16/Jour.png", "action": self.On_param_feries},
                    ],
                },
            ],
             },

            # Outils
            {"code": "menu_outils", "label": _(u"Outils"), "items": [
                {"code": "photos", "label": _(u"Imprimer des photos individuelles"), "infobulle": _(u"Imprimer des photos individuelles"), "image": "Images/16x16/Importer_photo.png", "action": self.On_outils_photos},
                {"code": "frais", "label": _(u"Gestion des frais de déplacements"), "infobulle": _(u"Gestion des frais de déplacements"), "image": "Images/16x16/Calculatrice.png", "action": self.On_outils_frais},
                "-",
                {"code": "registre", "label": _(u"Registre unique du personnel"), "infobulle": _(u"Registre unique du personnel"), "image": "Images/16x16/Contrat.png", "action": self.On_outils_registre},
                "-",
                {"code": "outlook", "label": _(u"Exporter les individus vers MS Outlook"), "infobulle": _(u"Exporter les individus vers MS Outlook"), "image": "Images/16x16/Outlook.png", "action": self.On_outils_outlook},
                {"code": "publipostage", "label": _(u"Créer des courriers ou des emails par publipostage"), "infobulle": _(u"Créer des courriers ou des emails par publipostage"), "image": "Images/16x16/Mail.png", "action": self.On_outils_publipostage},
                "-",
                {"code": "editeur_emails", "label": _(u"Editeur d'Emails"), "infobulle": _(u"Editeur d'Emails"), "image": "Images/16x16/Editeur_email.png", "action": self.On_outils_emails},
                {"code": "teamword", "label": _(u"Teamword, l'éditeur de texte"), "infobulle": _(u"Teamword, l'éditeur de texte"), "image": "Images/16x16/Document.png", "action": self.On_outils_teamword},
                "-",
                {"code": "menu_outils_utilitaires", "label": _(u"Utilitaires administrateur"), "items": [
                    {"code": "ouvrir_rep_utilisateur", "label": _(u"Ouvrir le répertoire utilisateur"), "infobulle": _(u"Ouvrir le répertoire utilisateur"), "image": "Images/16x16/Dossier.png", "action": self.On_outils_ouvrir_rep_utilisateur},
                    {"code": "ouvrir_rep_donnees", "label": _(u"Ouvrir le répertoire des données"), "infobulle": _(u"Ouvrir le répertoire des données"), "image": "Images/16x16/Dossier.png", "action": self.On_outils_ouvrir_rep_donnees},
                    {"code": "ouvrir_rep_modeles", "label": _(u"Ouvrir le répertoire des modèles de documents"), "infobulle": _(u"Ouvrir le répertoire des modèles de documents"), "image": "Images/16x16/Dossier.png", "action": self.On_outils_ouvrir_rep_modeles},
                    {"code": "ouvrir_rep_documents", "label": _(u"Ouvrir le répertoire des documents édités"), "infobulle": _(u"Ouvrir le répertoire des documents édités"), "image": "Images/16x16/Dossier.png", "action": self.On_outils_ouvrir_rep_editions},
                    ]},
                "-",
                {"code": "updater", "label": _(u"Rechercher une mise à jour du logiciel"), "infobulle": _(u"Rechercher une mise à jour du logiciel"), "image": "Images/16x16/Updater.png", "action": self.On_outils_updater},
            ],
                 },

            # Aide
            {"code": "menu_aide", "label": _(u"Aide"), "items": [
                {"code": "aide", "label": _(u"Consulter l'aide"), "infobulle": _(u"Consulter l'aide de Teamworks"), "image": "Images/16x16/Aide.png", "action": self.On_aide_aide},
                {"code": "acheter_licence", "label": _(u"Acheter une licence pour accéder au manuel de référence"), "infobulle": _(u"Acheter une licence"), "image": "Images/16x16/Acheter_licence.png", "action": self.On_propos_soutenir},
                "-",
                {"code": "forum", "label": _(u"Accéder au forum d'entraide"), "infobulle": _(u"Accéder au forum d'entraide"), "image": "Images/16x16/Dialogue.png", "action": self.On_aide_forum},
                {"code": "tutoriels_videos", "label": _(u"Visionner des tutoriels vidéos"), "infobulle": _(u"Visionner des tutoriels vidéos"), "image": "Images/16x16/Film.png", "action": self.On_aide_videos},
                #"-",
                #{"code": "email_auteur", "label": _(u"Envoyer un Email à l'auteur"), "infobulle": _(u"Envoyer un Email à l'auteur"), "image": "Images/16x16/Mail.png", "action": self.On_aide_auteur},
            ],
             },

            # A propos
            {"code": "menu_a_propos", "label": _(u"A propos"), "items": [
                {"code": "notes_versions", "label": _(u"Notes de versions"), "infobulle": _(u"Notes de versions"), "image": "Images/16x16/Versions.png", "action": self.On_propos_versions},
                {"code": "licence_logiciel", "label": _(u"Licence"), "infobulle": _(u"Licence du logiciel"), "image": "Images/16x16/Licence.png", "action": self.On_propos_licence},
                "-",
                {"code": "soutenir", "label": _(u"Soutenir Teamworks"), "infobulle": _(u"Soutenir Teamworks"), "image": "Images/16x16/Soutenir.png", "action": self.On_propos_soutenir},
                "-",
                {"code": "a_propos", "label": _(u"A propos"), "infobulle": _(u"A propos"), "image": "Images/16x16/Information.png", "action": self.On_propos_propos},
            ],
             },

        ]

        # Création du menu
        def CreationItem(menuParent, item):
            id = wx.Window.NewControlId()
            if "genre" in item:
                genre = item["genre"]
            else:
                genre = wx.ITEM_NORMAL
            itemMenu = wx.MenuItem(menuParent, id, item["label"], item["infobulle"], genre)
            if "image" in item:
                itemMenu.SetBitmap(wx.Bitmap(Chemins.GetStaticPath(item["image"]), wx.BITMAP_TYPE_PNG))
            try:
                menuParent.Append(itemMenu)
            except:
                if 'phoenix' in wx.PlatformInfo:
                    menuParent.Append(itemMenu)
                else:
                    menuParent.AppendItem(itemMenu)
            if "actif" in item:
                itemMenu.Enable(item["actif"])
            self.Bind(wx.EVT_MENU, item["action"], id=id)
            self.dictInfosMenu[item["code"]] = {"id": id, "ctrl": itemMenu}

        def CreationMenu(menuParent, item, sousmenu=False):
            menu = UTILS_Adaptations.Menu()
            id = wx.Window.NewControlId()
            for sousitem in item["items"]:
                if sousitem == "-":
                    menu.AppendSeparator()
                elif "items" in sousitem:
                    CreationMenu(menu, sousitem, sousmenu=True)
                else:
                    CreationItem(menu, sousitem)
            if sousmenu == True:
                menuParent.AppendMenu(id, item["label"], menu)
            else:
                menuParent.Append(menu, item["label"])
            self.dictInfosMenu[item["code"]] = {"id": id, "ctrl": menu}

        self.menu = wx.MenuBar()
        self.dictInfosMenu = {}
        for item in self.listeItemsMenu:
            CreationMenu(self.menu, item)

        # -------------------------- AJOUT DES DERNIERS FICHIERS OUVERTS -----------------------------
        menu_fichier = self.dictInfosMenu["menu_fichier"]["ctrl"]

        # Intégration des derniers fichiers ouverts :
        if "derniersFichiers" in self.userConfig:
            listeDerniersFichiersTmp = self.userConfig["derniersFichiers"]
        else:
            listeDerniersFichiersTmp = []
        if len(listeDerniersFichiersTmp) > 0:
            menu_fichier.AppendSeparator()

        # Vérification de la liste
        listeDerniersFichiers = []
        for nomFichier in listeDerniersFichiersTmp:
            if "[RESEAU]" in nomFichier:
                # Version RESEAU
                listeDerniersFichiers.append(nomFichier)
            else:
                # VERSION LOCAL
                fichier = UTILS_Fichiers.GetRepData(u"%s_TDATA.dat" % nomFichier)
                test = os.path.isfile(fichier)
                if test == True:
                    listeDerniersFichiers.append(nomFichier)
        self.userConfig["derniersFichiers"] = listeDerniersFichiers

        if len(listeDerniersFichiers) > 0:
            index = 0
            for nomFichier in listeDerniersFichiers:
                if "[RESEAU]" in nomFichier:
                    nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
                item = wx.MenuItem(menu_fichier, ID_DERNIER_FICHIER + index, u"%d. %s" % (index + 1, nomFichier), _(u"Ouvrir le fichier : '%s'") % nomFichier)
                try:
                    menu_fichier.Append(item)
                except:
                    if 'phoenix' in wx.PlatformInfo:
                        menu_fichier.Append(item)
                    else:
                        menu_fichier.AppendItem(item)
                index += 1
            self.Bind(wx.EVT_MENU_RANGE, self.On_fichier_DerniersFichiers, id=ID_DERNIER_FICHIER, id2=ID_DERNIER_FICHIER + index)

        # Finalisation Barre de menu
        self.SetMenuBar(self.menu)

    def RechercherPositionItemMenu(self, codeMenu="", codeItem=""):
        menu = self.dictInfosMenu[codeMenu]["ctrl"]
        IDitem = self.dictInfosMenu[codeItem]["id"]
        index = 0
        for item in menu.GetMenuItems():
            if item.GetId() == IDitem:
                return index
            index += 1
        return 0

    def On_fichier_DerniersFichiers(self, event):
        """ Ouvre un des derniers fichiers ouverts """
        idMenu = event.GetId()
        nomFichier = self.userConfig["derniersFichiers"][idMenu - ID_DERNIER_FICHIER]
        self.OuvrirFichier(nomFichier)

    def ActiveBarreMenus(self, etat=True):
        """ Active ou non des menus de la barre """
        for numMenu in range(2, 3):
            self.menu.EnableTop(numMenu, etat)

    def Build_Statusbar(self):
        self.statusbar = self.CreateStatusBar(2, 0)
        self.statusbar.SetStatusWidths([400, -1])
        
    def OnSize(self, event):
        event.Skip()

    def GetFichierConfig(self):
        """ Récupère le dictionnaire du fichier de config """
        cfg = UTILS_Config.FichierConfig()
        return cfg.GetDictConfig()

    def SaveFichierConfig(self):
        """ Sauvegarde le dictionnaire du fichier de config """
        cfg = UTILS_Config.FichierConfig()
        cfg.SetDictConfig(dictConfig=self.userConfig )

    def OnClose(self, event):
        if self.Quitter() == False :
            return
        event.Skip()
        
    def Quitter(self, videRepertoiresTemp=True, sauvegarde_auto=True):
        """ Fin de l'application """
        # Mémorisation du paramètre de la taille d'écran
        if self.IsMaximized() == True :
            taille_fenetre = [0, 0]
        else:
            taille_fenetre = list(self.GetSize())
        self.userConfig["taille_fenetre"] = taille_fenetre

        # Codage du mdp réseau si besoin
        if "[RESEAU]" in self.userConfig["nomFichier"] and "#64#" not in self.userConfig["nomFichier"]:
            nom = GestionDB.EncodeNomFichierReseau(self.userConfig["nomFichier"])
            self.userConfig["nomFichier"] = nom

        # Sauvegarde du fichier de configuration
        self.SaveFichierConfig()

        # Sauvegarde automatique
        if self.userConfig["nomFichier"] != "" and sauvegarde_auto == True :
            resultat = self.SauvegardeAutomatique()
            if resultat == wx.ID_CANCEL :
                return False

        # Vidage du répertoire Temp
        if videRepertoiresTemp == True :
            FonctionsPerso.VideRepertoireTemp()
        
        # Vidage du répertoire Updates
        FonctionsPerso.VideRepertoireUpdates()

        # Affiche les connexions restées ouvertes
        GestionDB.AfficheConnexionOuvertes()

    def SauvegardeAutomatique(self):
        save = UTILS_Sauvegarde_auto.Sauvegarde_auto(self)
        resultat = save.Start()
        return resultat

    def OuvrirDernierFichier(self):
        # Chargement du dernier fichier chargé si assistant non affiché
        if "assistant_demarrage" in self.userConfig:
            nePasAfficherAssistant = self.userConfig["assistant_demarrage"]
            if nePasAfficherAssistant == True:
                if self.nomDernierFichier != "":
                    self.OuvrirFichier(self.nomDernierFichier)

    def OuvrirFichier(self, nomFichier):
        """ Suite de la commande menu Ouvrir """
        self.SetStatusText(_(u"Ouverture d'un fichier en cours..."))

        # Vérifie que le fichier n'est pas déjà ouvert
        if self.userConfig["nomFichier"] == nomFichier:
            if "[RESEAU]" in nomFichier:
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
            dlg = wx.MessageDialog(self, _(u"Le fichier '") + nomFichier + _(u"' est déjà ouvert !"), _(u"Ouverture de fichier"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.SetStatusText(_(u"Le fichier '%s' est déjà ouvert.") % nomFichier)
            return False

        # Teste l'existence du fichier :
        if self.TesterUnFichier(nomFichier) == False:
            if "[RESEAU]" in nomFichier:
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
            self.SetStatusText(_(u"Impossible d'ouvrir le fichier '%s'.") % nomFichier)
            return False

        # Vérification du mot de passe
        if nomFichier != "":
            if self.Verif_Password(nomFichier) == False:
                if "[RESEAU]" in nomFichier:
                    nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
                self.SetStatusText(_(u"Echec de l'ouverture du fichier '%s' : Mot de passe incorrect.") % nomFichier)
                return False

        # Vérifie si la version du fichier est à jour
        if nomFichier != "":
            if self.ValidationVersionFichier(nomFichier) == False:
                if "[RESEAU]" in nomFichier:
                    nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
                self.SetStatusText(_(u"Echec de l'ouverture du fichier '%s'.") % nomFichier)
                return False

        # Applique le changement de fichier en cours
        self.userConfig["nomFichier"] = nomFichier

        # Remplissage de la table DIVERS pour la date de dernière ouverture
        if nomFichier != "":
            date_jour = str(datetime.date.today())
            listeDonnees = [("date_derniere_ouverture", date_jour), ]
            db = GestionDB.DB()
            db.ReqMAJ("divers", listeDonnees, "IDdivers", 1)
            db.Close()

        # Vérifie que le répertoire de destination de sauvegarde auto existe vraiment
        if nomFichier != "":
            self.VerifDestinationSaveAuto()

        # Met à jour l'affichage
        self.MAJAffichage()
        self.SetTitleFrame(nomFichier=nomFichier)

        # Met à jour la liste des derniers fichiers ouverts dans le CONFIG de la page
        self.MAJlisteDerniersFichiers(nomFichier)

        # Met à jour le menu
        self.MAJmenuDerniersFichiers()

        # Désactive le menu Conversion Réseau s'il s'agit déjà d'un fichier réseau
        self.dictInfosMenu["fermer_fichier"]["ctrl"].Enable(True)
        if "[RESEAU]" in nomFichier:
            self.dictInfosMenu["convertir_fichier_reseau"]["ctrl"].Enable(False)
            self.dictInfosMenu["convertir_fichier_local"]["ctrl"].Enable(True)
        else:
            self.dictInfosMenu["convertir_fichier_reseau"]["ctrl"].Enable(True)
            self.dictInfosMenu["convertir_fichier_local"]["ctrl"].Enable(False)

        # Sauvegarde du fichier de configuration
        self.SaveFichierConfig()

        # Active les items du toolbook et sélectionne la page accueil
        self.toolBook.ActiveToolBook(True)
        self.ActiveBarreMenus(True)

        # Confirmation de succès
        if "[RESEAU]" in nomFichier:
            nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
        self.SetStatusText(_(u"Le fichier '%s' a été ouvert avec succès.") % nomFichier)

    def VerifDestinationSaveAuto(self):
        """ Vérifie que le répertoire de destination existe vraiment """
        try:
            DB = GestionDB.DB()
            req = "SELECT save_destination FROM divers WHERE IDdivers=1;"
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) != 0:
                save_destination_defaut = listeDonnees[0][0]
                test = os.path.isdir(save_destination_defaut)
                if test == False:
                    standardPath = wx.StandardPaths.Get()
                    save_destination = standardPath.GetDocumentsDir()
                    save_destination = save_destination.replace("\\", "/")
                    listeDonnees = [("save_destination", save_destination), ]
                    DB.ReqMAJ("divers", listeDonnees, "IDdivers", 1)
            DB.Close()
        except:
            print("pb dans la fonction verifDestinationSaveAuto de teamworks.py")

    def MenuDerniersFichiers(self, event):
        """ Ouvre un des derniers fichiers ouverts """
        idMenu = event.GetId()
        nomFichier = self.userConfig["derniersFichiers"][idMenu - 150]
        self.OuvrirFichier(nomFichier)

    def MAJmenuDerniersFichiers(self):
        """ Met à jour la liste des derniers fichiers dans le menu """
        # Suppression de la liste existante
        menuFichier = self.dictInfosMenu["menu_fichier"]["ctrl"]
        for index in range(ID_DERNIER_FICHIER, ID_DERNIER_FICHIER + 10):
            item = self.menu.FindItemById(index)
            if item == None:
                break
            else:
                if 'phoenix' in wx.PlatformInfo:
                    menuFichier.Remove(self.menu.FindItemById(index))
                else:
                    menuFichier.RemoveItem(self.menu.FindItemById(index))
                self.Disconnect(index, -1, 10014)  # Annule le Bind

        # Ré-intégration des derniers fichiers ouverts :
        listeDerniersFichiers = self.userConfig["derniersFichiers"]
        if len(listeDerniersFichiers) > 0:
            index = 0
            for nomFichier in listeDerniersFichiers:
                # Version Reseau
                if "[RESEAU]" in nomFichier:
                    nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
                item = wx.MenuItem(menuFichier, ID_DERNIER_FICHIER + index, u"%d. %s" % (index + 1, nomFichier), _(u"Ouvrir le fichier : '%s'") % nomFichier)
                if 'phoenix' in wx.PlatformInfo:
                    menuFichier.Append(item)
                else:
                    menuFichier.AppendItem(item)
                index += 1
            self.Bind(wx.EVT_MENU_RANGE, self.On_fichier_DerniersFichiers, id=ID_DERNIER_FICHIER, id2=ID_DERNIER_FICHIER + index)

    def MAJlisteDerniersFichiers(self, nomFichier):
        """ MAJ la liste des derniers fichiers ouverts dans le config et la barre des menus """

        # MAJ de la liste des derniers fichiers ouverts :
        listeFichiers = self.userConfig["derniersFichiers"]
        nbreFichiersMax = 3  # Valeur à changer en fonction des souhaits

        # Si le nom est déjà dans la liste, on le supprime :
        if nomFichier in listeFichiers: listeFichiers.remove(nomFichier)

        # On ajoute le nom du fichier en premier dans la liste :
        listeFichiers.insert(0, nomFichier)
        listeFichiers = listeFichiers[:nbreFichiersMax]

        # On enregistre dans le Config :
        self.userConfig["derniersFichiers"] = listeFichiers

    def TesterUnFichier(self, nomFichier):
        """ Fonction pour tester l'existence d'un fichier """
        if "[RESEAU]" in nomFichier:
            # Version RESEAU
            pos = nomFichier.index("[RESEAU]")
            paramConnexions = nomFichier[:pos]
            port, host, user, passwd = paramConnexions.split(";")
            nomFichierCourt = nomFichier[pos:].replace("[RESEAU]", "")
            nomFichierCourt = nomFichierCourt.lower()

            # Si c'est une nouvelle version de fichier
            serveurValide = True
            fichierValide = True
            dictResultats = GestionDB.TestConnexionMySQL(typeTest='fichier', nomFichier=_(u"%s_tdata") % nomFichier)

            if dictResultats["connexion"][0] == False:
                serveurValide = False
            else:
                if dictResultats["fichier"][0] == False:
                    fichierValide = False

            if serveurValide == True and fichierValide == True:
                return True

            # Si c'est une ancienne version de fichier
            dictResultats = GestionDB.TestConnexionMySQL(typeTest='fichier', nomFichier=nomFichier)
            if dictResultats["connexion"][0] == True and dictResultats["fichier"][0] == True:
                # Création de la nouvelle base
                self.SetStatusText(_(u"Conversion pour Teamworks 2 : Création de la nouvelle base..."))
                DB = GestionDB.DB(nomFichier=nomFichier, modeCreation=True)
                DB.Close()

                # Importation des anciennes tables de données
                DB = GestionDB.DB(suffixe="", nomFichier=nomFichier)
                listeTables = DB.GetListeTables()
                for (nomTable,) in listeTables:
                    self.SetStatusText(_(u"Conversion pour Teamworks 2 : Transfert de la table %s....") % nomTable)
                    req = "RENAME TABLE %s.%s TO %s_tdata.%s;" % (nomFichierCourt, nomTable, nomFichierCourt, nomTable)
                    DB.ExecuterReq(req)
                DB.Commit()
                DB.Close()

                # Suppression de l'ancienne table
                self.SetStatusText(_(u"Conversion pour Teamworks 2 : Suppression de l'ancienne base..."))
                DB = GestionDB.DB(nomFichier=nomFichier)
                req = "DROP DATABASE %s;" % nomFichierCourt
                DB.ExecuterReq(req)
                DB.Close()

                return True

            if serveurValide == False:
                # Connexion impossible au serveur MySQL
                erreur = dictResultats["connexion"][1]
                dlg = wx.MessageDialog(self, _(
                    u"Il est impossible de se connecter au serveur MySQL.\n\nErreur : %s") % erreur,
                                       "Erreur d'ouverture de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            if fichierValide == False:
                # Ouverture impossible du fichier MySQL demandé
                erreur = dictResultats["fichier"][1]
                dlg = wx.MessageDialog(self, _(
                    u"La connexion avec le serveur MySQL fonctionne mais il est impossible d'ouvrir le fichier MySQL demandé.\n\nErreur : %s") % erreur,
                                       "Erreur d'ouverture de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            return True

        # SQLITE
        else:
            # Test de validité du fichier SQLITE :
            valide = False
            if os.path.isfile(UTILS_Fichiers.GetRepData(u"%s_TDATA.dat" % nomFichier)):
                valide = True
            else:
                cheminFichier = UTILS_Fichiers.GetRepData(u"%s.twk" % nomFichier)
                if os.path.isfile(cheminFichier):
                    valide = True
                    # Si c'est une version TW1 : Renommage du fichier DATA pour TW2
                    os.rename(cheminFichier, UTILS_Fichiers.GetRepData(u"%s_TDATA.dat" % nomFichier))

            if valide == False:
                dlg = wx.MessageDialog(self, _(u"Il est impossible d'ouvrir le fichier demandé !"),
                                       "Erreur d'ouverture de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            else:
                return True

    def ConvertVersionTuple(self, texteVersion=""):
        """ Convertit un numéro de version texte en tuple """
        if type(texteVersion) == list:
            return tuple(texteVersion)
        if type(texteVersion) == tuple:
            return texteVersion
        tupleTemp = []
        for num in texteVersion.split("."):
            tupleTemp.append(int(num))
        return tuple(tupleTemp)

    def ValidationVersionFichier(self, nomFichier):
        """ Vérifie que la version du fichier est à jour avec le logiciel """
        # Récupère le numéro de version du logiciel
        versionLogiciel = self.ConvertVersionTuple(VERSION_APPLICATION)

        # Récupère le numéro de version du fichier
        if UTILS_Parametres.TestParametre(categorie="fichier", nom="version", nomFichier=nomFichier) == True:
            versionFichier = self.ConvertVersionTuple(
                UTILS_Parametres.Parametres(mode="get", categorie="fichier", nom="version", valeur=VERSION_APPLICATION,
                                            nomFichier=nomFichier))
        else:
            # Pour compatibilité avec version 1 de Teamworks
            versionFichier = (1, 0, 5, 2)

        # Compare les deux versions
        if versionFichier < versionLogiciel:
            # Fait la conversion à la nouvelle version
            info = "Lancement de la conversion %s -> %s..." % (
            ".".join([str(x) for x in versionFichier]), ".".join([str(x) for x in versionLogiciel]))
            self.SetStatusText(info)
            print(info)

            # Affiche d'une fenêtre d'attente
            message = _(u"Mise à jour de la base de données en cours... Veuillez patientez...")
            dlgAttente = PBI.PyBusyInfo(message, parent=None, title=_(u"Mise à jour"), icon=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
            if 'phoenix' not in wx.PlatformInfo:
                wx.Yield()

            DB = UpgradeDB.DB(nomFichier=nomFichier)
            resultat = DB.Upgrade(versionFichier)
            DB.Close()

            # Fermeture de la fenêtre d'attente
            del dlgAttente

            if resultat != True:
                print(resultat)
                dlg = wx.MessageDialog(self, _(u"Le logiciel n'arrive pas à convertir le fichier '") + nomFichier + _(
                    u":\n\nErreur : ") + resultat + _(u"\n\nVeuillez contacter le développeur du logiciel..."),
                                       _(u"Erreur de conversion de fichier"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            # Mémorisation de la version actuelle du fichier
            UTILS_Parametres.Parametres(mode="set", categorie="fichier", nom="version",
                                        valeur=".".join([str(x) for x in versionLogiciel]), nomFichier=nomFichier)
            info = "Conversion %s -> %s reussie." % (
            ".".join([str(x) for x in versionFichier]), ".".join([str(x) for x in versionLogiciel]))
            self.SetStatusText(info)
            print(info)

        return True

    def On_fichier_fermer(self, event):
        """ Fermer le fichier ouvert """
        # Vérifie qu'un fichier est chargé
        if self.userConfig["nomFichier"] == "":
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucun fichier à fermer !"), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Sauvegarde automatique
        resultat = self.SauvegardeAutomatique()
        if resultat == wx.ID_CANCEL :
            return

        # change le nom de fichier
        self.userConfig["nomFichier"] = ""
        self.SetTitleFrame()

        # Désactive les items du toolbook et sélectionne la page accueil
        self.toolBook.ActiveToolBook(False)

        # Désactive certains menus
        self.ActiveBarreMenus(False)

        # Désactive la commande FERMER du menu Fichier
        self.dictInfosMenu["fermer_fichier"]["ctrl"].Enable(False)
        self.dictInfosMenu["convertir_fichier_reseau"]["ctrl"].Enable(False)
        self.dictInfosMenu["convertir_fichier_local"]["ctrl"].Enable(False)


    def On_fichier_convertir_reseau(self, event):
        nomFichier = self.userConfig["nomFichier"]
        from Utils import UTILS_Conversion_fichier
        resultat = UTILS_Conversion_fichier.ConversionLocalReseau(self, nomFichier)
        print("Succes de la procedure : ", resultat)

    def On_fichier_convertir_local(self, event):
        nomFichier = self.userConfig["nomFichier"]
        from Utils import UTILS_Conversion_fichier
        resultat = UTILS_Conversion_fichier.ConversionReseauLocal(self, nomFichier)
        print("Succes de la procedure : ", resultat)

    def On_fichier_assistant(self, event):
        self.Assistant_demarrage(mode="menu")

    def On_fichier_nouveau(self, event):
        """ Créé une nouvelle base de données """
        from Data import DATA_Tables as Tables
        
        # Demande le nom du fichier
        from Dlg import DLG_Saisie_nouveau_fichier
        dlg = DLG_Saisie_nouveau_fichier.MyDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            nomFichier = dlg.GetNomFichier()
            listeTables = dlg.GetListeTables()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        
        # Affiche d'une fenêtre d'attente
        message = _(u"Création du nouveau fichier en cours... Veuillez patientez...")
        dlgAttente = PBI.PyBusyInfo(message, parent=None, title=_(u"Création d'un fichier"), icon=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        if 'phoenix' not in wx.PlatformInfo:
            wx.Yield()
            
        if "[RESEAU]" in nomFichier :
            self.SetStatusText(_(u"Création du fichier '%s' en cours...") % nomFichier[nomFichier.index("[RESEAU]"):])
        else:
            self.SetStatusText(_(u"Création du fichier '%s' en cours...") % nomFichier)
        
        # Vérification de validité du fichier
        if nomFichier == "" :
            del dlgAttente
            dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide !"), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
            self.SetStatusText(_(u"Echec de la création du fichier '%s' : nom du fichier non valide.") % nomFichier)
            return False

        if "[RESEAU]" not in nomFichier :
            # Version LOCAL
            
            # Vérifie si un fichier ne porte pas déjà ce nom :
            fichier = UTILS_Fichiers.GetRepData(nomFichier + "_TDATA.dat")
            test = os.path.isfile(fichier) 
            if test == True :
                del dlgAttente
                dlg = wx.MessageDialog(self, _(u"Vous possédez déjà un fichier qui porte le nom '") + nomFichier + _(u"'.\n\nVeuillez saisir un autre nom."), "Erreur", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.SetStatusText(_(u"Echec de la création du fichier '%s' : Le nom existe déjà.") % nomFichier)
                return False
        
        else:
            # Version RESEAU
            dictResultats = GestionDB.TestConnexionMySQL(typeTest="fichier", nomFichier=_(u"%s_TDATA") % nomFichier)
            
            # Vérifie la connexion au réseau
            if dictResultats["connexion"][0] == False :
                erreur = dictResultats["connexion"][1]
                dlg = wx.MessageDialog(self, _(u"La connexion au réseau MySQL est impossible. \n\nErreur : %s") % erreur, _(u"Erreur de connexion"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                del dlgAttente
                return False
            
            # Vérifie que le fichier n'est pas déjà utilisé
            if dictResultats["fichier"][0] == True :
                dlg = wx.MessageDialog(self, _(u"Le fichier existe déjà."), _(u"Erreur de création de fichier"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                del dlgAttente
                return False
        
        ancienFichier = self.userConfig["nomFichier"]
        self.userConfig["nomFichier"] = nomFichier 
        
        # Création de la base DATA
        DB = GestionDB.DB(suffixe="DATA", modeCreation=True)
        if DB.echec == 1 :
            del dlgAttente
            erreur = DB.erreur
            dlg = wx.MessageDialog(self, _(u"Erreur dans la création du fichier de données.\n\nErreur : %s") % erreur, _(u"Erreur de création de fichier"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.userConfig["nomFichier"] = ancienFichier 
            return False
        self.SetStatusText(_(u"Création des tables de données..."))
        DB.CreationTables(Tables.DB_DATA, fenetreParente=self)
        self.SetStatusText(_(u"Importation des données par défaut..."))
        DB.Importation_valeurs_defaut(listeTables)
        DB.Close()
        
        # Création de la base PHOTOS
        DB = GestionDB.DB(suffixe="PHOTOS", modeCreation=True)
        if DB.echec == 1 :
            del dlgAttente
            erreur = DB.erreur
            dlg = wx.MessageDialog(self, _(u"Erreur dans la création du fichier de photos.\n\nErreur : %s") % erreur, _(u"Erreur de création de fichier"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.userConfig["nomFichier"] = ancienFichier 
            return False
        self.SetStatusText(_(u"Création de la table de données des photos..."))
        DB.CreationTables(Tables.DB_PHOTOS)
        DB.Close()
        
        # Création de la base DOCUMENTS
        DB = GestionDB.DB(suffixe="DOCUMENTS", modeCreation=True)
        if DB.echec == 1 :
            del dlgAttente
            erreur = DB.erreur
            dlg = wx.MessageDialog(self, _(u"Erreur dans la création du fichier de documents.\n\nErreur : %s") % erreur, _(u"Erreur de création de fichier"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.userConfig["nomFichier"] = ancienFichier 
            return False
        self.SetStatusText(_(u"Création de la table de données des documents..."))
        DB.CreationTables(Tables.DB_DOCUMENTS)
        DB.Close()

        # Créé un identifiant unique pour ce fichier
        d = datetime.datetime.now()
        IDfichier = d.strftime("%Y%m%d%H%M%S")
        for x in range(0, 3) :
            IDfichier += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

        # Mémorisation des informations sur le fichier
        listeDonnees = [
            ( "date_creation", str(datetime.date.today()) ),
            ( "version", VERSION_APPLICATION ),
            ( "IDfichier", IDfichier ),
            ]
        DB = GestionDB.DB()
        for nom, valeur in listeDonnees :
            donnees = [("categorie",  "fichier"), ("nom",  nom), ("parametre",  valeur),]
            DB.ReqInsert("parametres", donnees)
        DB.Close()

        # Remplissage de la table DIVERS
        date_jour =  str(datetime.date.today())
        if "[RESEAU]" in nomFichier :
            save_active = 0
        else:
            save_active = 1
        save_frequence = 0
        save_conservation = 3
        standardPath = wx.StandardPaths.Get()
        save_destination = standardPath.GetDocumentsDir()
        save_elements = DLG_Config_sauvegarde.GetListeSourcesStr()
        listeDonnees = [("date_derniere_ouverture",  date_jour),
                                ("date_creation_fichier",  date_jour),
                                ("save_active",  save_active),
                                ("save_frequence",  save_frequence),
                                ("save_elements",  save_elements),
                                ("save_destination",  save_destination),
                                ("save_conservation",  save_conservation),
                                ("codeIDfichier",  IDfichier),
                                ]
        DB = GestionDB.DB() 
        newID = DB.ReqInsert("divers", listeDonnees)
        DB.Close()
        
        # Met à jour l'affichage des panels
        self.MAJAffichage()
        self.SetTitleFrame(nomFichier=nomFichier)
        
        # Met à jour la liste des derniers fichiers de la barre des menus
        self.MAJlisteDerniersFichiers(nomFichier)
        
        # Met à jour le menu
        self.MAJmenuDerniersFichiers()
        
        # Active les items du toolbook et sélectionne la page accueil
        self.toolBook.ActiveToolBook(True)
        self.ActiveBarreMenus(True)

        # Désactive le menu Conversion Réseau s'il s'agit déjà d'un fichier réseau
        if "[RESEAU]" in nomFichier:
            self.dictInfosMenu["convertir_fichier_reseau"]["ctrl"].Enable(False)
            self.dictInfosMenu["convertir_fichier_local"]["ctrl"].Enable(True)
        else:
            self.dictInfosMenu["convertir_fichier_reseau"]["ctrl"].Enable(True)
            self.dictInfosMenu["convertir_fichier_local"]["ctrl"].Enable(False)

        # Sauvegarde du fichier de configuration
        self.SaveFichierConfig()
        
        # Boîte de dialogue pour confirmer la création
        if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
        
        del dlgAttente
        
        dlg = wx.MessageDialog(self, _(u"Le fichier '") + nomFichier + _(u"' a été créé avec succès."), _(u"Création d'un fichier"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
        self.SetStatusText(_(u"Le fichier '%s' a été créé avec succès.") % nomFichier)
        
        # Rappel de la nécessité de créer des utilisateurs réseau
        if "[RESEAU]" in nomFichier :
            dlg = wx.MessageDialog(self, _(u"Pour l'instant, vous êtes le seul, en tant qu'administrateur, à pouvoir accéder à ce fichier. Vous devez donc créer des utilisateurs réseau ou accorder des autorisations d'accès aux utilisateurs déjà enregistrés.\n\nPour gérer les comptes utilisateurs réseau, rendez-vous sur le panneau 'Configuration' puis sur la page 'Utilisateurs réseau'."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()


    def On_fichier_ouvrir(self, event):
        """ Ouvrir un fichier présent dur le disque dur """    
        # Boîte de dialogue pour demander le nom du fichier à ouvrir
        from Dlg import DLG_Ouvrir_fichier
        dlg = DLG_Ouvrir_fichier.MyDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            nomFichier = dlg.GetNomFichier()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        # Ouverture du fichier
        self.OuvrirFichier(nomFichier)

    def On_fichier_sauvegarder(self, event):
        """ Sauvegarder occasionnelle """
        from Dlg import DLG_Sauvegarde
        dlg = DLG_Sauvegarde.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_fichier_Sauvegardes_auto(self, event):
        from Dlg import DLG_Sauvegardes_auto
        dlg = DLG_Sauvegardes_auto.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_fichier_quitter(self, event):
        self.Quitter()
        self.Destroy()
        event.Skip()

    def On_fichier_restaurer(self, event):
        """ Restaurer une sauvegarde """
        from Dlg import DLG_Restauration
        fichier = DLG_Restauration.SelectionFichier()
        if fichier != None :
            if fichier.endswith(".twz") == True :
                # Version TW1
                frameResto = DLG_Config_sauvegarde.Restauration(self, fichier)
                frameResto.Show()
            else:
                # Version TW2
                dlg = DLG_Restauration.Dialog(self, fichier=fichier)
                dlg.ShowModal()
                dlg.Destroy()

    def On_param_preferences(self, event):
        from Dlg import DLG_Preferences
        dlg = DLG_Preferences.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_param_enregistrement(self, event):
        from Dlg import DLG_Enregistrement
        dlg = DLG_Enregistrement.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_param_gadgets(self, event):
        """ Configuration des gadgets de la page d'accueil """
        # Vérifie qu'un fichier est chargé
        if self.userConfig["nomFichier"] == "":
            dlg = wx.MessageDialog(self, _(u"Vous n'avez chargé aucun fichier."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        from Dlg import DLG_Config_gadgets
        dlg = DLG_Config_gadgets.Dialog(None)
        if dlg.ShowModal() == wx.ID_YES:
            self.toolBook.GetPage(0).MAJpanel()
        dlg.Destroy()

    def On_param_utilisateurs_reseau(self, event):
        if "[RESEAU]" not in self.userConfig["nomFichier"] :
            dlg = wx.MessageDialog(self, _(u"Cette fonction n'est accessible que si vous utilisez un fichier réseau !"), _(u"Accès non autorisé"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        from Dlg import DLG_Utilisateurs_reseau
        dlg = DLG_Utilisateurs_reseau.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_param_emails_exp(self, event):
        from Dlg import DLG_Emails_exp
        dlg = DLG_Emails_exp.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_protection_mdp(self, event):
        from Dlg import DLG_Config_password
        dlg = DLG_Config_password.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_param_questionnaire(self, event):
        from Dlg import DLG_Config_questionnaires
        dlg = DLG_Config_questionnaires.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_param_qualifications(self, event):
        from Dlg import DLG_Config_types_diplomes
        dlg = DLG_Config_types_diplomes.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_param_pieces(self, event):
        from Dlg import DLG_Config_types_pieces
        dlg = DLG_Config_types_pieces.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.toolBook.MAJ_page_si_affichee("individus")

    def On_param_situations(self, event):
        from Dlg import DLG_Config_situations
        dlg = DLG_Config_situations.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_param_pays(self, event):
        from Dlg import DLG_Config_pays
        dlg = DLG_Config_pays.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_param_categories_presence(self, event):
        from Dlg import DLG_Config_categories_presences
        dlg = DLG_Config_categories_presences.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.toolBook.MAJ_page_si_affichee("presences")

    def On_param_classifications(self, event):
        from Dlg import DLG_Config_classifications
        dlg = DLG_Config_classifications.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_param_champs_contrats(self, event):
        from Dlg import DLG_Config_champs_contrats
        dlg = DLG_Config_champs_contrats.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_param_modeles_contrats(self, event):
        from Dlg import DLG_Config_modeles_contrats
        dlg = DLG_Config_modeles_contrats.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_param_types_contrats(self, event):
        from Dlg import DLG_Config_types_contrats
        dlg = DLG_Config_types_contrats.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_param_val_points(self, event):
        from Dlg import DLG_Config_val_point
        dlg = DLG_Config_val_point.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_param_entretiens(self, event):
        from Dlg import DLG_Config_verrouillage_entretien
        dlg = DLG_Config_verrouillage_entretien.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_param_fonctions(self, event):
        from Dlg import DLG_Config_fonctions
        dlg = DLG_Config_fonctions.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.toolBook.MAJ_page_si_affichee("recrutement")

    def On_param_affectations(self, event):
        from Dlg import DLG_Config_affectations
        dlg = DLG_Config_affectations.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.toolBook.MAJ_page_si_affichee("recrutement")

    def On_param_diffuseurs(self, event):
        from Dlg import DLG_Config_diffuseurs
        dlg = DLG_Config_diffuseurs.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.toolBook.MAJ_page_si_affichee("recrutement")

    def On_param_offres(self, event):
        from Dlg import DLG_Config_emplois
        dlg = DLG_Config_emplois.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.toolBook.MAJ_page_si_affichee("recrutement")

    def On_param_vacances(self, event):
        from Dlg import DLG_Vacances
        dlg = DLG_Vacances.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.toolBook.MAJ_page_si_affichee("accueil")
        self.toolBook.MAJ_page_si_affichee("presences")

    def On_param_feries(self, event):
        from Dlg import DLG_Feries
        dlg = DLG_Feries.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.toolBook.MAJ_page_si_affichee("accueil")
        self.toolBook.MAJ_page_si_affichee("presences")

    def On_outils_outlook(self ,event):
        # Vérifie qu'un fichier est chargé
        if self.userConfig["nomFichier"] == "" :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez chargé aucun fichier."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
    
        from Dlg import DLG_Export_outlook
        outlook = DLG_Export_outlook.LibOutlook()
        # Recherche si Outlook peut être ouvert
        dlg = wx.MessageDialog(self, _(u"Un test va être effectué pour vérifier que Outlook est bien accessible sur votre ordinateur.\n\nSi c'est bien le cas, Outlook va vous demander si vous acceptez que cet accès ait bien lieu.\n\nCochez la case 'Autoriser l'accès' et sélectionnez un temps de 10 minutes..."), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
            
        if outlook.echec == True :
            # Pas de outlook accessible :
            dlg = wx.MessageDialog(self, _(u"Microsoft Outlook ne peut pas être ouvert..."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if outlook.Test() == False :
            # Outlook est verrouillé:
            dlg = wx.MessageDialog(self, _(u"Microsoft Outlook ne peut pas être ouvert.\nIl semble verrouillé..."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Ouverture de la frame exportation
        dlg = DLG_Export_outlook.Dialog(None)
        dlg.ShowModal()
        dlg.Destroy()

    def On_outils_updater(self, event):
        """Mises à jour internet """
        from Dlg import DLG_Updater
        dlg = DLG_Updater.Dialog(self)
        dlg.ShowModal() 
        installation = dlg.GetEtat() 
        dlg.Destroy()
        if installation == True :
            self.Quitter(videRepertoiresTemp=False, sauvegarde_auto=False)
            self.Destroy()

    def On_outils_frais(self, event):
        """ Gestion globale des frais de déplacements """
        from Dlg import DLG_Gestion_frais
        dlg = DLG_Gestion_frais.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_outils_registre(self, event):
        from Dlg import DLG_Liste_contrats
        dlg = DLG_Liste_contrats.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_outils_photos(self, event):
        """ Imprimer les photos des personnes """
        # Ouverture de la frame d'impression des photos  
        from Dlg import DLG_Impression_photo
        dlg = DLG_Impression_photo.DialogSelectionPersonnes(None)
        dlg.ShowModal()
        dlg.Destroy()

    def On_outils_publipostage(self, event):
        """ Imprimer par publipostage """
        from Dlg import DLG_Publiposteur_Choix
        dlg = DLG_Publiposteur_Choix.Dialog(None)
        dlg.ShowModal()
        dlg.Destroy()

    def On_outils_emails(self, event):
        """ Lancer Editeur d'emails """
        from Dlg import DLG_Mailer
        dlg = DLG_Mailer.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def On_outils_teamword(self, event):
        """ Lancer Teamword """
        from Dlg import DLG_Teamword
        frame = DLG_Teamword.MyFrame(None)
        frame.Show()

    def On_outils_ouvrir_rep_utilisateur(self, event):
        """ Ouvrir le répertoire Utilisateur """
        UTILS_Fichiers.OuvrirRepertoire(UTILS_Fichiers.GetRepUtilisateur())

    def On_outils_ouvrir_rep_donnees(self, event):
        """ Ouvrir le répertoire Utilisateur """
        UTILS_Fichiers.OuvrirRepertoire(UTILS_Fichiers.GetRepData())

    def On_outils_ouvrir_rep_modeles(self, event):
        """ Ouvrir le répertoire des modèles de documents """
        UTILS_Fichiers.OuvrirRepertoire(UTILS_Fichiers.GetRepModeles())

    def On_outils_ouvrir_rep_editions(self, event):
        """ Ouvrir le répertoire des éditions de documents """
        UTILS_Fichiers.OuvrirRepertoire(UTILS_Fichiers.GetRepEditions())

    def On_aide_aide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide(None)

    def On_aide_forum(self, event):
        """ Accéder au forum d'entraide """
        FonctionsPerso.LanceFichierExterne("https://teamworks.ovh/index.php/assistance/le-forum")

    def On_aide_videos(self, event):
        """ Accéder au tutoriels vidéos """
        FonctionsPerso.LanceFichierExterne("https://teamworks.ovh/index.php/assistance/les-tutoriels-videos")

    def On_propos_versions(self, event):
        """ A propos : Notes de versions """
        # Lecture du fichier
        import codecs
        txtLicence = codecs.open(Chemins.GetMainPath("Versions.txt"), encoding='utf-8', mode='r')
        msg = txtLicence.read()
        txtLicence.close()
        from Dlg import DLG_Messagebox
        if six.PY2:
            msg = msg.decode("iso-8859-15")
        dlg = DLG_Messagebox.Dialog(self, titre=_(u"Notes de versions"), introduction=_("Liste des versions du logiciel :"), detail=msg, icone=wx.ICON_INFORMATION, boutons=[_(u"Fermer"), ], defaut=0)
        dlg.ShowModal()
        dlg.Destroy()

    def On_propos_licence(self, event):
        """ A propos : Licence """
        import wx.lib.dialogs
        txtLicence = open(Chemins.GetMainPath("Licence.txt"), "r")
        msg = txtLicence.read()
        txtLicence.close()
        if six.PY2:
            msg = msg.decode("iso-8859-15")
        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg, _(u"A propos"), size=(500, 500))
        dlg.ShowModal()

    def On_propos_soutenir(self, event):
        """ A propos : Soutenir """
        from Dlg import DLG_Financement
        dlg = DLG_Financement.Dialog(None, code="documentation")
        dlg.ShowModal()
        dlg.Destroy()

    def On_propos_propos(self, event):
        """ A propos : A propos """
        texte = u"""
"Teamworks - gestion d'équipe
Copyright © 2008-2019 Ivan LUCAS

Remerciements :

- Aurélie, pour son soutien et son aide technique
- Jacques Delage pour les beta-tests et les suggestions
- Pacificator et toute la communauté Python de developpez.com
- Robin Dunn, pour ses travaux et son aide sur wxPython
- Tous les beta-testeurs pour leur suggestions et leurs remarques

Et en vrac : 
Guido van Rossum (Python), Gerhard Häring (pysqlite), 
reportLab team (reportlab), Mark Hammond (pywin32), 
Phillip Piper (ObjectListView), Armin Rigo (Psycho)...

"""
        dlg = wx.MessageDialog(self, texte, "A propos", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


    def MAJAffichage(self):
        # Mise à jour des panels :
        self.toolBook.GetPage(0).MAJpanel() 

    
    def GetVersionApplication(self):
        return VERSION_APPLICATION

    def RechercheMAJinternet(self):
        """ Recherche une mise à jour sur internet """
        # Récupère la version de l'application
        versionApplication = VERSION_APPLICATION
        # Récupère la version de la MAJ sur internet
        try :
            if "linux" in sys.platform :
                # Version Debian
                fichierVersions = urlopen('https://raw.githubusercontent.com/Noethys/Teamworks/master/teamworks/Versions.txt', timeout=5)
            else:
                # Version Windows
                fichierVersions = urlopen('http://www.teamworks.ovh/fichiers/windows/Versions.txt', timeout=5)
            texteNouveautes= fichierVersions.read()
            fichierVersions.close()
            if six.PY3:
                texteNouveautes = texteNouveautes.decode("utf-8")
            pos_debut_numVersion = texteNouveautes.find("n")
            if "(" in texteNouveautes[:50] :
                pos_fin_numVersion = texteNouveautes.find("(")
            else:
                pos_fin_numVersion = texteNouveautes.find(":")
            versionMaj = texteNouveautes[pos_debut_numVersion+1:pos_fin_numVersion].strip()
        except Exception as err:
            print(err)
            print("Recuperation du num de version de la MAJ sur internet impossible.")
            versionMaj = "0.0.0.0"
        # Compare les deux versions et renvois le résultat
        try :
            if self.ConvertVersionTuple(versionMaj) > self.ConvertVersionTuple(VERSION_APPLICATION) :
                self.versionMAJ = versionMaj
                return True
            else:
                return False
        except :
            return False


    def GetVersionAnnonce(self):
        if "annonce" in self.userConfig :
            versionAnnonce = self.userConfig["annonce"]
            if versionAnnonce != None :
                return versionAnnonce
        return (0, 0, 0, 0)

    def Annonce(self):
        """ Création une annonce au premier démarrage du logiciel """
        nomFichier = sys.executable
        if nomFichier.endswith("python.exe") == False :
            versionAnnonce = self.ConvertVersionTuple(self.GetVersionAnnonce())
            versionLogiciel = self.ConvertVersionTuple(VERSION_APPLICATION)
            if versionAnnonce < versionLogiciel :
                # Déplace les fichiers exemples vers le répertoire des fichiers de données
                try :
                    UTILS_Fichiers.DeplaceExemples()
                except Exception as err:
                    print("Erreur dans UTILS_Fichiers.DeplaceExemples :")
                    print((err,))
                # Affiche le message d'accueil
                from Dlg import DLG_Message_accueil
                dlg = DLG_Message_accueil.Dialog(self)
                dlg.ShowModal()
                dlg.Destroy()
                # Mémorise le numéro de version actuel
                self.userConfig["annonce"] = versionLogiciel

    def Assistant_demarrage(self, mode="ouverture"):
        """ Charge l'assistant démarrage """
        # Récupère l'état du checkBox affichage
        if "assistant_demarrage" in self.userConfig :
            checkAffichage = self.userConfig["assistant_demarrage"]
        else:
            checkAffichage = False
        # Si on est en mode "menu" :Vérifie s'il faut afficher l'assistant ou non
        if mode == "ouverture" :
            if checkAffichage == True :
                return False
        # Afficher ouvrir dernier fichier dans assistant ?
        if self.nomDernierFichier == "":
            afficherDernierFichier = False
        else:
            afficherDernierFichier = True
        
        # Charge la boîte de dialogue
        from Dlg import DLG_Assistant_demarrage
        dlg = DLG_Assistant_demarrage.Dialog(None, checkAffichage=checkAffichage, afficherDernierFichier=afficherDernierFichier, nomDernierFichier=self.nomDernierFichier)
        dlg.ShowModal()
        choix = dlg.GetChoix()
        checkAffichage = dlg.GetCheckAffichage()
        dlg.Destroy()
        # Mémorise l'état du checkBox affichage
        self.userConfig["assistant_demarrage"] = checkAffichage
        # Charge la commande demandée
        if choix != None :
            if choix == 1 : FonctionsPerso.LanceFichierExterne(_(u"https://www.teamworks.ovh"))
            if choix == 2 : self.On_fichier_nouveau(None)
            if choix == 3 : FonctionsPerso.LanceFichierExterne("https://teamworks.ovh/index.php/assistance/les-tutoriels-videos")
            if choix == 4 : self.On_fichier_ouvrir(None)
            if choix == 5 : self.OuvrirFichier(nomFichier="Exemple")
            if choix == 6 : self.OuvrirFichier(nomFichier=self.nomDernierFichier)
        else :
            # Utiliser directement TW
            pass
            
        return True
    
    def EstFichierExemple(self):
        """ Vérifie si c'est un fichier EXEMPLE qui est ouvert actuellement """
        if self.userConfig["nomFichier"] != None :
            if "EXEMPLE_" in self.userConfig["nomFichier"] :
                return True
        return False

    def AnnonceFinancement(self):
        # Vérifie si identifiant saisi et valide
        identifiant = UTILS_Config.GetParametre("enregistrement_identifiant", defaut=None)
        if identifiant != None:
            # Vérifie nbre jours restants
            code = UTILS_Config.GetParametre("enregistrement_code", defaut=None)
            validite = DLG_Enregistrement.GetValidite(identifiant, code)
            if validite != False:
                date_fin_validite, nbreJoursRestants = validite
                dateDernierRappel = UTILS_Config.GetParametre("enregistrement_dernier_rappel", defaut=None)

                if nbreJoursRestants < 0:
                    # Licence périmée
                    if dateDernierRappel != None:
                        UTILS_Config.SetParametre("enregistrement_dernier_rappel", None)

                elif nbreJoursRestants <= 30:
                    # Licence bientôt périmée
                    UTILS_Config.SetParametre("enregistrement_dernier_rappel", datetime.date.today())
                    if dateDernierRappel != None:
                        nbreJoursDepuisRappel = (dateDernierRappel - datetime.date.today()).days
                    else:
                        nbreJoursDepuisRappel = None
                    if nbreJoursDepuisRappel == None or nbreJoursDepuisRappel >= 10:
                        from Dlg import DLG_Messagebox
                        image = wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Cle.png"), wx.BITMAP_TYPE_ANY)
                        introduction = _(u"Votre licence d'accès au manuel de référence en ligne se termine dans %d jours. \n\nSi vous le souhaitez, vous pouvez continuer à bénéficier de cet accès et prolonger votre soutien financier au projet Teamworks en renouvelant votre abonnement Classic ou Premium.") % nbreJoursRestants
                        dlg = DLG_Messagebox.Dialog(self, titre=_(u"Enregistrement"),
                                                    introduction=introduction, detail=None,
                                                    icone=image, boutons=[(u"Renouveler mon abonnement"), _(u"Fermer")], defaut=0)
                        reponse = dlg.ShowModal()
                        dlg.Destroy()
                        if reponse == 0:
                            FonctionsPerso.LanceFichierExterne("https://teamworks.ovh/public/bon_commande_documentation.pdf")
                        return True

                else:
                    # Licence valide
                    if dateDernierRappel != None:
                        UTILS_Config.SetParametre("enregistrement_dernier_rappel", None)

        if random.randrange(1, 100) <= 10:
            from Dlg import DLG_Financement
            dlg = DLG_Financement.Dialog(self)
            dlg.ShowModal()
            dlg.Destroy()
            return True
        else:
            return False


class SaisiePassword(wx.Dialog):
    def __init__(self, parent, id=-1, title=_(u"Saisie du mot de passe"), nomFichier=""):
        wx.Dialog.__init__(self, parent, id, title)

        self.sizer_3_staticbox = wx.StaticBox(self, -1, "")
        if "[RESEAU]" in nomFichier :
            nomFichierTmp = nomFichier[nomFichier.index("[RESEAU]"):]
        else:
            nomFichierTmp = nomFichier
        self.label_2 = wx.StaticText(self, -1, _(u"Le fichier '") + self.FormateNomFichier(nomFichierTmp) + _(u"' est protégé."))
        self.label_password = wx.StaticText(self, -1, "Mot de passe :")
        self.text_password = wx.TextCtrl(self, -1, "", size=(200, -1), style=wx.TE_PASSWORD)
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, id=wx.ID_OK, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        self.__set_properties()
        self.__do_layout()
        
    def FormateNomFichier(self, nom):
        max = 25
        if len(nom) > max :
            nomFichier = nom[:max] + "..."
        else:
            nomFichier = nom
        return nomFichier

    def __set_properties(self):
        self.text_password.SetToolTip(wx.ToolTip(_(u"Saisissez votre mot de passe ici")))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        grid_sizer_2 = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_4 = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.HORIZONTAL)
        grid_sizer_3 = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_2.Add(self.label_2, 0, wx.ALL, 10)
        grid_sizer_3.Add(self.label_password, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_3.Add(self.text_password, 0, wx.EXPAND, 0)
        grid_sizer_3.AddGrowableCol(1)
        sizer_3.Add(grid_sizer_3, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_2.Add(sizer_3, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_4.Add((20, 20), 0, 0, 0)
        grid_sizer_4.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_4.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_4.AddGrowableCol(0)
        grid_sizer_2.Add(grid_sizer_4, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_2)
        grid_sizer_2.AddGrowableCol(0)
        grid_sizer_2.Fit(self)
        self.Layout()
        self.CenterOnScreen()

    def GetPassword(self):
        return self.text_password.GetValue()


# ----------------------------------------------------------------------------------------------------------------------------------------------------------

class MyApp(wx.App):
    def OnInit(self):
        #wx.InitAllImageHandlers()
        heure_debut = time.time()
        # wx.Locale(wx.LANGUAGE_FRENCH)

        # AdvancedSplashScreen
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Special/Logo_splash.png"), wx.BITMAP_TYPE_PNG)
        frame = AS.AdvancedSplash(None, bitmap=bmp, timeout=1000, agwStyle=AS.AS_TIMEOUT | AS.AS_CENTER_ON_SCREEN)
        frame.Refresh()
        frame.Update()
        if 'phoenix' not in wx.PlatformInfo:
            wx.Yield()

        # Création de la frame principale
        frame = MyFrame(None)
        self.SetTopWindow(frame)
        frame.Show()   

        # Affiche une annonce si c'est un premier démarrage du logiciel
        frame.Annonce()

        # Charge l'assistant ou dernier fichier
        if frame.afficherAssistant == True :
            frame.Assistant_demarrage(mode="ouverture")
        else:
            frame.OuvrirDernierFichier()

        # Après ouverture d'un fichier :
        if frame.EstFichierExemple() == False:
            financement = frame.AnnonceFinancement()

        # Affiche le temps de démarrage de TW
        duree = time.time()-heure_debut

        return True


        
class Redirect(object):
    def __init__(self, nomJournal=""):
        self.filename = open(nomJournal, "a")

    def write(self, text):
        if self.filename.closed:
            pass
        else:
            self.filename.write(text)
            self.filename.flush()



if __name__ == "__main__":
    # Vérifie l'existence des répertoires dans le répertoire Utilisateur
    for rep in ("Temp", "Updates", "Sync", "Lang", "Modeles", "Editions") :
        rep = UTILS_Fichiers.GetRepUtilisateur(rep)
        if os.path.isdir(rep) == False :
            os.makedirs(rep)

    # Vérifie si des fichiers du répertoire Data sont à déplacer vers le répertoire Utilisateur
    UTILS_Fichiers.DeplaceFichiers()

    # Initialisation du fichier de customisation
    CUSTOMIZE = UTILS_Customize.Customize()

    # Crash report
    UTILS_Rapport_bugs.Activer_rapport_erreurs(version=VERSION_APPLICATION)

    # Log
    nomJournal = UTILS_Fichiers.GetRepUtilisateur(CUSTOMIZE.GetValeur("journal", "nom", "journal.log"))

    # Supprime le journal.log si supérieur à 10 Mo
    if os.path.isfile(nomJournal) :
        taille = os.path.getsize(nomJournal)
        if taille > 5000000 :
            os.remove(nomJournal)

    # Redirection vers un fichier
    nomFichier = sys.executable
    if nomFichier.endswith("python.exe") == False and CUSTOMIZE.GetValeur("journal", "actif", "1") != "0" and os.path.isfile("nolog.txt") == False :
        sys.stdout = Redirect(nomJournal)

    # Lancement de l'application
    app = MyApp(redirect=False)

    app.MainLoop()

    

