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
import wx.lib.masked as masked
import sqlite3
import sys
if 'phoenix' in wx.PlatformInfo:
    from wx.adv import DatePickerCtrl, DP_DROPDOWN
else :
    from wx import DatePickerCtrl, DP_DROPDOWN

import decimal
decimal.getcontext().prec = 2



class SaisieDeplacement(wx.Dialog):
    """ Saisie d'un déplacement pour les frais de déplacement """
    def __init__(self, parent, id=-1, title=_(u"Saisie d'un déplacement"), IDdeplacement=None, IDpersonne=None):
        wx.Dialog.__init__(self, parent, id, title)
        self.IDdeplacement = IDdeplacement
        self.IDpersonne = IDpersonne
        
        # Création d'une liste des villes et codes postaux
        con = sqlite3.connect(Chemins.GetStaticPath("Databases/Villes.db3"))
        cur = con.cursor()
        cur.execute("SELECT ville, cp FROM villes")
        self.listeVillesTmp = cur.fetchall()
        con.close()
        
        # Création d'une liste de noms de villes
        self.listeNomsVilles = []
        self.listeVilles = []
        for nom, cp in self.listeVillesTmp:
            self.listeVilles.append((nom, "%05d" % cp))
            self.listeNomsVilles.append(nom)
        
        # Importation de la table des distances
        self.ImportationDistances()
        
        # Généralités
        self.staticbox_generalites = wx.StaticBox(self, -1, _(u"Généralités"))
        
        self.label_date = wx.StaticText(self, -1, _(u"Date :"), size=(95, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_date = DatePickerCtrl(self, -1, style=DP_DROPDOWN)
        
        self.label_utilisateur = wx.StaticText(self, -1, _(u"Utilisateur :"), size=(95, -1), style=wx.ALIGN_RIGHT)
        self.ImportationPersonnes()
        self.ctrl_utilisateur = AdvancedComboBox( self, "", size=(100, -1), choices = self.listePersonnes)
        
        self.label_objet = wx.StaticText(self, -1, _(u"Objet :"), size=(95, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_objet = wx.TextCtrl(self, -1, "", size=(-1, -1), style=wx.TE_MULTILINE)
        
        # Trajet
        self.staticbox_trajet = wx.StaticBox(self, -1, _(u"Trajet"))
        
        self.label_depart = wx.StaticText(self, -1, _(u"Ville de départ :"), size=(95, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_cp_depart = TextCtrlCp(self, value="", listeVilles=self.listeVilles, size=(55, -1), style=wx.TE_CENTRE, mask = "#####") 
        self.ctrl_ville_depart = TextCtrlVille(self, value="", ctrlCp=self.ctrl_cp_depart, listeVilles=self.listeVilles, listeNomsVilles=self.listeNomsVilles)
        self.ctrl_cp_depart.ctrlVille = self.ctrl_ville_depart
        self.bouton_options_depart = wx.Button(self, -1, "...", size=(20, 20))
        
        self.label_arrivee = wx.StaticText(self, -1, _(u"Ville d'arrivée :"), size=(95, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_cp_arrivee = TextCtrlCp(self, value="", listeVilles=self.listeVilles, size=(55, -1), style=wx.TE_CENTRE, mask = "#####") 
        self.ctrl_ville_arrivee = TextCtrlVille(self, value="", ctrlCp=self.ctrl_cp_arrivee, listeVilles=self.listeVilles, listeNomsVilles=self.listeNomsVilles)
        self.ctrl_cp_arrivee.ctrlVille = self.ctrl_ville_arrivee
        self.bouton_options_arrivee = wx.Button(self, -1, "...", size=(20, 20))
        
        self.label_distance = wx.StaticText(self, -1, _(u"Distance :"), size=(95, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_distance = wx.TextCtrl(self, -1, "0", size=(55, -1))
        self.label_km = wx.StaticText(self, -1, _(u"Km  (Aller simple)"))
        
        
        self.label_aller_retour = wx.StaticText(self, -1, _(u"Aller/retour :"), size=(95, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_aller_retour = wx.CheckBox(self, -1, u"")
        
        ##############################################################
        # Pour désactiver l'autocomplete du controle VILLE qui ne fonctionne pas sous Linux
        if "linux" in sys.platform :
            self.ctrl_ville_depart.Enable(False)
            self.ctrl_ville_arrivee.Enable(False)       
        
        ##############################################################
        
        # Remboursement
        self.staticbox_remboursement = wx.StaticBox(self, -1, _(u"Remboursement"))
        
        self.label_tarif = wx.StaticText(self, -1, _(u"Tarif du Km :"), size=(95, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_tarif = wx.TextCtrl(self, -1, "0.00", size=(55, -1))
        self.label_euro_tarif = wx.StaticText(self, -1, u"€")
        
        self.label_montant = wx.StaticText(self, -1, _(u"Montant du rmbst :"), size=(110, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_montant = wx.StaticText(self, -1, u"0.00 €")
        font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.ctrl_montant.SetFont(font)
        
        self.label_remboursement = wx.StaticText(self, -1, _(u"Remboursement :"), size=(95, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_remboursement = wx.StaticText(self, -1, _(u"Aucun remboursement."))

        
        # Boutons
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        
         # IDpersonne :
        if self.IDpersonne != None :
            self.SetPersonne(self.IDpersonne)
        # Si c'est une modification :
        if self.IDdeplacement != None :
            self.SetTitle(_(u"Modification d'un déplacement"))
            self.Importation()
        else:
            self.ImportDernierTarif()
        # Cache le controle utilisateur :
        if self.IDpersonne != None :
            self.label_utilisateur.Show(False)
            self.ctrl_utilisateur.Show(False)
            self.SetSize((-1, 430))
        
        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOptionsDepart, self.bouton_options_depart)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOptionsArrivee, self.bouton_options_arrivee)
        self.Bind(wx.EVT_CHECKBOX, self.OnAllerRetour, self.ctrl_aller_retour)
        self.ctrl_distance.Bind(wx.EVT_KILL_FOCUS, self.distance_EvtKillFocus)
        self.ctrl_tarif.Bind(wx.EVT_KILL_FOCUS, self.tarif_EvtKillFocus)

        

    def __set_properties(self):
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler la saisie")))
        self.ctrl_date.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici la date du déplacement")))
        self.ctrl_utilisateur.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici l'utilisateur pour ce déplacement")))
        self.ctrl_objet.SetToolTip(wx.ToolTip(_(u"Saisissez ici l'objet du déplacement. Ex : réunion, formation, etc...")))
        self.ctrl_cp_depart.SetToolTip(wx.ToolTip(_(u"Saisissez ici le code postal de la ville de départ")))
        self.ctrl_ville_depart.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom de la ville de départ")))
        self.ctrl_cp_arrivee.SetToolTip(wx.ToolTip(_(u"Saisissez ici le code postal de la ville d'arrivée")))
        self.ctrl_ville_arrivee.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom de la ville d'arrivée")))
        self.ctrl_distance.SetToolTip(wx.ToolTip(_(u"Saisissez ici la distance en Km entre les 2 villes sélectionnées.\nSi Teamworks la connait, il l'indiquera automatiquement.")))
        self.ctrl_aller_retour.SetToolTip(wx.ToolTip(_(u"Cochez cette case si le déplacement a fait l'objet d'un aller/retour.\nLa distance sera ainsi doublée.")))
        self.ctrl_tarif.SetToolTip(wx.ToolTip(_(u"Saisissez ici le montant du tarif du Km pour permettre calculer le montant du remboursement pour ce déplacement.")))
        self.bouton_options_depart.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour rechercher une ville ou pour saisir manuellement une ville non présente dans la base de données du logiciel")))
        self.bouton_options_arrivee.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour rechercher une ville ou pour saisir manuellement une ville non présente dans la base de données du logiciel")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Généralités
        sizerStaticBox_generalites = wx.StaticBoxSizer(self.staticbox_generalites, wx.HORIZONTAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        
        grid_sizer_generalites.Add(self.label_date, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_generalites.Add(self.ctrl_date, 0, wx.ALL, 0)
        grid_sizer_generalites.Add(self.label_utilisateur, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_generalites.Add(self.ctrl_utilisateur, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_generalites.Add(self.label_objet, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_generalites.Add(self.ctrl_objet, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_generalites.AddGrowableCol(1)
        sizerStaticBox_generalites.Add(grid_sizer_generalites, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(sizerStaticBox_generalites, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 10)
        
        # Trajet
        sizerStaticBox_trajet = wx.StaticBoxSizer(self.staticbox_trajet, wx.HORIZONTAL)
        grid_sizer_trajet = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        
        grid_sizer_trajet.Add(self.label_depart, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        sizer_depart = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        sizer_depart.Add(self.ctrl_cp_depart, 1, wx.EXPAND|wx.ALL, 0)
        sizer_depart.Add(self.ctrl_ville_depart, 1, wx.EXPAND|wx.ALL, 0)
        sizer_depart.Add(self.bouton_options_depart, 1, wx.EXPAND|wx.ALL, 0)
        sizer_depart.AddGrowableCol(1)
        grid_sizer_trajet.Add(sizer_depart, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_trajet.Add(self.label_arrivee, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        sizer_arrivee = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        sizer_arrivee.Add(self.ctrl_cp_arrivee, 1, wx.EXPAND|wx.ALL, 0)
        sizer_arrivee.Add(self.ctrl_ville_arrivee, 1, wx.EXPAND|wx.ALL, 0)
        sizer_arrivee.Add(self.bouton_options_arrivee, 1, wx.EXPAND|wx.ALL, 0)
        sizer_arrivee.AddGrowableCol(1)
        grid_sizer_trajet.Add(sizer_arrivee, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_trajet.Add(self.label_distance, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        sizer_distance = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        sizer_distance.Add(self.ctrl_distance, 1, wx.EXPAND|wx.ALL, 0)
        sizer_distance.Add(self.label_km, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_trajet.Add(sizer_distance, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_trajet.Add( self.label_aller_retour, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        sizer_ar = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        sizer_ar.Add(self.ctrl_aller_retour, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_trajet.Add(sizer_ar, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_trajet.AddGrowableCol(1)
        sizerStaticBox_trajet.Add(grid_sizer_trajet, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(sizerStaticBox_trajet, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        
        # Remboursement
        sizerStaticBox_rbmt = wx.StaticBoxSizer(self.staticbox_remboursement, wx.HORIZONTAL)
        grid_sizer_rbmt = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        
        grid_sizer_rbmt.Add( self.label_tarif , 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        sizer_rbmt = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        sizer_rbmt.Add(self.ctrl_tarif, 1, wx.EXPAND|wx.ALL, 0)
        sizer_rbmt.Add(self.label_euro_tarif, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        sizer_rbmt.Add(self.label_montant, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        sizer_rbmt.Add(self.ctrl_montant, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_rbmt.Add(sizer_rbmt, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_rbmt.Add(self.label_remboursement, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_rbmt.Add(self.ctrl_remboursement, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_rbmt.AddGrowableCol(1)
        sizerStaticBox_rbmt.Add(grid_sizer_rbmt, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(sizerStaticBox_rbmt, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
                
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
        self.CenterOnScreen()
    
    def ImportDernierTarif(self):
        # Récupération du dernier tarif saisi
        DB = GestionDB.DB()        
        req = """SELECT cp_depart, ville_depart, tarif_km FROM deplacements ORDER BY IDdeplacement DESC LIMIT 1; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : 
            return
        else :
            cp_depart = listeDonnees[0][0]
            ville_depart = listeDonnees[0][1]
            tarif_km = listeDonnees[0][2]
            self.ctrl_cp_depart.autoComplete = False
            self.ctrl_ville_depart.autoComplete = False
            self.ctrl_cp_depart.SetValue(str(cp_depart))
            self.ctrl_ville_depart.SetValue(ville_depart)
            self.ctrl_cp_depart.autoComplete = True
            self.ctrl_ville_depart.autoComplete = True
            self.ctrl_tarif.SetValue(str(tarif_km))
        

    def OnBoutonOptionsDepart(self, event):
        print("options ville depart")

    def OnBoutonOptionsArrivee(self, event):
        print("options ville arrivee")
                
    def ImportationPersonnes(self):
        """ Importation de la liste des personnes """
        # Récupération de la liste des personnes
        DB = GestionDB.DB()        
        req = """SELECT IDpersonne, nom, prenom FROM personnes ORDER BY nom, prenom; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Création de la liste pour le listBox
        self.listePersonnes = []
        self.dictPersonnes = {}
        index = 0
        for IDpersonne, nom, prenom in listeDonnees :
            self.listePersonnes.append(nom + " " + prenom)
            self.dictPersonnes[index] = IDpersonne
            index += 1
            
    def ImportationDistances(self):
        """ Importation de la table des distances """
        DB = GestionDB.DB()        
        req = """SELECT * FROM distances """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.listeDistances = listeDonnees
    
    def Importation(self):
        """ Importation des données si c'est une modification de déplacement """
        # Récupération des données du déplacement
        DB = GestionDB.DB()        
        req = """SELECT * FROM deplacements WHERE IDdeplacement=%d; """ % self.IDdeplacement
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        # Intégration des données dans le formulaire
        self.IDpersonne = listeDonnees[0][1]
        self.SetPersonne(self.IDpersonne)
        date = listeDonnees[0][2]
        self.SetDate(datetime.date(year=int(date[:4]), month=int(date[5:7]), day=int(date[8:10])))
        self.ctrl_objet.SetValue(listeDonnees[0][3])
        self.SetVilleDepart(str(listeDonnees[0][4]), listeDonnees[0][5])
        self.SetVilleArrivee(str(listeDonnees[0][6]), listeDonnees[0][7])
        distance = str(listeDonnees[0][8])
        self.ctrl_distance.SetValue(str(distance))
        if listeDonnees[0][9] == "True" : 
            self.SetAllerRetour(True)
        else:
            self.SetAllerRetour(False)
        self.ctrl_tarif.SetValue(str(listeDonnees[0][10]))
        self.CalcMontantRmbst()
        self.SetRemboursement(listeDonnees[0][11])
    
    def SetRemboursement(self, IDremboursement=None):
        """ Définit le remboursement """
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
            self.ctrl_remboursement.SetLabel("N°" + str(IDremboursement) + " du " + dateRemboursement)
        
    def DateEngFr(self, textDate):
        text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
        return text

    def SetAllerRetour(self, etat=False):
        """ Définit l'aller retour """
        self.ctrl_aller_retour.SetValue(etat)
        if etat == False :
            self.label_km.SetLabel("Km  (Aller simple)")
        else :
            self.label_km.SetLabel("Km  (Aller/retour)")
        
    def OnAllerRetour(self, event):
        if self.ValideControleFloat(self.ctrl_distance) == False : return
        distanceActuelle = float(self.ctrl_distance.GetValue())
        if self.ctrl_aller_retour.GetValue() == False :
            self.label_km.SetLabel("Km  (Aller simple)")
            self.ctrl_distance.SetValue(str(distanceActuelle/2.0))
        else :
            self.label_km.SetLabel("Km  (Aller/retour)")
            self.ctrl_distance.SetValue(str(distanceActuelle*2.0))
        # Recalcule le montant
        self.CalcMontantRmbst()
    
    def CalcMontantRmbst(self):
        if self.ValideControleFloat(self.ctrl_distance) == False : return
        if self.ValideControleFloat(self.ctrl_tarif) == False : return
        distance = decimal.Decimal(self.ctrl_distance.GetValue())
        tarif = decimal.Decimal(self.ctrl_tarif.GetValue())
        montant = distance * tarif
        self.ctrl_montant.SetLabel(u"%.2f €" % montant)
    
    def distance_EvtKillFocus(self, event):
        # Vérifie la validité de la valeur
        if self.ValideControleFloat(self.ctrl_distance) == False : 
            dlg = wx.MessageDialog(self, _(u"La distance saisie n'est pas correcte. \nElle doit être sous la forme '32.50' ou '54' par exemple..."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_distance.SetFocus()
            return
        # Recalcule le montant
        self.CalcMontantRmbst()

    def tarif_EvtKillFocus(self, event):
        # Vérifie la validité de la valeur
        if self.ValideControleFloat(self.ctrl_tarif) == False : 
            dlg = wx.MessageDialog(self, _(u"Le tarif n'est pas valide. \nIl doit être sous la forme '0.32' ou '1.53' par exemple..."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_tarif.SetFocus()
            return
        # Recalcule le montant
        self.CalcMontantRmbst()
        
    def ValideControleFloat(self, controle=None):
        """ Vérifie la validité d'un contrôle de type Float """
        valeur = controle.GetValue()
        # Vérifie que la valeur est bien constituée de chiffres uniquement
        incoherences = ""
        for lettre in valeur :
            if lettre not in "0123456789." : incoherences += "'"+ lettre + "', "
        if len(incoherences) != 0 :
            return False
        else :
            try :
                test = float(valeur)
            except :
                controle.SetValue("0.0")
                # Recalcule le montant
                self.CalcMontantRmbst()
                return False
            return True
            
                
    def MajDistance(self):
        """ Met à jour le Contrôle Distance en fonction des villes saisies """
        depart = (self.ctrl_cp_depart.GetValue(), self.ctrl_ville_depart.GetValue())
        arrivee = (self.ctrl_cp_arrivee.GetValue(), self.ctrl_ville_arrivee.GetValue())
        # Recherche une distance dans la base de données des distances
        for IDdistance, cp_depart, ville_depart, cp_arrivee, ville_arrivee, distance in self.listeDistances :
            depart_temp = (str(cp_depart), ville_depart)
            arrivee_temp = (str(cp_arrivee), ville_arrivee)
            if (depart == depart_temp and arrivee == arrivee_temp) or (depart == arrivee_temp and arrivee == depart_temp) :
                if self.ctrl_aller_retour.GetValue() == True :
                    self.ctrl_distance.SetValue(str(distance*2.0))
                else :
                    self.ctrl_distance.SetValue(str(distance *1.0))
                break    
        # MAJ du montant total
        self.CalcMontantRmbst()
        
    def SetVilleDepart(self, cp=None, ville=None):
        """ Ecrit une ville dans le contrôle ville de départ """
        if cp != None :
            self.ctrl_cp_depart.autoComplete = False
            self.ctrl_cp_depart.SetValue(cp)
            self.ctrl_cp_depart.autoComplete = True
        if ville != None :
            self.ctrl_ville_depart.autoComplete = False
            self.ctrl_ville_depart.SetValue(ville.upper())
            self.ctrl_ville_depart.autoComplete = True
 
    def SetVilleArrivee(self, cp=None, ville=None):
        """ Ecrit une ville dans le contrôle ville de départ """
        if cp != None :
            self.ctrl_cp_arrivee.autoComplete = False
            self.ctrl_cp_arrivee.SetValue(cp)
            self.ctrl_cp_arrivee.autoComplete = True
        if ville != None :
            self.ctrl_ville_arrivee.autoComplete = False
            self.ctrl_ville_arrivee.SetValue(ville.upper())
            self.ctrl_ville_arrivee.autoComplete = True
    
    def SetPersonne(self, IDpersonne=None):
        # Recherche de l'index dans le dictPersonnes
        for index, IDpers in self.dictPersonnes.items() :
            if IDpersonne == IDpers :
                self.ctrl_utilisateur.Select(index)
                break
            
    def SetDate(self, date):
        """ Saisi une date au format datetime dans le datepicker """
        self.SetDatePicker(self.ctrl_date, date)
               
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

    def OnBoutonAide(self, event):
        """ Aide """
        FonctionsPerso.Aide(44)
        
    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        
        # Vérifie contrôle Utilisateur
        valeur = self.ctrl_utilisateur.GetValue()
        if valeur == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un utilisateur."), "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_utilisateur.SetFocus()
            return
        
        # Vérifie contrôle Objet
        valeur = self.ctrl_objet.GetValue()
        if valeur == "" :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez pas saisi d'objet pour ce déplacement. \n\nVoulez-vous quand même valider ce déplacement ?\n(Cliquez sur 'Non' ou 'Annuler' pour modifier maintenant l'objet)"), _(u"Erreur de saisie"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            if reponse == wx.ID_NO or reponse == wx.ID_CANCEL:
                dlg.Destroy()
                self.ctrl_objet.SetFocus()
                return
            else: dlg.Destroy()
        
        # Vérifie contrôle cp départ
        valeur = self.ctrl_cp_depart.GetValue()
        if valeur == "" or valeur == "     " :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un code postal pour la ville de départ."), "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_cp_depart.SetFocus()
            return
        
        # Vérifie contrôle ville départ
        valeur = self.ctrl_ville_depart.GetValue()
        if valeur == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom de ville de départ."), "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_ville_depart.SetFocus()
            return
        
        # Vérifie contrôle cp arrivée
        valeur = self.ctrl_cp_arrivee.GetValue()
        if valeur == "" or valeur == "     " :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un code postal pour la ville d'arrivée."), "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_cp_arrivee.SetFocus()
            return
        
        # Vérifie contrôle ville arrivée
        valeur = self.ctrl_ville_arrivee.GetValue()
        if valeur == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom de ville d'arrivée"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_ville_arrivee.SetFocus()
            return
        
        # Vérifie contrôle distance
        valeur = self.ctrl_distance.GetValue()
        if valeur == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une distance en Km pour le trajet."), "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_distance.SetFocus()
            return
        
        if self.ValideControleFloat(self.ctrl_distance) == False : 
            dlg = wx.MessageDialog(self, _(u"La distance saisie n'est pas correcte. \nElle doit être sous la forme '32.50' ou '54' par exemple..."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_distance.SetFocus()
            return
        
        if float(valeur) == 0 :
            dlg = wx.MessageDialog(self, _(u"La distance est de 0 Km. \n\nVoulez-vous quand même valider ce déplacement ?\n(Cliquez sur 'Non' ou 'Annuler' pour modifier maintenant la distance)"), _(u"Erreur de saisie"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            if reponse == wx.ID_NO or reponse == wx.ID_CANCEL:
                dlg.Destroy()
                self.ctrl_distance.SetFocus()
                return
            else: dlg.Destroy()
        
        # Vérifie contrôle tarif
        valeur = self.ctrl_tarif.GetValue()
        if valeur == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir la valeur du tarif du Km en euros."), "Erreur", wx.OK | wx.ICON_EXCLAMATION)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_tarif.SetFocus()
            return
        
        if self.ValideControleFloat(self.ctrl_tarif) == False : 
            dlg = wx.MessageDialog(self, _(u"Le tarif n'est pas valide. \nIl doit être sous la forme '0.32' ou '1.53' par exemple..."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_tarif.SetFocus()
            return
        
        if float(valeur) == 0 :
            dlg = wx.MessageDialog(self, _(u"Le tarif du Km est de 0 €. \n\nVoulez-vous quand même valider ce déplacement ?\n(Cliquez sur 'Non' ou 'Annuler' pour modifier maintenant ce tarif)"), _(u"Erreur de saisie"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            if reponse == wx.ID_NO or reponse == wx.ID_CANCEL:
                dlg.Destroy()
                self.ctrl_distance.SetFocus()
                return
            else: dlg.Destroy()
        
        # Sauvegarde
        self.SauvegardeDeplacement()
        
        # Sauvegarde les Distances
        self.SauvegardeDistance()

        # Ferme la boîte de dialogue
        self.EndModal(wx.ID_OK)        
        
        
    def SauvegardeDeplacement(self):
        """ Sauvegarde des données """
        # Récupération des valeurs saisies
        date = str(self.GetDatePickerValue(self.ctrl_date))
        IDpersonne = self.dictPersonnes[self.ctrl_utilisateur.GetCurrentSelection()]
        objet = self.ctrl_objet.GetValue()
        cp_depart = self.ctrl_cp_depart.GetValue()
        ville_depart = self.ctrl_ville_depart.GetValue()
        cp_arrivee = self.ctrl_cp_arrivee.GetValue()
        ville_arrivee = self.ctrl_ville_arrivee.GetValue()
        distance = float(self.ctrl_distance.GetValue())
        aller_retour = str(self.ctrl_aller_retour.GetValue())
        tarif_km = float(self.ctrl_tarif.GetValue())
        
        DB = GestionDB.DB()
        # Création de la liste des données
        listeDonnees = [    ("date",   date),  
                                    ("IDpersonne",    IDpersonne),
                                    ("objet",    objet),
                                    ("cp_depart",    cp_depart), 
                                    ("ville_depart",    ville_depart),
                                    ("cp_arrivee",    cp_arrivee), 
                                    ("ville_arrivee",    ville_arrivee), 
                                    ("distance",    distance), 
                                    ("aller_retour",    aller_retour), 
                                    ("tarif_km",    tarif_km),
                                    ("IDremboursement",    0), 
                                    ]
        if self.IDdeplacement == None :
            # Enregistrement d'un nouveau déplacement
            newID = DB.ReqInsert("deplacements", listeDonnees)
            ID = newID
        else:
            # Modification du déplacement
            DB.ReqMAJ("deplacements", listeDonnees, "IDdeplacement", self.IDdeplacement)
            ID = self.IDdeplacement
        DB.Commit()
        DB.Close()
        return ID
        
    def SauvegardeDistance(self):
        """ Sauvegarde la distance dans la base de données """
        # Recherche dans la base si la distance existe
        depart = (self.ctrl_cp_depart.GetValue(), self.ctrl_ville_depart.GetValue())
        arrivee = (self.ctrl_cp_arrivee.GetValue(), self.ctrl_ville_arrivee.GetValue())
        distanceExiste = False
        distanceValeur = 0
        distanceID = None
        for IDdistance, cp_depart, ville_depart, cp_arrivee, ville_arrivee, distance in self.listeDistances :
            depart_temp = (str(cp_depart), ville_depart)
            arrivee_temp = (str(cp_arrivee), ville_arrivee)
            if (depart == depart_temp and arrivee == arrivee_temp) or (depart == arrivee_temp and arrivee == depart_temp) :
                distanceExiste = True
                distanceValeur = distance
                distanceID = IDdistance
                break    
        
        # Récupération des données
        cp_depart = int(self.ctrl_cp_depart.GetValue())
        ville_depart = self.ctrl_ville_depart.GetValue()
        cp_arrivee = int(self.ctrl_cp_arrivee.GetValue())
        ville_arrivee = self.ctrl_ville_arrivee.GetValue()
        distance = float(self.ctrl_distance.GetValue())
        aller_retour = self.ctrl_aller_retour.GetValue()
        if aller_retour == True :
            distance = distance/2
        
        DB = GestionDB.DB()
        # Création de la liste des données
        listeDonnees = [    ("cp_depart",   cp_depart),  
                                    ("ville_depart",    ville_depart),
                                    ("cp_arrivee",    cp_arrivee),
                                    ("ville_arrivee",    ville_arrivee), 
                                    ("distance",    distance),
                                    ]
        if distanceExiste == False :
            # Enregistrement d'une nouvelle distance
            newID = DB.ReqInsert("distances", listeDonnees)
        else:
            # Modification de la distance
            DB.ReqMAJ("distances", listeDonnees, "IDdistance", distanceID)
        DB.Commit()
        DB.Close()
            
            





class AdvancedComboBox(wx.ComboBox) :
    """ Crée un comboBox avec auto-complete limité à la liste donnée """
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
            event.Skip()
    
    def EvtKillFocus(self, event):
        # Si la valeur n'est pas correcte dans le champ, remet la valeur précédente
        if self.GetValue() not in self.choices and self.GetValue() != u"" :
            self.Undo()
        # Fait la sélection dans la liste
        if self.GetValue() in self.choices :
            self.SetStringSelection(self.GetValue())
        event.Skip()
        




# -----------------------------------------------------------------------------------------------------------------------------------


class TextCtrlCp(masked.TextCtrl):
    def __init__(self, parent, id=-1, value=None, ctrlVille=None, listeVilles=None, **par):
        masked.TextCtrl.__init__(self, parent, id, value, **par)
        self.parent = parent
        self.ctrlVille = ctrlVille
        self.listeVilles = listeVilles
        self.autoComplete = True
        
        # Binds
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

    def OnKillFocus(self, event):
        """ Quand le contrôle Code perd le focus """
        if self.autoComplete == False :
            return
        textCode = self.GetValue()
        # On vérifie que la ville n'est pas déjà dans la case ville
        villeSelect = self.ctrlVille.GetValue()
        if villeSelect != '':
            for ville, cp in self.listeVilles:
                if ville == villeSelect and cp == textCode :
                    return
                
        # On recherche si plusieurs villes ont ce même code postal
        ReponsesVilles = []
        for ville, cp in self.listeVilles:
            if cp == textCode :
                ReponsesVilles.append(ville)
        nbreReponses = len(ReponsesVilles)

        # Code postal introuvable
        if nbreReponses == 0:
            if textCode.strip() != '':
                dlg = wx.MessageDialog(self, _(u"Ce code postal n'est pas répertorié dans la base de données. \nVérifiez que vous n'avez pas fait d'erreur de saisie."), "Information", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            return
        
        if nbreReponses == 1:
            resultat = ReponsesVilles[0]
            self.ctrlVille.SetValue(resultat)

        # Fenêtre de choix entre plusieurs codes postau
        if nbreReponses > 1:
            resultat = self.ChoixVilles(textCode, ReponsesVilles)
            if resultat != '':
                self.ctrlVille.SetValue(resultat)

        # Sélection du texte de la case ville pour l'autocomplete
        self.ctrlVille.SetSelection(0, len(resultat))
        
        # MAJ de la distance
        self.parent.MajDistance()
        
        event.Skip()

    def ChoixVilles(self, cp, listeReponses):
        """ Boîte de dialogue pour donner le choix entre plusieurs villes possédant un code postal identique """
        resultat = ""
        titre = _(u"Sélection d'une ville")
        nbreReponses = len(listeReponses)
        listeReponses.sort()
        message = str(nbreReponses) + _(u" villes possèdent le code postal ") + str(cp) + _(u". Double-cliquez sur\nle nom d'une ville pour la sélectionner :")
        dlg = wx.SingleChoiceDialog(self, message, titre, listeReponses, wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            resultat = dlg.GetStringSelection()
        dlg.Destroy()
        return resultat


class TextCtrlVille(wx.TextCtrl):
    def __init__(self, parent, id=-1, value=None, ctrlCp=None, listeVilles=None, listeNomsVilles=None, **par):
        wx.TextCtrl.__init__(self, parent, id, value, **par)
        self.parent = parent
        self.ctrlCp = ctrlCp
        self.listeVilles = listeVilles
        self.listeNomsVilles = listeNomsVilles
        self.ignoreEvtText = False
        self.autoComplete = True
        
        # Binds
        self.Bind(wx.EVT_TEXT, self.OnText)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)


    def OnKillFocus(self, event):
        """ Quand le contrôle ville perd le focus """
        if self.autoComplete == False :
            return
        villeSelect = self.GetValue()
        if villeSelect == '':
            return

        # On recherche le nombre de villes ayant un nom identique
        nbreCodes = self.listeNomsVilles.count(villeSelect)

        if nbreCodes > 1:
            listeCodes = []
            for ville, cp in self.listeVilles :
                if villeSelect == ville:
                    listeCodes.append(cp)
                    
            # Chargement de la fenêtre de choix des codes
            resultat = self.ChoixCodes(villeSelect, listeCodes)
            if resultat != '':
                self.ctrlCp.SetValue(resultat)

        # Si la ville saisie n'existe pas
        if nbreCodes == 0:
            dlg = wx.MessageDialog(self, _(u"Cette ville n'est pas répertoriée dans la base de données. \nVérifiez que vous n'avez pas fait d'erreur de saisie."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        
        # MAJ de la distance
        self.parent.MajDistance()
        
        event.Skip()

    def OnChar(self, event):
        if event.GetKeyCode() == 8:
            self.ignoreEvtText = True
        event.Skip()

    def OnText(self, event):
        """ A chaque frappe de texte -> analyse """
        if self.autoComplete == False :
            return
        
        if self.ignoreEvtText:
            self.ignoreEvtText = False
            return
        currentText = event.GetString().upper()
        found = False
        for ville, cp in self.listeVilles :
            if ville.startswith(currentText):
                self.ignoreEvtText = True
                self.SetValue(ville)
                self.SetInsertionPoint(len(currentText))
                self.SetSelection(len(currentText), len(ville))
                self.ctrlCp.SetValue(cp)
                found = True
                break
        
        # MAJ de la distance
        self.parent.MajDistance()
        
        if not found:
            self.ctrlCp.SetValue('')
            event.Skip()

    def ChoixCodes(self, ville, listeReponses):
        """ Boîte de dialogue pour donner le choix entre plusieurs villes possédant le même nom """
        resultat = ""
        titre = _(u"Sélection d'une ville")
        nbreReponses = len(listeReponses)
        listeReponses.sort()
        message = str(nbreReponses) + _(u" villes portent le nom ") + str(ville) + _(u". Double-cliquez sur\nle code postal d'une ville pour la sélectionner :")
        dlg = wx.SingleChoiceDialog(self, message, titre, listeReponses, wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            resultat = dlg.GetStringSelection()
        dlg.Destroy()
        return resultat







if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = SaisieDeplacement(None, IDdeplacement=None, IDpersonne=None)
    frm.ShowModal()
    app.MainLoop()