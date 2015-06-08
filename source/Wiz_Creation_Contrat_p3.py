#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import GestionDB
import Config_Classifications
import Config_ValPoint
import Config_TypesContrats
import FonctionsPerso
import datetime


class Page(wx.Panel):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        
        self.dictTypes = {}
        
        self.sizer_dates_staticbox = wx.StaticBox(self, -1, "Dates du contrat")
        self.sizer_caract_staticbox = wx.StaticBox(self, -1, u"Caract�ristiques g�n�rales")
        self.sizer_essai_staticbox = wx.StaticBox(self, -1, u"P�riode d'essai")
        self.label_titre = wx.StaticText(self, -1, u"2. Caract�ristiques g�n�rales du contrat")
        self.label_intro = wx.StaticText(self, -1, u"Saisissez les caract�ristiques g�n�rales du contrat :")
        
        self.label_type = wx.StaticText(self, -1, "Type de contrat :")
        self.choice_type = wx.Choice(self, -1, choices=[])
        self.Importation_Type()
        self.bouton_type = wx.Button(self, -1, "...", style=wx.BU_EXACTFIT)
        
        self.label_class = wx.StaticText(self, -1, "Classification :")
        self.choice_class = wx.Choice(self, -1, choices=[])
        self.Importation_classifications()
        self.bouton_class = wx.Button(self, -1, "...", style=wx.BU_EXACTFIT)
        
        self.label_valpoint = wx.StaticText(self, -1, "Valeur du point :")
        self.choice_valpoint = wx.Choice(self, -1, choices=[])
        self.Importation_valPoint()
        self.bouton_valpoint = wx.Button(self, -1, "...", style=wx.BU_EXACTFIT)
        
        self.label_date_debut = wx.StaticText(self, -1, "       A partir du :")
        self.datepicker_date_debut = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN)
        self.label_date_fin = wx.StaticText(self, -1, "Jusqu'au :")
        self.datepicker_date_fin = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN)
        self.datepicker_date_debut.Enable(False)
        self.datepicker_date_fin.Enable(False)
        
        self.check_rupture = wx.CheckBox(self, -1, u" Rupture anticip�e du contrat au :")
        self.datepicker_rupture = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN)
        self.datepicker_rupture.Enable(False)
        
        self.label_essai = wx.StaticText(self, -1, u"    Nbre de jours :")
        self.periode_essai = wx.SpinCtrl(self, -1, "", size=(60, -1))
        self.periode_essai.SetRange(0,99)
        self.periode_essai.SetValue(0)
        self.aide_essai = wx.StaticText(self, -1, u"  (1 jour par semaine travaill�e)")
        self.aide_essai.SetForegroundColour('Grey')

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonClassifications, self.bouton_class)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonValPoint, self.bouton_valpoint)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonType, self.bouton_type)
        self.Bind(wx.EVT_CHOICE, self.OnChoiceType, self.choice_type)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckRupture, self.check_rupture)
        
        self.Affichage_dateFin()
        # Importation des donn�es
        if self.GetGrandParent().dictContrats["IDcontrat"] != 0 : self.Importation()

    def __set_properties(self):
        self.label_titre.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.bouton_type.SetMinSize((20, 20))
        self.bouton_type.SetToolTipString(u"Cliquez ici pour ajouter, modifier ou supprimer des types de contrat")
        self.bouton_class.SetMinSize((20, 20))
        self.bouton_class.SetToolTipString(u"Cliquez ici pour ajouter, modifier ou supprimer des classifications")
        self.bouton_valpoint.SetMinSize((20, 20))
        self.bouton_valpoint.SetToolTipString(u"Cliquez ici pour ajouter, modifier ou supprimer des valeurs de points")
        self.check_rupture.SetToolTipString(u"Cliquez ici pour saisir une date de fin de contrat si l'employeur ou le salari� ont mis fin pr�matur�ment au contrat.")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        sizer_dates = wx.StaticBoxSizer(self.sizer_dates_staticbox, wx.VERTICAL)
        grid_sizer_dates = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_rupture = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5) 
                
        sizer_caract = wx.StaticBoxSizer(self.sizer_caract_staticbox, wx.VERTICAL)
        grid_sizer_caract = wx.FlexGridSizer(rows=3, cols=3, vgap=5, hgap=5)
        grid_sizer_base.Add(self.label_titre, 0, 0, 0)
        grid_sizer_base.Add(self.label_intro, 0, wx.LEFT, 20)
        grid_sizer_caract.Add(self.label_type, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caract.Add(self.choice_type, 0, wx.EXPAND, 0)
        grid_sizer_caract.Add(self.bouton_type, 0, 0, 0)
        grid_sizer_caract.Add(self.label_class, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caract.Add(self.choice_class, 0, wx.EXPAND, 0)
        grid_sizer_caract.Add(self.bouton_class, 0, 0, 0)
        grid_sizer_caract.Add(self.label_valpoint, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caract.Add(self.choice_valpoint, 0, wx.EXPAND, 0)
        grid_sizer_caract.Add(self.bouton_valpoint, 0, 0, 0)
        grid_sizer_caract.AddGrowableCol(1)
        sizer_caract.Add(grid_sizer_caract, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(sizer_caract, 1, wx.LEFT|wx.EXPAND, 20)
        
        grid_sizer_dates.Add(self.label_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.datepicker_date_debut, 0, 0, 0)
        grid_sizer_dates.Add(self.label_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.datepicker_date_fin, 0, 0, 0)
        sizer_dates.Add(grid_sizer_dates, 1, wx.ALL|wx.EXPAND, 5)
        
        grid_sizer_rupture.Add((90, 10), 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_rupture.Add(self.check_rupture, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_rupture.Add(self.datepicker_rupture, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_dates.Add(grid_sizer_rupture, 1, wx.EXPAND, 0)
        
        grid_sizer_base.Add(sizer_dates, 1, wx.LEFT|wx.EXPAND, 20)
        
        sizer_essai = wx.StaticBoxSizer(self.sizer_essai_staticbox, wx.VERTICAL)
        grid_sizer_essai = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5) 
        grid_sizer_essai.Add(self.label_essai, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_essai.Add(self.periode_essai, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_essai.Add(self.aide_essai, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_essai.Add(grid_sizer_essai, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(sizer_essai, 1, wx.LEFT|wx.EXPAND, 20)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        
    
    def Importation(self):
        """ Remplit les controles avec les donn�es import�es si c'est une modification """
        dictContrats = self.GetGrandParent().dictContrats
        
        # Controles Choice
        type = dictContrats["IDtype"]
        self.SelectChoice(self.choice_type, data=type )
        classification = dictContrats["IDclassification"]
        self.SelectChoice(self.choice_class, data=classification )
        valeur_point = dictContrats["valeur_point"]
        self.SelectChoice(self.choice_valpoint, data=valeur_point )
        
        # Radio et Date de Rupture
        if dictContrats["date_rupture"] != "" :
            self.check_rupture.SetValue(True)
            self.datepicker_rupture.Enable(True)
            self.SetDatePicker(self.datepicker_rupture, dictContrats["date_rupture"])
        else:
            self.check_rupture.SetValue(False)
            self.datepicker_rupture.Enable(False)
        
        # Dates de d�but et de fin
        date_debut = dictContrats["date_debut"]
        date_fin = dictContrats["date_fin"]
        if date_debut != "" : self.SetDatePicker(self.datepicker_date_debut, dictContrats["date_debut"])
        if date_fin != "" and date_fin != "2999-01-01" : self.SetDatePicker(self.datepicker_date_fin, dictContrats["date_fin"])
        self.datepicker_date_debut.Enable(True)
        self.datepicker_date_fin.Enable(True)
        
        if self.dictTypes[type] == "non" :
            self.label_date_fin.Show(True)
            self.datepicker_date_fin.Show(True)
        else:
            self.label_date_fin.Show(False)
            self.datepicker_date_fin.Show(False)
            
        # P�riode d'essai
        essai = dictContrats["essai"]
        self.periode_essai.SetValue(essai)
        
    def CalcEssai(self):
        """ Calcule la dur�e de la p�riode d'essai en fonction des dates du contrat """
        essai = 0
        
        # Si CDI
        if self.dictTypes[self.choice_type.GetClientData(self.choice_type.GetSelection())] == "oui" :
            self.periode_essai.SetValue(30)
            return
            
        # Si CDD
        
        # Calcul de la dur�e du contrat
        date_tmp = self.datepicker_date_debut.GetValue()
        date_debut = datetime.date(date_tmp.GetYear(), date_tmp.GetMonth()+1, date_tmp.GetDay())
        date_tmp = self.datepicker_date_fin.GetValue()
        date_fin = datetime.date(date_tmp.GetYear(), date_tmp.GetMonth()+1, date_tmp.GetDay())
        
        if date_debut > date_fin :
            self.periode_essai.SetValue(0)
            return
        
        nbreJours = (date_fin - date_debut).days
        nbreSemaines = nbreJours / 7
        
        print nbreJours, nbreSemaines      
        
        
        self.periode_essai.SetValue(essai)


        
    def SetDatePicker(self, controle, date) :
        """ Met une date dans un datePicker donn� """
        annee = int(date[:4])
        mois = int(date[5:7])-1
        jour = int(date[8:10])
        date = wx.DateTime()
        date.Set(jour, mois, annee)
        controle.SetValue(date)    
        
        
    def OnCheckRupture(self, event):
        if self.check_rupture.GetValue() == True :
            self.datepicker_rupture.Enable(True)
        else:
            self.datepicker_rupture.Enable(False)
        
    def OnChoiceType(self, event):
        self.datepicker_date_debut.Enable(True)
        self.datepicker_date_fin.Enable(True)        
        self.Affichage_dateFin()
        self.CalcEssai()
        
    def Affichage_dateFin(self):
        """ Faire apparaitre ou disparaitre le controle DateFin en fonction du type de contrat choisi """
        selection = self.choice_type.GetSelection()
        if selection != -1 : 
            IDselection = self.choice_type.GetClientData(selection)
        else: return
        if self.dictTypes[IDselection] == "non" :
            self.label_date_fin.Show(True)
            self.datepicker_date_fin.Show(True)
        else:
            self.label_date_fin.Show(False)
            self.datepicker_date_fin.Show(False)
        
    def OnBoutonClassifications(self, event):
        frmClassification = Config_Classifications.MyFrame(self, "")
        frmClassification.Show()

    def OnBoutonValPoint(self, event):
        frmValPoint = Config_ValPoint.MyFrame(self, "")
        frmValPoint.Show()
        
    def OnBoutonType(self, event):
        frmTypes = Config_TypesContrats.MyFrame(self, "")
        frmTypes.Show()
        
    def MAJ_choice_Class(self):
        self.Importation_classifications()
        
    def Importation_classifications(self):
        controle = self.choice_class
        selection = controle.GetSelection()
        IDselection = None
        if selection != -1 : IDselection = controle.GetClientData(selection)
        # R�cup�ration des donn�es
        DB = GestionDB.DB()
        req = """SELECT * FROM contrats_class """
        DB.ExecuterReq(req)
        liste = DB.ResultatReq()
        DB.Close()
        # Placement de la liste dans le Choice
        controle.Clear()
        x = 0
        for key, valeur in liste :
            controle.Append(valeur, key) 
            if IDselection == key : controle.SetSelection(x)
            x += 1
            
    def MAJ_choice_ValPoint(self):
        self.Importation_valPoint()
            
    def Importation_valPoint(self):
        controle = self.choice_valpoint
        selection = controle.GetSelection()
        IDselection = None
        if selection != -1 : IDselection = controle.GetClientData(selection)
        # R�cup�ration des donn�es
        DB = GestionDB.DB()
        req = """SELECT * FROM valeurs_point ORDER BY date_debut """
        DB.ExecuterReq(req)
        liste = DB.ResultatReq()
        DB.Close()
       
        # Recherche de la valeur actuelle
        dateJour = str(datetime.date.today())
        valeurActuelle = None
        for ID, valeur, dateDebut in liste :
            if dateJour >= dateDebut :
                valeurActuelle = ID 
        
        # Placement de la liste dans le Choice            
        controle.Clear()
        x = 0
        for ID, valeur, dateDebut in liste :
            txt = str(valeur) + u" �  (� partir du " + FonctionsPerso.DateEngFr(dateDebut) + ")"
            controle.Append(txt, ID) 
            # S�lection de l'ancienne valeur s�lectionn�e
            if IDselection == ID : controle.SetSelection(x)
            # S�lection de la valeur actuelle si rien n'a �t� s�lectionn�e
            if IDselection == None and valeurActuelle == ID : controle.SetSelection(x)
            x += 1
        
        self.listeValPoint = liste
            
    def MAJ_choice_Type(self):
        self.Importation_Type()
        
    def Importation_Type(self):
        controle = self.choice_type
        selection = controle.GetSelection()
        IDselection = None
        if selection != -1 : IDselection = controle.GetClientData(selection)
        # R�cup�ration des donn�es
        DB = GestionDB.DB()
        req = """SELECT * FROM contrats_types """
        DB.ExecuterReq(req)
        liste = DB.ResultatReq()
        DB.Close()
        # Placement de la liste dans le Choice
        controle.Clear()
        self.dictTypes = {}
        x = 0
        for key, nom, nom_abrege, duree_indeterminee in liste :
            self.dictTypes[key] = duree_indeterminee
            controle.Append(nom, key) 
            if IDselection == key : controle.SetSelection(x)
            x += 1
            
        if selection != -1 : self.Affichage_dateFin()

    def GetDatePickerValue(self, controle):
        date_tmp = controle.GetValue()
        return str(datetime.date(date_tmp.GetYear(), date_tmp.GetMonth()+1, date_tmp.GetDay()))

    def GetChoiceData(self, controle):
        selection = controle.GetSelection()
        if selection != -1 : 
            IDselection = controle.GetClientData(selection)
        else:
            IDselection = None
        return IDselection

    def SelectChoice(self, controle, data):
        nbreItems = controle.GetCount()
        index = 0
        for item in range(nbreItems) :
            if controle.GetClientData(index) == data :
                controle.SetSelection(index)
                return
            index += 1
                        
    def Validation(self):
        
        # R�cup�ration des valeurs saisies
        type = self.GetChoiceData(self.choice_type)
        classification = self.GetChoiceData(self.choice_class)
        valPoint = self.GetChoiceData(self.choice_valpoint)    
        date_debut = self.GetDatePickerValue(self.datepicker_date_debut)
        date_fin = self.GetDatePickerValue(self.datepicker_date_fin)
        rupture = self.check_rupture.GetValue()
        date_rupture = self.GetDatePickerValue(self.datepicker_rupture)
        essai = self.periode_essai.GetValue()
        
        # V�rifie que des valeurs ont �t� saisies
        if type == None :
            dlg = wx.MessageDialog(self, u"Vous devez s�lectionner un type de contrat dans la liste propos�e.", "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.choice_type.SetFocus()
            return False

        if classification == None :
            dlg = wx.MessageDialog(self, u"Vous devez s�lectionner une classification dans la liste propos�e.", "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.choice_class.SetFocus()
            return False
        
        if valPoint == None :
            dlg = wx.MessageDialog(self, u"Vous devez s�lectionner une valeur de point dans la liste propos�e.", "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.choice_valpoint.SetFocus()
            return False
        
        # V�rifie que la date de fin est sup�rieure � la date de d�but de contrat
        if date_debut > date_fin and self.datepicker_date_fin.IsShown() :
            dlg = wx.MessageDialog(self, u"La date de fin de contrat que vous avez saisie est inf�rieure � la date de d�but !", "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.datepicker_date_fin.SetFocus()
            return False

        # V�rifie que la date de rupture est sup�rieure � la date de d�but de contrat
        if date_debut > date_rupture and rupture == True :
            dlg = wx.MessageDialog(self, u"La date de rupture de contrat que vous avez saisie est inf�rieure � la date de d�but !", "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.datepicker_date_fin.SetFocus()
            return False

        # V�rifie que la date de rupture est sup�rieure � la date de d�but de contrat et inf�rieure � la date de fin si contrat � dur�e d�termin�e :
        if self.datepicker_date_fin.IsShown() and date_rupture >= date_fin and rupture == True :
            dlg = wx.MessageDialog(self, u"La date de rupture de contrat que vous avez saisie est �gale ou sup�rieure � la date de fin de contrat !", "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.datepicker_date_fin.SetFocus()
            return False
        
        # V�rifie que la valeur du point correspondant bien � la date de d�but de contrat
        valeurNecessaire = None
        for ID, valeur, dateValeur in self.listeValPoint :
            if date_debut >= dateValeur :
                valeurNecessaire = ID
        
        if valeurNecessaire == None :
            dlg = wx.MessageDialog(self, u"La valeur du point n'est pas correcte. Il n'existe pas dans la liste propos�e de valeur correspondante � la date de d�but de contrat. \n\nVous devez donc cr�er une nouvelle valeur. \n\nSouhaitez-vous le faire maintenant ?", "Erreur", wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_NO :
                dlg.Destroy() 
                return False
            else:
                dlg.Destroy()
                self.OnBoutonValPoint(None)
                return False
         
        if valeurNecessaire != valPoint :
            dlg = wx.MessageDialog(self, u"La valeur du point ne correspond pas � la date de d�but du contrat. Vous devez s�lectionner une autre valeur de points dans la liste propos�e.\n\nVoulez-vous que je le fasse � votre place ?", "Erreur", wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_NO :
                dlg.Destroy() 
                return False
            else:
                dlg.Destroy()
                # S�lection automatique de la bonne valeur de point
                for index in range(self.choice_valpoint.GetCount()) :
                    if self.choice_valpoint.GetClientData(index) == valeurNecessaire :
                        self.choice_valpoint.SetSelection(index)
                        return False
        
        # P�riode d'essai
        if essai == "" :
            dlg = wx.MessageDialog(self, u"Vous devez saisir un nombre de jours pour p�riode d'essai.", "Erreur", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        if essai == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez pas d�fini de p�riode d'essai. \n\nSouhaitez-vous quand m�me continuer ? \n(Sinon cliquez 'non' ou 'annuler')", "Erreur de saisie", wx.ICON_QUESTION | wx.YES_NO | wx.CANCEL | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_YES :
                dlg.Destroy() 
            else:
                dlg.Destroy()
                return False
        
        # M�morisation des donn�es
        dictContrats = self.GetGrandParent().dictContrats
        dictContrats["IDtype"] = type
        dictContrats["IDclassification"] = classification
        dictContrats["valeur_point"] = valPoint
        dictContrats["date_debut"] = date_debut
        if self.datepicker_date_fin.IsShown() :
            dictContrats["date_fin"] = date_fin
        else:
            dictContrats["date_fin"] = "2999-01-01"
        if rupture == True :
            dictContrats["date_rupture"] = date_rupture
        else:
            dictContrats["date_rupture"] = ""
        dictContrats["essai"] = essai
        
        return True
    
