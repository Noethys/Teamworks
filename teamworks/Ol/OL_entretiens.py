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
import wx.lib.agw.hyperlink as hl
import operator
import FonctionsPerso
import os
import sys
from Dlg import DLG_Saisie_entretien
from Dlg import DLG_Selection_candidat
from Utils import UTILS_Fichiers
from Utils import UTILS_Adaptations
from ObjectListView import ObjectListView, ColumnDefn


NOMS_CANDIDATS = {}
NOMS_PERSONNES = {}

VERROUILLAGE = None

##if VERROUILLAGE == None :
##    password = FonctionsPerso.Parametres(mode="get", categorie="recrutement", nom="password_entretien", valeur="")
##    if password == "" :
##        VERROUILLAGE = False
##    else:
##        VERROUILLAGE = True
        

# Liste sans nom du candidat
LISTE_COLONNES_1 = [
            [_(u"ID"), "left", 0, "IDentretien", "", _(u"ID de l'entretien"), True, 1 ],
            [_(u"Date"), "left", 80, _(u"date"), "date", _(u"Date de l'entretien"), True, 2 ],
            [_(u"Heure"), "left", 50, "heure", "heure", _(u"Heure de l'entretien"), True, 3 ],
            [_(u"Avis"), "left", 120, "avis", "image_avis", _(u"Avis sur le candidat"), True, 4 ],
            [_(u"Commentaire"), "left", 270, "remarques", "", _(u"Commentaire sur l'entretien"), True, 5 ],
            ] # nom Colonne, alignement, largeur, nom Champ, Args pour OLV, Description, Affiché ?, Ordre

# Liste avec nom du candidat
LISTE_COLONNES_2 = [
            [_(u"ID"), "left", 0, "IDentretien", "", _(u"ID de l'entretien"), True, 1 ],
            [_(u"Date"), "left", 80, _(u"date"), "date", _(u"Date de l'entretien"), True, 2 ],
            [_(u"Heure"), "left", 50, "heure", "heure", _(u"Heure de l'entretien"), True, 3 ],
            [_(u"Nom"), "left", 120, "nom_candidat", "", _(u"Nom du candidat"), True, 4 ],
            [_(u"Avis"), "left", 120, "avis", "image_avis", _(u"Avis sur le candidat"), True, 5 ],
            [_(u"Commentaire"), "left", 300, "remarques", "", _(u"Commentaire sur l'entretien"), True, 6 ],
            ] # nom Colonne, alignement, largeur, nom Champ, Args pour OLV, Description, Affiché ?, Ordre

# Liste pour gagdet
LISTE_COLONNES_3 = [
            [_(u"ID"), "left", 0, "IDentretien", "", _(u"ID de l'entretien"), True, 1 ],
            [_(u"Date et Heure et Nom"), "left", 210, _(u"date_heure_nom"), "date_heure_nom", _(u"Date, heure et nom"), True, 2 ],
            [_(u"Avis"), "left", 0, "avis", "image_avis", _(u"Avis sur le candidat"), False, 4 ],
            ] # nom Colonne, alignement, largeur, nom Champ, Args pour OLV, Description, Affiché ?, Ordre

# ---------------------------------------- LISTVIEW   -----------------------------------------------------------------------

class Track(object):
    def __init__(self, donnees):
        self.IDentretien = donnees[0]
        self.IDcandidat = donnees[1]
        self.date = donnees[2]
        self.heure = donnees[3]
        self.date_heure = self.date + ";" + self.heure
        if VERROUILLAGE == True :
            self.avis = 999
            self.remarques = _(u"Commentaire verrouillé")
        else:
            self.avis = donnees[4]
            self.remarques = donnees[5]
        self.IDpersonne = donnees[6]

        self.nom_candidat = ""
        if self.IDpersonne == 0 or self.IDpersonne == None:
            civilite, nom, prenom = NOMS_CANDIDATS[self.IDcandidat]
            self.nom_candidat = u"%s %s" % (nom, prenom)
        else:
            if self.IDpersonne in NOMS_PERSONNES:
                civilite, nom, prenom = NOMS_PERSONNES[self.IDpersonne]
                self.nom_candidat = u"%s %s" % (nom, prenom)
            
        self.date_heure_nom = self.date_heure + ";" + self.nom_candidat
    
    
class ListView(ObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDcandidat = kwds.pop("IDcandidat", None)
        self.IDpersonne = kwds.pop("IDpersonne", None)
        self.modeAffichage = kwds.pop("modeAffichage", None)
        self.colorerSalaries = kwds.pop("colorerSalaries", True)
        self.prochainsEntretiens = kwds.pop("prochainsEntretiens", False)
        self.afficheHyperlink = kwds.pop("afficheHyperlink", True)
        self.selectionID = None
        self.selectionTrack = None
        self.presents = False
        self.donnees = []
        self.criteres = ""
        self.listeFiltres = []
        self.itemSelected = False
        self.donnees = []
            
        # Initialisation du listCtrl
        ObjectListView.__init__(self, *args, **kwds)
        if self.modeAffichage == None or self.modeAffichage == "sans_nom" : self.listeColonnes = LISTE_COLONNES_1
        if self.modeAffichage == "avec_nom" : self.listeColonnes = LISTE_COLONNES_2
        if self.modeAffichage == "gadget" : self.listeColonnes = LISTE_COLONNES_3
        self.listeColonnesOriginale = list(self.listeColonnes)
        
        # Initialisation du mot de passe :
        global VERROUILLAGE
        if VERROUILLAGE == None :
            password = FonctionsPerso.Parametres(mode="get", categorie="recrutement", nom="password_entretien", valeur="")
            if password == "" :
                VERROUILLAGE = False
            else:
                VERROUILLAGE = True
                
        # Texte
        self.imgVerrouillage = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/Special/Cadenas.png"), wx.BITMAP_TYPE_ANY), pos=(2, self.GetSize()[1]+1-18))
        self.imgVerrouillage.SetBackgroundColour(self.GetBackgroundColour())
        self.texteVerrouillage = Hyperlink(self, label=u"", infobulle=u"", pos=(14, self.GetSize()[1]+18))
        self.texteVerrouillage.SetBackgroundColour(self.GetBackgroundColour())
        self.SetLabelHyperlink()
        if self.afficheHyperlink == False :
            self.imgVerrouillage.Show(False)
            self.texteVerrouillage.Show(False)
        
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        self.Bind(wx.EVT_SIZE, self.OnSize)
    
    def OnSize(self, event):
        self.imgVerrouillage.SetPosition((2, self.GetClientSize()[1]+1-18))
        self.texteVerrouillage.SetPosition((14, self.GetClientSize()[1]-18))
        event.Skip()
        
    def SetLabelHyperlink(self):
        if self.afficheHyperlink == False : return
        password = FonctionsPerso.Parametres(mode="get", categorie="recrutement", nom="password_entretien", valeur="")
        if VERROUILLAGE == True :
            self.texteVerrouillage.SetLabel(_(u"Cliquez ici pour déverrouiller l'affichage"))
        else:
            if password == "" :
                self.texteVerrouillage.SetLabel(_(u"Cliquez ici pour définir un code de verrouillage de l'affichage"))
            else:
                self.texteVerrouillage.SetLabel(_(u"Cliquez ici pour verrouiller l'affichage"))
        
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
        self.Importation_candidats()
        self.Importation_personnes() 
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
##        
##        def GetListeAffectations(dictFiltres):
##            """ Recherche des affectations """
##            listeTemp = []
##            for IDcandidature, listeAffectations in DICT_CAND_AFFECTATIONS.iteritems() :
##                for ID, label in dictFiltres["valeur"] :
##                    if ID in listeAffectations :
##                        if IDcandidature not in listeTemp :
##                            listeTemp.append(IDcandidature)
##            return listeTemp
        
        # ------------------------------------------------------------------------------------------------------------------------
        nbreFiltres = 0
        criteresSQL = ""
        listeListes = []
        for dictFiltres in listeFiltres :
            
            if dictFiltres["nomControle"] == "candidature_dispo" : 
                listeListes.append(GetListeDisponibilites(dictFiltres))
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
        if self.IDcandidat != None and self.IDcandidat != 0 :
            self.criteres = "WHERE IDcandidat=%d" % self.IDcandidat
        if self.IDpersonne != None and self.IDpersonne != 0 :
            self.criteres = "WHERE IDpersonne=%d" % self.IDpersonne
        if self.prochainsEntretiens == True :
            self.criteres = "WHERE date>='%s'" % datetime.date.today()
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
        req = """SELECT IDentretien, IDcandidat, date, heure, avis, remarques, IDpersonne 
        FROM entretiens %s ORDER BY date, heure; """ % self.criteres
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
                if track.nom_candidat != "":
                    listeListeView.append(track)
                    if self.selectionID == item[0] :
                        self.selectionTrack = track
        return listeListeView

    def Importation_candidats(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDcandidat, civilite, nom, prenom
        FROM candidats ORDER BY nom, prenom; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global NOMS_CANDIDATS
        NOMS_CANDIDATS = {}
        for IDcandidat, civilite, nom, prenom in listeDonnees :
            NOMS_CANDIDATS[IDcandidat] = (civilite, nom, prenom)

    def Importation_personnes(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDpersonne, civilite, nom, prenom
        FROM personnes ORDER BY nom, prenom; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global NOMS_PERSONNES
        NOMS_PERSONNES = {}
        for IDpersonne, civilite, nom, prenom in listeDonnees :
            NOMS_PERSONNES[IDpersonne] = (civilite, nom, prenom)
                        
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        if self.GetParent().GetName() == "gadget" :
            self.oddRowsBackColor = wx.Colour(214, 223, 247) # wx.Colour(255, 255, 255) #"#EEF4FB" # Bleu
            self.evenRowsBackColor = wx.Colour(214, 223, 247) #"#F0FBED" # Vert
        else:
            self.oddRowsBackColor = "#EEF4FB" # wx.Colour(255, 255, 255) #"#EEF4FB" # Bleu
            self.evenRowsBackColor = wx.Colour(255, 255, 255) #"#F0FBED" # Vert
        self.useExpansionColumn = True
        
        # Images
        if self.modeAffichage != "gadget" :
            imagelist = wx.ImageList(22, 22)
            self.imgCadenas= imagelist.Add(wx.Bitmap(Chemins.GetStaticPath("Images/22x22/Cadenas.png"), wx.BITMAP_TYPE_PNG))
            self.imgAvis0= imagelist.Add(wx.Bitmap(Chemins.GetStaticPath("Images/22x22/Smiley_question.png"), wx.BITMAP_TYPE_PNG))
            self.imgAvis1= imagelist.Add(wx.Bitmap(Chemins.GetStaticPath("Images/22x22/Smiley_nul.png"), wx.BITMAP_TYPE_PNG))
            self.imgAvis2= imagelist.Add(wx.Bitmap(Chemins.GetStaticPath("Images/22x22/Smiley_bof.png"), wx.BITMAP_TYPE_PNG))
            self.imgAvis3= imagelist.Add(wx.Bitmap(Chemins.GetStaticPath("Images/22x22/Smiley_bien.png"), wx.BITMAP_TYPE_PNG))
            self.imgAvis4= imagelist.Add(wx.Bitmap(Chemins.GetStaticPath("Images/22x22/Smiley_genial.png"), wx.BITMAP_TYPE_PNG))
            self.SetImageLists(smallImageList=imagelist)
        
        # Formatage des données
        def ImageGetter_avis(track):
            if VERROUILLAGE == True :
                return self.imgCadenas
            if track.avis == 0 : return self.imgAvis0
            elif track.avis == 1 : return self.imgAvis1
            elif track.avis == 2 : return self.imgAvis2
            elif track.avis == 3 : return self.imgAvis3
            elif track.avis == 4 : return self.imgAvis4
            else: return self.imgAvis0
        
        def FormateLabelAvis(avis):
            if avis == 0 : return _(u"Avis inconnu")
            if avis == 1 : return _(u"Pas convaincant")
            if avis == 2 : return _(u"Mitigé")
            if avis == 3 : return _(u"Bien")
            if avis == 4 : return _(u"Très bien")
            if avis == 999 : return _(u"Avis verrouillé")
            else: return ""
            
        def FormateDate(dateStr):
            if dateStr == "" or dateStr == None : return ""
            date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text
        
        def FormateHeure(dateStr):
            text = dateStr.replace(":", "h")
            return text
        
        def FormateDateHeure(dateStr):
            date, heure = dateStr.split(";")
            text = FormateDate(date) + " " + FormateHeure(heure)
            return text
        
        def FormateDateHeureNom(dateStr):
            date, heure, nom = dateStr.split(";")
            text = FormateDate(date) + " " + FormateHeure(heure) + " : " + nom
            return text
        
        def rowFormatter(listItem, track):
            if track.IDpersonne != None and track.IDpersonne != 0 :
                listItem.SetTextColour(wx.RED)
        
        if self.colorerSalaries == True :
            self.rowFormatter = rowFormatter
        
        # Création des colonnes
        liste_ColonnesTmp = self.listeColonnes
        # Tri par ordre
        liste_ColonnesTmp.sort(key=operator.itemgetter(7))
        
        liste_Colonnes = []
        for labelCol, alignement, largeur, nomChamp, args, description, affiche, ordre in liste_ColonnesTmp :
            if affiche == True :
                if args == "date" :
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp, stringConverter=FormateDate)
                elif args == "heure" :
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp, stringConverter=FormateHeure)
                elif args == "date_heure" :
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp, stringConverter=FormateDateHeure)
                elif args == "date_heure_nom" :
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp, stringConverter=FormateDateHeureNom)
                elif args == "image_avis" :
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp, stringConverter=FormateLabelAvis, imageGetter=ImageGetter_avis)
                else:
                    colonne = ColumnDefn(labelCol, alignement, largeur, nomChamp)
                liste_Colonnes.append(colonne)
        
        self.SetColumns(liste_Colonnes)

        self.SetSortColumn(self.columns[1])
        self.SetEmptyListMsg(_(u"Aucun entretien"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetObjects(self.donnees)
        
       
    def MAJ(self, IDcandidat=None, presents=None):
        if IDcandidat != None :
            self.selectionID = IDcandidat
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
        # Affichage et MAJ de l'hyperlink
        if self.afficheHyperlink == True :
            if len(self.donnees)>0 :
                self.imgVerrouillage.Show(True)
                self.texteVerrouillage.Show(True)
                self.SetLabelHyperlink() 
            else:
                self.imgVerrouillage.Show(False)
                self.texteVerrouillage.Show(False)
    
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
            ID = self.Selection()[0].IDcandidat
                
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
        
        # Item Verrouillage
        if VERROUILLAGE == True :
            item = wx.MenuItem(menuPop, 120, _(u"Déverrouillage"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cadenas.png"), wx.BITMAP_TYPE_PNG)
        else:
            item = wx.MenuItem(menuPop, 120, _(u"Verrouillage"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cadenas_ferme.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Verrouillage, id=120)
        
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

    def Menu_Verrouillage(self, event):
        self.GestionVerrouillage(MAJ=True)
        
    def Menu_Rechercher(self, event):
        self.Rechercher()
        
    def Menu_AfficherTout(self, event):
        self.AfficherTout()
        
    def Menu_Options(self, event):
        self.Options()

    def Menu_Aide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")
        
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
        dlg = DLG_Filtre_recrutement.MyDialog(self, categorie="entretiens", listeValeursDefaut=self.listeFiltres, title=_(u"Sélection de filtres de liste"))
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
                    self.GetGrandParent().GetParent().label_selection.Refresh()
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
            
        dlg = DLG_Saisie_entretien.Dialog(self, IDentretien=None, IDcandidat=IDcandidat, IDpersonne=IDpersonne)
        dlg.ShowModal()
        dlg.Destroy()

    def Modifier(self):
        
        try :
            if self.GetGrandParent().GetParent().GetName() == "Recrutement" :
                self.GetGrandParent().GetParent().AffichePanelResume(False)
        except : 
            pass
            
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un entretien à modifier dans la liste"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDentretien = self.Selection()[0].IDentretien
        IDcandidat = self.Selection()[0].IDcandidat
        IDpersonne = self.Selection()[0].IDpersonne
        
        # Si verrouillage :
        if VERROUILLAGE == True :
            self.GestionVerrouillage(MAJ=True)
            if VERROUILLAGE == True :
                return
            
        dlg = DLG_Saisie_entretien.Dialog(self, IDentretien=IDentretien, IDcandidat=IDcandidat, IDpersonne=IDpersonne)
        dlg.ShowModal()
        dlg.Destroy()

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

        # Demande de confirmation
        texte = self.Selection()[0].date
        nom_complet = self.Selection()[0].nom_candidat
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer l'entretien du %s pour %s ?") % (FonctionsPerso.DateEngFr(texte), nom_complet)))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        IDentretien = self.Selection()[0].IDentretien

        # Suppression
        DB = GestionDB.DB()
        DB.ReqDEL("entretiens", "IDentretien", IDentretien)
        DB.Close()
        
        # MàJ
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
                self.GetGrandParent().MAJlabelsPages("entretiens")
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
            style = wx.FD_SAVE
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
        labels_colonnes, liste_valeurs = self.GetValeurs()
        from Utils import UTILS_Excel
        UTILS_Excel.Excel(self, labels_colonnes, liste_valeurs)

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

    def GestionVerrouillage(self, MAJ=False):
        global VERROUILLAGE

        # Récup du mot de passe
        password = FonctionsPerso.Parametres(mode="get", categorie="recrutement", nom="password_entretien", valeur="")
        
        if VERROUILLAGE == True :
            
            # Déverrouiller
            dlg = SaisiePassword(self)  
            if dlg.ShowModal() == wx.ID_OK:
                pwd = dlg.GetPassword()
                if pwd == password :
                    VERROUILLAGE = False
                else:
                    dlg2 = wx.MessageDialog(self, _(u"Votre mot de passe est erroné."), _(u"Mot de passe erroné"), wx.OK | wx.ICON_ERROR)
                    dlg2.ShowModal()
                    dlg2.Destroy()
                dlg.Destroy()
            else:
                dlg.Destroy()
        
        else:
            
            # Verrouiller
            if password == "" :
                
                # si pas de mot de passe : on en créé un :
                from Dlg import DLG_Saisie_password_dialog
                texteIntro = _(u"Vous pouvez protéger l'accès aux informations liées aux entretiens \nd'embauche (avis et commentaires). Saisissez le mot de passe \nsouhaité à deux reprises pour activer cette protection :")
                dlg = DLG_Saisie_password_dialog.MyDialog(self, texteIntro=texteIntro)
                if dlg.ShowModal() == wx.ID_OK:
                    pwd = dlg.GetPassword()
                    password = FonctionsPerso.Parametres(mode="set", categorie="recrutement", nom="password_entretien", valeur=pwd)
                    dlg.Destroy()
                    VERROUILLAGE = True
                else:
                    dlg.Destroy()
                    
            else :
                # Si un mot de passe existe déjà, on verrouille juste l'affichage :
                VERROUILLAGE = True
        
        if MAJ == True :
            # MAJ du listView
            self.MAJ()

            # MAJ des autres listeView du panel Recrutement
            try :
                if self.GetParent().GetName() == "gadget" : 
                    self.GetGrandParent().GetGrandParent().MAJapresVerrouillage(OL_principal=True, OL_resume=True) 
                if self.GetGrandParent().GetName() == "panel_resume" : 
                    self.GetGrandParent().GetGrandParent().GetParent().MAJapresVerrouillage(OL_gadget=True, OL_principal=True)
                if self.GetGrandParent().GetParent().GetName() == "Recrutement" : 
                    self.GetGrandParent().GetParent().MAJapresVerrouillage(OL_gadget=True, OL_resume=True)
            except :
                pass
            
            

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
        nomDoc = UTILS_Fichiers.GetRepTemp("liste_entretiens.pdf")
        if "win" in sys.platform : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=landscape(A4))
        story = []

        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (620, 100) )
        dateDuJour = DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Liste des entretiens"), _(u"Edité le %s") % dateDuJour )  )
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
            largeursColonnes.append(largeur/2*1.7)
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

class Hyperlink(hl.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="test", infobulle="test infobulle", URL="", size=(-1, -1), pos=(0, 0)):
        hl.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        
        # Construit l'hyperlink
        self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.EnableRollover(True)
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink)
    
    def OnLeftLink(self, event):
        self.GetParent().GestionVerrouillage(MAJ=True)
        
# -------------------------------------------------------------------------------------------------------------------------------------------

class SaisiePassword(wx.Dialog):
    def __init__(self, parent, id=-1, title=_(u"Saisie du code de déverrouillage")):
        wx.Dialog.__init__(self, parent, id, title)
            
        self.sizer_3_staticbox = wx.StaticBox(self, -1, "")
        self.label_2 = wx.StaticText(self, -1, _(u"Les avis et commentaires sont verrouillés.\nPour les afficher, saisissez votre code de déverrouillage :"))
        self.label_password = wx.StaticText(self, -1, "Mot de passe :")
        self.text_password = wx.TextCtrl(self, -1, "", size=(200, -1), style=wx.TE_PASSWORD)
        
        self.label_3 = wx.StaticText(self, -1, _(u"Remarque : Le déverrouillage ne sera effectif que jusqu'à la fermeture du logiciel.\nPour désactiver définitivement la protection par mot de passe, rendez-vous dans \nle panneau Configuration (rubrique 'Recrutement')."))
        defaultFont = self.GetFont()
        defaultFont.SetPointSize(7)
        self.label_3.SetFont(defaultFont)
        
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, id=wx.ID_OK, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        self.text_password.SetToolTip(wx.ToolTip(_(u"Saisissez votre mot de passe ici")))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cadenas.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.__do_layout()

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
        grid_sizer_2.Add(self.label_3, 0, wx.ALL, 10)
        grid_sizer_4.Add((20, 20), 0, 0, 0)
        grid_sizer_4.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_4.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_4.AddGrowableCol(0)
        grid_sizer_2.Add(grid_sizer_4, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_2)
        grid_sizer_2.AddGrowableCol(0)
        grid_sizer_2.Fit(self)
        self.Layout()
        self.CentreOnScreen()

    def GetPassword(self):
        return self.text_password.GetValue()
    
    
# ---------------------------------------------------------------------------------------------------------------------------------------------


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
