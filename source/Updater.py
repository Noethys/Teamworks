#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import FonctionsPerso
import sys 
from time import sleep 
from threading import Thread 
import urllib
import os
import wx.lib.hyperlink as hl
import zipfile
import glob


def AffichetailleFichier(fichierURL):
    try :
        fichier = urllib.URLopener().open(fichierURL)
        tailleFichier = (fichier.info().getheaders('Content-Length'))
        tailleFichier = tailleFichier[0]
    except IOError :
        tailleFichier = 0
    return tailleFichier

def AffichePourcentage(stade, taille):
    pourcent = int(stade*100/taille)
    pourcent = str(pourcent) + " %"
    return pourcent
    
def FormateTailleFichier(taille):
    if 0 <= taille <1000 :
        texte = str(taille) + " octets"
    elif 1000 <= taille < 1000000 :
        texte = str(taille/1000) + " Ko"
    else :
        texte = str(taille/1000000) + " Mo"
    return texte


    
##def zipdirectory(journal, filezip, pathzip):
##    """ Sauvegarde globale """
##    lenpathparent = len(pathzip)+1
##    
##    def _zipdirectory(zfile, path):
##        for i in glob.glob(path+'/*'):
##            if os.path.isdir(i): 
##                if i.endswith("Updates") == False : # On sauvegarde pas le dossier Updates
##                    _zipdirectory(zfile, i )
##            else:
##                nomFichier = os.path.split(i)[1]
##                journal.WriteText("..." + nomFichier + "\n")
##                zfile.write(i, i[lenpathparent:]) 
##    zfile = zipfile.ZipFile(filezip,'w',compression=zipfile.ZIP_DEFLATED)
##    _zipdirectory(zfile, pathzip)
##    zfile.close()
    


class zipdirectory(Thread):
    def __init__(self, parent, journal, filezip, pathzip):
        Thread.__init__(self)
        self.parent = parent
        self.journal = journal
        self.filezip = filezip
        self.pathzip = pathzip
        self.lenpathparent = len(pathzip)+1
        self.Terminated = False
        self.nbreFichiers = 0
        
    def run(self):
        def _zipdirectory(zfile, path):
            for i in glob.glob(path+'/*'):
                if os.path.isdir(i): 
                    if i.endswith("Updates") == False : # On sauvegarde pas le dossier Updates
                        _zipdirectory(zfile, i )
                else:
                    nomFichier = os.path.split(i)[1]
                    if "linux" not in sys.platform :
                        self.journal.WriteText("..." + nomFichier + "\n")
                    zfile.write(i, i[self.lenpathparent:]) 
                    self.nbreFichiers += 1
        
        zfile = zipfile.ZipFile(self.filezip,'w',compression=zipfile.ZIP_DEFLATED)
        _zipdirectory(zfile, self.pathzip)
        zfile.close()
        self.journal.WriteText(str(self.nbreFichiers) + u" fichiers ont �t� sauvegard�s avec succ�s.")
        
        # Lance la suite de l'installation
        self.parent._Installation()
        
    def stop(self):
        self.Terminated = True    
    



class Abort(Exception): 
    pass 

class Download(Thread): 

    def __init__(self, parent, fichierURL, fichierDest, progressBar, zoneTexte): 
        Thread.__init__(self) 
        self.parent = parent
        self.succes = False
        self.fichierURL = fichierURL 
        self.stop = False 
        self.fichierDest = fichierDest
        self.progressBar = progressBar
        self.zoneTexte = zoneTexte
        self.frameParente = self.parent.GetParent()
        print "Telechargement de la nouvelle version : etape 4"

    def _hook(self, nb_blocs, taille_bloc, taille_fichier):
        #print u"Telecharge=", nb_blocs*taille_bloc, u"/ total=", taille_fichier
        if nb_blocs*taille_bloc >= taille_fichier:
            #print "Le telechargement est termine !"
            self.succes = True
            self.zoneTexte.SetLabel(u"Le t�l�chargement est termin�. Veuillez patientez...")
            self.frameParente.SetTitle(u"Mises � jour Internet")
            raise Abort
        if self.stop: 
            raise Abort
        count = int(nb_blocs*taille_bloc)
        self.progressBar.SetValue(count+1)
        print "Telechargement de la nouvelle version : etape 6"
        if nb_blocs % 5 == 0 :
            if "linux" not in sys.platform :
                texteInfo = u"T�l�chargement en cours...  " + FormateTailleFichier(nb_blocs*taille_bloc)+" / "+FormateTailleFichier(taille_fichier)
                if texteInfo != self.zoneTexte.GetLabel() :
                    self.zoneTexte.SetLabel(texteInfo)
            self.frameParente.SetTitle(AffichePourcentage(nb_blocs*taille_bloc, taille_fichier) + u" | T�l�chargement d'une mise � jour")

    def run(self): 
        print "Telechargement de la nouvelle version : etape 5"
        try: 
            if "linux" in sys.platform :
                self.zoneTexte.SetLabel(u"T�l�chargement en cours...")
            urllib.urlretrieve(self.fichierURL, self.fichierDest, self._hook) 
        except Abort, KeyBoardInterrupt: 
            print 'Aborted ici !' 
            if self.succes == True :
                # T�l�chargement r�ussi
                self.parent.Suite(succes=True)
            else:
                # T�l�chargement non complet
                self.parent.Suite(succes=False)
        except: 
            self.stop = True 
            raise 

    def abort(self): 
        self.stop = True
        
        
        
        
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PAGE RECHERCHE DE MAJ INTERNET
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_recherche(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="page_recherche", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Cr�ation des widgets
        texteIntro = u"Cliquez sur le bouton 'Rechercher' pour lancer la recherche."
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        self.gauge = wx.Gauge(self, -1)
        
        # R�glages pour la gauge
        self.count = 0
        self.Bind(wx.EVT_TIMER, self.TimerHandler)
        self.timer = wx.Timer(self)
                
        # Boutons
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Rechercher.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)

    def __del__(self):
        self.timer.Stop()

    def TimerHandler(self, event):
        self.count = self.count + 1
        if self.count >= 50:
            self.count = 0
        self.gauge.Pulse()
        
    def __set_properties(self):
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString(u"Cliquez pour annuler et fermer")
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        

    def __do_layout(self):        
        # Sizer Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        # Sizer principal
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.label_introduction, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.gauge, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add((5, 5), 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)       
        self.SetSizer(grid_sizer_base)
        self.Layout()
        
    def Onbouton_aide(self, event):
        self.parent.Aide()
                    
    def Onbouton_annuler(self, event):
        self.parent.Fermer()
        
    def Onbouton_ok(self, event):
        self.Recherche()

    def Activation(self):
        if self.parent.afficher_page_recherche == False :
            self.Recherche()
        
    def GetVersionTeamworks(self):
        """ Recherche du num�ro de version de TW """
        fichierVersion = open("Versions.txt", "r")
        txtVersion = fichierVersion.readlines()[0]
        fichierVersion.close() 
        pos_debut_numVersion = txtVersion.find("n")
        if "(" in txtVersion[:50] :
            pos_fin_numVersion = txtVersion.find("(")
        else:
            pos_fin_numVersion = txtVersion.find(":")
        numVersion = txtVersion[pos_debut_numVersion+1:pos_fin_numVersion].strip()
        return numVersion

    def Recherche(self):
        """ Recherche internet """
        
        texteIntro = u"Recherche d'une mise � jour internet en cours..."
        self.label_introduction.SetLabel(texteIntro)
        
        # Active la gauge
        self.timer.Start(20)
        
        # Recherche si le fichier de versions est pr�sent sur internet
        try :
            if "linux" in sys.platform :
                # Version Debian
                fichierVersions = urllib.urlopen('http://www.clsh-lannilis.com/teamworks/debian/Versions.txt')
            else:
                # Version Windows
                fichierVersions = urllib.urlopen('http://www.clsh-lannilis.com/teamworks/Versions.txt')
            self.texteNouveautes= fichierVersions.read()
            fichierVersions.close()
        except :
            self.Suite(etat="erreur") 
            return
        
        # Recherche du num�ro de version
        pos_debut_numVersion = self.texteNouveautes.find("n")
        pos_fin_numVersion = self.texteNouveautes.find(":")
        if "(" in self.texteNouveautes[:50] :
            pos_fin_numVersion = self.texteNouveautes.find("(")
        else:
            pos_fin_numVersion = self.texteNouveautes.find(":")
        self.versionFichier = self.texteNouveautes[pos_debut_numVersion+1:pos_fin_numVersion].strip()

        print "Version MAJ disponible =", self.versionFichier
        
        # Si la mise � jour n'est pas n�cessaire :
        versionApplication = self.GetVersionTeamworks()
        print "versionApplication=", versionApplication
        
        if FonctionsPerso.CompareVersions(versionApp=versionApplication, versionMaj=self.versionFichier) == False :
            self.Suite(etat="aucune")
            return

        # Recherche la taille du fichier � t�l�charger
        taille = int(AffichetailleFichier(self.parent.fichierURL))
        self.tailleFichier = FormateTailleFichier(taille)
        self.parent.tailleFichier = taille
        if self.tailleFichier == 0 :
            self.Suite(etat="erreur")
        
        # Si le fichier est bien trouv�, on passe � la suite...
        self.Suite(etat="trouvee")
        
        
    def Suite(self, etat):
        """ Apr�s la recherche passe � la suite """
        # Recherche termin�e
        if etat == "erreur" :
            # Probl�me de recherche internet
            self.label_introduction.SetLabel(u"Connexion au serveur de mise � jour impossible.")
            self.timer.Stop()
            self.Layout()
        if etat == "aucune" :
            # Aucune mise � jour n'a �t� trouv�e
            self.label_introduction.SetLabel(u"Vous disposez d�j� de la derni�re version du logiciel.")
            self.timer.Stop()
            self.bouton_ok.Show(True)
            self.Layout()
        if etat == "trouvee" :
            # Une mise � jour a �t� trouv�e !
            self.parent.versionFichier = self.versionFichier
            self.parent.fichierDest = "Updates/" + self.parent.versionFichier
            if "win" in sys.platform : self.parent.fichierDest = self.parent.fichierDest.replace("/", "\\")
            # V�rifie qu'elle n'a pas d�j� �t� t�l�charg�e sur le disque dur
            fichierAverifier = self.parent.fichierDest+ "/" + self.parent.nomFichier
            if "win" in sys.platform : fichierAverifier = fichierAverifier.replace("/", "\\")
            if os.path.isfile(fichierAverifier) == True :
                tailleFichierAverifier = os.path.getsize(fichierAverifier)  
                tailleFichierOrigin = self.parent.tailleFichier
                if tailleFichierAverifier == tailleFichierOrigin :
                    # Ok le fichier existe bien d�j�
                    texteIntro1 = u"La mise � jour " + self.versionFichier + u" a d�j� �t� t�l�charg�e pr�c�demment."
                    self.parent.page_fin_telechargement.label_introduction1.SetLabel(texteIntro1)
                    self.parent.Active_page("page_fin_telechargement")
            else:
                # Sinon, on la t�l�charge...
                texteIntro1 = u"La version " + self.versionFichier + " de TeamWorks est disponible (" + self.tailleFichier + ")."
                self.parent.page_disponible.label_introduction1.SetLabel(texteIntro1)
                texteNouveautes = "> Historique des mises � jour :\n\n" + self.texteNouveautes
                self.parent.page_disponible.textCtrl_nouveautes.SetValue(texteNouveautes.decode("iso-8859-15"))
                self.parent.Active_page("page_disponible")
              

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PAGE MAJ DISPONIBLE
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_disponible(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="page_disponible", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Cr�ation des widgets
        texteIntro1 = ""
        self.label_introduction1 = FonctionsPerso.StaticWrapText(self, -1, texteIntro1)
        texteIntro2 = u"Souhaitez-vous la t�l�charger maintenant ?"
        self.label_introduction2 = FonctionsPerso.StaticWrapText(self, -1, texteIntro2)
        self.textCtrl_nouveautes = wx.TextCtrl(self, -1,"", size=(-1, 50), style=wx.TE_MULTILINE)
        
        # Boutons
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Telecharger_L95.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)

    def __set_properties(self):
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString(u"Cliquez pour annuler et fermer")
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        

    def __do_layout(self):        
        # Sizer Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        # Sizer principal
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.label_introduction1, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.label_introduction2, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.textCtrl_nouveautes, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)       
        self.SetSizer(grid_sizer_base)
        self.Layout()
        self.grid_sizer_base = grid_sizer_base
        
    def Onbouton_aide(self, event):
        self.parent.Aide()
                    
    def Onbouton_annuler(self, event):
        # Fermeture
        print "annuler"
        self.parent.Fermer()
        
    def Onbouton_ok(self, event):
        # T�l�charger
        self.parent.Active_page("page_telechargement")

    def Activation(self):
        # Pour contrer bug de Layout
        self.SetSize((500, 700))
        
        
        
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PAGE TELECHARGEMENT
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_telechargement(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="page_telechargement", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Cr�ation des widgets
        texteIntro = u"Le t�l�chargement va commencer dans quelques instants..."
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        self.gauge = wx.Gauge(self, -1)
        
        # Boutons
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Telecharger_L95.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok.Show(False)
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)

    def __set_properties(self):
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour lancer le t�l�chargement")
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString(u"Cliquez pour annuler et fermer")
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        

    def __do_layout(self):        
        # Sizer Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        # Sizer principal
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.label_introduction, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.gauge, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add((5, 5), 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)       
        self.SetSizer(grid_sizer_base)
        self.Layout()
        
    def Onbouton_aide(self, event):
        self.parent.Aide()
                    
    def Onbouton_annuler(self, event):
        self.Arreter_telechargement()
        
    def Onbouton_ok(self, event):
        self.Lancer_telechargement()

    def Activation(self):
        # Cr�e une petite attente avant le d�but du t�l�chargement
        self.count = 0
        self.Bind(wx.EVT_TIMER, self.TimerHandler)
        self.timer = wx.Timer(self)
        self.timer.Start(1)

    def __del__(self):
        self.timer.Stop()

    def TimerHandler(self, event):
        self.count = self.count + 1
        if self.count == 10 :
            self.timer.Stop()
            # Lance le t�l�chargement
            print "Telechargement de la nouvelle version : etape 1"
            self.Lancer_telechargement()
            
    def Suite(self, succes):
        """ Apr�s le t�l�chargement passe � la suite """
        # V�rifie que le fichier est bien entier :
        print "Telechargement de la nouvelle version : etape finale"
        tailleFichierDest = os.path.getsize(self.parent.fichierDest+ "/" + self.parent.nomFichier)  
        tailleFichierOrigin = self.parent.tailleFichier
        if tailleFichierDest != tailleFichierOrigin :
            succes = False
        
        # T�l�chargement termin�
        if succes == True :
            # Si t�l�chargement complet, on passe � la page de fin de t�l�chargement
            sleep(2) # Attend 2 secondes avant de continuer
            self.parent.Active_page("page_fin_telechargement")
        else:
            # Vidage du rep Updates
            FonctionsPerso.VideRepertoireUpdates(forcer=True)
            # Le t�l�chargement n'est pas complet, demande � l'utilisateur de recommencer
            self.label_introduction.SetLabel(u"Le t�l�chargement n'est pas complet. Voulez-vous recommencer ?")
            self.bouton_ok.Show(True)
            self.Layout()
        
    def Lancer_telechargement(self):
        """ Lance le thread de t�l�chargement """
        print "Telechargement de la nouvelle version : etape 2"
        # Cr�ation du r�pertoire de destination
        if os.path.isdir(self.parent.fichierDest) == False :
            os.mkdir(self.parent.fichierDest)
        # T�l�chargement
        max = int(AffichetailleFichier(self.parent.fichierURL))
        self.gauge.SetRange(max)
        self.downloader = Download(self, self.parent.fichierURL, self.parent.fichierDest + "/" + self.parent.nomFichier, self.gauge, self.label_introduction) 
        self.downloader.start()
        print "Telechargement de la nouvelle version : etape 3"
        self.bouton_ok.Show(False)
        

    def Arreter_telechargement(self):
        """ Arrete le t�l�chargement """
        # On v�rifie si le thread n'a jamais �t� lanc� avant :
        try:
            downloadEnCours = self.downloader.isAlive()
        except AttributeError :
            downloadEnCours = False

        if downloadEnCours:
            # Demande la confirmation de l'arr�t
            dlgConfirm = wx.MessageDialog(self, u"Souhaitez-vous vraiment arr�ter le t�l�chargement ?", u"Confirmation d'arr�t", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            reponse = dlgConfirm.ShowModal()
            dlgConfirm.Destroy()
            if reponse == wx.ID_NO:
                return
            # Si le t�l�chargement est en cours, on le stoppe :
            self.downloader.abort()
            self.label_introduction.SetLabel(u"Vous avez interrompu le t�l�chargement.")
            self.bouton_ok.Show(True)
        else:
            # Si le t�l�chargement n'est pas en cours, on ferme la fen�tre
            self.parent.Fermer()




# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PAGE FIN TELECHARGEMENT
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_fin_telechargement(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="page_fin_telechargement", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Cr�ation des widgets
        texteIntro1 = u"La mise � jour a �t� t�l�charg�e avec succ�s."
        self.label_introduction1 = FonctionsPerso.StaticWrapText(self, -1, texteIntro1)
        texteIntro2 = u"Souhaitez-vous l'installer maintenant ?"
        self.label_introduction2 = FonctionsPerso.StaticWrapText(self, -1, texteIntro2)
        
        # Boutons
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Installer_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)

    def __set_properties(self):
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString(u"Cliquez pour annuler et fermer")
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        

    def __do_layout(self):        
        # Sizer Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        # Sizer principal
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.label_introduction1, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.label_introduction2, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add((5, 5), 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)       
        self.SetSizer(grid_sizer_base)
        self.Layout()
        
    def Onbouton_aide(self, event):
        self.parent.Aide()
                    
    def Onbouton_annuler(self, event):
        # Fermeture
        print "annuler"
        self.parent.Fermer()
        
    def Onbouton_ok(self, event):
        # T�l�chargement termin�e avec succ�s
        self.parent.Active_page("page_installation")

    def Activation(self):
        self.SetSize((500, 600))
        self.Refresh()
        
        
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PAGE INSTALLATION
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Page_installation(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="page_installation", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Cr�ation des widgets
        texteIntro = u"Installation de la mise � jour en cours..."
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        self.journal = wx.TextCtrl(self, -1,"", size=(-1, 10), style=wx.TE_MULTILINE)
        
        # Boutons
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Installer_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)

    def __set_properties(self):
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString(u"Cliquez pour annuler et fermer")
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        

    def __do_layout(self):        
        # Sizer Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        # Sizer principal
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.label_introduction, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.journal, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)       
        self.SetSizer(grid_sizer_base)
        self.Layout()
        
    def Onbouton_aide(self, event):
        self.parent.Aide()
                    
    def Onbouton_annuler(self, event):
        # Fermeture
        pass
        
    def Onbouton_ok(self, event):
        # Fermeture
        print "ok"

    def Activation(self):
        # Pour contrer bug de Layout
        self.SetSize((500, 700))
        self.Installation()
    
    def Installation(self):
        """ Proc�dure d'installation """
        # Sauvegarde globale du r�pertoire teamWorks
        self.bouton_ok.Enable(False)
        self.bouton_annuler.Enable(False)
        self._Sauvegarde()
        
    def _Sauvegarde(self):
        """ Proc�dure de sauvegarde globale du r�pertoire """
        self.label_introduction.SetLabel(u"Sauvegarde globale des donn�es en cours...")
        if "linux" not in sys.platform :
            self.journal.WriteText(u"> Sauvegarde globale des donn�es :\n\n")
        
        fichierDest = self.parent.fichierDest + "/global_save.zip"
        if "win" in sys.platform : fichierDest = fichierDest.replace("/", "\\")
        repApplication = os.getcwd()
        
        save = zipdirectory(self, self.journal, fichierDest, repApplication)
        save.start()
        
    def _Installation(self):
        """ Proc�dure d'installation """
        self.label_introduction.SetLabel(u"Chargement de l'installeur...")
        self.journal.WriteText(u"\n\nInstalleur en cours de chargement. Veuillez patienter...")
        
        # Lancement de l'installeur
        fichierMAJ = self.parent.fichierDest + "/" + self.parent.nomFichier
        FonctionsPerso.LanceFichierExterne(fichierMAJ)
        
        # Fermeture de TeamWorks
        try :
            topWindow = wx.GetApp().GetTopWindow()
            nomWindow = topWindow.GetName()
        except :
            nomWindow = None
        if nomWindow == "general" : 
            # Si la frame 'General' est charg�e, on sauvegarde et on ferme TeamWorks
            sleep(2)
            topWindow.Quitter()
            topWindow.Destroy()
        else:
            # Si il n'y a que le Updater qui est charg�, on quitte uniquement cette fen�tre
            sleep(2)
            self.parent.Fermer()

        
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    """ Frame de test """
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, title=u"Mises � jour Internet", name="frm_updater", style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.page_active = ""
        
        self.MakeModal(True)
        
        # Changer ci-dessous pour ne pas afficher la page de recherche (1ere page)
        self.afficher_page_recherche = True 
        
        # Fichiers
        if "linux" in sys.platform :
            # Version Debian
            self.nomFichier = "teamworks.deb"
            self.fichierURL = "http://www.clsh-lannilis.com/teamworks/debian/" + self.nomFichier
        else:
            # Version Windows
            self.nomFichier = "teamworks.exe"
            self.fichierURL = "http://www.clsh-lannilis.com/teamworks/" + self.nomFichier
            
        self.fichierDest = ""
        self.tailleFichier = 0
        self.versionFichier = ""
        
        # Cr�ation du sizer
        self.sizer_base = wx.BoxSizer(wx.VERTICAL)
        
        # Cr�ation des pages dans le sizer
        self.Creation_page("page_recherche", "Page_recherche")
        self.Creation_page("page_disponible", "Page_disponible")
        self.Creation_page("page_telechargement", "Page_telechargement")
        self.Creation_page("page_fin_telechargement", "Page_fin_telechargement")
        self.Creation_page("page_installation", "Page_installation")
        
        # Chois de la page ouverte au d�marrage
        self.Active_page("page_recherche")
        
        # Finalisation du sizer
        self.SetSizer(self.sizer_base)
        self.Layout()
        
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Updater.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetMinSize((450, 250))
        self.SetSize((450, 320))
        self.CentreOnScreen()
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    
    def Creation_page(self, nomPage="", nomClasse=""):
        """ Cr�ation d'une page """
        exec("self." + nomPage + " = " + nomClasse + "(self)")
        exec("self.sizer_base.Add(self." + nomPage + ", 1, wx.EXPAND, 0)")
        exec("self." + nomPage +".Show(False)")
    
    def Active_page(self, choixPage=""):
        """ Active une page choisie """
        # Faire dispara�tre la page actuelle
        if self.page_active != "" : 
            exec("self." + self.page_active + ".Show(False)")
        # Faire appara�tre et active la page choisie
        if choixPage != "" :
            self.page_active = choixPage
            exec("self." + choixPage + ".Show(True)")
            exec("self." + choixPage + ".Activation()")
            self.Layout()
    
    
    def Aide(self):
        FonctionsPerso.Aide(28)
        
    def Fermer(self):
        self.MakeModal(False)
        self.Destroy()

    def OnClose(self, event):
        if self.page_active == "page_telechargement" :
            self.page_telechargement.Arreter_telechargement()
        elif self.page_active == "page_installation" :
            pass
        else:
            self.Fermer()
            #event.Skip()
        
               
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()