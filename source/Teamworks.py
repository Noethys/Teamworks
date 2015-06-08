#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-15 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------


from time import strftime
import time
HEUREDEBUT = time.time()


import wx

import UTILS_Config
import UTILS_Parametres

import Accueil
import Personnes
import Presences
import Recrutement
import Configuration
import Calendrier
import FonctionsPerso
import GestionDB
import os
import datetime
import Config_Sauvegarde
import locale
import urllib
import random
import sys
import Attente

import shelve
import dbhash
import anydbm

import threading

import wx.lib.agw.advancedsplash as AS
import wx.lib.agw.toasterbox as Toaster
import wx.lib.agw.pybusyinfo as PBI

   

# Constantes
VERSION_APPLICATION = FonctionsPerso.GetVersionTeamworks()
MAIL_AUTEUR = "teamworks" + "@clsh-lannilis.com"
ADRESSE_FORUM = "http://teamworks.forumactif.com"
            
            
            
class Toolbook(wx.Toolbook):
    def __init__(self, parent):
        wx.Toolbook.__init__(self, parent, -1, style= wx.BK_TOP)
        self.Build_Pages()
        
    def Build_Pages(self):
        """ Construit les pages du toolbook """
        # Images du ToolBook
        il = wx.ImageList(32, 32)
        self.img_accueil  = il.Add(wx.Bitmap("Images/32x32/Maison.png", wx.BITMAP_TYPE_PNG))
        self.img_personnes  = il.Add(wx.Bitmap("Images/32x32/Personnes.png", wx.BITMAP_TYPE_PNG))
        self.img_presences  = il.Add(wx.Bitmap("Images/32x32/Horloge.png", wx.BITMAP_TYPE_PNG))
        self.img_recrutement  = il.Add(wx.Bitmap("Images/32x32/Recrutement.png", wx.BITMAP_TYPE_PNG))
        self.img_configuration  = il.Add(wx.Bitmap("Images/32x32/Configuration.png", wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)
        
        # Création des pages
        self.AddPage(Accueil.Panel(self), u"Accueil", imageId=self.img_accueil)
        self.AddPage(Personnes.PanelPersonnes(self), u"Personnes", imageId=self.img_personnes)
        self.AddPage(Presences.PanelPresences(self), u"Présences", imageId=self.img_presences)
        self.AddPage(Recrutement.Panel(self), u"Recrutement", imageId=self.img_recrutement)
        self.AddPage(Configuration.Panel(self), u"Configuration", imageId=self.img_configuration)
        
        # Met le texte à droite dans la toolbar
        tb = self.GetToolBar()        
        tb.SetWindowStyleFlag(wx.TB_HORZ_TEXT)
        self.SetInternalBorder(0)
        
        self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGING, self.OnPageChanging)

        
    def MAJ_panel(self, numPage=0):
        """ Test de MAJ des panels lors d'un changement d'onglet """
        self.Freeze() # Gèle l'affichage pour éviter des clignements
        try : 
            self.GetPage(numPage).MAJpanel() 
        except :
            pass
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
        toolBar.EnableTool(5, etat) # Configuration
        
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
        
        # Ecrit la date et l'heure dans le journal.log
        dateDuJour = datetime.datetime.now().strftime("%A %d %B %Y %H:%M:%S")
        nomSysteme = sys.platform
        print "------------ " + dateDuJour + " | v:%s | sys:%s ------------" % (VERSION_APPLICATION, nomSysteme)
        
        try : locale.setlocale(locale.LC_ALL, 'FR')
        except : pass
        
        # Diminution de la taille de la police sous linux
        if "linux" in sys.platform :
            defaultFont = self.GetFont()
            defaultFont.SetPointSize(8)
            self.SetFont(defaultFont)
        
        # Recherche si une mise à jour internet existe
        self.MAJexiste = self.RechercheMAJinternet()
        
        # Vérifie que le fichier de configuration existe bien
        self.nomFichierConfig = "Data/Config.dat"
        test = os.path.isfile(self.nomFichierConfig) 
        if test == False :
            # Déplacement du userconfig vers le répertoire Data pour TW2
            if os.path.isfile("userconfig.dat") :
                import shutil
                shutil.move("userconfig.dat", "Data/Config.dat")
            else :
                # Création du fichier de configuration
                cfg = UTILS_Config.FichierConfig(nomFichier=self.nomFichierConfig)
                cfg.SetDictConfig(dictConfig={ "nomFichier" : "", "derniersFichiers" : [], "taille_fenetre" : (0, 0) } )
                self.nouveauFichierConfig = True
        else:
            self.nouveauFichierConfig = False

        # Suppression du fichier Exemple ancien de TW1
        if os.path.isfile("Data/Exemple.twk") :
            os.remove("Data/Exemple.twk")

        # Récupération des fichiers de configuration
        self.userConfig = self.GetFichierConfig(nomFichier=self.nomFichierConfig) # Fichier de config de l'utilisateur
        
        # Récupération du nom du dernier fichier chargé
        self.nomDernierFichier = self.userConfig["nomFichier"]
        self.userConfig["nomFichier"] = ""
                
        if self.userConfig.has_key("assistant_demarrage") :
            if self.userConfig["assistant_demarrage"] == True :
                self.afficherAssistant = False
            else: self.afficherAssistant = True
        else:
            self.afficherAssistant = True
                    
        # Affiche le titre du fichier en haut de la frame
        self.SetTitleFrame(nomFichier="")
        
        # Construit la barre de menus
        self.Build_MenuBar()
        # Construit la barre de status
        self.Build_Statusbar()
        # Construit le toolbool
        self.toolBook = Toolbook(self)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.__do_layout()
        
        # Désactive les commandes
        self.menubar.EnableTop(1, False)
        self.menubar.EnableTop(2, False)
        self.toolBook.ActiveToolBook(False)
        
            

    def __do_layout(self):
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetMinSize((800, 600))
        sizer_base = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(self.toolBook, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        self.SetSize((800, 600))

        # Détermine la taille de la fenêtre
        if self.userConfig.has_key("taille_fenetre") == False :
            self.userConfig["taille_fenetre"] = (0, 0)
        
        taille_fenetre = self.userConfig["taille_fenetre"]
        if taille_fenetre == (0, 0) :
            self.Maximize(True)
        else:
            self.SetSize(taille_fenetre)
        self.Centre()



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
                    dlg2 = wx.MessageDialog(self, u"Votre mot de passe est erroné.", u"Mot de passe erroné", wx.OK | wx.ICON_ERROR)
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
            nomFichier = u"Fichier réseau : %s | Utilisateur : %s" % (nomFichier, user)
        if nomFichier != "" :
            nomFichier = " - [" + nomFichier + "]"
        titreFrame = "Teamworks" + " v" + VERSION_APPLICATION + nomFichier
        self.SetTitle(titreFrame)
    
    def Build_MenuBar(self):
        """ Construit la barre de menus """
        menubar = wx.MenuBar()
        
        # Menu Fichier
        menu1 = wx.Menu()
        
        item = wx.MenuItem(menu1, 100, u"Assistant Démarrage", u"Ouvrir l'assistant démarrage")
        item.SetBitmap(wx.Bitmap("Images/16x16/Assistant.png", wx.BITMAP_TYPE_PNG))
        menu1.AppendItem(item)
        
        menu1.AppendSeparator()
        
        item = wx.MenuItem(menu1, 101, u"Créer un nouveau fichier\tCtrl+N", u"Créer un nouveau fichier")
        item.SetBitmap(wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG))
        menu1.AppendItem(item)
        item = wx.MenuItem(menu1, 102, u"Ouvrir un fichier\tCtrl+O", u"Ouvrir un fichier existant")
        item.SetBitmap(wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)) 
        menu1.AppendItem(item)
        item = wx.MenuItem(menu1, 103, u"Fermer le fichier\tCtrl+F", u"Fermer le fichier ouvert")
        item.SetBitmap(wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)) 
        menu1.AppendItem(item)
        
        menu1.AppendSeparator()
        
        item = wx.MenuItem(menu1, 104, u"Créer une sauvegarde\tCtrl+S", u"Créer une sauvegarde globale des données")
        item.SetBitmap(wx.Bitmap("Images/16x16/Sauvegarder.png", wx.BITMAP_TYPE_PNG)) 
        menu1.AppendItem(item)
        item = wx.MenuItem(menu1, 105, u"Restaurer une sauvegarde\tCtrl+R", u"Restaurer une sauvegarde")
        item.SetBitmap(wx.Bitmap("Images/16x16/Restaurer.png", wx.BITMAP_TYPE_PNG)) 
        menu1.AppendItem(item)

        menu1.AppendSeparator()

        item = wx.MenuItem(menu1, 107, u"Convertir en fichier réseau", u"Convertir le fichier ouvert en fichier réseau")
        item.SetBitmap(wx.Bitmap("Images/16x16/Conversion_reseau.png", wx.BITMAP_TYPE_PNG)) 
        menu1.AppendItem(item)
        item.Enable(False)
        item = wx.MenuItem(menu1, 108, u"Convertir en fichier local", u"Convertir le fichier ouvert en fichier local")
        item.SetBitmap(wx.Bitmap("Images/16x16/Conversion_local.png", wx.BITMAP_TYPE_PNG)) 
        menu1.AppendItem(item)
        item.Enable(False)
        
        menu1.AppendSeparator()
        
        item = wx.MenuItem(menu1, 106, u"Quitter\tCtrl+Q", u"Quitter l'application")
        item.SetBitmap(wx.Bitmap("Images/16x16/Quitter.png", wx.BITMAP_TYPE_PNG)) 
        menu1.AppendItem(item)
        
        menu1.AppendSeparator()
        
        # Intégration des derniers fichiers ouverts :
        listeDerniersFichiersTmp = self.userConfig["derniersFichiers"]
        
        # Vérification de la liste
        listeDerniersFichiers = []
        for nomFichier in listeDerniersFichiersTmp :
            
            if "[RESEAU]" in nomFichier :
                # Version RESEAU
                listeDerniersFichiers.append(nomFichier)
            else:
                # VERSION LOCAL
                fichier = "Data/" + nomFichier + "_TDATA.dat"
                test = os.path.isfile(fichier)
                if test == True : 
                    listeDerniersFichiers.append(nomFichier)
        self.userConfig["derniersFichiers"] = listeDerniersFichiers
        
        if len(listeDerniersFichiers) > 0 : 
            index = 0
            for nomFichier in listeDerniersFichiers :
                if "[RESEAU]" in nomFichier :
                    nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
                item = wx.MenuItem(menu1, 150 + index, str(index+1) + ". " + nomFichier, u"Ouvrir le fichier : " + nomFichier)
                menu1.AppendItem(item)
                index += 1
            self.Bind(wx.EVT_MENU_RANGE, self.MenuDerniersFichiers, id=150, id2=150 + index)

        menubar.Append(menu1, "Fichier")
        
        self.Bind(wx.EVT_MENU, self.MenuAssistantDemarrage, id=100)
        self.Bind(wx.EVT_MENU, self.MenuNouveau, id=101)
        self.Bind(wx.EVT_MENU, self.MenuOuvrir, id=102)
        self.Bind(wx.EVT_MENU, self.MenuFermer, id=103)
        self.Bind(wx.EVT_MENU, self.MenuSauvegarder, id=104)
        self.Bind(wx.EVT_MENU, self.MenuRestaurer, id=105)
        self.Bind(wx.EVT_MENU, self.MenuQuitter, id=106)
        self.Bind(wx.EVT_MENU, self.On_fichier_Convertir_reseau, id=107)
        self.Bind(wx.EVT_MENU, self.On_fichier_Convertir_local, id=108)
        
        # Menu Affichage
        menu2 = wx.Menu()
        
        item = wx.MenuItem(menu2, 201, u"Gestion des Gadgets de la page d'accueil", u"Gestion des Gadgets de la page d'accueil")
        item.SetBitmap(wx.Bitmap("Images/16x16/Calendrier_ajout.png", wx.BITMAP_TYPE_PNG))
        menu2.AppendItem(item)
        
        menubar.Append(menu2, "Affichage")
        
        self.Bind(wx.EVT_MENU, self.MenuGadgets, id=201)
        
        # Menu Outils
        menu3 = wx.Menu()
        
        item = wx.MenuItem(menu3, 305, u"Imprimer des photos de personnes", u"Imprimer des photos de personnes")
        item.SetBitmap(wx.Bitmap("Images/16x16/Personnes.png", wx.BITMAP_TYPE_PNG))
        menu3.AppendItem(item)
        item = wx.MenuItem(menu3, 304, u"Gestion des frais de déplacements", u"Gestion des frais de déplacements")
        item.SetBitmap(wx.Bitmap("Images/16x16/Calculatrice.png", wx.BITMAP_TYPE_PNG))
        menu3.AppendItem(item)
        menu3.AppendSeparator()
        item = wx.MenuItem(menu3, 301, u"Exporter les personnes dans MS Outlook", u"Exporter les personnes dans MS Outlook")
        item.SetBitmap(wx.Bitmap("Images/16x16/Outlook.png", wx.BITMAP_TYPE_PNG))
        menu3.AppendItem(item)
        if "linux" in sys.platform :
            item.Enable(False)
        menu3.AppendSeparator()
        item = wx.MenuItem(menu3, 303, u"Envoyer un mail groupé avec votre client de messagerie", u"Envoyer un mail groupé à un panel de personnes")
        item.SetBitmap(wx.Bitmap("Images/16x16/Mail.png", wx.BITMAP_TYPE_PNG))
        menu3.AppendItem(item)
        item = wx.MenuItem(menu3, 306, u"Créer des courriers ou des emails par publipostage", u"Créer des courriers ou des emails par publipostage")
        item.SetBitmap(wx.Bitmap("Images/16x16/Mail.png", wx.BITMAP_TYPE_PNG))
        menu3.AppendItem(item)
        menu3.AppendSeparator()
        item = wx.MenuItem(menu3, 307, u"Lancer Teamword, l'éditeur de texte", u"Lancer Teamword, l'éditeur de texte")
        item.SetBitmap(wx.Bitmap("Images/16x16/Document.png", wx.BITMAP_TYPE_PNG))
        menu3.AppendItem(item)
                
        menubar.Append(menu3, "Outils")
        
        self.Bind(wx.EVT_MENU, self.MenuExportOutlook, id=301)
        self.Bind(wx.EVT_MENU, self.MenuEnvoiMailGroupe, id=303)
        self.Bind(wx.EVT_MENU, self.MenuGestionFrais, id=304)
        self.Bind(wx.EVT_MENU, self.MenuImprimerPhotos, id=305)
        self.Bind(wx.EVT_MENU, self.MenuPublipostage, id=306)
        self.Bind(wx.EVT_MENU, self.MenuTeamword, id=307)
        
        # Menu Internet
        menu6 = wx.Menu()
        
        item = wx.MenuItem(menu6, 601, u"Rechercher des mises à jour du logiciel", u"Rechercher des mises à jour du logiciel")
        item.SetBitmap(wx.Bitmap("Images/16x16/Updater.png", wx.BITMAP_TYPE_PNG))
        menu6.AppendItem(item)
        
        menubar.Append(menu6, u"Internet")
        
        self.Bind(wx.EVT_MENU, self.MenuUpdater, id=601)
        
        # Menu Aide
        menu4 = wx.Menu()
        
        item = wx.MenuItem(menu4, 401, u"Consulter l'aide intégrée\tCtrl+A", u"Consulter l'aide de TeamWorks")
        item.SetBitmap(wx.Bitmap("Images/16x16/Aide.png", wx.BITMAP_TYPE_PNG))
        menu4.AppendItem(item)
        
        item = wx.MenuItem(menu4, 404, u"Télécharger le guide de l'utilisateur (248 pages - PDF)", u"Télécharger le guide de l'utilisateur (248 pages - PDF)")
        item.SetBitmap(wx.Bitmap("Images/16x16/Guide.png", wx.BITMAP_TYPE_PNG))
        menu4.AppendItem(item)
        
        item = wx.MenuItem(menu4, 403, u"Accéder au forum TeamWorks", u"Accéder au forum TeamWorks")
        item.SetBitmap(wx.Bitmap("Images/16x16/Planete.png", wx.BITMAP_TYPE_PNG))
        menu4.AppendItem(item)
        
        menu4.AppendSeparator()
        
        item = wx.MenuItem(menu4, 402, u"Envoyer un mail à l'auteur", u"Envoyer un mail à l'auteur de Teamworks")
        item.SetBitmap(wx.Bitmap("Images/16x16/Mail.png", wx.BITMAP_TYPE_PNG))
        menu4.AppendItem(item)
        
        menubar.Append(menu4, "Aide")
        
        self.Bind(wx.EVT_MENU, self.MenuAide, id=401)
        self.Bind(wx.EVT_MENU, self.MenuForum, id=403)
        self.Bind(wx.EVT_MENU, self.MenuMailAuteur, id=402)
        self.Bind(wx.EVT_MENU, self.MenuTelechargerGuide, id=404)
        
        # Menu A Propos
        menu7 = wx.Menu()
        
        item = wx.MenuItem(menu7, 701, u"Pourquoi et comment faire un don de soutien ?", u"Pourquoi et comment faire un don de soutien ?")
        item.SetBitmap(wx.Bitmap("Images/16x16/Smile.png", wx.BITMAP_TYPE_PNG))
        menu7.AppendItem(item)
        
        self.Bind(wx.EVT_MENU, self.MenuDons, id=701)
        
        menubar.Append(menu7, u"Soutenir Teamworks")
        
        # Menu A Propos
        menu5 = wx.Menu()
        
        item = wx.MenuItem(menu5, 501, u"Notes de versions", u"Notes de versions")
        item.SetBitmap(wx.Bitmap("Images/16x16/Document.png", wx.BITMAP_TYPE_PNG))
        menu5.AppendItem(item)
        item = wx.MenuItem(menu5, 502, u"Licence", u"Licence du logiciel")
        item.SetBitmap(wx.Bitmap("Images/16x16/Document.png", wx.BITMAP_TYPE_PNG))
        menu5.AppendItem(item)
        menu5.AppendSeparator()
        item = wx.MenuItem(menu5, 503, u"A propos", u"A propos")
        item.SetBitmap(wx.Bitmap("Images/16x16/Document.png", wx.BITMAP_TYPE_PNG))
        menu5.AppendItem(item)
        
        self.Bind(wx.EVT_MENU, self.MenuVersions, id=501)
        self.Bind(wx.EVT_MENU, self.MenuLicence, id=502)
        self.Bind(wx.EVT_MENU, self.MenuApropos, id=503)
        
        menubar.Append(menu5, "A propos")
        
        
        
        # Finalisation Barre de menu
        self.SetMenuBar(menubar)
        self.menubar = menubar #.EnableTop(1, False)
        
        
    def Build_Statusbar(self):
        self.statusbar = self.CreateStatusBar(2, 0)
        self.statusbar.SetStatusWidths( [400, -1] )
        
    def OnSize(self, event):
        #self.SetTitle(u"Taille de la fenêtre : %s" % event.GetSize())
        event.Skip()      
       
    def GetFichierConfig(self, nomFichier=""):
        """ Récupère le dictionnaire du fichier de config """
        cfg = FonctionsPerso.FichierConfig(nomFichier)
        return cfg.GetDictConfig()

    def SaveFichierConfig(self, nomFichier):
        """ Sauvegarde le dictionnaire du fichier de config """
        cfg = FonctionsPerso.FichierConfig(nomFichier)
        cfg.SetDictConfig(dictConfig=self.userConfig )

    def OnClose(self, event):
        self.Quitter()
        event.Skip()
        
    def Quitter(self, videRepertoiresTemp=True):
        """ Fin de l'application """
        
##        if self.userConfig["nomFichier"] != "" :
##            # Vérifie si une Sauvegarde automatique est demandée
##            DB = GestionDB.DB()        
##            req = "SELECT save_active FROM divers WHERE IDdivers=1;"
##            DB.ExecuterReq(req)
##            save_active = DB.ResultatReq()
##            DB.Close()
##            if save_active[0][0] == 1 :
##                # Sauvegarde automatique
##                self.SetStatusText(u"Veuillez patienter pendant la sauvegarde automatique des données...")
##                saveAuto = Config_Sauvegarde.Sauvegarde_auto()
##                saveAuto.Save()
##                self.SetStatusText("")
##                # Enregistre la date du jour comme date de dernière sauvegarde
##                date_jour =  str(datetime.date.today())  
##                listeDonnees = [("save_date_derniere",  date_jour),]
##                db = GestionDB.DB()
##                db.ReqMAJ("divers", listeDonnees, "IDdivers", 1)
##                db.Close()
                
        # Mémorisation du paramètre de la taille d'écran
        if self.IsMaximized() == True :
            taille_fenetre = (0, 0)
        else:
            taille_fenetre = tuple(self.GetSize())
        self.userConfig["taille_fenetre"] = taille_fenetre
        
        # Sauvegarde du fichier de configuration
        self.SaveFichierConfig(nomFichier=self.nomFichierConfig)
        
        # Vidage du répertoire Temp
        if videRepertoiresTemp == True :
            FonctionsPerso.VideRepertoireTemp()
        
        # Vidage du répertoire Updates
        FonctionsPerso.VideRepertoireUpdates()

    def On_fichier_Convertir_reseau(self, event):
##        if self.dictUtilisateur["profil"] != "administrateur" :
##            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement avoir un profil Administrateur\npour accéder aux fonctions de conversion de fichier !", u"Accès non autorisé", wx.OK | wx.ICON_ERROR)
##            dlg.ShowModal()
##            dlg.Destroy()
##            return
        nomFichier = self.userConfig["nomFichier"]
        import UTILS_Conversion_fichier
        resultat = UTILS_Conversion_fichier.ConversionLocalReseau(self, nomFichier)
        print "Succes de la procedure : ", resultat

    def On_fichier_Convertir_local(self, event):
##        if self.dictUtilisateur["profil"] != "administrateur" :
##            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement avoir un profil Administrateur\npour accéder aux fonctions de conversion de fichier !", u"Accès non autorisé", wx.OK | wx.ICON_ERROR)
##            dlg.ShowModal()
##            dlg.Destroy()
##            return
        nomFichier = self.userConfig["nomFichier"]
        import UTILS_Conversion_fichier
        resultat = UTILS_Conversion_fichier.ConversionReseauLocal(self, nomFichier)
        print "Succes de la procedure : ", resultat

        
    def MenuNouveau(self, event):
        """ Créé une nouvelle base de données """
        import DATA_Tables as Tables
        
        # Demande le nom du fichier
        import Saisie_nouveau_fichier
        dlg = Saisie_nouveau_fichier.MyDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            nomFichier = dlg.GetNomFichier()
            listeTables = dlg.GetListeTables()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        
        # Affiche d'une fenêtre d'attente
        message = u"Création du nouveau fichier en cours... Veuillez patientez..."
        dlgAttente = PBI.PyBusyInfo(message, parent=None, title=u"Création d'un fichier", icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 
            
        if "[RESEAU]" in nomFichier :
            self.SetStatusText(u"Création du fichier '%s' en cours..." % nomFichier[nomFichier.index("[RESEAU]"):])
        else:
            self.SetStatusText(u"Création du fichier '%s' en cours..." % nomFichier)
        
        # Vérification de validité du fichier
        if nomFichier == "" :
            del dlgAttente
            dlg = wx.MessageDialog(self, u"Le nom que vous avez saisi n'est pas valide !", "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
            self.SetStatusText(u"Echec de la création du fichier '%s' : nom du fichier non valide." % nomFichier)
            return False

        if "[RESEAU]" not in nomFichier :
            # Version LOCAL
            
            # Vérifie si un fichier ne porte pas déjà ce nom :
            fichier = "Data/" + nomFichier + "_TDATA.dat"
            test = os.path.isfile(fichier) 
            if test == True :
                del dlgAttente
                dlg = wx.MessageDialog(self, u"Vous possédez déjà un fichier qui porte le nom '" + nomFichier + u"'.\n\nVeuillez saisir un autre nom.", "Erreur", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.SetStatusText(u"Echec de la création du fichier '%s' : Le nom existe déjà." % nomFichier)
                return False
        
        else:
            # Version RESEAU
            dictResultats = GestionDB.TestConnexionMySQL(typeTest="fichier", nomFichier=u"%s_TDATA" % nomFichier)
            
            # Vérifie la connexion au réseau
            if dictResultats["connexion"][0] == False :
                erreur = dictResultats["connexion"][1]
                dlg = wx.MessageDialog(self, u"La connexion au réseau MySQL est impossible. \n\nErreur : %s" % erreur, u"Erreur de connexion", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                del dlgAttente
                return False
            
            # Vérifie que le fichier n'est pas déjà utilisé
            if dictResultats["fichier"][0] == True :
                dlg = wx.MessageDialog(self, u"Le fichier existe déjà.", u"Erreur de création de fichier", wx.OK | wx.ICON_ERROR)
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
            dlg = wx.MessageDialog(self, u"Erreur dans la création du fichier de données.\n\nErreur : %s" % erreur, u"Erreur de création de fichier", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.userConfig["nomFichier"] = ancienFichier 
            return False
        self.SetStatusText(u"Création des tables de données...")
        DB.CreationTables(Tables.DB_DATA, fenetreParente=self)
        self.SetStatusText(u"Importation des données par défaut...")
        DB.Importation_valeurs_defaut(listeTables)
        DB.Close()
        
        # Création de la base PHOTOS
        DB = GestionDB.DB(suffixe="PHOTOS", modeCreation=True)
        if DB.echec == 1 :
            del dlgAttente
            erreur = DB.erreur
            dlg = wx.MessageDialog(self, u"Erreur dans la création du fichier de photos.\n\nErreur : %s" % erreur, u"Erreur de création de fichier", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.userConfig["nomFichier"] = ancienFichier 
            return False
        self.SetStatusText(u"Création de la table de données des photos...")
        DB.CreationTables(Tables.DB_PHOTOS)
        DB.Close()
        
        # Création de la base DOCUMENTS
        DB = GestionDB.DB(suffixe="DOCUMENTS", modeCreation=True)
        if DB.echec == 1 :
            del dlgAttente
            erreur = DB.erreur
            dlg = wx.MessageDialog(self, u"Erreur dans la création du fichier de documents.\n\nErreur : %s" % erreur, u"Erreur de création de fichier", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.userConfig["nomFichier"] = ancienFichier 
            return False
        self.SetStatusText(u"Création de la table de données des documents...")
        DB.CreationTables(Tables.DB_DOCUMENTS)
        DB.Close()
        
##        # Vérification de validité du fichier
##        if nomFichier == "" :
##            dlg = wx.MessageDialog(self, u"Le nom que vous avez saisi n'est pas valide !", "Erreur", wx.OK | wx.ICON_ERROR)
##            dlg.ShowModal()
##            dlg.Destroy()
##            if "[RESEAU]" in nomFichier :
##                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
##            self.SetStatusText(u"Echec de la création du fichier '%s' : nom du fichier non valide." % nomFichier)
##            return False
##        
##        if "[RESEAU]" not in nomFichier :
##            # Version LOCAL
##            
##            # Vérifie si un fichier ne porte pas déjà ce nom :
##            fichier = "Data/" + nomFichier + "_DATA.dat"
##            test = os.path.isfile(fichier) 
##            if test == True :
##                dlg = wx.MessageDialog(self, u"Vous possédez déjà un fichier qui porte le nom '" + nomFichier + u"'.\n\nVeuillez saisir un autre nom.", "Erreur", wx.OK | wx.ICON_ERROR)
##                dlg.ShowModal()
##                dlg.Destroy()
##                self.SetStatusText(u"Echec de la création du fichier '%s' : Le nom existe déjà." % nomFichier)
##                return False
##        
##        else:
##            # Version RESEAU
##            dictResultats = GestionDB.TestConnexionMySQL(typeTest="fichier", nomFichier=nomFichier)
##            
##            # Vérifie la connexion au réseau
##            if dictResultats["connexion"][0] == False :
##                erreur = dictResultats["connexion"][1]
##                dlg = wx.MessageDialog(self, u"La connexion au réseau MySQL est impossible. \n\nErreur : %s" % erreur, u"Erreur de connexion", wx.OK | wx.ICON_ERROR)
##                dlg.ShowModal()
##                dlg.Destroy()
##                return False
##            
##            # Vérifie que le fichier n'est pas déjà utilisé
##            if dictResultats["fichier"][0] == True :
##                dlg = wx.MessageDialog(self, u"Le fichier existe déjà.", u"Erreur de création de fichier", wx.OK | wx.ICON_ERROR)
##                dlg.ShowModal()
##                dlg.Destroy()
##                return False
##        
##        # Création de la base de données
##        ancienFichier = self.userConfig["nomFichier"]
##        self.userConfig["nomFichier"] = nomFichier 
##        db = GestionDB.DB(modeCreation=True)
##        if db.echec == 1 :
##            erreur = db.erreur
##            dlg = wx.MessageDialog(self, u"Erreur dans la création du fichier.\n\nErreur : %s" % erreur, u"Erreur de création de fichier", wx.OK | wx.ICON_ERROR)
##            dlg.ShowModal()
##            dlg.Destroy()
##            self.userConfig["nomFichier"] = ancienFichier 
##            return False
##        
##        db.CreationTables()
##        db.Importation_valeurs_defaut(listeTables)
        
##        # Obtient la version de la DB de l'application
##        versionDBApplication = self.GetVersionDBApplication()
        
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
        save_elements = Config_Sauvegarde.GetListeSourcesStr()
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
        self.menubar.EnableTop(1, True)
        self.menubar.EnableTop(2, True)

        # Désactive le menu Conversion Réseau s'il s'agit déjà d'un fichier réseau
        menuBar = self.GetMenuBar()
        if "[RESEAU]" in nomFichier :
            menuBar.FindItemById(107).Enable(False)
            menuBar.FindItemById(108).Enable(True)
        else:
            menuBar.FindItemById(107).Enable(True)
            menuBar.FindItemById(108).Enable(False)

        # Sauvegarde du fichier de configuration
        self.SaveFichierConfig(nomFichier=self.nomFichierConfig)
        
        # Boîte de dialogue pour confirmer la création
        if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
        
        del dlgAttente
        
        dlg = wx.MessageDialog(self, u"Le fichier '" + nomFichier + u"' a été créé avec succès.", u"Création d'un fichier", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
        self.SetStatusText(u"Le fichier '%s' a été créé avec succès." % nomFichier)
        
        # Rappel de la nécessité de créer des utilisateurs réseau
        if "[RESEAU]" in nomFichier :
            dlg = wx.MessageDialog(self, u"Pour l'instant, vous êtes le seul, en tant qu'administrateur, à pouvoir accéder à ce fichier. Vous devez donc créer des utilisateurs réseau ou accorder des autorisations d'accès aux utilisateurs déjà enregistrés.\n\nPour gérer les comptes utilisateurs réseau, rendez-vous sur le panneau 'Configuration' puis sur la page 'Utilisateurs réseau'.", "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()


    def MenuOuvrir(self, event):
        """ Ouvrir un fichier présent dur le disque dur """    
        # Boîte de dialogue pour demander le nom du fichier à ouvrir
        import DLG_Ouvrir_fichier
        dlg = DLG_Ouvrir_fichier.MyDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            nomFichier = dlg.GetNomFichier()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        # Ouverture du fichier
        self.OuvrirFichier(nomFichier)
    
    def OuvrirDernierFichier(self):
        # Chargement du dernier fichier chargé si assistant non affiché
        if self.userConfig.has_key("assistant_demarrage") :
            nePasAfficherAssistant = self.userConfig["assistant_demarrage"]
            if nePasAfficherAssistant == True :
                if self.nomDernierFichier != "" :
                    self.OuvrirFichier(self.nomDernierFichier)
    
    def OuvrirFichier(self, nomFichier):
        """ Suite de la commande menu Ouvrir """
        self.SetStatusText(u"Ouverture d'un fichier en cours...")
        
##        if "[RESEAU]" in nomFichier :
##            pos = nomFichier.index("[RESEAU]")
##            isNetwork = True
##            fichierComplet = nomFichier
##            paramConnexions = nomFichier[:pos]
##            nomFichier = nomFichier[pos:]
##        else:
##            isNetwork = False
        
        # Vérifie que le fichier n'est pas déjà ouvert
        if self.userConfig["nomFichier"] == nomFichier :
            if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
            dlg = wx.MessageDialog(self, u"Le fichier '" + nomFichier + u"' est déjà ouvert !", u"Ouverture de fichier", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.SetStatusText(u"Le fichier '%s' est déjà ouvert." % nomFichier)
            return False

        # Teste l'existence du fichier :
        if self.TesterUnFichier(nomFichier) == False :
            if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
            self.SetStatusText(u"Impossible d'ouvrir le fichier '%s'." % nomFichier)
            return False
        
                
        # Vérification du mot de passe
        if nomFichier != "" :
            if self.Verif_Password(nomFichier) == False :
                if "[RESEAU]" in nomFichier :
                    nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
                self.SetStatusText(u"Echec de l'ouverture du fichier '%s' : Mot de passe incorrect." % nomFichier)
                return False
        
        # Vérifie si la version du fichier est à jour
        if nomFichier != "" :
            if self.ValidationVersionFichier(nomFichier) == False :
                if "[RESEAU]" in nomFichier :
                    nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
                self.SetStatusText(u"Echec de l'ouverture du fichier '%s'." % nomFichier)
                return False

        # Applique le changement de fichier en cours
        self.userConfig["nomFichier"] = nomFichier

        # Remplissage de la table DIVERS pour la date de dernière ouverture
        if nomFichier != "" :
            date_jour =  str(datetime.date.today())  
            listeDonnees = [("date_derniere_ouverture",  date_jour),]
            db = GestionDB.DB()
            db.ReqMAJ("divers", listeDonnees, "IDdivers", 1)
            db.Close()

        # Vérifie que le répertoire de destination de sauvegarde auto existe vraiment
        if nomFichier != "" :
            self.VerifDestinationSaveAuto()

        # Met à jour l'affichage 
        self.MAJAffichage()
        self.SetTitleFrame(nomFichier=nomFichier)

        # Met à jour la liste des derniers fichiers ouverts dans le CONFIG de la page
        self.MAJlisteDerniersFichiers(nomFichier) 
        
        # Met à jour le menu
        self.MAJmenuDerniersFichiers()
        
        # Désactive le menu Conversion Réseau s'il s'agit déjà d'un fichier réseau
        menuBar = self.GetMenuBar()
        if "[RESEAU]" in nomFichier :
            menuBar.FindItemById(107).Enable(False)
            menuBar.FindItemById(108).Enable(True)
        else:
            menuBar.FindItemById(107).Enable(True)
            menuBar.FindItemById(108).Enable(False)

        # Sauvegarde du fichier de configuration
        self.SaveFichierConfig(nomFichier=self.nomFichierConfig)
        
        # Active les items du toolbook et sélectionne la page accueil
        self.toolBook.ActiveToolBook(True)
        self.menubar.EnableTop(1, True)
        self.menubar.EnableTop(2, True)

        # Confirmation de succès
        if "[RESEAU]" in nomFichier :
                nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
        self.SetStatusText(u"Le fichier '%s' a été ouvert avec succès." % nomFichier)       
        
        
    def VerifDestinationSaveAuto(self):
        """ Vérifie que le répertoire de destination existe vraiment """
        try :
            DB = GestionDB.DB()
            req = "SELECT save_destination FROM divers WHERE IDdivers=1;"
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) != 0 :
                save_destination_defaut = listeDonnees[0][0]
                test = os.path.isdir(save_destination_defaut) 
                if test == False :
                    standardPath = wx.StandardPaths.Get()
                    save_destination = standardPath.GetDocumentsDir()
                    save_destination =  save_destination.replace("\\", "/")
                    listeDonnees = [("save_destination",  save_destination),]
                    DB.ReqMAJ("divers", listeDonnees, "IDdivers", 1)
            DB.Close()
        except :
            print "pb dans la fonction verifDestinationSaveAuto de teamworks.py"

    def MenuFermer(self, event) :
        """ Fermer le fichier ouvert """
        # Vérifie qu'un fichier est chargé
        if self.userConfig["nomFichier"] == "" :
            dlg = wx.MessageDialog(self, u"Il n'y a aucun fichier à fermer !", u"Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # change le nom de fichier
        self.userConfig["nomFichier"] = ""
        self.SetTitleFrame()
        # Désactive les items du toolbook et sélectionne la page accueil
        self.toolBook.ActiveToolBook(False)
        # Désactive certains menus
        self.menubar.EnableTop(1, False)
        self.menubar.EnableTop(2, False)
        menuBar = self.GetMenuBar()
        menuItem = menuBar.FindItemById(107)
        menuItem.Enable(False)
        menuItem = menuBar.FindItemById(108)
        menuItem.Enable(False)
        
    def MenuSauvegarder(self, event):
        """ Sauvegarder occasionnelle """
        import DLG_Sauvegarde
        dlg = DLG_Sauvegarde.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        # Version TW1
##        frameSave = Config_Sauvegarde.Saisie_sauvegarde_occasionnelle(self)
##        frameSave.Show()
        
    def MenuRestaurer(self, event):
        """ Restaurer une sauvegarde """
        import DLG_Restauration
        fichier = DLG_Restauration.SelectionFichier()
        if fichier != None :
            if fichier.endswith(".twz") == True :
                # Version TW1
                frameResto = Config_Sauvegarde.Restauration(self, fichier)
                frameResto.Show()
            else:
                # Version TW2
                dlg = DLG_Restauration.Dialog(self, fichier=fichier)
                dlg.ShowModal() 
                dlg.Destroy()

        
        # Version TW1 :
##        # Demande l'emplacement du fichier
##        wildcard = "Sauvegarde TWorks (*.twz)|*.twz"
##        dlg = wx.FileDialog(self, message=u"Veuillez sélectionner le fichier de sauvegarde à restaurer", defaultDir=os.getcwd(), defaultFile="", wildcard=wildcard, style=wx.OPEN)
##        if dlg.ShowModal() == wx.ID_OK:
##            fichier = dlg.GetPath()
##        else:
##            return
##        dlg.Destroy()
##        
##        # Vérifie la validité du fichier sélectionné
##        if fichier.endswith(".twz") == False :
##            dlg = wx.MessageDialog(self, u"Le fichier n'est pas valide.", "Erreur", wx.OK| wx.ICON_ERROR)  
##            dlg.ShowModal()
##            dlg.Destroy()
##            return
##        
##        # Lance la restauration
##        frameResto = Config_Sauvegarde.Restauration(self, fichier)
##        frameResto.Show()
         
    def MenuDerniersFichiers(self, event):
        """ Ouvre un des derniers fichiers ouverts """
        idMenu = event.GetId()
        nomFichier = self.userConfig["derniersFichiers"][idMenu - 150]
        self.OuvrirFichier(nomFichier)
        
    def MAJmenuDerniersFichiers(self):
        """ Met à jour la liste des derniers fichiers dans le menu """
        # Met à jour la liste des derniers fichiers dans la BARRE DES MENUS
        menuBar = self.GetMenuBar()
        menuItem = menuBar.FindItemById(106)
        # Suppression de la liste existante
        menu = menuItem.GetMenu()
        for index in range(150, 160) :
            item = menuBar.FindItemById(index)
            if item == None : 
                break
            else:
                menu.RemoveItem(menuBar.FindItemById(index)) 
                self.Disconnect(index, -1, 10014) # Annule le Bind
        
        # Ré-intégration des derniers fichiers ouverts :
        listeDerniersFichiers = self.userConfig["derniersFichiers"]
        if len(listeDerniersFichiers) > 0 : 
            index = 0
            for nomFichier in listeDerniersFichiers :
                # Version Reseau
                if "[RESEAU]" in nomFichier :
                    nomFichier = nomFichier[nomFichier.index("[RESEAU]"):]
                item = wx.MenuItem(menu, 150 + index, str(index+1) + ". " + nomFichier, u"Ouvrir le fichier : " + nomFichier)
                menu.AppendItem(item)
                index += 1
            self.Bind(wx.EVT_MENU_RANGE, self.MenuDerniersFichiers, id=150, id2=150 + index)
        
        
    def MAJlisteDerniersFichiers(self, nomFichier) :
        """ MAJ la liste des derniers fichiers ouverts dans le config et la barre des menus """
        
        # MAJ de la liste des derniers fichiers ouverts :
        listeFichiers = self.userConfig["derniersFichiers"]
        nbreFichiersMax = 3 # Valeur à changer en fonction des souhaits
        
        # Si le nom est déjà dans la liste, on le supprime :
        if nomFichier in listeFichiers : listeFichiers.remove(nomFichier)
           
        # On ajoute le nom du fichier en premier dans la liste :
        listeFichiers.insert(0, nomFichier)
        listeFichiers = listeFichiers[:nbreFichiersMax]
        
        # On enregistre dans le Config :
        self.userConfig["derniersFichiers"] = listeFichiers
        
        
    def TesterUnFichier(self, nomFichier):
        """ Fonction pour tester l'existence d'un fichier """
        if "[RESEAU]" in nomFichier :
            # Version RESEAU
            pos = nomFichier.index("[RESEAU]")
            paramConnexions = nomFichier[:pos]
            port, host, user, passwd = paramConnexions.split(";")
            nomFichierCourt = nomFichier[pos:].replace("[RESEAU]", "")
            nomFichierCourt = nomFichierCourt.lower() 
            
            # Si c'est une nouvelle version de fichier
            serveurValide = True
            fichierValide = True
            dictResultats = GestionDB.TestConnexionMySQL(typeTest='fichier', nomFichier=u"%s_tdata" % nomFichier)
            
            if dictResultats["connexion"][0] == False :
                serveurValide = False
            else :
                if dictResultats["fichier"][0] == False :
                    fichierValide = False

            if serveurValide == True and fichierValide == True : 
                return True
            
            # Si c'est une ancienne version de fichier
            dictResultats = GestionDB.TestConnexionMySQL(typeTest='fichier', nomFichier=nomFichier)
            if dictResultats["connexion"][0] == True and dictResultats["fichier"][0] == True :
                # Création de la nouvelle base
                self.SetStatusText(u"Conversion pour Teamworks 2 : Création de la nouvelle base...")
                DB = GestionDB.DB(nomFichier=nomFichier, modeCreation=True)
                DB.Close() 
                
                # Importation des anciennes tables de données
                DB = GestionDB.DB(suffixe="", nomFichier=nomFichier)
                listeTables = DB.GetListeTables()
                for (nomTable,) in listeTables :
                    self.SetStatusText(u"Conversion pour Teamworks 2 : Transfert de la table %s...." % nomTable)
                    req = "RENAME TABLE %s.%s TO %s_tdata.%s;" % (nomFichierCourt, nomTable, nomFichierCourt, nomTable)
                    DB.ExecuterReq(req)
                DB.Commit()
                DB.Close() 

                # Suppression de l'ancienne table
                self.SetStatusText(u"Conversion pour Teamworks 2 : Suppression de l'ancienne base...")
                DB = GestionDB.DB(nomFichier=nomFichier)
                req = "DROP DATABASE %s;" % nomFichierCourt
                DB.ExecuterReq(req)
                DB.Close() 
                
                return True
            
            if serveurValide == False :
                # Connexion impossible au serveur MySQL
                erreur = dictResultats["connexion"][1]
                dlg = wx.MessageDialog(self, u"Il est impossible de se connecter au serveur MySQL.\n\nErreur : %s" % erreur, "Erreur d'ouverture de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
            if fichierValide == False :
                # Ouverture impossible du fichier MySQL demandé
                erreur = dictResultats["fichier"][1]
                dlg = wx.MessageDialog(self, u"La connexion avec le serveur MySQL fonctionne mais il est impossible d'ouvrir le fichier MySQL demandé.\n\nErreur : %s" % erreur, "Erreur d'ouverture de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            
            return True
        
        # SQLITE
        else:
            # Test de validité du fichier SQLITE :
            valide = False
            if os.path.isfile(u"Data/%s_TDATA.dat" % nomFichier)  :
                valide = True
            else :
                cheminFichier = u"Data/%s.twk" % nomFichier
                if os.path.isfile(cheminFichier) :
                    valide = True
                    # Si c'est une version TW1 : Renommage du fichier DATA pour TW2
                    os.rename(cheminFichier, u"Data/%s_TDATA.dat" % nomFichier)
            
            if valide == False :
                dlg = wx.MessageDialog(self, u"Il est impossible d'ouvrir le fichier demandé !", "Erreur d'ouverture de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            else:
                return True

##    def GetVersionDBApplication(self):
##        # Obtient le numéro de version de la db du logiciel
##        versionApplication = VERSION_APPLICATION
##        tmp = versionApplication.split(".")
##        versionDBApplication = int(tmp[2])
##        return versionDBApplication

    def ConvertVersionTuple(self, texteVersion=""):
        """ Convertit un numéro de version texte en tuple """
        tupleTemp = []
        for num in texteVersion.split(".") :
            tupleTemp.append(int(num))
        return tuple(tupleTemp)

##    def ValidationVersionFichier(self, nomFichier):
##        """ Vérifie que la version du fichier est à jour avec le logiciel """
##        # Obtient le numéro de version de la db du logiciel
##        versionApplication = self.GetVersionDBApplication()
##        
##        # Obtient le numéro de version du fichier
##        DB = GestionDB.DB(nomFichier = nomFichier)        
##        req = "SELECT version_DB FROM divers WHERE IDdivers=1;"
##        DB.ExecuterReq(req)
##        versionFichier = DB.ResultatReq()[0][0]
##        DB.Close()
##
##        # Compare les deux versions
##        if versionFichier < versionApplication :
##            print "conversion de fichier necessaire."
##            # Fait la conversion à la nouvelle version
##            DB = GestionDB.DB(nomFichier = nomFichier)        
##            nouvelleVersionDB = DB.ConversionDB(versionDB_fichier=versionFichier)
##            DB.Close()
##            print "nouvelleVersionDB=", nouvelleVersionDB
##            if type(nouvelleVersionDB) == str :
##                dlg = wx.MessageDialog(self, u"Le logiciel n'arrive pas à convertir le fichier '" + nomFichier + u":\n\nErreur : " + nouvelleVersionDB + u"\n\nVeuillez contacter le développeur du logiciel...", u"Erreur de conversion de fichier", wx.OK | wx.ICON_ERROR)
##                dlg.ShowModal()
##                dlg.Destroy()
##                return False
##            else:
##                print "conversion reussie."
##                return True

    def ValidationVersionFichier(self, nomFichier):
        """ Vérifie que la version du fichier est à jour avec le logiciel """
        # Récupère le numéro de version du logiciel
        versionLogiciel = self.ConvertVersionTuple(VERSION_APPLICATION)
        
        # Récupère le numéro de version du fichier
        if UTILS_Parametres.TestParametre(categorie="fichier", nom="version", nomFichier=nomFichier) == True :
            versionFichier = self.ConvertVersionTuple(UTILS_Parametres.Parametres(mode="get", categorie="fichier", nom="version", valeur=VERSION_APPLICATION, nomFichier=nomFichier))
        else:
            # Pour compatibilité avec version 1 de Teamworks
            versionFichier = (1, 0, 5, 2)
        
        # Compare les deux versions
        if versionFichier < versionLogiciel :
            # Fait la conversion à la nouvelle version
            info = "Lancement de la conversion %s -> %s..." %(".".join([str(x) for x in versionFichier]), ".".join([str(x) for x in versionLogiciel]))
            self.SetStatusText(info)
            print info
            
            # Affiche d'une fenêtre d'attente
            message = u"Mise à jour de la base de données en cours... Veuillez patientez..."
            dlgAttente = PBI.PyBusyInfo(message, parent=None, title=u"Mise à jour", icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
            wx.Yield() 
            
            DB = GestionDB.DB(nomFichier = nomFichier)        
            resultat = DB.ConversionDB(versionFichier)
            DB.Close()
            
            # Fermeture de la fenêtre d'attente
            del dlgAttente
            
            if resultat != True :
                print resultat
                dlg = wx.MessageDialog(self, u"Le logiciel n'arrive pas à convertir le fichier '" + nomFichier + u":\n\nErreur : " + resultat + u"\n\nVeuillez contacter le développeur du logiciel...", u"Erreur de conversion de fichier", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            # Mémorisation de la version actuelle du fichier
            UTILS_Parametres.Parametres(mode="set", categorie="fichier", nom="version", valeur=".".join([str(x) for x in versionLogiciel]), nomFichier=nomFichier)
            info = "Conversion %s -> %s reussie." %(".".join([str(x) for x in versionFichier]), ".".join([str(x) for x in versionLogiciel]))
            self.SetStatusText(info)
            print info
            
        return True

    def MenuQuitter(self, event):
        self.Quitter()
        self.Destroy()
        event.Skip()


    def MenuAide(self, event):
        """ Affiche l'aide complète """
        FonctionsPerso.Aide()

    def MenuForum(self, event):
        """ Ouvre le forum TeamWorks """
        FonctionsPerso.LanceFichierExterne(ADRESSE_FORUM)
        
    def MenuMailAuteur(self, event):
        """ Envoyer un mail à l'auteur avec le client de messagerie par défaut """
        FonctionsPerso.EnvoyerMail(adresses = (MAIL_AUTEUR,))
        
    def MenuExportOutlook(self ,event):
        
        # Vérifie qu'un fichier est chargé
        if self.userConfig["nomFichier"] == "" :
            dlg = wx.MessageDialog(self, u"Vous n'avez chargé aucun fichier.", u"Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
    
        import Export_outlook
        outlook = Export_outlook.LibOutlook()
        # Recherche si Outlook peut être ouvert
        dlg = wx.MessageDialog(self, u"Un test va être effectué pour vérifier que Outlook est bien accessible sur votre ordinateur.\n\nSi c'est bien le cas, Outlook va vous demander si vous acceptez que cet accès ait bien lieu.\n\nCochez la case 'Autoriser l'accès' et sélectionnez un temps de 10 minutes...", u"Information", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
            
        if outlook.echec == True :
            # Pas de outlook accessible :
            dlg = wx.MessageDialog(self, u"Microsoft Outlook ne peut pas être ouvert...", u"Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if outlook.Test() == False :
            # Outlook est verrouillé:
            dlg = wx.MessageDialog(self, u"Microsoft Outlook ne peut pas être ouvert.\nIl semble verrouillé...", u"Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Ouverture de la frame exportation
        frameExport = Export_outlook.MyFrame(None)
        frameExport.Show()

    def MenuGadgets(self, event):
        """ Configuration des gadgets de la page d'accueil """
        
        # Vérifie qu'un fichier est chargé
        if self.userConfig["nomFichier"] == "" :
            dlg = wx.MessageDialog(self, u"Vous n'avez chargé aucun fichier.", u"Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        import Config_Gadgets
        frame_config = Config_Gadgets.MyFrame(None)
        frame_config.Show()

        

    def MenuUpdater(self, event):
        """Mises à jour internet """
##        import Updater
##        frameUpdater = Updater.MyFrame(self)
##        frameUpdater.Show()
        import DLG_Updater
        dlg = DLG_Updater.Dialog(self)
        dlg.ShowModal() 
        installation = dlg.GetEtat() 
        dlg.Destroy()
        if installation == True :
            self.Quitter(videRepertoiresTemp=False)
            self.Destroy()
        
    def MenuEnvoiMailGroupe(self, event):
        """ Envoi d'un mail groupé """
        import Envoi_email_groupe
        dlg = Envoi_email_groupe.MyDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            listeAdresses = dlg.GetAdresses()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        # Création du mail
        FonctionsPerso.EnvoyerMail(adresses=listeAdresses)

    def MenuGestionFrais(self, event):
        """ Gestion globale des frais de déplacements """
        import Gestion_frais
        frm = Gestion_frais.MyFrame(self)
        frm.Show()
        
    def MenuImprimerPhotos(self, event):
        """ Imprimer les photos des personnes """
        # Ouverture de la frame d'impression des photos  
        import Impression_photo
        frame = Impression_photo.FrameSelectionPersonnes(None)
        frame.Show()

    def MenuPublipostage(self, event):
        """ Imprimer par publipostage """
        import Publiposteur_Choix
        frame = Publiposteur_Choix.MyFrame(None)
        frame.Show()

    def MenuTeamword(self, event):
        """ Lancer Teamword """
        import Teamword
        frame = Teamword.MyFrame(None)
        frame.Show()
        
    def MenuVersions(self, event):
        """ A propos : Notes de versions """
        import  wx.lib.dialogs
        txtLicence = open("Versions.txt", "r")
        msg = txtLicence.read()
        txtLicence.close()
        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg.decode("iso-8859-15"), u"Notes de versions", size=(420, 400))
        dlg.ShowModal()
        
    def MenuLicence(self, event):
        """ A propos : Licence """
        import  wx.lib.dialogs
        txtLicence = open("Licence.txt", "r")
        msg = txtLicence.read()
        txtLicence.close()
        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, msg.decode("iso-8859-15"), u"A propos", size=(420, 400))
        dlg.ShowModal()

    def MenuApropos(self, event):
        """ A propos : A propos """
        texte = u"""
"TeamWorks - Gestion d'équipes"
Logiciel de gestion d'équipes pour les centres de loisirs et de vacances.
Copyright © 2008-2015 Ivan LUCAS

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
    
    def MenuDons(self, event):
        FonctionsPerso.LanceFichierExterne(u"http://teamworks.forumactif.com/faire-un-don-de-soutien-f2/pourquoi-et-comment-faire-un-don-de-soutien-t129.htm")
    
    def MenuTelechargerGuide(self, event):
        FonctionsPerso.LanceFichierExterne(u"http://www.clsh-lannilis.com/teamworks/aide/guide-utilisateur-tw.pdf")
        
    def MenuAssistantDemarrage(self, event):
        self.Assistant_demarrage(mode="menu")
        
    def MAJAffichage(self):
        # Mise à jour des panels :
        self.toolBook.GetPage(0).MAJpanel() 
##        self.toolBook.GetPage(1).MAJpanel() 
##        self.toolBook.GetPage(2).MAJpanel()
##        self.toolBook.GetPage(3).MAJpanel()

    
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
                fichierVersions = urllib.urlopen('http://www.clsh-lannilis.com/teamworks/debian/Versions.txt')
            else:
                # Version Windows
                fichierVersions = urllib.urlopen('http://www.clsh-lannilis.com/teamworks/Versions.txt')
            texteNouveautes= fichierVersions.read()
            fichierVersions.close()
            pos_debut_numVersion = texteNouveautes.find("n")
            if "(" in texteNouveautes[:50] :
                pos_fin_numVersion = texteNouveautes.find("(")
            else:
                pos_fin_numVersion = texteNouveautes.find(":")
            versionMaj = texteNouveautes[pos_debut_numVersion+1:pos_fin_numVersion].strip()
        except :
            print "Pb dans la recuperation du num de version de la MAJ sur internet"
            versionMaj = "0.0.0.0"
        # Compare les deux versions et renvois le résultat
        resultat = FonctionsPerso.CompareVersions(versionApp=versionApplication, versionMaj=versionMaj)
        return resultat

    def GetVersionAnnonce(self):
        if self.userConfig.has_key("annonce") :
            versionAnnonce = self.userConfig["annonce"]
            if versionAnnonce != None :
                return versionAnnonce
        return (0, 0, 0, 0)

    def Annonce(self):
        """ Création une annonce au premier démarrage du logiciel """
        nomFichier = sys.executable
        if nomFichier.endswith("python.exe") == False :
            versionAnnonce = self.GetVersionAnnonce()
            versionLogiciel = self.ConvertVersionTuple(VERSION_APPLICATION)
            if versionAnnonce < versionLogiciel :
                import DLG_Message_accueil
                dlg = DLG_Message_accueil.Dialog(self)
                dlg.ShowModal()
                dlg.Destroy()
                # Mémorise le numéro de version actuel
                self.userConfig["annonce"] = versionLogiciel

    def Assistant_demarrage(self, mode="ouverture"):
        """ Charge l'assistant démarrage """
        # Récupère l'état du checkBox affichage
        if self.userConfig.has_key("assistant_demarrage") :
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
        import Assistant_demarrage
        dlg = Assistant_demarrage.MyFrame(None, checkAffichage=checkAffichage, afficherDernierFichier=afficherDernierFichier, nomDernierFichier=self.nomDernierFichier)
        dlg.ShowModal()
        choix = dlg.GetChoix()
        checkAffichage = dlg.GetCheckAffichage()
        dlg.Destroy()
        # Mémorise l'état du checkBox affichage
        self.userConfig["assistant_demarrage"] = checkAffichage
        # Charge la commande demandée
        if choix != None :
            if choix == 1 : FonctionsPerso.LanceFichierExterne(u"http://teamworks.forumactif.com/caracteristiques-f1/a-la-video-de-presentation-t121.htm")
            if choix == 2 : self.MenuNouveau(None)
            if choix == 3 : FonctionsPerso.LanceFichierExterne("http://teamworks.forumactif.com")
            if choix == 4 : self.MenuOuvrir(None)
            if choix == 5 : self.OuvrirFichier(nomFichier="Exemple")
            if choix == 6 : self.OuvrirFichier(nomFichier=self.nomDernierFichier)
        else :
            # Utiliser directement TW
            pass
            
        return True
    
    
    
    
    


class SaisiePassword(wx.Dialog):
    def __init__(self, parent, id=-1, title=u"Saisie du mot de passe", nomFichier=""):
        wx.Dialog.__init__(self, parent, id, title)

        self.sizer_3_staticbox = wx.StaticBox(self, -1, "")
        if "[RESEAU]" in nomFichier :
            nomFichierTmp = nomFichier[nomFichier.index("[RESEAU]"):]
        else:
            nomFichierTmp = nomFichier
        self.label_2 = wx.StaticText(self, -1, u"Le fichier '" + self.FormateNomFichier(nomFichierTmp) + u"' est protégé.")
        self.label_password = wx.StaticText(self, -1, "Mot de passe :")
        self.text_password = wx.TextCtrl(self, -1, "", size=(200, -1), style=wx.TE_PASSWORD)
        self.bouton_ok = wx.BitmapButton(self, wx.ID_OK, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
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
        self.text_password.SetToolTipString(u"Saisissez votre mot de passe ici")
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
        self.Centre()

    def GetPassword(self):
        return self.text_password.GetValue()


# ----------------------------------------------------------------------------------------------------------------------------------------------------------

class MyApp(wx.App):
    def OnInit(self):
        #wx.InitAllImageHandlers()
        heure_debut = time.time()
        wx.Locale(wx.LANGUAGE_FRENCH)

        # Vérifie l'existence des répertoires
        for rep in ("Aide", "Temp", "Updates", "Data", "Lang", "Documents/Editions") :
            if os.path.isdir(rep) == False :
                os.makedirs(rep)
                print "Creation du repertoire : ", rep

        # AdvancedSplashScreen
        bmp = wx.Bitmap("Images/Special/Logo_splash.png", wx.BITMAP_TYPE_PNG)
        frame = AS.AdvancedSplash(None, bitmap=bmp, timeout=1000, agwStyle=AS.AS_TIMEOUT | AS.AS_CENTER_ON_SCREEN)
        frame.Refresh()
        frame.Update()
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

        # Affiche le temps de démarrage de TW
        duree = time.time()-heure_debut
##        print "Temps de demarrage = %s secondes." % duree
        
        return True


        
        
        
if __name__ == "__main__":
    nomFichier = sys.executable
    if nomFichier.endswith("python.exe") :
        app = MyApp(redirect=False)
    else :
        app = MyApp(redirect=True, filename="journal.log")
    app.MainLoop()

    

