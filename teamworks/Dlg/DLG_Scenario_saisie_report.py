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
import FonctionsPerso
import GestionDB
import datetime
from ObjectListView import ObjectListView, ColumnDefn
if 'phoenix' in wx.PlatformInfo:
    from wx.adv import BitmapComboBox
else :
    from wx.combo import BitmapComboBox
from Utils import UTILS_Adaptations
DLG_Scenario = UTILS_Adaptations.Import("Dlg.DLG_Scenario")

class MyDialog(wx.Dialog):
    """ Saisie d'une prévision pour un scénario """
    def __init__(self, parent, IDscenario=None, IDpersonne=0, IDcategorie=0, report=None, mode_heure=0):
        wx.Dialog.__init__(self, parent, id=-1, title=_(u"Saisie d'un report"), size=(440, 420), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.IDscenario = IDscenario
        self.IDpersonne = IDpersonne
        self.report = report
        self.mode_heure = mode_heure
        self.typeReport = "M"
        self.IDcategorie = IDcategorie

        # Label
        self.label_intro = wx.StaticText(self, -1, _(u"Saisissez un report :"))
        
        self.staticbox_periode = wx.StaticBox(self, -1, u"")
        
        # Manuel
        self.radio_1 = wx.RadioButton(self, -1, _(u"Manuel"), style = wx.RB_GROUP )
                
        # Type
        self.label_type = wx.StaticText(self, -1, _(u"Type :"))
        self.ctrl_type = wx.Choice(self, -1, choices = [_(u"Heures à réaliser (+)"), _(u"Heures déjà réalisées (-)")])
        self.ctrl_type.SetSelection(0)
        
        # Temps
        self.label_temps = wx.StaticText(self, -1, _(u"Temps :"))
        self.ctrl_temps_heures = wx.TextCtrl(self, -1, u"0", size=(50, -1), style=wx.TE_RIGHT)
        self.label_temps_signe = wx.StaticText(self, -1, u"h")
        self.ctrl_temps_minutes = wx.TextCtrl(self, -1, u"00", size=(30, -1))
        
        # Mode Heure/décimal
        self.label_mode = wx.StaticText(self, -1, _(u"Mode :"))
        self.ctrl_modeHeure = wx.Choice(self, -1, choices = [_(u"Heure"), _(u"Décimal")])
        self.ctrl_modeHeure.SetSelection(self.mode_heure)
        
        # Automatique
        self.radio_2 = wx.RadioButton(self, -1, _(u"Automatique"))
        
        # ListView Scenarios
        self.label_scenario = wx.StaticText(self, -1, _(u"Scénario :"))
        self.listview_scenarios = ListView(self, -1, IDscenario=self.IDscenario, IDpersonne=self.IDpersonne, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_apercu.Enable(False)
        self.listview_scenarios.SetMinSize((50, 50))
        
        # Choix catégorie
        self.label_categorie = wx.StaticText(self, -1, _(u"Catégorie :"))
        self.ctrl_categorie = BitmapComboBox(self, style=wx.CB_READONLY)
        self.InitCombo(IDscenario=None)
        
        # Boutons
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CHOICE, self.OnChoiceModeHeure, self.ctrl_modeHeure)
        self.ctrl_temps_heures.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusHeures)
        self.ctrl_temps_minutes.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocusMinutes)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton, self.radio_1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton, self.radio_2)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)

        if self.report != None and report[0] == "M" :
            self.SetReport(self.report)
            self.typeReport = "M"
            self.OnRadioButton(None)
        
        if self.report != None and report[0] == "A" :
            self.radio_2.SetValue(1)
            self.typeReport = "A"
            self.OnRadioButton(None)
            IDscenario, IDcategorie = self.report[1:].split(";")
            IDscenario, IDcategorie = int(IDscenario), int(IDcategorie)
            self.listview_scenarios.MAJ(IDscenario)
            self.InitCombo(IDscenario=IDscenario, IDcategorieSelection=IDcategorie)
        
        if self.report == None :
            self.radio_1.SetValue(1)
            self.OnRadioButton(None)
            
        if self.mode_heure == 1 :
            self.ConvertModeHeure(self.ctrl_temps_minutes.GetValue(), 1)
            self.ctrl_modeHeure.SetSelection(1)
            self.ctrl_temps_minutes.SetToolTip(wx.ToolTip(_(u"Saisissez un nombre de minutes au format décimal (entre 0 et 99)")))
        
        if self.IDpersonne == None :
            self.radio_2.Enable(False)

    def __set_properties(self):
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.ctrl_temps_heures.SetToolTip(wx.ToolTip(_(u"Saisissez un nombre d'heures")))
        self.ctrl_temps_minutes.SetToolTip(wx.ToolTip(_(u"Saisissez un nombre de minutes (entre 0 et 59)")))
        self.SetMinSize((510, 460))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 0, wx.TOP|wx.RIGHT|wx.LEFT, 10)

        sizerStaticBox = wx.StaticBoxSizer(self.staticbox_periode, wx.HORIZONTAL)
        
        grid_sizer_box = wx.FlexGridSizer(rows=10, cols=3, vgap=0, hgap=0)
        
        # Manuel
        grid_sizer_box.Add(self.radio_1, 0, wx.ALL, 5)
        grid_sizer_box.Add( (5, 5), 0, wx.ALL, 5)
        grid_sizer_box.Add( (0, 0), 0, wx.ALL, 0)
        
        grid_sizer_box.Add(self.label_type, 0, wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_box.Add(self.ctrl_type, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_box.Add( (0, 0), 0, wx.ALL, 0)
        
        grid_sizer_box.Add(self.label_temps, 0, wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        grid_sizer_1 = wx.FlexGridSizer(rows=1, cols=6, vgap=0, hgap=0)
        grid_sizer_1.Add(self.ctrl_temps_heures, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_1.Add(self.label_temps_signe, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_1.Add(self.ctrl_temps_minutes, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_1.Add( (10, 5), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_1.Add(self.label_mode, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_1.Add(self.ctrl_modeHeure, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_box.Add(grid_sizer_1, 0, wx.ALL, 0)
        
        grid_sizer_box.Add( (5, 5), 0, wx.ALL, 5)
        grid_sizer_box.Add( (5, 5), 0, wx.ALL, 5)
        grid_sizer_box.Add( (5, 5), 0, wx.ALL, 5)
        grid_sizer_box.Add( (5, 5), 0, wx.ALL, 5)
        
        # Automatique
        grid_sizer_box.Add(self.radio_2, 0, wx.ALL, 0)
        grid_sizer_box.Add( (5, 5), 0, wx.ALL, 10)
        grid_sizer_box.Add( (0, 0), 0, wx.ALL, 0)
        
        grid_sizer_box.Add(self.label_scenario, 0, wx.ALIGN_RIGHT|wx.ALL, 5)
        grid_sizer_box.Add(self.listview_scenarios, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_box.Add(self.bouton_apercu, 1, wx.TOP, 5)
        
        grid_sizer_box.Add(self.label_categorie, 0, wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_box.Add(self.ctrl_categorie, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_box.Add( (0, 0), 0, wx.ALL, 0)
        
        grid_sizer_box.AddGrowableCol(1)
        grid_sizer_box.AddGrowableRow(5)
        
        sizerStaticBox.Add(grid_sizer_box, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(sizerStaticBox, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        self.Layout()
        self.CenterOnScreen()
    
    def OnBoutonApercu(self, event):
        IDscenario = self.listview_scenarios.GetSelection()
        if IDscenario == None : return
        dlg = DLG_Scenario.Dialog(self, IDscenario)
        dlg.ShowModal()
        dlg.Destroy()
        
    def FormateCouleur(self, texte):
        pos1 = texte.index(",")
        pos2 = texte.index(",", pos1+1)
        r = int(texte[1:pos1])
        v = int(texte[pos1+2:pos2])
        b = int(texte[pos2+2:-1])
        return (r, v, b)

    def CreationImage(self, tailleImages, r, v, b):
        """ Création des images pour le TreeCtrl """
        if 'phoenix' in wx.PlatformInfo:
            bmp = wx.Image(tailleImages[0], tailleImages[1], True)
            bmp.SetRGB((0, 0, 16, 16), r, v, b)
        else:
            bmp = wx.EmptyImage(tailleImages[0], tailleImages[1], True)
            bmp.SetRGBRect((0, 0, 16, 16), r, v, b)
        return bmp.ConvertToBitmap()
    
    def InitCombo(self, IDscenario=None, IDcategorieSelection=None):
        # Get catégories
        DB = GestionDB.DB()
        req = "SELECT IDcategorie, nom_categorie, IDcat_parent, ordre, couleur FROM cat_presences ORDER BY IDcategorie"
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        DB.Close()
        dictCategories = {}
        for valeurs in listeCategories :
            dictCategories[valeurs[0]] = valeurs
        
        if IDscenario != None :
            dictColonnes, dictColonneTotal = self.GetDictColonnes(IDscenario)
            if len(dictColonnes) == 0 and len(dictColonneTotal) == 0 :
                return
            
        # Catégories prévues dans le scénario
        if IDscenario != None : listeCategoriesPrevues = self.GetCategoriesPrevues(IDscenario)
        else: listeCategoriesPrevues = []

        # Catégories utilisées dans le scénario
        if IDscenario != None : 
            listeCategoriesUtilisees = []
            listeCategoriesUtiliseesTmp = self.GetCategoriesUtilisees(IDscenario)
            for ID in listeCategoriesUtiliseesTmp :
                if ID not in listeCategoriesPrevues :
                    listeCategoriesUtilisees.append(ID)
        else: listeCategoriesUtilisees = []
        
        # Autres catégories
        listeAutresCategories = []
        for valeurs in listeCategories :
            ID = valeurs[0]
            if ID not in listeCategoriesPrevues and ID not in listeCategoriesUtilisees :
                listeAutresCategories.append(ID)
        listeAutresCategories.sort()
        
        # Liste de groupes de catégories
        listeGroupes = [ 
            (10000, _(u"Catégories scénarisées"), listeCategoriesPrevues),
            (10001, _(u"Catégories utilisées"), listeCategoriesUtilisees),
            (10002, _(u"Autres catégories"), listeAutresCategories),
            ]
        
        # Images pour le bitmapComboBox
        tailleImages = (16, 16)
        self.ctrl_categorie.Clear()
        index = 0
        for IDgroupe, nomGroupe, listeCatGroupe in listeGroupes :
            bmp = self.CreationImage( tailleImages, 255, 255, 255)
            self.ctrl_categorie.Append("----------- %s (%d) -----------" % (nomGroupe, len(listeCatGroupe)), bmp, IDgroupe)
            index += 1
            
            for IDcategorie in listeCatGroupe :
                if IDcategorie == 999 :
                    IDcategorie, nom_categorie, IDcat_parent, ordre, couleur = 999, _(u"Sans catégorie"), 0, 0, "(255, 255, 255)"
                elif IDcategorie == 1000 :
                    IDcategorie, nom_categorie, IDcat_parent, ordre, couleur = 1000, _(u"Total"), 0, 0, "(255, 255, 255)"
                else:
                    IDcategorie, nom_categorie, IDcat_parent, ordre, couleur = dictCategories[IDcategorie]
                couleur = self.FormateCouleur(couleur)
                r, v, b = couleur
                bmp = self.CreationImage( tailleImages, r, v, b)
                # Ajout du nbre d'heures :
                if IDscenario != None :
                    if IDcategorie in dictColonnes :
                        nom_categorie = u"%s (%s)" % (nom_categorie, self.FormateHeure(dictColonnes[IDcategorie]["total_reste_heures"]))
                    if IDcategorie == 1000 :
                        nom_categorie = u"%s (%s)" % (nom_categorie, self.FormateHeure(dictColonneTotal["total_reste_heures"]))
                self.ctrl_categorie.Append(nom_categorie, bmp, IDcategorie)
                if IDcategorieSelection == None :
                    IDcategorieSelection = self.IDcategorie
                if IDcategorie == IDcategorieSelection :
                    self.ctrl_categorie.SetSelection(index)
                index += 1
    
    def FormateHeure(self, label):
        if label == None or label == "" : return ""
        signe = label[0]
        hr, mn = label[1:].split(":")
        if signe == "+" : 
            signe = ""
        else:
            signe = "- "
        if self.mode_heure == 0 :
            # Mode Heure
            texte = _(u"%s%sh%s") % (signe, hr, mn)
        else:
            # Mode décimal
            minDecimal = int(mn)*100//60
            texte = u"%s%s.%s" % (signe, hr, minDecimal)
        return texte
    
    def GetDictColonnes(self, IDscenario):
        DB = GestionDB.DB()
        req = "SELECT IDscenario, IDpersonne, date_debut, date_fin, toutes_categories FROM scenarios WHERE IDscenario=%d;" % IDscenario
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : return [], []
        
        IDpersonne = listeDonnees[0][1]
        date_debut = listeDonnees[0][2]
        date_fin = listeDonnees[0][3]
        detail_mois = 0
        toutes_categories = listeDonnees[0][4]
        
        # GetValeursColonnes
        valeurs = DLG_Scenario.GetDictColonnes(IDscenario, IDpersonne, detail_mois, date_debut, date_fin, toutes_categories)
        dictColonnes = valeurs.GetDictColonnes()
        dictColonneTotal = valeurs.GetDictColonneTotal()
        return dictColonnes, dictColonneTotal
            
    def GetCategoriesPrevues(self, IDscenario):
        DB = GestionDB.DB()
        req = "SELECT IDscenario_cat, IDscenario, IDcategorie, prevision, report, date_debut_realise, date_fin_realise FROM scenarios_cat WHERE IDscenario=%d;" % IDscenario
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeCategories = []
        for valeurs in listeDonnees :
            IDcategorie = valeurs[2]
            listeCategories.append(IDcategorie)
        listeCategories.append(1000) # Colonne total
        listeCategories.sort()
        return listeCategories

    def GetCategoriesUtilisees(self, IDscenario):
        DB = GestionDB.DB()
        req = "SELECT IDscenario, IDpersonne, date_debut, date_fin FROM scenarios WHERE IDscenario=%d;" % IDscenario
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : return []
        
        IDpersonne = listeDonnees[0][1]
        date_debut = listeDonnees[0][2]
        date_fin = listeDonnees[0][3]

        DB = GestionDB.DB()
        req = "SELECT IDcategorie FROM presences WHERE (IDpersonne=%d AND '%s'<=date AND date<='%s') GROUP BY IDcategorie ORDER BY IDcategorie;" % (IDpersonne, date_debut, date_fin)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : return []
        listeCategoriesUtilisees = []
        for IDcategorie, in listeDonnees :
            listeCategoriesUtilisees.append(IDcategorie)
        return listeCategoriesUtilisees
                                    
                                    
    def OnRadioButton(self, event):
        if self.radio_1.GetValue() == True :
            etat_radio_1 = True
            etat_radio_2 = False
        else:
            etat_radio_1 = False
            etat_radio_2 = True
        # Manuel
        self.typeReport = "M"
        self.label_type.Enable(etat_radio_1)
        self.ctrl_type.Enable(etat_radio_1)
        self.label_temps.Enable(etat_radio_1)
        self.ctrl_temps_heures.Enable(etat_radio_1)
        self.label_temps_signe.Enable(etat_radio_1)
        self.ctrl_temps_minutes.Enable(etat_radio_1)
        self.label_mode.Enable(etat_radio_1)
        self.ctrl_modeHeure.Enable(etat_radio_1)
        
        # Automatique
        self.typeReport = "A"
        self.label_scenario.Enable(etat_radio_2)
        self.listview_scenarios.Enable(etat_radio_2)
        self.label_categorie.Enable(etat_radio_2)
        self.ctrl_categorie.Enable(etat_radio_2)
        
        if etat_radio_2 == True and self.listview_scenarios.GetSelection() == None :
            self.ctrl_categorie.Enable(False)
            self.bouton_apercu.Enable(False)

        
    def OnKillFocusHeures(self, event):
        heures = self.ctrl_temps_heures.GetValue()
        erreur = False
        try:
            heures = int(heures)
        except :
            erreur = True
        
        if heures < 0 :
            erreur = True
        
        if erreur == True :
            self.ctrl_temps_heures.SetValue("0")
##            dlg = wx.MessageDialog(self, _(u"Le nombre d'heures semble inexact. Veuillez vérifier votre saisie."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
##            dlg.ShowModal()
##            dlg.Destroy()
##            self.ctrl_temps_heures.SetFocus()
##            return
            

    def OnKillFocusMinutes(self, event):
        minutes = self.ctrl_temps_minutes.GetValue()
        erreur = False
        try:
            minutes = int(minutes)
        except :
            erreur = True
                
        if self.mode_heure == 0 :
            if minutes < 0 or minutes > 59 :
                erreur = True
        
        if self.mode_heure == 1 :
            if minutes < 0 or minutes > 99 :
                erreur = True
        
        if erreur == True :
            self.ctrl_temps_minutes.SetValue("00")
            minutes = 0
##            dlg = wx.MessageDialog(self, _(u"Le nombre de minutes semble inexact. Veuillez vérifier votre saisie."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
##            dlg.ShowModal()
##            dlg.Destroy()
##            self.ctrl_temps_minutes.SetFocus()
##            return
        
        if self.mode_heure == 0 :
            self.ctrl_temps_minutes.SetValue( "%02d" % minutes)


    def SetReport(self, report):
        """ Renvoie la prévision """
        if report[1] == "+" :
            self.ctrl_type.SetSelection(0)
        else:
            self.ctrl_type.SetSelection(1)
        heures, minutes = report[2:].split(":")
        self.ctrl_temps_heures.SetValue(str(heures))
        self.ctrl_temps_minutes.SetValue(str(minutes))
    
    def OnChoiceModeHeure(self, event):
        if self.ctrl_modeHeure.GetSelection() == self.mode_heure : return
        self.ConvertModeHeure(self.ctrl_temps_minutes.GetValue(), self.ctrl_modeHeure.GetSelection())
        
    def ConvertModeHeure(self, min="", mode=0):
        try :
            min = int(min)
        except :
            return
        if mode == 0 :
            resultat = min * 60 // 100
            self.label_temps_signe.SetLabel(u"h")
            self.ctrl_temps_minutes.SetValue( "%02d" % resultat)
            self.ctrl_temps_minutes.SetToolTip(wx.ToolTip(_(u"Saisissez un nombre de minutes (entre 0 et 59)")))
        if mode == 1 :
            resultat = min * 100 // 60
            self.label_temps_signe.SetLabel(u".")
            self.ctrl_temps_minutes.SetValue(str(resultat))
            self.ctrl_temps_minutes.SetToolTip(wx.ToolTip(_(u"Saisissez un nombre de minutes au format décimal (entre 0 et 99)")))
        self.mode_heure = mode

    def GetReport(self):
        """ Renvoie le report """
        if self.radio_1.GetValue() == True :
            # Mode manuel
            if self.ctrl_type.GetSelection() == 0 :
                signe = "+"
            else:
                signe = "-"
            heures = int(self.ctrl_temps_heures.GetValue())
            minutes = int(self.ctrl_temps_minutes.GetValue())
            if self.mode_heure == 1 : 
                minutes = minutes * 60 // 100
            report = _(u"M%s%02d:%02d") % (signe, heures, minutes)
            
        else:
            # Mode Auto
            IDscenario = self.listview_scenarios.GetSelection()
            indexCategorie = self.ctrl_categorie.GetSelection()
            IDCategorie = self.ctrl_categorie.GetClientData(indexCategorie)
            report = _(u"A%d;%d") % (IDscenario, IDCategorie)
        
        return report
    
    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        if self.radio_1.GetValue() == True :
            # Mode manuel
            pass
            
        else:
            # Mode Auto
            IDscenario = self.listview_scenarios.GetSelection()
            if IDscenario == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un scénario dans la liste proposée"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            
            index = self.ctrl_categorie.GetSelection()
            if index == -1 :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une catégorie dans la liste proposée"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            
            IDCategorie = self.ctrl_categorie.GetClientData(index)
            if IDCategorie >= 10000:
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une catégorie dans la liste proposée"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
        
        self.EndModal(wx.ID_OK)
        

# ---------------------------------------- COMBOTREEBOX ------------------------------------------------------------------------






# ---------------------------------------- LISTVIEW ENVOIS -----------------------------------------------------------------------

class Track(object):
    def __init__(self, donnees):
        self.IDscenario = donnees[0]
        self.nom = donnees[1]
        self.description = donnees[2]
        self.date_debut = donnees[3]
        self.date_fin = donnees[4]
        
        
    def FormateDate(self, dateStr):
            if dateStr == "" : return ""
            date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text
        


class ListView(ObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDscenario = kwds.pop("IDscenario", None)
        self.IDpersonne = kwds.pop("IDpersonne", None)
        selectionID = kwds.pop("selectionID", None)
        # Initialisation du listCtrl
        ObjectListView.__init__(self, *args, **kwds)
        self.selectionID = None
        self.selectionTrack = None
        self.desactiveMAJ = False
        self.InitModel()
        self.InitObjectListView()
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
##        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)
##        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelected)
        
##    def OnActivated(self,event):
##        self.GetGrandParent().OnModifierCotisation(None)

##    def OnSelected(self,event):
##        ID = self.Selection()[0].IDenvoi_cotisations
##        if self.desactiveMAJ == True : return
##        self.GetGrandParent().SelectEnvoi(ID)

    def OnItemSelected(self, event):
        IDscenario = self.GetSelection()
        self.GetParent().InitCombo(IDscenario)
        self.GetParent().ctrl_categorie.Enable(True)
        self.GetParent().bouton_apercu.Enable(True)

    def OnItemDeselected(self, event):
        self.GetParent().ctrl_categorie.Enable(False)
        self.GetParent().bouton_apercu.Enable(False)
        
    def InitModel(self):
        self.donnees = self.GetTracks()
                        
    def GetTracks(self):
        if self.IDpersonne == None : return []
        DB = GestionDB.DB()
        if self.IDscenario != None :
            req = "SELECT IDscenario, nom, description, date_debut, date_fin FROM scenarios WHERE IDpersonne=%d AND IDscenario!=%d ORDER BY date_debut;" % (self.IDpersonne, self.IDscenario)
        else:
            req = "SELECT IDscenario, nom, description, date_debut, date_fin FROM scenarios WHERE IDpersonne=%d ORDER BY date_debut;" % self.IDpersonne
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

    def GetCategories(self, IDscenario):
        DB = GestionDB.DB()        
        req = """
        SELECT IDscenario, nom, description, date_debut, date_fin
        FROM scenarios
        WHERE IDpersonne=%d
        ORDER BY date_debut
        ;""" % self.IDpersonne
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()

    def InitObjectListView(self):
                    
        def FormateDate(dateStr):
            if dateStr == "" : return ""
            date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text
                
        self.useAlternateBackColors = False
        
        # Paramètres ListView
        self.useExpansionColumn = True
        self.SetColumns([
            ColumnDefn(u"", "left", 0, ""),
            ColumnDefn(_(u"ID"), "center", 0, "IDscenario"),
            ColumnDefn(_(u"Nom"), "left", 80, "nom"),
            ColumnDefn(_(u"Description"), "left", 60, "description"),
            ColumnDefn(_(u"Date début"), "left", 70, "date_debut", stringConverter=FormateDate),
            ColumnDefn(_(u"Date fin"), "left", 90, "date_fin", stringConverter=FormateDate),
        ])
        self.SetSortColumn(self.columns[4])
        self.SetEmptyListMsg(_(u"Aucun scénario enregistré"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetObjects(self.donnees)
        self.useAlternateBackColors = False
        
   
    def MAJ(self, selectionID=None):
        if selectionID != None :
            self.selectionID = selectionID
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if self.selectionTrack != None :
            self.desactiveMAJ = True
            self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
            self.desactiveMAJ = False
        self.selectionID = None
        self.selectionTrack = None

 
    def GetSelection(self):
        if len(self.GetSelectedObjects()) != 0 :
            IDscenario = self.GetSelectedObjects()[0].IDscenario
        else:
            IDscenario = None
        return IDscenario






if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = MyDialog(None, IDpersonne=1, IDcategorie=2, report=None, mode_heure=0)
    frm.ShowModal()
    app.MainLoop()