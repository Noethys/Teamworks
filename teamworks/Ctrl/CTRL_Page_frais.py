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
import six
import wx.lib.mixins.listctrl  as  listmix
import GestionDB
import datetime
import FonctionsPerso
from Dlg import DLG_Saisie_deplacement
from Dlg import DLG_Saisie_remboursement
from Utils import UTILS_Adaptations


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateFrEng(textDate):
    text = str(textDate[6:10]) + "/" + str(textDate[3:5]) + "/" + str(textDate[:2])
    return text   




class Panel(wx.Panel):
    def __init__(self, parent, id=-1, IDpersonne=0):
        wx.Panel.__init__(self, parent, id, name="page_frais", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDpersonne = IDpersonne

        # Widgets
        self.staticBox_deplacements = wx.StaticBox(self, -1, _(u"Déplacements"))
        self.ctrl_deplacements = ListCtrl_deplacements(self, -1)
        self.ctrl_deplacements.SetMinSize((20, 20))
        self.bouton_deplacements_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_deplacements_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_deplacements_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_deplacements_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG))
        
        self.staticBox_remboursements = wx.StaticBox(self, -1, _(u"Remboursements"))
        self.ctrl_remboursements = ListCtrl_remboursements(self, -1)
        self.ctrl_remboursements.SetMinSize((20, 20))
        self.bouton_remboursements_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_remboursements_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_remboursements_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
        
        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjoutDeplacement, self.bouton_deplacements_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifDeplacement, self.bouton_deplacements_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprDeplacement, self.bouton_deplacements_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimerDeplacement, self.bouton_deplacements_imprimer)
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjoutRemboursement, self.bouton_remboursements_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifRemboursement, self.bouton_remboursements_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprRemboursement, self.bouton_remboursements_supprimer)
        

    def __set_properties(self):
        self.bouton_deplacements_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir un nouveau déplacement")))
        self.bouton_deplacements_ajouter.SetSize(self.bouton_deplacements_ajouter.GetBestSize())
        self.bouton_deplacements_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le déplacement sélectionné dans la liste")))
        self.bouton_deplacements_modifier.SetSize(self.bouton_deplacements_modifier.GetBestSize())
        self.bouton_deplacements_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le déplacement sélectionné dans la liste")))
        self.bouton_deplacements_supprimer.SetSize(self.bouton_deplacements_supprimer.GetBestSize())
        self.bouton_deplacements_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer une fiche de frais de déplacement")))
        
        self.bouton_remboursements_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir un nouveau remboursement")))
        self.bouton_remboursements_ajouter.SetSize(self.bouton_remboursements_ajouter.GetBestSize())
        self.bouton_remboursements_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le remboursement sélectionné dans la liste")))
        self.bouton_remboursements_modifier.SetSize(self.bouton_remboursements_modifier.GetBestSize())
        self.bouton_remboursements_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le remboursement sélectionné dans la liste")))
        self.bouton_remboursements_supprimer.SetSize(self.bouton_remboursements_supprimer.GetBestSize())


    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        # --------------
        # Déplacements
        staticBox_deplacements = wx.StaticBoxSizer(self.staticBox_deplacements, wx.VERTICAL)
        grid_sizer_deplacements = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_deplacements.Add(self.ctrl_deplacements, 1, wx.EXPAND, 0)
        grid_sizer_boutons_deplacements = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_deplacements.Add(self.bouton_deplacements_ajouter, 0, 0, 0)
        grid_sizer_boutons_deplacements.Add(self.bouton_deplacements_modifier, 0, 0, 0)
        grid_sizer_boutons_deplacements.Add(self.bouton_deplacements_supprimer, 0, 0, 0)
        grid_sizer_boutons_deplacements.Add((10, 10), 0, 0, 0)
        grid_sizer_boutons_deplacements.Add(self.bouton_deplacements_imprimer, 0, 0, 0) 
        grid_sizer_deplacements.Add(grid_sizer_boutons_deplacements, 1, wx.EXPAND, 0)
        grid_sizer_deplacements.AddGrowableRow(0)
        grid_sizer_deplacements.AddGrowableCol(0)
        staticBox_deplacements.Add(grid_sizer_deplacements, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticBox_deplacements, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 5)
        
        # ---------------
        # Remboursements
        staticBox_remboursements = wx.StaticBoxSizer(self.staticBox_remboursements, wx.VERTICAL)
        grid_sizer_remboursements = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_remboursements.Add(self.ctrl_remboursements, 1, wx.EXPAND, 0)
        grid_sizer_boutons_remboursements = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_remboursements.Add(self.bouton_remboursements_ajouter, 0, 0, 0)
        grid_sizer_boutons_remboursements.Add(self.bouton_remboursements_modifier, 0, 0, 0)
        grid_sizer_boutons_remboursements.Add(self.bouton_remboursements_supprimer, 0, 0, 0)
        grid_sizer_boutons_remboursements.Add((10, 10), 0, 0, 0)
##        grid_sizer_boutons_remboursements.Add(self.bouton_remboursements_imprimer, 0, 0, 0) 
        grid_sizer_remboursements.Add(grid_sizer_boutons_remboursements, 1, wx.EXPAND, 0)
        grid_sizer_remboursements.AddGrowableRow(0)
        grid_sizer_remboursements.AddGrowableCol(0)
        staticBox_remboursements.Add(grid_sizer_remboursements, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticBox_remboursements, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 5)
        
        # ---------------
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        
        # ---------------

    def MAJ_frm_gestion_frais(self):
        """ Met à jour le listCtrl de la frame gestion des frais si elle est ouverte """
        try :
            if self.GetGrandParent().GetName() == "frm_gestion_frais" :
                self.GetGrandParent().ctrl_personnes.MAJListeCtrl()
        except :
            pass
        

    def OnBoutonAjoutDeplacement(self, event):
        if self.IDpersonne == None : 
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une personne dans la liste"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.AjouterDeplacement()
        event.Skip()

    def AjouterDeplacement(self):
        dlg = DLG_Saisie_deplacement.SaisieDeplacement(self, IDdeplacement=None, IDpersonne=self.IDpersonne)
        if dlg.ShowModal() == wx.ID_OK:
            self.ctrl_deplacements.MAJListeCtrl()
            self.ctrl_remboursements.MAJListeCtrl()
            dlg.Destroy()
        else:
            dlg.Destroy()
        # MAJ de la frame de gestion des frais si elle est ouverte
        self.MAJ_frm_gestion_frais()

    def OnBoutonModifDeplacement(self, event):
        if self.IDpersonne == None : 
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une personne dans la liste"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.ModifierDeplacement()
        event.Skip()

    def ModifierDeplacement(self):
        """ Modification de coordonnées """
        index = self.ctrl_deplacements.GetFirstSelected()
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un déplacement à modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDdeplacement = int(self.ctrl_deplacements.GetItem(index, 0).GetText())
        # Ouverture du formulaire de modification
        dlg = DLG_Saisie_deplacement.SaisieDeplacement(self, IDdeplacement=IDdeplacement, IDpersonne=self.IDpersonne)
        if dlg.ShowModal() == wx.ID_OK:
            self.ctrl_deplacements.MAJListeCtrl()
            self.ctrl_remboursements.MAJListeCtrl()
            dlg.Destroy()
        else:
            dlg.Destroy()
        # MAJ de la frame de gestion des frais si elle est ouverte
        self.MAJ_frm_gestion_frais()

    def OnBoutonSupprDeplacement(self, event):
        if self.IDpersonne == None : 
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une personne dans la liste"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.SupprimerDeplacement()
        event.Skip()
        
    def SupprimerDeplacement(self):
        """ Suppression d'une coordonnée """
        index = self.ctrl_deplacements.GetFirstSelected()

        # Vérifie qu'un item a bien été sélectionné
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un déplacement à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        IDdeplacement = int(self.ctrl_deplacements.GetItem(index, 0).GetText())
        
        # Vérifie que le déplacement n'est pas attribué à un remboursement :
        DB = GestionDB.DB()        
        req = """SELECT IDdeplacement, IDremboursement FROM deplacements WHERE IDdeplacement=%d; """ % IDdeplacement
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dejaAttribue = None
        for IDdeplacement, IDremboursement in listeDonnees :
            if IDremboursement != 0 : 
                dejaAttribue = IDremboursement
                break
        if dejaAttribue != None : 
            dlg = wx.MessageDialog(self, _(u"Ce déplacement a déjà été attribué au remboursement n°") + str(dejaAttribue) + _(u".\nVous ne pouvez donc pas le supprimer."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Demande de confirmation
        texte = self.ctrl_deplacements.GetItem(index, 3).GetText() + "\nLe " + self.ctrl_deplacements.GetItem(index, 1).GetText()
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer ce déplacement ? \n\n") + texte))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return

        # Suppression
        DB = GestionDB.DB()
        DB.ReqDEL("deplacements", "IDdeplacement", IDdeplacement)

        # MàJ du listCtrl de la fiche individuelle
        self.ctrl_deplacements.MAJListeCtrl()
        self.ctrl_remboursements.MAJListeCtrl()
        
        # MAJ de la frame de gestion des frais si elle est ouverte
        self.MAJ_frm_gestion_frais()

        
    def OnBoutonImprimerDeplacement(self, event):
        """ Impression """
        if self.IDpersonne == None : 
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une personne dans la liste"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Vérifie qu'il existe des déplacements
        if self.ctrl_deplacements.GetItemCount() == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucun déplacement à imprimer pour cette personne."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Appel de la frame d'impression
        from Dlg import DLG_Impression_frais
        dlg = DLG_Impression_frais.Dialog(self, self.IDpersonne)
        dlg.ShowModal()
        dlg.Destroy()
        
        
# ---------------------------------------------------

    def OnBoutonAjoutRemboursement(self, event):
        if self.IDpersonne == None : 
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une personne dans la liste"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.AjouterRemboursement()
        event.Skip()

    def AjouterRemboursement(self):
        dlg = DLG_Saisie_remboursement.SaisieRemboursement(self, IDremboursement=None, IDpersonne=self.IDpersonne)
        if dlg.ShowModal() == wx.ID_OK:
            self.ctrl_deplacements.MAJListeCtrl()
            self.ctrl_remboursements.MAJListeCtrl()
            dlg.Destroy()
        else:
            dlg.Destroy()
        # MAJ de la frame de gestion des frais si elle est ouverte
        self.MAJ_frm_gestion_frais()

    def OnBoutonModifRemboursement(self, event):
        if self.IDpersonne == None : 
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une personne dans la liste"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.ModifierRemboursement()
        event.Skip()

    def ModifierRemboursement(self):
        """ Modification de coordonnées """
        index = self.ctrl_remboursements.GetFirstSelected()
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un remboursement à modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDremboursement = int(self.ctrl_remboursements.GetItem(index, 1).GetText())
        # Ouverture du formulaire de modification
        dlg = DLG_Saisie_remboursement.SaisieRemboursement(self, IDremboursement=IDremboursement, IDpersonne=self.IDpersonne)
        if dlg.ShowModal() == wx.ID_OK:
            self.ctrl_deplacements.MAJListeCtrl()
            self.ctrl_remboursements.MAJListeCtrl()
            dlg.Destroy()
        else:
            dlg.Destroy()
        # MAJ de la frame de gestion des frais si elle est ouverte
        self.MAJ_frm_gestion_frais()

    def OnBoutonSupprRemboursement(self, event):
        if self.IDpersonne == None : 
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une personne dans la liste"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.SupprimerRemboursement()
        event.Skip()
        
    def SupprimerRemboursement(self):
        """ Suppression d'un remboursement """
        index = self.ctrl_remboursements.GetFirstSelected()

        # Vérifie qu'un item a bien été sélectionné
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un remboursement à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        IDremboursement = int(self.ctrl_remboursements.GetItem(index, 1).GetText())
        
        # Vérifie si des déplacements ont déjà été attachés à ce remboursement
        DB = GestionDB.DB()        
        req = """SELECT IDdeplacement FROM deplacements WHERE IDremboursement=%d; """ % IDremboursement
        DB.ExecuterReq(req)
        listeDeplacements = DB.ResultatReq()
        DB.Close()
        nbreRattaches = len(listeDeplacements)
        if nbreRattaches != 0 : 
            txtMessage = _(u"Ce remboursement possède déjà ") + str(nbreRattaches) + _(u" déplacement(s) rattaché(s).\nSouhaitez-vous vous quand même le supprimer ?")
            dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            reponse = dlgConfirm.ShowModal()
            dlgConfirm.Destroy()
            if reponse == wx.ID_NO:
                return
        
        # Demande de confirmation
        texte = self.ctrl_remboursements.GetItem(index, 2).GetText() + _(u" d'un montant de ") + self.ctrl_remboursements.GetItem(index, 3).GetText() 
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer le remboursement du ") + texte + " ?"))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        

        # Suppression
        DB = GestionDB.DB()
        DB.ReqDEL("remboursements", "IDremboursement", IDremboursement)
        
        # Modification du IDdeplacement de chaque déplacement rattaché
        DB = GestionDB.DB()
        for donnees in listeDeplacements :
            IDdeplacement = donnees[0]
            listeDonnees = [    ("IDremboursement",   0),  ]
            DB.ReqMAJ("deplacements", listeDonnees, "IDdeplacement", IDdeplacement)
        DB.Commit()
        DB.Close()

        # MàJ du listCtrl de la fiche individuelle
        self.ctrl_deplacements.MAJListeCtrl()
        self.ctrl_remboursements.MAJListeCtrl()
        
        # MAJ de la frame de gestion des frais si elle est ouverte
        self.MAJ_frm_gestion_frais()
        

# ----------- LISTCTRL DEPLACEMENTS  ---------------------------------------------------------------------------------------------------

        
class ListCtrl_deplacements(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent, id=-1):
        wx.ListCtrl.__init__( self, parent, id, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.IDpersonne = self.GetParent().IDpersonne
        self.parent = parent

        # Initialisation des images
        tailleIcones = 16
        self.il = wx.ImageList(tailleIcones, tailleIcones)
        self.imgTriAz= self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Tri_az.png"), wx.BITMAP_TYPE_PNG))
        self.imgTriZa= self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Tri_za.png"), wx.BITMAP_TYPE_PNG))
        self.imgOk = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))
        self.imgPasOk = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        #adding some attributes (colourful background for each item rows)
        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour("#EEF4FB") # Vert = #F0FBED
        
        # Remplissage
        if self.IDpersonne != None :
            self.Remplissage()
        
        #events
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)

    def Remplissage(self):
        
        # Récupération des données dans la base de données
        self.Importation()
        
        # Création des colonnes
        self.nbreColonnes = 8
        self.InsertColumn(0, u"N°")
        self.SetColumnWidth(0, 50)
        self.InsertColumn(1, _(u"Date"))
        self.SetColumnWidth(1, 80)
        self.InsertColumn(2, _(u"Objet"))
        self.SetColumnWidth(2, 80) 
        self.InsertColumn(3, _(u"Trajet"))
        self.SetColumnWidth(3, 170)  
        self.InsertColumn(4, _(u"Distance"))
        self.SetColumnWidth(4, 70)
        self.InsertColumn(5, _(u"Tarif"))
        self.SetColumnWidth(5, 70)  
        self.InsertColumn(6, _(u"Montant"))
        self.SetColumnWidth(6, 70)
        self.InsertColumn(7, _(u"Rmbst"))
        self.SetColumnWidth(7, 50)  

        #These two should probably be passed to init more cleanly
        #setting the numbers of items = number of elements in the dictionary
        self.itemDataMap = self.donnees
        self.itemIndexMap = list(self.donnees.keys())
        self.SetItemCount(self.nbreLignes)
        
        #mixins
##        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

        #sort by genre (column 1), A->Z ascending order (1)
        self.SortListItems(1, 1)

    def OnItemSelected(self, event):
        self.parent.bouton_deplacements_modifier.Enable(True)
        self.parent.bouton_deplacements_supprimer.Enable(True)
        
    def OnItemDeselected(self, event):
        self.parent.bouton_deplacements_modifier.Enable(False)
        self.parent.bouton_deplacements_supprimer.Enable(False)
        
    def Importation(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDdeplacement, date, objet, ville_depart, ville_arrivee, distance, aller_retour, tarif_km, IDremboursement FROM deplacements WHERE IDpersonne=%d ORDER BY date; """ % self.IDpersonne
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.nbreLignes = len(listeDonnees)
        # Création du dictionnaire de données
        self.donnees = {}
        index = 0
        for IDdeplacement, date, objet, ville_depart, ville_arrivee, distance, aller_retour, tarif_km, IDremboursement in listeDonnees :
            # Formatage Trajet
            if aller_retour == "True" :
                trajet = ville_depart + " <--> " + ville_arrivee
            else:
                trajet = ville_depart + " -> " + ville_arrivee
            # Formatage Remboursement
            if IDremboursement != None and IDremboursement != 0 and IDremboursement != "" :
                remboursement = u"N°" + str(IDremboursement)
            else :
                remboursement = ""
            # Formatage distance
            dist = str(distance) + _(u" Km")
            # Formatage montant
            montant = float(distance) * float(tarif_km)
            montantStr = u"%.2f €" % montant
            # Formatage tarif/Km
            tarif_km = str(tarif_km) + _(u" €/km")
            self.donnees[IDdeplacement] = (IDdeplacement, date, objet, trajet, dist, tarif_km, montantStr, remboursement)
            index += 1
            
    def MAJListeCtrl(self):
        self.ClearAll()
        if self.IDpersonne != None :
            self.Remplissage()
            listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)
           
    def OnItemActivated(self, event):
        self.parent.ModifierDeplacement()
        
    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    #---------------------------------------------------
    # These methods are callbacks for implementing the
    # "virtualness" of the list...

    def OnGetItemText(self, item, col):
        """ Affichage des valeurs dans chaque case du ListCtrl """
        index=self.itemIndexMap[item]
        valeur = six.text_type(self.itemDataMap[index][col])
        # Reformate une valeur date en version française
        if col == 1 :
            if valeur[4:5]=="-" and valeur[7:8]=="-":
                valeur = str(valeur[8:10])+"/"+str(valeur[5:7])+"/"+str(valeur[0:4])
        return valeur

    def OnGetItemImage(self, item):
        """ Affichage des images en début de ligne """
        index=self.itemIndexMap[item]
        valeur =self.itemDataMap[index][7]
        if valeur == "" :
            return self.imgPasOk
        else:
            return self.imgOk

    def OnGetItemAttr(self, item):
        """ Application d'une couleur de fond pour une ligne sur deux """
        # Création d'une ligne de couleur 1 ligne sur 2
        if item % 2 == 1:
            return self.attr1
        else:
            return None
       
    #-----------------------------------------------------------
    # Matt C, 2006/02/22
    # Here's a better SortItems() method --
    # the ColumnSorterMixin.__ColumnSorter() method already handles the ascending/descending,
    # and it knows to sort on another column if the chosen columns have the same value.

    def SortItems(self,sorter=FonctionsPerso.cmp):
        items = list(self.itemDataMap.keys())
        items = FonctionsPerso.SortItems(items, sorter)
        self.itemIndexMap = items
        # redraw the list
        self.Refresh()

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.imgTriAz, self.imgTriZa)

    # ---------------------------------------------------------

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        
        if self.GetFirstSelected() == -1:
            return False
        index = self.GetFirstSelected()
        key = int(self.getColumnText(index, 0))
        
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
        self.parent.AjouterDeplacement()
        
    def Menu_Modifier(self, event):
        self.parent.ModifierDeplacement()

    def Menu_Supprimer(self, event):
        self.parent.SupprimerDeplacement()





# ----------- LISTCTRL REMBOURSEMENTS  ---------------------------------------------------------------------------------------------------

class ListCtrl_remboursements(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent, id=-1):
        wx.ListCtrl.__init__( self, parent, id, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.IDpersonne = self.GetParent().IDpersonne
        self.parent = parent

        # Initialisation des images
        tailleIcones = 16
        self.il = wx.ImageList(tailleIcones, tailleIcones)
        self.imgTriAz= self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Tri_az.png"), wx.BITMAP_TYPE_PNG))
        self.imgTriZa= self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Tri_za.png"), wx.BITMAP_TYPE_PNG))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        #adding some attributes (colourful background for each item rows)
        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour("#EEF4FB") # Vert = #F0FBED
        
        # Remplissage
        if self.IDpersonne != None :
            self.Remplissage()
        
        #events
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)

    def Remplissage(self):
        
        # Récupération des données dans la base de données
        self.Importation()
        
        # Création des colonnes
        self.nbreColonnes = 5
        self.InsertColumn(0, u"")
        self.SetColumnWidth(0, 0)
        self.InsertColumn(1, u"N°")
        self.SetColumnWidth(1, 30)
        self.InsertColumn(2, _(u"Date"))
        self.SetColumnWidth(2, 80)
        self.InsertColumn(3, _(u"Montant"))
        self.SetColumnWidth(3, 70) 
        self.InsertColumn(4, _(u"Déplacements rattachés"))
        self.SetColumnWidth(4, 200)   

        #These two should probably be passed to init more cleanly
        #setting the numbers of items = number of elements in the dictionary
        self.itemDataMap = self.donnees
        self.itemIndexMap = list(self.donnees.keys())
        self.SetItemCount(self.nbreLignes)
        
        #mixins
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

        #sort by genre (column 1), A->Z ascending order (1)
        self.SortListItems(2, 1)

    def OnItemSelected(self, event):
        self.parent.bouton_remboursements_modifier.Enable(True)
        self.parent.bouton_remboursements_supprimer.Enable(True)
        
    def OnItemDeselected(self, event):
        self.parent.bouton_remboursements_modifier.Enable(False)
        self.parent.bouton_remboursements_supprimer.Enable(False)
        
    def Importation(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDremboursement, date, montant, listeIDdeplacement FROM remboursements WHERE IDpersonne=%d ORDER BY date; """ % self.IDpersonne
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.nbreLignes = len(listeDonnees)
        # Création du dictionnaire de données
        self.donnees = {}
        index = 0
        for IDremboursement, date, montant, listeIDdeplacement in listeDonnees :
            # Formatage montant
            montant = u"%.2f €" % montant
            # Formatage liste IDdeplacement
            listeID = listeIDdeplacement.split("-")
            if listeID[0] == "" :
                texteListeID = _(u"Aucun déplacement rattaché")
            else :
                texteListeID = u"N° "
                for ID in listeID :
                    texteListeID += ID + ", "
                texteListeID = texteListeID[:-2]
            self.donnees[IDremboursement] = ("", IDremboursement, date, montant, texteListeID)
            index += 1
            
    def MAJListeCtrl(self):
        self.ClearAll()
        if self.IDpersonne != None :
            self.Remplissage()
            self.resizeLastColumn(0)
            listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)
           
    def OnItemActivated(self, event):
        self.parent.ModifierRemboursement()
        
    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    #---------------------------------------------------
    # These methods are callbacks for implementing the
    # "virtualness" of the list...

    def OnGetItemImage(self, item):
        """ Affichage des images en début de ligne """
        return -1

    def OnGetItemText(self, item, col):
        """ Affichage des valeurs dans chaque case du ListCtrl """
        index = self.itemIndexMap[item]
        valeur = six.text_type(self.itemDataMap[index][col])
        # Reformate une valeur date en version française
        if col == 2 :
            if valeur[4:5]=="-" and valeur[7:8]=="-":
                valeur = str(valeur[8:10])+"/"+str(valeur[5:7])+"/"+str(valeur[0:4])
        return valeur
    
    def OnGetItemAttr(self, item):
        """ Application d'une couleur de fond pour une ligne sur deux """
        # Création d'une ligne de couleur 1 ligne sur 2
        if item % 2 == 1:
            return self.attr1
        else:
            return None
       
    #-----------------------------------------------------------
    # Matt C, 2006/02/22
    # Here's a better SortItems() method --
    # the ColumnSorterMixin.__ColumnSorter() method already handles the ascending/descending,
    # and it knows to sort on another column if the chosen columns have the same value.

    def SortItems(self,sorter=FonctionsPerso.cmp):
        items = list(self.itemDataMap.keys())
        items = FonctionsPerso.SortItems(items, sorter)
        self.itemIndexMap = items
        # redraw the list
        self.Refresh()

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.imgTriAz, self.imgTriZa)

    # ---------------------------------------------------------

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        
        if self.GetFirstSelected() == -1:
            return False
        index = self.GetFirstSelected()
        key = int(self.getColumnText(index, 1))
        
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
        self.parent.AjouterRemboursement()
        
    def Menu_Modifier(self, event):
        self.parent.ModifierRemboursement()

    def Menu_Supprimer(self, event):
        self.parent.SupprimerRemboursement()



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        self.panel = Panel(self)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.panel, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer_1)
        self.Layout()
        self.SetMinSize((600, 400))

        IDpersonne = 1
        self.panel.IDpersonne = IDpersonne
        self.panel.ctrl_deplacements.IDpersonne = IDpersonne
        self.panel.ctrl_remboursements.IDpersonne = IDpersonne
        self.panel.ctrl_deplacements.MAJListeCtrl()
        self.panel.ctrl_remboursements.MAJListeCtrl()


if __name__ == '__main__':
    app = wx.App(0)
    frame_1 = MyFrame(None, -1)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
