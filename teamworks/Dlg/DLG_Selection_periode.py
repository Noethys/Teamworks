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
from Ctrl import CTRL_Bouton_image
import FonctionsPerso
import GestionDB
import wx.lib.mixins.listctrl  as  listmix
import datetime
if 'phoenix' in wx.PlatformInfo:
    from wx.adv import DatePickerCtrl, DP_DROPDOWN
else :
    from wx import DatePickerCtrl, DP_DROPDOWN
import calendar


class SelectionPeriode(wx.Dialog):
    """ On récupère les infos de cette boîte avec GetDates() ou avec GetPersonnesPresentes() """
    def __init__(self, parent, id=-1, title=_(u"Sélection d'une période"), nomFichier=""):
        wx.Dialog.__init__(self, parent, id, title, size=(350, 400))

        # Label
        self.label = wx.StaticText(self, -1, _(u"Veuillez sélectionner ou saisir une période :"))
        
        # listCtrl vacances
        self.staticbox_vacances = wx.StaticBox(self, -1, _(u"Périodes de vacances"))
        self.ctrl_vacances = ListCtrl_vacances(self)
        self.ctrl_vacances.SetMinSize((20, 20)) 
        
        # Mois et Année
        self.staticbox_moisAnnee = wx.StaticBox(self, -1, _(u"Mois et année"))
        self.label_mois = wx.StaticText(self, -1, "Mois :", size=(50, -1), style=wx.ALIGN_RIGHT)
        self.listeMois = [u"", _(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre")]
        self.ctrl_mois = wx.Choice(self, -1, choices = self.listeMois) #AdvancedComboBox( self, "", size=(100, -1), choices = self.listeMois)
        self.label_annee = wx.StaticText(self, -1, _(u"Année :"), style=wx.ALIGN_RIGHT)
        
        self.listeAnnees = ["",]
        for annee in range(2000, 2050) :
            self.listeAnnees.append(str(annee))
        self.ctrl_annee = wx.Choice(self, -1, choices = self.listeAnnees) #AdvancedComboBox( self, "", size=(70, -1), choices = self.listeAnnees) #TextCtrlAnnee(self, "", size=(50, -1) )
        
        # Dates
        self.staticbox_dates = wx.StaticBox(self, -1, _(u"Dates"))
        self.label_date_debut = wx.StaticText(self, -1, "Du :", size=(50, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_date_debut = DatePickerCtrl(self, -1, style=DP_DROPDOWN)
        self.label_date_fin = wx.StaticText(self, -1, "Au :", style=wx.ALIGN_RIGHT)
        self.ctrl_date_fin = DatePickerCtrl(self, -1, style=DP_DROPDOWN)
        
        # Boutons
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_CHOICE, self.On_maj_mois, self.ctrl_mois)
        self.Bind(wx.EVT_CHOICE, self.On_maj_annee, self.ctrl_annee)
        

    def __set_properties(self):
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label, 0, wx.ALL, 10)
        
        # Vacances
        sizerStaticBox_vacances = wx.StaticBoxSizer(self.staticbox_vacances, wx.HORIZONTAL)
        sizerStaticBox_vacances.Add(self.ctrl_vacances, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(sizerStaticBox_vacances, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        # Mois et Année
        sizerStaticBox_moisAnnee = wx.StaticBoxSizer(self.staticbox_moisAnnee, wx.HORIZONTAL)
        sizerStaticBox_moisAnnee.Add(self.label_mois, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        sizerStaticBox_moisAnnee.Add(self.ctrl_mois, 0, wx.EXPAND|wx.ALL, 5)
        sizerStaticBox_moisAnnee.Add(self.label_annee, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        sizerStaticBox_moisAnnee.Add(self.ctrl_annee, 0, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(sizerStaticBox_moisAnnee, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        # Dates
        sizerStaticBox_dates = wx.StaticBoxSizer(self.staticbox_dates, wx.HORIZONTAL)
        sizerStaticBox_dates.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        sizerStaticBox_dates.Add(self.ctrl_date_debut, 0, wx.EXPAND|wx.ALL, 5)
        sizerStaticBox_dates.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        sizerStaticBox_dates.Add(self.ctrl_date_fin, 0, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(sizerStaticBox_dates, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
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

    def GetDates(self):
        """ Renvoie les dates des deux datepickers au format datetime """
        date_debut = self.GetDatePickerValue(self.ctrl_date_debut)
        date_fin = self.GetDatePickerValue(self.ctrl_date_fin)
        return (date_debut, date_fin)

    def SetDates(self, date_debut=None, date_fin=None):
        """ Ecrit les dates de début et fin dans les deux datepickers """
        if date_debut != None : self.SetDatePicker(self.ctrl_date_debut, date_debut)
        if date_fin != None : self.SetDatePicker(self.ctrl_date_fin, date_fin)
    
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
        
    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        self.EndModal(wx.ID_OK)
        
    def ctrl_mois_EvtComboBox(self, event):
        self.On_maj_mois()
        
    def On_maj_mois(self, event):
        """ Quand un item est sélectionné dans le combobox mois """
        index = self.ctrl_mois.GetSelection()
        if index > 0 :
            mois = index
            # Si pas d'année saisie, sélectionne l'année en cours
            indexAnnee = self.ctrl_annee.GetSelection()
            if indexAnnee < 2 :
                annee = datetime.datetime.now().year
                self.ctrl_annee.SetStringSelection(str(annee))
            else:
                annee = int(self.listeAnnees[self.ctrl_annee.GetSelection()])
            # Si mois et année valide, on saisi les dates dans les datepickers
            date_debut = datetime.date(annee, mois, 1)
            date_fin = datetime.date(annee, mois, calendar.monthrange(annee, mois)[1])
            self.SetDates(date_debut, date_fin)

    def ctrl_annee_EvtComboBox(self, event):
        self.On_maj_annee()
        
    def On_maj_annee(self, event):
        """ Quand un item est sélectionné dans le combobox annee """
        index = self.ctrl_annee.GetSelection()
        if index != -1 :
            annee = int(self.listeAnnees[index])
            # Si un mois a déjà été saisi, on saisie les dates extrêmes du mois sélectionné dans les datespickers
            if self.ctrl_mois.GetSelection() != -1 :
                mois = self.ctrl_mois.GetSelection() + 1
                date_debut = datetime.date(annee, mois, 1)
                date_fin = datetime.date(annee,mois, calendar.monthrange(annee, mois)[1])
                self.SetDates(date_debut, date_fin)
            else:
                # Sinon, on saisie les dates extrêmes de l'année dans les datepickers
                date_debut = datetime.date(annee, 1, 1)
                date_fin = datetime.date(annee, 12, 31)
                self.SetDates(date_debut, date_fin)

    def GetPersonnesPresentes(self):
        """ Permet de récupérer la liste des personnes présentes sur la période sélectionnée """
        date_debut, date_fin = self.GetDates()
        # Récupération des presences des personnes
        DB = GestionDB.DB()        
        req = """SELECT IDpersonne FROM presences WHERE date>='%s' AND date<='%s' GROUP BY IDpersonne""" % (date_debut, date_fin)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listePersonnes = []
        if len(listeDonnees) != 0 :
            # Formatage de la liste
            for donnees in listeDonnees :
                listePersonnes.append(donnees[0])
        return listePersonnes
        
        
        
##class AdvancedComboBox(wx.ComboBox) :
##    """ Crée un comboBox avec auto-complete limité à la liste donnée """
##    def __init__(self, parent, value, choices=[], style=0, **par):
##        wx.ComboBox.__init__(self, parent, wx.ID_ANY, value, style=style|wx.CB_DROPDOWN, choices=choices, **par)
##        self.parent = parent
##        self.choices = choices
##        self.Bind(wx.EVT_TEXT, self.EvtText)
##        self.Bind(wx.EVT_CHAR, self.EvtChar)
##        self.Bind(wx.EVT_COMBOBOX, self.EvtCombobox)
##        self.Bind(wx.EVT_KILL_FOCUS, self.EvtKillFocus)
##        self.ignoreEvtText = False
##
##    def EvtCombobox(self, event):
##        self.ignoreEvtText = True
##        event.Skip()
##
##    def EvtChar(self, event):
##        if event.GetKeyCode() == 8 and self.GetValue() != u"" :
##            self.ignoreEvtText = True
##        event.Skip()
##
##    def EvtText(self, event):
##        if self.ignoreEvtText :
##            self.ignoreEvtText = False
##            return
##        currentText = event.GetString()
##        found = False
##        index = 0
##        for choice in self.choices :
##            if choice.startswith(currentText):
##                self.SetValue(choice)
##                self.SetInsertionPoint(len(currentText))
##                self.SetMark(len(currentText), len(choice))
##                found = True
##                break
##            index += 1
##        if not found and currentText!= "" :
##            ancienTexte = currentText[:-1]
##            if len(ancienTexte) == 0 :
##                self.SetValue("")
##            else :
##                for choice in self.choices :
##                    if choice.startswith(ancienTexte):
##                        self.SetValue(choice)
##                        self.SetInsertionPoint(len(ancienTexte))
##                        self.SetMark(len(ancienTexte), len(choice))
##                        break
##        event.Skip()
##    
##    def EvtKillFocus(self, event):
##        # Si la valeur n'est pas correcte dans le champ, remet la valeur précédente
##        if self.GetValue() not in self.choices and self.GetValue() != u"" :
##            self.Undo()
##        # Fait la sélection dans la liste
##        if self.GetValue() in self.choices :
##            self.SetStringSelection(self.GetValue())
##        # Met à jour les contrôles mois et annee
##        self.parent.On_maj_mois()
##        self.parent.On_maj_annee()
##        event.Skip()
        


class ListCtrl_vacances(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__( self, parent, -1, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES|wx.LC_NO_HEADER)
        self.parent = parent

        #adding some attributes (colourful background for each item rows)
        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour("#EEF4FB") # Vert = #F0FBED

        # Remplissage du ListCtrl
        self.Remplissage()
        
        #events
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)

    def Remplissage(self):
        
        # Récupération des données dans la base de données
        self.Importation()
        
        # Création des colonnes
        self.nbreColonnes = 2
        self.InsertColumn(0, _(u"Nom"))
        self.SetColumnWidth(0, 100)
        self.InsertColumn(1, _(u"Dates"))
        self.SetColumnWidth(1, 100)
        
        #These two should probably be passed to init more cleanly
        #setting the numbers of items = number of elements in the dictionary
        self.itemDataMap = self.donnees
        self.itemIndexMap = list(self.donnees.keys())
        self.SetItemCount(self.nbreLignes)
        
        #mixins
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

        #sort by genre (column 1), A->Z ascending order (1)
        self.SortListItems(1, 0)
            
    def DateEngFr(self, textDate):
        text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
        return text

    def Importation(self):
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDperiode, nom, annee, date_debut, date_fin
        FROM periodes_vacances ORDER BY date_debut DESC; """
        DB.ExecuterReq(req)
        listeVacances = DB.ResultatReq()
        DB.Close()
        self.nbreLignes = len(listeVacances)
        # Création du dictionnaire de données
        self.donnees = {}
        index = 0
        for IDperiode, nom, annee, date_debut, date_fin in listeVacances :
            self.donnees[index] = [nom + " " + annee, date_debut + "_" + date_fin]
            index += 1
            
    def MAJListeCtrl(self):
        self.ClearAll()
        self.Remplissage()
        self.resizeLastColumn(0)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)
           
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
        # Formatage de la colonne dates
        if col == 1 : 
            date_debut, date_fin = valeur.split("_")
            valeur = "Du " + self.DateEngFr(date_debut) + " au " + self.DateEngFr(date_fin)
        return valeur

    def OnGetItemImage(self, item):
        """ Affichage des images en début de ligne """
        return -1

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

    def OnItemActivated(self, event):
        pass

    def OnItemSelected(self, event):
        """ Item selectionné """
        index = self.GetFirstSelected()
        valeur = six.text_type(self.itemDataMap[index][1])
        date_debut, date_fin = valeur.split("_")
        date_debut = datetime.date(year=int(date_debut[:4]), month=int(date_debut[5:7]), day=int(date_debut[8:10]))
        date_fin = datetime.date(year=int(date_fin[:4]), month=int(date_fin[5:7]), day=int(date_fin[8:10]))
        # Efface les contenus des contrôles mois et annee
        self.parent.ctrl_mois.SetStringSelection("")
        self.parent.ctrl_annee.SetStringSelection("")
        # Set les dates dans les datepickers
        self.parent.SetDates(date_debut, date_fin)


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = SelectionPeriode(None)
    frm.ShowModal()
    app.MainLoop()