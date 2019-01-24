#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

from UTILS_Traduction import _
import datetime
import wx
import CTRL_Bouton_image
import GestionDB
import operator
import FonctionsPerso
import FicheIndividuelle
import os
import sys

from ObjectListView import ObjectListView, ColumnDefn

try: import psyco; psyco.full()
except: pass

DICT_PAYS = {}
DICT_SITUATIONS = {}
DICT_COORDONNEES = {}
DICT_QUALIFICATIONS = {}
DICT_TYPES_DIPLOMES = {}

LISTE_COLONNES = [
            [u"", "left", 22, "IDpersonne", "image_civilite", _(u"ID de la personne"), True, 1 ],
            [_(u"Civilité"), "left", 50, _(u"civilite"), "", _(u"Civilité"), True, 2 ],
            [_(u"Nom"), "left", 120, "nom", "", _(u"Nom de famille"), True, 3 ],
            [_(u"Nom de jeune fille"), "left", 120, "nom_jfille", "", _(u"Nom de jeune fille"), False, 4 ],
            [_(u"Prénom"), "left", 120, "prenom", "", _(u"Prénom"), True, 5 ],
            [_(u"Âge"), "left", 50, "age", "", _(u"Âge"), True, 6 ],
            [_(u"Qualifications"), "left", 90, "qualifications", "", _(u"Qualifications"), True, 7 ],
            [_(u"Date naiss."), "left", 70, "date_naiss", "date" , _(u"Date de naissance"), True, 8 ],
            [_(u"CP naiss."), "left", 60, "cp_naiss", "", _(u"Code postal de la ville de naissance"), True, 9 ],
            [_(u"Ville naiss."), "left", 110, "ville_naiss", "", _(u"Nom de la ville de naissance"), True, 10 ],
            [_(u"Pays naiss."), "left", 80, "nom_pays_naiss", "", _(u"Nom du pays de naissance"), False, 11 ],
            [_(u"Nationalité"), "left", 90, "nom_nationalite",  "", _(u"Nationalité"), False, 12 ],
            [_(u"Num. sécurité sociale"), "left", 130, "num_secu", "", _(u"Numéro de sécurité sociale"), True, 13 ],
            [_(u"Adresse"), "left", 160, "adresse_resid",  "", _(u"Adresse de résidence"), True, 14 ],
            [_(u"CP"), "left", 50, "cp_resid",  "", _(u"Code postal de la ville de résidence"), True, 15 ],
            [_(u"Ville"), "left", 110, "ville_resid",  "", _(u"Nom de la ville de résidence"), True, 16 ],
            [_(u"Téléphones"), "left", 200, "telephones", "", _(u"Numéros de téléphones"), True, 17 ],
            [_(u"Email"), "left", 150, "email", "", _(u"Adresses emails"), True, 18 ],
            [_(u"Fax"), "left", 150, "fax", "", _(u"Numéros de fax"), False, 19 ],            
            [_(u"Situation"), "left", 100, "nom_situation",  "", _(u"Situation sociale"), True, 20 ],
##            [_(u"Etat du dossier"), "left", 200, "dossier",  "", _(u"Etat du dossier"), True, 20 ],
            ] # nom Colonne, alignement, largeur, nom Champ, Args pour OLV, Description, Affiché ?, Ordre
            

# ---------------------------------------- LISTVIEW PERSONNES  -----------------------------------------------------------------------


class Track(object):
    def __init__(self, donnees):
        self.IDpersonne = donnees[0]
        self.civilite = donnees[1]
        self.nom = donnees[2]
        self.nom_jfille = donnees[3] 
        self.prenom = donnees[4]
        self.date_naiss = donnees[5]
        self.age = self.RetourneAge(self.date_naiss)
        self.cp_naiss = donnees[6]
        self.ville_naiss = donnees[7]
        self.pays_naiss = donnees[8]
        self.nom_pays_naiss = DICT_PAYS[self.pays_naiss][0]
        self.nationalite = donnees[9]
        self.nom_nationalite = DICT_PAYS[self.nationalite][1]
        self.num_secu = donnees[10]
        self.adresse_resid = donnees[11]
        self.cp_resid = donnees[12]
        self.ville_resid = donnees[13]
        self.IDsituation = donnees[14]
        self.nom_situation = self.GetNomSituation(self.IDsituation)
        self.telephones = self.GetCoordonnees(self.IDpersonne, type="telephone")
        self.email = self.GetCoordonnees(self.IDpersonne, type="email")
        self.fax = self.GetCoordonnees(self.IDpersonne, type="fax")
        self.qualifications = self.GetQualifications(self.IDpersonne)
##        self.dossier = self.GetPbDossier(self.IDpersonne)
        
            
    def RetourneAge(self, dateStr):
        if dateStr == "" or dateStr == None : return ""
        bday = datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10]))
        datedujour = datetime.date.today()
        age = (datedujour.year - bday.year) - int((datedujour.month, datedujour.day) < (bday.month, bday.day))
        texteAge = str(age) + " ans"
        return texteAge

    def GetNomSituation(self, IDsituation):
        if IDsituation == 0 or IDsituation == None :
            return ""
        else:
            return DICT_SITUATIONS[IDsituation]

    def GetCoordonnees(self, IDpersonne, type=""):
        if DICT_COORDONNEES.has_key(IDpersonne) == False :
            return ""
        listeCoordonnees = DICT_COORDONNEES[IDpersonne]
        txtCoords = ""
        nbreCoords = 0
        for IDcoord, IDpersonne, categorie, texte, intitule in listeCoordonnees :
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

    def GetPbDossier(self, IDpersonne):
        dictNoms, dictProblemes = FonctionsPerso.Creation_liste_pb_personnes()
        if dictProblemes.has_key(IDpersonne) == False : return ""
        dict2 = dictProblemes[IDpersonne]
        texte = ""
        for nomCategorie, listePb in dict2.iteritems() :
            for pb in listePb :
                texte += pb + ", "
        if len(dict2) > 0 :
            texte = texte[:-2]
        return texte

    def GetQualifications(self, IDcandidat):
        if DICT_QUALIFICATIONS.has_key(IDcandidat) == False :
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
        # Récupération des paramètres perso
        self.activeDoubleClic = kwds.pop("activeDoubleClic", True)
        self.activeCheckBoxes = kwds.pop("activeCheckBoxes", False)
        self.activeMenuContextuel = kwds.pop("activeMenuContextuel", True)
        self.selectionID = None
        self.selectionTrack = None
        self.presents = False
        self.criteres = ""
        self.itemSelected = False
        # Initialisation du listCtrl
        self.listeColonnes = LISTE_COLONNES
        self.listeColonnesOriginale = list(self.listeColonnes)
        ObjectListView.__init__(self, *args, **kwds)
        self.Importation_pays()
        self.InitModel()
        self.InitObjectListView()
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        if self.activeDoubleClic == True :
            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        if self.activeMenuContextuel == True :
            self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        
    def OnItemActivated(self,event):
        self.Modifier()
        
    def OnItemSelected(self, event):
        self.itemSelected = True
        try :
            self.GetGrandParent().GetParent().bouton_modifier.Enable(True)
            self.GetGrandParent().GetParent().bouton_supprimer.Enable(True)
            if len(self.Selection()) == 0:
                return False
            IDpersonne = self.Selection()[0].IDpersonne
            # Met à jour le cadre Résumé
            self.GetGrandParent().GetParent().panel_resume.OnSelectPersonne(IDpersonne=IDpersonne)
            self.GetGrandParent().GetParent().AffichePanelResume(True)
        except :
            pass
        
    def OnItemDeselected(self, event):
        self.itemSelected = False
        wx.FutureCall(100, self.DeselectionneItem)
    
    def DeselectionneItem(self) :
        if self.itemSelected == False :
            try :
                self.GetGrandParent().GetParent().bouton_modifier.Enable(False)
                self.GetGrandParent().GetParent().bouton_supprimer.Enable(False)
                self.GetGrandParent().GetParent().AffichePanelResume(False)
            except :
                pass
        self.itemSelected = False
        
    def InitModel(self):
        self.Importation_situations()
        self.Importation_coordonnees()
        self.Importation_qualifications() 
        self.Importation_types_diplomes() 
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        DB = GestionDB.DB()
        req = """SELECT IDpersonne, civilite, nom, nom_jfille, prenom, date_naiss, cp_naiss, ville_naiss, pays_naiss, nationalite, num_secu, adresse_resid, cp_resid, ville_resid, IDsituation
        FROM personnes %s ORDER BY nom, prenom; """ % self.criteres
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeListeView = []
        for item in listeDonnees :
            track = Track(item)
            listeListeView.append(track)
            if self.selectionID == item[0] :
                self.selectionTrack = track
        return listeListeView

    def Importation_pays(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDpays, nom, nationalite
        FROM pays; """
        DB.ExecuterReq(req)
        listePays = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global DICT_PAYS
        dictPays = {}
        for pays in listePays :
            DICT_PAYS[pays[0]] = (pays[1], pays[2])

    def Importation_situations(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDsituation, situation
        FROM Situations; """
        DB.ExecuterReq(req)
        listeSituations = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global DICT_SITUATIONS
        DICT_SITUATIONS = {}
        for situation in listeSituations :
            DICT_SITUATIONS[situation[0]] = situation[1]

    def Importation_coordonnees(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDcoord, IDpersonne, categorie, texte, intitule
        FROM Coordonnees; """
        DB.ExecuterReq(req)
        listeCoordonnees = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global DICT_COORDONNEES
        DICT_COORDONNEES = {}
        for IDcoord, IDpersonne, categorie, texte, intitule in listeCoordonnees :
            donnees = (IDcoord, IDpersonne, categorie, texte, intitule)
            if DICT_COORDONNEES.has_key(IDpersonne) :
                DICT_COORDONNEES[IDpersonne].append(donnees)
            else :
                DICT_COORDONNEES[IDpersonne] = [(donnees),]
                                    
    def Importation_qualifications(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDdiplome, IDpersonne, IDtype_diplome
        FROM diplomes; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Transforme liste en dict
        global DICT_QUALIFICATIONS
        DICT_QUALIFICATIONS = {}
        for IDdiplome, IDpersonne, IDtype_diplome in listeDonnees :
            if DICT_QUALIFICATIONS.has_key(IDpersonne) :
                DICT_QUALIFICATIONS[IDpersonne].append(IDtype_diplome)
            else:
                DICT_QUALIFICATIONS[IDpersonne] = [IDtype_diplome,]

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
        
    def InitObjectListView(self):
        # Images
        imgHomme = self.AddNamedImages("homme", wx.Bitmap("Images/16x16/Homme.png", wx.BITMAP_TYPE_PNG))
        imgFemme = self.AddNamedImages("femme", wx.Bitmap("Images/16x16/Femme.png", wx.BITMAP_TYPE_PNG))
        
        # Formatage des données
        def ImageGetter_civilite(track):
            if track.civilite == "Mr" : return imgHomme
            else: return imgFemme
            
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

        if self.activeCheckBoxes == True :
            self.CreateCheckStateColumn(0)
            self.SetSortColumn(self.columns[3])
        else:
            self.SetSortColumn(self.columns[2])
        self.SetEmptyListMsg(_(u"Aucune personne"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
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
    
    def Selection(self):
        return self.GetSelectedObjects()
    
    def SetListeColonnes(self, listeColonnes):
        self.listeColonnes = listeColonnes


# --------------------------------------------------------------------------------------------------------------------------------------------------






    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            return False
        ID = self.Selection()[0].IDpersonne
        
        # Récupération d'une adresse Email
        DB = GestionDB.DB()
        req = "SELECT texte FROM coordonnees WHERE IDpersonne = %d AND categorie='Email'" % ID
        DB.ExecuterReq(req)
        listeEmails = DB.ResultatReq()
        DB.Close()
        if len(listeEmails) != 0 :
            self.adresseMail = listeEmails[0][0]
        else:
            self.adresseMail = ""
        
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Modifier, id=20)

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)
        
        menuPop.AppendSeparator()
        
        # Item Envoyer un Mail
        if self.adresseMail != "" :
            item = wx.MenuItem(menuPop, 80, _(u"Envoyer un Email"))
            bmp = wx.Bitmap("Images/16x16/Mail.png", wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Menu_Mail, id=80)
        
        # Item Publipostage
        item = wx.MenuItem(menuPop, 140, _(u"Créer un courrier ou un mail par publipostage"))
        bmp = wx.Bitmap("Images/16x16/Mail.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Courrier, id=140)

        menuPop.AppendSeparator()
        
        # Item Rechercher Présents
        item = wx.MenuItem(menuPop, 40, _(u"Rechercher les présents"))
        bmp = wx.Bitmap("Images/16x16/Calendrier3jours.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Rechercher, id=40)

        # Item Afficher tout
        item = wx.MenuItem(menuPop, 50, _(u"Afficher tout"))
        bmp = wx.Bitmap("Images/16x16/Actualiser.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_AfficherTout, id=50)
        
        # Item Options
        item = wx.MenuItem(menuPop, 60, _(u"Options de liste"))
        bmp = wx.Bitmap("Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Options, id=60)
        
        menuPop.AppendSeparator()
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 90, _(u"Imprimer la liste"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuImprimer, id=90)
        
        # Item Export Texte
        item = wx.MenuItem(menuPop, 100, _(u"Exporter la liste au format Texte"))
        bmp = wx.Bitmap("Images/16x16/Document.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuExportTexte, id=100)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 110, _(u"Exporter la liste au format Excel"))
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.MenuExportExcel, id=110)
        
        menuPop.AppendSeparator()

        # Item Aide
        item = wx.MenuItem(menuPop, 70, _(u"Aide"))
        bmp = wx.Bitmap("Images/16x16/Aide.png", wx.BITMAP_TYPE_PNG)
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

    def Menu_Courrier(self, event):
        self.CourrierPublipostage()
        
    def Menu_AfficherTout(self, event):
        self.AfficherTout()
        
    def Menu_Options(self, event):
        self.Options()

    def Menu_Aide(self, event):
        self.GetGrandParent().GetParent().OnBoutonAide(None)
        
    def Menu_Mail(self, event):
        FonctionsPerso.EnvoyerMail(adresses = (self.adresseMail,))

    def AfficherTout(self):
        """ Réafficher toute la liste """
        try :
            self.GetGrandParent().GetParent().barreRecherche.OnCancel(None)
        except : pass
        self.criteres = ""
        self.MAJ()
            
    def Options(self):
        """ Choix et ordre des colonnes """
        import Config_liste_personnes
        frm = Config_liste_personnes.MyFrame(self, self.listeColonnes)
        frm.Show()

    def MenuImprimer(self, event):
        self.Imprimer()
        
    def MenuExportTexte(self, event):
        self.ExportTexte()
        
    def MenuExportExcel(self, event):
        self.ExportExcel()



    def Ajouter(self):
        frmFiche = FicheIndividuelle.MyFrame(self.GetParent(), IDpersonne=0)
        frmFiche.Show()

    def Modifier(self):
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une fiche personne à modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        IDpersonne = self.Selection()[0].IDpersonne
        frmFiche = FicheIndividuelle.MyFrame(self.GetParent(), IDpersonne=IDpersonne)
        frmFiche.Show()
                
    def Supprimer(self):
        if len(self.Selection()) == 0:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une fiche personne à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        IDpersonne = self.Selection()[0].IDpersonne
        
        # Vérifie qu'il n'y a aucun contrat enregistré pour cette personne
        DB = GestionDB.DB()
        req = """SELECT IDcontrat FROM contrats WHERE IDpersonne=%d;""" % IDpersonne
        DB.ExecuterReq(req)
        listeContrats = DB.ResultatReq()
        DB.Close()
        if len(listeContrats)>0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer une personne qui possède un ou plusieurs contrat(s).\n\nSi vous voulez vraiment supprimer cette fiche, vous devez d'abord supprimer le ou les contrat(s) de la personne."), "Information", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Vérifie qu'il n'y a aucune présence enregistrée pour cette personne
        DB = GestionDB.DB()
        req = """SELECT IDpresence FROM presences WHERE IDpersonne=%d;""" % IDpersonne
        DB.ExecuterReq(req)
        listePresences = DB.ResultatReq()
        DB.Close()
        if len(listePresences)>0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer une personne pour laquelle des présences ont déjà été enregistrées.\n\nSi vous voulez vraiment supprimer cette fiche, vous devez d'abord supprimer le ou les présence(s) de la personne."), "Information", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Vérifie qu'il n'y a aucun déplacement enregistré pour cette personne
        DB = GestionDB.DB()
        req = """SELECT IDdeplacement FROM deplacements WHERE IDpersonne=%d;""" % IDpersonne
        DB.ExecuterReq(req)
        listeDeplacements = DB.ResultatReq()
        DB.Close()
        if len(listeDeplacements)>0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer une personne pour laquelle des déplacements ont déjà été enregistrés.\n\nSi vous voulez vraiment supprimer cette fiche, vous devez d'abord supprimer le ou les déplacements(s) de la personne."), "Information", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Vérifie qu'il n'y a aucun remboursement enregistré pour cette personne
        DB = GestionDB.DB()
        req = """SELECT IDremboursement FROM remboursements WHERE IDpersonne=%d;""" % IDpersonne
        DB.ExecuterReq(req)
        listeRemboursements= DB.ResultatReq()
        DB.Close()
        if len(listeRemboursements)>0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer une personne pour laquelle des remboursements ont déjà été enregistrés.\n\nSi vous voulez vraiment supprimer cette fiche, vous devez d'abord supprimer le ou les remboursement(s) de la personne."), "Information", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Demande de confirmation
        Nom = self.Selection()[0].prenom + " " + self.Selection()[0].nom
        txtMessage = unicode((_(u"Voulez-vous vraiment supprimer cette identité ? \n\n> ") + Nom + _(u"\n\n\nAttention : Les coordonnées, diplômes ou pièces de cette personne seront également supprimés.")))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Suppression
        DB = GestionDB.DB()
        # Suppression de la fiche
        DB.ReqDEL("personnes", "IDpersonne", IDpersonne)
        # Suppression des coordonnées
        DB.ReqDEL("coordonnees", "IDpersonne", IDpersonne)
        # Suppression des diplômes
        DB.ReqDEL("diplomes", "IDpersonne", IDpersonne)
        # Suppression des pièces
        DB.ReqDEL("pieces", "IDpersonne", IDpersonne)
        
        DB.Close()

        # MàJ du ListCtrl
        self.MAJ()
        self.GetGrandParent().GetParent().AffichePanelResume(False)

    def Rechercher(self):
        """ Rechercher les présents sur une période donnée """
        if self.GetNbrePersonnes() == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune personne dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        import Selection_periode
        dlg = Selection_periode.SelectionPeriode(self)  
        if dlg.ShowModal() == wx.ID_OK:
            listePersonnesPresentes = dlg.GetPersonnesPresentes()
            datesSelection = dlg.GetDates()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        
        # S'il n'y a aucune personne présente sur la période sélectionnée
        if len(listePersonnesPresentes) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune personne présente sur la période que vous avez sélectionné."), _(u"Erreur"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Sélection dans le listView
        if len(listePersonnesPresentes) == 1 : listePersonnesPresentes = "(%d)" % listePersonnesPresentes[0]
        else : listePersonnesPresentes = str(tuple(listePersonnesPresentes))
        
        self.criteres = " WHERE IDpersonne IN %s " % listePersonnesPresentes
        self.MAJ()
        return datesSelection
    
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
    
    def GetNbrePersonnes(self):
        return len(self.donnees)

    def CourrierPublipostage(self, mode="unique"):
        if mode == "unique" :
            if len(self.Selection()) == 0:
                dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une personne dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            listeID = [self.Selection()[0].IDpersonne,]
        else:
            if self.GetNbreItems() == 0 :
                dlg = wx.MessageDialog(self, _(u"Il n'y a aucune personne dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            # Récupération des valeurs
            liste_labelsColonnes, listeValeurs = self.GetValeurs()
            # Selection des lignes
            import Selections_liste
            dlg = Selections_liste.MyFrame(self, liste_labelsColonnes, listeValeurs, type="exportTexte")
            if dlg.ShowModal() == wx.ID_OK:
                listeSelections = dlg.GetSelections()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return False
            listeID = listeSelections
        
        # Récupère les données pour le publipostage
        import Publipostage_donnees
        dictDonnees = Publipostage_donnees.GetDictDonnees(categorie="personne", listeID=listeID)
        # Ouvre le publiposteur
        import Publiposteur
        frm = Publiposteur.MyWizard(self, "", dictDonnees=dictDonnees)
        frm.Show()


    def ExportTexte(self):
        """ Export de la liste au format texte """
        if self.GetNbrePersonnes() == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune personne dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Récupération des valeurs
        liste_labelsColonnes, listeValeurs = self.GetValeurs()
        
        # Selection des lignes
        import Selections_liste
        dlg = Selections_liste.MyFrame(self, liste_labelsColonnes, listeValeurs, type="exportTexte")
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
        
        if self.GetNbrePersonnes() == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune personne dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Récupération des valeurs
        liste_labelsColonnes, listeValeurs = self.GetValeurs()
        
        # Selection des lignes
        import Selections_liste
        dlg = Selections_liste.MyFrame(self, liste_labelsColonnes, listeValeurs, type="exportExcel")
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
        if self.GetNbrePersonnes() == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune personne dans la liste !"), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        # Récupération des valeurs
        liste_labelsColonnes, listeValeurs = self.GetValeurs()
        
        # Selection des lignes
        import Selections_liste
        dlg = Selections_liste.MyFrame(self, liste_labelsColonnes, listeValeurs, type="imprimerListePersonnes")
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
        nomDoc = "Temp/liste_personnes.pdf"
        if "win" in sys.platform : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=landscape(A4))
        story = []

        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (620, 100) )
        dateDuJour = DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Liste de personnes"), _(u"Edité le %s") % dateDuJour )  )
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
            largeursColonnes.append(largeur/2)
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
                            ('ALIGN', (0,0), (-1,-1), 'LEFT'), # Titre du groupe à gauche
                            ('FONT',(0,0),(-1,-1), "Helvetica", 6), # Donne la police de caract. + taille de police 
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
        self.myOlv = ListView(panel, id=-1,  style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "ObjectListView")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
