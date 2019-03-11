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
import GestionDB
import datetime
import time
from Dlg import DLG_Saisie_presence
import FonctionsPerso
from Utils import UTILS_Adaptations


class Dialog(wx.Dialog):
    def __init__(self, parent, IDmodele=0):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.IDmodele = IDmodele
        self.nom = ""
        self.type = "journ"
        self.description = ""
        self.periodes = [False, False, False]
        self.inclureFeries = False
        
        if IDmodele != 0 : 
            self.Importation_parametres()
        
        self.panel_base = wx.Panel(self, -1)
        self.sizer_planning_staticbox = wx.StaticBox(self.panel_base, -1, _(u"Constitution du modèle"))
        self.sizer_param_staticbox = wx.StaticBox(self.panel_base, -1, _(u"Paramètres du modèle"))
        self.label_nom = wx.StaticText(self.panel_base, -1, _(u"Nom :"))
        self.text_nom = wx.TextCtrl(self.panel_base, -1, self.nom)
        self.label_type = wx.StaticText(self.panel_base, -1, "Type :")
        self.radio_type_1 = wx.RadioButton(self.panel_base, -1, "Journalier", style=wx.RB_GROUP)
        self.radio_type_2 = wx.RadioButton(self.panel_base, -1, "Hebdomadaire")
        self.label_description = wx.StaticText(self.panel_base, -1, "Description :")
        self.text_description = wx.TextCtrl(self.panel_base, -1, self.description, style=wx.TE_MULTILINE)
        self.label_periodes = wx.StaticText(self.panel_base, -1, _(u"Périodes :"))
        self.checkbox_periodes_1 = wx.CheckBox(self.panel_base, -1, "Toutes")
        self.checkbox_periodes_2 = wx.CheckBox(self.panel_base, -1, _(u"Périodes scolaires"))
        self.checkbox_periodes_3 = wx.CheckBox(self.panel_base, -1, "Vacances scolaires")
        self.tree_planning = TreeCtrlPlanning(self.panel_base)
        self.checkbox_inclureferies = wx.CheckBox(self.panel_base, -1, _(u"Inclure les jours fériés"))
        self.checkbox_inclureferies.SetValue(self.inclureFeries)
        self.bouton_ajouter = wx.BitmapButton(self.panel_base, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self.panel_base, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self.panel_base, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioType1, self.radio_type_1 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioType2, self.radio_type_2 )
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox1, self.checkbox_periodes_1 )
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox2, self.checkbox_periodes_2 )
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox3, self.checkbox_periodes_3 )
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.text_nom.Bind(wx.EVT_KILL_FOCUS, self.OnLeaveTxtNom)
        self.text_description.Bind(wx.EVT_KILL_FOCUS, self.OnLeaveTxtDescription)

        self.ActivationBoutons(False, False, False)
        
    def __set_properties(self):
        if self.IDmodele == 0 :
            self.SetTitle(_(u"Création d'un modèle"))
        else:
            self.SetTitle(_(u"Modification d'un modèle"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.text_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom de votre choix pour ce modèle")))
        self.radio_type_1.SetToolTip(wx.ToolTip(_(u"Sélectionnez 'Journalier' di vous ne souhaitez créer qu'un modèle comportant une journée-type")))
        self.radio_type_2.SetToolTip(wx.ToolTip(_(u"Sélectionnez 'Hebdomadaire' si vous souhaitez créer un modèle qui comporte une semaine-type")))
        self.text_description.SetToolTip(wx.ToolTip(_(u"Vous pouvez donner ici une description de ce modèle")))
        self.checkbox_periodes_1.SetToolTip(wx.ToolTip(_(u"Les tâches saisies dans cette catégorie de période seront créées sur des périodes de vacances et des périodes de vacances")))
        self.checkbox_periodes_2.SetToolTip(wx.ToolTip(_(u"Les tâches créées dans cette catégorie seront appliquées uniquement sur des périodes scolaires")))
        self.checkbox_periodes_3.SetToolTip(wx.ToolTip(_(u"Les tâches saisies dans cette catégorie de période seront appliquées uniquement sur des vacances scolaires")))
        self.tree_planning.SetMinSize((500, 250))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une tâche")))
        self.bouton_ajouter.SetSize(self.bouton_ajouter.GetBestSize())
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la tâche sélectionnée")))
        self.bouton_modifier.SetSize(self.bouton_modifier.GetBestSize())
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la tâche sélectionnée")))
        self.bouton_supprimer.SetSize(self.bouton_supprimer.GetBestSize())
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip("Cliquez ici pour valider"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip("Cliquez ici pour annuler"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.checkbox_inclureferies.SetToolTip(wx.ToolTip(_(u"Cochez cette case si vous souhaitez que le modèle soit également appliqué les jours fériés.")))
        
        self.checkbox_periodes_1.SetValue(self.periodes[0] )
        self.checkbox_periodes_2.SetValue(self.periodes[1] )
        self.checkbox_periodes_3.SetValue(self.periodes[2] )
        if self.type == "journ" : self.radio_type_1.SetValue(True)
        else: self.radio_type_2.SetValue(True)

    def __do_layout(self):
        sizer1_base = wx.BoxSizer(wx.VERTICAL)
        sizer2_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        sizer_planning = wx.StaticBoxSizer(self.sizer_planning_staticbox, wx.VERTICAL)
        grid_sizer_planning = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_planning = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        sizer_param = wx.StaticBoxSizer(self.sizer_param_staticbox, wx.VERTICAL)
        grid_sizer_param = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_6 = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_type = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_param.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.text_nom, 0, wx.EXPAND, 0)
        grid_sizer_param.Add(self.label_type, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_type.Add(self.radio_type_1, 0, 0, 0)
        grid_sizer_type.Add(self.radio_type_2, 0, 0, 0)
        grid_sizer_param.Add(grid_sizer_type, 1, wx.EXPAND, 0)
        grid_sizer_param.Add(self.label_description, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.text_description, 0, wx.EXPAND, 0)
        grid_sizer_param.Add(self.label_periodes, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_6.Add(self.checkbox_periodes_1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_6.Add(self.checkbox_periodes_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_6.Add(self.checkbox_periodes_3, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(grid_sizer_6, 1, wx.EXPAND, 0)
        grid_sizer_param.AddGrowableCol(1)
        sizer_param.Add(grid_sizer_param, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_param, 1, wx.EXPAND, 0)
        grid_sizer_planning.Add(self.tree_planning, 1, wx.EXPAND, 0)
        grid_sizer_boutons_planning.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons_planning.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons_planning.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_planning.Add(grid_sizer_boutons_planning, 1, wx.EXPAND, 0)
        grid_sizer_planning.Add(self.checkbox_inclureferies, 0, wx.EXPAND, 0)
        grid_sizer_planning.AddGrowableCol(0)
        grid_sizer_planning.AddGrowableRow(0)
        sizer_planning.Add(grid_sizer_planning, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_planning, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        sizer2_base.Add(grid_sizer_base, 1, wx.ALL|wx.EXPAND, 10)
        self.panel_base.SetSizer(sizer2_base)
        sizer1_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer1_base)
        sizer1_base.Fit(self)
        self.Layout()
        self.Centre()

    def OnLeaveTxtNom(self, event):
        if self.nom != self.text_nom.GetValue() :
            self.nom = self.text_nom.GetValue()
            self.tree_planning.Remplissage()
        
    def OnLeaveTxtDescription(self, event):
        if self.description != self.text_description.GetValue() :
            self.description = self.text_description.GetValue()

    def OnRadioType1(self, event):
        self.type = "journ"
        self.tree_planning.Remplissage()
        
    def OnRadioType2(self, event):
        self.type = "hebdo"
        self.tree_planning.Remplissage()
        
    def OnCheckBox1(self, event):
        self.periodes[0] = self.checkbox_periodes_1.GetValue()
        self.tree_planning.Remplissage()

    def OnCheckBox2(self, event):
        self.periodes[1] = self.checkbox_periodes_2.GetValue()
        self.tree_planning.Remplissage()

    def OnCheckBox3(self, event):
        self.periodes[2] = self.checkbox_periodes_3.GetValue()
        self.tree_planning.Remplissage()
        
    def Importation_parametres(self):
        DB = GestionDB.DB()
        req = "SELECT * FROM modeles_planning WHERE IDmodele=%d" % self.IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        
        if len(listeDonnees) == 0 : return
        
        self.nom = listeDonnees[0][1]
        self.type = listeDonnees[0][2]
        self.description = listeDonnees[0][3]
        periodesTemp = listeDonnees[0][4]
        if periodesTemp[0] == "1" : self.periodes[0] = True
        if periodesTemp[1] == "1" : self.periodes[1] = True
        if periodesTemp[2] == "1" : self.periodes[2] = True
        if listeDonnees[0][5] == 1 :
            self.inclureFeries = True
    
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(14)
        
    def OnBoutonAnnuler(self, event):
        """ Bouton annuler """        
        modif = False
        for tache in self.tree_planning.listeTaches :
            if tache[9] == "modif" or tache[9] == "suppr" or tache[9] == "new" :
                modif = True
        
        if modif == True :
            dlg = wx.MessageDialog(self, _(u"Vous avez fait des modifications sur ce modèle. Souhaitez-vous vraiment toutes les annuler ?"), _(u"Annulation"), wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_NO :
                dlg.Destroy() 
                return
            dlg.Destroy()
        
        self.EndModal(wx.ID_CANCEL)
        
    def OnBoutonOk(self, event):
        """ Bouton Ok """
        # Validation des paramètres
        IDmodele = self.IDmodele
        nom = self.nom
        type = self.type
        description = self.description
        inclureferies = int(self.checkbox_inclureferies.GetValue())
        periodes = ""
        for tmp in self.periodes :
            if tmp == True :
                periodes += "1"
            else:
                periodes += "0"
                
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom pour le modèle."), "Erreur de saisie", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy() 
            self.text_nom.SetFocus()
            return
        
        if periodes == "000" :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins une période."), "Erreur de saisie", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy() 
            return
            
        # Validation des taches
        listeTaches = self.tree_planning.listeTaches
        if len(listeTaches) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez enregistré aucune tâche pour ce modèle. Souhaitez-vous vraiment quitter l'édition de ce modèle ?"),  _(u"Quitter l'édition d'un modèle"), wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_NO :
                dlg.Destroy() 
                return
            dlg.Destroy()
        
        DB = GestionDB.DB()
        
        # Enregistrement des paramètres
        listeDonnees = [    ("nom",  nom),
                                    ("type",  type),
                                    ("description",   description),
                                    ("periodes",  periodes),
                                    ("inclureferies",  inclureferies),
                                        ]
        if IDmodele == 0 :
            # Ajout
            type = "creation"
            IDmodele = DB.ReqInsert("modeles_planning", listeDonnees)
            DB.Commit()
        else:
            # Modification
            type = "modification"
            DB.ReqMAJ("modeles_planning", listeDonnees, "IDmodele", IDmodele)
            DB.Commit()
        
        # Enregistrement des taches
        for tache in listeTaches :
            IDtache = tache[0]
            listeDonnees = [("IDmodele", IDmodele), ("type",  tache[2]), ("periode", tache[3]),  ("jour",  tache[4]), ("heure_debut",  tache[5]), ("heure_fin",  tache[6]), ("IDcategorie",  tache[7]), ("intitule",  tache[8]), ]
            # Ajout
            if tache[9] == "new" or type == "creation" :
                ID = DB.ReqInsert("modeles_taches", listeDonnees)
                DB.Commit()
            # Modification
            if tache[9] == "modif" :
                DB.ReqMAJ("modeles_taches", listeDonnees, "IDtache", IDtache)
                DB.Commit()
            # Suppression
            if tache[9] == "suppr" :
                DB.ReqDEL("modeles_taches", "IDtache", IDtache)

        DB.Close()
        
        # MAJ formulaire Application d'un modèle s'il est ouvert
        try :
            listCtrl_modeles = self.GetParent().list_ctrl_modeles
            listCtrl_modeles.Remplissage()
            listCtrl_modeles.SetFocus()
            idx = 0
            for index in range(listCtrl_modeles.GetItemCount()) :
                if listCtrl_modeles.GetItemData(index) == IDmodele :
                    idx = index
                    break
            listCtrl_modeles.Select(idx, True)
            listCtrl_modeles.EnsureVisible(idx)
        except :
            pass

        self.EndModal(wx.ID_OK)
            
        
    def OnBoutonAjouter(self, event):
        """ Ajouter une tâche """
        treeSelection = self.tree_planning.selection
        
        if treeSelection < 100000 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un jour dans la liste proposée"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy() 
            return
        
        if str(treeSelection)[1] == "0" :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un jour dans la liste proposée"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy() 
            return
        
        frame_SaisiePresences = DLG_Saisie_presence.Frm_SaisiePresences(self, mode="modele")
        frame_SaisiePresences.Show()
        frame_SaisiePresences.panel.sizer_1.Hide(False)
        frame_SaisiePresences.panel.sizer_donnees_staticbox.Hide()
        frame_SaisiePresences.panel.grid_sizer_base.Layout()
        frame_SaisiePresences.SetMinSize((400, 320))
        frame_SaisiePresences.SetSize((400, 320))

    def Sauvegarde(self, donnees) :
        
        ID = donnees[0]
        if ID == 0 :
            IDtache = self.GetNumID()
        else:
            IDtache = ID
        heure_debut = donnees[5]
        heure_fin = donnees[6]
        IDcategorie = donnees[7]
        intitule = donnees[8]
        type = self.type
        IDmodele = self.IDmodele
        if ID == 0 :
            periode, jour = self.GetPeriodeJour(self.tree_planning.selection)
        else:
            periode = donnees[3]
            jour = donnees[4]
        
        # Validation des données
        listeTaches = self.tree_planning.listeTaches
        for tache in listeTaches :
            if tache[2] == type and tache[3] == periode and tache[4] == jour and tache[0] != ID :
                if tache[5] < heure_debut < tache[6] : return False
                if tache[5] < heure_fin < tache[6] : return False
        
        # Mémorisation des données
        if ID == 0 :
            tache = [IDtache, IDmodele, type, periode, jour, heure_debut, heure_fin, IDcategorie, intitule, "new"]
            listeTaches.append(tache)
        else:
            x = 0
            for tache in listeTaches :
                if tache[0] == ID :
                    index = x
                    break
                x += 1
            
            if listeTaches[index][9] == "new" :
                etat = "new"
            else:
                etat = "modif"
            listeTaches[index] = [IDtache, IDmodele, type, periode, jour, heure_debut, heure_fin, IDcategorie, intitule, etat]
        
        # MAJ du tree
        self.tree_planning.Remplissage()
        
        return True
    
  
    
    def GetNumID(self):
        """ Recherche le prochain numéro ID de la liste des taches """
        num = 0
        for tache in self.tree_planning.listeTaches :
            if tache[0]>num : num = tache[0]
        num += 1
        return num        
        
    def GetPeriodeJour(self, selectionData):
        data = str(selectionData)
        print(data)
        periode = int(data[0])
        jour =  int(data[1])
        return periode, jour
        
    def OnBoutonModifier(self, event):
        """ Modifier une tâche """
        IDmodif = self.tree_planning.selection
        
        if IDmodif == None : return
        if IDmodif >= 100000 :  return
        
        # Recherche des données à mettre dans le formulaire de saisie
        listeTaches = self.tree_planning.listeTaches
        for tache in listeTaches :
            if tache[0] == IDmodif :
                listeDonnees = [tache[0], tache[1], tache[2], tache[3], tache[4], tache[5], tache[6], tache[7], tache[8]]
                break              
        
        frame_SaisiePresences = DLG_Saisie_presence.Frm_SaisiePresences(self, listeDonnees=listeDonnees, IDmodif=IDmodif, mode="modele")
        frame_SaisiePresences.Show()
        frame_SaisiePresences.panel.sizer_1.Hide(False)
        frame_SaisiePresences.panel.sizer_donnees_staticbox.Hide()
        frame_SaisiePresences.panel.grid_sizer_base.Layout()
        frame_SaisiePresences.SetMinSize((400, 320))
        frame_SaisiePresences.SetSize((400, 320))
        


    def OnBoutonSupprimer(self, event):
        """ Supprimer une tâche """
        IDmodif = self.tree_planning.selection
        
        if IDmodif >= 100000 or IDmodif==None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez pas sélectionné de tâche à supprimer dans la liste"), "Erreur de saisie", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy() 
            return
        
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette tâche ?"),  _(u"Suppression d'une tâche"), wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
        if dlg.ShowModal() == wx.ID_NO :
            dlg.Destroy() 
            return
        dlg.Destroy()
        
        # Recherche des données à mettre dans le formulaire de saisie
        listeTaches = self.tree_planning.listeTaches
        x = 0
        for tache in listeTaches :
            if tache[0] == IDmodif :
                index = x
                break
            x += 1
        
        if listeTaches[index][9] == "new" :  
            listeTaches.pop(index)
        else:
            listeTaches[index][9] = "suppr" 
        
        # MAJ du tree
        self.tree_planning.Remplissage()
    
    def ActivationBoutons(self, ajouter=True, modifier=True, supprimer=True) :
        self.bouton_ajouter.Enable(ajouter)
        self.bouton_modifier.Enable(modifier)
        self.bouton_supprimer.Enable(supprimer)
        

class TreeCtrlPlanning(wx.TreeCtrl):
    def __init__(self, parent):
        wx.TreeCtrl.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, style=wx.TR_NO_BUTTONS)
        # Autres styles possibles = wx.TR_HAS_BUTTONS|wx.TR_EDIT_LABELS| wx.TR_MULTIPLE|wx.TR_HIDE_ROOT
        self.parent = parent
        
        self.listeTaches = []
        if self.GetGrandParent().IDmodele != 0 :
            self.listeTaches = self.Importation_taches(self.GetGrandParent().IDmodele)
        self.dictCategories = self.Importation_categories_presences()
        self.selection = None
        
        self.Remplissage()
                
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate, self)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSING, self.OnCollapsing, self)

    def OnCollapsing(self, event):
        event.Veto()
        
    def Remplissage(self):
        self.DeleteAllItems()
        
        # Création de la racine
        if self.GetGrandParent().nom == "" :
            nomModele = _(u"Nouveau modèle")
        else:
            nomModele = self.GetGrandParent().nom
        self.root = self.AddRoot(nomModele)
        if 'phoenix' in wx.PlatformInfo:
            self.SetItemData(self.root, None)
        else:
            self.SetPyData(self.root, None)
        
        # Création des périodes
        if self.GetGrandParent().periodes[0] == True :
            self.P1 = self.AppendItem(self.root, _(u"Toutes les périodes"))
            if 'phoenix' in wx.PlatformInfo:
                self.SetItemData(self.P1, 100000)
            else:
                self.SetPyData(self.P1, 100000)
            self.CreationJours(self.P1, 1)
        
        if self.GetGrandParent().periodes[1] == True :
            self.P2 = self.AppendItem(self.root, _(u"Périodes scolaires"))
            if 'phoenix' in wx.PlatformInfo:
                self.SetItemData(self.P2, 200000)
            else:
                self.SetPyData(self.P2, 200000)
            self.CreationJours(self.P2, 2)
        
        if self.GetGrandParent().periodes[2] == True :
            self.P3 = self.AppendItem(self.root, _(u"Vacances scolaires"))
            if 'phoenix' in wx.PlatformInfo:
                self.SetItemData(self.P3, 300000)
            else:
                self.SetPyData(self.P3, 300000)
            self.CreationJours(self.P3, 3)
        
        self.CreationTaches(None, None)
        
        self.ExpandAll()    
    
    def CreationJours(self, rootPeriode, numPeriode) :
        if self.GetGrandParent().type == "hebdo" :    
            listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
        else:
            listeJours = (_(u"Tous les jours"),)
        
        numJour = 1    
        for jour in listeJours :
            exec("self.P" + str(numPeriode) + "J" + str(numJour) + " = self.AppendItem(rootPeriode, jour)")
            exec("self.SetPyData(self.P" + str(numPeriode) + "J" + str(numJour) + " , (numPeriode*100000) + (numJour*10000)) ")
            numJour += 1

    def CreationTaches(self, rootJour, numJour) :
        print(self.listeTaches)
        for tache in self.listeTaches :
            ID = tache[0]
            type = tache[2]
            numPeriode = tache[3]
            numJour = tache[4]
            heure_debut = tache[5]
            heure_fin = tache[6]
            IDcategorie = tache[7]
            nom_categorie = self.dictCategories[IDcategorie]
            intitule = tache[8]
            etat = tache[9]
            
            if self.GetGrandParent().type == type and self.GetGrandParent().periodes[numPeriode-1] == True and etat != "suppr" :
                txtTache = heure_debut + "-" + heure_fin + " : " + nom_categorie
                if intitule != "" : txtTache += " (" + intitule + ")"
                exec("self.P" + str(numPeriode) + "J" + str(numJour) + "T" + str(ID) + " = self.AppendItem(self.P" + str(numPeriode) + "J" + str(numJour) + ", txtTache)")
                exec("self.SetPyData(self.P" + str(numPeriode) + "J" + str(numJour) + "T" + str(ID) + " , ID)")

    def Importation_taches(self, IDmodele=0):
        """ Récupération de la liste des catégories dans la base """
        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        req = "SELECT * FROM modeles_taches WHERE IDmodele=%d" % IDmodele
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        
        listeTaches = []
        for donnees in listeDonnees :
            l = []
            for d in donnees :
                l.append(d)
            l.append("init")
            listeTaches.append(l)

        return listeTaches               
            
    def Importation_categories_presences(self):
        DB = GestionDB.DB()
        req = "SELECT IDcategorie, nom_categorie FROM cat_presences"
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        DB.Close()
        # Transformation en dictionnaire
        dictCategories = {}
        for ID, nom in listeCategories :
            dictCategories[ID] = nom
        return dictCategories        
                    

    def OnSelChanged(self, event):
        self.item = event.GetItem()
        textItem = self.GetItemText(self.item)
        data = self.GetPyData(self.item)
        self.selection = data
        if data == None : 
            mode = "aucun"
        if data >= 100000 : 
            mode = "jour"
            if str(data)[1] == "0" : 
                mode = "aucun"
        if 0 < data < 100000 : mode = "tache"
        
        if mode == "jour" :
            self.GetGrandParent().ActivationBoutons(True, False, False)
        if mode == "tache" :
            self.GetGrandParent().ActivationBoutons(False, True, True)
        if mode == "aucun" :
            self.GetGrandParent().ActivationBoutons(False, False, False)
        
        event.Skip()
        

    def OnActivate(self, event):
        self.item = event.GetItem()
        data = self.GetPyData(self.item)
        self.selection = data
        if data == None : 
            mode = "aucun"
        if data >= 100000 : 
            mode = "jour"
            if str(data)[1] == "0" : 
                mode = "aucun"
        if 0 < data < 100000 : mode = "tache"
        
        self.GetGrandParent().OnBoutonModifier(None)
        event.Veto()


    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """

        # Recherche et sélection de l'item pointé avec la souris
        item = self.FindTreeItem(event.GetPosition())
        if item == None : return
        data = self.GetPyData(item)
        if data == None : return
        if data >= 100000 : 
            mode = "jour"
            if str(data)[1] == "0" : return
        if 0 < data < 100000 : mode = "tache"
        self.SelectItem(item, True)
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()
        
        if mode == "jour" :
            # Item Ajouter
            item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        if mode == "tache" :
            # Item Modifier
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

    def FindTreeItem(self, position):
        """ Permet de retrouver l'item pointé dans le TreeCtrl """
        item, flags = self.HitTest(position)
        if item and flags & (wx.TREE_HITTEST_ONITEMLABEL |
                             wx.TREE_HITTEST_ONITEMICON):
            return item
        return None
    
    def Menu_Ajouter(self, event):
        self.GetGrandParent().OnBoutonAjouter(None)
        
    def Menu_Modifier(self, event):
        self.GetGrandParent().OnBoutonModifier(None)

    def Menu_Supprimer(self, event):
        self.GetGrandParent().OnBoutonSupprimer(None)

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, IDmodele=1)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
