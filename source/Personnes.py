#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import wx.lib.mixins.listctrl  as  listmix
from wx.lib.splitter import MultiSplitterWindow
import GestionDB
import re
import datetime
import FonctionsPerso
import Gadget_pb_personnes
import os
import sys

import OL_personnes
import CTRL_Photo

from ObjectListView import Filter

try: import psyco; psyco.full()
except: pass
        

class PanelDossiers(FonctionsPerso.PanelArrondi):
    def __init__(self, parent, ID=-1, name="panel_dossiers"):
        FonctionsPerso.PanelArrondi.__init__(self, parent, ID, texteTitre=u"Etat des dossiers")
        self.SetBackgroundColour((122, 161, 230))
        
        self.tree_ctrl_problemes = Gadget_pb_personnes.TreeCtrl(self)
        self.tree_ctrl_problemes.couleurFond = (214, 223, 247)
        self.tree_ctrl_problemes.SetBackgroundColour((214, 223, 247))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((19, 19), 0, wx.EXPAND, 0)
        sizer.Add(self.tree_ctrl_problemes, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.TOP, 14)
        self.SetSizer(sizer)




class PanelResume(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, name="panel_resume")
        self.parent = parent
        
        self.barreTitre_resume = FonctionsPerso.BarreTitre(self,  u"Détail de la sélection", u"Détail de la sélection")

        # Contrôles
        self.bitmap_photo = CTRL_Photo.CTRL_Photo(self, style=wx.SUNKEN_BORDER)
        self.bitmap_photo.SetPhoto(IDindividu=None, nomFichier="Images/128x128/Personne.png", taillePhoto=(128, 128))
        
        self.resume_L1 = wx.StaticText(self, -1, "")
        self.resume_L2 = wx.StaticText(self, -1, "")
        self.resume_L3 = wx.StaticText(self, -1, "")
        self.resume_L4 = wx.StaticText(self, -1, "")
        self.resume_L5 = wx.StaticText(self, -1, "")
        self.resume_L6 = wx.StaticText(self, -1, "")
        #self.tree_ctrl_resume = TreeCtrlCategories(self)
                
        # Propriétés
        self.SetBackgroundColour((214, 223, 247))
        self.resume_L1.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.barreTitre_resume, 0, wx.EXPAND, 0)
        
        grid_sizer_resume = wx.FlexGridSizer(rows=1, cols=3, vgap=0, hgap=0)
        grid_sizer_texte = wx.FlexGridSizer(rows=9, cols=1, vgap=0, hgap=0)
        grid_sizer_resume.Add(self.bitmap_photo, 0, wx.ALL|wx.EXPAND, 10)
        grid_sizer_texte.Add(self.resume_L1, 0, 0, 0)
        grid_sizer_texte.Add((5, 5), 0, wx.EXPAND, 0)
        grid_sizer_texte.Add(self.resume_L2, 0, 0, 0)
        grid_sizer_texte.Add((5, 5), 0, wx.EXPAND, 0)
        grid_sizer_texte.Add(self.resume_L3, 0, 0, 0)
        grid_sizer_texte.Add(self.resume_L4, 0, 0, 0)
        grid_sizer_texte.Add((5, 5), 0, wx.EXPAND, 0)
        grid_sizer_texte.Add(self.resume_L5, 0, 0, 0)
        grid_sizer_texte.Add(self.resume_L6, 0, 0, 0)
        grid_sizer_resume.Add(grid_sizer_texte, 1, wx.ALL|wx.EXPAND, 10)
        #grid_sizer_resume.Add(self.tree_ctrl_resume, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_resume.AddGrowableCol(1)
        
        grid_sizer_base.Add(grid_sizer_resume, 0, wx.EXPAND, 0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        
        self.Bind(wx.EVT_SIZE, self.OnSize)
    
    def OnSize(self, event):
        self.bitmap_photo.Refresh() 
        event.Skip()
        
    def RecupIDfichier(self):
        """ Récupère le code identifiant unique du fichier """
        DB = GestionDB.DB()        
        req = "SELECT codeIDfichier FROM divers WHERE IDdivers=1;"
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        DB.Close()
        codeIDfichier = donnees[0][0]
        return codeIDfichier
    

    def Charge_photo(self, IDpersonne):
        """ Charge la photo de la personne """
        self.photo = None
        nomFichier = "Photos/" + self.RecupIDfichier() + str(IDpersonne) + ".jpg"
        # On regarde s'il y a une photo présente dans le répertoire Photos pour cette personne
        if os.path.isfile(nomFichier):
            # Recherche si un cadre de déco est rattaché
            nomCadre = FonctionsPerso.RecupNomCadrePersonne(IDpersonne)
            if nomCadre != None :
                # Vérifie que le cadre déco existe dans le répertoire
                if os.path.isfile("Images/CadresPhotos/" + nomCadre + ".png") :
                    bmp = FonctionsPerso.CreationPhotoPersonne(IDpersonne=IDpersonne, nomFichierPhoto=nomFichier, tailleFinale = (128, 128), qualiteBmp = 100)
                else:
                    nomCadre = None
        
            # Si pas de cadre de déco
            if nomCadre == None :
                bmp = wx.Bitmap(nomFichier, wx.BITMAP_TYPE_ANY)
                bmp = bmp.ConvertToImage()
                bmp = bmp.Rescale(width=128, height=128, quality=100) 
                bmp = bmp.ConvertToBitmap()
            
            # Met la photo dans le StaticBitmap
            self.bitmap_photo.SetBitmap(bmp)
            self.photo = nomFichier
            return True
        else:
            return False
            
    def OnSelectPersonne(self, IDpersonne=0):
        """ Met à jour le cadre résumé identité """
        
        # Récupération des données de la table Personnes
        DB = GestionDB.DB()        
        req = """SELECT civilite, nom, prenom, date_naiss, ville_naiss, adresse_resid, cp_resid, ville_resid
        FROM personnes WHERE IDpersonne=%d; """ % IDpersonne
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()[0]
        DB.Close()
        
        civilite = donnees[0]
        if donnees[1] == "" or donnees[1] == None :
            nom = "?"
        else:
            nom = donnees[1]
        if donnees[2] == "" or donnees[2] == None :
            prenom = "?"
        else:
            prenom = donnees[2]
        if donnees[3] == "" or donnees[3] == None :
            date_naiss = "?"
        else:
            date_naiss = FonctionsPerso.DateEngFr(donnees[3])
        if donnees[4] == "" or donnees[4] == None :
            ville_naiss = u"?"
        else:    
            ville_naiss = donnees[4]
        if donnees[5] == "" or donnees[5] == None :
            adresse_resid = u"?"
        else:
            adresse_resid = donnees[5]
        if donnees[6] == "" or donnees[6] == None :
            cp_resid = u"?"
        else:
            cp_resid = str(donnees[6])
        if donnees[7] == "" or donnees[7] == None :
            ville_resid = u"?"
        else:
            ville_resid = donnees[7]
            
        age = self.RetourneAge(donnees[3])
        
        # Récupération des données de la table Coordonnées
        DB = GestionDB.DB()        
        req = """SELECT categorie, texte, intitule
        FROM coordonnees WHERE IDpersonne=%d; """ % IDpersonne
        DB.ExecuterReq(req)
        listeCoords = DB.ResultatReq()
        DB.Close()
        
        if len(listeCoords) != 0 :
            texteCoords = u"Tél : "
            for coord in listeCoords :
                categorie = coord[0]
                texte = coord[1]
                intitule = coord[2]
                texteCoords += texte + " | "
            texteCoords = texteCoords[:-3]
        else :
            texteCoords = u"Aucune coordonnée"
        
        # Création des lignes
        ligne1 = nom + " " + prenom
        if civilite == "Mr" : 
            ligne2 = u"Né le "
        else :
            ligne2 = u"Née le " 
        ligne2 += date_naiss + u" à " + ville_naiss + ", " + age
        ligne3 = u"Résidant " + adresse_resid + " " + cp_resid + " " + ville_resid
        
        # Photo
##        if self.Charge_photo(IDpersonne) == False :
##            if civilite == "Mr" :
##                img = wx.Bitmap("Images/128x128/Homme.png", wx.BITMAP_TYPE_ANY)
##            else :
##                img = wx.Bitmap("Images/128x128/Femme.png", wx.BITMAP_TYPE_ANY)
##            self.bitmap_photo.SetBitmap(img)        
        
        if civilite == "Mr" :
            img = "Homme.png"
        elif civilite == "Mme" or civilite == "Melle" :
            img = "Femme.png"
        else:
            img = "Personne.png"
            
        nomFichier = "Images/128x128/" + img
        self.bitmap_photo.SetPhoto(IDpersonne, nomFichier, taillePhoto=(128, 128))
        
        # Recherche des contrats
        DB = GestionDB.DB()        
        req = """SELECT contrats_class.nom, contrats.date_debut, contrats.date_fin, contrats.date_rupture, contrats_types.duree_indeterminee
        FROM contrats INNER JOIN contrats_class ON contrats.IDclassification = contrats_class.IDclassification INNER JOIN contrats_types ON contrats.IDtype = contrats_types.IDtype
        WHERE contrats.IDpersonne=%d
        ORDER BY contrats.date_fin;""" % IDpersonne
        DB.ExecuterReq(req)
        listeContrats = DB.ResultatReq()
        DB.Close()
        
        contratEnCours = False
        if len(listeContrats) == 0 : 
            # Aucun contrat existant
            etatContrat = u"Aucun contrat à ce jour."
            detailContrat = u""
        else:
            # Analyse des contrats
            dateDuJour = str(datetime.date.today())
            for classification, date_debut, date_fin, date_rupture, type in listeContrats :
                # Contrats à durée déterminée
                if type == "non" : 
                    if date_debut <= dateDuJour <= date_fin : 
                        etatContrat = u">> Contrat en cours :"
                        detailContrat = classification + " du " + FonctionsPerso.DateEngFr(date_debut) + " au " + FonctionsPerso.DateEngFr(date_fin) + "."
                        contratEnCours = True
                        break
                    elif date_fin < dateDuJour : 
                        etatContrat = u"Aucun contrat en cours. Dernier contrat :"
                        detailContrat = classification + " du " + FonctionsPerso.DateEngFr(date_debut) + " au " + FonctionsPerso.DateEngFr(date_fin) + "."
                    elif date_debut > dateDuJour : 
                        etatContrat = u"Aucun contrat en cours. Prochain contrat :"
                        detailContrat = classification + " du " + FonctionsPerso.DateEngFr(date_debut) + " au " + FonctionsPerso.DateEngFr(date_fin) + "."
                else:
                    # Contrats à durée indéterminée
                    if date_rupture != "" :
                        if date_debut <= dateDuJour <= date_rupture : 
                            etatContrat = u">> Contrat en cours :"
                            detailContrat = classification + " du " + FonctionsPerso.DateEngFr(date_debut) + " au " + FonctionsPerso.DateEngFr(date_rupture) + " (rupture)."
                            contratEnCours = True
                            break
                        elif date_rupture < dateDuJour : 
                            etatContrat = u"Aucun contrat en cours. Dernier contrat :"
                            detailContrat = classification + " du " + FonctionsPerso.DateEngFr(date_debut) + " au " + FonctionsPerso.DateEngFr(date_rupture) + " (rupture)."
                        elif date_debut > dateDuJour : 
                            etatContrat = u"Aucun contrat en cours. Prochain contrat :"
                            detailContrat = classification + " du " + FonctionsPerso.DateEngFr(date_debut) + " au " + FonctionsPerso.DateEngFr(date_rupture) + " (rupture)."
                    else:
                        if date_debut <= dateDuJour : 
                            etatContrat = u">> Contrat en cours :"
                            detailContrat = classification + u" depuis le " + FonctionsPerso.DateEngFr(date_debut) + u" (durée ind.)."
                            contratEnCours = True
                            break
                        elif date_debut > dateDuJour : 
                            etatContrat = u"Aucun contrat en cours. Prochain contrat :"
                            detailContrat = classification + u" à partir du " + FonctionsPerso.DateEngFr(date_debut) + u" (durée ind.)."
        
        # Met dans les controles
        self.resume_L1.SetLabel(ligne1)
        self.resume_L2.SetLabel(ligne2)
        self.resume_L3.SetLabel(ligne3)
        self.resume_L4.SetLabel(texteCoords)
        self.resume_L5.SetLabel(etatContrat)
        self.resume_L6.SetLabel(detailContrat)
        
        if contratEnCours == True : 
            self.resume_L5.SetForegroundColour('Red')
        else:
            self.resume_L5.SetForegroundColour('Black')

        self.Refresh()

    def RetourneAge(self, dateStr):
        if dateStr == "" or dateStr == None : return ""
        bday = datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10]))
        datedujour = datetime.date.today()
        age = (datedujour.year - bday.year) - int((datedujour.month, datedujour.day) < (bday.month, bday.day))
        texteAge = str(age) + " ans"
        return texteAge
            
            
            
                    
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class PanelPersonnes(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, name="Personnes")
        self.parent = parent
        self.init = False 

    def InitPage(self):               
        self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_3D | wx.SP_NO_XP_THEME | wx.SP_LIVE_UPDATE)
        self.window_D = wx.Panel(self.splitter, -1)
        
        # Panel Etat des dossiers
        self.window_G = MultiSplitterWindow(self.splitter, -1, style= wx.SP_NOSASH | wx.SP_LIVE_UPDATE)
        self.window_G.SetOrientation(wx.VERTICAL)
        self.window_G.SetMinimumPaneSize(100)
        self.panel_dossiers = PanelDossiers(self.window_G)
        self.window_G.AppendWindow(self.panel_dossiers, 500) # Ici c'est la hauteur du panel pb de dossiers
        
        # Panel vide
        self.panel_vide = wx.Panel(self.window_G, -1)
        self.panel_vide.SetBackgroundColour((122, 161, 230))
        self.window_G.AppendWindow(self.panel_vide, 200)
        
        self.panel_resume = PanelResume(self.window_D)
        self.label_selection = wx.StaticText(self.window_D, -1, u"")
        self.label_selection.SetForegroundColour((122, 161, 230))
        self.label_selection.Show(False)
        self.listCtrl_personnes = OL_personnes.ListView(self.window_D, id=-1,  name="OL_personnes", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.listCtrl_personnes.SetMinSize((20, 20))
        self.barreRecherche = BarreRecherche(self.window_D)
        
        self.bouton_ajouter = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_rechercher = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Calendrier3jours.png", wx.BITMAP_TYPE_ANY))
        self.bouton_affichertout = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Actualiser.png", wx.BITMAP_TYPE_ANY))
        self.bouton_options = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        self.bouton_courrier = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Mail.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        self.bouton_export_texte = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Document.png", wx.BITMAP_TYPE_ANY))
        self.bouton_export_excel = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_ANY))
        self.bouton_aide = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Aide.png", wx.BITMAP_TYPE_ANY))
        
        self.barreTitre_liste = FonctionsPerso.BarreTitre(self.window_D,  u"Liste des personnes", u"Liste des personnes")
        
        # Diminution de la taille de la police sous linux
        if "linux" in sys.platform :
            self.bouton_export_excel.Enable(False)
            
        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRechercher, self.bouton_rechercher)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAfficherTout, self.bouton_affichertout)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOptions, self.bouton_options)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCourrier, self.bouton_courrier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExportTexte, self.bouton_export_texte)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExportExcel, self.bouton_export_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        self.bouton_modifier.Enable(False)
        self.bouton_supprimer.Enable(False)
        
        self.AffichePanelResume(False)
        
        self.init = True
        
##        self.splitter.SetSashPosition(250, True)
        
    def __set_properties(self):
        self.barreRecherche.SetToolTipString(u"Saisissez ici un nom, un prénom, un nom de ville, etc... pour retrouver une personne donnée.")
        self.bouton_ajouter.SetToolTipString(u"Cliquez ici pour créer une nouvelle fiche individuelle")
        self.bouton_ajouter.SetSize(self.bouton_ajouter.GetBestSize())
        self.bouton_modifier.SetToolTipString(u"Cliquez ici pour modifier la fiche sélectionnée dans la liste\n(Vous pouvez également double-cliquer sur une ligne)")
        self.bouton_modifier.SetSize(self.bouton_modifier.GetBestSize())
        self.bouton_supprimer.SetToolTipString(u"Cliquez ici pour supprimer la fiche sélectionnée dans la liste")
        self.bouton_supprimer.SetSize(self.bouton_supprimer.GetBestSize())
        self.bouton_rechercher.SetToolTipString(u"Cliquez ici pour rechercher les personnes présentes sur une période donnée")
        self.bouton_rechercher.SetSize(self.bouton_rechercher.GetBestSize())
        self.bouton_affichertout.SetToolTipString(u"Cliquez ici pour réafficher toute la liste")
        self.bouton_affichertout.SetSize(self.bouton_affichertout.GetBestSize())
        self.bouton_options.SetToolTipString(u"Cliquez ici pour afficher les options de la liste")
        self.bouton_options.SetSize(self.bouton_options.GetBestSize())
        self.bouton_imprimer.SetToolTipString(u"Cliquez ici pour imprimer la liste")
        self.bouton_imprimer.SetSize(self.bouton_imprimer.GetBestSize())
        self.bouton_export_texte.SetToolTipString(u"Cliquez ici pour exporter la liste au format texte")
        self.bouton_export_texte.SetSize(self.bouton_export_texte.GetBestSize())
        self.bouton_export_excel.SetToolTipString(u"Cliquez ici pour exporter la liste au format Excel")
        self.bouton_export_excel.SetSize(self.bouton_export_excel.GetBestSize())
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_courrier.SetToolTipString(u"Cliquez ici pour créer un courrier ou un Email par publipostage")

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_D = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_D = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        grid_sizer_liste = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_liste2 = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=16, cols=1, vgap=5, hgap=5)
        
##        # Panel Gauche
##        sizer_G = wx.BoxSizer(wx.VERTICAL)
####        sizer_G.Add(self.barreTitre_problemes, 0, wx.EXPAND, 0)
##        grid_sizer_G = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
##        grid_sizer_G.Add(self.tree_ctrl_problemes, 1, wx.EXPAND|wx.ALL, 40)
##        grid_sizer_G.AddGrowableRow(0)
##        grid_sizer_G.AddGrowableCol(0)
##        sizer_G.Add(grid_sizer_G, 1, wx.ALL|wx.EXPAND, 0)
##        self.window_G.SetSizer(sizer_G)
        
        # Panel Droite
        grid_sizer_D.Add(self.barreTitre_liste, 0, wx.EXPAND, 0)
        
        grid_sizer_D.Add(self.label_selection, 1, wx.EXPAND|wx.ALL, 4)
        
        # Liste des personnes
        grid_sizer_liste2.Add(self.listCtrl_personnes, 1, wx.EXPAND, 0)
        grid_sizer_liste2.Add(self.barreRecherche, 0, wx.EXPAND, 0)
        grid_sizer_liste2.AddGrowableRow(0)
        grid_sizer_liste2.AddGrowableCol(0)
        grid_sizer_liste.Add(grid_sizer_liste2, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_rechercher, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_affichertout, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_options, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_courrier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_export_texte, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_export_excel, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.AddGrowableRow(2)
        grid_sizer_liste.Add(grid_sizer_boutons, 1, wx.EXPAND|wx.TOP|wx.BOTTOM|wx.RIGHT, 5)
        grid_sizer_liste.AddGrowableRow(0)
        grid_sizer_liste.AddGrowableCol(0)
        grid_sizer_D.Add(grid_sizer_liste, 1, wx.EXPAND|wx.ALL, 0)
        
##        grid_sizer_D.Add(self.barreRecherche, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_D.Add(self.panel_resume, 1, wx.EXPAND, 0)
        
        grid_sizer_D.AddGrowableRow(2)
        grid_sizer_D.AddGrowableCol(0)
        
        sizer_D.Add(grid_sizer_D, 1, wx.EXPAND, 0)
        self.window_D.SetSizer(sizer_D)
        self.splitter.SplitVertically(self.window_G, self.window_D, 240)
        sizer_base.Add(self.splitter, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.Centre()
        
        self.grid_sizer_D = grid_sizer_D

    
    def OnBoutonAjouter(self, event):
        self.listCtrl_personnes.Ajouter()
        
    def OnBoutonModifier(self, event):
        self.listCtrl_personnes.Modifier()
        
    def OnBoutonSupprimer(self, event):
        self.listCtrl_personnes.Supprimer()

    def OnBoutonRechercher(self, event):
        resultat = self.listCtrl_personnes.Rechercher()
        if resultat != False :
            self.AfficheLabelSelection(True)
            date_debut = resultat[0].strftime("%d/%m/%Y")
            date_fin = resultat[1].strftime("%d/%m/%Y")
            texte = u"Sélection des personnes présentes du %s au %s :" % (date_debut, date_fin)
            self.label_selection.SetLabel(texte)

    def OnBoutonAfficherTout(self, event):
        self.listCtrl_personnes.AfficherTout()
        self.AfficheLabelSelection(etat=False)   
        
    def OnBoutonOptions(self, event):
        self.listCtrl_personnes.Options() 
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(12)
        
    def AffichePanelResume(self, etat=True):
        """ Affiche ou fait disparaître le panel Résumé """
        if etat == True and self.panel_resume.IsShown() == True: 
            return
        self.panel_resume.Show(etat)
        self.grid_sizer_D.Layout()
        self.Refresh()
    
    def AfficheLabelSelection(self, etat=True):
        """ Affiche ou fait disparaître le label Sélection en cours de la liste des personnes """
        if etat==True and self.label_selection.IsShown()==True: 
            return
        self.label_selection.Show(etat)
        self.grid_sizer_D.Layout()
        self.Refresh()
        
        
    def MAJpanel(self, listeElements=[]) :
        """ Met à jour les éléments du panel personnes """
        # Elements possibles : [] pour tout, listCtrl_personnes
        if self.init == False :
            self.InitPage()
        #print "Je mets a jour le panel Personnes "
        if "listCtrl_personnes" in listeElements or listeElements==[] : 
            self.listCtrl_personnes.MAJ()
            self.panel_dossiers.tree_ctrl_problemes.MAJ_treeCtrl()
            if self.listCtrl_personnes.GetNbrePersonnes() == 0 :
                self.AffichePanelResume(False)
                
    def OnBoutonCourrier(self, event):
        self.listCtrl_personnes.CourrierPublipostage(mode='multiple')
        
    def OnBoutonImprimer(self, event):
        self.listCtrl_personnes.Imprimer()
        
    def OnBoutonExportTexte(self, event):
        self.listCtrl_personnes.ExportTexte()
        
    def OnBoutonExportExcel(self, event):
        self.listCtrl_personnes.ExportExcel()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class TreeCtrlCategories(wx.TreeCtrl):
    def __init__(self, parent):
        wx.TreeCtrl.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, style=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT|wx.NO_BORDER)
        # Autres styles possibles = wx.TR_HAS_BUTTONS|wx.TR_EDIT_LABELS| wx.TR_MULTIPLE|wx.TR_HIDE_ROOT
        self.parent = parent
        
        return # <<<<<<<<<<<<<
    
        self.listeDonnees = self.GetListeProblemes()
        print self.listeDonnees


        self.root = self.AddRoot(u"Problèmes à résoudre")
        self.SetPyData(self.root, None)

        self.AddTreeNodes(self.root, self.listeDonnees)

    def AddTreeNodes(self, parentItem, items, img=None):
        for item in items:
            if type(item) == str or type(item) == unicode:
                # Items
                newItem = self.AppendItem(parentItem, item)
                self.SetPyData(newItem, None)
            else:
                # Tête de rubrique
                texte = item[0]
                    
                newItem = self.AppendItem(parentItem, texte)
                self.SetPyData(newItem, None)
                # Autres
                self.AddTreeNodes(newItem, item[1], img)
                
    def OnActivate(self, event):
        if self.item:
            print ("OnActivate: %s\n" % self.GetItemText(self.item))

    def GetListeProblemes(self):
        dictNoms, dictProblemes = FonctionsPerso.Recup_liste_pb_personnes(recalc=False)
        # Transforme le dict en liste
        listeProblemes = []
        index1 = 0
        for IDpersonne, dictCategories in dictProblemes.iteritems() :
            listeProblemes.append( [dictNoms[IDpersonne], []] )
            for nomCategorie, valeurs in dictCategories.iteritems() :
                listeProblemes[index1][1].append( [nomCategorie, valeurs] )
            index1 += 1
        
        return listeProblemes

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,-1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent

        self.SetDescriptiveText(u"Rechercher une personne dans la liste")
        self.ShowSearchButton(True)
        
        self.listView = self.GetParent().GetGrandParent().listCtrl_personnes
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap("Images/16x16/Loupe.png", wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnSearch(self, evt):
        self.Recherche(self.GetValue())
            
    def OnCancel(self, evt):
        self.SetValue("")
        self.Recherche(self.GetValue())

    def OnDoSearch(self, evt):
        self.Recherche(self.GetValue())
        
    def Recherche(self, txtSearch):
        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()
        
# -----------------------------------------------------------------------------------------------------------------------------------------------------
        
class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.statusbar = self.CreateStatusBar(2, 0)
        self.statusbar.SetStatusWidths( [360, -1] )
        panel = PanelPersonnes(self)
        panel.InitPage()
        self.SetTitle(u"Panel Présences")
        self.SetSize((900, 800))
        self.Centre()



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
