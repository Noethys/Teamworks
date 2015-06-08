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

import Gadget_candidatures
import OL_candidatures
import OL_candidats
import OL_entretiens
import OL_emplois

from ObjectListView import Filter

try: import psyco; psyco.full()
except: pass


MODE_AFFICHAGE = "candidats"



class GadgetEntretiens(FonctionsPerso.PanelArrondi):
    def __init__(self, parent, ID=-1, name="gadget_entretiens"):
        FonctionsPerso.PanelArrondi.__init__(self, parent, ID, texteTitre=u"Prochains entretiens")
        self.SetBackgroundColour((122, 161, 230))
        
        self.ctrl = OL_entretiens.ListView(self, id=-1,  name="OL_gadget_entretiens", afficheHyperlink=False, prochainsEntretiens=True, modeAffichage="gadget", colorerSalaries=False, style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.NO_BORDER|wx.LC_SINGLE_SEL)
        self.ctrl.couleurFond = (214, 223, 247)
        self.ctrl.SetBackgroundColour((214, 223, 247))
        self.ctrl.stEmptyListMsg.SetBackgroundColour((214, 223, 247))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((19, 19), 0, wx.EXPAND, 0)
        sizer.Add(self.ctrl, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.TOP, 14)
        self.SetSizer(sizer)
        
        self.MAJ()
    
    def MAJ(self):
        self.ctrl.MAJ()


class GadgetAvertissement(FonctionsPerso.PanelArrondi):
    def __init__(self, parent, ID=-1, name="gadget_avertissement"):
        FonctionsPerso.PanelArrondi.__init__(self, parent, ID, texteTitre=u"Avertissement")
        self.SetBackgroundColour((122, 161, 230))
        
        texteIntro = u"Attention, ce module Recrutement est encore en phase de test. Merci de bien vouloir signaler les bugs rencontrés."
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        self.label_introduction.SetBackgroundColour((214, 223, 247))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((19, 19), 0, wx.EXPAND, 0)
        sizer.Add(self.label_introduction, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.TOP, 16)
        self.SetSizer(sizer)

class GadgetInformations(FonctionsPerso.PanelArrondi):
    def __init__(self, parent, ID=-1, name="gadget_informations"):
        FonctionsPerso.PanelArrondi.__init__(self, parent, ID, texteTitre=u"Informations")
        self.SetBackgroundColour((122, 161, 230))
        
        self.treeCtrl = Gadget_candidatures.TreeCtrl(self)
        self.treeCtrl.couleurFond = (214, 223, 247)
        self.treeCtrl.SetBackgroundColour((214, 223, 247))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((19, 19), 0, wx.EXPAND, 0)
        sizer.Add(self.treeCtrl, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.TOP, 13)
        self.SetSizer(sizer)

    def MAJ(self):
        self.treeCtrl.MAJ()


class Panelidentite(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, name="panel_identite", style=wx.SUNKEN_BORDER)
        self.parent = parent

        self.resume_L1 = wx.StaticText(self, -1, "")
        self.resume_L2 = wx.StaticText(self, -1, "")
        self.resume_L3 = wx.StaticText(self, -1, "")
        self.resume_L4 = wx.StaticText(self, -1, "")
        self.resume_L5 = wx.StaticText(self, -1, "")
        self.resume_L6 = wx.StaticText(self, -1, "")
                
        # Propriétés
        self.SetBackgroundColour((214, 223, 247))
        self.resume_L1.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        
        grid_sizer_resume = wx.FlexGridSizer(rows=1, cols=3, vgap=0, hgap=0)
        grid_sizer_texte = wx.FlexGridSizer(rows=8, cols=1, vgap=0, hgap=0)
        grid_sizer_texte.Add(self.resume_L1, 0, 0, 0)
        grid_sizer_texte.Add((5, 5), 0, wx.EXPAND, 0)
        grid_sizer_texte.Add(self.resume_L2, 0, 0, 0)
        grid_sizer_texte.Add(self.resume_L3, 0, 0, 0)
        grid_sizer_texte.Add((5, 5), 0, wx.EXPAND, 0)
        grid_sizer_texte.Add(self.resume_L4, 0, 0, 0)
        grid_sizer_texte.Add(self.resume_L5, 0, 0, 0)
        grid_sizer_texte.Add(self.resume_L6, 0, 0, 0)
        grid_sizer_resume.Add(grid_sizer_texte, 1, wx.ALL|wx.EXPAND, 10)
        #grid_sizer_resume.Add(self.tree_ctrl_resume, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_resume.AddGrowableCol(1)
        
        grid_sizer_base.Add(grid_sizer_resume, 0, wx.EXPAND, 0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)

    def MAJidentite(self, IDcandidat=None, IDpersonne=None):
        """ Met à jour le cadre résumé identité """
        
        # Récupération des données de la table Candidats
        DB = GestionDB.DB()
        if IDpersonne == None or IDpersonne == 0 :
            req = """SELECT civilite, nom, prenom, date_naiss, adresse_resid, cp_resid, ville_resid, memo, age
            FROM candidats WHERE IDcandidat=%d; """ % IDcandidat
        else:
            req = """SELECT civilite, nom, prenom, date_naiss, adresse_resid, cp_resid, ville_resid, memo
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
        date_naiss = donnees[3]
        if IDpersonne == None or IDpersonne == 0 :
            age = donnees[8]
        else:
            age = ""
        if donnees[4] == "" or donnees[4] == None :
            adresse_resid = u"?"
        else:
            adresse_resid = donnees[4]
        if donnees[5] == "" or donnees[5] == None :
            cp_resid = u"?"
        else:
            cp_resid = str(donnees[5])
        if donnees[6] == "" or donnees[6] == None :
            ville_resid = u"?"
        else:
            ville_resid = donnees[6]
        
        if date_naiss == "" and age == 0 or age == "" :
            texteAge = u"Age et date de naissance inconnus"
        if date_naiss == "" and age != 0 and age != "" :
            texteAge = "Age : %d ans" % age
        if date_naiss != "" and date_naiss != None :
            texteAge = u"Date de naissance : %s (%s)" % (FonctionsPerso.DateEngFr(date_naiss), self.RetourneAge(donnees[3]))
        
        # Récupération des qualifications du candidat
        DB = GestionDB.DB()
        if IDpersonne == None or IDpersonne == 0 :  
            req = """SELECT diplomes_candidats.IDtype_diplome, types_diplomes.nom_diplome
            FROM diplomes_candidats LEFT JOIN types_diplomes ON diplomes_candidats.IDtype_diplome = types_diplomes.IDtype_diplome
            WHERE IDcandidat=%d; """ % IDcandidat
        else:
            req = """SELECT diplomes.IDtype_diplome, types_diplomes.nom_diplome
            FROM diplomes LEFT JOIN types_diplomes ON diplomes.IDtype_diplome = types_diplomes.IDtype_diplome
            WHERE IDpersonne=%d; """ % IDpersonne
        DB.ExecuterReq(req)
        listeQualifications = DB.ResultatReq()
        DB.Close()
        texteQualifications = ""
        if len(listeQualifications) == 0 :
            texteQualifications = u"Aucune qualification"
        else:
            if civilite == "Mr" :
                texteQualifications = u"Qualifié "
            else:
                texteQualifications = u"Qualifiée "
            index = 1
            for IDtype_diplome, nom_diplome in listeQualifications :
                texteQualifications += nom_diplome
                if index == len(listeQualifications)-1 :
                    texteQualifications += " et "
                else:
                    texteQualifications += ", "
                index += 1
            texteQualifications = texteQualifications[:-2]
        
        # Récupération des données de la table Coordonnées
        DB = GestionDB.DB()
        if IDpersonne == None or IDpersonne == 0 :      
            req = """SELECT categorie, texte, intitule
            FROM coords_candidats WHERE IDcandidat=%d; """ % IDcandidat
        else:
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
        ligne2 = texteAge
        ligne3 = texteQualifications
        ligne4 = u"Résidant %s %s %s" % (adresse_resid, cp_resid, ville_resid)
        ligne5 = texteCoords
        # Met dans les controles
        self.resume_L1.SetLabel(ligne1)
        self.resume_L2.SetLabel(ligne2)
        self.resume_L3.SetLabel(ligne3)
        self.resume_L4.SetLabel(ligne4)
        self.resume_L5.SetLabel(ligne5)
##        self.resume_L6.SetLabel(detailContrat)
            
    def RetourneAge(self, dateStr):
        if dateStr == "" or dateStr == None : return ""
        bday = datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10]))
        datedujour = datetime.date.today()
        age = (datedujour.year - bday.year) - int((datedujour.month, datedujour.day) < (bday.month, bday.day))
        texteAge = str(age) + " ans"
        return texteAge



class PanelResume(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, name="panel_resume")
        self.parent = parent
        
        self.barreTitre_resume = FonctionsPerso.BarreTitre(self,  u"Détail de la sélection", u"Détail de la sélection")

        # Contrôles
        self.noteBook = wx.Notebook(self, -1, size=(-1, 150), style=wx.BK_BOTTOM)
        il = wx.ImageList(16, 16)
        self.img1 = il.Add(wx.Bitmap("Images/16x16/Identite.png", wx.BITMAP_TYPE_PNG))
        self.img2 = il.Add(wx.Bitmap("Images/16x16/Candidature.png", wx.BITMAP_TYPE_PNG))
        self.img3 = il.Add(wx.Bitmap("Images/16x16/Dialogue.png", wx.BITMAP_TYPE_PNG))
        self.noteBook.AssignImageList(il)
        
        # Panel Identité
        self.panel_identite = Panelidentite(self.noteBook)       
        self.noteBook.AddPage(self.panel_identite, u"Identité du candidat")
        self.noteBook.SetPageImage(0, self.img1)
        # ListView Candidatures
        self.listCtrl_candidatures = OL_candidatures.ListView(self.noteBook, id=-1,  name="OL_candidatures", modeAffichage = "avec_nom", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)       
        self.noteBook.AddPage(self.listCtrl_candidatures, u"Candidatures")
        self.noteBook.SetPageImage(1, self.img2)
        # ListView Entretiens
        self.listCtrl_entretiens = OL_entretiens.ListView(self.noteBook, id=-1,  name="OL_entretiens", modeAffichage="avec_nom", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.noteBook.AddPage(self.listCtrl_entretiens, u"Entretiens")
        self.noteBook.SetPageImage(2, self.img3)
        
        # Propriétés
        self.SetBackgroundColour((214, 223, 247))
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.barreTitre_resume, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.noteBook, 0, wx.EXPAND, 0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.grid_sizer_base = grid_sizer_base

            
    def MAJ(self, IDcandidat=None, IDpersonne=None, IDemploi=None):
        """ Met à jour le cadre résumé identité """
        if IDemploi == None :
            
            if self.noteBook.GetPageCount() == 1 :
                self.noteBook.RemovePage(0)
                self.noteBook.AddPage(self.panel_identite, u"Identité du candidat")
                self.noteBook.SetPageImage(0, self.img1)
                self.noteBook.AddPage(self.listCtrl_candidatures, u"Candidatures")
                self.noteBook.SetPageImage(1, self.img2)
                self.noteBook.AddPage(self.listCtrl_entretiens, u"Entretiens")
                self.noteBook.SetPageImage(2, self.img3)
            
            # MAJ des pages du noteBook
            self.panel_identite.MAJidentite(IDcandidat=IDcandidat, IDpersonne=IDpersonne)
            
            self.listCtrl_candidatures.IDcandidat = IDcandidat
            self.listCtrl_candidatures.IDpersonne = IDpersonne
            self.listCtrl_candidatures.MAJ()
            
            self.listCtrl_entretiens.IDcandidat = IDcandidat
            self.listCtrl_entretiens.IDpersonne = IDpersonne
            self.listCtrl_entretiens.MAJ()
            
            # MAJ des noms des pages du noteBook
            self.noteBook.SetPageText(0, u"Identité du candidat")
            nbreCandidatures = self.listCtrl_candidatures.GetNbreItems()
            if nbreCandidatures == 1 :
                self.noteBook.SetPageText(1, u"1 candidature")
            else:
                self.noteBook.SetPageText(1, u"%d candidatures" % nbreCandidatures)
            nbreEntretiens = self.listCtrl_entretiens.GetNbreItems()
            if nbreEntretiens == 1 :
                self.noteBook.SetPageText(2, u"1 entretien")
            else:
                self.noteBook.SetPageText(2, u"%d entretiens" % nbreEntretiens)
            self.panel_identite.Enable(True)
            self.listCtrl_entretiens.Enable(True)
##            self.noteBook.SetSelection(0)
            
        if IDemploi != None :
            # Pour afficher les candidatures attachées aux offres d'emploi
            if self.noteBook.GetPageCount() == 3 :
                self.noteBook.RemovePage(2)
                self.noteBook.RemovePage(1)
                self.noteBook.RemovePage(0)
                self.noteBook.AddPage(self.listCtrl_candidatures, u"Candidatures")
                self.noteBook.SetPageImage(0, self.img2)
            self.listCtrl_candidatures.IDcandidat = None
            self.listCtrl_candidatures.IDemploi = IDemploi
            self.listCtrl_candidatures.MAJ()
            nbreCandidatures = self.listCtrl_candidatures.GetNbreItems()
            if nbreCandidatures == 1 :
                self.noteBook.SetPageText(0, u"1 candidature")
            else:
                self.noteBook.SetPageText(0, u"%d candidatures" % nbreCandidatures)
        
    def MAJlabelsPages(self, nomPage="candidatures"):
        if nomPage=="candidatures" :
            nbreCandidatures = self.listCtrl_candidatures.GetNbreItems()
            if nbreCandidatures == 1 :
                self.noteBook.SetPageText(1, u"1 candidature")
            else:
                self.noteBook.SetPageText(1, u"%d candidatures" % nbreCandidatures)
        if nomPage=="entretiens" :
            nbreEntretiens = self.listCtrl_entretiens.GetNbreItems()
            if nbreEntretiens == 1 :
                self.noteBook.SetPageText(2, u"1 entretien")
            else:
                self.noteBook.SetPageText(2, u"%d entretiens" % nbreEntretiens)
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



class BarreAffichage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style = wx.NO_BORDER)
        self.parent = parent
##        self.SetBackgroundColour("white")
        
        self.barreTitre = FonctionsPerso.BarreTitre(self,  u"Options d'affichage", u"Options d'affichage")
        
        # Widgets        
        self.txtRadio = wx.StaticText( self, -1, u"Afficher les :" )
        self.radio1 = wx.RadioButton( self, -1, u"Candidats", style = wx.RB_GROUP )
        self.radio2 = wx.RadioButton( self, -1, u"Candidatures" )
        self.radio3 = wx.RadioButton( self, -1, u"Entretiens")
        self.radio4 = wx.RadioButton( self, -1, u"Offres d'emploi" )
        
        self.boutonOutils = wx.StaticBitmap(self, -1, wx.Bitmap("Images/16x16/Outils.png", wx.BITMAP_TYPE_PNG) )
        self.txtOutils = wx.StaticText( self, -1, "Outils" )
        self.boutonOutils.SetToolTipString(u"Cliquez ici pour afficher le menu des outils du planning")
        self.txtOutils.SetToolTipString(u"Cliquez ici pour afficher le menu des outils du planning")
        
        self.boutonAide = wx.StaticBitmap(self, -1, wx.Bitmap("Images/16x16/Aide.png", wx.BITMAP_TYPE_PNG) )
        self.txtAide = wx.StaticText( self, -1, "Aide " )
        self.boutonAide.SetToolTipString(u"Cliquez ici pour afficher l'aide")
        self.txtAide.SetToolTipString(u"Cliquez ici pour afficher l'aide")

        # Bind
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio1, self.radio1 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio2, self.radio2 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio3, self.radio3 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio4, self.radio4 )
        
        self.boutonOutils.Bind(wx.EVT_MOTION, self.OnMotion_Outils)
        self.boutonOutils.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow_Outils)
        self.boutonOutils.Bind(wx.EVT_LEFT_DOWN, self.Menu_Outils)
        self.txtOutils.Bind(wx.EVT_MOTION, self.OnMotion_Outils)
        self.txtOutils.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow_Outils)
        self.txtOutils.Bind(wx.EVT_LEFT_DOWN, self.Menu_Outils)
        
        self.boutonAide.Bind(wx.EVT_MOTION, self.OnMotion_Aide)
        self.boutonAide.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow_Aide)
        self.boutonAide.Bind(wx.EVT_LEFT_DOWN, self.Com_Aide)
        self.txtAide.Bind(wx.EVT_MOTION, self.OnMotion_Aide)
        self.txtAide.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow_Aide)
        self.txtAide.Bind(wx.EVT_LEFT_DOWN, self.Com_Aide)
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.barreTitre, 0, wx.ALL|wx.EXPAND, 0)
        sizer = wx.FlexGridSizer(rows=1, cols=12)
        sizer.Add( self.txtRadio, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 3 )
        sizer.Add( self.radio1, 0, wx.ALL, 3 )
        sizer.Add( self.radio2, 0, wx.ALL, 3 )
        sizer.Add( self.radio3, 0, wx.ALL, 3 )
        sizer.Add( self.radio4, 0, wx.ALL, 3 )
        sizer.Add( (10, 10), 0, wx.ALL, 3 )
##        sizer.Add( self.boutonImprimer, 0, wx.ALL, 2 )
##        sizer.Add( self.txtImprimer, 0, wx.ALL, 3 )
##        sizer.Add( (3, 10), 0, wx.ALL, 3 )
        sizer.Add( self.boutonOutils, 0, wx.ALL, 2 )
        sizer.Add( self.txtOutils, 0, wx.ALL, 3 )
        sizer.Add( (3, 10), 0, wx.ALL, 3 )
        sizer.Add( self.boutonAide, 0, wx.ALL, 2 )
        sizer.Add( self.txtAide, 0, wx.ALL, 3 )
        sizer.AddGrowableCol(5)
        grid_sizer_base.Add(sizer, 0, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        
        
    
    def OnRadio1(self, event):
        global MODE_AFFICHAGE
        MODE_AFFICHAGE = "candidats"
        self.GetGrandParent().GetParent().AfficheListes()

    def OnRadio2(self, event):
        global MODE_AFFICHAGE
        MODE_AFFICHAGE = "candidatures"
        self.GetGrandParent().GetParent().AfficheListes()

    def OnRadio3(self, event):
        global MODE_AFFICHAGE
        MODE_AFFICHAGE = "candidats"
        self.GetGrandParent().GetParent().AfficheListes()

    def OnRadio4(self, event):
        global MODE_AFFICHAGE
        MODE_AFFICHAGE = "candidatures"
        self.GetGrandParent().GetParent().AfficheListes()
        
    def OnMotion_Outils(self, event):
        self.boutonOutils.SetBitmap(wx.Bitmap("Images/16x16/Outils_2.png", wx.BITMAP_TYPE_PNG))
        self.txtOutils.SetForegroundColour(wx.RED)
        self.txtOutils.Refresh()
        event.Skip()

    def OnLeaveWindow_Outils(self, event):
        self.boutonOutils.SetBitmap(wx.Bitmap("Images/16x16/Outils.png", wx.BITMAP_TYPE_PNG))
        self.txtOutils.SetForegroundColour(wx.BLACK)
        self.txtOutils.Refresh()
        event.Skip()

    def OnMotion_Aide(self, event):
        self.boutonAide.SetBitmap(wx.Bitmap("Images/16x16/Aide_2.png", wx.BITMAP_TYPE_PNG))
        self.txtAide.SetForegroundColour(wx.RED)
        self.txtAide.Refresh()
        event.Skip()

    def OnLeaveWindow_Aide(self, event):
        self.boutonAide.SetBitmap(wx.Bitmap("Images/16x16/Aide.png", wx.BITMAP_TYPE_PNG))
        self.txtAide.SetForegroundColour(wx.BLACK)
        self.txtAide.Refresh()
        event.Skip()
    
    def Com_Aide(self, event):
        FonctionsPerso.Aide(1)

    def Menu_Outils(self, event):
        """Ouverture du menu contextuel des options d'affichage du planning """
        
        # Création du menu contextuel
        menu = wx.Menu()
        
        # Commande Imprimer
        IDitem = 10
        item = wx.MenuItem(menu, IDitem, u"Imprimer", u"Imprimer le planning affiché")
        item.SetBitmap(wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_10, id=IDitem)
        
        menu.AppendSeparator()
        
        # Commande Stats simples
        IDitem = 20
        item = wx.MenuItem(menu, IDitem, u"Statistiques", u"Afficher les statistiques des présences")
        item.SetBitmap(wx.Bitmap("Images/16x16/Stats.png", wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_20, id=IDitem)
        
        # Commande Scénarios
        IDitem = 30
        item = wx.MenuItem(menu, IDitem, u"Gestion des scénarios", u"Gestion des scénarios")
        item.SetBitmap(wx.Bitmap("Images/16x16/Scenario.png", wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_30, id=IDitem)
        
        menu.AppendSeparator()
        
        # Sous-menu Options d'affichage
        smOptions = wx.Menu()

        # Affichage des légendes
        IDitem = 210
        smOptions.Append(IDitem, u"Afficher les légendes", u"Affiche ou non les légendes des présences", wx.ITEM_CHECK)
        if hauteurBarre == 26 :
            smOptions.Check(IDitem, True)
        self.Bind(wx.EVT_MENU, self.Menu_210, id=IDitem)
        
        # Affichage des périodes de contrats
        IDitem = 220
        smOptions.Append(IDitem, u"Afficher les périodes de contrats", u"Affiche ou non les périodes des contrats des personnes sélectionnées", wx.ITEM_CHECK)
        if afficher_contrats == True :
            smOptions.Check(IDitem, True)
        self.Bind(wx.EVT_MENU, self.Menu_220, id=IDitem)
        
        menu.AppendMenu(20, u"Options d'affichage", smOptions)
        
        self.PopupMenu(menu)
        menu.Destroy()

    def Menu_10(self, event):
        """ Imprimer le planning """
        self.GetParent().DCplanning.Impression()

    def Menu_20(self, event):
        """ Afficher les stats """
        topWindow = wx.GetApp().GetTopWindow() 
        try : topWindow.SetStatusText(u"Chargement du module des statistiques en cours. Veuillez patientez...")
        except : pass
        panelPresences = self.GetGrandParent().GetParent()
        # Récupération des dates du calendrier
        listeDatesCalendrier = panelPresences.panelCalendrier.GetSelectionDates()
        listeDates = []
        for dateDD in listeDatesCalendrier :
            listeDates.append(str(dateDD))
        # Récupération des personnes de la liste de personnes
        listePersonnes = panelPresences.panelPersonnes.listCtrlPersonnes.GetListePersonnes()
        import Statistiques
        frm = Statistiques.MyFrame(self, listeDates=listeDates, listePersonnes=listePersonnes)
        frm.Show()
        topWindow = wx.GetApp().GetTopWindow() 
        try : topWindow.SetStatusText(u"")
        except : pass

    def Menu_30(self, event):
        """ Gestion des scénarios """
        import Scenario_gestion
        frm = Scenario_gestion.MyFrame(self)
        frm.Show()
        
    def Menu_210(self, event):
        """ Afficher légendes """
        global hauteurBarre, modeTexte
        if hauteurBarre == 26 :
            hauteurBarre = 15
            modeTexte = 1
            etat = False
        else:
            hauteurBarre = 26
            modeTexte = 2
            etat = True
        # MAJ du planning
        self.GetGrandParent().GetParent().MAJpanelPlanning()
        # Mémorisation du paramètre
        FonctionsPerso.Parametres(mode="set", categorie="planning", nom="afficher_legendes", valeur=etat)

    def Menu_220(self, event):
        """ Afficher contrats """
        global afficher_contrats
        if afficher_contrats == True :
            afficher_contrats = False
        else:
            afficher_contrats = True
        # MAJ du planning
        self.GetGrandParent().GetParent().MAJpanelPlanning()
        # Mémorisation du paramètre
        FonctionsPerso.Parametres(mode="set", categorie="planning", nom="afficher_contrats", valeur=afficher_contrats)





# --------------------------------------------------------------------------------------------------------------------------------------------------------------------



class ToolBar(wx.ToolBar):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.TB_FLAT|wx.TB_TEXT
        wx.ToolBar.__init__(self, *args, **kwds)
        self.SetToolBitmapSize((22, 22))
        self.AddLabelTool(10, u"Candidats", wx.Bitmap("Images/22x22/Candidats.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_RADIO, u"Afficher la liste des candidats", "")
        self.AddLabelTool(20, u"Candidatures", wx.Bitmap("Images/22x22/Candidatures.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_RADIO, u"Afficher la liste des candidatures", "")
        self.AddLabelTool(30, u"Entretiens", wx.Bitmap("Images/22x22/Entretiens.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_RADIO, u"Afficher la liste des entretiens", "")
        self.AddLabelTool(40, u"Offres d'emploi", wx.Bitmap("Images/22x22/Apercu.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_RADIO, u"Afficher les offres d'emploi et les candidatures associées", "")
        self.AddSeparator()
        self.AddLabelTool(50, u"Rechercher", wx.Bitmap("Images/22x22/Loupe.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, u"Filtrer la liste", "")
##        self.AddLabelTool(60, u"Outils", wx.Bitmap("Images/22x22/Outils.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, u"Outils", "")
        self.AddSeparator()
        self.AddLabelTool(70, u"Aide", wx.Bitmap("Images/22x22/button_help.png", wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, u"Aide", "")
        self.Realize()

        self.Bind(wx.EVT_TOOL, self.ModeAffichage, id=10)
        self.Bind(wx.EVT_TOOL, self.ModeAffichage, id=20)
        self.Bind(wx.EVT_TOOL, self.ModeAffichage, id=30)
        self.Bind(wx.EVT_TOOL, self.ModeAffichage, id=40)
        self.Bind(wx.EVT_TOOL, self.Rechercher, id=50)
        self.Bind(wx.EVT_TOOL, self.Aide, id=70)
        
    def ModeAffichage(self, event):
        global MODE_AFFICHAGE
        if event.GetId() == 10 : MODE_AFFICHAGE = "candidats"
        if event.GetId() == 20 : MODE_AFFICHAGE = "candidatures"
        if event.GetId() == 30 : MODE_AFFICHAGE = "entretiens"
        if event.GetId() == 40 : MODE_AFFICHAGE = "emplois"
        self.GetGrandParent().GetParent().AfficheListes()
        self.GetGrandParent().GetParent().AffichePanelResume(False)

    def Rechercher(self, event):
        self.GetGrandParent().GetParent().OnBoutonRechercher(None)
    
    def Aide(self, event):
        self.GetGrandParent().GetParent().OnBoutonAide(None)
        
        

class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, name="Recrutement")
        self.parent = parent
        self.init = False 

    def InitPage(self):               
        self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_3D | wx.SP_NO_XP_THEME | wx.SP_LIVE_UPDATE)
        self.window_D = wx.Panel(self.splitter, -1)
        
        # Panel Etat des dossiers
        self.window_G = MultiSplitterWindow(self.splitter, -1, style= wx.SP_NOSASH | wx.SP_LIVE_UPDATE)
        self.window_G.SetOrientation(wx.VERTICAL)
        self.window_G.SetMinimumPaneSize(100)
        self.gadget_entretiens = GadgetEntretiens(self.window_G)
        self.gadget_informations = GadgetInformations(self.window_G)
##        self.gadget_avertissement = GadgetAvertissement(self.window_G)
        self.window_G.AppendWindow(self.gadget_entretiens, 180) # Ici c'est la hauteur du panel pb de dossiers
        self.window_G.AppendWindow(self.gadget_informations, 300) # Ici c'est la hauteur du panel pb de dossiers
##        self.window_G.AppendWindow(self.gadget_avertissement, 100) # Ici c'est la hauteur du panel pb de dossiers
        
        # Panel vide
        self.panel_vide = wx.Panel(self.window_G, -1)
        self.panel_vide.SetBackgroundColour((122, 161, 230))
        self.window_G.AppendWindow(self.panel_vide, 200)
        
        # Barre ToolBar
        self.barreOutils = ToolBar(self.window_D)
        
##        self.panel_affichage = BarreAffichage(self.window_D)
        self.panel_resume = PanelResume(self.window_D)
        self.label_selection = wx.StaticText(self.window_D, -1, u"", size=((-1, 25)))
        self.label_selection.SetForegroundColour((122, 161, 230))
        self.label_selection.Show(False)
        self.listCtrl_candidats = OL_candidats.ListView(self.window_D, id=-1,  name="OL_candidats", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.listCtrl_candidatures = OL_candidatures.ListView(self.window_D, id=-1,  name="OL_candidatures", modeAffichage = "avec_nom", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)       
        self.listCtrl_entretiens = OL_entretiens.ListView(self.window_D, id=-1,  name="OL_entretiens", modeAffichage="avec_nom", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.listCtrl_emplois = OL_emplois.ListView(self.window_D, id=-1,  name="OL_emplois", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.barreRecherche = BarreRecherche(self.window_D)
        
        self.listCtrl_candidats.SetMinSize((20, 20))
        self.listCtrl_candidatures.SetMinSize((20, 20))
        self.listCtrl_entretiens.SetMinSize((20, 20))
        self.listCtrl_emplois.SetMinSize((20, 20))
        
        self.bouton_ajouter = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_rechercher = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Loupe.png", wx.BITMAP_TYPE_ANY))
        self.bouton_affichertout = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Actualiser.png", wx.BITMAP_TYPE_ANY))
        self.bouton_options = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        self.bouton_courrier = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Mail.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        self.bouton_export_texte = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Document.png", wx.BITMAP_TYPE_ANY))
        self.bouton_export_excel = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_ANY))
        self.bouton_aide = wx.BitmapButton(self.window_D, -1, wx.Bitmap("Images/16x16/Aide.png", wx.BITMAP_TYPE_ANY))
        
        self.barreTitre_liste = FonctionsPerso.BarreTitre(self.window_D,  u"Liste des candidats", u"Liste des candidats")
        
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
        self.AfficheListes()
        
##        self.splitter.SetSashPosition(250, True)
        
    def __set_properties(self):
        self.barreRecherche.SetToolTipString(u"Saisissez ici un nom, un prénom, un nom de ville, etc... pour retrouver un candidat dans la liste.")
        self.bouton_ajouter.SetToolTipString(u"Cliquez ici pour créer une nouvelle fiche individuelle")
        self.bouton_modifier.SetToolTipString(u"Cliquez ici pour modifier la fiche sélectionnée dans la liste\n(Vous pouvez également double-cliquer sur une ligne)")
        self.bouton_supprimer.SetToolTipString(u"Cliquez ici pour supprimer la fiche sélectionnée dans la liste")
        self.bouton_affichertout.SetToolTipString(u"Cliquez ici pour réafficher toute la liste")
        self.bouton_options.SetToolTipString(u"Cliquez ici pour afficher les options de la liste")
        self.bouton_courrier.SetToolTipString(u"Cliquez ici créer un courrier ou un Email par publipostage")
        self.bouton_imprimer.SetToolTipString(u"Cliquez ici pour imprimer la liste")
        self.bouton_export_texte.SetToolTipString(u"Cliquez ici pour exporter la liste au format texte")
        self.bouton_export_excel.SetToolTipString(u"Cliquez ici pour exporter la liste au format Excel")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")


    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_D = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_D = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        grid_sizer_liste = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_liste2 = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=14, cols=1, vgap=5, hgap=5)
        
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
##        grid_sizer_D.Add(self.barreOutils, 1, wx.EXPAND, 0)
        grid_sizer_D.Add(self.barreTitre_liste, 1, wx.EXPAND, 0)
        grid_sizer_D.Add(self.barreOutils, 1, wx.EXPAND, 0)
        grid_sizer_D.Add(self.label_selection, 1, wx.EXPAND|wx.ALL, 4)
        
        # Liste des personnes
        grid_sizer_liste2.Add(self.listCtrl_candidats, 1, wx.EXPAND, 0)
        grid_sizer_liste2.Add(self.listCtrl_candidatures, 1, wx.EXPAND, 0)
        grid_sizer_liste2.Add(self.listCtrl_entretiens, 1, wx.EXPAND, 0)
        grid_sizer_liste2.Add(self.listCtrl_emplois, 1, wx.EXPAND, 0)
        grid_sizer_liste2.Add(self.barreRecherche, 0, wx.EXPAND, 0)
        grid_sizer_liste2.AddGrowableRow(0)
        grid_sizer_liste2.AddGrowableRow(1)
        grid_sizer_liste2.AddGrowableRow(2)
        grid_sizer_liste2.AddGrowableRow(3)
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
        
        # Barre des options
##        grid_sizer_D.Add(self.panel_affichage, 1, wx.EXPAND, 0)
        
        grid_sizer_D.AddGrowableRow(3)
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
        exec("self.listCtrl_%s.Ajouter()" % MODE_AFFICHAGE)
        
    def OnBoutonModifier(self, event):
        exec("self.listCtrl_%s.Modifier()" % MODE_AFFICHAGE)
        
    def OnBoutonSupprimer(self, event):
        exec("self.listCtrl_%s.Supprimer()" % MODE_AFFICHAGE)

    def OnBoutonRechercher(self, event):
        exec("self.listCtrl_%s.Rechercher()" % MODE_AFFICHAGE)

    def OnBoutonAfficherTout(self, event):
        exec("self.listCtrl_%s.AfficherTout()" % MODE_AFFICHAGE)
        self.AfficheLabelSelection(etat=False)   
        
    def OnBoutonOptions(self, event):
        exec("self.listCtrl_%s.Options()" % MODE_AFFICHAGE)
        
    def OnBoutonAide(self, event):
##        FonctionsPerso.Aide(12)
        dlg = wx.MessageDialog(self, u"L'aide du module Recrutement est en cours de rédaction.\nElle sera disponible lors d'une mise à jour ultérieure.", "Aide indisponible", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
    def AffichePanelResume(self, etat=True):
        """ Affiche ou fait disparaître le panel Résumé """
        if etat == True and self.panel_resume.IsShown() == True: 
            return
        self.panel_resume.Show(etat)
        self.grid_sizer_D.Layout()
        self.Refresh()
    
    def AfficheLabelSelection(self, etat=True):
        """ Affiche ou fait disparaître le label Sélection en cours de la liste en cours """
        if etat==True and self.label_selection.IsShown()==True: 
            return
        self.label_selection.Show(etat)
        self.grid_sizer_D.Layout()
        self.Refresh()
    
    def AfficheListes(self):
        # Candidats
        if MODE_AFFICHAGE == "candidats" :
            self.listCtrl_candidats.Show(True)
            self.barreRecherche.Show(True)
            self.barreTitre_liste.barreTitre.SetLabel(u"Liste des candidats")
            self.bouton_courrier.Show(True)
            self.bouton_ajouter.SetToolTipString(u"Cliquez ici pour créer un nouveau candidat")
            self.bouton_modifier.SetToolTipString(u"Cliquez ici pour modifier le candidat sélectionné dans la liste\n(Vous pouvez également double-cliquer sur une ligne)")
            self.bouton_supprimer.SetToolTipString(u"Cliquez ici pour supprimer le candidat sélectionné dans la liste")
        else:
            self.listCtrl_candidats.Show(False)
            self.barreRecherche.Show(False)
        # Candidatures
        if MODE_AFFICHAGE == "candidatures" :
            self.listCtrl_candidatures.Show(True)
            self.barreTitre_liste.barreTitre.SetLabel(u"Liste des candidatures")
            self.bouton_courrier.Show(True)
            self.bouton_ajouter.SetToolTipString(u"Cliquez ici pour créer une nouvelle candidature")
            self.bouton_modifier.SetToolTipString(u"Cliquez ici pour modifier la candidature sélectionnée dans la liste\n(Vous pouvez également double-cliquer sur une ligne)")
            self.bouton_supprimer.SetToolTipString(u"Cliquez ici pour supprimer la candidature sélectionnée dans la liste")
        else:
            self.listCtrl_candidatures.Show(False)
        # Entretiens
        if MODE_AFFICHAGE == "entretiens" :
            self.listCtrl_entretiens.Show(True)
            self.barreTitre_liste.barreTitre.SetLabel(u"Liste des entretiens")
            self.bouton_courrier.Show(False)
            self.bouton_ajouter.SetToolTipString(u"Cliquez ici pour créer un nouvel entretien")
            self.bouton_modifier.SetToolTipString(u"Cliquez ici pour modifier l'entretien sélectionné dans la liste\n(Vous pouvez également double-cliquer sur une ligne)")
            self.bouton_supprimer.SetToolTipString(u"Cliquez ici pour supprimer l'entretien sélectionné dans la liste")
        else:
            self.listCtrl_entretiens.Show(False)
        # Offres d'emploi
        if MODE_AFFICHAGE == "emplois" :
            self.listCtrl_emplois.Show(True)
            self.barreTitre_liste.barreTitre.SetLabel(u"Liste des offres d'emploi")
            self.bouton_courrier.Show(False)
            self.bouton_ajouter.SetToolTipString(u"Cliquez ici pour créer une nouvelle offre d'emploi")
            self.bouton_modifier.SetToolTipString(u"Cliquez ici pour modifier l'offre d'emploi sélectionnée dans la liste\n(Vous pouvez également double-cliquer sur une ligne)")
            self.bouton_supprimer.SetToolTipString(u"Cliquez ici pour supprimer l'offre d'emploi sélectionnée dans la liste")
        else:
            self.listCtrl_emplois.Show(False)
        # Refresh
        self.grid_sizer_D.Layout()
        self.Refresh()
        # Refresh ListView
        exec("self.listCtrl_%s.MAJ()" % MODE_AFFICHAGE)
        
    def MAJpanel(self, listeElements=[], MAJpanelResume=True) :
        """ Met à jour les éléments du panel personnes """
        # Elements possibles : [] pour tout, listCtrl_personnes
        if self.init == False :
            self.InitPage()
        
        if self.listCtrl_candidats.IsShown() : self.listCtrl_candidats.MAJ()
        if self.listCtrl_candidatures.IsShown() : self.listCtrl_candidatures.MAJ()
        if self.listCtrl_entretiens.IsShown() : self.listCtrl_entretiens.MAJ()
        if self.listCtrl_emplois.IsShown() : self.listCtrl_emplois.MAJ()
        self.gadget_entretiens.MAJ()
        self.gadget_informations.MAJ()
        
        if MAJpanelResume == True :
            self.AffichePanelResume(False)
    
    def MAJapresVerrouillage(self, OL_gadget=False, OL_principal=False, OL_resume=False):
        """ Met les OL entretiens à jour après verrouillage ou deverrouillage """
        if OL_gadget == True :
            self.gadget_entretiens.MAJ()
        if OL_principal == True :
            if self.listCtrl_entretiens.IsShown() : 
                self.listCtrl_entretiens.MAJ()
        if OL_resume == True :
            if self.panel_resume.noteBook.GetPageCount() > 1 :
                if self.panel_resume.listCtrl_entretiens.IsShown() :
                    self.panel_resume.listCtrl_entretiens.MAJ()
    
    def OnBoutonCourrier(self, event):
        exec("self.listCtrl_%s.CourrierPublipostage(mode='multiple')" % MODE_AFFICHAGE)
        
    def OnBoutonImprimer(self, event):
        exec("self.listCtrl_%s.Imprimer()" % MODE_AFFICHAGE)
        
    def OnBoutonExportTexte(self, event):
        exec("self.listCtrl_%s.ExportTexte()" % MODE_AFFICHAGE)
        
    def OnBoutonExportExcel(self, event):
        exec("self.listCtrl_%s.ExportExcel()" % MODE_AFFICHAGE)


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,-1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent

        self.SetDescriptiveText(u"Rechercher une personne dans la liste")
        self.ShowSearchButton(True)
        
        self.listView = self.GetParent().GetGrandParent().listCtrl_candidats
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
        panel = Panel(self)
        panel.InitPage()
        panel.MAJpanel() 
        self.SetTitle(u"Panel Recrutement")
        self.SetSize((800, 690))
        self.Centre()



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
