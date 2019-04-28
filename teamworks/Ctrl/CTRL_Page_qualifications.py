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
from Utils import UTILS_Adaptations
from Dlg import DLG_Saisie_piece
import GestionDB
import datetime
import six


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateFrEng(textDate):
    text = str(textDate[6:10]) + "/" + str(textDate[3:5]) + "/" + str(textDate[:2])
    return text   

class Panel_Statut(wx.Panel):
    def __init__(self, parent, id, IDpersonne=0):
        wx.Panel.__init__(self, parent, id, style=wx.TAB_TRAVERSAL)

        self.parent = parent
        self.IDpersonne = IDpersonne

        # Widgets
        self.staticBox_pieces_staticbox = wx.StaticBox(self, -1, _(u"Pièces à fournir"))
        self.staticBox_dossier_staticbox = wx.StaticBox(self, -1, _(u"Pièces reçues"))
        self.staticBox_diplomes_staticbox = wx.StaticBox(self, -1, _(u"Qualifications"))

        self.list_ctrl_diplomes = ListCtrl_Diplomes(self, -1)
        self.list_ctrl_diplomes.SetMinSize((20, 20))
        self.list_ctrl_diplomes.SetBackgroundColour((236, 233, 216))

        self.list_ctrl_pieces = ListCtrl_Pieces(self, -1)
        self.list_ctrl_pieces.SetMinSize((20, 20))
        self.list_ctrl_pieces.SetBackgroundColour((236, 233, 216))
        
        self.list_ctrl_dossier = ListCtrl_Dossier(self, -1)
        self.list_ctrl_dossier.SetMinSize((20, 20))
        
        self.bouton_diplomes_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_dossier_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_dossier_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_dossier_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
        
        self.__set_properties()
        self.__do_layout()
        

    def __set_properties(self):
        self.bouton_diplomes_modifier.SetToolTip(wx.ToolTip("Cliquez ici pour modifier cette liste"))
        self.bouton_diplomes_modifier.SetSize(self.bouton_diplomes_modifier.GetBestSize())
        self.list_ctrl_pieces.SetToolTip(wx.ToolTip(_(u"Liste des pièces que la personne doit fournir. \n\nAstuce : Double-cliquez sur une ligne pour créer directement \nune pièce du type sélectionné dans la liste")))
        self.list_ctrl_diplomes.SetToolTip(wx.ToolTip(_(u"Cliquez sur le bouton 'Modifier' pour modifier cette liste")))
        self.bouton_dossier_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir une nouvelle pièce")))
        self.bouton_dossier_ajouter.SetSize(self.bouton_dossier_ajouter.GetBestSize())
        self.bouton_dossier_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la pièce sélectionnée dans la liste")))
        self.bouton_dossier_modifier.SetSize(self.bouton_dossier_modifier.GetBestSize())
        self.bouton_dossier_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la pièce sélectionnée")))
        self.bouton_dossier_supprimer.SetSize(self.bouton_dossier_supprimer.GetBestSize())

        # Evenements
        self.Bind(wx.EVT_BUTTON, self.OnBouton_Diplomes, self.bouton_diplomes_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjoutPiece, self.bouton_dossier_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifPiece, self.bouton_dossier_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprPiece, self.bouton_dossier_supprimer)

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        staticBox_dossier = wx.StaticBoxSizer(self.staticBox_dossier_staticbox, wx.VERTICAL)
        grid_sizer_dossier = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_dossier = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Pièces
        staticBox_pieces = wx.StaticBoxSizer(self.staticBox_pieces_staticbox, wx.VERTICAL)
        grid_sizer_pieces = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_pieces.Add(self.list_ctrl_pieces, 1, wx.EXPAND, 0)
        grid_sizer_pieces.AddGrowableRow(0)
        grid_sizer_pieces.AddGrowableCol(0)
        staticBox_pieces.Add(grid_sizer_pieces, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut.Add(staticBox_pieces, 1, wx.LEFT|wx.TOP|wx.EXPAND, 5)
        
        # Diplômes
        staticBox_diplomes = wx.StaticBoxSizer(self.staticBox_diplomes_staticbox, wx.VERTICAL)
        grid_sizer_diplomes = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_diplomes = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_diplomes.Add(self.list_ctrl_diplomes, 1, wx.EXPAND, 0)
        grid_sizer_boutons_diplomes.Add(self.bouton_diplomes_modifier, 0, 0, 0)
        grid_sizer_diplomes.Add(grid_sizer_boutons_diplomes, 1, wx.EXPAND, 0)
        grid_sizer_diplomes.AddGrowableRow(0)
        grid_sizer_diplomes.AddGrowableCol(0)
        staticBox_diplomes.Add(grid_sizer_diplomes, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_haut.Add(staticBox_diplomes, 1, wx.RIGHT|wx.TOP|wx.EXPAND, 5)
        
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableCol(0)
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.EXPAND, 0)
        
        # Dossier
        grid_sizer_dossier.Add(self.list_ctrl_dossier, 1, wx.EXPAND, 0)
        grid_sizer_boutons_dossier.Add(self.bouton_dossier_ajouter, 0, 0, 0)
        grid_sizer_boutons_dossier.Add(self.bouton_dossier_modifier, 0, 0, 0)
        grid_sizer_boutons_dossier.Add(self.bouton_dossier_supprimer, 0, 0, 0)
        grid_sizer_dossier.Add(grid_sizer_boutons_dossier, 1, wx.EXPAND, 0)
        grid_sizer_dossier.AddGrowableRow(0)
        grid_sizer_dossier.AddGrowableCol(0)
        staticBox_dossier.Add(grid_sizer_dossier, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticBox_dossier, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 5)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)

    def MAJ_barre_problemes(self):
        self.parent.GetGrandParent().MAJ_barre_problemes()
        
    def OnBouton_Diplomes(self, event):
        """ Boîte de dialogue pour choisir les diplômes """
        resultat = ""
        titre = _(u"Sélection des qualifications")

        # Récupération de la liste de tous les diplomes
        DB = GestionDB.DB()
        req = "SELECT IDtype_diplome, nom_diplome FROM types_diplomes ORDER BY nom_diplome"
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        DB.Close()

        # Création d'un dictionnaire diplomes et d'une liste pour la boîte de dialogue
        dictDiplomes = {}
        listeNoms = []
        preSelection = []
        TypesDiplomesPerso = []
        index = 0
        for diplome in donnees:
            ID = diplome[0]
            nom = diplome[1]
            dictDiplomes[index] = ID
            listeNoms.append(nom)
            # Recherche si est dans la liste de la personne
            if ID in self.list_ctrl_diplomes.listeDiplomes:
                preSelection.append(index)
                TypesDiplomesPerso.append(ID)
            index += 1
        message = _(u"Sélectionnez les qualifications que possède la personne dans la liste proposée :")
        dlg = wx.MultiChoiceDialog(self, message, titre, listeNoms, wx.CHOICEDLG_STYLE)
        
        # Coche ceux qui doivent être déjà sélectionnés dans la liste
        dlg.SetSelections(preSelection)
        
        # Résultats
        if dlg.ShowModal() == wx.ID_OK:
            resultat = dlg.GetSelections()
        else:
            return
        dlg.Destroy()
        
        # On cherche les nouveaux diplomes saisis
        listeAEnregistrer = []
        for diplome in resultat:
            IDtype_diplome = dictDiplomes[diplome]
            
            # On regarde si l'ID est déjà dans la liste des diplomes de la personne
            if IDtype_diplome in TypesDiplomesPerso:
                # On passe et on l'efface de la liste
                TypesDiplomesPerso.remove(IDtype_diplome)
            else:
                listeAEnregistrer.append(IDtype_diplome)

        # On enregistre les nouveaux
        if len(listeAEnregistrer) != 0:
            DB = GestionDB.DB()
            for IDtype in listeAEnregistrer:
                DB.ExecuterReq("INSERT INTO diplomes (IDpersonne, IDtype_diplome) VALUES (%d, %d)" % (self.IDpersonne, IDtype))
            DB.Commit()
            DB.Close()

        # On voit si certains ont été enlevés de la liste
        if len(TypesDiplomesPerso) != 0:
            DB = GestionDB.DB()
            for IDtype in TypesDiplomesPerso:
                DB.ExecuterReq("DELETE FROM diplomes WHERE IDpersonne=%d AND IDtype_diplome=%d" % (self.IDpersonne, IDtype))
            DB.Commit()
            DB.Close()

        # MAJ du ListCtrl des Diplomes
        self.list_ctrl_diplomes.Remplissage()
        self.list_ctrl_pieces.Remplissage()
        self.MAJ_barre_problemes()            

    def OnBoutonAjoutPiece(self, event):
        self.AjouterPiece()
        event.Skip()

    def AjouterPiece(self, IDtypePiece=None):
        dlg = DLG_Saisie_piece.Dialog(self, -1, IDpiece=0, IDpersonne=self.IDpersonne, IDtypePiece=IDtypePiece)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonModifPiece(self, event):
        self.ModifierPiece()
        event.Skip()

    def ModifierPiece(self):
        """ Modification de coordonnées """
        index = self.list_ctrl_dossier.GetFirstSelected()
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une pièce à modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        varIDpiece = self.list_ctrl_dossier.GetItemData(index)
        dlg = DLG_Saisie_piece.Dialog(self, -1, IDpiece=varIDpiece, IDpersonne=self.IDpersonne)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonSupprPiece(self, event):
        self.SupprimerPiece()
        event.Skip()
        
    def SupprimerPiece(self):
        """ Suppression d'une coordonnée """
        index = self.list_ctrl_dossier.GetFirstSelected()

        # Vérifie qu'un item a bien été sélectionné
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une pièce à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation
        textePiece = self.list_ctrl_dossier.GetItemText(index)
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer cette pièce ? \n\n> ") + textePiece))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        varIDpiece = self.list_ctrl_dossier.GetItemData(index)

        # Suppression
        DB = GestionDB.DB()
        DB.ReqDEL("pieces", "IDpiece", varIDpiece)

        # MàJ du listCtrl Coords de la fiche individuelle
        self.list_ctrl_dossier.Remplissage()
        self.list_ctrl_pieces.Remplissage()
        self.MAJ_barre_problemes()
        

# ----------- LISTCTRL DIPLOMES ---------------------------------------------------------------------------------------------------

class ListCtrl_Diplomes(wx.ListCtrl):
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, id, size=(80, -1), style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_NO_HEADER|wx.LC_SINGLE_SEL|wx.SUNKEN_BORDER)

        self.parent = parent
        self.IDpersonne = self.GetParent().IDpersonne

        
        # Création de la Colonne
        self.InsertColumn(0, "Qualification")
        self.SetColumnWidth(0, 75)

        # Création des items
        self.Remplissage()
        
        # Binds
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def Remplissage(self):
        """ Remplissage du ListCtrl """
        # Importation des données
        self.Importation()

        # S'il existe des items, on les efface d'abord
        if self.GetItemCount() != 0:
            self.DeleteAllItems()
            
        # Création des items
        index = 0
        for key, valeurs in self.DictDiplomes.items():
            IDdiplome = key
            IDtype_diplome = valeurs[0]
            self.listeDiplomes.append(IDtype_diplome)
            nom_diplome = valeurs[1]
            # Création de l'item
            if 'phoenix' in wx.PlatformInfo:
                self.InsertItem(index, nom_diplome)
            else:
                self.InsertStringItem(index, nom_diplome)
            # Intégration du data ID
            self.SetItemData(index, key)
            index += 1

        # Tri dans l'ordre alphabétique
        self.SortItems(self.ColumnSorter)

    def ColumnSorter(self, key1, key2):
        item1 = self.DictDiplomes[key1][1]
        item2 = self.DictDiplomes[key2][1]
        if item1 < item2:    
               return -1
        else:                   
               return 1


    def Importation(self):
        """ Importe les données des diplomes """

        self.DictDiplomes = {}
        self.listeDiplomes = [] # Pour la boîte de dialogue de choix des diplomes

        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        req = "SELECT IDdiplome, diplomes.IDtype_diplome, nom_diplome FROM diplomes, types_diplomes WHERE diplomes.IDtype_diplome=types_diplomes.IDtype_diplome and IDpersonne=%d" % self.IDpersonne
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        DB.Close()
        
        for ligne in donnees:
            index = ligne[0]
            self.DictDiplomes[index] = (ligne[1], ligne[2])
        
    def OnItemSelected(self, event):
        """ Item cliqué """
        index = self.GetFirstSelected()
        key = self.GetItemData(index)
        print(_(u"Click sur l'item ID : "), key)
        event.Skip()

    def OnItemActivated(self, event):
        """ Item double-cliqué """
        index = self.GetFirstSelected()
        key = self.GetItemData(index)
        print(_(u"Double-click sur l'item ID : "), key)
        event.Skip()
        
    def OnSize(self, event):
        # La largeur de la colonne s'adapte à la largeur du listCtrl
        size = self.GetSize()
        self.SetColumnWidth(0, size.x-25)
        event.Skip()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel du ListCtrl Diplomes."""
        
        if self.GetFirstSelected() == -1:
            return False
        index = self.GetFirstSelected()
        key = self.GetItemData(index)
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Edit.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Modifier, id=10)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    
    def Menu_Modifier(self, event):
        index = self.GetFirstSelected()
        key = self.GetItemData(index)
        print("Modifier le num : ", key)


      

# ----------- LISTCTRL PIECES ---------------------------------------------------------------------------------------------------


class ListCtrl_Pieces(wx.ListCtrl):
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, id, size=(180, -1), style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_HRULES|wx.LC_SINGLE_SEL|wx.SUNKEN_BORDER)

        self.parent = parent
        self.IDpersonne = self.GetParent().IDpersonne
        
        # ImageList
        self.il = wx.ImageList(16,16)
        self.imgOk = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))
        self.imgAttention = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Attention.png"), wx.BITMAP_TYPE_PNG))
        self.imgPasOk = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        # Colonnes
        self.InsertColumn(0, "")
        self.SetColumnWidth(0, 175)

        # Création des items
        self.Remplissage()

        # Binds
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def Remplissage(self):
        """ Remplissage du ListCtrl """
        # Importation des données
        self.Importation()

        # S'il existe des items, on les efface d'abord
        if self.GetItemCount() != 0:
            self.DeleteAllItems()
            
        # Création des items
        index = 0
        for key, valeurs in self.DictPieces.items():
            etat = valeurs[0]
            nomPiece = valeurs[1]
            # Création de l'item
            if 'phoenix' in wx.PlatformInfo:
                self.InsertItem(index, nomPiece)
            else:
                self.InsertStringItem(index, nomPiece)
            # Intégration de l'image
            if etat == "Ok":
                self.SetItemImage(index, self.imgOk)
            if etat == "Attention":
                self.SetItemImage(index, self.imgAttention)
            if etat == "PasOk":
                self.SetItemImage(index, self.imgPasOk)
            # Intégration du data ID
            self.SetItemData(index, key)
            index += 1

        # Tri dans l'ordre alphabétique
        self.SortItems(self.ColumnSorter)


    def ColumnSorter(self, key1, key2):
        item1 = self.DictPieces[key1][1]
        item2 = self.DictPieces[key2][1]
        if item1 < item2:    
               return -1
        else:                   
               return 1

    def Importation(self):
        """ Importe les données """

        date_jour = datetime.date.today()

        # Initialisation de la base de données
        DB = GestionDB.DB()
        
        # Recherche des pièces SPECIFIQUES que la personne doit fournir...
        req = """
        SELECT types_pieces.IDtype_piece, types_pieces.nom_piece
        FROM diplomes INNER JOIN diplomes_pieces ON diplomes.IDtype_diplome = diplomes_pieces.IDtype_diplome INNER JOIN types_pieces ON diplomes_pieces.IDtype_piece = types_pieces.IDtype_piece
        WHERE diplomes.IDpersonne=%d;
        """ % self.IDpersonne
        DB.ExecuterReq(req)
        listePiecesAFournir = DB.ResultatReq()
        
        # pour mysql :
        if type( listePiecesAFournir) != list :
            listePiecesAFournir = list(listePiecesAFournir)
        
        # Recherche des pièces BASIQUES que la personne doit fournir...
        req = """
        SELECT diplomes_pieces.IDtype_piece, types_pieces.nom_piece
        FROM diplomes_pieces INNER JOIN types_pieces ON diplomes_pieces.IDtype_piece = types_pieces.IDtype_piece
        WHERE diplomes_pieces.IDtype_diplome=0;
        """ 
        DB.ExecuterReq(req)
        listePiecesBasiquesAFournir = DB.ResultatReq()
        
        listePiecesAFournir.extend(listePiecesBasiquesAFournir)
        
        # Recherche des pièces que la personne possède
        req = """
        SELECT types_pieces.IDtype_piece, pieces.date_debut, pieces.date_fin
        FROM types_pieces LEFT JOIN pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
        WHERE (pieces.IDpersonne=%d AND pieces.date_debut<='%s' AND pieces.date_fin>='%s')
        ORDER BY pieces.date_fin;
        """ % (self.IDpersonne, date_jour, date_jour)
        DB.ExecuterReq(req)
        listePieces = DB.ResultatReq()
        dictTmpPieces = {}
        for IDtype_piece, date_debut, date_fin in listePieces :
            dictTmpPieces[IDtype_piece] = (date_debut, date_fin)
        
        # Passe en revue toutes les pièces à fournir et regarde si la personne possède les pièces correspondantes
        self.DictPieces = {}
        for IDtype_piece, nom_piece in listePiecesAFournir :
            if (IDtype_piece in dictTmpPieces) == True :
                date_debut = dictTmpPieces[IDtype_piece][0]
                date_fin = dictTmpPieces[IDtype_piece][1]
                # Recherche la validité
                date_fin = datetime.date(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]))
                reste = str(date_fin - date_jour)
                if reste != "0:00:00":
                    jours = int(reste[:reste.index("day")])
                    if jours < 15  and jours > 0:
                        etat = "Attention"
                    elif jours <= 0:
                        etat = "PasOk"
                    else:
                        etat = "Ok"
                else:
                    etat = "Attention"
            else:
                etat = "PasOk"
            self.DictPieces[IDtype_piece] = (etat, nom_piece)
        
##        # ---------------------------------------------------------------------------------------------------------------- Archives :
##        self.DictPieces = {}
##
##        # Recherche des pièces spécifiques
##        req = """
##        SELECT diplomes_pieces.IDtype_piece, types_pieces.nom_piece, Count(pieces.IDpiece) AS CompteDeIDpiece, Min(pieces.date_debut) AS MinDedate_debut, Max(pieces.date_fin) AS MaxDedate_fin, diplomes.IDpersonne 
##        FROM diplomes_pieces
##        INNER JOIN types_diplomes ON diplomes_pieces.IDtype_diplome = types_diplomes.IDtype_diplome
##        INNER JOIN types_pieces ON diplomes_pieces.IDtype_piece = types_pieces.IDtype_piece
##        INNER JOIN diplomes ON types_diplomes.IDtype_diplome = diplomes.IDtype_diplome
##        LEFT JOIN pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
##        GROUP BY diplomes.IDpersonne, diplomes_pieces.IDtype_piece, types_pieces.nom_piece
##        HAVING diplomes.IDpersonne=%d AND Min(pieces.date_debut)<='%s' AND Max(pieces.date_fin)>='%s' OR diplomes.IDpersonne=%d;
##        """ % (self.IDpersonne, date_jour, date_jour, self.IDpersonne)
##        DB.ExecuterReq(req)
##        listePiecesSpecif = DB.ResultatReq()
##        # Création du dictionnaire de données pour les pièces spécifiques
##        for piece in listePiecesSpecif:
##            IDtype_piece = piece[0]
##            nom_piece = piece[1]
##            nbre_pieces = piece[2]
##            date_debut = piece[3]
##            date_fin = piece[4]
##            # Recherche la validité
##            if nbre_pieces >0 :
##                date_fin = datetime.date(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]))
##                reste = str(date_fin - date_jour)
##                if reste != "0:00:00":
##                    jours = int(reste[:reste.index("day")])
##                    if jours < 15  and jours > 0:
##                        etat = "Attention"
##                    elif jours <= 0:
##                        etat = "PasOk"
##                    else:
##                        etat = "Ok"
##                else:
##                    etat = "Attention"
##            else:
##                etat = "PasOk"
##            self.DictPieces[IDtype_piece] = (etat, nom_piece)
        
        
##        # Recherche des pièces basiques (communes à tous les employés)
##        req = """
##        SELECT types_pieces.IDtype_piece, types_pieces.nom_piece, Count(pieces.IDpiece) AS CompteDeIDpiece, Min(pieces.date_debut) AS MinDedate_debut, Max(pieces.date_fin) AS MaxDedate_fin, pieces.IDpersonne
##        FROM diplomes_pieces
##        INNER JOIN types_pieces ON diplomes_pieces.IDtype_piece = types_pieces.IDtype_piece
##        LEFT JOIN pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece GROUP BY types_pieces.IDtype_piece, types_pieces.nom_piece, diplomes_pieces.IDtype_diplome, pieces.IDpersonne
##        HAVING (((diplomes_pieces.IDtype_diplome)=0) AND ((Min(pieces.date_debut))<='%s' Or (Min(pieces.date_debut)) Is Null) AND ((Max(pieces.date_fin))>='%s' Or (Max(pieces.date_fin)) Is Null) AND ((pieces.IDpersonne)=%d Or (pieces.IDpersonne) Is Null)) OR (((diplomes_pieces.IDtype_diplome)=0));
##        """ % (date_jour, date_jour, self.IDpersonne)
##        DB.ExecuterReq(req)
##        listePiecesBase = DB.ResultatReq()
##
##        # Création du dictionnaire de données pour les pièces basiques (communes à tous les employés)
##        for piece in listePiecesBase:
##            IDtype_piece = piece[0]
##            nom_piece = piece[1]
##            nbre_pieces = piece[2]
##            date_debut = piece[3]
##            date_fin = piece[4]
##
##            # Recherche la validité
##            if nbre_pieces >0 :
##                date_fin = datetime.date(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]))
##                reste = str(date_fin - date_jour)
##                if reste != "0:00:00":
##                    jours = int(reste[:reste.index("day")])
##                    if jours < 15 and jours > 0:
##                        etat = "Attention"
##                    elif jours <= 0:
##                        etat = "PasOk"
##                    else:
##                        etat = "Ok"
##                else:
##                    etat = "Attention"
##            else:
##                etat = "PasOk"
##            self.DictPieces[IDtype_piece] = (etat, nom_piece)
        
        # Fermeture de la base de données
        DB.Close()

    def OnSize(self, event):
        # La largeur de la colonne s'adapte à la largeur du listCtrl
        size = self.GetSize()
        self.SetColumnWidth(0, size.x-25)
        event.Skip()        

    def OnItemActivated(self, event):
        """ Saisie d'une pièce du type double-cliqué """
        index = self.GetFirstSelected()
        IDtypePiece = self.GetItemData(index)
        
        self.parent.AjouterPiece(IDtypePiece=IDtypePiece)
        
        

# ----------- LISTCTRL DOSSIER ---------------------------------------------------------------------------------------------------


class ListCtrl_Dossier(wx.ListCtrl):
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, id, size=(250, -1), style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.LC_SINGLE_SEL|wx.SUNKEN_BORDER) #wx.LC_NO_HEADER|

        self.parent = parent
        self.IDpersonne = self.GetParent().IDpersonne

        # Colonnes
        self.InsertColumn(0, _(u"Type de pièce"))
        self.SetColumnWidth(0, 260)
        self.InsertColumn(1, _(u"Obtention"))
        self.SetColumnWidth(1, 80)
        self.InsertColumn(2, _(u"Expiration"))
        self.SetColumnWidth(2, 80)
        self.InsertColumn(3, _(u"Observations"))
        self.SetColumnWidth(3, 180)

        self.il = wx.ImageList(16, 16)
        self.image_document = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document2.png"), wx.BITMAP_TYPE_PNG))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
                
        # Création des items
        self.Remplissage()

        # Binds
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def Remplissage(self):
        """ Remplissage du ListCtrl """
        # Importation des données
        self.Importation()

        # S'il existe des items, on les efface d'abord
        if self.GetItemCount() != 0:
            self.DeleteAllItems()
            
        # Création des items
        index = 0
        for key, valeurs in self.DictDossier.items():
            etat = valeurs[0]
            nomPiece = valeurs[1]
            dateDebut = DateEngFr(valeurs[2])
            dateFin = DateEngFr(valeurs[3])
            # Création de l'item
            if 'phoenix' in wx.PlatformInfo:
                self.InsertItem(index, nomPiece)
            else:
                self.InsertStringItem(index, nomPiece)
            # ETat
            if etat == "Perim":
                item = self.GetItem(index)
                item.SetTextColour("GREY")
                self.SetItem(item)
            
            # Image si document associé
            if key in self.dict_docs :
                self.nbre_documents = self.dict_docs[key]
            else:
                self.nbre_documents = 0
            if self.nbre_documents > 0 :
                self.SetItemImage(index, self.image_document)

            # Autres colonnes
            if dateFin == "01/01/2999":
                dateFin = _(u"Illimitée")
            self.SetItemImage(index, self.image_document)
            if 'phoenix' in wx.PlatformInfo:
                self.SetItem(index, 1, dateDebut)
                self.SetItem(index, 2, dateFin)
                self.SetItem(index, 3, self.etatExpiration(valeurs[2], valeurs[3]))
            else:
                self.SetItem(index, 1, dateDebut)
                self.SetItem(index, 2, dateFin)
                self.SetItem(index, 3, self.etatExpiration(valeurs[2], valeurs[3]))
            # Intégration du data ID
            self.SetItemData(index, key)
            index += 1

        # Tri dans l'ordre alphabétique
        self.SortItems(self.ColumnSorter)

        # Fait dérouler la liste
        nbreItems = self.GetItemCount()
        if nbreItems > 0:
            self.EnsureVisible(nbreItems-1) 

    def GetDocumentsScan(self):
        """ Retourne le nbre de documents scannés pour chaque pièce """
        DB = GestionDB.DB(suffixe="DOCUMENTS")
        req = "SELECT IDdocument, IDpiece FROM documents;"
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dictDocuments = {}
        for IDdocument, IDpiece in listeDonnees :
            if (IDpiece in dictDocuments) == False :
                dictDocuments[IDpiece] = 1
            else:
                dictDocuments[IDpiece] += 1
        return dictDocuments

    def etatExpiration(self, dateDebut, dateFin):
        """ Recherche l'état de l'expiration """

        # Si illimité
        if dateFin == "2999-01-01":
            return ""

        # Si non illimité
        dateJour = datetime.date.today()
        dateFin = datetime.date(int(dateFin[:4]), int(dateFin[5:7]), int(dateFin[8:10]))

        reste = str(dateFin - dateJour)
        if reste != "0:00:00":
            jours = int(reste[:reste.index("day")])
            if jours < 0:
                return _(u"Pièce expirée")
            elif jours == 1:
                return _(u"Expire demain !")
            else:
                return _(u"Expire dans %d jours") % jours
        else:
            return _(u"Expire aujourd'hui !")
        return "ok"

    def ColumnSorter(self, key1, key2):
        if 'phoenix' in wx.PlatformInfo:
            item1 = self.GetItem( self.FindItem(-1, key1), 2).GetText()
            item2 = self.GetItem( self.FindItem(-1, key2), 2).GetText()
        else:
            item1 = self.GetItem( self.FindItemData(-1, key1), 2).GetText()
            item2 = self.GetItem( self.FindItemData(-1, key2), 2).GetText()
        # Intercepte les illimités et les transforme en date très lointaine
        if item1 == _(u"Illimitée"):
            item1 = "01/01/2999"
        if item2 == _(u"Illimitée"):
            item2 = "01/01/2999"
        # Bascule les dates françaises en dates anglaises pour faire le tri
        item1 = DateFrEng(item1)
        item2 = DateFrEng(item2)
        
        if item1 < item2:    
               return -1
        else:                   
               return 1

    def Importation(self):
        """ Importe les données """
        date_jour = datetime.date.today()

        # Get dict documents
        self.dict_docs = self.GetDocumentsScan() 

        # Initialisation de la base de données
        DB = GestionDB.DB()
        self.DictDossier = {}
        
        # Recherche des pièces
        req = """
        SELECT pieces.IDpiece, types_pieces.nom_piece, pieces.date_debut, pieces.date_fin, pieces.IDpersonne
        FROM pieces INNER JOIN types_pieces ON pieces.IDtype_piece = types_pieces.IDtype_piece
        WHERE (((pieces.IDpersonne)=%d));
        """ % self.IDpersonne
        DB.ExecuterReq(req)
        listePieces = DB.ResultatReq()

        # Création du dictionnaire de données des pièces du dossier
        for piece in listePieces:
            IDpiece = piece[0]
            nom_piece = piece[1]
            date_debut = piece[2]
            date_fin = piece[3]
            # Recherche la validité
            date_fin_2 = datetime.date(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]))
            reste = str(date_fin_2 - date_jour)
            if reste != "0:00:00":
                jours = int(reste[:reste.index("day")])
                if jours > 0 :
                    etat = "Ok"
                else:
                    etat = "Perim"
            else:
                etat = "Ok"
            self.DictDossier[IDpiece] = (etat, nom_piece, date_debut, date_fin)
        
        # Fermeture de la base de données
        DB.Close()       

    def OnItemActivated(self, event):
        """ Item double-cliqué """
        self.parent.ModifierPiece()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel du ListCtrl Diplomes."""
        
        if self.GetFirstSelected() == -1:
            return False
        index = self.GetFirstSelected()
        key = self.GetItemData(index)
        
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

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Menu_Ajouter(self, event):
        self.parent.AjouterPiece()
        
    def Menu_Modifier(self, event):
        self.parent.ModifierPiece()

    def Menu_Supprimer(self, event):
        self.parent.SupprimerPiece()

    



