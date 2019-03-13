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
import GestionDB
import operator
import FonctionsPerso
import os
import sys
from Utils import UTILS_Fichiers
from Utils import UTILS_Adaptations

from CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


# Liste sans nom du candidat
LISTE_COLONNES_1 = [
            [_(u"ID"), "left", 0, "IDcontrat", "entier", _(u"ID du contrat"), True, 1 ],
            [_(u"Type de contrat"), "left", 180, "type_contrat", "texte", _(u"Type de contrat"), True, 2 ],
            [_(u"Date de début"), "left", 90, _(u"date_debut"), "date", _(u"Date de début de contrat"), True, 3 ],
            [_(u"Date de fin"), "left", 90, _(u"date_fin"), "date", _(u"Date de fin de contrat"), True, 4 ],
            [_(u"Classification"), "left", 100, _(u"classification"), "text", _(u"Classification du contrat"), True, 5 ],
            ] # nom Colonne, alignement, largeur, nom Champ, Args pour OLV, Description, Affiché ?, Ordre

# Liste avec nom du candidat
LISTE_COLONNES_2 = [
            [_(u"ID"), "left", 0, "IDcontrat", "entier", _(u"ID du contrat"), True, 1 ],
            [_(u"Nom du salarié"), "left", 140, "nomPersonne", "texte", _(u"Nom du salarié"), True, 2 ],
            [_(u"Type de contrat"), "left", 180, "type_contrat", "texte", _(u"Type de contrat"), True, 3 ],
            [_(u"Date de début"), "left", 90, _(u"date_debut"), "date", _(u"Date de début de contrat"), True, 4 ],
            [_(u"Date de fin"), "left", 90, _(u"date_fin"), "date", _(u"Date de fin de contrat"), True, 5 ],
            [_(u"Classification"), "left", 100, _(u"classification"), "texte", _(u"Classification du contrat"), True, 6 ],
            ] # nom Colonne, alignement, largeur, nom Champ, Args pour OLV, Description, Affiché ?, Ordre

# Liste complète de tous les contrats
LISTE_COLONNES_3 = [
            [_(u"ID"), "left", 0, "IDcontrat", "entier", _(u"ID du contrat"), True, 1 ],
            [_(u"Entrée"), "left", 90, "date_debut", "date", _(u"Date de début de contrat"), True, 2],
            [_(u"Sortie"), "left", 90, "date_fin", "date", _(u"Date de fin de contrat"), True, 3],
            [_(u"Civilité"), "left", 50, "civilite", "texte", _(u"Civilité"), True, 4],
            [_(u"Nom"), "left", 120, "nom", "texte", _(u"Nom de famille"), True, 5],
            [_(u"Nom de jeune fille"), "left", 120, "nom_jfille", "texte", _(u"Nom de jeune fille"), True, 6],
            [_(u"Prénom"), "left", 120, "prenom", "texte", _(u"Prénom"), True, 7],
            [_(u"Date naiss."), "left", 70, "date_naiss", "date", _(u"Date de naissance"), True, 8],
            [_(u"Nationalité"), "left", 90, "nationalite", "texte", _(u"Nationalité"), True, 9],
            [_(u"Num. sécurité sociale"), "left", 130, "num_secu", "texte", _(u"Numéro de sécurité sociale"), True, 10],
            [_(u"Type de contrat"), "left", 200, "type_contrat", "texte", _(u"Type de contrat"), True, 11],
            [_(u"Classification"), "left", 200, "classification", "texte", _(u"Classification du contrat"), True, 12],
            [_(u"Qualifications"), "left", 200, "qualifications", "texte", _(u"Qualifications"), True, 13],
            ] # nom Colonne, alignement, largeur, nom Champ, Args pour OLV, Description, Affiché ?, Ordre


# ---------------------------------------- LISTVIEW PERSONNES  -----------------------------------------------------------------------


class Track(object):
    def __init__(self, parent, donnees):
        self.parent = parent
        self.IDcontrat = donnees[0]
        self.IDpersonne = donnees[1]
        self.date_debut = donnees[2]
        self.date_fin = donnees[3]
        self.classification = donnees[4]
        self.type_contrat = donnees[5]
        self.civilite = donnees[6]
        self.nom = donnees[7]
        self.nom_jfille = donnees[8]
        self.prenom = donnees[9]
        self.date_naiss = donnees[10]
        self.nationalite = donnees[11]
        self.num_secu = donnees[12]
        self.qualifications = self.GetQualifications(self.IDpersonne)

        # Nom complet
        if self.prenom == None :
            self.prenom = ""
        self.nomPersonne = u"%s %s" % (self.nom, self.prenom)

    def GetQualifications(self, IDcandidat):
        if (IDcandidat in self.parent.dict_qualifications) == False :
            return ""
        listeQualifications = self.parent.dict_qualifications[IDcandidat]
        txtQualifications = ""
        nbreQualifications = 0
        for IDtype_diplome in listeQualifications :
            txtQualifications += self.parent.dict_types_diplomes[IDtype_diplome] + ", "
            nbreQualifications += 1
        if nbreQualifications > 0 :
            txtQualifications = txtQualifications[:-2]
        return txtQualifications



class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        wx.Locale(wx.LANGUAGE_FRENCH)
        # Récupération des paramètres perso
        self.IDpersonne = kwds.pop("IDpersonne", None)
        self.modeAffichage = kwds.pop("modeAffichage", None)
        self.activeCheckBoxes = kwds.pop("activeCheckBoxes", False)
        self.activeDoubleClic = kwds.pop("activeDoubleClic", True)
        self.activeMenuContextuel = kwds.pop("activeMenuContextuel", True)
        self.selectionID = None
        self.selectionTrack = None
        self.presents = False
        self.criteres = ""
        self.listeFiltres = []
        self.itemSelected = False
        self.popupIndex = -1
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        if self.modeAffichage == None or self.modeAffichage == "sans_nom" : 
            self.listeColonnes = LISTE_COLONNES_1
        if self.modeAffichage == "avec_nom" : 
            self.listeColonnes = LISTE_COLONNES_2
        if self.modeAffichage == "liste_contrats" :
            self.listeColonnes = LISTE_COLONNES_3

        self.listeColonnesOriginale = list(self.listeColonnes)

        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        if self.activeMenuContextuel == True :
            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        if self.activeMenuContextuel == True :
            self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        else:
            self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenuBasique)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
                
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
                IDpersonne = self.Selection()[0].IDpersonne
                # Met à jour le cadre Résumé
                self.GetGrandParent().GetParent().panel_resume.MAJ(IDcandidat=IDcandidat, IDpersonne=IDpersonne)
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
        self.donnees = self.GetTracks()
        
    def GetTracks(self):
        """ Récupération des données """
        # Critères
        listeID = None
        self.criteres = ""
        if self.IDpersonne != None and self.IDpersonne != 0 :
            self.criteres = "WHERE IDpersonne=%d" % self.IDpersonne
        # Liste de filtres
        if len(self.listeFiltres) > 0 :
            listeID, criteres = self.GetListeFiltres(self.listeFiltres)
            if criteres != "" :
                if self.criteres == "" :
                    self.criteres = "WHERE " + criteres
                else:
                    self.criteres += " AND " + criteres

        # Req
        DB = GestionDB.DB()

        # Qualifications
        req = """SELECT IDdiplome, IDpersonne, IDtype_diplome
        FROM diplomes; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        # Transforme liste en dict
        self.dict_qualifications = {}
        for IDdiplome, IDpersonne, IDtype_diplome in listeDonnees:
            if IDpersonne in self.dict_qualifications:
                self.dict_qualifications[IDpersonne].append(IDtype_diplome)
            else:
                self.dict_qualifications[IDpersonne] = [IDtype_diplome, ]

        # Types de diplômes
        req = """SELECT IDtype_diplome, nom_diplome
        FROM types_diplomes; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        # Transforme liste en dict
        self.dict_types_diplomes = {}
        for IDtype_diplome, nom_diplome in listeDonnees:
            self.dict_types_diplomes[IDtype_diplome] = nom_diplome

        # Contrats
        req = """
        SELECT contrats.IDcontrat, contrats.IDpersonne, contrats.date_debut, contrats.date_fin,
        contrats_class.nom, contrats_types.nom, 
        personnes.civilite, personnes.nom, personnes.nom_jfille, personnes.prenom, 
        personnes.date_naiss, pays.nom, personnes.num_secu
        FROM contrats 
        LEFT JOIN personnes ON contrats.IDpersonne = personnes.IDpersonne
        LEFT JOIN contrats_class ON contrats_class.IDclassification = contrats.IDclassification 
        LEFT JOIN contrats_types ON contrats_types.IDtype = contrats.IDtype
        LEFT JOIN pays ON pays.IDpays = personnes.nationalite
        %s
        """ % self.criteres
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
                track = Track(self, item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
                        
    def InitObjectListView(self):                    
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
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp, typeDonnee=args, stringConverter=FormateDate)
                else:
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp, typeDonnee=args)
                liste_Colonnes.append(colonne)
        
        self.SetColumns(liste_Colonnes)
        
        self.SetEmptyListMsg(_(u"Aucun contrat"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        if self.activeCheckBoxes == True :
            self.CreateCheckStateColumn(1)
            self.SetSortColumn(self.columns[2])
        else:
            self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
        
        
       
    def MAJ(self, IDpersonne=None, presents=None):
        if IDpersonne != None :
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

    def OnContextMenuBasique(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False

        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, dictParametres=self.GetParametresImpression())

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetParametresImpression(self):
        dictParametres = {
            "titre" : _(u"Registre unique du personnel"),
            "orientation" : wx.LANDSCAPE,
            }
        return dictParametres

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        self.DestroyPopup()
        
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False

        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        menuPop.AppendSeparator()
            
        # Item Modifier
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
        
        # Item Publipostage
        item = wx.MenuItem(menuPop, 140, _(u"Créer un courrier ou un mail par publipostage"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Mail.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Courrier, id=140)
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
        
    def Menu_AfficherTout(self, event):
        self.AfficherTout()
    
    def Menu_Rechercher(self, event):
        self.Rechercher()
    
    def Menu_Courrier(self, event):
        self.CourrierPublipostage()
        
    def Menu_Options(self, event):
        self.Options()

    def Menu_Aide(self, event):
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
        dlg = DLG_Config_liste_personnes.Dialog(self, self.listeColonnes)
        dlg.ShowModal()
        dlg.Destroy()

    def MenuImprimer(self, event):
        self.Imprimer()
        
    def MenuExportTexte(self, event):
        self.ExportTexte()
        
    def MenuExportExcel(self, event):
        self.ExportExcel()

    def Rechercher(self):
        # Récupération des filtres souhaités
        from Dlg import DLG_Filtre_recrutement
        dlg = DLG_Filtre_recrutement.MyDialog(self, categorie="candidatures", listeValeursDefaut=self.listeFiltres, title=_(u"Sélection de filtres de liste"))
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
            
        # Si aucun candidat sélectionné
        if (self.IDcandidat == None or self.IDcandidat == 0) and (self.IDpersonne == None or self.IDpersonne == 0 ):
            dlg = DLG_Selection_candidat.MyDialog(self)
            if dlg.ShowModal() == wx.ID_OK:
                IDcandidat = dlg.GetIDcandidat()
                IDpersonne = dlg.GetIDpersonne()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return False
        else:
            IDcandidat = self.IDcandidat
            IDpersonne = self.IDpersonne
            
        # Ouverture de la saisie d'un candidature
        dlg = Saisie_Candidature.Dialog(self, IDcandidat=IDcandidat, IDpersonne=IDpersonne, IDcandidature=None)
        dlg.ShowModal()
        dlg.Destroy()

    def Modifier(self):
        
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                self.GetGrandParent().GetParent().AffichePanelResume(False)
        except : 
            pass
            
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une candidature à modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        IDcandidature = self.Selection()[0].IDcandidature
        IDcandidat = self.Selection()[0].IDcandidat
        IDpersonne = self.Selection()[0].IDpersonne
        dlg = Saisie_Candidature.Dialog(self, IDcandidat=IDcandidat, IDpersonne=IDpersonne, IDcandidature=IDcandidature)
        dlg.ShowModal()
        dlg.Destroy()
                
    def Supprimer(self):
        
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                self.GetGrandParent().GetParent().AffichePanelResume(False)
        except : 
            pass
            
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une candidature à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        IDcandidature = self.Selection()[0].IDcandidature
                
        # Demande de confirmation
        date_depot = self.Selection()[0].depot
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer la candidature du %s ?") % date_depot))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Suppression
        DB = GestionDB.DB()
        
        # Suppression
        DB.ReqDEL("candidatures", "IDcandidature", IDcandidature)
        DB.ReqDEL("disponibilites", "IDcandidature", IDcandidature)
        DB.ReqDEL("cand_fonctions", "IDcandidature", IDcandidature)
        DB.ReqDEL("cand_affectations", "IDcandidature", IDcandidature)
        
        DB.Close()
        # MàJ du ListCtrl
        self.MAJ()
        
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" : 
                self.GetGrandParent().GetParent().gadget_entretiens.MAJ()
                self.GetGrandParent().GetParent().gadget_informations.MAJ()
        except :
            pass
        
        try :
            if self.GetGrandParent().GetName() == "panel_resume" :
                panelRecrutement = self.GetGrandParent().GetGrandParent().GetParent()
                panelRecrutement.MAJpanel(MAJpanelResume=False)
                self.GetGrandParent().MAJlabelsPages("candidatures")
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
                dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une candidature dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            listeID = [self.Selection()[0].IDcandidature,]
        else:
            if self.GetNbreItems() == 0 :
                dlg = wx.MessageDialog(self, _(u"Il n'y a aucune candidature dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
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
        dictDonnees = UTILS_Publipostage_donnees.GetDictDonnees(categorie="candidature", listeID=listeID)
        # Ouvre le publiposteur
        from Dlg import DLG_Publiposteur
        frm = DLG_Publiposteur.MyWizard(self, "", dictDonnees=dictDonnees)
        frm.Show()

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
            



class Popup(wx.PopupWindow):
    def __init__(self, parent, style=wx.SIMPLE_BORDER, key=0):
        wx.PopupWindow.__init__(self, parent, style)
        self.panel = wx.Panel(self, -1)
        listView = self.GetParent()
        track = listView.GetObjectAt(key)
        imageList = listView.smallImageList.imageList
        
        # Récupération des images
        img_depot = imageList.GetBitmap(listView.GetImageAt(track, 1))
        img_decision = imageList.GetBitmap(listView.GetImageAt(track, 6))
        img_reponse = imageList.GetBitmap(listView.GetImageAt(track, 7))
        
        # Récupération des données
        listeColonnes = [
            ( 1, _(u"Dépôt"), img_depot, track.depot_long ),
            ( 1, _(u"Nom"), None, track.nom_candidat ),
            ( 2, _(u"Emploi"), None, track.offre_emploi ),
            ( 3, _(u"Disponibilités"), None, track.disponibilites ),
            ( 4, _(u"Fonctions"), None, track.fonctions ),
            ( 5, _(u"Affectations"), None, track.affectations ),
            ( 6, _(u"Décision"), img_decision, track.decision ),
            ( 7, _(u"Réponse"), img_reponse, track.texte_reponse_long ),
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
        nomDoc = UTILS_Fichiers.GetRepTemp("liste_candidatures.pdf")
        if "win" in sys.platform : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=landscape(A4))
        story = []

        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (620, 100) )
        dateDuJour = DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Liste des candidatures"), _(u"Edité le %s") % dateDuJour )  )
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
            largeursColonnes.append(largeur/2*1.6)
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
        self.myOlv = ListView(panel, id=-1, modeAffichage="liste_contrats", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
