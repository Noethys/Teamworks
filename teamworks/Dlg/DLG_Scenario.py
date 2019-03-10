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
import FonctionsPerso
import wx.grid as gridlib
import calendar
import wx.lib.agw.hyperlink as hl
import wx.lib.scrolledpanel as scrolled
import os
import sys
from Utils import UTILS_Fichiers
from Dlg import DLG_Scenario_select_categories
from Dlg import DLG_Scenario_select_periode
from Dlg import DLG_Scenario_saisie_prevision
from Dlg import DLG_Scenario_saisie_report
if 'phoenix' in wx.PlatformInfo:
    from wx.adv import DatePickerCtrl, DP_DROPDOWN, EVT_DATE_CHANGED
else :
    from wx import DatePickerCtrl, DP_DROPDOWN, EVT_DATE_CHANGED


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateEngEnDateDD(dateEng):
    """ Tranforme une date anglaise en datetime.date """
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DatetimeDateEnStr(date):
    """ Transforme un datetime.date en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = ("Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche")
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), "juin", _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateStr = listeJours[date.weekday()] + " " + str(date.day) + " " + listeMois[date.month-1] + " " + str(date.year)
    return dateStr


class Dialog(wx.Dialog):
    def __init__(self, parent, IDscenario=None, IDpersonne=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDscenario = IDscenario
        self.panel = wx.Panel(self, -1)
        
        # StaticBox
        self.staticbox_param = wx.StaticBox(self.panel, -1, _(u"Paramètres du scénario"))
        self.staticbox_legende = wx.StaticBox(self.panel, -1, _(u"Légende"))
        self.staticbox_detail = wx.StaticBox(self.panel, -1, _(u"Détail du scénario"))
        
        # Nom
        self.label_nom = wx.StaticText(self.panel, -1, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self.panel, -1, u"")
        
        # Description
        self.label_description = wx.StaticText(self.panel, -1, _(u"Description :"))
        self.ctrl_description = wx.TextCtrl(self.panel, -1, u"", style=wx.TE_MULTILINE)
        
        # Personne
        self.label_personne = wx.StaticText(self.panel, -1, "Personne :")
        self.listePersonnes, self.dictPersonnes = self.GetListePersonnes()
        self.ctrl_personne = wx.Choice(self.panel, -1, choices = self.listePersonnes)
        if IDpersonne != None :
            self.SetPersonne(IDpersonne)
            self.ctrl_personne.Enable(False)
            
        # Période
        self.label_date_debut = wx.StaticText(self.panel, -1, _(u"Période du :"))
        self.ctrl_date_debut = DatePickerCtrl(self.panel, -1, style=DP_DROPDOWN)
        self.label_date_fin = wx.StaticText(self.panel, -1, "au")
        self.ctrl_date_fin = DatePickerCtrl(self.panel, -1, style=DP_DROPDOWN)
        
        # Coche toutes catégories
        self.ctrl_toutes_categories = wx.CheckBox(self.panel, -1, _(u"Inclure toutes les catégories utilisées"))
        self.ctrl_toutes_categories.SetValue(True)
        
        # Hyperlink Sélection des catégories
        self.hyperlink_categories = self.Build_Hyperlink()
        
        # Panel Légende
        self.panelLegende = PanelLegende(self.panel)
        
        # Choix affichage détail
        self.label_detail = wx.StaticText(self.panel, -1, _(u"Détail :"))
        self.ctrl_detail = wx.Choice(self.panel, -1, choices = [_(u"Aucun"), _(u"Jour"), _(u"Mois"), _(u"Année")])
        self.ctrl_detail.SetSelection(0)
        
        # Choix affichage heure/décimal
        self.label_modeHeure = wx.StaticText(self.panel, -1, _(u"Mode minutes :"))
        self.ctrl_modeHeure = wx.Choice(self.panel, -1, choices = [_(u"Normal"), _(u"Décimal")])
        self.ctrl_modeHeure.SetSelection(0)
        
        if IDscenario != None : 
            self.Importation_parametres()
        else:
            anneeEnCours = datetime.date.today().year
            self.SetDatePicker(self.ctrl_date_debut, datetime.date(year=anneeEnCours, month=1, day=1))
            self.SetDatePicker(self.ctrl_date_fin, datetime.date(year=anneeEnCours, month=12, day=31))
            
        # Tableau
        self.ctrl_tableau = Tableau(self.panel)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_excel= wx.BitmapButton(self.panel, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Export_excel.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer_tableau = wx.BitmapButton(self.panel, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Imprimer_tableau.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()
        
        self.ctrl_tableau.InitTableau()
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckToutesCategories, self.ctrl_toutes_categories )
        self.Bind(wx.EVT_CHOICE, self.OnChoicePersonne, self.ctrl_personne)
        self.Bind(wx.EVT_CHOICE, self.OnChoiceDetail, self.ctrl_detail)
        self.Bind(wx.EVT_CHOICE, self.OnChoiceModeHeure, self.ctrl_modeHeure)
        self.Bind(EVT_DATE_CHANGED, self.OnDateDebut, self.ctrl_date_debut)
        self.Bind(EVT_DATE_CHANGED, self.OnDateFin, self.ctrl_date_fin)
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimerTableau, self.bouton_imprimer_tableau)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        
    def __set_properties(self):
        if self.IDscenario == 0 :
            self.SetTitle(_(u"Création d'un scénario"))
        else:
            self.SetTitle(_(u"Modification d'un scénario"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici un nom pour le scénario")))
        self.ctrl_description.SetToolTip(wx.ToolTip(_(u"Saisissez ici une description claire du scénario (optionnel)")))
        self.ctrl_personne.SetToolTip(wx.ToolTip(_(u"Sélectionnez une personne dans la liste proposée")))
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de début de période")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin de période")))
        self.ctrl_toutes_categories.SetToolTip(wx.ToolTip(_(u"Cochez cette option pour inclure dans le scénario \ntoutes les catégories pour lesquelles des présences \nont été enregistrées sur la période du scénario.")))
        self.ctrl_detail.SetToolTip(wx.ToolTip(_(u"Cette option vous permet de sélectionner le niveau de détail souhaité dans l'affichage des heure réalisées")))
        self.ctrl_modeHeure.SetToolTip(wx.ToolTip(_(u"Sélectionnez le mode d'affichage des minutes : normal ou décimal")))
        
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.bouton_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter les données des scénarios au format Excel")))
        self.bouton_imprimer_tableau.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour publier le tableau au format PDF")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Paramètres
        sizerStaticBox_param = wx.StaticBoxSizer(self.staticbox_param, wx.HORIZONTAL)
        grid_sizer_param = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        
        grid_sizer_param.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.ctrl_nom, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_param.Add(self.label_description, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_param.Add(self.ctrl_description, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_param.Add(self.label_personne, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_param.Add(self.ctrl_personne, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_param.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_periode.Add(self.ctrl_date_debut, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_periode.Add( (5, 5), 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_periode.Add(self.ctrl_toutes_categories, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_periode.AddGrowableCol(3)
        grid_sizer_param.Add(grid_sizer_periode, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_param.AddGrowableCol(1)
        sizerStaticBox_param.Add(grid_sizer_param, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_haut.Add(sizerStaticBox_param, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 0)
        
        # Légende
        sizerStaticBox_legende = wx.StaticBoxSizer(self.staticbox_legende, wx.HORIZONTAL)
        sizerStaticBox_legende.Add(self.panelLegende, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_haut.Add(sizerStaticBox_legende, 0, wx.EXPAND|wx.LEFT, 5)
        grid_sizer_haut.AddGrowableCol(1)
        
        grid_sizer_base.Add(grid_sizer_haut, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 10)
        
        # Détail du scénario
        sizerStaticBox_detail = wx.StaticBoxSizer(self.staticbox_detail, wx.HORIZONTAL)
        grid_sizer_detail = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        grid_sizer_detail.Add(self.ctrl_tableau, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=8, vgap=5, hgap=5)
        grid_sizer_options.Add(self.label_detail, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_options.Add(self.ctrl_detail, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_options.Add( (5, 5), 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_options.Add(self.label_modeHeure, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_options.Add(self.ctrl_modeHeure, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_options.Add( (5, 5), 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_options.Add(self.hyperlink_categories, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_options.AddGrowableCol(5)
        grid_sizer_detail.Add(grid_sizer_options, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_detail.AddGrowableRow(0)
        grid_sizer_detail.AddGrowableCol(0)
        sizerStaticBox_detail.Add(grid_sizer_detail, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(sizerStaticBox_detail, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_excel, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer_tableau, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(3)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
                
        self.panel.SetSizer(grid_sizer_base)
        self.Layout()
        
        self.SetSize((900, 700))
        self.CentreOnScreen()

        
    def OnDateDebut(self, event):
        self.ctrl_tableau.MAJ()
        
    def OnDateFin(self, event):
        self.ctrl_tableau.MAJ()
        
    def OnCheckToutesCategories(self, event):
        self.ctrl_tableau.MAJ()
    
    def OnChoicePersonne(self, event):
        self.ctrl_tableau.MAJ()
        
    def OnChoiceDetail(self, event):
        self.ctrl_tableau.MAJ()
    
    def OnChoiceModeHeure(self, event):
        self.ctrl_tableau.MAJ()

    def Build_Hyperlink(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self.panel, -1, _(u"Ajouter ou supprimer des catégories"), URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLUE", "BLUE", "RED")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(True, True, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner les catégories à inclure dans votre scénario")))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink(self, event):
        """ Sélectionner catégories à inclure """
        listeSelectionsDefaut = self.ctrl_tableau.listeCategoriesPrevues
        listeDisabledItems = [999,] 
        dlg = DLG_Scenario_select_categories.MyDialog(self, listeSelectionsDefaut, listeDisabledItems)
        if dlg.ShowModal() == wx.ID_OK:
            listeSelections = dlg.GetListeSelections()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        
        # Suppression d'une catégorie
        for IDcategorie in listeSelectionsDefaut :
            if IDcategorie not in listeSelections :
                del self.ctrl_tableau.dictVirtualDB[IDcategorie]

        # Ajout d'une catégorie
        for IDcategorie in listeSelections :
            if IDcategorie not in listeSelectionsDefaut :
                self.ctrl_tableau.dictVirtualDB[IDcategorie] = self.ctrl_tableau.CreateNewCategorie(IDcategorie)
                #self.ctrl_tableau.dictVirtualDB[IDcategorie]["etat"] = "ajout"

        # MAJ tableau
        self.ctrl_tableau.MAJ()

    def GetListePersonnes(self):
        DB = GestionDB.DB()
        req = "SELECT IDpersonne, nom, prenom FROM personnes ORDER BY nom, prenom;"
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listePersonnes = []
        dictPersonnes = {}
        if len(listeDonnees) != 0 : 
            index = 0
            for IDpersonne, nom, prenom in listeDonnees :
                listePersonnes.append( (u"%s %s" % (nom, prenom)) )
                dictPersonnes[index] = (IDpersonne, nom, prenom)
                index += 1
        return listePersonnes, dictPersonnes
                
    def SetDatePicker(self, controle, date) :
        """ Met une date au format datetime dans un datePicker donné """
        annee = int(date.year)
        mois = int(date.month)-1
        jour = int(date.day)
        date = wx.DateTime()
        date.Set(jour, mois, annee)
        controle.SetValue(date)
        
    def GetDatePickerValue(self, controle):
        """ Renvoie la date au format datetime d'un datePicker """
        date_tmp = controle.GetValue()
        return datetime.date(date_tmp.GetYear(), date_tmp.GetMonth()+1, date_tmp.GetDay())
    
    def GetDatesPeriode(self):
        date_debut = self.GetDatePickerValue(self.ctrl_date_debut)
        date_fin = self.GetDatePickerValue(self.ctrl_date_fin)
        return date_debut, date_fin

    def GetIDpersonne(self):
        """ Renvoie l'IDpersonne de la liste des personnes """
        index = self.ctrl_personne.GetSelection()
        if index == -1 : return None
        IDpersonne = self.dictPersonnes[index][0]
        return IDpersonne

    def SetPersonne(self, IDpersonne=None):
        """ Sélectionne une personne à partir de son ID dans la liste des personnes """
        if IDpersonne == None : return
        for index, valeurs in self.dictPersonnes.items() :
            ID = valeurs[0]
            if IDpersonne == ID :
                self.ctrl_personne.SetSelection(index)
    
    def Importation_parametres(self):
        DB = GestionDB.DB()
        req = "SELECT * FROM scenarios WHERE IDscenario=%d" % self.IDscenario
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        for IDscenario, IDpersonne, nom, description, mode_heure, detail_mois, date_debut, date_fin, toutes_categories in listeDonnees :
            # Nom
            if nom == None : nom = ""
            self.ctrl_nom.SetLabel(nom)
            # Description
            if description == None : description = ""
            self.ctrl_description.SetLabel(description)
            # Personne
            self.SetPersonne(IDpersonne)
            # Période
            date_debut_DD = DateEngEnDateDD(date_debut)
            self.SetDatePicker(self.ctrl_date_debut, date_debut_DD)
            date_fin_DD = DateEngEnDateDD(date_fin)
            self.SetDatePicker(self.ctrl_date_fin, date_fin_DD)
            # Coche toutes catégories
            self.ctrl_toutes_categories.SetValue(toutes_categories)
            # Mode_detail
            self.ctrl_detail.SetSelection(detail_mois)
            # Mode_heure
            self.ctrl_modeHeure.SetSelection(mode_heure)

    def OnClose(self, event):
        self.OnBoutonAnnuler(None)

    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(58)

    def OnBoutonAnnuler(self, event):
        txtMessage = six.text_type((_(u"Voulez-vous vraiment annuler ? \n\nSi vous avez effectué des modifications dans ce scénario, elles seront annulées.")))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation d'annulation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        self.EndModal(wx.ID_CANCEL)
        
    def OnBoutonOk(self, event) :
        # Vérifie que des valeurs ont été saisies
        valeur = self.ctrl_nom.GetValue()
        if valeur == None or valeur == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour ce scénario !"), "Erreur", wx.OK|wx.ICON_ERROR)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return
        
        valeur = self.GetIDpersonne()
        if valeur == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une personne dans la liste proposée !"), "Erreur", wx.OK|wx.ICON_ERROR)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_personne.SetFocus()
            return
        
        # Vérifie qu'il n'y a aucune erreur de report
        if self.ctrl_tableau.nbreErreursReport > 0 :
            if self.ctrl_tableau.nbreErreursReport == 1 :
                texte = _(u"Une erreur de report a été trouvée. \n\nVeuillez modifier le report en question avant de sauvegarder ce scénario.")
            else:
                texte = _(u"%d erreurs de report ont été trouvées. \n\nVeuillez modifier les reports en question avant de sauvegarder ce scénario.") % nbreErreursReport
            dlg = wx.MessageDialog(self, texte, "Erreur de report", wx.OK|wx.ICON_ERROR)  
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Sauvegarde
        IDscenario = self.Sauvegarde()
        
        # MAJ de la frame parente
        if FonctionsPerso.FrameOuverte("gestion_scenarios") != None :
            self.GetParent().MAJ_ListCtrl(IDscenario)
            
        # Fermeture
        self.EndModal(wx.ID_OK)

    def Sauvegarde(self):
        DB = GestionDB.DB()     
        
        # Sauvegarde des paramètres du scénario
        IDpersonne = self.GetIDpersonne()
        nom = self.ctrl_nom.GetValue()
        description = self.ctrl_description.GetValue()
        mode_heure = self.ctrl_modeHeure.GetSelection()
        detail_mois = self.ctrl_detail.GetSelection()
        date_debut, date_fin = self.GetDatesPeriode()
        toutes_categories = int(self.ctrl_toutes_categories.GetValue())
        
        listeDonnees = [ ("IDpersonne",   IDpersonne),  
                                    ("nom",   nom),  
                                    ("description",    description),
                                    ("mode_heure",    mode_heure), 
                                    ("detail_mois",    detail_mois),
                                    ("date_debut",    str(date_debut)), 
                                    ("date_fin",    str(date_fin)),
                                    ("toutes_categories",    toutes_categories),
                                     ]
                                    
        if self.IDscenario == None :
            IDscenario = DB.ReqInsert("scenarios", listeDonnees) 
        else:
            DB.ReqMAJ("scenarios", listeDonnees, "IDscenario", self.IDscenario)
            IDscenario = self.IDscenario
        DB.Commit()

        # Sauvegarde des catégories de scénarios
        req = "SELECT IDscenario_cat, IDscenario, IDcategorie, prevision, report, date_debut_realise, date_fin_realise FROM scenarios_cat WHERE IDscenario=%d;" % IDscenario
        DB.ExecuterReq(req)
        listeCategoriesDB = DB.ResultatReq()

        dictVirtualDB = self.ctrl_tableau.dictVirtualDB
        
        # Ajout ou modification de catégories
        listeIDTraites = []
        for IDcategorie, valeurs in dictVirtualDB.items() :
            etat = valeurs["etat"]
            date_debut_realise = valeurs["date_debut_realise"]
            date_fin_realise = valeurs["date_fin_realise"]
            IDscenario_cat = valeurs["IDscenario_cat"]
            prevision = valeurs["prevision"]
            report = valeurs["report"]
        
            listeDonnees = [ ("IDscenario",   IDscenario),  
                                    ("IDcategorie",   IDcategorie),  
                                    ("prevision",    prevision),
                                    ("report",    report), 
                                    ("date_debut_realise",    date_debut_realise),
                                    ("date_fin_realise",    date_fin_realise), 
                                     ]
                                    
            if IDscenario_cat == None :
                IDscenario_cat = DB.ReqInsert("scenarios_cat", listeDonnees) 
            else:
                DB.ReqMAJ("scenarios_cat", listeDonnees, "IDscenario_cat", IDscenario_cat)
                IDscenario_cat = IDscenario_cat
            DB.Commit()
            
            # Créée une liste des IDscenario_cat traités :
            listeIDTraites.append(IDscenario_cat)
        
        # Suppression de scenarios_cat :
        for valeurs in listeCategoriesDB :
            IDscenario_cat = valeurs[0]
            if IDscenario_cat not in listeIDTraites :
                DB.ReqDEL("scenarios_cat", "IDscenario_cat", IDscenario_cat)
        
        # Fermeture de la DB
        DB.Close()
        
        return IDscenario

    def OnBoutonExcel(self, event):
        if "linux" in sys.platform :
            dlg = wx.MessageDialog(self, _(u"Désolé, cette fonction n'est pas disponible sous Linux."), _(u"Fonction indisponible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.ExportExcel()

    def OnBoutonImprimerTableau(self, event):
        """ Impression tableau de données """
        avecCouleurs = True
        
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        hauteur, largeur = A4
                
        # Initialisation du PDF
        nomDoc = UTILS_Fichiers.GetRepTemp("tableauScenarioTemp.pdf")
        if "win" in sys.platform : nomDoc = nomDoc.replace("/", "\\")
        tailleMarge = 40
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur, hauteur), leftMargin=tailleMarge, rightMargin=tailleMarge, topMargin=tailleMarge, bottomMargin=tailleMarge, )
        story = []
        
        # Récupération des données du tableau
        tableau = self.ctrl_tableau
        nbreColonnes = tableau.GetNumberCols()
        nbreLignes = tableau.GetNumberRows()
        
        # Initialisation du tableau
        dataTableau = []
        listeCouleurs = []
        
        # Création des colonnes
        largeursColonnes = []
        largeurColonne = 60
        largeurColonneLabel = 140
        for col in range(0, nbreColonnes) :
            if col == 0 : largeursColonnes.append(largeurColonneLabel)
            else: largeursColonnes.append(largeurColonne)
        
        listeStyles = [
                            ('GRID', (0,0), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
                            ('VALIGN', (0, 0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                            ('ALIGN', (0, 0), (-1, 0), 'CENTRE'), # Centre les labels de colonne
                            ('ALIGN', (1, 1), (-1,- 1), 'RIGHT'), # Valeurs à gauche
                            ('ALIGN', (0, 1), (0, -1), 'CENTRE'), # Colonne Label Ligne centrée
                            ('FONT',(0, 0),(-1,-1), "Helvetica", 8), # Donne la police de caract. + taille de police de la ligne de total
                            ]
                            
        # Création des lignes
        for numLigne in range(0, nbreLignes) :
            valeursLigne = []
            for numCol in range(0, nbreColonnes) :
                valeurCase = tableau.GetCellValue(numLigne, numCol)
                couleurCase = tableau.GetCellBackgroundColour(numLigne, numCol)
                if couleurCase != (255, 255, 255, 255) and avecCouleurs == True :
                    r, g, b = self.ConvertCouleur(couleurCase)
                    listeStyles.append( ('BACKGROUND', (numCol, numLigne), (numCol, numLigne), (r, g, b) ) )
                if numLigne == 0 :
                    valeurCase = valeurCase.replace(" ", "\n")
                valeursLigne.append(valeurCase)
            dataTableau.append(valeursLigne)
    
        # Style du tableau
        style = TableStyle(listeStyles)
        
        # Création du tableau
        tableau = Table(dataTableau, largeursColonnes,  hAlign='LEFT')
        tableau.setStyle(style)
        story.append(tableau)
        story.append(Spacer(0,20))
            
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)
        
    def ConvertCouleur(self, couleur):
        r, g, b = couleur
        return r/255.0, g/255.0, b/255.0
    
    def ExportExcel(self):
        """ Export de la liste au format Excel """
        
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        nomFichier = "ExportExcel.xls"
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
        nomScenario = self.ctrl_nom.GetValue()
        if nomScenario == None or nomScenario == "" : nomScenario = _(u"Scénario")
        ws1 = wb.add_sheet(nomScenario)
        
        # Remplissage de la feuille
        tableau = self.ctrl_tableau
        nbreColonnes = tableau.GetNumberCols()
        nbreLignes = tableau.GetNumberRows()
        
        for numLigne in range(0, nbreLignes) :
            for numCol in range(0, nbreColonnes) :
                valeurCase = tableau.GetCellValue(numLigne, numCol)
                ws1.write(numLigne, numCol, valeurCase)
                ws1.col(numCol).width = 7000
                
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



class Tableau(gridlib.Grid): 
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent, -1, size=(200, 200), style=wx.WANTS_CHARS)
        self.parent = parent.GetParent()
        self.IDscenario = self.parent.IDscenario
        self.nbreErreursReport = 0
        self.moveTo = None
        
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellLeftDClick)
        
        # Importation des catégories de présences
        self.dictCategories = self.Importation_categories()
        
        # Création du VirtualDB (table scenarios_cat)
        self.dictVirtualDB = self.GetVirtualDB(self.IDscenario)

        # Création Grid
        self.CreateGrid(0, 0)
        
        # Init Tableau
##        self.InitTableau()

    
    def MAJ(self):
        if self.GetNumberRows() > 0 : 
            # Suppression des lignes du tableau
            self.DeleteRows(0, self.GetNumberRows())
        if self.GetNumberCols() > 0 : 
            # Suppression des colonnes du tableau
            self.DeleteCols(0, self.GetNumberCols())
        self.ClearGrid()
        self.InitTableau()
        self.Refresh()


        
    def InitTableau(self):
        # Paramètres
        self.inclure_toutes_categories = self.parent.ctrl_toutes_categories.GetValue()
        self.mode_detail = self.parent.ctrl_detail.GetSelection()
        self.mode_heure = self.parent.ctrl_modeHeure.GetSelection()
        IDpersonne = self.parent.GetIDpersonne()
        date_debut, date_fin = self.parent.GetDatesPeriode()
        
        # Init liste légende
        self.listeLegendes = []
        self.listeReports = []
        
        # Importation des catégories du scénarios
        self.listeCategoriesPrevues = self.GetCategoriesPrevues()
        
        # Crée liste des mois
        date_debut, date_fin = self.parent.GetDatesPeriode()
        
        # Inclure les catégories non scénarisées
        if IDpersonne != None :
            self.listeCategoriesUtilisees = self.GetCategoriesUtilisees(IDpersonne, str(date_debut), str(date_fin))
        else:
            self.listeCategoriesUtilisees = []
        
        if len(self.listeCategoriesUtilisees) > 0 and self.inclure_toutes_categories == True :
            self.listeLegendes.append( ( ("texte", "*"), ("texte", _(u"Catégories utilisées mais non scénarisées")), _(u"Ces catégories ne sont pas scénarisées mais apparaissent puisque des présences correspondantes ont été enregistrées sur la période du scénario en cours")) )
                    
        self.listeCategoriesNonPrevues = []
        if self.inclure_toutes_categories == True :
            self.listeCategories = []
            for IDcategorie in self.listeCategoriesPrevues :
                self.listeCategories.append(IDcategorie)
            for IDcategorie in self.listeCategoriesUtilisees :
                if IDcategorie not in self.listeCategories :
                    self.listeCategories.append(IDcategorie)
                    self.listeCategoriesNonPrevues.append(IDcategorie)
        else:
            self.listeCategories = self.listeCategoriesPrevues
        self.listeCategories.sort()

        # Crée labels des lignes
        self.listeLabelsLigne = self.GetListeLabelsLignes()

        # Récupération des données de chaque colonne
        dictColonnes = {}
        for IDcategorie in self.listeCategories :
            if IDcategorie in self.listeCategoriesPrevues :
                IDscenario = self.IDscenario
            else:
                IDscenario = None
            dictDonneesColonne = self.GetValeursColonne(IDscenario, IDcategorie, IDpersonne, mode_detail=self.mode_detail)
            dictColonnes[IDcategorie] = dictDonneesColonne
        # Ajout de la colonne TOTAL
        dictColonneTotal= self.GetColonneTotal(dictColonnes)

        # Récupération des labels des lignes de détail
        listeLabelsDetails = []
        for IDscenario_cat, dictDonneesColonne in dictColonnes.items() :
            listeLabels = dictDonneesColonne["listeLabelsDetails"]
            for label in listeLabels :
                if label not in listeLabelsDetails :
                    listeLabelsDetails.append(label)
        listeLabelsDetails.sort()
        
        # Rajout des labels de détail dans la liste des labels
        index = 0
        for label in listeLabelsDetails :
            nomFormate = self.FormateLabelDetail(label)
            infoLigne = { "type" : "ligne", "label" : nomFormate, "code" : label, "couleur_fond_label" : "#FFFFFF", "couleur_police_label" : "#000000", "couleur_fond_case" : "#FFFFFF"}
            self.listeLabelsLigne.insert(6 + index, infoLigne)
            index += 1
                               
        # Création de la grille
        nbreLignes =  len(self.listeLabelsLigne) + 1 # +1 = entete de colonnes
        nbreColonnes = len(self.listeCategories) + 2 # +1 : Colonne des labels + Colonne Total
        
        if self.GetNumberRows() == 0 : 
            # Création des lignes du tableau
            self.AppendRows(nbreLignes)
        if self.GetNumberCols() == 0 : 
            # Création des colonnes du tableau
            self.AppendCols(nbreColonnes)
            
        self.SetColSize(0, 170)
        self.SetColLabelValue(0, "")
        self.SetColLabelValue(1, "")
        self.SetRowLabelSize(1)
        self.SetColLabelSize(1)
        for x in range(0, nbreColonnes):
            self.SetColLabelValue(x, "")
        for x in range(0, nbreLignes):
            self.SetRowLabelValue(x, "")
            
        # Remplissage des entetes de colonnes :
        index_col = 1
        for IDcategorie in self.listeCategories :
            if IDcategorie == 999 :
                nom_colonne = _(u"Sans catégorie")
                self.SetCellBackgroundColour(0, index_col, "#FFFFFF")
            else:
                nom_colonne = self.dictCategories[IDcategorie][0]
                if IDcategorie in self.listeCategoriesNonPrevues :
                    nom_colonne += "*"
                couleur_colonne = self.dictCategories[IDcategorie][3]
                couleur_colonne = eval(couleur_colonne)
                self.SetCellBackgroundColour(0, index_col, couleur_colonne)
            self.SetCellValue(0, index_col, nom_colonne)
            self.SetReadOnly(0, index_col, True)
            self.SetCellAlignment(0, index_col, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.SetRowSize(0, 50)
            self.SetColSize(index_col, 75)
            renderer = gridlib.GridCellAutoWrapStringRenderer()
            self.SetCellRenderer(0, index_col, renderer)
            index_col += 1
        # Ajout de la colonne TOTAL
        self.SetCellValue(0, index_col, _(u"Total"))
        self.SetReadOnly(0, index_col, True)
        self.SetCellAlignment(0, index_col, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.SetRowSize(0, 50)
        self.SetColSize(index_col, 75)
        
        # Remplissage des entetes de lignes :
        index_ligne = 1
        for dictLignes in self.listeLabelsLigne :
            
            type = dictLignes["type"]
            label = dictLignes["label"]
            code = dictLignes["code"]
            couleur_fond_label = dictLignes["couleur_fond_label"]
            couleur_police_label = dictLignes["couleur_police_label"]
            couleur_fond_case = dictLignes["couleur_fond_case"]
            
            if type == "groupe" :
            
                # Création du nom de groupe
                self.SetCellValue(index_ligne, 0, label)
                self.SetRowSize(index_ligne, 8)
                self.SetCellAlignment(index_ligne, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.SetCellBackgroundColour(index_ligne, 0, couleur_fond_label)
                self.SetReadOnly(index_ligne, 0, True)
                self.SetCellTextColour(index_ligne, 0, couleur_police_label)
                font = wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL)
                self.SetCellFont(index_ligne, 0, font)            
                for x in range(1, len(self.listeCategories)+2):
                    self.SetCellBackgroundColour(index_ligne, x, couleur_fond_case)
                    self.SetReadOnly(index_ligne, x, True)
                index_ligne += 1
            
            else :
                
                # Création de chaque ligne du groupe
                self.SetCellValue(index_ligne, 0, label)
                self.SetCellAlignment(index_ligne, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.SetCellBackgroundColour(index_ligne, 0, couleur_fond_label)
                self.SetReadOnly(index_ligne, 0, True)
                self.SetRowSize(index_ligne, 30)
                
                index_ligne += 1
        

        # Remplissage des cases
        self.nbreErreursReport = 0
        index_col = 1
        for IDcategorie in self.listeCategories :
            dictDonneesColonne = dictColonnes[IDcategorie]
            index_ligne = 1
            for dictLigne in self.listeLabelsLigne :
                type = dictLigne["type"]
                label = dictLigne["label"]
                code = dictLigne["code"]
                couleur_fond_label = dictLigne["couleur_fond_label"]
                couleur_police_label = dictLigne["couleur_police_label"]
                couleur_fond_case = dictLigne["couleur_fond_case"]
                
                if type == "ligne" :
                    # Recherche de la valeur de la case
                    self.SetCellAlignment(index_ligne, index_col, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                    self.SetReadOnly(index_ligne, index_col, True)
                    self.SetCellBackgroundColour(index_ligne, index_col, couleur_fond_case)
                    
                    if code in dictDonneesColonne :
                        valeur = dictDonneesColonne[code]
                        if valeur == None : valeur = ""
                        self.SetCellValue(index_ligne, index_col, self.FormateLabelCase(valeur, code))
                        if code == "report" :
                            # Affichage des erreurs de report
                            report = dictDonneesColonne[code] 
                            if report != None :
                                if report[0] == "A" :
                                    a, b, c, label, d = report.split(";")
                                    if label.startswith("ERREUR") :
                                        self.SetCellBackgroundColour(index_ligne, index_col, (255, 0, 0))
                                        if label[6:] == "1" : texteErreur = _(u"Un report ne peut pas provenir du scénario d'une autre personne !")
                                        elif label[6:] == "2" : texteErreur = _(u"Le report fait référence à un scénario supprimé !")
                                        else : texteErreur = _(u"Erreur inconnue !")
                                        self.listeLegendes.append( ( ("couleur", (255, 0, 0)), ("texte", _(u"Erreur de report : %s") % texteErreur), u"") )
                                        self.nbreErreursReport += 1
                                        
                        if code == "periode_realise" :
                            font = wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL)
                            self.SetCellFont(index_ligne, index_col, font)
                            self.SetCellAlignment(index_ligne, index_col, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                        
                        if "total" in code :
                            font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD)
                            self.SetCellFont(index_ligne, index_col, font)
                    
                index_ligne += 1
            
            index_col += 1
        
        
        # Ajout du total de la ligne
        index_ligne = 1
        for dictLigne in self.listeLabelsLigne :
            type = dictLigne["type"]
            label = dictLigne["label"]
            code = dictLigne["code"]
            couleur_fond_label = dictLigne["couleur_fond_label"]
            couleur_police_label = dictLigne["couleur_police_label"]
            couleur_fond_case = dictLigne["couleur_fond_case"]
            
            if type == "ligne" :
                if code in dictColonneTotal :
                    valeur = dictColonneTotal[code]
                    if valeur == None : valeur = ""
                    self.SetCellValue(index_ligne, index_col, self.FormateLabelCase(valeur, code))
                    font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD)
                    self.SetCellFont(index_ligne, index_col, font)
                    self.SetReadOnly(index_ligne, index_col, True)
                    self.SetCellAlignment(index_ligne, index_col, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
            index_ligne += 1
        
        # Légende
        for lettre, report_IDscenario, IDcategorie, report_heures, nomScenario, descriptionScenario in self.listeReports :
            IDcategorie = int(IDcategorie)
            if IDcategorie == 999 : nomCategorie = _(u"Sans catégorie")
            elif IDcategorie == 1000 : nomCategorie = _(u"Total")
            else : nomCategorie = self.dictCategories[int(IDcategorie)][0]
            self.listeLegendes.append( ( ("texte", "(%s)" % lettre), ("lien", _(u"Report depuis '%s' (%s)") % (nomScenario, nomCategorie), report_IDscenario, IDcategorie), _(u"Description de ce scénario : %s") % descriptionScenario) )
        self.parent.panelLegende.MAJ(self.listeLegendes)
        
        self.moveTo = (self.GetNumberRows()-1, self.GetNumberCols()-1)

    def FormateLabelCase(self, label, code):
        """ Formate le label pour chaque case """
        if code == "periode_realise" :
            # Formate les cases périodes
            date_debut, date_fin = label.split(";")
            if date_debut == "None" and date_fin == "None" : 
                return _(u"Tout")
            if date_debut == "3000-01-01" and date_fin == "3000-01-01" : 
                return _(u"Rien")
            if date_debut == "None" and date_fin != "None" : 
                return _(u"Jusqu'au\n%s") % DateEngFr(date_fin)
            if date_debut != "None" and date_fin == "None" : 
                return _(u"A partir du\n%s") % DateEngFr(date_debut)
            if date_debut != "None" and date_fin != "None" : 
                return _(u"Du %s\nau %s") % (DateEngFr(date_debut), DateEngFr(date_fin))
        elif code == "report" :
            # Formate les cases Report
            if label == None or label == "" : return ""
            if label[0] == "M" :
                label = label[1:]
                return self.FormateHeure(label)
            if label[0] == "A" :
                report_IDscenario, IDcategorie, report_heures, nomScenario, descriptionScenario = label.split(";")
                alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                lettre = alphabet[len(self.listeReports)]
                self.listeReports.append( (lettre, report_IDscenario, IDcategorie, report_heures, nomScenario, descriptionScenario) )
                texte = u"(%s)  %s" % (lettre, self.FormateHeure(report_heures))
                return texte
            return self.FormateHeure(label)
        else:
            # Formate les cases standard d'heures
            return self.FormateHeure(label)
            
    
    def FormateHeure(self, label):
        if label == None or label == "" : return ""
        signe = label[0]
        hr, mn = label[1:].split(":")
        if hr == "00" and mn == "00" : return ""
        if signe == "+" : 
            signe = ""
        else:
            signe = "- "
        if self.mode_heure == 0 :
            # Mode Heure
            texte = _(u"%s%sh%s") % (signe, hr, mn)
        else:
            # Mode décimal
            minDecimal = int(mn)*100/60
            texte = u"%s%s.%s" % (signe, hr, minDecimal)
        return texte
    
    def FormateLabelDetail(self, label):
        # Formate noms de mois :
        if len(label) == 6 or len(label) == 7 :
            numAnnee, numMois = label.split("-")
            listeMois = ("Janvier", _(u"Février"), "Mars", "Avril", "Mai", "Juin", "Juillet", _(u"Août"), "Septembre", "Octobre", "Novembre", _(u"Décembre"))
            texte = u"%s %s" % (listeMois[int(numMois)-1], numAnnee)
            return texte
        
        # Formate noms de jours :
        elif len(label) == 10 :
            dateDD = DateEngEnDateDD(label)
            dateStrFr = DatetimeDateEnStr(dateDD)
            return dateStrFr
        
        # Au cas ou :
        else :
            return label
        

    def OnIdle(self, event):
        if self.moveTo != None:
            nbLignes = self.GetNumberRows()
            nbCols = self.GetNumberCols()
            self.SetGridCursor(nbLignes-1, nbCols-1)
            #self.SetGridCursor(self.moveTo[0], self.moveTo[1])
            self.moveTo = None
        event.Skip()
    
    def OnCellLeftDClick(self, event):
        numLigne = event.GetRow()
        numCol = event.GetCol()
        
        if numLigne > 0 and len(self.listeCategories)+1 > numCol > 0 :
            codeLigne = self.listeLabelsLigne[numLigne-1]["code"]
            IDcategorie = self.listeCategories[numCol-1]
            
            if codeLigne == "periode_realise" :
                self.CommandeSelectionPeriode(IDcategorie)
                
            if codeLigne == "prevision" :
                self.CommandeSaisiePrevision(IDcategorie)
            
            if codeLigne == "report" :
                self.CommandeSaisieReport(IDcategorie)

    def CommandeSelectionPeriode(self, IDcategorie):
        if IDcategorie in self.dictVirtualDB :
            date_debut_defaut = self.dictVirtualDB[IDcategorie]["date_debut_realise"]
            if date_debut_defaut != None : date_debut_defaut = DateEngEnDateDD(date_debut_defaut)
            date_fin_defaut = self.dictVirtualDB[IDcategorie]["date_fin_realise"]
            if date_fin_defaut != None : date_fin_defaut = DateEngEnDateDD(date_fin_defaut)
        else:
            date_debut_defaut, date_fin_defaut = self.parent.GetDatesPeriode()
        dlg = DLG_Scenario_select_periode.MyDialog(self)
        dlg.SetDates(date_debut_defaut, date_fin_defaut)
        if dlg.ShowModal() == wx.ID_OK:
            date_debut, date_fin = dlg.GetDates()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        if date_debut != None : date_debut = str(date_debut)
        if date_fin != None : date_fin = str(date_fin)
        if IDcategorie in self.dictVirtualDB :
            # Modification d'une catégorie
            self.dictVirtualDB[IDcategorie]["date_debut_realise"] = date_debut
            self.dictVirtualDB[IDcategorie]["date_fin_realise"] = date_fin
        else:
            # Ajout d'une catégorie
            self.dictVirtualDB[IDcategorie] = self.CreateNewCategorie(IDcategorie)
            self.dictVirtualDB[IDcategorie]["date_debut_realise"] = date_debut
            self.dictVirtualDB[IDcategorie]["date_fin_realise"] = date_fin
        # MAJ tableau
        self.MAJ()
        
    def CommandeSaisiePrevision(self, IDcategorie):
        if IDcategorie in self.dictVirtualDB :
            prevision = self.dictVirtualDB[IDcategorie]["prevision"]
        else:
            prevision = "+00:00"
        dlg = DLG_Scenario_saisie_prevision.MyDialog(self, prevision, self.parent.ctrl_modeHeure.GetSelection())
        if dlg.ShowModal() == wx.ID_OK:
            prevision = dlg.GetPrevision()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        if IDcategorie in self.dictVirtualDB :
            # Modification d'une catégorie
            self.dictVirtualDB[IDcategorie]["prevision"] = prevision
        else:
            # Ajout d'une catégorie
            self.dictVirtualDB[IDcategorie] = self.CreateNewCategorie(IDcategorie)
            self.dictVirtualDB[IDcategorie]["prevision"] = prevision
        # MAJ tableau
        self.MAJ()

    def CommandeSaisieReport(self, IDcategorie):
        if IDcategorie in self.dictVirtualDB :
            report = self.dictVirtualDB[IDcategorie]["report"]
        else:
            report = None
        dlg = DLG_Scenario_saisie_report.MyDialog(self, self.IDscenario, self.parent.GetIDpersonne(), IDcategorie, report, self.parent.ctrl_modeHeure.GetSelection())
        if dlg.ShowModal() == wx.ID_OK:
            report = dlg.GetReport()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        if IDcategorie in self.dictVirtualDB :
            # Modification d'une catégorie
            self.dictVirtualDB[IDcategorie]["report"] = report
        else:
            # Ajout d'une catégorie
            self.dictVirtualDB[IDcategorie] = self.CreateNewCategorie(IDcategorie)
            self.dictVirtualDB[IDcategorie]["report"] = report
        # MAJ tableau
        self.MAJ()
        
    def GetColonneTotal(self, dictColonnes):
        listeLignesExceptions = ["date_debut_realise", "date_fin_realise", "IDscenario_cat", "periode_realise", "listeLabelsDetails", "IDcategorie"]
        dictTotauxLignes = {}
        for IDcategorie, dictDonneesColonne in dictColonnes.items() :
            for codeLigne, valeur in dictDonneesColonne.items() :
                if codeLigne not in listeLignesExceptions :
                    # Particularité de la ligne report
                    if codeLigne == "report" :
                        if valeur == None or valeur == "" : valeur = u"+00:00"
                        if valeur[0] == "M" :
                            valeur = valeur[1:]
                        if valeur[0] == "A" :
                            report_IDscenario, report_IDcategorie, report_heures, nomScenario, descriptionScenario = valeur.split(";")
                            valeur = report_heures
                    # Addition des colonnes
                    if codeLigne in dictTotauxLignes :
                        dictTotauxLignes[codeLigne] = self.OperationHeures(dictTotauxLignes[codeLigne], valeur, "addition")
                    else:
                        dictTotauxLignes[codeLigne] = valeur
                        
        return dictTotauxLignes
        
    def GetCategoriesPrevues(self):
        """ Recherche des catégories incluses dans le scénario chargé """
        self.IDscenario = self.parent.IDscenario    
        listeCategories = list(self.dictVirtualDB.keys())
        listeCategories.sort()
        return listeCategories
    
    
    
    
        
    def Importation_categories(self):
        DB = GestionDB.DB()
        req = "SELECT IDcategorie, nom_categorie, IDcat_parent, ordre, couleur FROM cat_presences"
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : return {}
        dictCategories = {}
        for IDcategorie, nom_categorie, IDcat_parent, ordre, couleur in listeDonnees :
            dictCategories[IDcategorie] = (nom_categorie, IDcat_parent, ordre, couleur)
        return dictCategories

##    def GetListeMoisPeriode(self, date_debut, date_fin) :
##        """ Liste les mois d'une période """
##        listeMois = [] # [num_mois, num_annee, nom_mois, date_debut_mois, date_fin_mois]
##        listeNomsMois = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))
##        
##        nbreJoursPeriode = (date_fin - date_debut).days
##        listeMois.append( (date_debut.month, date_debut.year,listeNomsMois[date_debut.month-1], datetime.date(date_debut.year, date_debut.month, 1), datetime.date(date_debut.year, date_debut.month, calendar.monthrange(year=date_debut.year, month=date_debut.month)[1]) ) )
##        
##        datePrecedente = date_debut
##        for listeJours in range(0, nbreJoursPeriode) :
##            date = datePrecedente + datetime.timedelta(days=1)
##            if date.month != datePrecedente.month :
##                listeMois.append( (date.month, date.year, listeNomsMois[date.month-1], datetime.date(date.year, date.month, 1), datetime.date(date.year, date.month, calendar.monthrange(year=date.year, month=date.month)[1]) ) )
##            datePrecedente = date
##        
##        return listeMois

    def GetListeLabelsLignes(self):
        # Labels de lignes de base :
        listeLignes = [
            
            { "type" : "groupe", "label" : _(u"Heures prévues"), "code" : "", "couleur_fond_label" : "#C0C0C0", "couleur_police_label" : "#FFFFFF", "couleur_fond_case" : "#C0C0C0"},
            { "type" : "ligne", "label" : _(u"Prévisions"), "code" : "prevision", "couleur_fond_label" : "#FFFFFF", "couleur_police_label" : "#000000", "couleur_fond_case" : "#F0F0EE"},
            { "type" : "ligne", "label" : _(u"Report"), "code" : "report", "couleur_fond_label" : "#FFFFFF", "couleur_police_label" : "#000000", "couleur_fond_case" : "#F0F0EE"},
            { "type" : "ligne", "label" : _(u"Total"), "code" : "total_heures_prevues", "couleur_fond_label" : "#FFFFFF", "couleur_police_label" : "#000000", "couleur_fond_case" : "#FFFFFF"},
            
            { "type" : "groupe", "label" : _(u"Heures réalisées"), "code" : "", "couleur_fond_label" : "#C0C0C0", "couleur_police_label" : "#FFFFFF", "couleur_fond_case" : "#C0C0C0"},
            { "type" : "ligne", "label" : _(u"Périodes de référence"), "code" : "periode_realise", "couleur_fond_label" : "#FFFFFF", "couleur_police_label" : "#000000", "couleur_fond_case" : "#F0F0EE"},
            { "type" : "ligne", "label" : _(u"Total"), "code" : "total_heures_realisees", "couleur_fond_label" : "#FFFFFF", "couleur_police_label" : "#000000", "couleur_fond_case" : "#FFFFFF"},
            
            { "type" : "groupe", "label" : _(u"Reste heures à réaliser"), "code" : "", "couleur_fond_label" : "#C0C0C0", "couleur_police_label" : "#FFFFFF", "couleur_fond_case" : "#C0C0C0"},
            { "type" : "ligne", "label" : _(u"Total"), "code" : "total_reste_heures", "couleur_fond_label" : "#FFFFFF", "couleur_police_label" : "#000000", "couleur_fond_case" : "#FFFFFF"},
        
        ]
        return listeLignes
    
    
    def GetVirtualDB(self, IDscenario=None):
        """ Mémorise la table scenarios_cat pour permettre l'annulation après modifications """
        dictVirtualDB = {}
        if IDscenario != None :
            DB = GestionDB.DB()
            req = "SELECT IDscenario_cat, IDscenario, IDcategorie, prevision, report, date_debut_realise, date_fin_realise FROM scenarios_cat WHERE IDscenario=%d;" % IDscenario
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            if len(listeDonnees) == 0 : return dictVirtualDB
            # Importation des données de base de la colonne
            for IDscenario_cat, IDscenario, IDcategorie, prevision, report, date_debut_realise, date_fin_realise in listeDonnees :
                dictDonnees = {}
                dictDonnees["IDscenario_cat"] = IDscenario_cat
                dictDonnees["IDscenario"] = IDscenario
                dictDonnees["prevision"] = prevision
                dictDonnees["report"] = report
                if date_debut_realise == "" : date_debut_realise = None
                dictDonnees["date_debut_realise"] = date_debut_realise
                if date_fin_realise == "" : date_fin_realise = None
                dictDonnees["date_fin_realise"] = date_fin_realise
                dictDonnees["etat"] = "initial" # initial, modif, suppr, ajout
                dictVirtualDB[IDcategorie] = dictDonnees
        else:
            # S'il s'agit d'une création de scénarios
            dictVirtualDB[999] = self.CreateNewCategorie(999)
            
        return dictVirtualDB
    
    def CreateNewCategorie(self, IDcategorie):
        dictDonnees = {}
        dictDonnees["IDscenario_cat"] = None
        dictDonnees["IDcategorie"] = IDcategorie
        dictDonnees["prevision"] = None
        dictDonnees["report"] = None
        date_debut, date_fin = self.parent.GetDatesPeriode()
        dictDonnees["date_debut_realise"] = str(date_debut)
        dictDonnees["date_fin_realise"] = str(date_fin)
        dictDonnees["etat"] = "ajout"
        return dictDonnees
    
    def GetValeursColonne(self, IDscenario=None, IDcategorie=None, IDpersonne=None, mode_detail=0, modeReport=False) :
        dictDonnees = {}

        # Récupération des données scénarisées
        if IDscenario != None :
            
            # Si c'est pour un report, on cherche dans la base de données directement
            if modeReport == True :
                # Si c'est une catégorie prévue
                DB = GestionDB.DB()
                req = "SELECT IDscenario_cat, IDscenario, IDcategorie, prevision, report, date_debut_realise, date_fin_realise FROM scenarios_cat WHERE IDscenario=%d AND IDcategorie=%d;" % (IDscenario, IDcategorie)
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                if len(listeDonnees) == 0 : 
                    dictDonnees["IDscenario_cat"] = None
                    dictDonnees["IDcategorie"] = IDcategorie
                    dictDonnees["prevision"] = None
                    dictDonnees["report"] = None
                    date_debut, date_fin = self.parent.GetDatesPeriode()
                    dictDonnees["date_debut_realise"] = str(date_debut)
                    dictDonnees["date_fin_realise"] = str(date_fin) 
                     
                # Importation des données de base de la colonne
                for IDscenario_cat, IDscenario, IDcategorie, prevision, report, date_debut_realise, date_fin_realise in listeDonnees :
                    dictDonnees["IDscenario_cat"] = IDscenario_cat
                    dictDonnees["IDcategorie"] = IDcategorie
                    dictDonnees["prevision"] = prevision
                    dictDonnees["report"] = report
                    if date_debut_realise == "" : date_debut_realise = None
                    dictDonnees["date_debut_realise"] = date_debut_realise
                    if date_fin_realise == "" : date_fin_realise = None
                    dictDonnees["date_fin_realise"] = date_fin_realise
            
            else:
                
                # Lecture de la VirtualDB
                if IDcategorie in self.dictVirtualDB :
                    dictDonnees["IDscenario_cat"] = self.dictVirtualDB[IDcategorie]["IDscenario_cat"]
                    dictDonnees["IDcategorie"] = IDcategorie
                    dictDonnees["prevision"] = self.dictVirtualDB[IDcategorie]["prevision"]
                    dictDonnees["report"] = self.dictVirtualDB[IDcategorie]["report"]
                    date_debut_realise = self.dictVirtualDB[IDcategorie]["date_debut_realise"]
                    if date_debut_realise == "" : date_debut_realise = None
                    dictDonnees["date_debut_realise"] = date_debut_realise
                    date_fin_realise = self.dictVirtualDB[IDcategorie]["date_fin_realise"]
                    if date_fin_realise == "" : date_fin_realise = None
                    dictDonnees["date_fin_realise"] = date_fin_realise
            
        else:
            
            # Lecture de la VirtualDB
            if IDcategorie in self.dictVirtualDB :
                dictDonnees["IDscenario_cat"] = self.dictVirtualDB[IDcategorie]["IDscenario_cat"]
                dictDonnees["IDcategorie"] = IDcategorie
                dictDonnees["prevision"] = self.dictVirtualDB[IDcategorie]["prevision"]
                dictDonnees["report"] = self.dictVirtualDB[IDcategorie]["report"]
                date_debut_realise = self.dictVirtualDB[IDcategorie]["date_debut_realise"]
                if date_debut_realise == "" : date_debut_realise = None
                dictDonnees["date_debut_realise"] = date_debut_realise
                date_fin_realise = self.dictVirtualDB[IDcategorie]["date_fin_realise"]
                if date_fin_realise == "" : date_fin_realise = None
                dictDonnees["date_fin_realise"] = date_fin_realise
            else :
                # Si c'est une catégorie NON prévue
                dictDonnees["IDscenario_cat"] = None
                dictDonnees["IDcategorie"] = IDcategorie
                dictDonnees["prevision"] = None
                dictDonnees["report"] = None
                date_debut, date_fin = self.parent.GetDatesPeriode()
                dictDonnees["date_debut_realise"] = str(date_debut)
                dictDonnees["date_fin_realise"] = str(date_fin)      
        
            
        # Calcul du total des heures prévues
        prevision = dictDonnees["prevision"]
        report = dictDonnees["report"]
        heures_report = "+00:00"
        if report != None :
            if report[0] == "M" :
                heures_report = report[1:]
            if report[0] == "A" :
                report_IDscenario, report_IDcategorie = report[1:].split(";")
                heures_report, nomScenario, descriptionScenario = self.GetReportColonne(int(report_IDcategorie), IDpersonne, int(report_IDscenario))
                dictDonnees["report"] = "%s;%s;%s;%s" % (report, heures_report, nomScenario, descriptionScenario)
        total_heures_prevues = self.OperationHeures(prevision, heures_report, "addition")
        dictDonnees["total_heures_prevues"] = total_heures_prevues
        
        # Formatage da la période du réalisé
        dictDonnees["periode_realise"] = "%s;%s" % (dictDonnees["date_debut_realise"], dictDonnees["date_fin_realise"])
        
        # Récupération des heures réalisées
        date_debut_realise = dictDonnees["date_debut_realise"]
        date_fin_realise = dictDonnees["date_fin_realise"]
        IDcategorie = dictDonnees["IDcategorie"]

        dictHeuresRealisees, listeLabelsDetails = self.GetHeuresRealisees(IDpersonne, date_debut_realise, date_fin_realise, IDcategorie, mode_detail)
        # Total heures réalisées
        total_heures_realisees = dictHeuresRealisees["total_heures_realisees"]
        dictDonnees["total_heures_realisees"] = total_heures_realisees
        # Détail Jour ou Mois des heures réalisées :
        dictDonnees["listeLabelsDetails"] = listeLabelsDetails
        for label in listeLabelsDetails :
            dictDonnees[label] = dictHeuresRealisees[label]
        
        # total reste heures
        total_reste_heures = self.OperationHeures(total_heures_prevues, total_heures_realisees, "soustraction")
        dictDonnees["total_reste_heures"] = total_reste_heures
                
        return dictDonnees
    
    def OperationHeures(self, heureA=None, heureB=None, operation="addition"):
        # Préparation heure A
        if heureA == None :
            totalMinutesA = 0
        else:
            signeA = heureA[0]
            hrA, mnA = heureA[1:].split(":")
            hrA, mnA = int(float(hrA)), int(float(mnA))
            totalMinutesA = (hrA*60) + mnA
            if signeA == "-" : totalMinutesA = -totalMinutesA
        # Préparation heure B
        if heureB == None :
            totalMinutesB = 0
        else:
            signeB = heureB[0]
            hrB, mnB = heureB[1:].split(":")
            hrB, mnB = int(float(hrB)), int(float(mnB))
            totalMinutesB = (hrB*60) + mnB
            if signeB == "-" : totalMinutesB = -totalMinutesB
        # Opération
        if operation == "addition" : totalMinutes = totalMinutesA + totalMinutesB
        if operation == "soustraction" : totalMinutes = totalMinutesA - totalMinutesB
        # Formatage du résultat
        if totalMinutes >= 0 :
            nbreHeures = totalMinutes/60
            nbreMinutes = totalMinutes-(nbreHeures*60)
        else:
            nbreHeures = -(-totalMinutes/60)
            nbreMinutes = -(totalMinutes-(nbreHeures*60))
        if len(str(nbreMinutes))==1 : nbreMinutes = str("0") + str(nbreMinutes)
        duree = str(nbreHeures) + ":" + str(nbreMinutes)
        if nbreHeures>=0 : duree = "+%s" % duree
        return duree
        
        
    def GetReportColonne(self, IDcategorie, IDpersonne, IDscenario) :
        """ Report d'une colonne """
        # Récupère le nom du scénario
        DB = GestionDB.DB()
        req = "SELECT IDscenario, nom, description, detail_mois, date_debut, date_fin, toutes_categories, IDpersonne FROM scenarios WHERE IDscenario=%d" % IDscenario
        DB.ExecuterReq(req)
        listePresences = DB.ResultatReq()
        
        if len(listePresences) == 0 :
            # Le scénario a été supprimé
            totalResteColonne, nomScenario, descriptionScenario = "+00:00", "ERREUR2", ""
            return totalResteColonne, nomScenario, descriptionScenario
        
        nomScenario = listePresences[0][1]
        descriptionScenario = listePresences[0][2]
        detail_mois = listePresences[0][3]
        date_debut = listePresences[0][4]
        date_fin = listePresences[0][5]
        toutes_categories = listePresences[0][6]
        reportIDpersonne = listePresences[0][7]
        
        if IDpersonne != reportIDpersonne :
            # Le report provient du scénario d'une autre personne
            totalResteColonne, nomScenario, descriptionScenario = "+00:00", "ERREUR1", ""
            return totalResteColonne, nomScenario, descriptionScenario
        
        # Récupère le nbre d'heures pour le report
        if IDcategorie == 1000 :
            valeurs = GetDictColonnes(IDscenario, IDpersonne, detail_mois, date_debut, date_fin, toutes_categories)
            dictDonneesColonne = valeurs.GetDictColonneTotal()
        else:
            dictDonneesColonne = self.GetValeursColonne(IDscenario, IDcategorie, IDpersonne, mode_detail=0, modeReport=True)
        totalResteColonne = dictDonneesColonne["total_reste_heures"]
        
        return totalResteColonne, nomScenario, descriptionScenario


    def GetHeuresRealisees(self, IDpersonne=None, date_debut_periode=None, date_fin_periode=None, IDcategorie=None, mode_detail=None):        
        if IDpersonne == None : return {"total_heures_realisees" : "+00:00"}, []
        DB = GestionDB.DB()
        if date_debut_periode != None and date_fin_periode != None : req = "SELECT IDpresence, date, heure_debut, heure_fin FROM presences WHERE (IDpersonne=%d AND IDcategorie=%d AND '%s'<=date AND date<='%s') ORDER BY date;" % (IDpersonne, IDcategorie, date_debut_periode, date_fin_periode)
        if date_debut_periode != None and date_fin_periode == None : req = "SELECT IDpresence, date, heure_debut, heure_fin FROM presences WHERE (IDpersonne=%d AND IDcategorie=%d AND '%s'<=date) ORDER BY date;" % (IDpersonne, IDcategorie, date_debut_periode)
        if date_debut_periode == None and date_fin_periode != None : req = "SELECT IDpresence, date, heure_debut, heure_fin FROM presences WHERE (IDpersonne=%d AND IDcategorie=%d AND '%s'>=date) ORDER BY date;" % (IDpersonne, IDcategorie, date_fin_periode)
        if date_debut_periode == None and date_fin_periode == None : req = "SELECT IDpresence, date, heure_debut, heure_fin FROM presences WHERE (IDpersonne=%d AND IDcategorie=%d) ORDER BY date;" % (IDpersonne, IDcategorie)
        DB.ExecuterReq(req)
        listePresences = DB.ResultatReq()
        if len(listePresences) == 0 : return {"total_heures_realisees" : "+00:00"}, []

        dictHeuresRealisees = {}
        total_heure_realisees = "+00:00"
        listeLabelsDetails = []
        
        for IDpresence, date, heure_debut, heure_fin in listePresences :
            dateDD = DateEngEnDateDD(date)
            # Addition pour le total de la catégorie
            duree = self.OperationHeures("+" + heure_fin, "+" + heure_debut, "soustraction")
            total_heure_realisees = self.OperationHeures(total_heure_realisees, duree, "addition")
            dictHeuresRealisees["total_heures_realisees"] = total_heure_realisees
            # Détail
            if mode_detail == 1 :
                codeJour = str(dateDD)
                if codeJour in dictHeuresRealisees :
                    dictHeuresRealisees[codeJour] = self.OperationHeures(dictHeuresRealisees[codeJour], duree, "addition")
                else:
                    dictHeuresRealisees[codeJour] = duree
                if codeJour not in listeLabelsDetails : listeLabelsDetails.append(codeJour)
            if mode_detail == 2 :
                codeMois = "%d-%02d" % (dateDD.year, dateDD.month)
                if codeMois in dictHeuresRealisees :
                    dictHeuresRealisees[codeMois] = self.OperationHeures(dictHeuresRealisees[codeMois], duree, "addition")
                else:
                    dictHeuresRealisees[codeMois] = duree
                if codeMois not in listeLabelsDetails : listeLabelsDetails.append(codeMois)
            if mode_detail == 3 :
                codeAnnee = str(dateDD.year)
                if codeAnnee in dictHeuresRealisees :
                    dictHeuresRealisees[codeAnnee] = self.OperationHeures(dictHeuresRealisees[codeAnnee], duree, "addition")
                else:
                    dictHeuresRealisees[codeAnnee] = duree
                if codeAnnee not in listeLabelsDetails : listeLabelsDetails.append(codeAnnee)

        return dictHeuresRealisees, listeLabelsDetails

    def GetCategoriesUtilisees(self, IDpersonne, date_debut, date_fin):
        DB = GestionDB.DB()
        req = "SELECT IDcategorie FROM presences WHERE (IDpersonne=%d AND '%s'<=date AND date<='%s') GROUP BY IDcategorie ORDER BY IDcategorie;" % (IDpersonne, date_debut, date_fin)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : return []
        listeCategoriesUtilisees = []
        for IDcategorie, in listeDonnees :
            listeCategoriesUtilisees.append(IDcategorie)
        return listeCategoriesUtilisees


class GetDictColonnes():
    def __init__(self, IDscenario, IDpersonne, detail_mois, date_debut, date_fin, toutes_categories) :
        self.IDscenario = IDscenario
        self.IDpersonne = IDpersonne
        self.detail_mois = detail_mois
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.toutes_categories = toutes_categories
        
        # Importation des catégories prévues
        if self.IDscenario != None : self.listeCategoriesPrevues = self.GetCategoriesPrevues()
        else: self.listeCategoriesPrevues = []
    
        # Inclure les catégories non scénarisées
        if IDpersonne != None : self.listeCategoriesUtilisees = self.GetCategoriesUtilisees()
        else: self.listeCategoriesUtilisees = []

        self.listeCategoriesNonPrevues = []
        if self.toutes_categories == True :
            self.listeCategories = []
            for IDcategorie in self.listeCategoriesPrevues :
                self.listeCategories.append(IDcategorie)
            for IDcategorie in self.listeCategoriesUtilisees :
                if IDcategorie not in self.listeCategories :
                    self.listeCategories.append(IDcategorie)
                    self.listeCategoriesNonPrevues.append(IDcategorie)
        else:
            self.listeCategories = self.listeCategoriesPrevues
        self.listeCategories.sort()
        
        # Crée labels des lignes
        self.listeLabelsLigne = self.GetListeLabelsLignes()

        # Récupération des données de chaque colonne
        self.dictColonnes = {}
        for IDcategorie in self.listeCategories :
            if IDcategorie in self.listeCategoriesPrevues :
                IDscenario = self.IDscenario
            else:
                IDscenario = None
            dictDonneesColonne = self.GetValeursColonne(self.IDscenario, IDcategorie, self.detail_mois, modeReport=True)
            self.dictColonnes[IDcategorie] = dictDonneesColonne
        # Ajout de la colonne TOTAL
        self.dictColonneTotal = self.GetColonneTotal(self.dictColonnes)


    def GetDictColonnes(self):
        return self.dictColonnes

    def GetDictColonneTotal(self):
        return self.dictColonneTotal
    
    def GetCategoriesPrevues(self):
        DB = GestionDB.DB()
        req = "SELECT IDscenario_cat, IDscenario, IDcategorie, prevision, report, date_debut_realise, date_fin_realise FROM scenarios_cat WHERE IDscenario=%d;" % self.IDscenario
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : return []
        listeID = []
        for valeurs in listeDonnees :
            listeID.append(valeurs[2])
        return listeID

    def GetCategoriesUtilisees(self):
        DB = GestionDB.DB()
        req = "SELECT IDcategorie FROM presences WHERE (IDpersonne=%d AND '%s'<=date AND date<='%s') GROUP BY IDcategorie ORDER BY IDcategorie;" % (self.IDpersonne, self.date_debut, self.date_fin)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : return []
        listeCategoriesUtilisees = []
        for IDcategorie, in listeDonnees :
            listeCategoriesUtilisees.append(IDcategorie)
        return listeCategoriesUtilisees

    def GetListeLabelsLignes(self):
        listeLignes = [
            
            { "type" : "groupe", "label" : _(u"Heures prévues"), "code" : "", "couleur_fond_label" : "#C0C0C0", "couleur_police_label" : "#FFFFFF", "couleur_fond_case" : "#C0C0C0"},
            { "type" : "ligne", "label" : _(u"Prévisions"), "code" : "prevision", "couleur_fond_label" : "#FFFFFF", "couleur_police_label" : "#000000", "couleur_fond_case" : "#ECE9D8"},
            { "type" : "ligne", "label" : _(u"Report"), "code" : "report", "couleur_fond_label" : "#FFFFFF", "couleur_police_label" : "#000000", "couleur_fond_case" : "#ECE9D8"},
            { "type" : "ligne", "label" : _(u"Total"), "code" : "total_heures_prevues", "couleur_fond_label" : "#FFFFFF", "couleur_police_label" : "#000000", "couleur_fond_case" : "#FFFFFF"},
            
            { "type" : "groupe", "label" : _(u"Heures réalisées"), "code" : "", "couleur_fond_label" : "#C0C0C0", "couleur_police_label" : "#FFFFFF", "couleur_fond_case" : "#C0C0C0"},
            { "type" : "ligne", "label" : _(u"Périodes de référence"), "code" : "periode_realise", "couleur_fond_label" : "#FFFFFF", "couleur_police_label" : "#000000", "couleur_fond_case" : "#ECE9D8"},
            { "type" : "ligne", "label" : _(u"Total"), "code" : "total_heures_realisees", "couleur_fond_label" : "#FFFFFF", "couleur_police_label" : "#000000", "couleur_fond_case" : "#FFFFFF"},
            
            { "type" : "groupe", "label" : _(u"Reste heures à réaliser"), "code" : "", "couleur_fond_label" : "#C0C0C0", "couleur_police_label" : "#FFFFFF", "couleur_fond_case" : "#C0C0C0"},
            { "type" : "ligne", "label" : _(u"Total"), "code" : "total_reste_heures", "couleur_fond_label" : "#FFFFFF", "couleur_police_label" : "#000000", "couleur_fond_case" : "#FFFFFF"},
        
        ]
        return listeLignes

    def GetValeursColonne(self, IDscenario, IDcategorie, detail_mois, modeReport=False) :
        dictDonnees = {}
        # Récupération des données scénarisées
        if self.IDscenario != None :
            # Si c'est pour un report, on cherche dans la base de données directement
            if modeReport == True or modeReport == False :
                # Si c'est une catégorie prévue
                DB = GestionDB.DB()
                req = "SELECT IDscenario_cat, IDscenario, IDcategorie, prevision, report, date_debut_realise, date_fin_realise FROM scenarios_cat WHERE IDscenario=%d AND IDcategorie=%d;" % (IDscenario, IDcategorie)
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                if len(listeDonnees) == 0 : 
                    dictDonnees["IDscenario_cat"] = None
                    dictDonnees["IDcategorie"] = IDcategorie
                    dictDonnees["prevision"] = None
                    dictDonnees["report"] = None
                    dictDonnees["date_debut_realise"] = str(self.date_debut)
                    dictDonnees["date_fin_realise"] = str(self.date_fin) 
                     
                # Importation des données de base de la colonne
                for IDscenario_cat, IDscenario, IDcategorie, prevision, report, date_debut_realise, date_fin_realise in listeDonnees :
                    dictDonnees["IDscenario_cat"] = IDscenario_cat
                    dictDonnees["IDcategorie"] = IDcategorie
                    dictDonnees["prevision"] = prevision
                    dictDonnees["report"] = report
                    if date_debut_realise == "" : date_debut_realise = None
                    dictDonnees["date_debut_realise"] = date_debut_realise
                    if date_fin_realise == "" : date_fin_realise = None
                    dictDonnees["date_fin_realise"] = date_fin_realise
            
            else:
                
                # Lecture de la VirtualDB
                if IDcategorie in self.dictVirtualDB :
                    dictDonnees["IDscenario_cat"] = self.dictVirtualDB[IDcategorie]["IDscenario_cat"]
                    dictDonnees["IDcategorie"] = IDcategorie
                    dictDonnees["prevision"] = self.dictVirtualDB[IDcategorie]["prevision"]
                    dictDonnees["report"] = self.dictVirtualDB[IDcategorie]["report"]
                    date_debut_realise = self.dictVirtualDB[IDcategorie]["date_debut_realise"]
                    if date_debut_realise == "" : date_debut_realise = None
                    dictDonnees["date_debut_realise"] = date_debut_realise
                    date_fin_realise = self.dictVirtualDB[IDcategorie]["date_fin_realise"]
                    if date_fin_realise == "" : date_fin_realise = None
                    dictDonnees["date_fin_realise"] = date_fin_realise
            
        else:
            # Si c'est une catégorie NON prévue
            dictDonnees["IDscenario_cat"] = None
            dictDonnees["IDcategorie"] = IDcategorie
            dictDonnees["prevision"] = None
            dictDonnees["report"] = None
            dictDonnees["date_debut_realise"] = str(self.date_debut)
            dictDonnees["date_fin_realise"] = str(self.date_fin)      
        
            
        # Calcul du total des heures prévues
        prevision = dictDonnees["prevision"]
        report = dictDonnees["report"]
        heures_report = "+00:00"
        if report != None :
            if report[0] == "M" :
                heures_report = report[1:]
            if report[0] == "A" :
                report_IDscenario, report_IDcategorie = report[1:].split(";")
                heures_report, nomScenario, descriptionScenario = self.GetReportColonne(int(report_IDcategorie), self.IDpersonne, int(report_IDscenario))
                dictDonnees["report"] = "%s;%s;%s;%s" % (report, heures_report, nomScenario, descriptionScenario)
        total_heures_prevues = self.OperationHeures(prevision, heures_report, "addition")
        dictDonnees["total_heures_prevues"] = total_heures_prevues
        
        # Formatage da la période du réalisé
        dictDonnees["periode_realise"] = "%s;%s" % (dictDonnees["date_debut_realise"], dictDonnees["date_fin_realise"])
        
        # Récupération des heures réalisées
        date_debut_realise = dictDonnees["date_debut_realise"]
        date_fin_realise = dictDonnees["date_fin_realise"]
        IDcategorie = dictDonnees["IDcategorie"]

        dictHeuresRealisees, listeLabelsDetails = self.GetHeuresRealisees(self.IDpersonne, date_debut_realise, date_fin_realise, IDcategorie, detail_mois)
        # Total heures réalisées
        total_heures_realisees = dictHeuresRealisees["total_heures_realisees"]
        dictDonnees["total_heures_realisees"] = total_heures_realisees
        # Détail Jour ou Mois des heures réalisées :
        dictDonnees["listeLabelsDetails"] = listeLabelsDetails
        for label in listeLabelsDetails :
            dictDonnees[label] = dictHeuresRealisees[label]
        
        # total reste heures
        total_reste_heures = self.OperationHeures(total_heures_prevues, total_heures_realisees, "soustraction")
        dictDonnees["total_reste_heures"] = total_reste_heures
                
        return dictDonnees

    def GetColonneTotal(self, dictColonnes):
        listeLignesExceptions = ["date_debut_realise", "date_fin_realise", "IDscenario_cat", "periode_realise", "listeLabelsDetails", "IDcategorie"]
        dictTotauxLignes = {}
        for IDcategorie, dictDonneesColonne in dictColonnes.items() :
            for codeLigne, valeur in dictDonneesColonne.items() :
                if codeLigne not in listeLignesExceptions :
                    # Particularité de la ligne report
                    if codeLigne == "report" :
                        if valeur == None or valeur == "" : valeur = u"+00:00"
                        if valeur[0] == "M" :
                            valeur = valeur[1:]
                        if valeur[0] == "A" :
                            report_IDscenario, report_IDcategorie, report_heures, nomScenario, descriptionScenario = valeur.split(";")
                            valeur = report_heures
                    # Addition des colonnes
                    if codeLigne in dictTotauxLignes :
                        dictTotauxLignes[codeLigne] = self.OperationHeures(dictTotauxLignes[codeLigne], valeur, "addition")
                    else:
                        dictTotauxLignes[codeLigne] = valeur
                        
        return dictTotauxLignes

    def OperationHeures(self, heureA=None, heureB=None, operation="addition"):
        # Préparation heure A
        if heureA == None :
            totalMinutesA = 0
        else:
            signeA = heureA[0]
            hrA, mnA = heureA[1:].split(":")
            hrA, mnA = int(hrA), int(mnA)
            totalMinutesA = (hrA*60) + mnA
            if signeA == "-" : totalMinutesA = -totalMinutesA
        # Préparation heure B
        if heureB == None :
            totalMinutesB = 0
        else:
            signeB = heureB[0]
            hrB, mnB = heureB[1:].split(":")
            hrB, mnB = int(hrB), int(mnB)
            totalMinutesB = (hrB*60) + mnB
            if signeB == "-" : totalMinutesB = -totalMinutesB
        # Opération
        if operation == "addition" : totalMinutes = totalMinutesA + totalMinutesB
        if operation == "soustraction" : totalMinutes = totalMinutesA - totalMinutesB
        # Formatage du résultat
        if totalMinutes >= 0 :
            nbreHeures = totalMinutes/60
            nbreMinutes = totalMinutes-(nbreHeures*60)
        else:
            nbreHeures = -(-totalMinutes/60)
            nbreMinutes = -(totalMinutes-(nbreHeures*60))
        if len(str(nbreMinutes))==1 : nbreMinutes = str("0") + str(nbreMinutes)
        duree = str(nbreHeures) + ":" + str(nbreMinutes)
        if nbreHeures>=0 : duree = "+%s" % duree
        return duree
        
        
    def GetReportColonne(self, IDcategorie, IDpersonne, IDscenario) :
        """ Ici programmer la récupération du report d'une colonne """
        # Récupère le nbre d'heures pour le report
        dictDonneesColonne = self.GetValeursColonne(IDscenario, IDcategorie, detail_mois=0, modeReport=True)
        totalResteColonne = dictDonneesColonne["total_reste_heures"]
        # Récupère le nom du scénario
        DB = GestionDB.DB()
        req = "SELECT IDscenario, nom, description FROM scenarios WHERE IDscenario=%d" % IDscenario
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 :
            return "+00:00", _(u"Report supprimé"), u""
        listePresences = listeDonnees[0]
        nomScenario = listePresences[1]
        descriptionScenario = listePresences[2]
        return totalResteColonne, nomScenario, descriptionScenario


    def GetHeuresRealisees(self, IDpersonne=None, date_debut_periode=None, date_fin_periode=None, IDcategorie=None, mode_detail=None):        
        DB = GestionDB.DB()
        if date_debut_periode != None and date_fin_periode != None : req = "SELECT IDpresence, date, heure_debut, heure_fin FROM presences WHERE (IDpersonne=%d AND IDcategorie=%d AND '%s'<=date AND date<='%s') ORDER BY date;" % (IDpersonne, IDcategorie, date_debut_periode, date_fin_periode)
        if date_debut_periode != None and date_fin_periode == None : req = "SELECT IDpresence, date, heure_debut, heure_fin FROM presences WHERE (IDpersonne=%d AND IDcategorie=%d AND '%s'<=date) ORDER BY date;" % (IDpersonne, IDcategorie, date_debut_periode)
        if date_debut_periode == None and date_fin_periode != None : req = "SELECT IDpresence, date, heure_debut, heure_fin FROM presences WHERE (IDpersonne=%d AND IDcategorie=%d AND '%s'>=date) ORDER BY date;" % (IDpersonne, IDcategorie, date_fin_periode)
        if date_debut_periode == None and date_fin_periode == None : req = "SELECT IDpresence, date, heure_debut, heure_fin FROM presences WHERE (IDpersonne=%d AND IDcategorie=%d) ORDER BY date;" % (IDpersonne, IDcategorie)
        DB.ExecuterReq(req)
        listePresences = DB.ResultatReq()
        if len(listePresences) == 0 : return {"total_heures_realisees" : "+00:00"}, []

        dictHeuresRealisees = {}
        total_heure_realisees = "+00:00"
        listeLabelsDetails = []
        
        for IDpresence, date, heure_debut, heure_fin in listePresences :
            dateDD = DateEngEnDateDD(date)
            # Addition pour le total de la catégorie
            duree = self.OperationHeures("+" + heure_fin, "+" + heure_debut, "soustraction")
            total_heure_realisees = self.OperationHeures(total_heure_realisees, duree, "addition")
            dictHeuresRealisees["total_heures_realisees"] = total_heure_realisees
            # Détail
            if mode_detail == 1 :
                codeMois = "%s-%s" % (dateDD.year, dateDD.month)
                if codeMois in dictHeuresRealisees :
                    dictHeuresRealisees[codeMois] = self.OperationHeures(dictHeuresRealisees[codeMois], duree, "addition")
                else:
                    dictHeuresRealisees[codeMois] = duree
                if codeMois not in listeLabelsDetails : listeLabelsDetails.append(codeMois)
            if mode_detail == 2 :
                codeJour = str(dateDD)
                if codeJour in dictHeuresRealisees :
                    dictHeuresRealisees[codeJour] = self.OperationHeures(dictHeuresRealisees[codeJour], duree, "addition")
                else:
                    dictHeuresRealisees[codeJour] = duree
                if codeJour not in listeLabelsDetails : listeLabelsDetails.append(codeJour)

        return dictHeuresRealisees, listeLabelsDetails


    def GetVirtualDB(self, IDscenario=None):
        """ Mémorise la table scenarios_cat pour permettre l'annulation après modifications """
        dictVirtualDB = {}
        if IDscenario != None :
            DB = GestionDB.DB()
            req = "SELECT IDscenario_cat, IDscenario, IDcategorie, prevision, report, date_debut_realise, date_fin_realise FROM scenarios_cat WHERE IDscenario=%d;" % IDscenario
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) == 0 : return dictVirtualDB
            # Importation des données de base de la colonne
            for IDscenario_cat, IDscenario, IDcategorie, prevision, report, date_debut_realise, date_fin_realise in listeDonnees :
                dictDonnees = {}
                dictDonnees["IDscenario_cat"] = IDscenario_cat
                dictDonnees["IDscenario"] = IDscenario
                dictDonnees["prevision"] = prevision
                dictDonnees["report"] = report
                if date_debut_realise == "" : date_debut_realise = None
                dictDonnees["date_debut_realise"] = date_debut_realise
                if date_fin_realise == "" : date_fin_realise = None
                dictDonnees["date_fin_realise"] = date_fin_realise
                dictDonnees["etat"] = "initial" # initial, modif, suppr, ajout
                dictVirtualDB[IDcategorie] = dictDonnees
        else:
            # S'il s'agit d'une création de scénarios
            pass
        return dictVirtualDB






class PanelLegende(scrolled.ScrolledPanel):
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent, -1)
        self.listeControles = []
        self.listeControlesDefaut = [
            ( ("couleur", (240, 240, 238)), ("texte", _(u"Cases modifiables avec un double-clic de la souris")), u""),
            ] # symbole, legende, infobulle
        
        self.MAJ()
        
    def MAJ(self, listeControlesSupp = []):
        self.DestroyChildren()
        self.listeControles = []
        grid_sizer = wx.FlexGridSizer(rows=20, cols=2, vgap=5, hgap=5)
        
        if len(listeControlesSupp) > 0 :
            self.listeControles.extend(self.listeControlesDefaut)
            self.listeControles.extend(listeControlesSupp)
        else:
            self.listeControles.extend(self.listeControlesDefaut)

        index = 0
        for symbole, legende, infobulle in self.listeControles :
            # Symbole
            if symbole[0] == "texte" : controle1 = wx.StaticText(self, -1, symbole[1])
            if symbole[0] == "couleur" : controle1 = wx.StaticBitmap(self, -1, self.CreationImage(symbole[1]))
            # Légende
            if legende[0] == "texte" : controle2 = wx.StaticText(self, index, legende[1])
            if legende[0] == "lien" : controle2 = self.Build_Hyperlink(index, legende[1], infobulle)
            grid_sizer.Add(controle1, 0, wx.ALIGN_CENTRE|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
            grid_sizer.Add(controle2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
            # Infobulle
            controle1.SetToolTip(wx.ToolTip(infobulle))
            controle2.SetToolTip(wx.ToolTip(infobulle))
            index += 1
        
        self.SetSizer(grid_sizer)
        self.SetAutoLayout(1)
        self.SetupScrolling()
        
    def CreationImage(self, couleur):
        """ Création des images pour le TreeCtrl """
        l, h = (8, 8)
        r, v, b = couleur
        if 'phoenix' in wx.PlatformInfo:
            bmp = wx.Image(l, h, True)
            bmp.SetRGB((0, 0, l, h), 0, 0, 0)
            bmp.SetRGB((1, 1, l-2, h-2), r, v, b)
        else:
            bmp = wx.EmptyImage(l, h, True)
            bmp.SetRGBRect((0, 0, l, h), 0, 0, 0)
            bmp.SetRGBRect((1, 1, l-2, h-2), r, v, b)
        return bmp.ConvertToBitmap()
        
    def Build_Hyperlink(self, id=-1, label="", infobulle="") :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(8, wx.NORMAL, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self, id, label, URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLACK", "BLACK", "RED")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(infobulle))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink(self, event):
        """ Ouvre le scénario du report """
        index = event.GetId()
        IDscenario = int(self.listeControles[index][1][2][1:])
        IDcategorie = int(self.listeControles[index][1][3])
        # Ouvre le scénario
        frm = MyFrame(self, IDscenario)
        frm.Show()





if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, IDscenario=32, IDpersonne=None)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
