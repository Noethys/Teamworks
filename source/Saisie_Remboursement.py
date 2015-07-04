#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import FonctionsPerso
import GestionDB
import datetime
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import sys

try: import psyco; psyco.full()
except: pass


class SaisieRemboursement(wx.Dialog):
    """ Saisie d'un remboursement pour les frais de d�placement """
    def __init__(self, parent, id=-1, title=_(u"Saisie d'un remboursement"), IDremboursement=None, IDpersonne=None):
        wx.Dialog.__init__(self, parent, id, title) #, size=(400, 450)
        self.IDremboursement = IDremboursement
        self.IDpersonne = IDpersonne
        
        # G�n�ralit�s
        self.staticbox_generalites = wx.StaticBox(self, -1, _(u"Caract�ristiques"))
        
        self.label_date = wx.StaticText(self, -1, _(u"Date :"), size=(60, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_date = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN)
        
        self.label_montant = wx.StaticText(self, -1, _(u"Montant :"), size=(60, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_montant = wx.TextCtrl(self, -1, u"", size=(50, -1), )
        self.label_euro_montant = wx.StaticText(self, -1, u"�")
        
        self.label_utilisateur = wx.StaticText(self, -1, _(u"Utilisateur :"), size=(60, -1), style=wx.ALIGN_RIGHT)
        self.ImportationPersonnes()
        self.ctrl_utilisateur = AdvancedComboBox( self, "", size=(100, -1), choices = self.listePersonnes)
        
        # D�placements
        self.staticbox_deplacements = wx.StaticBox(self, -1, _(u"D�placements rattach�s"))
        
        self.label_rattachement = wx.StaticText(self, -1, u"", size=(-1, -1))
        self.ctrl_deplacements = ListCtrl_deplacements(self, size=(-1, 200), IDremboursement=IDremboursement, IDpersonne=self.IDpersonne)
        
        # Boutons
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        
         # IDpersonne :
        if self.IDpersonne != None :
            self.SetPersonne(self.IDpersonne)
        # Si c'est une modification :
        if self.IDremboursement != None :
            self.SetTitle(_(u"Modification d'un remboursement"))
            self.Importation()
        # Cache le controle utilisateur :
        if self.IDpersonne != None :
            self.label_utilisateur.Show(False)
            self.ctrl_utilisateur.Show(False)
            self.SetSize((-1, 415))
        
        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.ctrl_montant.Bind(wx.EVT_KILL_FOCUS, self.montant_EvtKillFocus)

    def __set_properties(self):
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler la saisie"))
        self.ctrl_date.SetToolTipString(_(u"S�lectionnez ici la date du d�placement"))
        self.ctrl_utilisateur.SetToolTipString(_(u"S�lectionnez ici l'utilisateur pour ce d�placement"))
##        self.ctrl_objet.SetToolTipString(_(u"Saisissez ici l'objet du d�placement. Ex : r�union, formation, etc..."))
##        self.ctrl_cp_depart.SetToolTipString(_(u"Saisissez ici le code postal de la ville de d�part"))
##        self.ctrl_ville_depart.SetToolTipString(_(u"Saisissez ici le nom de la ville de d�part"))
##        self.ctrl_cp_arrivee.SetToolTipString(_(u"Saisissez ici le code postal de la ville d'arriv�e"))
##        self.ctrl_ville_arrivee.SetToolTipString(_(u"Saisissez ici le nom de la ville d'arriv�e"))
##        self.ctrl_distance.SetToolTipString(_(u"Saisissez ici la distance en Km entre les 2 villes s�lectionn�es.\nSi Teamworks la connait, il l'indiquera automatiquement."))
##        self.ctrl_aller_retour.SetToolTipString(_(u"Cochez cette case si le d�placement a fait l'objet d'un aller/retour.\nLa distance sera ainsi doubl�e."))
##        self.ctrl_tarif.SetToolTipString(_(u"Saisissez ici le montant du tarif du Km pour permettre calculer le montant du remboursement pour ce d�placement."))
##        self.bouton_options_depart.SetToolTipString(_(u"Cliquez ici pour rechercher une ville ou pour saisir manuellement une ville non pr�sente dans la base de donn�es du logiciel"))
##        self.bouton_options_arrivee.SetToolTipString(_(u"Cliquez ici pour rechercher une ville ou pour saisir manuellement une ville non pr�sente dans la base de donn�es du logiciel"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # G�n�ralit�s
        sizerStaticBox_generalites = wx.StaticBoxSizer(self.staticbox_generalites, wx.HORIZONTAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        
        grid_sizer_generalites.Add(self.label_date, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        
        sizer_generalites = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        sizer_generalites.Add(self.ctrl_date, 0, wx.ALL, 0)
        sizer_generalites.Add( (20,5), 0, wx.ALL, 0)
        sizer_generalites.Add(self.label_montant, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        sizer_generalites.Add(self.ctrl_montant, 1, wx.EXPAND|wx.ALL, 0)
        sizer_generalites.Add(self.label_euro_montant, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_generalites.Add(sizer_generalites, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_generalites.Add(self.label_utilisateur, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_generalites.Add(self.ctrl_utilisateur, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_generalites.AddGrowableCol(1)
        sizerStaticBox_generalites.Add(grid_sizer_generalites, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(sizerStaticBox_generalites, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 10)
        
        # D�placements
        sizerStaticBox_deplacements = wx.StaticBoxSizer(self.staticbox_deplacements, wx.HORIZONTAL)
        grid_sizer_deplacements = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        grid_sizer_deplacements.Add(self.ctrl_deplacements, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_deplacements.Add(self.label_rattachement, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_deplacements.AddGrowableRow(0)
        grid_sizer_deplacements.AddGrowableCol(0)
        sizerStaticBox_deplacements.Add(grid_sizer_deplacements, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(sizerStaticBox_deplacements, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
                        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.Fit(self)
        self.Layout()
    
                
    def ImportationPersonnes(self):
        """ Importation de la liste des personnes """
        # R�cup�ration de la liste des personnes
        DB = GestionDB.DB()        
        req = """SELECT IDpersonne, nom, prenom FROM personnes ORDER BY nom, prenom; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Cr�ation de la liste pour le listBox
        self.listePersonnes = []
        self.dictPersonnes = {}
        index = 0
        for IDpersonne, nom, prenom in listeDonnees :
            self.listePersonnes.append(nom + " " + prenom)
            self.dictPersonnes[index] = IDpersonne
            index += 1
            
    
    def Importation(self):
        """ Importation des donn�es si c'est une modification de d�placement """
        
        # R�cup�ration des donn�es du d�placement
        DB = GestionDB.DB()        
        req = """SELECT IDremboursement, IDpersonne, date, montant, listeIDdeplacement FROM remboursements WHERE IDremboursement=%d; """ % self.IDremboursement
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        
        # Int�gration des donn�es dans le formulaire
        self.IDpersonne = listeDonnees[0][1]
        self.SetPersonne(self.IDpersonne)
        date = listeDonnees[0][2]
        self.SetDate(datetime.date(year=int(date[:4]), month=int(date[5:7]), day=int(date[8:10])))
        self.ctrl_montant.SetValue(str(listeDonnees[0][3]))
        # MAJ de l'affichage
        self.MajIDpersonne()
        self.MajLabelRattachement(float(self.ctrl_montant.GetValue()))
    
    def SetRemboursement(self, IDremboursement=None):
        """ D�finit le remboursement """
        if IDremboursement == None or IDremboursement == 0 or IDremboursement == "":
            self.ctrl_remboursement.SetLabel("Aucun remboursement.")
        else:
            # Recherche date du remboursement
            DB = GestionDB.DB()        
            req = """SELECT date FROM remboursements WHERE IDremboursement=%d; """ % IDremboursement
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            DB.Close()
            dateRemboursement = self.DateEngFr(listeDonnees[0][0])
            self.ctrl_remboursement.SetLabel("N�" + str(IDremboursement) + " du " + dateRemboursement)
        
    def DateEngFr(self, textDate):
        text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
        return text

    def SetAllerRetour(self, etat=False):
        """ D�finit l'aller retour """
        self.ctrl_aller_retour.SetValue(etat)
        if etat == False :
            self.label_km.SetLabel("Km  (Aller simple)")
        else :
            self.label_km.SetLabel("Km  (Aller/retour)")
        
    
    def CalcMontantRmbst(self):
        if self.ValideControleFloat(self.ctrl_distance) == False : return
        if self.ValideControleFloat(self.ctrl_tarif) == False : return
        distance = float(self.ctrl_distance.GetValue())
        tarif = float(self.ctrl_tarif.GetValue())
        montant = distance * tarif
        self.ctrl_montant.SetLabel(u"%.2f �" % montant)
    

    def montant_EvtKillFocus(self, event):
        # V�rifie la validit� de la valeur
        if self.ValideControleFloat(self.ctrl_montant) == False : 
            dlg = wx.MessageDialog(self, _(u"Le montant n'est pas valide. \nIl doit �tre sous la forme '1.32' ou '100.50' par exemple..."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_deplacements.Enable(False)
            self.ctrl_montant.SetFocus()
            return
        # Met � jour le montant dans le listCtrl
        if self.ctrl_utilisateur.GetCurrentSelection() != -1 :
            self.MajLabelRattachement(float(self.ctrl_montant.GetValue()))
            
    
    def MajIDpersonne(self):
        """ Quand l'utilisateur est mis � jour """
        self.IDpersonne = self.GetPersonne()
        self.ctrl_deplacements.IDpersonne = self.IDpersonne
        self.ctrl_deplacements.MAJListeCtrl()
        
    def MajLabelRattachement(self, montant=None):
        # Met � jour le montant dans le listCtrl
        if montant != None :
            self.ctrl_deplacements.montantRemboursement = montant
        self.ctrl_deplacements.MajLabelRattachement()
        
    def ValideControleFloat(self, controle=None):
        """ V�rifie la validit� d'un contr�le de type Float """
        valeur = controle.GetValue()
        if valeur == "" : return True
        # V�rifie que la valeur est bien constitu�e de chiffres uniquement
        incoherences = ""
        for lettre in valeur :
            if lettre not in "0123456789." : incoherences += "'"+ lettre + "', "
        if len(incoherences) != 0 :
            return False
        else :
            try :
                test = float(valeur)
            except :
                return False
            return True
            
                
    def MajDistance(self):
        """ Met � jour le Contr�le Distance en fonction des villes saisies """
        depart = (self.ctrl_cp_depart.GetValue(), self.ctrl_ville_depart.GetValue())
        arrivee = (self.ctrl_cp_arrivee.GetValue(), self.ctrl_ville_arrivee.GetValue())
        
        for IDdistance, cp_depart, ville_depart, cp_arrivee, ville_arrivee, distance in self.listeDistances :
            depart_temp = (str(cp_depart), ville_depart)
            arrivee_temp = (str(cp_arrivee), ville_arrivee)
            if (depart == depart_temp and arrivee == arrivee_temp) or (depart == arrivee_temp and arrivee == depart_temp) :
                if self.ctrl_aller_retour.GetValue() == True :
                    self.ctrl_distance.SetValue(str(distance*2))
                else :
                    self.ctrl_distance.SetValue(str(distance))
                break    
        
    def GetPersonne(self):
        """ R�cup�re l'IDpersonne du comboBox """
        index = self.ctrl_utilisateur.GetCurrentSelection()
        if index == -1 : return None
        IDpersonne = self.dictPersonnes[index]
        return IDpersonne
    
    def SetPersonne(self, IDpersonne=None):
        # Recherche de l'index dans le dictPersonnes
        for index, IDpers in self.dictPersonnes.iteritems() :
            if IDpersonne == IDpers :
                self.ctrl_utilisateur.Select(index)
                break
            
    def SetDate(self, date):
        """ Saisi une date au format datetime dans le datepicker """
        self.SetDatePicker(self.ctrl_date, date)
               
    def SetDatePicker(self, controle, date) :
        """ Met une date au format datetime dans un datePicker donn� """
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

    def OnBoutonAide(self, event):
        """ Aide """
        FonctionsPerso.Aide(36)
        
    def OnBoutonOk(self, event):
        """ Validation des donn�es saisies """

        # V�rifie contr�le Utilisateur
        valeur = self.ctrl_utilisateur.GetValue()
        if valeur == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner un utilisateur."), "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_utilisateur.SetFocus()
            return
        
        # V�rifie contr�le montant
        valeur = self.ctrl_montant.GetValue()
        if valeur == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un montant en euros pour ce remboursement."), "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return
        
        if self.ValideControleFloat(self.ctrl_montant) == False : 
            dlg = wx.MessageDialog(self, _(u"Le montant saisi n'est pas valide \nIl doit �tre sous la forme '32.50' ou '54' par exemple..."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return
        
        if float(valeur) == 0 :
            dlg = wx.MessageDialog(self, _(u"Le montant que vous avez saisi est de 0 �\n\nSouhaitez-vous conserver ce montant ?\n(Cliquez sur 'Non' ou 'Annuler' pour modifier maintenant le montant)"), _(u"Erreur de saisie"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            if reponse == wx.ID_NO or reponse == wx.ID_CANCEL:
                dlg.Destroy()
                self.ctrl_montant.SetFocus()
                return
            else: dlg.Destroy()
        
        # V�rifie contr�le d�placements
        listeIDcoches, listeIDdecoches = self.ctrl_deplacements.ListeItemsCoches()
        
        if len(listeIDcoches) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez coch� aucun d�placement dans la liste.\n\nSouhaitez-vous quand m�me valider ?\n(Cliquez sur 'Non' ou 'Annuler' pour cocher maintenant des d�placements)"), _(u"Erreur de saisie"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            if reponse == wx.ID_NO or reponse == wx.ID_CANCEL:
                dlg.Destroy()
                return
            else: dlg.Destroy()
        
        # Sauvegarde
        self.Sauvegarde()

        # Ferme la bo�te de dialogue
        self.EndModal(wx.ID_OK)        
        
        
    def Sauvegarde(self):
        """ Sauvegarde des donn�es """
        # R�cup�ration des valeurs saisies
        date = str(self.GetDatePickerValue(self.ctrl_date))
        IDpersonne = self.dictPersonnes[self.ctrl_utilisateur.GetCurrentSelection()]
        montant = float(self.ctrl_montant.GetValue())
        # R�cup�ration des d�placements coch�s
        listeIDcoches, listeIDdecoches = self.ctrl_deplacements.ListeItemsCoches()
        texteID = ""
        if len(listeIDcoches) != 0 :
            for ID in listeIDcoches :
                texteID += str(ID) + "-"
            texteID = texteID[:-1]
        
        DB = GestionDB.DB()
        # Cr�ation de la liste des donn�es
        listeDonnees = [    ("date",   date),  
                                    ("IDpersonne",    IDpersonne),
                                    ("montant",    montant),
                                    ("listeIDdeplacement",    texteID), 
                                    ]
        if self.IDremboursement == None :
            # Enregistrement d'un nouveau remboursement
            newID = DB.ReqInsert("remboursements", listeDonnees)
            ID = newID
        else:
            # Modification du remboursement
            DB.ReqMAJ("remboursements", listeDonnees, "IDremboursement", self.IDremboursement)
            ID = self.IDremboursement
        DB.Commit()
        DB.Close()
        
        #
        # Modification du IDdeplacement de chaque d�placement rattach�
        #
        DB = GestionDB.DB()
        # Cr�ation de la liste des donn�es
        for IDdeplacement in listeIDcoches :
            listeDonnees = [    ("IDremboursement",   ID),  ]
            DB.ReqMAJ("deplacements", listeDonnees, "IDdeplacement", IDdeplacement)
        # D�coche les autres items
        for IDdeplacement in listeIDdecoches :
            listeDonnees = [    ("IDremboursement",   0),  ]
            DB.ReqMAJ("deplacements", listeDonnees, "IDdeplacement", IDdeplacement)
        DB.Commit()
        DB.Close()

        return ID
            
            



class AdvancedComboBox(wx.ComboBox) :
    """ Cr�e un comboBox avec auto-complete limit� � la liste donn�e """
    def __init__(self, parent, value, choices=[], style=0, **par):
        wx.ComboBox.__init__(self, parent, wx.ID_ANY, value, style=style|wx.CB_DROPDOWN, choices=choices, **par)
        self.parent = parent
        self.choices = choices
        self.Bind(wx.EVT_TEXT, self.EvtText)
        self.Bind(wx.EVT_CHAR, self.EvtChar)
        self.Bind(wx.EVT_COMBOBOX, self.EvtCombobox)
        self.Bind(wx.EVT_KILL_FOCUS, self.EvtKillFocus)
        self.ignoreEvtText = False

    def EvtCombobox(self, event):
        self.ignoreEvtText = True
        self.parent.MajIDpersonne()
        event.Skip()

    def EvtChar(self, event):
        if event.GetKeyCode() == 8 and self.GetValue() != u"" :
            self.ignoreEvtText = True
        event.Skip()

    def EvtText(self, event):
        if self.ignoreEvtText :
            self.ignoreEvtText = False
            return
        currentText = event.GetString()
        found = False
        index = 0
        for choice in self.choices :
            if choice.startswith(currentText):
                self.SetValue(choice)
                self.SetInsertionPoint(len(currentText))
                self.SetMark(len(currentText), len(choice))
                found = True
                break
            index += 1
        if not found and currentText!= "" :
            ancienTexte = currentText[:-1]
            if len(ancienTexte) == 0 :
                self.SetValue("")
            else :
                for choice in self.choices :
                    if choice.startswith(ancienTexte):
                        self.SetValue(choice)
                        self.SetInsertionPoint(len(ancienTexte))
                        self.SetMark(len(ancienTexte), len(choice))
                        break
        self.parent.MajIDpersonne()
        event.Skip()
    
    def EvtKillFocus(self, event):
        # Si la valeur n'est pas correcte dans le champ, remet la valeur pr�c�dente
        if self.GetValue() not in self.choices and self.GetValue() != u"" :
            self.Undo()
        # Fait la s�lection dans la liste
        if self.GetValue() in self.choices :
            self.SetStringSelection(self.GetValue())
        self.parent.MajIDpersonne()
        event.Skip()
        




# -----------------------------------------------------------------------------------------------------------------------------------

class ListCtrl_deplacements(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent, size=(-1, -1), IDremboursement=None, IDpersonne=None):
        wx.ListCtrl.__init__(self, parent, -1, size=(size), style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        CheckListCtrlMixin.__init__(self)
        self.parent = parent
        self.IDpersonne = IDpersonne
        self.IDremboursement = IDremboursement
        self.montantRemboursement = 0
        
        self.MAJListeCtrl()
        
        # Binds
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

    def Remplissage(self):

        self.Importation()

        # Cr�ation des colonnes
        self.InsertColumn(0, u"N�")
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
        
        # Remplissage avec les valeurs
        self.remplissage = True
        
        for IDdeplacement, date, objet, trajet, dist, tarif_km, montant, remboursement in self.donnees :
            index = self.InsertStringItem(sys.maxint, str(IDdeplacement))
            self.SetStringItem(index, 1, date)
            self.SetStringItem(index, 2, objet)
            self.SetStringItem(index, 3, trajet)
            self.SetStringItem(index, 4, dist)
            self.SetStringItem(index, 5, tarif_km)
            self.SetStringItem(index, 6, montant)
            
            self.SetItemData(index, IDdeplacement)
            
            # Check
            if remboursement != 0 :
                self.CheckItem(index) 
                                    
        self.remplissage = False

    def MAJListeCtrl(self):
        self.ClearAll()
        # Active ou non ce listCtrl si IDpersonne a �t� renseign�
        if self.IDpersonne == None :
            self.Enable(False)
            self.parent.label_rattachement.SetLabel(_(u"Veuillez s�lectionner un utilisateur dans la liste propos�e..."))
            return
        else:
            self.Enable(True)
        # Remplissage
        self.Remplissage()
        self.MajLabelRattachement()
        
    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)

    def OnCheckItem(self, index, flag):
        """ Ne fait rien si c'est le remplissage qui coche la case ! """
        self.MajLabelRattachement()

    def MajLabelRattachement(self):
        """ Met � jour le label R�sum� de rattachement """
        montantRattache = 0
        montantNonRattache = 0
        nbreItems = self.GetItemCount()
        for index in range(0, nbreItems) :
            montant = float(self.GetItem(index, 6).GetText()[:-2])
            # V�rifie si l'item est coch�
            if self.IsChecked(index) :
                montantRattache += montant
        
        montantNonRattache = self.montantRemboursement - montantRattache
        if montantNonRattache == 0 :
            self.parent.label_rattachement.SetLabel(_(u"Vous devez cocher les d�placements ci-dessous pour les rattacher."))
        if montantNonRattache > 0 :
            self.parent.label_rattachement.SetLabel(_(u"Vous pouvez encore rattacher pour ") + u"%.2f �" % montantNonRattache + _(u" de d�placements."))
        if montantNonRattache < 0 :
            self.parent.label_rattachement.SetLabel(_(u"Attention ! Vous avez rattach� ") + u"%.2f �" % (-montantNonRattache) + _(u" de d�placements en trop !"))
        if len(self.donnees) == 0 :
            self.parent.label_rattachement.SetLabel(_(u"Aucun d�placement n'est � rattacher pour cette personne."))

    def Importation(self):
        # R�cup�ration des donn�es
        DB = GestionDB.DB()
        if self.IDremboursement ==None :
            # Si en mode ajout : On ne s�lectionne que les d�placements non rattach�s
            req = """SELECT IDdeplacement, date, objet, ville_depart, ville_arrivee, distance, aller_retour, tarif_km, IDremboursement FROM deplacements WHERE IDpersonne=%d AND IDremboursement=0 ORDER BY date; """ % self.IDpersonne
        else:
            # Si en mode modification, on s�lectionne les d�placements rattach�s � self.IDremboursement et les non rattach�s
            req = """SELECT IDdeplacement, date, objet, ville_depart, ville_arrivee, distance, aller_retour, tarif_km, IDremboursement FROM deplacements WHERE IDpersonne=%d AND (IDremboursement=0 OR IDremboursement=%d) ORDER BY date; """ % (self.IDpersonne, self.IDremboursement)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.nbreLignes = len(listeDonnees)
        # Cr�ation du dictionnaire de donn�es
        self.donnees = []
        index = 0
        self.montantRattache = 0
        self.montantNonRattache = 0
        
        for IDdeplacement, date, objet, ville_depart, ville_arrivee, distance, aller_retour, tarif_km, IDremboursement in listeDonnees :
            #Formatage date
            dateTmp = str(date[8:10])+"/"+str(date[5:7])+"/"+str(date[0:4])
            # Formatage Trajet
            if aller_retour == "True" :
                trajet = ville_depart + " <--> " + ville_arrivee
            else:
                trajet = ville_depart + " -> " + ville_arrivee
            # Formatage distance
            dist = str(distance) + _(u" Km")
            # Formatage montant
            montant = float(distance) * float(tarif_km)
            montantStr = u"%.2f �" % montant
            # Formatage tarif/Km
            tarif_km = str(tarif_km) + _(u" �/km")
            # Montant rattach�
            if IDremboursement != 0 : 
                self.montantRattache += montant
            self.donnees.append((IDdeplacement, dateTmp, objet, trajet, dist, tarif_km, montantStr, IDremboursement))
            index += 1

    def ListeItemsCoches(self):
        """ R�cup�re la liste des IDdeplacements coch�s """
        listeIDcoches = []
        listeIDdecoches = []
        nbreItems = self.GetItemCount()
        for index in range(0, nbreItems) :
            ID = int(self.GetItem(index, 0).GetText())
            # V�rifie si l'item est coch�
            if self.IsChecked(index) :
                listeIDcoches.append(ID)
            else:
                listeIDdecoches.append(ID)
        return listeIDcoches, listeIDdecoches
            
        
        
        


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = SaisieRemboursement(None, IDremboursement=1, IDpersonne=None)
    frm.ShowModal()
    app.MainLoop()