#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import datetime
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
import operator
import FonctionsPerso
import os
import sys
from Dlg import DLG_Saisie_emploi
from Utils import UTILS_Fichiers
from ObjectListView import ObjectListView, ColumnDefn


NOMS_CANDIDATS = {}
DICT_CANDIDATURES = {}

# Liste sans nom du candidat
LISTE_COLONNES_1 = [
            [_(u"ID"), "left", 0, "IDemploi", "", _(u"ID de l'offre d'emploi"), True, 1 ],
            [_(u"Lancement"), "left", 100, "date_debut", "date", _(u"Date de lancement du recrutement"), True, 2 ],
            [_(u"Clôture"), "left", 70, "date_fin", "date", _(u"Date de clôture du recrutement"), True, 3 ],
            [_(u"Intitulé"), "left", 300, _(u"intitule"), "", _(u"Intitulé de l'offre d'emploi"), True, 4 ],
            [_(u"Candidatures"), "left", 80, "nbre_candidatures", "", _(u"Nombre de candidatures rattachées"), True, 5 ],
            [_(u"Détail"), "left", 400, "detail", "", _(u"Détail de l'offre d'emploi"), True, 6 ],
            ] # nom Colonne, alignement, largeur, nom Champ, Args pour OLV, Description, Affiché ?, Ordre


# Importation de données pour les filtres spéciaux

def Importation_disponibilites():
    # Récupération des données
    DB = GestionDB.DB()        
    req = """SELECT IDdisponibilite, IDemploi, date_debut, date_fin
    FROM emplois_dispo; """
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    # Transforme liste en dict
    DICT_DISPONIBILITES = {}
    for IDdisponibilite, IDemploi, date_debut, date_fin in listeDonnees :
        date_debut = datetime.date(year=int(date_debut[:4]), month=int(date_debut[5:7]), day=int(date_debut[8:10]))
        date_fin = datetime.date(year=int(date_fin[:4]), month=int(date_fin[5:7]), day=int(date_fin[8:10]))
        if DICT_DISPONIBILITES.has_key(IDemploi) :
            DICT_DISPONIBILITES[IDemploi].append((IDdisponibilite, date_debut, date_fin))
        else:
            DICT_DISPONIBILITES[IDemploi] = [(IDdisponibilite, date_debut, date_fin),]
    return DICT_DISPONIBILITES

def Importation_emplois_fonctions():
    # Récupération des données
    DB = GestionDB.DB()        
    req = """SELECT IDemploi_fonction, IDemploi, IDfonction
    FROM emplois_fonctions; """
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    # Transforme liste en dict
    DICT_EMPLOIS_FONCTIONS = {}
    for IDemploi_fonction, IDemploi, IDfonction in listeDonnees :
        if DICT_EMPLOIS_FONCTIONS.has_key(IDemploi) :
            DICT_EMPLOIS_FONCTIONS[IDemploi].append(IDfonction)
        else:
            DICT_EMPLOIS_FONCTIONS[IDemploi] = [IDfonction,]
    return DICT_EMPLOIS_FONCTIONS

def Importation_emplois_affectations():
    # Récupération des données
    DB = GestionDB.DB()        
    req = """SELECT IDemploi_affectation, IDemploi, IDaffectation
    FROM emplois_affectations; """
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    # Transforme liste en dict
    DICT_EMPLOIS_AFFECTATIONS = {}
    for IDemploi_affectation, IDemploi, IDaffectation in listeDonnees :
        if DICT_EMPLOIS_AFFECTATIONS.has_key(IDemploi) :
            DICT_EMPLOIS_AFFECTATIONS[IDemploi].append(IDaffectation)
        else:
            DICT_EMPLOIS_AFFECTATIONS[IDemploi] = [IDaffectation,]
    return DICT_EMPLOIS_AFFECTATIONS

def Importation_diffuseurs():
    # Récupération des données
    DB = GestionDB.DB()        
    req = """SELECT IDemploi_diffuseur, IDemploi, IDdiffuseur
    FROM emplois_diffuseurs; """
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close()
    # Transforme liste en dict
    DICT_DIFFUSEURS = {}
    for IDemploi_diffuseur, IDemploi, IDdiffuseur in listeDonnees :
        if DICT_DIFFUSEURS.has_key(IDemploi) :
            DICT_DIFFUSEURS[IDemploi].append(IDdiffuseur)
        else:
            DICT_DIFFUSEURS[IDemploi] = [IDdiffuseur,]
    return DICT_DIFFUSEURS                



# ---------------------------------------- LISTVIEW   -----------------------------------------------------------------------

class Track(object):
    def __init__(self, donnees):
        self.IDemploi = donnees[0]
        self.date_debut = donnees[1]
        self.date_fin = donnees[2]
        self.intitule = donnees[3]
        self.detail = donnees[4]
        # Nbre candidatures rattachées
        if DICT_CANDIDATURES.has_key(self.IDemploi) :
            self.nbre_candidatures = DICT_CANDIDATURES[self.IDemploi]
        else:
            self.nbre_candidatures = 0
    
    
class ListView(ObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.selectionID = None
        self.selectionTrack = None
        self.presents = False
        self.criteres = ""
        self.listeFiltres = []
        self.itemSelected = False
        # Initialisation du listCtrl
        ObjectListView.__init__(self, *args, **kwds)
        self.listeColonnes = LISTE_COLONNES_1
        self.listeColonnesOriginale = list(self.listeColonnes)
##        self.InitModel()
##        self.InitObjectListView()
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        
    def OnItemActivated(self,event):
        self.Modifier()
        
    def OnItemSelected(self, event):
        self.itemSelected = True
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                self.GetGrandParent().GetParent().bouton_modifier.Enable(True)
                self.GetGrandParent().GetParent().bouton_supprimer.Enable(True)
                if len(self.Selection()) == 0:
                    return False
                IDemploi = self.Selection()[0].IDemploi
                # Met à jour le cadre Résumé
                self.GetGrandParent().GetParent().panel_resume.MAJ(IDemploi=IDemploi)
                self.GetGrandParent().GetParent().AffichePanelResume(True)
        except : 
            pass
        
    def OnItemDeselected(self, event):
        self.itemSelected = False
        wx.FutureCall(100, self.DeselectionneItem)
    
    def DeselectionneItem(self) :
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                if self.itemSelected == False :
                    self.GetGrandParent().GetParent().bouton_modifier.Enable(False)
                    self.GetGrandParent().GetParent().bouton_supprimer.Enable(False)
                    self.GetGrandParent().GetParent().AffichePanelResume(False)
        except : 
            pass
        self.itemSelected = False
            
    def InitModel(self):
        self.Importation_candidatures()
        self.donnees = self.GetTracks()

    def GetListeFiltres(self, listeFiltres=[]):
                
        # ------------------------------------------------------------------------------------------------------------------------
        
        def GetListeDisponibilites(dictFiltres):
            """ Recherche des disponibilités """
            listeTemp = []
            for IDemploi, disponibilites in Importation_disponibilites().iteritems() :
                for IDdisponibilite, date_debut, date_fin in disponibilites :
                    if date_fin>=dictFiltres["valeur"][0] and date_debut<=dictFiltres["valeur"][1] :
                        listeTemp.append(IDemploi)
            return listeTemp
        
        def GetListeFonctions(dictFiltres):
            """ Recherche des fonctions """
            listeTemp = []
            for IDemploi, listeFonctions in Importation_emplois_fonctions().iteritems() :
                for ID, label in dictFiltres["valeur"] :
                    if ID in listeFonctions :
                        if IDemploi not in listeTemp :
                            listeTemp.append(IDemploi)
            return listeTemp
        
        def GetListeAffectations(dictFiltres):
            """ Recherche des affectations """
            listeTemp = []
            for IDemploi, listeAffectations in Importation_emplois_affectations().iteritems() :
                for ID, label in dictFiltres["valeur"] :
                    if ID in listeAffectations :
                        if IDemploi not in listeTemp :
                            listeTemp.append(IDemploi)
            return listeTemp
        
        def GetListeDiffuseurs(dictFiltres):
            """ Recherche des diffuseurs """
            listeTemp = []
            for IDemploi, listeDiffuseurs in Importation_diffuseurs().iteritems() :
                for ID, label in dictFiltres["valeur"] :
                    if ID in listeDiffuseurs :
                        if IDemploi not in listeTemp :
                            listeTemp.append(IDemploi)
            return listeTemp
        
        # ------------------------------------------------------------------------------------------------------------------------
        nbreFiltres = 0
        criteresSQL = ""
        listeListes = []
        for dictFiltres in listeFiltres :
            
            if dictFiltres["nomControle"] == "emplois_dispo" : 
                listeListes.append(GetListeDisponibilites(dictFiltres))
            elif dictFiltres["nomControle"] == "emplois_fonctions" : 
                listeListes.append(GetListeFonctions(dictFiltres))
            elif dictFiltres["nomControle"] == "emplois_affectations" : 
                listeListes.append(GetListeAffectations(dictFiltres))
            elif dictFiltres["nomControle"] == "emplois_diffuseurs" : 
                listeListes.append(GetListeDiffuseurs(dictFiltres))
            else:
                criteresSQL += dictFiltres["sql"] + " AND "
                nbreFiltres += 1
                
        # Recherche des ID communs aux listes
        nbreListes = len(listeListes)
        if nbreListes == 0 :
            listeID = None
        elif nbreListes == 1 :
            listeID = listeListes[0]
        else :
            # Si plusieurs listes 
            texteFonction = ""
            index = 0
##            for liste in listeListes :
##                texteFonction += "set(listeListes[%d]) & " % index
##                index += 1
##            texteFonction = texteFonction[:-3]
##            exec("listeID=%s" % texteFonction)
            listeID = listeListes[0]
            for liste in listeListes[1:] :
                listeID = set(listeID) & set(liste)
            listeID = list(listeID)
            
        # Traitement des requetes SQL
        if nbreFiltres > 0 :
            criteresSQL = criteresSQL[:-5]

        return listeID, criteresSQL


    def GetTracks(self):
        """ Récupération des données """
        # Critères
        listeID = None
        self.criteres = ""
        # Liste de filtres
        if len(self.listeFiltres) > 0 :
            listeID, criteres = self.GetListeFiltres(self.listeFiltres)
            if criteres != "" :
                if self.criteres == "" :
                    self.criteres = "WHERE " + criteres
                else:
                    self.criteres += " AND " + criteres
                    
        DB = GestionDB.DB()
        req = """SELECT IDemploi, date_debut, date_fin, intitule, detail 
        FROM emplois %s ORDER BY date_debut; """ % self.criteres
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeListeView = []
        for item in listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
    
    def Importation_candidatures(self):
        # Recherche le nombre de candidatures attachées
        DB = GestionDB.DB()
        req = """SELECT IDcandidature, Count(IDemploi) AS CompteDeIDemploi
        FROM candidatures 
        GROUP BY IDemploi;
        """
        DB.ExecuterReq(req)
        listeNbTitulaires = DB.ResultatReq()
        DB.Close()
        # Transformation en dictionnaire
        global DICT_CANDIDATURES
        DICT_CANDIDATURES = {}
        for IDemploi, nbrePersonne in listeNbTitulaires :
            DICT_CANDIDATURES[IDemploi] = nbrePersonne
        return dict
    
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#EEF4FB" # wx.Colour(255, 255, 255) #"#EEF4FB" # Bleu
        self.evenRowsBackColor = wx.Colour(255, 255, 255) #"#F0FBED" # Vert
        self.useExpansionColumn = True
                
        # Formatage des données
        def FormateDate(dateStr):
            if dateStr == "" or dateStr == None : return ""
            date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text        
        
        # Création des colonnes
        liste_ColonnesTmp = self.listeColonnes
        # Tri par ordre
        liste_ColonnesTmp.sort(key=operator.itemgetter(7))
        
        liste_Colonnes = []
        for labelCol, alignement, largeur, nomChamp, args, description, affiche, ordre in liste_ColonnesTmp :
            if affiche == True :
                if args == "date" :
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp, stringConverter=FormateDate)
                else:
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp)
                liste_Colonnes.append(colonne)
        
        self.SetColumns(liste_Colonnes)

        self.SetSortColumn(self.columns[1])
        self.SetEmptyListMsg(_(u"Aucune offre d'emploi"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetObjects(self.donnees)
       
    def MAJ(self, IDemploi=None, presents=None):
        if IDemploi != None :
            self.selectionID = IDemploi
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        if presents != None :
            self.presents = presents
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if self.selectionTrack != None :
            self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
        self.selectionID = None
        self.selectionTrack = None
        self.SetLabelSelection() 
    
    def Selection(self):
        return self.GetSelectedObjects()
    
    def SetListeColonnes(self, listeColonnes):
        self.listeColonnes = listeColonnes


# --------------------------------------------------------------------------------------------------------------------------------------------------



    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDemploi
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()
        
        # Item Rechercher
        item = wx.MenuItem(menuPop, 80, _(u"Rechercher"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Rechercher, id=80)

        # Item Afficher tout
        item = wx.MenuItem(menuPop, 50, _(u"Afficher tout"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_AfficherTout, id=50)
        
        # Item Options
        item = wx.MenuItem(menuPop, 60, _(u"Options de liste"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Options, id=60)
        
        menuPop.AppendSeparator()
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 90, _(u"Imprimer la liste"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuImprimer, id=90)
        
        # Item Export Texte
        item = wx.MenuItem(menuPop, 100, _(u"Exporter la liste au format Texte"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuExportTexte, id=100)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 110, _(u"Exporter la liste au format Excel"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuExportExcel, id=110)
        
        menuPop.AppendSeparator()

        # Item Aide
        item = wx.MenuItem(menuPop, 70, _(u"Aide"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Aide.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Aide, id=70)
                
        self.PopupMenu(menuPop)
        menuPop.Destroy()


    def Menu_Ajouter(self, event):
        self.Ajouter()
        
    def Menu_Modifier(self, event):
        self.Modifier()
        return

    def Menu_Supprimer(self, event):
        self.Supprimer()
    
    def Menu_Rechercher(self, event):
        self.Rechercher()
        
    def Menu_AfficherTout(self, event):
        self.AfficherTout()
        
    def Menu_Options(self, event):
        self.Options()

    def Menu_Aide(self, event):
##        self.GetGrandParent().GetParent().OnBoutonAide(None)
        dlg = wx.MessageDialog(self, _(u"L'aide du module Recrutement est en cours de rédaction.\nElle sera disponible lors d'une mise à jour ultérieure."), "Aide indisponible", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
    def Menu_Mail(self, event):
        FonctionsPerso.EnvoyerMail(adresses = (self.adresseMail,))

    def AfficherTout(self):
        """ Réafficher toute la liste """
        self.criteres = ""
        self.listeFiltres = []
        self.MAJ()
            
    def Options(self):
        """ Choix et ordre des colonnes """
        from Dlg import DLG_Config_liste_personnes
        frm = DLG_Config_liste_personnes.MyFrame(self, self.listeColonnes)
        frm.Show()

    def MenuImprimer(self, event):
        self.Imprimer()
        
    def MenuExportTexte(self, event):
        self.ExportTexte()
        
    def MenuExportExcel(self, event):
        self.ExportExcel()

    def Rechercher(self):
        # Récupération des filtres souhaités
        from Dlg import DLG_Filtre_recrutement
        dlg = DLG_Filtre_recrutement.MyDialog(self, categorie="emplois", listeValeursDefaut=self.listeFiltres, title=_(u"Sélection de filtres de liste"))
        if dlg.ShowModal() == wx.ID_OK:
            listeFiltres = dlg.GetListeFiltres()
            dlg.Destroy()
            # Application des filtres
            self.listeFiltres = listeFiltres
            self.MAJ()
        else:
            dlg.Destroy()

    def SetLabelSelection(self):
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                if len(self.listeFiltres) > 0 :
                    texte = _(u"Filtres de sélection : ")
                    for dictFiltre in self.listeFiltres :
                        texte += u"%s (%s), " % (dictFiltre["labelControle"], dictFiltre["label"])
                    texte = texte[:-2]
                    self.GetGrandParent().GetParent().AfficheLabelSelection(True)
                    self.GetGrandParent().GetParent().label_selection.SetLabel(texte)
                else:
                    self.GetGrandParent().GetParent().AfficheLabelSelection(False)
                    self.GetGrandParent().GetParent().label_selection.SetLabel("")
        except : 
            pass
            
    def Ajouter(self):
        
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                self.GetGrandParent().GetParent().AffichePanelResume(False)
        except : 
            pass
            
        frm = DLG_Saisie_emploi.MyFrame(self, IDemploi=None)
        frm.Show()

    def Modifier(self):
        
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                self.GetGrandParent().GetParent().AffichePanelResume(False)
        except : 
            pass
            
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une offre d'emploi à modifier dans la liste"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDemploi = self.Selection()[0].IDemploi
        frm = DLG_Saisie_emploi.MyFrame(self, IDemploi=IDemploi)
        frm.Show()

    def Supprimer(self):
        
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                self.GetGrandParent().GetParent().AffichePanelResume(False)
        except : 
            pass
            
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un entretien à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        ID = self.Selection()[0].IDemploi
        nom = self.Selection()[0].intitule

        # Vérifie que cette offre d'emploi n'est pas attribuée à une candidature
        DB = GestionDB.DB()
        req = "SELECT IDcandidature FROM candidatures WHERE IDemploi=%d;" % ID
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) != 0 :
            dlg = wx.MessageDialog(self, _(u"Vous avez déjà enregistré ") + str(len(listeDonnees)) + _(u" candidature(s) rattachée(s) à cette offre d'emploi. \nVous ne pouvez donc pas la supprimer."), "Information", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation
        txtMessage = unicode((_(u"Voulez-vous vraiment supprimer cette offre d'emploi ? \n\n> ") + nom))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Suppression du type de pièce
        DB = GestionDB.DB()
        DB.ReqDEL("emplois", "IDemploi", ID)
        DB.ReqDEL("emplois_dispo", "IDemploi", ID)
        DB.ReqDEL("emplois_fonctions", "IDemploi", ID)
        DB.ReqDEL("emplois_affectations", "IDemploi", ID) 
        DB.ReqDEL("emplois_diffuseurs", "IDemploi", ID)

        # MàJ
        self.MAJ()
    
    def GetValeurs(self):
        """ Récupère les valeurs affichées sous forme de liste """
        # Récupère les labels de colonnes
        liste_ColonnesTmp = self.listeColonnes
        liste_ColonnesTmp.sort(key=operator.itemgetter(7))
        liste_labelsColonnes = []
        for labelCol, alignement, largeur, nomChamp, args, description, affiche, ordre in liste_ColonnesTmp :
            if affiche == True :
                liste_labelsColonnes.append( (labelCol, alignement, largeur, nomChamp) )

        # Récupère les valeurs
        listeValeurs = []
        listeObjects = self.GetFilteredObjects()
        for object in listeObjects :
            valeursLigne = []
            for indexCol in range(0, self.GetColumnCount() ) :
                valeur = self.GetStringValueAt(object, indexCol)
                valeursLigne.append(valeur)
            listeValeurs.append(valeursLigne)
        
        return liste_labelsColonnes, listeValeurs
    
    def GetNbreItems(self):
        return len(self.donnees)
        
    def ExportTexte(self):
        """ Export de la liste au format texte """
        if self.GetNbreItems() == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune personne dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Récupération des valeurs
        liste_labelsColonnes, listeValeurs = self.GetValeurs()
        
        # Selection des lignes
        from Dlg import DLG_Selection_liste
        dlg = DLG_Selection_liste.MyFrame(self, liste_labelsColonnes, listeValeurs, type="exportTexte")
        if dlg.ShowModal() == wx.ID_OK:
            listeSelections = dlg.GetSelections()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        
        nomFichier = "ExportTexte.txt"
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        wildcard = "Fichier texte (*.txt)|*.txt|" \
                        "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            self, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut, 
            defaultFile = nomFichier, 
            wildcard = wildcard, 
            style = wx.SAVE
            )
        dlg.SetFilterIndex(2)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # Le fichier de destination existe déjà :
        if os.path.isfile(cheminFichier) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()

        # Création du fichier texte
        texte = ""
        separateur = ";"
        for labelCol, alignement, largeur, nomChamp in liste_labelsColonnes :
            texte += nomChamp + separateur
        texte = texte[:-1] + "\n"

        for valeurs in listeValeurs :
            if int(valeurs[0]) in listeSelections :
                for valeur in valeurs :
                    texte += valeur + separateur
                texte = texte[:-1] + "\n"
        
        # Elimination du dernier saut à la ligne
        texte = texte[:-1]

        # Création du fichier texte
        f = open(cheminFichier, "w")
        f.write(texte.encode("iso-8859-15"))
        f.close()
        
        # Confirmation de création du fichier et demande d'ouverture directe dans Excel
        txtMessage = _(u"Le fichier Texte a été créé avec succès. Souhaitez-vous l'ouvrir dès maintenant ?")
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)
            
            
    def ExportExcel(self):
        """ Export de la liste au format Excel """
        if "linux" in sys.platform :
            dlg = wx.MessageDialog(self, _(u"Désolé, cette fonction n'est pas disponible dans la version LINUX de Teamworks."), "Fonction indisponible", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if self.GetNbreItems() == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune personne dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Récupération des valeurs
        liste_labelsColonnes, listeValeurs = self.GetValeurs()
        
        # Selection des lignes
        from Dlg import DLG_Selection_liste
        dlg = DLG_Selection_liste.MyFrame(self, liste_labelsColonnes, listeValeurs, type="exportExcel")
        if dlg.ShowModal() == wx.ID_OK:
            listeSelections = dlg.GetSelections()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        
        nomFichier = "ExportExcel.xls"
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        wildcard = "Fichier Excel (*.xls)|*.xls|" \
                        "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            self, message = _(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"), defaultDir=cheminDefaut, 
            defaultFile = nomFichier, 
            wildcard = wildcard, 
            style = wx.SAVE
            )
        dlg.SetFilterIndex(2)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # Le fichier de destination existe déjà :
        if os.path.isfile(cheminFichier) == True :
            dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()
                
        # Export
        import pyExcelerator
        # Création d'un classeur
        wb = pyExcelerator.Workbook()
        # Création d'une feuille
        ws1 = wb.add_sheet("Liste des personnes")
        # Remplissage de la feuille

        # Création des labels de colonnes
        x = 0
        y = 0
        for labelCol, alignement, largeur, nomChamp in liste_labelsColonnes :
            ws1.write(x, y, labelCol )
            ws1.col(y).width = largeur*42
            y += 1
        
        x = 1
        y = 0
        for valeurs in listeValeurs :
            if int(valeurs[0]) in listeSelections :
                for valeur in valeurs :
                    ws1.write(x, y, valeur )
                    y += 1
                x += 1
                y = 0
                
        # Finalisation du fichier xls
        wb.save(cheminFichier)
        
        # Confirmation de création du fichier et demande d'ouverture directe dans Excel
        txtMessage = _(u"Le fichier Excel a été créé avec succès. Souhaitez-vous l'ouvrir dès maintenant ?")
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)
            
    def Imprimer(self):
        """ Imprimer la liste au format PDF """
        if self.GetNbreItems() == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune personne dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        # Récupération des valeurs
        liste_labelsColonnes, listeValeurs = self.GetValeurs()
        
        # Selection des lignes
        from Dlg import DLG_Selection_liste
        dlg = DLG_Selection_liste.MyFrame(self, liste_labelsColonnes, listeValeurs, type="imprimerListePersonnes")
        if dlg.ShowModal() == wx.ID_OK:
            listeSelections = dlg.GetSelections()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        
        Impression(liste_labelsColonnes, listeValeurs, listeSelections)



# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

class Impression():
    def __init__(self, liste_labelsColonnes=[], listeValeurs=[], listeSelections=[]):
        """ Imprime la liste de personnes """
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.units import inch, cm
        from reportlab.lib.pagesizes import A4, portrait, landscape
        from reportlab.lib import colors
        
        hauteur_page = defaultPageSize[0]
        largeur_page = defaultPageSize[1]
        largeur_ligne = largeur_page - (75 * 2)

        # Initialisation du PDF
        nomDoc = UTILS_Fichiers.GetRepTemp("liste_emplois.pdf")
        if "win" in sys.platform : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=landscape(A4))
        story = []

        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (620, 100) )
        dateDuJour = DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Liste des offres d'emploi"), _(u"Edité le %s") % dateDuJour )  )
        style = TableStyle([
                            ('BOX', (0,0), (-1,-1), 0.25, colors.black), 
                            ('VALIGN', (0,0), (-1,-1), 'TOP'), 
                            ('ALIGN', (0,0), (0,0), 'LEFT'), 
                            ('FONT',(0,0),(0,0), "Helvetica-Bold", 16), 
                            ('ALIGN', (1,0), (1,0), 'RIGHT'), 
                            ('FONT',(1,0),(1,0), "Helvetica", 6), 
                            ])
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(style)
        story.append(tableau)
        story.append(Spacer(0,20))       
        
        # Tableau de données
        dataTableau = []
        
        # Création des colonnes
        largeursColonnes = []
        labelsColonnes = []

        index = 0
        for labelCol, alignement, largeur, nomChamp in liste_labelsColonnes :
            if largeur == 0 : largeur = 30
            largeursColonnes.append(largeur/2*1.4)
            labelsColonnes.append(labelCol)
            index += 1
        dataTableau.append(labelsColonnes)
        
        # Création des lignes
        for valeurs in listeValeurs :
            ligne = []
            if int(valeurs[0]) in listeSelections :
                for valeur in valeurs :
                    ligne.append(valeur)
                dataTableau.append(ligne)
    
        # Style du tableau
        style = TableStyle([
                            ('GRID', (0,0), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
                            ('ALIGN', (0,0), (-1,-1), 'CENTRE'), # Titre du groupe à gauche
                            ('VALIGN', (0,0), (-1,-1), 'TOP'),
                            ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police 
                            ])
           
        # Création du tableau
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(style)
        story.append(tableau)
        story.append(Spacer(0,20))
            
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)
        


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_emplois", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL candidatures")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
