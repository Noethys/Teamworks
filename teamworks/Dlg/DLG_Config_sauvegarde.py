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
import os
import zipfile
import wx.lib.agw.customtreectrl as CT
import datetime
from Utils import UTILS_Fichiers


LISTE_SOURCES = [    [_(u"Les fichiers de données"), UTILS_Fichiers.GetRepData(), "DATA"],
                                    [_(u"Les contrats édités"), "Documents/Editions/", "CONE"], 
                                    [_(u"Les modèles de contrats"), "Documents/Modeles/", "CONM"],
                                    [_(u"Les photos des personnes"), "Photos/", "PHOT"],
                                    ] # Type Source, répertoire, code extension
                                    
LISTE_INDESIRABLES = [
            "Thumbs.db",
            "Exemple.twk",
            "Contrat d'engagement éducatif - Exemple.doc",
            "Contrat d'engagement éducatif - Exemple.odt",
            "Contrat à durée déterminée - Exemple.doc",
            "Contrat à durée déterminée - Exemple.odt",
            "Autorisation parentale mineurs - Exemple.doc",
            "Autorisation parentale mineurs - Exemple.odt",
            "Certificat de travail - Exemple.doc",
            "Certificat de travail - Exemple.odt",
            "Contrat à durée déterminée - Exemple.doc",
            "Contrat à durée déterminée - Exemple.odt",
            "Contrat d'engagement éducatif - Exemple.doc",
            "Contrat d'engagement éducatif - Exemple.odt",
            "Fiche candidature animateur - Exemple.doc",
            "Fiche candidature animateur - Exemple.odt",
            "Fiche renseignements salarié - Exemple.doc",
            "Fiche renseignements salarié - Exemple.odt",
            "Invitation réunion - Exemple.doc",
            "Invitation réunion - Exemple.odt",
            "20090529142759BMW1.jpg",
            "20090529142759BMW2.jpg",
            "20090529142759BMW3.jpg",
            "20090529142759BMW4.jpg",
            "20090529142759BMW5.jpg",
            "20090529142759BMW6.jpg",
            "20090529142759BMW7.jpg",
            "20090529142759BMW8.jpg",
            "20090529142759BMW9.jpg",
            "20090529142759BMW10.jpg",
            "20090529142759BMW11.jpg",
            "20090529142759BMW12.jpg",
            "20090529142759BMW13.jpg",
            "20090529142759BMW14.jpg",
            "20090529142759BMW15.jpg",
            "20090529142759BMW16.jpg",
            "20090529142759BMW17.jpg",
            ]
            
            
            
def GetListeSourcesStr():
    txt = ""
    for source in LISTE_SOURCES :
        txt += source[2] + ";"
    return txt[:-1]


class Sauvegarde():
    """ Creation d'un sauvegarde occasionnelle ou automatique """
    def Save(self, fichierDest="", listeFichiers=[]) :
        """ listeFichiers = [ (extension, rep, nomFichier), ] """
        if len(listeFichiers) == 0 : return "Rien à sauvegarder !"
                
        try :                                   
            # Création du fichier ZIP
            fichierZip = zipfile.ZipFile(fichierDest, "w", compression=zipfile.ZIP_DEFLATED)

            # Intégration des fichiers dans le ZIP
            for extension, rep, nomFichier in listeFichiers :
                cheminFichier = rep + nomFichier
                nouveauNomFichier = extension + "_" + nomFichier
                fichierZip.write(cheminFichier, nouveauNomFichier )
                
            # Finalise le fichier ZIP
            fichierZip.close()
            
            return None

        except :
            return "Erreur inconnue"



class Panel(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="panel_config_sauvegarde", style=wx.TAB_TRAVERSAL)
        
        self.barreTitre = FonctionsPerso.BarreTitre(self,  _(u"Sauvegarde automatique"), u"")
        texteIntro = _(u"Vous pouvez programmer ici une sauvegarde automatique de vos données. Cette option est appliquée par défaut pour effectuer une sauvegarde de toutes les données à chaque fois que vous quittez Teamworks. Vous pouvez personnaliser les paramétres de cette fonction ci-dessous.")
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        
        # Cadre d'activation
        self.staticbox1 = wx.StaticBox(self, -1, _(u"Activation"))
        self.checkBox_activer = wx.CheckBox(self, -1, _(u"Activer la sauvegarde automatique"))
                
        # Cadre des paramètres
        self.staticbox2 = wx.StaticBox(self, -1, _(u"Paramètres"))
        self.label_frequence = wx.StaticText(self, -1, _(u"Fréquence :"))
        self.label_frequence2 = wx.StaticText(self, -1, u"")
        self.label_elements = wx.StaticText(self, -1, _(u"Eléments à sauver :"))
        self.label_elements2 = wx.StaticText(self, -1, u"")
        self.label_destination = wx.StaticText(self, -1, _(u"Destination :"))
        self.label_destination2 = wx.StaticText(self, -1, u"")
        self.label_conservation = wx.StaticText(self, -1, _(u"Conservation :"))
        self.label_conservation2 = wx.StaticText(self, -1, u"")
        self.bouton_parametres = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Parametres_sauvegarde.png"), wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Aide.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        if parent.GetName() != "treebook_configuration" :
            self.bouton_aide.Show(False)

        self.Bind(wx.EVT_CHECKBOX, self.OnCheck_activer, self.checkBox_activer)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_parametres, self.bouton_parametres)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        # Layout
        grid_sizer_principal = wx.FlexGridSizer(rows=8, cols=1, vgap=0, hgap=0)
        grid_sizer_principal.Add(self.barreTitre, 1, wx.EXPAND, 0)
        grid_sizer_principal.Add(self.label_introduction, 1, wx.ALL|wx.EXPAND, 10)
        
        # Cadre 1
        staticbox1 = wx.StaticBoxSizer(self.staticbox1, wx.VERTICAL)
        staticbox1.Add(self.checkBox_activer, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_principal.Add(staticbox1, 1, wx.ALL|wx.EXPAND, 10)
        
        # Cadre 2
        staticbox2 = wx.StaticBoxSizer(self.staticbox2, wx.VERTICAL)
        grid_sizer_param = wx.FlexGridSizer(rows=9, cols=2, vgap=10, hgap=10)
        grid_sizer_param.Add(self.label_frequence, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.label_frequence2, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.label_elements, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_param.Add(self.label_elements2, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.label_destination, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.label_destination2, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.label_conservation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.label_conservation2, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add((20, 20), 0, 0, 0)
        grid_sizer_param.Add(self.bouton_parametres, 0, wx.TOP|wx.EXPAND, 10)

        staticbox2.Add(grid_sizer_param, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_principal.Add(staticbox2, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_principal.Add((20, 20), 0, wx.ALL|wx.EXPAND, 10)
        grid_sizer_principal.AddGrowableRow(4)
        grid_sizer_principal.AddGrowableCol(0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=10)
        grid_sizer_boutons.Add((5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_principal.Add(grid_sizer_boutons, 1, wx.EXPAND|wx.ALL, 10)
        
        self.SetSizer(grid_sizer_principal)
        grid_sizer_principal.Fit(self)
        grid_sizer_principal.AddGrowableRow(3)

    
    def Onbouton_parametres(self, event):
        frameSaisie = Saisie_sauvegarde_auto(self)
        frameSaisie.Show()        

    def MAJpanel(self):
        self.Importation()
        self.MAJ_Affichage() 
        
        
    def MAJ_Affichage(self):
        """ Met à jour l'affichage en fonction des données """
        # Activation des contrôles
        self.checkBox_activer.SetValue(self.activation)
        self.label_frequence.Enable(self.activation)
        self.label_frequence2.Enable(self.activation)
        self.label_elements.Enable(self.activation)
        self.label_elements2.Enable(self.activation)
        self.label_destination.Enable(self.activation)
        self.label_destination2.Enable(self.activation)
        self.label_conservation.Enable(self.activation)
        self.label_conservation2.Enable(self.activation)
        self.bouton_parametres.Enable(self.activation)
        self.Layout()
 
    def Importation(self):
        """ Recherche dans la base des paramètres de la sauvegarde auto. """
        DB = GestionDB.DB()        
        req = "SELECT save_active, save_frequence, save_elements, save_destination, save_conservation FROM divers WHERE IDdivers=1;"
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        DB.Close()
        if len(donnees) == 0 : return
        self.activation = donnees[0][0]
        self.frequence = donnees[0][1]
        self.elements = donnees[0][2]
        self.destination = donnees[0][3]
        self.conservation = donnees[0][4]
        
        # Remplissage choice frequence
        listeFrequences = [ _(u"A chaque fermeture du logiciel"), _(u"Toutes les semaines"), _(u"Tous les quinze jours"), _(u"Tous les mois")]
        if type(self.frequence) == int :
            self.label_frequence2.SetLabel(listeFrequences[self.frequence])
        # Remplissage listBox Elements
        txtElements = ""
        if self.elements != "" and self.elements != None :
            self.listeElements = self.elements.split(";")
            for source in LISTE_SOURCES :
                if source[2] in self.listeElements :
                    txtElements += "- " + source[0] + "\n"
            txtElements = txtElements[:-1]
        self.label_elements2.SetLabel(txtElements)
        # Remplissage texte Destination
        self.label_destination2.SetLabel(self.destination)
        # Remplissage
        if type(self.conservation) == int :
            if self.conservation < 2 : 
                self.label_conservation2.SetLabel(str(self.conservation) + _(u" sauvegarde de sécurité sera sauvegardée en archive."))
            else:
                self.label_conservation2.SetLabel(str(self.conservation) + _(u" sauvegardes de sécurité seront conservées en archive."))
                       
    def OnCheck_activer(self, event):
        
        # Empeche l'activation si c'est un fichier réseau :
        if "[RESEAU]" in FonctionsPerso.GetNomDB() and self.checkBox_activer.GetValue() == True :
            self.checkBox_activer.SetValue(False)
            dlg = wx.MessageDialog(self, _(u"La fonction de sauvegarde automatique n'est pas disponible pour les fichiers réseau."), _(u"Fonction indisponible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        self.activation = self.checkBox_activer.GetValue()
        self.MAJ_Affichage()
        
        # Enleve le mot de passe
        if self.checkBox_activer.GetValue() == True :
            activation = 1
        else :
            activation = 0
        # Enregistrement dans la base
        DB = GestionDB.DB()
        listeDonnees = [ ("save_active",   activation),]
        DB.ReqMAJ("divers", listeDonnees, "IDdivers", 1)
        DB.Commit()
        DB.Close()
    
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(17) 



class MyFrame(wx.Frame):
    def __init__(self, parent, title="" ):
        wx.Frame.__init__(self, parent, -1, title=title, name="frm_config_sauvegarde", style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.MakeModal(True)
        
        self.panel_base = wx.Panel(self, -1)
        self.panel_contenu = Panel(self.panel_base)
        self.panel_contenu.barreTitre.Show(False)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.SetMinSize((550, 450))
        self.SetSize((550, 450))

    def __set_properties(self):
        self.SetTitle(_(u"Sauvegarde automatique"))
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString(_(u"Cliquez pour annuler et fermer"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.ALL|wx.EXPAND, 0)
        sizer_pages.Add(self.panel_contenu, 1, wx.EXPAND | wx.TOP, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        self.Centre()
        self.sizer_pages = sizer_pages


        
        
    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def Onbouton_aide(self, event):
        FonctionsPerso.Aide(17)
            
    def Onbouton_annuler(self, event):
        # Si frame Creation_contrats ouverte, on met à jour le listCtrl Valeurs de points
        self.MAJparents()
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()
        
    def Onbouton_ok(self, event):
        # Si frame Creation_contrats ouverte, on met à jour le listCtrl Valeurs de points
        self.MAJparents()
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()     
        
    def MAJparents(self):
        if FonctionsPerso.FrameOuverte("frm_creation_contrats") != None :
            self.GetParent().MAJ_ListCtrl()
        if FonctionsPerso.FrameOuverte("frm_creation_modele_contrats") != None :
            self.GetParent().MAJ_ListCtrl() 




# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class Saisie_sauvegarde_auto(wx.Frame):
    def __init__(self, parent, title=""):
        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)
        
        self.panel_base = wx.Panel(self, -1)
        self.staticbox = wx.StaticBox(self.panel_base, -1, _(u"Paramètres"))
        self.label_frequence = wx.StaticText(self.panel_base, -1, _(u"Fréquence :"))
        listeFrequences = [ _(u"A chaque fermeture du logiciel"), _(u"Toutes les semaines"), _(u"Tous les quinze jours"), _(u"Tous les mois")]
        self.choice_frequence = wx.Choice(self.panel_base, -1, size=(300, -1), choices = listeFrequences)
        listeElements = []
        for source in LISTE_SOURCES :
            listeElements.append(source[0])
        self.label_elements = wx.StaticText(self.panel_base, -1, _(u"Eléments à sauver :"))
        self.listBox_elements = wx.CheckListBox(self.panel_base, -1, (-1, -1), wx.DefaultSize, listeElements)
        self.label_destination = wx.StaticText(self.panel_base, -1, _(u"Destination :"))
        self.textctrl_destination = wx.TextCtrl(self.panel_base, -1, "", size=(-1, -1))
        self.bouton_destination = wx.BitmapButton(self.panel_base, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Repertoire.png"), wx.BITMAP_TYPE_ANY))
        self.label_conservation = wx.StaticText(self.panel_base, -1, _(u"Conservation :"))
        self.choice_conservation = wx.Choice(self.panel_base, -1, choices = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        self.label_destination2 = wx.StaticText(self.panel_base, -1, _(u"sauvegardes de sécurité seront conservées en archive."))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDestination, self.bouton_destination)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.Importation()

        
    def __set_properties(self):
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Sauvegarder_param.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetTitle(_(u"Paramètres de la sauvegarde automatique"))
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString("Cliquez ici pour valider")
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString("Cliquez ici pour annuler la saisie")
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base_2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        
        # Cadre
        staticbox = wx.StaticBoxSizer(self.staticbox, wx.VERTICAL)
        grid_sizer_param = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_param.Add(self.label_frequence, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.choice_frequence, 0, wx.ALL|wx.EXPAND, 0)
        grid_sizer_param.Add(self.label_elements, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_param.Add(self.listBox_elements, 0, wx.ALL|wx.EXPAND, 0)
        grid_sizer_param.Add(self.label_destination, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_destination = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_destination.Add(self.textctrl_destination, 0, wx.ALL|wx.EXPAND, 0)
        grid_sizer_destination.Add(self.bouton_destination, 0, wx.ALL|wx.EXPAND, 0)
        grid_sizer_destination.AddGrowableCol(0)
        grid_sizer_param.Add(grid_sizer_destination, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_conservation = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_conservation.Add(self.choice_conservation, 0, wx.ALL|wx.EXPAND, 0)
        grid_sizer_conservation.Add(self.label_destination2, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_param.Add(self.label_conservation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(grid_sizer_conservation, 0, wx.ALL|wx.EXPAND, 0)
        staticbox.Add(grid_sizer_param, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_base.Add(staticbox, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        sizer_base_2.Add(grid_sizer_base, 1, wx.EXPAND, 0)
        self.panel_base.SetSizer(sizer_base_2)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)        
        sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()
 
    def Importation(self):
        """ Recherche dans la base des paramètres de la sauvegarde auto. """
        DB = GestionDB.DB()        
        req = "SELECT save_active, save_frequence, save_elements, save_destination, save_conservation FROM divers WHERE IDdivers=1;"
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        DB.Close()
        if len(donnees) == 0 : return
        self.frequence = donnees[0][1]
        self.elements = donnees[0][2]
        self.destination = donnees[0][3]
        self.conservation = donnees[0][4]
        
        # Remplissage choice frequence
        if type(self.frequence) == int :
            self.choice_frequence.Select(self.frequence)
        # Remplissage listBox Elements
        if self.elements != "" and self.elements != None :
            self.listeElements = self.elements.split(";")
            index = 0
            for source in LISTE_SOURCES :
                if source[2] in self.listeElements :
                    self.listBox_elements.Check(index, True)
                else:
                    self.listBox_elements.Check(index, False)
                index += 1
        # Remplissage texte Destination
        self.textctrl_destination.SetValue(self.destination)
        # Remplissage
        if type(self.conservation) == int :
            self.choice_conservation.Select(self.conservation)

    def OnBoutonDestination(self, event):
        if self.textctrl_destination.GetValue != "" : 
            cheminDefaut = self.textctrl_destination.GetValue()
            if os.path.isdir(cheminDefaut) == False :
                cheminDefaut = ""
        else:
            cheminDefaut = ""
        dlg = wx.DirDialog(self, _(u"Veuillez sélectionner un répertoire de destination :"), defaultPath=cheminDefaut, style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.textctrl_destination.SetValue(dlg.GetPath())
        dlg.Destroy()
        
        
    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(17)

    def OnBoutonAnnuler(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        
        # Fréquence
        varFrequence = self.choice_frequence.GetSelection()
        
        # liste des éléments à sauver
        varElements = ""
        for index in range(self.listBox_elements.GetCount()) :
            if self.listBox_elements.IsChecked(index) == True :
                varElements += LISTE_SOURCES[index][2] + ";"
        if len(varElements)>0 :
            varElements = varElements[:-1]
        else:
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins un élément à sauvegarder dans la liste proposée !"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        # Destination
        varDestination = self.textctrl_destination.GetValue()
        if varDestination == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un répertoire de destination valide !"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Teste la validité du répertoire
        if os.path.isdir(varDestination) == False :
            dlg = wx.MessageDialog(self, _(u"Le répertoire de destination sélectionné ne semble pas valide. Veuillez vérifier votre saisie !"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Conservation
        varConservation = self.choice_conservation.GetSelection()
           
    
        # Sauvegarde
                # Enregistrement dans la base
        DB = GestionDB.DB()
        listeDonnees = [    ("save_frequence",   varFrequence),
                                    ("save_elements",   varElements),
                                    ("save_destination",   varDestination),
                                    ("save_conservation",   varConservation),]
        DB.ReqMAJ("divers", listeDonnees, "IDdivers", 1)
        DB.Commit()
        DB.Close()
        
        # MAJ du panel Password
        if FonctionsPerso.FrameOuverte("panel_config_sauvegarde") != None :
            self.GetParent().MAJpanel()

        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()
        

# ------------------------------------------------------------------------------------------------------------------------------------------------------------




class Saisie_sauvegarde_occasionnelle(wx.Frame):
    def __init__(self, parent, title=""):
        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)
        
        self.panel_base = wx.Panel(self, -1)
        texteIntro = _(u"Vous pouvez ici créer une sauvegarde occasionnelle de vos données. Cela peut vous être utile si vous souhaitez par exemple sauvegarder certaines données sur une clé USB ou si vous allez changer d'ordinateur. Dans ce dernier cas, il vous suffira ensuite de restaurer la sauvegarde sur votre nouvel ordinateur...")
        self.label_introduction = FonctionsPerso.StaticWrapText(self.panel_base, -1, texteIntro)
        self.staticbox = wx.StaticBox(self.panel_base, -1, _(u"Paramètres de la sauvegarde"))
        
        self.label_nomFichier = wx.StaticText(self.panel_base, -1, _(u"Nom sauvegarde :"))
        self.textctrl_nomFichier = wx.TextCtrl(self.panel_base, -1, "")

        self.label_elements = wx.StaticText(self.panel_base, -1, _(u"Eléments à sauver :"))
        self.treeCtrl = TreeCtrl_Sauvegarde(self.panel_base, -1)       
        
        self.label_destination = wx.StaticText(self.panel_base, -1, _(u"Destination :"))
        standardPath = wx.StandardPaths.Get()
        destination = standardPath.GetDocumentsDir()
        self.textctrl_destination = wx.TextCtrl(self.panel_base, -1, destination, size=(-1, -1))
        self.bouton_destination = wx.BitmapButton(self.panel_base, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Repertoire.png"), wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDestination, self.bouton_destination)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # Créée le nom de Fichier ZIP par défaut
        #date_jour =  str(datetime.date.today().day) + "-" + str(datetime.date.today().month) + "-" + str(datetime.date.today().year)
        date_jour =  str(datetime.date.today())
        self.textctrl_nomFichier.SetValue("Sauvegarde_" + date_jour)

        
    def __set_properties(self):
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Sauvegarder.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetTitle(_(u"Paramètres de la sauvegarde occasionnelle"))
        self.textctrl_nomFichier.SetToolTipString(_(u"Saisissez ici un nom pour votre fichier de sauvegarde \nou laissez celui donné par défaut"))
        #self.treeCtrl.SetToolTipString(_(u"Cochez les éléments que vous souhaitez sauvegarder"))
        self.textctrl_destination.SetToolTipString(_(u"Vous pouvez saisir ici le répertoire de destination pour votre fichier de sauvegarde \nou cliquez sur le bouton pour choisir un emplacement"))
        self.bouton_destination.SetToolTipString(_(u"Cliquez ici pour sélectionner un répertoire de destination"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler la saisie"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base_2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_introduction, 1, wx.ALL|wx.EXPAND, 10)
        
        # Cadre
        staticbox = wx.StaticBoxSizer(self.staticbox, wx.VERTICAL)
        grid_sizer_param = wx.FlexGridSizer(rows=5, cols=2, vgap=10, hgap=10)
        
        grid_sizer_param.Add(self.label_nomFichier, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.textctrl_nomFichier, 0, wx.ALL|wx.EXPAND, 0)
        
        grid_sizer_param.Add(self.label_elements, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_param.Add(self.treeCtrl, 0, wx.ALL|wx.EXPAND, 0)
        grid_sizer_param.Add(self.label_destination, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_destination = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_destination.Add(self.textctrl_destination, 0, wx.ALL|wx.EXPAND, 0)
        grid_sizer_destination.Add(self.bouton_destination, 0, wx.ALL|wx.EXPAND, 0)
        grid_sizer_destination.AddGrowableCol(0)
        grid_sizer_param.Add(grid_sizer_destination, 1, wx.EXPAND|wx.ALL, 0)

        staticbox.Add(grid_sizer_param, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_base.Add(staticbox, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        sizer_base_2.Add(grid_sizer_base, 1, wx.EXPAND, 0)
        self.panel_base.SetSizer(sizer_base_2)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_param.AddGrowableCol(1)
        grid_sizer_param.AddGrowableRow(1)
        
        self.SetSizer(sizer_base)        
        sizer_base.Fit(self)
        self.Layout()
        self.SetMinSize((450, 320))
        self.SetSize((550, 400))
        self.CentreOnScreen()


    def OnBoutonDestination(self, event):
        if self.textctrl_destination.GetValue != "" : 
            cheminDefaut = self.textctrl_destination.GetValue()
            if os.path.isdir(cheminDefaut) == False :
                cheminDefaut = ""
        else:
            cheminDefaut = ""
        dlg = wx.DirDialog(self, _(u"Veuillez sélectionner un répertoire de destination :"), defaultPath=cheminDefaut, style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.textctrl_destination.SetValue(dlg.GetPath())
        dlg.Destroy()
        
        
    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(18)

    def OnBoutonAnnuler(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        
        # Nom du fichier
        varNomFichier = self.textctrl_nomFichier.GetValue()
        if varNomFichier == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom pour le fichier de sauvegarde !"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # liste des éléments à sauver
        listeElements = self.treeCtrl.GetListeItemsCoches()
        if len(listeElements) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins un élément à sauvegarder dans la liste proposée !"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        # Destination
        varDestination = self.textctrl_destination.GetValue()
        if varDestination == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un répertoire de destination valide !"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Teste la validité du répertoire
        if os.path.isdir(varDestination) == False :
            dlg = wx.MessageDialog(self, _(u"Le répertoire de destination sélectionné ne semble pas valide. Veuillez vérifier votre saisie !"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Création de la sauvegarde occasionnelle :
        fichierDest = varDestination + "/" + varNomFichier + ".twz"
        
        # Le fichier de destination existe déjà :
        if os.path.isfile(fichierDest) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier de sauvegarde portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()
                    
        save = Sauvegarde()
        etat = save.Save(fichierDest, listeElements)
        if etat == None :
            # Sauvegarde réussie : Quitte
            dlg = wx.MessageDialog(self, _(u"La sauvegarde a été créée avec succès."), "Confirmation", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.MakeModal(False)
            FonctionsPerso.SetModalFrameParente(self)
            self.Destroy()
        elif etat == False :
            # Sauvegarde non faite : Ne fait rien
            return
        else :
            # Message d'erreur
            dlg = wx.MessageDialog(self, _(u"L'erreur suivante s'est produit lors de la sauvegarde : \n\n") + err, "Erreur de sauvegarde", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            return

        

# ------------------------------------------------------------------------------------------------------------------------------------------------------


class TreeCtrl_Sauvegarde(CT.CustomTreeCtrl):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.SIMPLE_BORDER) :
        CT.CustomTreeCtrl.__init__(self, parent, id, pos, size, style)
        self.root = self.AddRoot("Sauvegarde")

        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | CT.TR_AUTO_CHECK_CHILD)
        self.EnableSelectionVista(True) 

        # Affiche les types de sources
        for typeSource, rep, extension in LISTE_SOURCES :
            item = self.AppendItem(self.root,  typeSource, ct_type=1)
            self.SetPyData(item, None)
            
            # Affiche les fichiers existants
            listeFichiers = os.listdir(rep)
            if len(listeFichiers) > 0 :
                nbreFichiers = 0
                for nomFichier in listeFichiers :
                    if nomFichier not in LISTE_INDESIRABLES :
                        child = self.AppendItem(item,  nomFichier, ct_type=1)
                        self.SetPyData(child, extension + "===" + rep + "===" + nomFichier)
                        nbreFichiers += 1
                
                if nbreFichiers > 0 :
                    self.CheckItem(item, checked=True)
                
            # Déroule l'item
            self.Expand(item)

    def GetListeItemsCoches(self):
        """ Obtient la liste des éléments cochés """
        listeFichiers = []
        # Parcours les types de sources : (1ère branche)
        nbreTypeSources = self.GetChildrenCount(self.root)
        item = self.GetFirstChild(self.root)[0]
        for index in range(nbreTypeSources) :
            if self.IsItemChecked(item) and self.GetItemPyData(item) != None : 
                data = self.GetItemPyData(item).split("===")
                listeFichiers.append(data)
            item = self.GetNext(item)
            
        return listeFichiers
           
            

# ------------------------------------------------------------------------------------------------------------------------------------------------

class Sauvegarde_auto():
    """ Sauvegardes automatiques à la fermeture du logiciel """
    def Save(self):
        
        nomFichierDest = "SaveAuto"
        
        # Recherche dans la base des paramètres de la sauvegarde auto.
        DB = GestionDB.DB()        
        req = "SELECT save_active, save_frequence, save_elements, save_destination, save_conservation, save_date_derniere FROM divers WHERE IDdivers=1;"
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        DB.Close()
        if len(donnees) == 0 : return False
        self.activation = donnees[0][0]
        self.frequence = donnees[0][1]
        self.elements = donnees[0][2]
        self.destination = donnees[0][3]
        self.conservation = donnees[0][4]
        self.dateDerniere = donnees[0][5]
        
        # Vérifie que la sauvegarde auto est activée :
        if self.activation == 0 : 
            return False
        
        # Vérifie que la fréquence impose une sauvegarde aujourd'hui :
        if self.frequence != 0 : 
            if self.dateDerniere != "" and self.dateDerniere != None :
                date_derniere = datetime.date( int(self.dateDerniere[:4]), int(self.dateDerniere[5:7]), int(self.dateDerniere[8:10]))
                date_jour =  datetime.date.today()
                nbreJours = (date_jour-date_derniere).days
                # Toutes les semaines
                if self.frequence == 1 and nbreJours < 7 : return False
                 # Tous les 15 jours
                if self.frequence == 2 and nbreJours < 15 : return False
                 # Tous les mois
                if self.frequence == 3 and nbreJours < 30 : return False
        
        # On vérifie que le répertoire de destination existe bien
        if os.path.isdir(self.destination) == False :
            print "Le repertoire de destination de sauvegarde auto n'existe pas."
            return False
            
        # Vérifie que la conservation n'impose pas la suppression d'un vieux fichier de sauvegarde
        if self.conservation > 0 :
            # On recherche les fichiers déjà présents dans le répertoire :
            listeFichierExistants = []
            contenuRepertoire = os.listdir(self.destination)
            for fichier in contenuRepertoire :
                if fichier.startswith(nomFichierDest) and fichier.endswith(".twz"):
                    listeFichierExistants.append(fichier)
        
            # On trie la liste du plus ancien au plus récent :
            listeFichierExistants.sort()
            
            # On supprime les plus anciens
            if len(listeFichierExistants) > self.conservation :
                for fichier in listeFichierExistants[:len(listeFichierExistants) - self.conservation] :
                    os.remove(self.destination + "/" + fichier)
        
        # Création de la liste des fichiers à sauvegarder :
        listeElements = self.elements.split(";")
        if len(listeElements) == 0 : return False
        listeFichiers = []
        for typeSource, rep, extension in LISTE_SOURCES :
            if extension in listeElements :
                fichiersRep = os.listdir(rep)
                for nomFichier in fichiersRep :
                    if nomFichier not in LISTE_INDESIRABLES :
                        listeFichiers.append( (extension, rep, nomFichier) )
        
        if len(listeFichiers) == 0 : # Aucun fichier à sauvegarder
            return False
        
        # Création de la sauvegarde
        fichierDest = self.destination + "/" + nomFichierDest + "_" + str(datetime.date.today()) + ".twz"
        save = Sauvegarde()
        etat = save.Save(fichierDest, listeFichiers)
        
        if etat == None :
            # Sauvegarde réussie : Quitte
            return
        elif etat == False :
            # Sauvegarde non faite : Ne fait rien
            return
        else :
            # Message d'erreur
            dlg = wx.MessageDialog(None, _(u"L'erreur suivante s'est produit lors de la sauvegarde : \n\n") + etat, "Erreur de sauvegarde", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            return
            


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class Restauration(wx.Frame):
    def __init__(self, parent, fichierRestauration=""):
        wx.Frame.__init__(self, parent, -1, title="", style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)
        self.fichierRestauration = fichierRestauration
        self.panel_base = wx.Panel(self, -1)
        texteIntro = _(u"Veuillez sélectionner les éléments à restaurer :")
        self.label_introduction = FonctionsPerso.StaticWrapText(self.panel_base, -1, texteIntro)
        self.treeCtrl = TreeCtrl_Restauration(self.panel_base, fichierRestauration, -1)         
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        
    def __set_properties(self):
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Restaurer.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetTitle(_(u"Restauration d'une sauvegarde"))
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString("Cliquez ici pour valider")
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString("Cliquez ici pour annuler la saisie")
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base_2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_introduction, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(self.treeCtrl, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        sizer_base_2.Add(grid_sizer_base, 1, wx.EXPAND, 0)
        self.panel_base.SetSizer(sizer_base_2)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        
        self.SetSizer(sizer_base)        
        sizer_base.Fit(self)
        self.Layout()
        self.SetMinSize((450, 320))
        self.SetSize((550, 400))
        self.CentreOnScreen()
        
        
    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(19)

    def OnBoutonAnnuler(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        
        # liste des éléments à sauver
        listeFichiers = self.treeCtrl.GetListeItemsCoches()
        if len(listeFichiers) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins un élément à restaurer dans la liste proposée !"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Lance la restauration
        self.Resto(listeFichiers)
    
    def Resto(self, listeFichiers=[]):
        # Créée un dictionnaire des répertoires :
        dictChemins = {}
        for nomSource, rep, ext in LISTE_SOURCES :
            dictChemins[ext] = rep

        # Ouverture du fichier ZIP
        fichierZip = zipfile.ZipFile(self.fichierRestauration, "r")
        
        for fichier in listeFichiers :
            extensionFichier = fichier[:4]
            nomFichier = fichier[5:]
            chemin = dictChemins[extensionFichier]
            
            # On vérifie que le fichier n'existe pas déjà dans le répertoire de destination
            if os.path.isfile(chemin + nomFichier) == True :
                dlg = wx.MessageDialog(None, _(u"Le fichier '") + nomFichier.decode("iso-8859-15") + _(u"' existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.CANCEL |wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse == wx.ID_NO :
                    validation = False                    
                elif reponse == wx.ID_YES :
                    validation = True
                else :
                    validation = "stop"
                    dlg2 = wx.MessageDialog(self, _(u"Restauration arrêtée."), _(u"Restauration arrêtée"), wx.OK| wx.ICON_INFORMATION)  
                    dlg2.ShowModal()
                    dlg2.Destroy()
                    fichierZip.close()
                    return
            else:
                validation = True               
            
            # On restaure le fichier
            if validation == True :
                try :
                    buffer = fichierZip.read(fichier)
                    f = open (chemin + nomFichier, "wb")
                    f.write(buffer)
                    f.close()
                except err :
                    dlg = wx.MessageDialog(self, _(u"La restauration du fichier '") + nomFichier + _(u"' a rencontré l'erreur suivante : \n") + err, "Erreur", wx.OK| wx.ICON_ERROR)  
                    dlg.ShowModal()
                    dlg.Destroy()
            
        fichierZip.close()
        
        # Message de confirmation de réussite
        dlg = wx.MessageDialog(self, _(u"Vos fichiers ont été restaurés avec succès."), _(u"Restauration réussie"), wx.OK| wx.ICON_INFORMATION)  
        dlg.ShowModal()
        dlg.Destroy()
        
        # Fermeture de la fenêtre
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()
        

# ------------------------------------------------------------------------------------------------------------------------------------------------------

class TreeCtrl_Restauration(CT.CustomTreeCtrl):
    def __init__(self, parent, fichier="", id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.SIMPLE_BORDER) :
        CT.CustomTreeCtrl.__init__(self, parent, id, pos, size, style)
        self.root = self.AddRoot("Restauration")

        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | CT.TR_AUTO_CHECK_CHILD)
        self.EnableSelectionVista(True) 

        # Ouverture du fichier ZIP
        fichierZip = zipfile.ZipFile(fichier, "r")
            
        # Recherche les types de sources présents dans la sauvegarde
        listeTypesSources = {}
        for fichier in fichierZip.namelist() :
            extensionFichier = fichier[:4]
            listeTypesSources[extensionFichier] = ""
        
        # Affiche les types de sources
        for typeSource, rep, extensionSource in LISTE_SOURCES :
            if listeTypesSources.has_key(extensionSource) == True :
                item = self.AppendItem(self.root,  typeSource, ct_type=1)
                self.SetPyData(item, None)
                
                # Affiche les fichiers existants
                for fichier in fichierZip.namelist() :
                    extensionFichier = fichier[:4]
                    nomFichier = fichier[5:]
                    if extensionFichier == extensionSource :
                        child = self.AppendItem(item,  nomFichier, ct_type=1)
                        self.SetPyData(child, fichier)
                    self.CheckItem(item, checked=True)
                    
                # Déroule l'item
                self.Expand(item)
        
        fichierZip.close()

    def GetListeItemsCoches(self):
        """ Obtient la liste des éléments cochés """
        listeFichiers = []
        # Parcours les types de sources : 
        nbreTypeSources = self.GetChildrenCount(self.root)
        item = self.GetFirstChild(self.root)[0]
        for index in range(nbreTypeSources) :
            if self.IsItemChecked(item) and self.GetItemPyData(item) != None : 
                data = self.GetItemPyData(item)
                listeFichiers.append(data)
            item = self.GetNext(item)
            
        return listeFichiers
           
            

# ------------------------------------------------------------------------------------------------------------------------------------------------



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
