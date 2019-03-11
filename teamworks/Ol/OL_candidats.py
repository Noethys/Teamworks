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
from Utils import UTILS_Adaptations
import GestionDB
import operator
import FonctionsPerso
import os
import sys
from Dlg import DLG_Saisie_candidat
from Utils import UTILS_Fichiers

from ObjectListView import ObjectListView, ColumnDefn


DICT_COORDONNEES = {}
DICT_QUALIFICATIONS = {}
DICT_TYPES_DIPLOMES = {}

LISTE_COLONNES = [
            [u"", "left", 22, "IDcandidat", "image_civilite", _(u"ID du candidat"), True, 1 ],
            [_(u"Civilité"), "left", 50, _(u"civilite"), "", _(u"Civilité"), True, 2 ],
            [_(u"Nom"), "left", 100, "nom", "", _(u"Nom de famille"), True, 3 ],
            [_(u"Prénom"), "left", 100, "prenom", "", _(u"Prénom"), True, 4 ],
            [_(u"Âge"), "left", 50, "age_texte", "", _(u"Âge"), True, 5 ],
            [_(u"Qualifications"), "left", 100, "qualifications",  "", _(u"Qualifications"), True, 6 ],
            [_(u"Adresse"), "lef", 160, "adresse_resid",  "", _(u"Adresse de résidence"), True, 7 ],
            [_(u"CP"), "left", 50, "cp_resid",  "", _(u"Code postal de la ville de résidence"), True, 8 ],
            [_(u"Ville"), "left", 110, "ville_resid",  "", _(u"Nom de la ville de résidence"), True, 9 ],
            [_(u"Téléphones"), "left", 200, "telephones", "", _(u"Numéros de téléphones"), True, 10 ],
            [_(u"Email"), "left", 150, "email", "", _(u"Adresses emails"), True, 11],
            [_(u"Fax"), "left", 150, "fax", "", _(u"Numéros de fax"), False, 12 ],            
            [_(u"Mémo"), "left", 100, "memo",  "", _(u"Mémo"), False, 13 ],
            ] # nom Colonne, alignement, largeur, nom Champ, Args pour OLV, Description, Affiché ?, Ordre
            

# ---------------------------------------- LISTVIEW PERSONNES  -----------------------------------------------------------------------


class Track(object):
    def __init__(self, donnees):
        self.IDcandidat = donnees[0]
        self.civilite = donnees[1]
        self.nom = donnees[2]
        if self.nom == None : self.nom = ""
        self.prenom = donnees[3]
        if self.prenom == None : self.prenom = ""
        self.nom_complet = self.nom + " " + self.prenom
        self.date_naiss = donnees[4]
        self.age = donnees[5]
        if self.age != 0 and self.age != None and self.age != "" :
            self.age_texte = _(u"%d ans") % self.age
        else:
            self.age_texte = self.RetourneAge(self.date_naiss)
        self.adresse_resid = donnees[6]
        if self.adresse_resid == None : self.adresse_resid = ""
        self.cp_resid = donnees[7]
        if self.cp_resid == None : self.cp_resid = ""
        self.ville_resid = donnees[8]
        if self.ville_resid == None : self.ville_resid = ""
        self.adresse_complete = u"%s %s %s" % (self.adresse_resid, self.cp_resid, self.ville_resid)
        self.memo = donnees[9]
        self.telephones = self.GetCoordonnees(self.IDcandidat, type="telephone")
        self.email = self.GetCoordonnees(self.IDcandidat, type="email")
        self.fax = self.GetCoordonnees(self.IDcandidat, type="fax")
        self.qualifications = self.GetQualifications(self.IDcandidat)
            
    def RetourneAge(self, dateStr):
        if dateStr == "" or dateStr == None : return ""
        bday = datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10]))
        datedujour = datetime.date.today()
        age = (datedujour.year - bday.year) - int((datedujour.month, datedujour.day) < (bday.month, bday.day))
        texteAge = str(age) + " ans"
        return texteAge

    def GetCoordonnees(self, IDcandidat, type=""):
        if (IDcandidat in DICT_COORDONNEES) == False :
            return ""
        listeCoordonnees = DICT_COORDONNEES[IDcandidat]
        txtCoords = ""
        nbreCoords = 0
        for IDcoord, IDcandidat, categorie, texte, intitule in listeCoordonnees :
            if type == "telephone" and (categorie == "Fixe" or categorie == "Mobile") :
                txtCoords += texte + ", "
                nbreCoords += 1
            if type == "email" and (categorie == "Email") :
                txtCoords += texte + ", "
                nbreCoords += 1
            if type == "fax" and (categorie == "Fax") :
                txtCoords += texte + ", "
                nbreCoords += 1
        if nbreCoords > 0 : 
            txtCoords = txtCoords[:-2]
        return txtCoords

    def GetQualifications(self, IDcandidat):
        if (IDcandidat in DICT_QUALIFICATIONS) == False :
            return ""
        listeQualifications = DICT_QUALIFICATIONS[IDcandidat]
        txtQualifications = ""
        nbreQualifications = 0
        for IDtype_diplome in listeQualifications :
            txtQualifications += DICT_TYPES_DIPLOMES[IDtype_diplome] + "; "
            nbreQualifications += 1
        if nbreQualifications > 0 : 
            txtQualifications = txtQualifications[:-2]
        return txtQualifications
    
class ListView(ObjectListView):
    def __init__(self, *args, **kwds):
        wx.Locale(wx.LANGUAGE_FRENCH)
        # Récupération des paramètres perso
        self.activeDoubleClic = kwds.pop("activeDoubleClic", True)
        self.activeMenuContextuel = kwds.pop("activeMenuContextuel", True)
        self.activeCheckBoxes = kwds.pop("activeCheckBoxes", False)
        self.activePopup = kwds.pop("activePopup", True)
        self.selectionID = None
        self.selectionTrack = None
        self.presents = False
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        # Initialisation du listCtrl
        self.listeColonnes = LISTE_COLONNES
        self.listeColonnesOriginale = list(self.listeColonnes)
        ObjectListView.__init__(self, *args, **kwds)
##        self.InitModel()
##        self.InitObjectListView()
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        if self.activeDoubleClic == True :
            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        if self.activeMenuContextuel == True :
            self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        
        if "linux" not in sys.platform and self.activePopup == True :
            # Désactive la fenetre popup sous Linux
            self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        
    def OnItemActivated(self,event):
        self.DestroyPopup()
        self.Modifier()
        
    def OnItemSelected(self, event):
        self.DestroyPopup()
        self.itemSelected = True
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                self.GetGrandParent().GetParent().bouton_modifier.Enable(True)
                self.GetGrandParent().GetParent().bouton_supprimer.Enable(True)
                if len(self.Selection()) == 0:
                    return False
                IDcandidat = self.Selection()[0].IDcandidat
                # Met à jour le cadre Résumé
                self.GetGrandParent().GetParent().panel_resume.MAJ(IDcandidat=IDcandidat)
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
        self.Importation_coordonnees()
        self.Importation_qualifications() 
        self.Importation_types_diplomes() 
        self.donnees = self.GetTracks()

    def GetListeFiltres(self, listeFiltres=[]):
                
        # ------------------------------------------------------------------------------------------------------------------------
        
##        def GetListeDisponibilites(dictFiltres):
##            """ Recherche des disponibilités """
##            listeTemp = []
##            for IDcandidature, disponibilites in DICT_DISPONIBILITES.iteritems() :
##                for IDdisponibilite, date_debut, date_fin in disponibilites :
##                    if date_fin>=dictFiltres["valeur"][0] and date_debut<=dictFiltres["valeur"][1] :
##                        listeTemp.append(IDcandidature)
##            return listeTemp
##        
##        def GetListeFonctions(dictFiltres):
##            """ Recherche des fonctions """
##            listeTemp = []
##            for IDcandidature, listeFonctions in DICT_CAND_FONCTIONS.iteritems() :
##                for ID, label in dictFiltres["valeur"] :
##                    if ID in listeFonctions :
##                        if IDcandidature not in listeTemp :
##                            listeTemp.append(IDcandidature)
##            return listeTemp
        
        def GetListeQualifications(dictFiltres):
            """ Recherche des qualifications """
            listeTemp = []
            for IDqualif, listeQualifications in DICT_QUALIFICATIONS.items() :
                for ID, label in dictFiltres["valeur"] :
                    if ID in listeQualifications :
                        if IDqualif not in listeTemp :
                            listeTemp.append(IDqualif)
            return listeTemp
        
        # ------------------------------------------------------------------------------------------------------------------------
        nbreFiltres = 0
        criteresSQL = ""
        listeListes = []
        for dictFiltres in listeFiltres :
            
            if dictFiltres["nomControle"] == "candidats_qualifications" : 
                listeListes.append(GetListeQualifications(dictFiltres))
##            elif dictFiltres["nomControle"] == "candidature_fonctions" : 
##                listeListes.append(GetListeFonctions(dictFiltres))
##            elif dictFiltres["nomControle"] == "candidature_affectations" : 
##                listeListes.append(GetListeAffectations(dictFiltres))
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
            for liste in listeListes :
                texteFonction += "set(listeListes[%d]) & " % index
                index += 1
            texteFonction = texteFonction[:-3]
            exec("listeID=%s" % texteFonction)
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
        req = """SELECT IDcandidat, civilite, nom, prenom, date_naiss, age, adresse_resid, cp_resid, ville_resid, memo
        FROM candidats %s ORDER BY nom, prenom; """ % self.criteres
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

    def Importation_qualifications(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDdiplome, IDcandidat, IDtype_diplome
        FROM diplomes_candidats; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global DICT_QUALIFICATIONS
        DICT_QUALIFICATIONS = {}
        for IDdiplome, IDcandidat, IDtype_diplome in listeDonnees :
            if IDcandidat in DICT_QUALIFICATIONS :
                DICT_QUALIFICATIONS[IDcandidat].append(IDtype_diplome)
            else:
                DICT_QUALIFICATIONS[IDcandidat] = [IDtype_diplome,]

    def Importation_types_diplomes(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDtype_diplome, nom_diplome
        FROM types_diplomes; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global DICT_TYPES_DIPLOMES
        DICT_TYPES_DIPLOMES = {}
        for IDtype_diplome, nom_diplome in listeDonnees :
            DICT_TYPES_DIPLOMES[IDtype_diplome] = nom_diplome
                                             
    def Importation_coordonnees(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDcoord, IDcandidat, categorie, texte, intitule
        FROM coords_candidats; """
        DB.ExecuterReq(req)
        listeCoordonnees = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global DICT_COORDONNEES
        DICT_COORDONNEES = {}
        for IDcoord, IDcandidat, categorie, texte, intitule in listeCoordonnees :
            donnees = (IDcoord, IDcandidat, categorie, texte, intitule)
            if IDcandidat in DICT_COORDONNEES :
                DICT_COORDONNEES[IDcandidat].append(donnees)
            else :
                DICT_COORDONNEES[IDcandidat] = [(donnees),]

    def InitObjectListView(self):
        # Images
        self.imgHomme = self.AddNamedImages("homme", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Homme.png"), wx.BITMAP_TYPE_PNG))
        self.imgFemme = self.AddNamedImages("femme", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Femme.png"), wx.BITMAP_TYPE_PNG))
        
        # Formatage des données
        def ImageGetter_civilite(track):
            if track.civilite == "Mr" : return self.imgHomme
            else: return self.imgFemme
            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#EEF4FB" # wx.Colour(255, 255, 255) #"#EEF4FB" # Bleu
        self.evenRowsBackColor = wx.Colour(255, 255, 255) #"#F0FBED" # Vert
        self.useExpansionColumn = True
        
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
                    # Formatage d'une date
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp, stringConverter=FormateDate)
                elif args == "image_civilite" :
                    # Formatage d'une date
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp, imageGetter=ImageGetter_civilite)
                else:
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp)
                liste_Colonnes.append(colonne)
        
        self.SetColumns(liste_Colonnes)

        self.SetEmptyListMsg(_(u"Aucun candidat"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        if self.activeCheckBoxes == True :
            self.CreateCheckStateColumn(0)
            self.SetSortColumn(self.columns[3])
        else:
            self.SetSortColumn(self.columns[2])
        self.SetObjects(self.donnees)
       
    def MAJ(self, IDcandidat=None, presents=None):
        if IDcandidat != None :
            self.selectionID = IDpersonne
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
        self.DestroyPopup()
        
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDcandidat
        
        # Récupération d'une adresse Email
        if noSelection == False :
            DB = GestionDB.DB()
            req = "SELECT texte FROM coords_candidats WHERE IDcandidat = %d AND categorie='Email'" % ID
            DB.ExecuterReq(req)
            listeEmails = DB.ResultatReq()
            DB.Close()
            if len(listeEmails) != 0 :
                self.adresseMail = listeEmails[0][0]
            else:
                self.adresseMail = ""
            
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

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
        
        # Item Envoyer un Mail
        if noSelection == False : 
            if self.adresseMail != "" :
                item = wx.MenuItem(menuPop, 80, _(u"Envoyer un Email avec votre logiciel de messagerie"))
                bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mail.png"), wx.BITMAP_TYPE_PNG)
                item.SetBitmap(bmp)
                menuPop.AppendItem(item)
                self.Bind(wx.EVT_MENU, self.Menu_Mail, id=80)
        
        # Item Publipostage
        item = wx.MenuItem(menuPop, 140, _(u"Créer un courrier ou un mail par publipostage"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mail.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Courrier, id=140)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()

        # Item Filtres de liste
        item = wx.MenuItem(menuPop, 120, _(u"Rechercher"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Rechercher, id=120)
        
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
        
    def Menu_AfficherTout(self, event):
        self.AfficherTout()

    def Menu_Rechercher(self, event):
        self.Rechercher()
        
    def Menu_Options(self, event):
        self.Options()

    def Menu_Aide(self, event):
##        self.GetGrandParent().GetParent().OnBoutonAide(None)
        dlg = wx.MessageDialog(self, _(u"L'aide du module Recrutement est en cours de rédaction.\nElle sera disponible lors d'une mise à jour ultérieure."), "Aide indisponible", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
    def Menu_Mail(self, event):
        FonctionsPerso.EnvoyerMail(adresses = (self.adresseMail,))

    def Menu_Courrier(self, event):
        self.CourrierPublipostage()
        
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
        dlg = DLG_Filtre_recrutement.MyDialog(self, categorie="candidats", listeValeursDefaut=self.listeFiltres, title=_(u"Sélection de filtres de liste"))
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
        frmFiche = DLG_Saisie_candidat.MyFrame(self, IDcandidat=None)
        frmFiche.Show()

    def Modifier(self):
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un candidat à modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                self.GetGrandParent().GetParent().AffichePanelResume(False)
        except : 
            pass
            
        IDcandidat = self.Selection()[0].IDcandidat
        frmFiche = DLG_Saisie_candidat.MyFrame(self, IDcandidat=IDcandidat)
        frmFiche.Show()
                
    def Supprimer(self):
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un candidat à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        IDcandidat = self.Selection()[0].IDcandidat
        
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                self.GetGrandParent().GetParent().AffichePanelResume(False)
        except : 
            pass
            
        # Vérifie qu'il n'y a pas de candidatures saisies pour ce candidat
        DB = GestionDB.DB()
        req = """SELECT IDcandidature, IDcandidat
        FROM candidatures WHERE IDcandidat = %d""" % IDcandidat
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 : 
            dlg = wx.MessageDialog(self, _(u"%s candidature(s) existe(nt) pour ce candidat. Vous ne pouvez donc pas supprimer sa fiche.\n\nRemarque : Si vous souhaitez vraiment supprimer cette fiche, il vous faudra d'abord supprimer la ou les candidature(s).") % len(listeDonnees), _(u"Impossible de supprimer"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Vérifie qu'il n'y a pas d'entretiens saisis pour ce candidat
        DB = GestionDB.DB()
        req = """SELECT IDentretien, IDcandidat
        FROM entretiens WHERE IDcandidat = %d""" % IDcandidat
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 : 
            dlg = wx.MessageDialog(self, _(u"%s entretien(s) existe(nt) pour ce candidat. Vous ne pouvez donc pas supprimer sa fiche.\n\nRemarque : Si vous souhaitez vraiment supprimer cette fiche, il vous faudra d'abord supprimer la ou les entretien(s).") % len(listeDonnees), _(u"Impossible de supprimer"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
                
        # Demande de confirmation
        nom_complet = self.Selection()[0].nom_complet
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer le candidat : %s ?") % nom_complet))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Suppression
        DB = GestionDB.DB()
        DB.ReqDEL("candidats", "IDcandidat", IDcandidat)
        DB.ReqDEL("coords_candidats", "IDcandidat", IDcandidat)
        DB.ReqDEL("diplomes_candidats", "IDcandidat", IDcandidat)
        DB.ReqDEL("candidatures", "IDcandidat", IDcandidat)
        DB.ReqDEL("entretiens", "IDcandidat", IDcandidat)
        DB.Close()
        # MàJ du ListCtrl
        self.MAJ()
        
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" : 
                self.GetGrandParent().GetParent().gadget_entretiens.MAJ()
                self.GetGrandParent().GetParent().gadget_informations.MAJ()
        except :
            pass
    
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

    def CourrierPublipostage(self, mode="unique"):
        if mode == "unique" :
            if len(self.Selection()) == 0:
                dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un candidat dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            listeID = [self.Selection()[0].IDcandidat,]
        else:
            if self.GetNbreItems() == 0 :
                dlg = wx.MessageDialog(self, _(u"Il n'y a aucun candidat dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            # Récupération des valeurs
            liste_labelsColonnes, listeValeurs = self.GetValeurs()
            # Selection des lignes
            from Dlg import DLG_Selection_liste
            dlg = DLG_Selection_liste.Dialog(self, liste_labelsColonnes, listeValeurs, type="exportTexte")
            if dlg.ShowModal() == wx.ID_OK:
                listeSelections = dlg.GetSelections()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return False
            listeID = listeSelections
        
        # Récupère les données pour le publipostage
        from Utils import UTILS_Publipostage_donnees
        dictDonnees = UTILS_Publipostage_donnees.GetDictDonnees(categorie="candidat", listeID=listeID)
        # Ouvre le publiposteur
        from Dlg import DLG_Publiposteur
        frm = DLG_Publiposteur.MyWizard(self, "", dictDonnees=dictDonnees)
        frm.Show()
        
        
    def ExportTexte(self):
        """ Export de la liste au format texte """
        if self.GetNbreItems() == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucun candidat dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Récupération des valeurs
        liste_labelsColonnes, listeValeurs = self.GetValeurs()
        
        # Selection des lignes
        from Dlg import DLG_Selection_liste
        dlg = DLG_Selection_liste.Dialog(self, liste_labelsColonnes, listeValeurs, type="exportTexte")
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
        dlg = DLG_Selection_liste.Dialog(self, liste_labelsColonnes, listeValeurs, type="exportExcel")
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
        dlg = DLG_Selection_liste.Dialog(self, liste_labelsColonnes, listeValeurs, type="imprimerListePersonnes")
        if dlg.ShowModal() == wx.ID_OK:
            listeSelections = dlg.GetSelections()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        
        Impression(liste_labelsColonnes, listeValeurs, listeSelections)


    def OnMouseMotion(self, event):
        # Panel flottant
        index = self.HitTest(event.GetPosition())[0]
        if index == -1:
            if self.popupIndex != -1 :
                self.DestroyPopup()
            return
        
        item = self.GetItem(index, 0)
           
        pos = self.ClientToScreen(event.GetPosition()) # Position du curseur sur l'écran
        decalage = (15, 15)

        tailleCtrl = self.GetSize()

        # Si le Popup est au bord du ListCtrl, on le ferme
        posInListCtrl = event.GetPosition() # Position du curseur dans le ListCtrl
        if self.popupIndex != -1:
            if posInListCtrl[0] < 4 or posInListCtrl[1] < 4 :
                self.DestroyPopup()
                return

        # Si on était déjà sur l'item , on ne fait que bouger le popup 
        if self.popupIndex == index :
            self.Popup.Position(pos, decalage)

        if self.popupIndex != index and self.popupIndex != -1:
            self.DestroyPopup()

        # Sinon, création d'un popup
        if self.popupIndex != index and posInListCtrl[0] > 3 and posInListCtrl[1] > 3:
            key = self.GetItemData(index)
            self.popupIndex = index
            self.Popup = Popup(self, key=key)
            self.Popup.Position(pos, decalage)
            self.Popup.Show(True)
            self.CaptureMouse()

    def DestroyPopup(self):
        """ Destruction de la fenêtre Popup """
        if self.HasCapture():
            self.ReleaseMouse()
        try:
            self.Popup
            self.Popup.Destroy()
            self.popupIndex = -1
        except:
            pass
            
    def ConvertirFiche(self, IDcandidat=None) :
        """ Convertir fiche """
        # Fiche individuelle
        DB = GestionDB.DB()
        req = """SELECT civilite, nom, prenom, date_naiss, age, adresse_resid, cp_resid, ville_resid, memo
        FROM candidats WHERE IDcandidat = %d""" % IDcandidat
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()[0]
        DB.Close()
        civilite, nom, prenom, date_naiss, age, adresse_resid, cp_resid, ville_resid, memo = listeDonnees
        listeDonnees = [    ("civilite",        civilite),
                            ("nom",             nom),
                            ("nom_jfille",             ""),
                            ("prenom",          prenom),
                            ("date_naiss",      date_naiss),
                            ("ville_naiss",     ""),
                            ("num_secu",     ""),
                            ("adresse_resid",   adresse_resid),
                            ("cp_resid",        cp_resid),
                            ("ville_resid",     ville_resid),
                            ("memo",            memo),
                            ("IDsituation",     0),
                            ("pays_naiss",     73),
                            ("nationalite",     73),
                        ]
        DB = GestionDB.DB()
        IDpersonne = DB.ReqInsert("personnes", listeDonnees)
        DB.Close()
        
        # Coordonnées
        DB = GestionDB.DB()
        req = "SELECT IDcoord, categorie, texte, intitule FROM coords_candidats WHERE IDcandidat=%d" % IDcandidat
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        for IDcoord, categorie, texte, intitule in donnees :
            listeDonnees = [    ("IDpersonne",  IDpersonne),
                                ("categorie",   categorie),
                                ("texte",       texte),
                                ("intitule",    intitule), ]
            DB.ReqInsert("coordonnees", listeDonnees)
        DB.Close()

        # Qualifications
        DB = GestionDB.DB()
        req = "SELECT IDdiplome, IDcandidat, IDtype_diplome FROM diplomes_candidats WHERE IDcandidat=%d" % IDcandidat
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        for IDdiplome, IDcandidat, IDtype_diplome in donnees :
            listeDonnees = [    ("IDpersonne",  IDpersonne),
                                ("IDtype_diplome",   IDtype_diplome), ]
            DB.ReqInsert("diplomes", listeDonnees)
        DB.Close()
        
        # Candidatures
        DB = GestionDB.DB()
        req = "SELECT IDcandidature, IDcandidat FROM candidatures WHERE IDcandidat=%d" % IDcandidat
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        for IDcandidature, IDcandidat in donnees :
            listeDonnees = [    ("IDpersonne",  IDpersonne),
                                        ("IDcandidat",   None), ]
            DB.ReqMAJ("candidatures", listeDonnees, "IDcandidature", IDcandidature)
        DB.Close()
        
        # Entretiens
        DB = GestionDB.DB()
        req = "SELECT IDentretien, IDcandidat FROM entretiens WHERE IDcandidat=%d" % IDcandidat
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        for IDentretien, IDcandidat in donnees :
            listeDonnees = [    ("IDpersonne",  IDpersonne),
                                        ("IDcandidat",   None), ]
            DB.ReqMAJ("entretiens", listeDonnees, "IDentretien", IDentretien)
        DB.Close()
        
        # Suppressions : Fiche candidat, coords_candidat, diplomes_candiat
        DB = GestionDB.DB()
        DB.ReqDEL("candidats", "IDcandidat", IDcandidat)
        DB.ReqDEL("coords_candidats", "IDcandidat", IDcandidat)
        DB.ReqDEL("diplomes_candidats", "IDcandidat", IDcandidat)
        DB.Close()
        
        # Demande d'ouverture de la fiche
        txtMessage = _(u"La fiche individuelle a été créée avec succès.\n\nSouhaitez-vous l'ouvrir maintenant ?")
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Conversion de fiche"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        from Dlg import DLG_Fiche_individuelle
        frmFiche = DLG_Fiche_individuelle.MyFrame(self.GetParent(), IDpersonne=IDpersonne)
        frmFiche.Show()
        


class Popup(wx.PopupWindow):
    def __init__(self, parent, style=wx.SIMPLE_BORDER, key=0):
        wx.PopupWindow.__init__(self, parent, style)
        self.panel = wx.Panel(self, -1)
        listView = self.GetParent()
        track = listView.GetObjectAt(key)
        imageList = listView.smallImageList.imageList
        
        # Récupération des données
        listeColonnes = [
            ( 1, _(u"Nom"), None, track.nom_complet ),
            ( 2, _(u"Age"), None, track.age_texte ),
            ( 3, _(u"Adresse"), None, track.adresse_complete ),
            ( 4, _(u"Qualifications"), None, track.qualifications ),
            ( 5, _(u"Téléphones"), None, track.telephones ),
            ( 6, _(u"Email"), None, track.email ),
            ] # IndexColonne, Label, Image, Donnée
        
        
        # Création du popup
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base_2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=7, cols=2, vgap=5, hgap=5)
        
        index = 0
        for indexCol, label, img, donnee in listeColonnes :
            # Label
            exec("self.label_" + str(index) + " = wx.StaticText(self.panel, -1, u'%s :' % label)")
            exec("self.label_" + str(index) + ".SetForegroundColour(wx.Colour(127, 0, 255))")
            exec("grid_sizer_base.Add(self.label_" + str(index) + ", 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)")
            # Détail : Image et valeur
            if img != None : exec("self.image_" + str(index) + " = wx.StaticBitmap(self.panel, -1, img)")
            exec("self.ctrl_" + str(index) + " = wx.StaticText(self.panel, -1, donnee)")
            # Sizer détail
            if img != None : 
                exec("grid_sizer_" + str(index) + " = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)")
                exec("grid_sizer_" + str(index) + ".Add(self.image_" + str(index) + ", 0, wx.ALIGN_CENTER_VERTICAL, 0)")
                exec("grid_sizer_" + str(index) + ".Add(self.ctrl_" + str(index) + ", 0, wx.ALIGN_CENTER_VERTICAL, 0)")
                exec("grid_sizer_" + str(index) + ".AddGrowableCol(1)")
                exec("grid_sizer_base.Add(grid_sizer_" + str(index) + ", 1, wx.EXPAND, 0)")
            else:
                exec("grid_sizer_base.Add(self.ctrl_" + str(index) + ", 1, wx.EXPAND, 0)")
            index += 1
            
        grid_sizer_base.AddGrowableCol(1)
        sizer_base_2.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 5)
        self.panel.SetSizer(sizer_base_2)
        sizer_base.Add(self.panel, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()        
        
        wx.CallAfter(self.Refresh)
        
        
        
        

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
        nomDoc = UTILS_Fichiers.GetRepTemp("liste_candidats.pdf")
        if "win" in sys.platform : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=landscape(A4))
        story = []

        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (620, 100) )
        dateDuJour = DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Liste des candidats"), _(u"Edité le %s") % dateDuJour )  )
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
            largeursColonnes.append(largeur/2*1.3)
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
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ()
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
