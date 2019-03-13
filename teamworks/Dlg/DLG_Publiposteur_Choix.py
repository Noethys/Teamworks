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
import six
import FonctionsPerso
import GestionDB
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import wx.lib.agw.customtreectrl as CT
import wx.lib.agw.hyperlink as hl

from Ol import OL_personnes
from Ol import OL_contrats
from Ol import OL_candidats
from Ol import OL_candidatures


class TreeCtrl(CT.CustomTreeCtrl):
    def __init__(self, parent, listeDonnees=[], id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.SIMPLE_BORDER) :
        CT.CustomTreeCtrl.__init__(self, parent, id, pos, size, style)
        self.root = self.AddRoot("Root")
        self.listeDonnees = listeDonnees
##        listeDonnees = [ 
##            (_(u"Mathis"), [(10, _(u"Contrat1")), (20, _(u"Contrat 2"))],), 
##            ]
        
        
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | CT.TR_AUTO_CHECK_CHILD)
        self.EnableSelectionVista(True) 
        
        # Affiche les types de sources
        for nomGroupe, items in listeDonnees :
            item = self.AppendItem(self.root,  nomGroupe, ct_type=1)
            self.SetPyData(item, None)
            
            # Affiche la 2ème branche
            for ID, intitule in items :
                child = self.AppendItem(item,  intitule, ct_type=1)
                self.SetPyData(child, ID)
                
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
    
    
class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent, donnees):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        CheckListCtrlMixin.__init__(self)
        self.selectionsID = []
        self.listeColonnes, self.listeDonnees = donnees
        self.Remplissage() 
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)

    def OnCheckItem(self, index, flag):
        ID = self.GetItemData(index)
        if flag:
            if ID not in self.selectionsID :
                self.selectionsID.append(ID)
        else:
            self.selectionsID.remove(ID)
    
    def Remplissage(self):
        index = 0
        for intitule, largeur in self.listeColonnes :
            self.InsertColumn(index, intitule)
            self.SetColumnWidth(index, largeur)
            index += 1
        
        for donnees in self.listeDonnees :
            index = self.InsertStringItem(six.MAXSIZE, six.text_type(donnees[0]))
            for x in range(1, len(donnees)) :
                self.SetStringItem(index, x, six.text_type(donnees[x]))
            self.SetItemData(index, donnees[0])


class ToolBook(wx.Toolbook):
    def __init__(self, parent):
        wx.Toolbook.__init__(self, parent, id=-1, style=
                             wx.BK_DEFAULT
                             #wx.BK_TOP
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                            )

        # make an image list 
        il = wx.ImageList(32, 32)
        img1 = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images\\32x32\\Personnes.png"), wx.BITMAP_TYPE_PNG))
        img2 = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images\\32x32\\Contrats.png"), wx.BITMAP_TYPE_PNG))
        img3 = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images\\32x32\\Candidats.png"), wx.BITMAP_TYPE_PNG))
        img4 = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images\\32x32\\Mail.png"), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)
        
        # Now make a bunch of panels for the list book
        self.panelPersonnes = OL_personnes.ListView(self, id=-1,  name="OL_personnes", activeCheckBoxes=True, activeDoubleClic=False, activeMenuContextuel=False, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.panelContrats = OL_contrats.ListView(self, id=-1,  name="OL_contrats", activeCheckBoxes=True, activeDoubleClic=False, activeMenuContextuel=False, modeAffichage = "avec_nom", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.panelCandidats = OL_candidats.ListView(self, id=-1,  name="OL_candidats", activeCheckBoxes=True, activePopup=False, activeDoubleClic=False, activeMenuContextuel=False, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.panelCandidatures = OL_candidatures.ListView(self, id=-1,  name="OL_candidatures", activeCheckBoxes=True, activePopup=False, activeDoubleClic=False, activeMenuContextuel=False, modeAffichage = "avec_nom", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)

        self.panelPersonnes.SetMinSize((200, 50))
        self.panelContrats.SetMinSize((200, 50))
        self.panelCandidats.SetMinSize((200, 50))
        self.panelCandidatures.SetMinSize((200, 50))

        self.panelContrats.MAJ() 
        self.panelCandidats.MAJ() 
        self.panelCandidatures.MAJ() 
        
        self.AddPage(self.panelPersonnes, _(u"Personnes"), imageId=img1)
        self.AddPage(self.panelContrats, _(u"Contrats"), imageId=img2)
        self.AddPage(self.panelCandidats, _(u"Candidats"), imageId=img3)
        self.AddPage(self.panelCandidatures, _(u"Candidatures"), imageId=img4)
    
    def GetCategorie(self):
        indexPage = self.GetSelection()
        if indexPage == 0 : categorie = "personne"
        if indexPage == 1 : categorie = "contrat"
        if indexPage == 2 : categorie = "candidat"
        if indexPage == 3 : categorie = "candidature"
        return categorie
        
    def GetIDCoches(self):
        listeID = []
        
        if self.GetCategorie() == "personne" :
            for track in self.panelPersonnes.GetCheckedObjects() :
                listeID.append(track.IDpersonne)
                
        if self.GetCategorie() == "contrat" :
            for track in self.panelContrats.GetCheckedObjects() :
                listeID.append(track.IDcontrat)
                
        if self.GetCategorie() == "candidat" :
            for track in self.panelCandidats.GetCheckedObjects() :
                listeID.append(track.IDcandidat)
                
        if self.GetCategorie() == "candidature" :
            for track in self.panelCandidatures.GetCheckedObjects() :
                listeID.append(track.IDcandidature)

        listeID.sort()
        return listeID
    
    def Rechercher(self):
        if self.GetCategorie() == "personne" : self.panelPersonnes.Rechercher()
        if self.GetCategorie() == "candidat" : self.panelCandidats.Rechercher()
        if self.GetCategorie() == "candidature" : self.panelCandidatures.Rechercher()
        if self.GetCategorie() == "contrat" :
            dlg = wx.MessageDialog(self, _(u"Cette fonction n'est pas encore disponible pour la liste des contrats."), _(u"Fonction indisponible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

    def AfficherTout(self):
        if self.GetCategorie() == "personne" : self.panelPersonnes.AfficherTout()
        if self.GetCategorie() == "candidat" : self.panelCandidats.AfficherTout()
        if self.GetCategorie() == "candidature" : self.panelCandidatures.AfficherTout()
        if self.GetCategorie() == "contrat" :
            dlg = wx.MessageDialog(self, _(u"Cette fonction n'est pas encore disponible pour la liste des contrats."), _(u"Fonction indisponible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
            
    def ImportationPersonnes(self):
        """ Récupération des données """
        DB = GestionDB.DB()
        req = """SELECT IDpersonne, nom || ' ' || prenom, adresse_resid, cp_resid, ville_resid
        FROM personnes ORDER BY nom, prenom; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeColonnes = [(u"", 22), (_(u"Nom"), 150), (_(u"Adresse"), 160), (_(u"CP"), 50), (_(u"Ville"), 150)]
        return listeColonnes, listeDonnees

    def ImportationContrats(self):
        """ Récupération des données """
        DB = GestionDB.DB()
        req = """
        SELECT contrats.IDcontrat, personnes.nom || ' ' || personnes.prenom AS nomPersonne, contrats_class.nom, contrats_types.nom, date_debut, date_fin
        FROM contrats 
        LEFT JOIN personnes ON contrats.IDpersonne = personnes.IDpersonne
        LEFT JOIN contrats_class ON contrats_class.IDclassification = contrats.IDclassification 
        LEFT JOIN contrats_types ON contrats_types.IDtype = contrats.IDtype
        ORDER BY nomPersonne, date_debut
        """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeContrats = []
        dictGroupes = {}
        for IDcontrat, nomPersonne, classification, type, date_debut, date_fin in listeDonnees :
            texteContrat = _(u"%s %s du %s au %s") % (type, classification, FonctionsPerso.DateEngFr(date_debut), FonctionsPerso.DateEngFr(date_fin))
            if nomPersonne in dictGroupes :
                dictGroupes[nomPersonne].append( (IDcontrat, texteContrat) )
            else:
                dictGroupes[nomPersonne] = [ (IDcontrat, texteContrat), ]
        listeKeys = list(dictGroupes.keys())
        listeKeys.sort()
        for key in listeKeys:
            listeContrats.append( (key, dictGroupes[key]) )
        return listeContrats

                                    
    def ImportationCandidats(self):
        """ Récupération des données """
        DB = GestionDB.DB()
        req = """SELECT IDcandidat, nom || ' ' || prenom, adresse_resid, cp_resid, ville_resid
        FROM candidats ORDER BY nom, prenom; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeColonnes = [(u"", 22), (_(u"Nom"), 150), (_(u"Adresse"), 160), (_(u"CP"), 50), (_(u"Ville"), 150)]
        return listeColonnes, listeDonnees        

    def ImportationCandidatures(self):
        """ Récupération des données """
        DB = GestionDB.DB()
        req = """
        SELECT candidatures.IDcontrat, cabdacontrats_class.nom, contrats_types.nom, date_debut, date_fin
        FROM candidatures 
        LEFT JOIN candidats ON candidats.IDcandidat = candidatures.IDcandidat
        LEFT JOIN contrats_class ON contrats_class.IDclassification = contrats.IDclassification 
        LEFT JOIN contrats_types ON contrats_types.IDtype = contrats.IDtype
        ORDER BY nomPersonne, date_debut
        """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeContrats = []
        dictGroupes = {}
        for IDcandidature, nomCandidat, classification, type, date_debut, date_fin in listeDonnees :
            texteContrat = _(u"%s %s du %s au %s") % (type, classification, FonctionsPerso.DateEngFr(date_debut), FonctionsPerso.DateEngFr(date_fin))
            if nomPersonne in dictGroupes :
                dictGroupes[nomPersonne].append( (IDcontrat, texteContrat) )
            else:
                dictGroupes[nomPersonne] = [ (IDcontrat, texteContrat), ]
        listeKeys = list(dictGroupes.keys())
        listeKeys.sort()
        for key in listeKeys:
            listeContrats.append( (key, dictGroupes[key]) )
        return listeContrats

## "candidatures":[         ("IDcandidature", "INTEGER PRIMARY KEY AUTOINCREMENT", _(u"ID"), _(u"ID de la candidature")),
##                                    ("IDcandidat", "INTEGER", _(u"IDcandidat"), _(u"ID du candidat")),
##                                    ("IDpersonne", "INTEGER", _(u"IDpersonne"), _(u"ID du salarié")),
##                                    ("date_depot", "DATE", _(u"Date de la candidature"), _(u"Date de la candidature")),
##                                    ("IDtype", "INTEGER", _(u"IDtype"), _(u"ID du type de candidature")),
##                                    ("acte_remarques", "VARCHAR(300)", _(u"Remarques"), _(u"Remarques sur le dépôt de candidature")),
##                                    ("IDemploi", "INTEGER", _(u"IDemploi"), _(u"ID de l'emploi")),
##                                    ("periodes_remarques", "VARCHAR(300)", _(u"Remarques"), _(u"Remarques sur les disponibilités")),
##                                    ("poste_remarques", "VARCHAR(300)", _(u"Remarques"), _(u"Remarques sur le poste de la candidature")),
##                                    ("IDdecision", "INTEGER", _(u"IDdecision"), _(u"ID de la décision")),
##                                    ("decision_remarques", "VARCHAR(300)", _(u"Remarques"), _(u"Remarques sur la décision")),
##                                    ("reponse_obligatoire", "INTEGER", _(u"Reponse obligatoire"), _(u"Réponse obligatoire (0 ou 1)")),
##                                    ("reponse", "INTEGER", _(u"Reponse"), _(u"Réponse de la candidature (0 ou 1)")),
##                                    ("date_reponse", "DATE", _(u"Date de la réponse"), _(u"Date de la réponse")),
##                                    ("IDtype_reponse", "INTEGER", _(u"IDtype"), _(u"ID du type de réponse")),
##                                    ], # Liste des candidatures du candidat
                                    

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.panel = wx.Panel(self, -1)
        
        self.label_intro = wx.StaticText(self.panel, -1, _(u"Veuillez sélectionner une catégorie de données puis cochez les données à utiliser :"))
        self.sizer_staticbox = wx.StaticBox(self.panel, -1, u"")
        
        # Panel
        self.toolBook = ToolBook(self.panel)
        self.toolBook.SetMinSize((500, 400))
        
        # Commandes
        self.imgFiltrer = wx.StaticBitmap(self.panel, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_ANY))
        self.texteFiltrer = Hyperlink(self.panel, id=100,  label=_(u"Rechercher"), infobulle=_(u"Rechercher"))
        self.imgActualiser = wx.StaticBitmap(self.panel, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser.png"), wx.BITMAP_TYPE_ANY))
        self.texteActualiser = Hyperlink(self.panel, id=200, label=_(u"Afficher tout"), infobulle=_(u"Afficher tout"))
        
        # Boutons de commande
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)

    def __set_properties(self):
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler la saisie")))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.SetMinSize((750, 600))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        grid_sizer_base.Add(self.label_intro, 0, wx.LEFT|wx.TOP|wx.RIGHT, 10)
        
        sizer_contenu = wx.StaticBoxSizer(self.sizer_staticbox, wx.VERTICAL)
        sizer_contenu.Add(self.toolBook, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
        
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=7, vgap=0, hgap=0)
        grid_sizer_commandes.Add((5, 5), 0, wx.EXPAND|wx.ALL, 2)
        grid_sizer_commandes.Add(self.imgFiltrer, 0, wx.ALL, 2)
        grid_sizer_commandes.Add(self.texteFiltrer, 0, wx.ALL, 2)
        grid_sizer_commandes.Add((5, 5), 0, wx.EXPAND|wx.ALL, 2)
        grid_sizer_commandes.Add(self.imgActualiser, 0, wx.ALL, 2)
        grid_sizer_commandes.Add(self.texteActualiser, 0, wx.ALL, 2)
        grid_sizer_commandes.Add((5, 5), 0, wx.EXPAND|wx.ALL, 2)
        grid_sizer_commandes.AddGrowableCol(0)
        sizer_contenu.Add(grid_sizer_commandes, 0, wx.EXPAND|wx.BOTTOM, 5)
        
        grid_sizer_base.Add(sizer_contenu, 1, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        
        self.panel.SetSizer(grid_sizer_base)
        sizer_base.Add(self.panel, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()
                    
    def OnBoutonAide(self, event):
        dlg = wx.MessageDialog(self, _(u"L'aide pour ce nouveau module est en cours de rédaction."), _(u"Aide indisponible"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        #FonctionsPerso.Aide(47)

    def Onbouton_annuler(self, event):
        self.EndModal(wx.ID_CANCEL)
        
    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        categorie = self.toolBook.GetCategorie() 
        listeID = self.toolBook.GetIDCoches()
        
        if len(listeID) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez coché aucun élément."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Récupère les données pour le publipostage
        from Utils import UTILS_Publipostage_donnees
        dictDonnees = UTILS_Publipostage_donnees.GetDictDonnees(categorie, listeID)

        # Ouvre le publiposteur
        from Dlg import DLG_Publiposteur
        dlg = DLG_Publiposteur.Dialog(None, "", dictDonnees=dictDonnees)
        dlg.ShowModal()
        dlg.Destroy()

        # Fermeture
        self.EndModal(wx.ID_OK)


class Hyperlink(hl.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="test", infobulle="test infobulle", URL="", size=(-1, -1), pos=(0, 0)):
        hl.HyperLinkCtrl.__init__(self, parent, id=id, label=label, URL=URL, size=size, pos=pos)
        
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
        if event.GetId() == 100 : self.GetGrandParent().toolBook.Rechercher()
        if event.GetId() == 200 : self.GetGrandParent().toolBook.AfficherTout()

    
if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
