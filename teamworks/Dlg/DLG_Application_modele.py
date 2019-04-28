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
import sys
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import GestionDB
import datetime
import FonctionsPerso
from Dlg import DLG_Saisie_modele
from Dlg import DLG_Confirm_appli_modele
from Utils import UTILS_Adaptations
if 'phoenix' in wx.PlatformInfo:
    from wx.adv import DatePickerCtrl, DP_DROPDOWN
else :
    from wx import DatePickerCtrl, DP_DROPDOWN


class Panel(wx.Panel):
    def __init__(self, parent, selectionLignes=[], selectionPersonnes=[], selectionDates=(None, None) ):
        wx.Panel.__init__(self, parent, -1, name="panel_applicModele", style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.selectionLignes = selectionLignes
        self.selectionPersonnes = selectionPersonnes
        self.selectionDates = selectionDates
        
        self.panel_base_1 = wx.Panel(self, -1)
        self.panel_base_2 = wx.Panel(self.panel_base_1, -1)
        self.sizer_modeles_staticbox = wx.StaticBox(self.panel_base_2, -1, _(u"Sélection des modèles"))
        self.sizer_parametres_staticbox = wx.StaticBox(self.panel_base_2, -1, _(u"Sélection de la période et des personnes"))
        self.radio_btn_1 = wx.RadioButton(self.panel_base_2, -1, u"")
        self.radio_btn_2 = wx.RadioButton(self.panel_base_2, -1, _(u"Selon les paramètres suivants :"))
        self.label_periode = wx.StaticText(self.panel_base_2, -1, _(u"Période du :"))
        self.date_debut = DatePickerCtrl(self.panel_base_2, -1, style=DP_DROPDOWN)
        self.label_au = wx.StaticText(self.panel_base_2, -1, "au")
        self.date_fin = DatePickerCtrl(self.panel_base_2, -1, style=DP_DROPDOWN)
        self.label_personnes = wx.StaticText(self.panel_base_2, -1, "Personnes :")
        self.list_ctrl_personnes = listCtrl_Personnes(self.panel_base_2)
        self.list_ctrl_personnes.SetMinSize((20, 80)) 
        self.list_ctrl_modeles = listCtrl_Modeles(self.panel_base_2)
        self.list_ctrl_modeles.SetMinSize((20, 20)) 
        self.bouton_ajouter = wx.BitmapButton(self.panel_base_2, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self.panel_base_2, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_dupliquer = wx.BitmapButton(self.panel_base_2, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Dupliquer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self.panel_base_2, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_aide = wx.BitmapButton(self.panel_base_2, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Aide_L72.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self.panel_base_2, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Ok_L72.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self.panel_base_2, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Annuler_L72.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio1, self.radio_btn_1 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio2, self.radio_btn_2 )
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDupliquer, self.bouton_dupliquer)
        self.Bind(wx.EVT_CLOSE, self.OnClose) 
        
        self.boutonsEnabled(True, False, False)
        self.SetLabelRadio1()
        
        # Définit les dates des datePickers
        if self.selectionDates[0] != None : 
            jour = self.selectionDates[0].day
            mois = self.selectionDates[0].month-1
            annee = self.selectionDates[0].year
            date = wx.DateTime()
            date.Set(jour, mois, annee)
            self.date_debut.SetValue(date)
            
        if self.selectionDates[1] != None : 
            jour = self.selectionDates[1].day
            mois = self.selectionDates[1].month-1
            annee = self.selectionDates[1].year
            date = wx.DateTime()
            date.Set(jour, mois, annee)
            self.date_fin.SetValue(date)

    def __set_properties(self):
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un modèle")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le modèle sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le modèle sélectionné dans la liste")))
        self.bouton_dupliquer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour dupliquer le modèle sélectionné dans la liste")))

    def __do_layout(self):
        sizer_base_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_base_2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        sizer_modeles = wx.StaticBoxSizer(self.sizer_modeles_staticbox, wx.VERTICAL)
        grid_sizer_modeles = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_modeles = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        sizer_parametres = wx.StaticBoxSizer(self.sizer_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_manuel = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_dates = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_parametres.Add(self.radio_btn_1, 0, 0, 0)
        grid_sizer_parametres.Add(self.radio_btn_2, 0, 0, 0)
        grid_sizer_manuel.Add(self.label_periode, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.date_debut, 0, 0, 0)
        grid_sizer_dates.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.date_fin, 0, 0, 0)
        grid_sizer_manuel.Add(grid_sizer_dates, 1, wx.EXPAND, 0)
        grid_sizer_manuel.Add(self.label_personnes, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_manuel.Add(self.list_ctrl_personnes, 1, wx.EXPAND, 0)
        grid_sizer_manuel.AddGrowableCol(1)
        grid_sizer_parametres.Add(grid_sizer_manuel, 1, wx.LEFT|wx.EXPAND, 30)
        grid_sizer_parametres.AddGrowableCol(0)
        sizer_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_parametres, 1, wx.EXPAND, 0)
        grid_sizer_modeles.Add(self.list_ctrl_modeles, 1, wx.EXPAND, 0)
        grid_sizer_boutons_modeles.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons_modeles.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons_modeles.Add(self.bouton_dupliquer, 0, 0, 0)
        grid_sizer_boutons_modeles.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_modeles.Add(grid_sizer_boutons_modeles, 1, wx.EXPAND, 0)
        grid_sizer_modeles.AddGrowableRow(0)
        grid_sizer_modeles.AddGrowableCol(0)
        sizer_modeles.Add(grid_sizer_modeles, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_modeles, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        self.panel_base_2.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base_2.Add(self.panel_base_2, 1, wx.ALL|wx.EXPAND, 10)
        self.panel_base_1.SetSizer(sizer_base_2)
        sizer_base_1.Add(self.panel_base_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base_1)
        sizer_base_1.Fit(self)
        self.Layout()
        self.grid_sizer_manuel = grid_sizer_manuel

    def SetLabelRadio1(self):
        """ Assigne un label au radio1 """
        if self.parent.GetName() == "panel_applicModele_FicheInd" :
            if len(self.selectionLignes) == 0 : txt = _(u"Selon les dates sélectionnées dans le calendrier")
            elif len(self.selectionLignes) == 1 : txt = _(u"Selon la date sélectionnée dans le calendrier")
            else : txt = _(u"Selon les ") + str(len(self.selectionLignes)) + _(u" dates sélectionnées dans le calendrier")
        else :
            if len(self.selectionLignes) == 0 : txt = _(u"Selon les lignes sélectionnées dans le planning")
            elif len(self.selectionLignes) == 1 : txt = _(u"Selon la ligne sélectionnée dans le planning")
            else : txt = _(u"Selon les ") + str(len(self.selectionLignes)) + _(u" lignes sélectionnées dans le planning")
        self.radio_btn_1.SetLabel(txt)
        if len(self.selectionLignes) == 0 :
            self.radio_btn_1.Enable(False)
            self.radio_btn_2.SetValue(True)
            self.date_debut.Enable(True)
            self.date_fin.Enable(True)
        else :
            self.radio_btn_1.Enable(True)
            self.radio_btn_1.SetValue(True)
            self.date_debut.Enable(False)
            self.date_fin.Enable(False)

    def OnClose(self, event):
        self.Fermer()
        event.Skip()
        
    def OnRadio1(self, event):
        self.ParamEnabled(False)
    
    def OnRadio2(self, event):
        self.ParamEnabled(True)
    
    def ParamEnabled(self, etat):
        self.label_periode.Enable(etat)
        self.date_debut.Enable(etat)
        self.label_au.Enable(etat)
        self.date_fin.Enable(etat)
        self.label_personnes.Enable(etat)
        self.list_ctrl_personnes.Enable(etat)
    
    def boutonsEnabled(self, ajouter=True, modifier=True, supprimer=True):
        self.bouton_ajouter.Enable(ajouter)
        self.bouton_modifier.Enable(modifier)
        self.bouton_supprimer.Enable(supprimer)
        self.bouton_dupliquer.Enable(supprimer)
        
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Appliquerunmodledeprsences")

    def OnBoutonAnnuler(self, event):
        self.Fermer()

    def Fermer(self):
        if self.parent.GetName() == "panel_applicModele_FicheInd" :
            # Si appellée à partir de la fiche individuelle
            self.parent.GetParent().Fermer()
        else:
            # Sinon...
            self.parent.Fermer()
            
    def OnBoutonOk(self, event):
        """ Bouton Ok """
        # Vérifie qu'au moins un modèle a été coché
        selectionModeles = self.list_ctrl_modeles.selections
        if len(selectionModeles) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un modèle dans la liste proposée."), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy() 
            return
        
        DB = GestionDB.DB()
        # Récupération des modèles
        if len(selectionModeles) == 1 : selectionModelesTmp = "(%d)" % selectionModeles[0]
        else : selectionModelesTmp = str(tuple(selectionModeles))
        req = "SELECT * FROM modeles_planning WHERE IDmodele IN %s" % selectionModelesTmp
        DB.ExecuterReq(req)
        listeModeles = DB.ResultatReq()
        dictModeles = {}
        inclureFeries = False
        for modele in listeModeles :
            dictModeles[modele[0]] = (modele[1], modele[2], modele[3], modele[4], modele[5])
            if modele[5] == 1 : 
                inclureFeries = True
        # Récupération des tâches
        req = "SELECT * FROM modeles_taches WHERE IDmodele IN %s" % selectionModelesTmp
        DB.ExecuterReq(req)
        listeTaches = DB.ResultatReq()
        DB.Close()
        
        # On enlève les taches non utiles (d'autres périodes)
        listeExclusions = []
        for tache in listeTaches :
            typeModele = dictModeles[tache[1]][1]
            periodesModele = dictModeles[tache[1]][3]
            # Comparaison du type
            if typeModele != tache[2] :
                if tache[0] not in listeExclusions : listeExclusions.append(tache[0])
            else:
                if tache[3] == 1 and periodesModele[0] != "1" : 
                    if tache[0] not in listeExclusions : listeExclusions.append(tache[0])
                if tache[3] == 2 and periodesModele[1] != "1" : 
                    if tache[0] not in listeExclusions : listeExclusions.append(tache[0])
                if tache[3] == 3 and periodesModele[2] != "1" : 
                    if tache[0] not in listeExclusions : listeExclusions.append(tache[0])
        
        for exclusion in listeExclusions :
            index = 0
            for tache in listeTaches :
                if tache[0] == exclusion :
                    listeTaches.pop(index)
                    break
                index += 1
                
        # Creation du schéma d'application
        periodeEcole = { 1 : [], 2 : [], 3 : [], 4 : [], 5 : [], 6 : [], 7 : []}
        periodeVacs = { 1 : [], 2 : [], 3 : [], 4 : [], 5 : [], 6 : [], 7 : []}
        
        for tache in listeTaches :
            IDtache = tache[0]
            type = tache[2]
            periode = tache[3]
            jour = tache[4]
            heure_debut = tache[5]
            heure_fin = tache[6]
            IDcategorie = tache[7]
            intitule = tache[8]
            
            # Application periodeEcole :
            if periode == 1 or periode == 2 :
                if type == "journ" :
                    for numJour in range(1, 8) :
                        detailTache = (IDtache, heure_debut, heure_fin, IDcategorie, intitule)
                        periodeEcole[numJour].append(detailTache)
                if type == "hebdo" :
                    detailTache = (IDtache, heure_debut, heure_fin, IDcategorie, intitule)
                    periodeEcole[jour].append(detailTache)
            
            # Application periodeVacs :
            if periode == 1 or periode == 3 :
                if type == "journ" :
                    for numJour in range(1, 8) :
                        detailTache = (IDtache, heure_debut, heure_fin, IDcategorie, intitule)
                        periodeVacs[numJour].append(detailTache)
                if type == "hebdo" :
                    detailTache = (IDtache, heure_debut, heure_fin, IDcategorie, intitule)
                    periodeVacs[jour].append(detailTache)
                   
        # On vérifie que des taches ne se chevauchent pas dans le schéma d'application
        chevauchement = 0
        
        for numJour in range(1, 8) :
            for tacheRef in periodeEcole[numJour] :
                for tacheComp in periodeEcole[numJour] :
                    if tacheComp[0] != tacheRef[0] :
                        # Comparaison des horaires
##                        if tacheComp[1] < tacheRef[1] < tacheComp[2] : 
##                            chevauchement += 1
##                        if tacheComp[1] < tacheRef [2]< tacheComp[2] : 
##                            chevauchement += 1
                        if ( tacheComp[1] < tacheRef[2] ) and ( tacheComp[2] > tacheRef[1] ) : 
                            chevauchement += 1
                            
        for numJour in range(1, 8) :
            for tacheRef in periodeVacs[numJour] :
                for tacheComp in periodeVacs[numJour] :
                    if tacheComp[0] != tacheRef[0] :
                        # Comparaison des horaires
##                        if tacheComp[1] < tacheRef[1] < tacheComp[2] : 
##                            chevauchement += 1
##                        if tacheComp[1] < tacheRef [2]< tacheComp[2] : 
##                            chevauchement += 1
                        if ( tacheComp[1] < tacheRef[2] ) and ( tacheComp[2] > tacheRef[1] ) : 
                            chevauchement += 1                            
        
        if chevauchement > 0 :
            nbreModelesCoches = len(selectionModeles)
            txt = _(u"Les ") + str(nbreModelesCoches) + _(u" modèles que vous avez sélectionnés ne sont pas compatibles entre eux : Des tâches se chevauchent. \n\nDéselectionnez ou modifiez les tâches de l'un des modèles.")
            dlg = wx.MessageDialog(self, txt, "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy() 
            return
        
        # Application du schéma d'application
        listeCreationsTaches = []
        
        if self.radio_btn_1.GetValue() == True :
           
            # Récupération des dates extremes de la sélection de lignes
            listeDatesSelection = []
            for ligne in self.selectionLignes :
                listeDatesSelection.append(ligne[1])
            listeDatesSelection.sort()
            dateMin = listeDatesSelection[0]
            dateMax = listeDatesSelection[-1]
            
            # Récupération des dates de jours de vacances
            listeJoursVacs = self.Importation_Jours_Vacances(dateMin, dateMax)
            
            # Création de la liste des taches à créer            
            for ligne in self.selectionLignes :
                
                IDpersonne = ligne[0]
                date = ligne[1]
                jourSemaine = date.isoweekday() 
                if date in listeJoursVacs : periode = "vacs"
                else: periode = "ecole"
                
                if periode == "vacs" :
                    listTachesTemp = periodeVacs[jourSemaine]
                    for tache in listTachesTemp :
                        detailTache = (IDpersonne, date, tache[1], tache[2], tache[3], tache[4])
                        listeCreationsTaches.append(detailTache)
                        
                if periode == "ecole" :
                    listTachesTemp = periodeEcole[jourSemaine]
                    for tache in listTachesTemp :
                        detailTache = (IDpersonne, date, tache[1], tache[2], tache[3], tache[4])
                        listeCreationsTaches.append(detailTache)
                        

        if self.radio_btn_2.GetValue() == True :
            
            # Vérifie que au moins 1 nom de personnes a été coché dans le listCtrl
            if len(self.selectionPersonnes) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un nom dans la liste des personnes."), "Erreur", wx.OK)  
                dlg.ShowModal()
                dlg.Destroy()
                return
            
            # Vérifie que les dates données dans les datePickers sont correctes
            date_tmp = self.date_debut.GetValue()
            date_debut = datetime.date(date_tmp.GetYear(), date_tmp.GetMonth()+1, date_tmp.GetDay())
            date_tmp = self.date_fin.GetValue()
            date_fin = datetime.date(date_tmp.GetYear(), date_tmp.GetMonth()+1, date_tmp.GetDay())
            
            if date_debut > date_fin :
                dlg = wx.MessageDialog(self, _(u"La date de début doit être inférieure à la date de fin."), "Erreur de saisie", wx.OK)  
                dlg.ShowModal()
                dlg.Destroy()
                return
            
            # Création de la liste de dates
            listeDatesSelection = []
            nbreJours = (date_fin - date_debut).days + 1
            dateTemp = date_debut
            for date in range(nbreJours) :
                listeDatesSelection.append(dateTemp)
                dateTemp = dateTemp + datetime.timedelta(days=1)
            listeDatesSelection.sort()
            dateMin = listeDatesSelection[0]
            dateMax = listeDatesSelection[-1]
            
            # Récupération des dates de jours de vacances
            listeJoursVacs = self.Importation_Jours_Vacances(dateMin, dateMax)
            
            # Création de la liste des taches à créer 
            for IDpersonne in self.selectionPersonnes :
                for date in listeDatesSelection :
                    jourSemaine = date.isoweekday()
                    if date in listeJoursVacs : periode = "vacs"
                    else: periode = "ecole"
            
                    if periode == "vacs" :
                        listTachesTemp = periodeVacs[jourSemaine]
                        for tache in listTachesTemp :
                            detailTache = [IDpersonne, date, tache[1], tache[2], tache[3], tache[4]]
                            listeCreationsTaches.append(detailTache)
                        
                    if periode == "ecole" :
                        listTachesTemp = periodeEcole[jourSemaine]
                        for tache in listTachesTemp :
                            detailTache = [IDpersonne, date, tache[1], tache[2], tache[3], tache[4]]
                            listeCreationsTaches.append(detailTache)         
        
        if len(listeCreationsTaches) == 0 :
            dlg = wx.MessageDialog(self, _(u"Selon les paramètres que vous avez saisis, aucune tâche n'est à créer..."), "Information", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        # Création de la liste formatée de confirmation
        dictCategories = self.Importation_categories_presences()
        
##        listeConfirmations = []
##        for tache in listeCreationsTaches :
##            nomPersonne = self.list_ctrl_personnes.dictPersonnes[tache[0]][0] + " " + self.list_ctrl_personnes.dictPersonnes[tache[0]][1]
##            date = DatetimeDateEnStr(tache[1])
##            horaires = tache[2][:2] + "h" + tache[2][3:] + "-" + tache[3][:2] + "h" + tache[3][3:]
##            categorie = dictCategories[tache[4]]
##            intitule = tache[5]
##            detailTache = (nomPersonne, date, horaires, categorie, intitule)
##            listeConfirmations.append(detailTache)
        
        dictConfirmations = {}
        for IDpersonne in self.selectionPersonnes :
            nomPersonne = self.list_ctrl_personnes.dictPersonnes[IDpersonne][0] + " " + self.list_ctrl_personnes.dictPersonnes[IDpersonne][1]
            dictConfirmations[(IDpersonne, nomPersonne)] = {}
            
        list(dictConfirmations.keys()).sort(reverse=True)
            
        for tache in listeCreationsTaches :
            IDpersonne = tache[0]
            nomPersonne = self.list_ctrl_personnes.dictPersonnes[IDpersonne][0] + " " + self.list_ctrl_personnes.dictPersonnes[IDpersonne][1]
            key = (IDpersonne, nomPersonne)
            date = tache[1]
            horaires = (tache[2] , tache[3]) #(tache[2][:2] + "h" + tache[2][3:] + "-" + tache[3][:2] + "h" + tache[3][3:]
            categorie = dictCategories[tache[4]]
            intitule = tache[5]
            #if len(dictConfirmations[nomPersonne]) == 0 :
            if date in dictConfirmations[key] :
                dictConfirmations[key][date].append( [horaires, categorie, intitule] )
                dictConfirmations[key][date].sort()
            else:                
                dictConfirmations[key][date] = [ [horaires, categorie, intitule], ]
        
        nbreTaches = len(listeCreationsTaches)
        
        # Fenêtre de demande de confirmation
        dlg = DLG_Confirm_appli_modele.Dialog(self, nbreTaches=nbreTaches, dictTaches=dictConfirmations, listeCreationsTaches=listeCreationsTaches, inclureFeries=inclureFeries)
        dlg.ShowModal()
        etat = dlg.etat
        dlg.Destroy()
        if etat == "termine":
            if self.parent.GetName() == "panel_applicModele_FicheInd":
                self.GetGrandParent().EndModal(wx.ID_OK)
            else:
                self.GetParent().EndModal(wx.ID_OK)

    def EnregistrementTaches(self, listeCreationsTaches) :
        """ Enregistrement des taches dans la base de données """        
        listeExceptions = []
                            
        # Récupération des dates de jours fériés
        self.listeFeriesFixes, self.listeFeriesVariables = self.Importation_Feries()
    
        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        for tache in listeCreationsTaches :

            IDpersonne = tache[0]
            date = tache[1]
            heure_debut = tache[2]
            heure_fin = tache[3]
            IDcategorie = tache[4]
            intitule = tache[5]
            
            valide = True

            # Vérifie qu'aucune tâche n'existe déjà à ce moment dans la base de données
            req = """
            SELECT IDpresence, date, heure_debut, heure_fin
            FROM presences
            WHERE (date='%s' AND IDpersonne=%d)  AND
            (heure_debut<'%s' And heure_fin>'%s');
            """ % (str(date), IDpersonne, heure_fin, heure_debut)
            DB.ExecuterReq(req)
            listePresences = DB.ResultatReq()
            nbreResultats = len(listePresences)
            
            # Un ou des présences existent à ce moment, donc pas d'enregistrement
            if nbreResultats != 0 :
                valide = False
                
            # Vérifie que ce n'est pas un jour férié
            #print date, type(date)
            if (date.day, date.month) in self.listeFeriesFixes :
                valide = False
            else:
                if date in self.listeFeriesVariables :
                    valide = False
            
            # Enregistrement si la date est bien valide
            if valide == True :
                listeDonnees = [    ("IDpersonne",     IDpersonne),
                                            ("date",               str(date)),
                                            ("heure_debut",    heure_debut),
                                            ("heure_fin",        heure_fin),
                                            ("IDcategorie",     IDcategorie),
                                            ("intitule",            intitule),
                                ]
                # Enregistrement dans la base
                ID = DB.ReqInsert("presences", listeDonnees)
                DB.Commit()
            else:
                
                # Si date non valide : on crée un rapport
                dictPersonnes = self.list_ctrl_personnes.dictPersonnes
                nomPersonne = dictPersonnes[IDpersonne][0] + " " + dictPersonnes[IDpersonne][1]
                listeExceptions.append((nomPersonne, DatetimeDateEnStr(date), (heure_debut, heure_fin)))

        # Fermeture de la base de données
        DB.Close()

        # Lecture de la liste des exceptions
        nbreInvalides =len(listeExceptions)
        nbreValides = len(listeCreationsTaches) - nbreInvalides
                
        if nbreInvalides != 0 :
            message = ""
            if nbreValides == 0 : message += _(u"Aucune tâche n'a été correctement enregistrée.\n\nL")
            elif nbreValides == 1 : message += str(nbreValides) + _(u" tâche a été correctement enregistrée.\n\nMais l")
            else: message += str(nbreValides) + _(u" tâches ont été correctement enregistrées.\n\nMais l")
            if nbreInvalides == 1 :
                message += _(u"a tâche de la liste suivante n'a pas pu être saisie car elle chevauchait une ou plusieurs des tâches existantes. ")
                message += _(u"Vous devrez donc d'abord supprimer ou modifier les horaires de ces tâches existantes avant de pouvoir saisir celle-ci.\n\n")
            else:
                message += _(u"es ") + str(nbreInvalides) + _(u" tâches de la liste suivante n'ont pas pu être saisies car elles chevauchaient des tâches existantes. ")
                message += _(u"Vous devrez donc d'abord supprimer ou modifier les horaires de ces tâches existantes avant de pouvoir saisir celles-ci.\n\n")
            for exception in listeExceptions :
                message += "   > Le " + exception[1] + " pour " + exception[0] + " de " + exception[2][0] + u" à " + exception[2][1] + ".\n"
            dlg = wx.lib.dialogs.ScrolledMessageDialog(self, message, _(u"Rapport d'erreurs"))
            dlg.ShowModal()
            
        #print "fin de la procedure d'enregistrement !!!"


    def Importation_Jours_Vacances(self, dateMin=None, dateMax=None):
        """ Importation des dates d'ouverture de la structure """
        
##        # Anciennce version :
##        conditions = ""
##        if dateMin != None and dateMax != None : 
##            conditions = " WHERE date_ouverture >= '" + str(dateMin) + "' AND date_ouverture <= '" + str(dateMax)  + "'"
##        DB = GestionDB.DB()
##        req = "SELECT * FROM dates_ouverture" + conditions + ";"
##        DB.ExecuterReq(req)
##        listeVacs1 = DB.ResultatReq()
##        DB.Close()
##
##        # Formatage des dates pour la liste
##        listeVacs2 = []
##        for date in listeVacs1:
##            dateTemp = datetime.date(int(date[1][:4]), int(date[1][5:7]), int(date[1][8:10]))
##            listeVacs2.append(dateTemp)
##        listeVacs2.sort()
##        return listeVacs2
    
        req = "SELECT * FROM periodes_vacances ORDER BY date_debut;"
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeVacances1 = DB.ResultatReq()
        DB.Close()
        
        listeVacances2 = []
        for id, nom, annee, date_debut, date_fin in listeVacances1 :
            datedebut = datetime.date(int(date_debut[:4]), int(date_debut[5:7]), int(date_debut[8:10]))
            datefin = datetime.date(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]))
            listeVacances2.append(datedebut)
            for x in range((datefin-datedebut).days) :
                datedebut = datedebut + datetime.timedelta(days=1)        
                listeVacances2.append(datedebut)
                
        return listeVacances2
    
    def Importation_Feries(self):
        """ Importation des dates des jours fériés """

        req = "SELECT * FROM jours_feries;"
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeFeriesTmp = DB.ResultatReq()
        DB.Close()
        
        listeFeriesFixes = []
        listeFeriesVariables = []
        for ID, type, nom, jour, mois, annee in listeFeriesTmp :
            if type =="fixe" :
                date = (jour, mois)
                listeFeriesFixes.append(date)            
            else:
                date = datetime.date(annee, mois, jour)
                listeFeriesVariables.append(date)
        return listeFeriesFixes, listeFeriesVariables
    
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
       
    def OnBoutonAjouter(self, event):
        """ Créer un nouveau modèle """
        dlg = DLG_Saisie_modele.Dialog(self, IDmodele=0)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonModifier(self, event):
        """ Modifier un modèle """
        index = self.list_ctrl_modeles.GetFirstSelected()
        if index == -1 : 
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un modèle dans la liste proposée"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy() 
            return
        IDmodele = self.list_ctrl_modeles.GetItemData(index)
        dlg = DLG_Saisie_modele.Dialog(self, IDmodele=IDmodele)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonSupprimer(self, event):
        """ Suppression d'un modèle """
        index = self.list_ctrl_modeles.GetFirstSelected()
        if index == -1 : 
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un modèle dans la liste proposée"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy() 
            return
        IDmodele = self.list_ctrl_modeles.GetItemData(index)
        nomModele = self.list_ctrl_modeles.dictModeles[IDmodele][0]
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer le modèle '") + nomModele + "' ?",  _(u"Suppression d'un modèle"), wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
        if dlg.ShowModal() == wx.ID_NO :
            dlg.Destroy() 
            return
        dlg.Destroy()
        
        if IDmodele in self.list_ctrl_modeles.selections :
                self.list_ctrl_modeles.selections.remove(IDmodele) 
        
        DB = GestionDB.DB()
        # Suppression des taches associées au modèle
        DB.ReqDEL("modeles_taches", "IDmodele", IDmodele)
        # Suppression du modèle
        DB.ReqDEL("modeles_planning", "IDmodele", IDmodele)
        DB.Close()
        
        # MAJ listCtrl Modeles
        self.list_ctrl_modeles.Remplissage()
        self.boutonsEnabled(True, False, False)


    def OnBoutonDupliquer(self, event):
        """ Dupliquer un modèle """
        # Demande de confirmation
        index = self.list_ctrl_modeles.GetFirstSelected()
        if index == -1 : 
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un modèle dans la liste proposée"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy() 
            return
        IDmodele = self.list_ctrl_modeles.GetItemData(index)
        nomModele = self.list_ctrl_modeles.dictModeles[IDmodele][0]
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment dupliquer le modèle '") + nomModele + u"' ?",  _(u"Duplication d'un modèle"), wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
        if dlg.ShowModal() == wx.ID_NO :
            dlg.Destroy() 
            return
        dlg.Destroy()
        
        # Duplication du modèle
        saisieModele = DLG_Saisie_modele.Frm_SaisieModele(self, IDmodele=IDmodele)
        saisieModele.Show()
        
        saisieModele.IDmodele = 0
        saisieModele.text_nom.SetValue(_(u"Copie de %s") % nomModele)
        
        
        
        

# -----------------------------------------------------------------------------------------------------------------------------------------------------------

class listCtrl_Personnes(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.LC_NO_HEADER)
        CheckListCtrlMixin.__init__(self)
        self.parent = parent
        
        self.dictPersonnes = self.Import_Personnes()
        self.Remplissage()
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)


    def Remplissage(self):
        self.ClearAll()
        # Création des colonnes
        self.InsertColumn(0, "Personnes")

        # Remplissage avec les valeurs
        for key, valeurs in self.dictPersonnes.items():
            if 'phoenix' in wx.PlatformInfo:
                index = self.InsertItem(six.MAXSIZE, valeurs[0] + " " + valeurs[1])
            else:
                index = self.InsertStringItem(six.MAXSIZE, valeurs[0] + " " + valeurs[1])
            self.SetItemData(index, key)
            # Sélection
            if key in self.GetGrandParent().GetParent().selectionPersonnes :
                self.CheckItem(index)

        # Ajustement tailles colonnes
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)

        # Tri
        self.SortItems(self.columnSorter)
                
    def columnSorter(self, key1, key2):
        item1 = self.dictPersonnes[key1][0] + " " + self.dictPersonnes[key1][1]
        item2 = self.dictPersonnes[key2][0] + " " + self.dictPersonnes[key2][1]
        if item1 == item2:  
            return 0
        elif item1 < item2: 
            return -1
        else:           
            return 1

    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)

    # this is called by the base class when an item is checked/unchecked
    def OnCheckItem(self, index, flag):
        IDpersonne = self.GetItemData(index)
        selection = self.GetGrandParent().GetParent().selectionPersonnes
        if flag:
            if IDpersonne not in selection :
                selection.append(IDpersonne)            
        else:
            if IDpersonne in selection :
                selection.remove(IDpersonne) 

    def Import_Personnes(self):
        """ Importe les noms des personnes de la base """
        
        req = """
            SELECT IDpersonne, nom, prenom
            FROM personnes 
            ORDER BY nom;
        """
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()

        # Transformation de la liste en dict
        dictPersonnes = {}
        for personne in listeDonnees :
            dictPersonnes[personne[0]] = [personne[1], personne[2]] # Nom, prénom
        
        return dictPersonnes
        



# -----------------------------------------------------------------------------------------------------------------------------------------------------------



class listCtrl_Modeles(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_VRULES )
        CheckListCtrlMixin.__init__(self)
        self.parent = parent

        self.selections = []
        self.Remplissage()
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)


    def Remplissage(self):
        """ Remplissage du listCtrl """
        self.dictModeles = self.Import_Modeles()
        self.ClearAll()
        # Création des colonnes
        self.InsertColumn(0, "Nom")
        self.InsertColumn(1, "Description")

        # Remplissage avec les valeurs
        for key, valeurs in self.dictModeles.items():
            if 'phoenix' in wx.PlatformInfo:
                index = self.InsertItem(six.MAXSIZE, valeurs[0])
                self.SetItem(index, 1, valeurs[1])
            else:
                index = self.InsertStringItem(six.MAXSIZE, valeurs[0])
                self.SetStringItem(index, 1, valeurs[1])
            self.SetItemData(index, key)
            # Sélection
            if key in self.selections :
                self.CheckItem(index)

        # Ajustement tailles colonnes
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)

        # Tri
        self.SortItems(self.columnSorter)

                
    def columnSorter(self, key1, key2):
        item1 = self.dictModeles[key1][0] 
        item2 = self.dictModeles[key2][0] 
        if item1 == item2:  
            return 0
        elif item1 < item2: 
            return -1
        else:           
            return 1

    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)
        
    def OnItemSelected(self, event):
        self.GetGrandParent().GetParent().boutonsEnabled(True, True, True)
        
    def OnItemDeselected(self, event):
        self.GetGrandParent().GetParent().boutonsEnabled(True, False, False)

    # this is called by the base class when an item is checked/unchecked
    def OnCheckItem(self, index, flag):
        IDmodele = self.GetItemData(index)
        if flag:
            if IDmodele not in self.selections :
                self.selections.append(IDmodele)            
        else:
            if IDmodele in self.selections :
                self.selections.remove(IDmodele) 

    def Import_Modeles(self):
        """ Importe les modèles de la base """
        
        req = """
            SELECT IDmodele, nom, description
            FROM modeles_planning 
            ORDER BY nom;
        """
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Transformation de la liste en dict
        dictModeles = {}
        for modele in listeDonnees :
            dictModeles[modele[0]] = [modele[1], modele[2]] # Nom, prénom
        
        return dictModeles
    
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """

        # Recherche et sélection de l'item pointé avec la souris
        index = self.GetFirstSelected()
        if index == -1 :
            mode = "selected"
        else:
            mode = "deselected"
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()
        
        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Créer un nouveau modèle"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        if mode == "deselected" :
            
            menuPop.AppendSeparator()
            
            # Item Modifier
            item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Menu_Modifier, id=20)

            # Item Dupliquer
            item = wx.MenuItem(menuPop, 40, _(u"Dupliquer"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Dupliquer.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Menu_Dupliquer, id=40)
            
            # Item Supprimer
            item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def Menu_Ajouter(self, event):
        self.GetGrandParent().GetParent().OnBoutonAjouter(None)
        
    def Menu_Modifier(self, event):
        self.GetGrandParent().GetParent().OnBoutonModifier(None)

    def Menu_Supprimer(self, event):
        self.GetGrandParent().GetParent().OnBoutonSupprimer(None)

    def Menu_Dupliquer(self, event):
        self.GetGrandParent().GetParent().OnBoutonDupliquer(None)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, selectionLignes=[], selectionPersonnes=[], selectionDates=(None, None)):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.panel = Panel(self, selectionLignes=selectionLignes, selectionPersonnes=selectionPersonnes, selectionDates=selectionDates)
        self.SetTitle(_(u"Application d'un modèle"))

        # Propriétés
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetMinSize((430, 500))
        
        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.panel, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        self.CenterOnScreen()
    
    def Fermer(self):
        self.EndModal(wx.ID_CANCEL)




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    selectionLignes = [(1, datetime.date(2008, 3, 10)), (1, datetime.date(2008, 3, 11)), (1, datetime.date(2008, 3, 12)), (1, datetime.date(2008, 3, 13)), ]
    dlg = Dialog(None, selectionLignes=selectionLignes)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
