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
import GestionDB
import datetime
import FonctionsPerso
from Dlg import DLG_Edition_DUE
from Dlg import DLG_Creation_contrat
from Utils import UTILS_Adaptations
import six


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateFrEng(textDate):
    text = str(textDate[6:10]) + "/" + str(textDate[3:5]) + "/" + str(textDate[:2])
    return text   

class Panel_Contrats(wx.Panel):
    def __init__(self, parent, id, IDpersonne=0):
        wx.Panel.__init__(self, parent, id, name="page_contrats", style=wx.TAB_TRAVERSAL)

        self.parent = parent
        self.IDpersonne = IDpersonne

        # Widgets
##        self.staticBox_pieces_staticbox = wx.StaticBox(self, -1, _(u"Pièces à fournir"))
        self.staticBox_contrats_staticbox = wx.StaticBox(self, -1, _(u"Contrats"))
        self.list_ctrl_contrats = ListCtrl_contrats(self, -1)
        self.list_ctrl_contrats.SetMinSize((20, 20)) 
        
        self.bouton_contrats_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_contrats_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_contrats_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_signature = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Signature.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_due = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Due.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG))

        self.__set_properties()
        self.__do_layout()
        

    def __set_properties(self):

        self.bouton_contrats_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir un nouveau contrat")))
        self.bouton_contrats_ajouter.SetSize(self.bouton_contrats_ajouter.GetBestSize())
        self.bouton_contrats_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le contrat sélectionné dans la liste")))
        self.bouton_contrats_modifier.SetSize(self.bouton_contrats_modifier.GetBestSize())
        self.bouton_contrats_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le contrat sélectionné dans la liste")))
        self.bouton_contrats_supprimer.SetSize(self.bouton_contrats_supprimer.GetBestSize())
        self.bouton_signature.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour signaler que le contrat est signé ou non")))
        self.bouton_due.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour signaler si la DUE a bien été faite")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer un contrat, une DUE, une attestation de travail, etc...")))
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjoutContrat, self.bouton_contrats_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifContrat, self.bouton_contrats_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprContrat, self.bouton_contrats_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSignature, self.bouton_signature)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDue, self.bouton_due)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        staticBox_contrats = wx.StaticBoxSizer(self.staticBox_contrats_staticbox, wx.VERTICAL)
        grid_sizer_contrats = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
##        # Pièces
##        staticBox_pieces = wx.StaticBoxSizer(self.staticBox_pieces_staticbox, wx.VERTICAL)
##        grid_sizer_pieces = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
##        grid_sizer_pieces.Add(self.list_ctrl_pieces, 1, wx.EXPAND, 0)
##        grid_sizer_pieces.AddGrowableRow(0)
##        grid_sizer_pieces.AddGrowableCol(0)
##        staticBox_pieces.Add(grid_sizer_pieces, 1, wx.ALL|wx.EXPAND, 5)
##        grid_sizer_haut.Add(staticBox_pieces, 1, wx.LEFT|wx.TOP|wx.EXPAND, 5)
##        
##        # Diplômes
##        staticBox_diplomes = wx.StaticBoxSizer(self.staticBox_diplomes_staticbox, wx.VERTICAL)
##        grid_sizer_diplomes = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
##        grid_sizer_boutons_diplomes = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
##        grid_sizer_diplomes.Add(self.list_ctrl_diplomes, 1, wx.EXPAND, 0)
##        grid_sizer_boutons_diplomes.Add(self.bouton_diplomes_modifier, 0, 0, 0)
##        grid_sizer_diplomes.Add(grid_sizer_boutons_diplomes, 1, wx.EXPAND, 0)
##        grid_sizer_diplomes.AddGrowableRow(0)
##        grid_sizer_diplomes.AddGrowableCol(0)
##        staticBox_diplomes.Add(grid_sizer_diplomes, 1, wx.ALL|wx.EXPAND, 5)
##        grid_sizer_haut.Add(staticBox_diplomes, 1, wx.RIGHT|wx.TOP|wx.EXPAND, 5)
##        
##        grid_sizer_haut.AddGrowableRow(0)
##        grid_sizer_haut.AddGrowableCol(0)
##        grid_sizer_haut.AddGrowableCol(1)
##        grid_sizer_base.Add(grid_sizer_haut, 1, wx.EXPAND, 0)
        
        # Dossier
        grid_sizer_contrats.Add(self.list_ctrl_contrats, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons_contrats = wx.FlexGridSizer(rows=8, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_contrats.Add(self.bouton_contrats_ajouter, 0, 0, 0)
        grid_sizer_boutons_contrats.Add(self.bouton_contrats_modifier, 0, 0, 0)
        grid_sizer_boutons_contrats.Add(self.bouton_contrats_supprimer, 0, 0, 0)
        grid_sizer_boutons_contrats.Add((10, 10), 0, 0, 0)
        grid_sizer_boutons_contrats.Add(self.bouton_signature, 0, 0, 0) 
        grid_sizer_boutons_contrats.Add(self.bouton_due, 0, 0, 0) 
        grid_sizer_boutons_contrats.Add((10, 10), 0, 0, 0)
        grid_sizer_boutons_contrats.Add(self.bouton_imprimer, 0, 0, 0) 
        grid_sizer_contrats.Add(grid_sizer_boutons_contrats, 1, wx.EXPAND, 0)
        
        grid_sizer_contrats.AddGrowableRow(0)
        grid_sizer_contrats.AddGrowableCol(0)
        staticBox_contrats.Add(grid_sizer_contrats, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticBox_contrats, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.TOP|wx.EXPAND, 5)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)

    def MAJ_barre_problemes(self):
        if self.IDpersonne in FonctionsPerso.Recherche_ContratsEnCoursOuAVenir() :
            self.parent.GetGrandParent().barre_problemes = True
        else:
            self.parent.GetGrandParent().barre_problemes = False
        self.parent.GetGrandParent().MAJ_barre_problemes()


    def OnBoutonAjoutContrat(self, event):
        self.AjouterContrat()
        event.Skip()

    def AjouterContrat(self):
        dlg = DLG_Creation_contrat.Dialog(self, IDcontrat=0, IDpersonne=self.IDpersonne)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonModifContrat(self, event):
        self.ModifierContrat()
        event.Skip()

    def ModifierContrat(self):
        """ Modification de coordonnées """
        index = self.list_ctrl_contrats.GetFirstSelected()
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un contrat à modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        varIDcontrat = self.list_ctrl_contrats.GetItemData(index)
        dlg = DLG_Creation_contrat.Dialog(self, IDcontrat=varIDcontrat, IDpersonne=self.IDpersonne)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonSupprContrat(self, event):
        self.SupprimerContrat()
        event.Skip()
        
    def SupprimerContrat(self):
        """ Suppression d'une coordonnée """
        index = self.list_ctrl_contrats.GetFirstSelected()

        # Vérifie qu'un item a bien été sélectionné
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un contrat à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation
        texteContrat = self.list_ctrl_contrats.GetItem(index, 3).GetText()
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer ce contrat ? \n\n> ") + texteContrat))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        varIDcontrat = self.list_ctrl_contrats.GetItemData(index)

        # Suppression
        DB = GestionDB.DB()
        DB.ReqDEL("contrats", "IDcontrat", varIDcontrat)
        DB.Close()

        # MàJ du listCtrl Coords de la fiche individuelle
        self.list_ctrl_contrats.Remplissage()
        self.MAJ_barre_problemes()
        
    def OnBoutonSignature(self, event):
        """ Signer un contrat """
        index = self.list_ctrl_contrats.GetFirstSelected()
        # Vérifie qu'un item a bien été sélectionné
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un contrat dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        IDcontrat = self.list_ctrl_contrats.GetItemData(index)
        etatSignature = self.list_ctrl_contrats.GetItem(index, 4).GetText()
        if etatSignature == "Oui" :
            etatSignature = ""
        else:
            etatSignature = "Oui"
        
        # Enregistrement de la modification dans la base
        DB = GestionDB.DB()
        listeDonnees = [    ("signature",     etatSignature),  ]
        DB.ReqMAJ("contrats", listeDonnees, "IDcontrat", IDcontrat)
        DB.Commit()
        DB.Close()
        
        # MAJ du listCtrl
        if 'phoenix' in wx.PlatformInfo:
            self.list_ctrl_contrats.SetItem(index, 4, etatSignature)
        else:
            self.list_ctrl_contrats.SetStringItem(index, 4, etatSignature)
        self.MAJ_barre_problemes()

    def OnBoutonDue(self, event):
        """ Signer un contrat """
        index = self.list_ctrl_contrats.GetFirstSelected()
        # Vérifie qu'un item a bien été sélectionné
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un contrat dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        IDcontrat = self.list_ctrl_contrats.GetItemData(index)
        etatDue = self.list_ctrl_contrats.GetItem(index, 5).GetText()
        if etatDue == "Oui" :
            etatDue = ""
        else:
            etatDue = "Oui"
        
        # Enregistrement de la modification dans la base
        DB = GestionDB.DB()
        listeDonnees = [    ("due",     etatDue),  ]
        DB.ReqMAJ("contrats", listeDonnees, "IDcontrat", IDcontrat)
        DB.Commit()
        DB.Close()
        
        # MAJ du listCtrl
        if 'phoenix' in wx.PlatformInfo:
            self.list_ctrl_contrats.SetItem(index, 5, etatDue)
        else:
            self.list_ctrl_contrats.SetStringItem(index, 5, etatDue)
        self.MAJ_barre_problemes()
        
    def OnBoutonImprimer(self, event):
        """ Impressions """
        index = self.list_ctrl_contrats.GetFirstSelected()
        # Vérifie qu'un contrat a été sélectionné dans la liste
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un contrat dans la liste proposée."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Demande le type d'impression à l'utilisateur
        from Dlg import DLG_Selection_type_document
        listeBoutons = [
            (Chemins.GetStaticPath("Images/BoutonsImages/Imprimer_doc_DUE.png"), _(u"Cliquez ici pour imprimer une D.U.E.")),
            (Chemins.GetStaticPath("Images/BoutonsImages/Imprimer_doc_contrat.png"), _(u"Cliquez ici pour imprimer un autre document (Contrat, attestation, etc...)")),
            ]
        dlg = DLG_Selection_type_document.Dialog(self, size=(450, 335), listeBoutons=listeBoutons, type="contrats")
        if dlg.ShowModal() == wx.ID_OK:
            ChoixType = dlg.GetChoix()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        if ChoixType == 1 : self.ImprimerDUE()
        if ChoixType == 2 : self.ImprimerContrat()
        
                
    def ImprimerContrat(self):
        """ Editer un contrat """
        index = self.list_ctrl_contrats.GetFirstSelected()
        IDcontrat = self.list_ctrl_contrats.GetItemData(index)

        # Récupère les données pour le publipostage
        from Utils import UTILS_Publipostage_donnees
        dictDonnees = UTILS_Publipostage_donnees.GetDictDonnees(categorie="contrat", listeID=[IDcontrat,])
        # Ouvre le publiposteur
        from Dlg import DLG_Publiposteur
        dlg = DLG_Publiposteur.Dialog(self, "", dictDonnees=dictDonnees)
        dlg.ShowModal()
        dlg.Destroy()

    def ImprimerDUE(self):
        """ Editer un contrat """
        index = self.list_ctrl_contrats.GetFirstSelected()
        IDcontrat = self.list_ctrl_contrats.GetItemData(index)
        dlg = DLG_Edition_DUE.Dialog(self, IDcontrat=IDcontrat)
        dlg.ShowModal()
        dlg.Destroy()


# ----------- LISTCTRL DOSSIER ---------------------------------------------------------------------------------------------------


class ListCtrl_contrats(wx.ListCtrl):
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, id, size=(250, -1), style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.LC_SINGLE_SEL|wx.SUNKEN_BORDER) 
        self.parent = parent
        self.IDpersonne = self.GetParent().IDpersonne

        # Colonnes
        self.InsertColumn(0, _(u"ID"))
        self.SetColumnWidth(0, 0)
        self.InsertColumn(1, _(u"Date de début"))
        self.SetColumnWidth(1, 85)
        self.InsertColumn(2, _(u"Date de fin"))
        self.SetColumnWidth(2, 85)
        self.InsertColumn(3, _(u"Classification"))
        self.SetColumnWidth(3, 220)
        self.InsertColumn(4, _(u"Signé"))
        self.SetColumnWidth(4, 43)
        self.InsertColumn(5, _(u"Due"))
        self.SetColumnWidth(5, 40)

        # Création des items
        self.Remplissage()

        # Binds
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def Remplissage(self):
        """ Remplissage du ListCtrl """
        # Importation des données
        self.Importation_Classifications()
        self.Importation()

        # S'il existe des items, on les efface d'abord
        if self.GetItemCount() != 0:
            self.DeleteAllItems()
            
        # Création des items
        index = 0
        for IDcontrat, valeurs in self.DictContrats.items():
            etat = valeurs[0]
            classification = valeurs[1]
            date_debut =valeurs[2]
            date_fin = valeurs[3]
            date_rupture = valeurs[4]
            signature= valeurs[5]
            due= valeurs[6]
            # Création de l'item
            if 'phoenix' in wx.PlatformInfo:
                self.InsertItem(index, str(IDcontrat))
            else:
                self.InsertStringItem(index, str(IDcontrat))
            # Etat
            if etat == "Perim":
                item = self.GetItem(index)
                item.SetTextColour("GREY")
                self.SetItem(item)

            # Autres colonnes
            if 'phoenix' in wx.PlatformInfo:
                self.SetItem(index, 1, DateEngFr(date_debut))
            else:
                self.SetStringItem(index, 1, DateEngFr(date_debut))
            if date_fin == "2999-01-01" :
                date_fin = _(u"Indétermin.")
            else:
                date_fin = DateEngFr(date_fin)
            if date_rupture != "" :
                date_fin = DateEngFr(date_rupture) + "-R"
            if 'phoenix' in wx.PlatformInfo:
                self.SetItem(index, 2, date_fin)
                self.SetItem(index, 3, classification)
                self.SetItem(index, 4, signature)
            else:
                self.SetStringItem(index, 2, date_fin)
                self.SetStringItem(index, 3, classification)
                self.SetStringItem(index, 4, signature)
            if due == None :
                due = ""
            if 'phoenix' in wx.PlatformInfo:
                self.SetItem(index, 5, due)
            else:
                self.SetStringItem(index, 5, due)
            # Intégration du data ID
            self.SetItemData(index, IDcontrat)
            index += 1

        # Tri dans l'ordre alphabétique
        self.SortItems(self.ColumnSorter)

        # Fait dérouler la liste
        nbreItems = self.GetItemCount()
        if nbreItems > 0:
            self.EnsureVisible(nbreItems-1) 

    def ColumnSorter(self, key1, key2):
        if 'phoenix' in wx.PlatformInfo:
            item1 = self.GetItem( self.FindItem(-1, key1), 1).GetText()
            item2 = self.GetItem( self.FindItem(-1, key2), 1).GetText()
        else:
            item1 = self.GetItem( self.FindItem(-1, key1), 1).GetText()
            item2 = self.GetItem( self.FindItem(-1, key2), 1).GetText()
        # Bascule les dates françaises en dates anglaises pour faire le tri
        item1 = DateFrEng(item1)
        item2 = DateFrEng(item2)
        
        if item1 < item2:    
               return -1
        else:                   
               return 1

    def Importation(self):
        """ Importe les données """
        
        # MAJ Header fiche individuelle
        self.parent.GetGrandParent().GetParent().contratEnCours = None
        self.parent.GetGrandParent().GetParent().MaJ_header()
                    
        date_jour = datetime.date.today()

        # Initialisation de la base de données
        DB = GestionDB.DB()
        self.DictContrats = {}
        
        # Recherche des pièces
        req = """
        SELECT IDcontrat, IDclassification, date_debut, date_fin, date_rupture, signature, due
        FROM contrats
        WHERE IDpersonne=%d ORDER BY date_debut;
        """ % self.IDpersonne
        DB.ExecuterReq(req)
        listeContrats = DB.ResultatReq()

        # Création du dictionnaire de données des contrats
        for contrat in listeContrats:
            IDcontrat = contrat[0]
            classification = self.DictClass[contrat[1]]
            date_debut = contrat[2]
            date_fin = contrat[3]
            date_rupture = contrat[4]
            signature= contrat[5]
            due= contrat[6]
            # Recherche la validité               
            date_fin_2 = datetime.date(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]))
            reste = str(date_fin_2 - date_jour)
            if reste != "0:00:00":
                jours = int(reste[:reste.index("day")])
                if jours > 0 :
                    etat = "Ok"
                    # MAJ Header fiche individuelle
                    self.parent.GetGrandParent().GetParent().contratEnCours = (classification, date_debut, date_fin, date_rupture)
                    self.parent.GetGrandParent().GetParent().MaJ_header()
                else:
                    etat = "Perim"
            else:
                etat = "Ok"
                # MAJ Header fiche individuelle
                self.parent.GetGrandParent().GetParent().contratEnCours = (classification, date_debut, date_fin, date_rupture)
                self.parent.GetGrandParent().GetParent().MaJ_header()
                    
            self.DictContrats[IDcontrat] = (etat, classification, date_debut, date_fin, date_rupture, signature, due)
        
        # Fermeture de la base de données
        DB.Close() 
        
    def Importation_Classifications(self):
        DB = GestionDB.DB()
        self.DictClass = {}
        req = """
        SELECT IDclassification, nom
        FROM contrats_class
        """ 
        DB.ExecuterReq(req)
        listeClassifications = DB.ResultatReq()
        # Création du dictionnaire
        for classification in listeClassifications:
            self.DictClass[classification[0]] = classification[1]
        # Fermeture de la base de données
        DB.Close() 

    def OnItemActivated(self, event):
        """ Item double-cliqué """
        self.parent.ModifierContrat()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel du ListCtrl Diplomes."""
        
        if self.GetFirstSelected() == -1:
            return False
        index = self.GetFirstSelected()
        key = self.GetItemData(index)
        
        etatSignature = self.GetItem(index, 4).GetText()
        etatDue = self.GetItem(index, 5).GetText()
        
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
        
        menuPop.AppendSeparator()
        
        # Item SIgnature
        if etatSignature == "Oui" :
            txt = _(u"Contrat non signé !")
        else:
            txt =_(u"Contrat signé !")
        item = wx.MenuItem(menuPop, 40, txt)
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Signature.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Signature, id=40)
        
        # Item Due
        if etatDue == "Oui" :
            txt = _(u"DUE non faite !")
        else:
            txt =_(u"DUE faite !")
        item = wx.MenuItem(menuPop, 80, txt)
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Due.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Due, id=80)
        
        menuPop.AppendSeparator()
        
        # Item Imprimer 
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer un document"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Imprimer, id=50)

        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Menu_Ajouter(self, event):
        self.parent.AjouterContrat()
        
    def Menu_Modifier(self, event):
        self.parent.ModifierContrat()

    def Menu_Supprimer(self, event):
        self.parent.SupprimerContrat()

    def Menu_Signature(self, event):
        self.parent.OnBoutonSignature(None)
        
    def Menu_Due(self, event):
        self.parent.OnBoutonDue(None)

    def Menu_Imprimer(self, event):
        self.parent.OnBoutonImprimer(None)

