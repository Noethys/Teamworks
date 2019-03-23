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
import wx.lib.masked as masked
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import sys
import datetime
import time
import wx.lib.dialogs


def DatetimeDateEnStr(date):
    """ Transforme un datetime.date en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = ("Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche")
    listeMois = ("janvier", _(u"février"), "mars", "avril", "mai", "juin", "juillet", _(u"août"), "septembre", "octobre", "novembre", _(u"décembre"))
    dateStr = listeJours[date.weekday()] + " " + str(date.day) + " " + listeMois[date.month-1] + " " + str(date.year)
    return dateStr

def StrEnDatetime(texteHeure):
    texteHeure = texteHeure[:5]
    posTemp = texteHeure.index(":")
    heuresTemp = int(texteHeure[:posTemp])
    minutesTemp =  int(texteHeure[posTemp+1:])
    heure = datetime.time(heuresTemp, minutesTemp)
    return heure

def StrEnDatetimeDate(texteDate):
    annee = texteDate[:4]
    mois = texteDate[5:7]
    jour = texteDate[8:10]
    date = datetime.date(int(annee), int(mois), int(jour))
    return date


class Panel(wx.Panel):
    def __init__(self, parent, id=-1, listeDonnees=[], IDmodif=0, mode="planning", panelPlanning=None):
        wx.Panel.__init__(self, parent, id=id, name="panel_saisiePresences", style=wx.TAB_TRAVERSAL)       
        self.parent = parent
        self.mode = mode
        self.panelPlanning = panelPlanning
        
        # Si c'est une modif :
        self.IDmodif = IDmodif
        if self.IDmodif != 0 and mode == "planning" : 
            donneesModif = self.ImportDonneesModif()
            self.donneesModif = donneesModif
            listeDonnees=[(donneesModif[1], donneesModif[2])]
        
        if self.IDmodif != 0 and mode == "modele" : 
            self.listeDonnees = listeDonnees

        # Création du dictionnaire de données (date, IDpersonne)
        if mode == "planning" :
            self.CreationDictDonnees(listeDonnees)

        self.panel_base = wx.Panel(self, -1)
        self.sizer_heures_staticbox = wx.StaticBox(self.panel_base, -1, _(u"Horaires"))
        self.sizer_intitule_staticbox = wx.StaticBox(self.panel_base, -1, _(u"Légende"))
        self.sizer_droit_staticbox = wx.StaticBox(self.panel_base, -1, _(u"Catégorie"))
        self.sizer_donnees_staticbox = wx.StaticBox(self.panel_base, -1, _(u"Dates et personnes sélectionnées"))

        self.listCtrl_donnees = ListCtrl_donnees(self.panel_base)
        self.listCtrl_donnees.SetMinSize((20, 80))
        if self.IDmodif != 0 : self.listCtrl_donnees.Enable(False)
        
        self.label_heure_debut = wx.StaticText(self.panel_base, -1, _(u"Début :"))
        self.text_heure_debut = masked.TextCtrl(self.panel_base, -1, "", style=wx.TE_CENTRE, mask = "##:##", validRegex   = "[0-2][0-9]:[0-5][0-9]")
        self.label_heure_fin = wx.StaticText(self.panel_base, -1, _(u"Fin :"))
        self.text_heure_fin = masked.TextCtrl(self.panel_base, -1, "", style=wx.TE_CENTRE, mask = "##:##", validRegex   = "[0-2][0-9]:[0-5][0-9]")

        self.text_intitule = wx.TextCtrl(self.panel_base, -1, "", style=wx.TE_MULTILINE)
       
        self.treeCtrl_categories = TreeCtrlCategories(self.panel_base)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.dictPersonnes = self.ImportPersonnes()
        
        if self.IDmodif != 0 and mode == "planning": 
            self.text_heure_debut.SetValue(str(donneesModif[3])[:5])
            self.text_heure_fin.SetValue(str(donneesModif[4])[:5])
            self.text_intitule.SetValue(donneesModif[6])
        
        if self.IDmodif != 0 and mode == "modele": 
            self.text_heure_debut.SetValue(listeDonnees[5])
            self.text_heure_fin.SetValue(listeDonnees[6])
            self.text_intitule.SetValue(listeDonnees[8])
        
        self.__set_properties()
        self.__do_layout()

        self.text_heure_debut.SetFocus()

        self.Bind(wx.EVT_TEXT, self.OnTextHeureDebutText, self.text_heure_debut)
        self.Bind(wx.EVT_TEXT, self.OnTextHeureFinText, self.text_heure_fin)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def __set_properties(self):
        self.treeCtrl_categories.SetMinSize((200, 180))
        self.text_heure_debut.SetMinSize((65, -1))
        self.text_heure_debut.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.text_heure_debut.SetCtrlParameters(invalidBackgroundColour = "PINK")
        self.text_heure_fin.SetMinSize((65, -1))
        self.text_heure_fin.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.text_heure_fin.SetCtrlParameters(invalidBackgroundColour = "PINK")
        self.text_intitule.SetToolTip(wx.ToolTip(_(u"Saisissez ici une légende (optionnel)")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Bouton Aide")))
        self.treeCtrl_categories.SetToolTip(wx.ToolTip(_(u"Sélectionnez ici une catégorie")))
        self.listCtrl_donnees.SetToolTip(wx.ToolTip(_(u"Vous pouvez désélectionner ici une ou plusieurs tâches\nque vous ne souhaitez finalement pas enregistrer.")))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Bouton Ok")))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Bouton annuler")))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        sizer_droit = wx.StaticBoxSizer(self.sizer_droit_staticbox, wx.VERTICAL)
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        sizer_intitule = wx.StaticBoxSizer(self.sizer_intitule_staticbox, wx.VERTICAL)
        sizer_heures = wx.StaticBoxSizer(self.sizer_heures_staticbox, wx.VERTICAL)
        grid_sizer_heures = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        sizer_1 = wx.StaticBoxSizer(self.sizer_donnees_staticbox, wx.VERTICAL)
        sizer_1.Add(self.listCtrl_donnees, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(sizer_1, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_heures.Add(self.label_heure_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_heures.Add(self.text_heure_debut, 0, wx.EXPAND, 0)
        grid_sizer_heures.Add(self.label_heure_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_heures.Add(self.text_heure_fin, 0, wx.EXPAND, 0)
        grid_sizer_heures.AddGrowableCol(1)
        sizer_heures.Add(grid_sizer_heures, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(sizer_heures, 1, wx.EXPAND, 0)
        sizer_intitule.Add(self.text_intitule, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(sizer_intitule, 1, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(1)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        sizer_droit.Add(self.treeCtrl_categories, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_contenu.Add(sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((15, 15), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.Centre()
        self.sizer_1 = sizer_1
        self.grid_sizer_base = grid_sizer_base


    def CreationDictDonnees(self, listeDonnees=[]):
        # Création du dictionnaire de données (date, IDpersonne)
        self.dictDonnees = {}
        ID = 1
        for IDpersonne, date in listeDonnees :
            self.dictDonnees[ID] = [IDpersonne, date, True] # True pour dire que à sélectionner
            ID += 1
                
    def Fermer(self):
        if self.parent.GetName() == "panel_saisiePresences_FicheInd" :
            # Si appellée à partir de la fiche individuelle
            self.parent.GetParent().Fermer()
        else:
            # Sinon...
            self.parent.Fermer()
        
    def OnClose(self, event):
        self.Fermer()
        event.Skip()
        
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Saisirunetcheunique")

    def OnBoutonAnnuler(self, event):
        self.Fermer()
        event.Skip()

    def OnBoutonOk(self, event):
        
        # Validation des données
        validation = self.ValidationDonnees()
        if validation == False : return
        
        # Si tout est valide : on sauvegarde
        if self.mode == "planning" :
            if self.IDmodif == 0 :
                etat = self.SauvegardeNouveau()
            else:
                etat = self.SauvegardeModif()
            if etat == "PasOk" : return
            
            # MAJ de la page Présences de la fiche individuelle si elle est ouverte
            if self.panelPlanning != None : 
                self.panelPlanning.MAJafterModif()
            else :
                if self.GetGrandParent().GetName() == "panel_pagePresences" :
                    self.GetGrandParent().MAJpanel()
                # MAJ du DCplanning
                if self.GetGrandParent().GetName() == "panel_widgetPlanning" :
                    self.GetGrandParent().MAJafterModif()
                # Si appellée à partir de la fiche individuelle
                if self.GetGrandParent().GetName() == "frm_saisiePresences_FicheInd" :
                    print("ok")
        
        if self.mode == "modele" :
            etat = self.SauvegardeModele()
            if etat == "PasOk" : return
             
        # Fermeture de la fenêtre
        self.Fermer()
        event.Skip()
        
        
    def ValidationDonnees(self):
        """ Validation des données """
        
        # Vérifie qu'au moins une tâche a été sélectionnée dans le listeCtrl
        if self.mode == "planning" :
            selection = False
            for key, valeurs in self.dictDonnees.items() :
                if valeurs[2] == True : selection = True
            if selection == False:
                message = _(u"Vous devez sélectionner au moins une date.")
                wx.MessageBox(message, "Erreur de saisie")
                return False

        # Vérifie la validité des heures
        heureDebut = self.text_heure_debut.GetValue()
        heureFin = self.text_heure_fin.GetValue()
        if heureDebut == "  :  " :
            message = _(u"Vous devez saisir une heure de début.")
            wx.MessageBox(message, "Erreur de saisie")
            self.text_heure_debut.SetFocus()
            return False
        if heureDebut[3:] >= "60" or heureDebut[3] == " " or heureDebut[4] == " ":
            message = _(u"L'heure de début n'est pas valide.")
            wx.MessageBox(message, "Erreur de saisie")
            self.text_heure_debut.SetFocus()
            return False
        if heureDebut[4] != "5" and heureDebut[4] != "0" :
            message = _(u"Vous ne pouvez saisir qu'un horaire terminant par 0 ou 5. \nEx.: 10:05 ou 10:10 ou 10:15, etc... mais pas 10:02 !")
            wx.MessageBox(message, "Erreur de saisie")
            self.text_heure_debut.SetFocus()
            return False
        if heureFin == "  :  " :
            message = _(u"Vous devez saisir une heure de fin.")
            wx.MessageBox(message, "Erreur de saisie")
            self.text_heure_fin.SetFocus()
            return False
        if heureDebut < "00:00" or heureDebut > "24:00" :
            message = _(u"L'heure de début n'est pas valide")
            wx.MessageBox(message, "Erreur de saisie")
            self.text_heure_debut.SetFocus()
            return False
        if heureFin[3:] >= "60" or heureFin[3] == " " or heureFin[4] == " ":
            message = _(u"L'heure de fin n'est pas valide.")
            wx.MessageBox(message, "Erreur de saisie")
            self.text_heure_fin.SetFocus()
            return False
        if heureFin < "00:00" or heureFin > "24:00" :
            message = _(u"L'heure de fin n'est pas valide")
            wx.MessageBox(message, "Erreur de saisie")
            self.text_heure_fin.SetFocus()
            return False
        if heureFin[4] != "5" and heureFin[4] != "0" :
            message = _(u"Vous ne pouvez saisir qu'un horaire terminant par 0 ou 5. \nEx.: 10:05 ou 10:10 ou 10:15, etc... mais pas 10:02 !")
            wx.MessageBox(message, "Erreur de saisie")
            self.text_heure_fin.SetFocus()
            return False
        if heureDebut > heureFin :
            message = _(u"L'heure de fin doit être supérieure à l'heure de début !")
            wx.MessageBox(message, "Erreur de saisie")
            self.text_heure_debut.SetFocus()
            return False

        # Vérifie qu'il y a un delta de 15min entre l'heure de début et de fin
        HMin = datetime.timedelta(hours=int(heureDebut[:2]), minutes=int(heureDebut[3:]))
        HMax = datetime.timedelta(hours=int(heureFin[:2]), minutes=int(heureFin[3:]))
        delta = ((HMax - HMin).seconds)//60.0
        if delta < 15 :
            message = _(u"La durée de la tâche doit être au minimum de 15 minutes !")
            wx.MessageBox(message, "Erreur de saisie")
            self.text_heure_debut.SetFocus()
            return False

        # Vérifie qu'une catégorie a été sélectionnée
        IDcategorie = self.treeCtrl_categories.selection
        if IDcategorie == None :
            message = _(u"Vous devez sélectionner une catégorie dans la liste proposée.")
            wx.MessageBox(message, "Erreur de saisie")
            return False

        # Vérifie la taille de l'intitulé
        intitule = self.text_intitule.GetValue()
        if len(intitule) > 200:
            message = _(u"Vous devez écrire une légende plus courte !")
            wx.MessageBox(message, "Erreur de saisie")
            self.text_intitule.SetFocus()
            return False
        
        return True
        
    def OnTextHeureDebutText(self, event):
        texte = event.GetString()
        controle = self.text_heure_debut

        validation = True
        texteBrut = controle.GetPlainValue()

        if texteBrut == "":
            validation = False

        # Vérifie chaque chiffre
        for chiffre in texteBrut:
            if chiffre != " ":
                if not (0 <= int(chiffre) <=9):
                    validation = False
            else:
                validation = False

        # Vérification de l'ensemble de la date
        if validation == True and len(texteBrut)==4:
            if not (0<= int(texteBrut[:2]) <=24):
                validation = False
            if not (0<= int(texteBrut[2:]) <=59):
                validation = False

            # Vérifie que heure_Fin est supérieure à Heure_Debut    
            if self.text_heure_debut.GetPlainValue() != "" and self.text_heure_fin.GetPlainValue() != "":
                delta = int(self.text_heure_fin.GetPlainValue()) - int(self.text_heure_debut.GetPlainValue())
                if delta < 1:
                    validation = False
                    dlg = wx.MessageDialog(self, _(u"L'heure de fin doit être supérieure à l'heure de début !"), "Information", wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
        
        # Si l'heure est valide, on passe à DATE_FIN
        if len(texteBrut)==4 and validation == True:
            self.text_heure_fin.SetFocus()

    def OnTextHeureFinText(self, event):
        texte = event.GetString()
        controle = self.text_heure_fin

        validation = True
        texteBrut = controle.GetPlainValue()

        if texteBrut == "":
            validation = False

        # Vérifie chaque chiffre
        for chiffre in texteBrut:
            if chiffre != " ":
                if not (0 <= int(chiffre) <=9):
                    validation = False
            else:
                validation = False

        # Vérification de l'ensemble de la date
        if validation == True and len(texteBrut)==4:
            if not (0<= int(texteBrut[:2]) <=24):
                validation = False
            if not (0<= int(texteBrut[2:]) <=59):
                validation = False
                
            # Vérifie que heure_Fin est supérieure à Heure_Debut    
            if self.text_heure_debut.GetPlainValue() != "" and self.text_heure_fin.GetPlainValue() != "":
                delta = int(self.text_heure_fin.GetPlainValue()) - int(self.text_heure_debut.GetPlainValue())
                if delta < 1:
                    validation = False
                    dlg = wx.MessageDialog(self, _(u"L'heure de fin doit être supérieure à l'heure de début !"), "Information", wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                
        # Si l'heure est valide, on passe à DATE_FIN
        if len(texteBrut)==4 and validation == True:
            self.text_intitule.SetFocus()


    def SauvegardeModif(self):
        """ Sauvegarde des données modifiées dans la base de données """

        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        # Création de la liste des données        
        IDpersonne = self.donneesModif[1]
        date = self.donneesModif[2]
        heureDebut = self.text_heure_debut.GetValue()
        heureFin = self.text_heure_fin.GetValue()
        IDcategorie = self.treeCtrl_categories.selection
        intitule = self.text_intitule.GetValue()
                
        listeDonnees = [      ("heure_debut",     heureDebut),
                                            ("heure_fin",           heureFin),
                                            ("IDcategorie",         IDcategorie),
                                            ("intitule",                   intitule),
                        ]
        
        # Vérifie qu'aucune tâche n'existe déjà à ce moment dans la base de données
        req = """
        SELECT IDpresence, date, heure_debut, heure_fin
        FROM presences
        WHERE (date='%s' AND IDpersonne=%d)  AND
        (heure_debut<'%s' And heure_fin>'%s');
        """ % (str(date), IDpersonne, heureFin, heureDebut)
        DB.ExecuterReq(req)
        listePresences = DB.ResultatReq()
        nbreResultats = len(listePresences)
        
        pasChevauchement = True
        if nbreResultats == 1 :
            if listePresences[0][0] != self.IDmodif : pasChevauchement = False
        if nbreResultats > 1 : pasChevauchement = False
        
        if pasChevauchement == False :
            dlg = wx.MessageDialog(self, _(u"Vous avez modifié les horaires de la tâche et elle chevauche désormais une autre tâche sur la même journée pour le même animateur. \n\nVeuillez donc modifier les horaires saisis pour pouvoir l'enregistrer."), "Erreur de saisie", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy() 
            return  "PasOk"      

        # Modification de la présence
        DB.ReqMAJ("presences", listeDonnees, "IDpresence", self.IDmodif)
        DB.Commit()
        DB.Close()
        return self.IDmodif

    def SauvegardeNouveau(self):
        """ Sauvegarde des données dans la base de données """
        # self.dictDonnees[ID] = [IDpersonne, date, True]

        listeExceptions = []

        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        
        for key, valeurs in self.dictDonnees.items() :
            if valeurs[2] == True :

                IDpersonne = valeurs[0]
                date = str(valeurs[1])
                heureDebut = self.text_heure_debut.GetValue()
                heureFin = self.text_heure_fin.GetValue()

                # Vérifie qu'aucune tâche n'existe déjà à ce moment dans la base de données
                req = """
                SELECT IDpresence, date, heure_debut, heure_fin
                FROM presences
                WHERE (date='%s' AND IDpersonne=%d)  AND
                (heure_debut<'%s' And heure_fin>'%s');
                """ % (str(date), IDpersonne, heureFin, heureDebut)
                DB.ExecuterReq(req)
                listePresences = DB.ResultatReq()
                nbreResultats = len(listePresences)
                print(nbreResultats)
                if nbreResultats != 0 :

                    # Un ou des présences existent à ce moment, donc pas d'enregistrement
                    nomPersonne = self.dictPersonnes[IDpersonne][0] + " " + self.dictPersonnes[IDpersonne][1]
                    listeExceptions.append((nomPersonne, DatetimeDateEnStr(valeurs[1])))

                else:

                    # Traitement de l'item s'il a été sélectionné dans le listCtrl
                    listeDonnees = [    ("IDpersonne",      IDpersonne),
                                        ("date",            date),
                                        ("heure_debut",     heureDebut),
                                        ("heure_fin",       heureFin),
                                        ("IDcategorie",     self.treeCtrl_categories.selection),
                                        ("intitule",        self.text_intitule.GetValue()),
                                    ]

                    # Enregistrement dans la base
                    ID = DB.ReqInsert("presences", listeDonnees)
                    DB.Commit()

        # Fermeture de la base de données
        DB.Close()

        # Lecture de la liste des exceptions
        nbreInvalides =len(listeExceptions)
        nbreValides = len(self.dictDonnees) - nbreInvalides
        
        self.Show(False)
        
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
                message += "   > Le " + exception[1] + " pour " + exception[0] + "\n"
            dlg = wx.lib.dialogs.ScrolledMessageDialog(self, message, _(u"Rapport d'erreurs"))
            dlg.ShowModal()

    def SauvegardeModele(self):
        """ Envoie les données au formulaire de saisie des modèles """
        ID = self.IDmodif
        heureDebut = self.text_heure_debut.GetValue()
        heureFin = self.text_heure_fin.GetValue()
        IDcategorie = self.treeCtrl_categories.selection
        intitule = self.text_intitule.GetValue()
        
        if ID != 0 :
            IDmodele = self.listeDonnees[1]
            type = self.listeDonnees[2]
            periode = self.listeDonnees[3]
            jour = self.listeDonnees[4]
        else:
            IDmodele = None
            type = None
            periode = None
            jour = None
        
        # Envoi des données au form de saisie des modèles
        valid = self.GetGrandParent().Sauvegarde((ID, IDmodele, type, periode, jour, heureDebut, heureFin, IDcategorie, intitule))
        if valid == False : 
            dlg = wx.MessageDialog(self, _(u"Les horaires que vous avez saisis chevauchent déjà une autre tâche sur la même journée."), "Erreur de saisie", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy() 
            return "PasOk"       
        return "Ok"       
        
    def ImportPersonnes(self):
        """ Récupération des noms des personnes """
        DB = GestionDB.DB()
        req = "SELECT IDpersonne, nom, prenom FROM personnes"
        DB.ExecuterReq(req)
        listePersonnes = DB.ResultatReq()
        DB.Close()
        # Transformation de la liste en dict
        dictPersonnes = {}
        for item in listePersonnes :
            dictPersonnes[item[0]] = (item[1], item[2])
        # Renvoie le dict
        return dictPersonnes

    def ImportDonneesModif(self):
        """ Récupération des données ur la présence à modifier """
        DB = GestionDB.DB()
        req = "SELECT * FROM presences WHERE IDpresence=%d" % self.IDmodif
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()[0]
        DB.Close()
        
        IDpresence = donnees[0]
        IDpersonne = donnees[1]
        date = StrEnDatetimeDate(donnees[2])
        heureDebut = StrEnDatetime(donnees[3])
        heureFin = StrEnDatetime(donnees[4])
        categorie = donnees[5]
        intitule = donnees[6]
        
        donnees = (IDpresence, IDpersonne, date, heureDebut, heureFin, categorie, intitule)
        return donnees
    
# ---------------------------------------------------------------------------------------------------

class ListCtrl_donnees(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_NO_HEADER|wx.LC_HRULES)
        CheckListCtrlMixin.__init__(self)
        self.parent = parent
        
        if self.parent.GetParent().mode =="modele": 
            return
        
        self.dictDonnees = self.parent.GetParent().dictDonnees
        self.dictPersonnes = self.parent.GetParent().ImportPersonnes()
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

        self.InitColonnes()
        self.Remplissage()

    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)


    # this is called by the base class when an item is checked/unchecked
    def OnCheckItem(self, index, flag):
        data = self.GetItemData(index)
        # MAJ de la liste
        self.MAJ_listeDonnees()

    def MAJ_listeDonnees(self):
        """ Met la liste de sélections à jour """
        nbreItems = 0
        for item in range(self.GetItemCount()):
            ID = self.GetItemData(item)
            if self.IsChecked(item) :
                etat = True
                nbreItems += 1
            else:
                etat = False
            self.dictDonnees[ID][2] = etat
        # Modification du label du sizer
        if nbreItems == 1 : 
            texteLabel = str(nbreItems) + _(u" tâche sera créée")
        else:
            texteLabel = str(nbreItems) + _(u" tâches seront créées")
        self.parent.GetParent().sizer_donnees_staticbox.SetLabel(texteLabel)

    def InitColonnes(self):
        self.InsertColumn(0, "")
        self.InsertColumn(1, "Personne")
        self.InsertColumn(2, "Date")

    def Remplissage(self):
        # Création d'une liste temporaire
        listeDonnees = []
        for ID, valeurs in self.dictDonnees.items() :
            listeDonnees.append((ID, valeurs[0], valeurs[1], valeurs[2]))
        listeDonnees.sort()
        # Remplissage
        for ID, IDpersonne, date, selection in listeDonnees:
            if 'phoenix' in wx.PlatformInfo:
                index = self.InsertItem(six.MAXSIZE, "")
            else:
                index = self.InsertStringItem(six.MAXSIZE, "")
            nomPersonne = self.dictPersonnes[IDpersonne][0] + " " + self.dictPersonnes[IDpersonne][1]
            if 'phoenix' in wx.PlatformInfo:
                self.SetItem(index, 1, nomPersonne)
                self.SetItem(index, 2, "> " + DatetimeDateEnStr(date))
            else:
                self.SetStringItem(index, 1, nomPersonne)
                self.SetStringItem(index, 2, "> " + DatetimeDateEnStr(date))
            self.SetItemData(index, ID)
            self.CheckItem(index)
      
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, wx.LIST_AUTOSIZE)

        


# ----------------------------------------------------------------------------------------------------
# Données Catégories pour remplir le TreeView


# IDcategorie, nom_categorie, IDcategorie_parent, ordre, couleur


class TreeCtrlCategories(wx.TreeCtrl):
    def __init__(self, parent):
        wx.TreeCtrl.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, style=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT)
        # Autres styles possibles = wx.TR_HAS_BUTTONS|wx.TR_EDIT_LABELS| wx.TR_MULTIPLE|wx.TR_HIDE_ROOT
        self.parent = parent

        self.listeCategories = self.Importation()
        self.selection = None

        tailleImages = (16,16)
        il = wx.ImageList(tailleImages[0], tailleImages[1])
        for categorie in self.listeCategories:
            ID = categorie[0]
            couleur = self.FormateCouleur(categorie[4])
            r = couleur[0]
            v = couleur[1]
            b = couleur[2]
            exec("self.img" + str(ID) +  "= il.Add(self.CreationImage(tailleImages, " + str(r) + ", " + str(v) + ", " + str(b) + "))")

        self.SetImageList(il)
        self.il = il

        self.root = self.AddRoot(_(u"Catégories"))
        if 'phoenix' in wx.PlatformInfo:
            self.SetItemData(self.root, None)
        else:
            self.SetPyData(self.root, None)
        self.Remplissage()
        
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded, self)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed, self)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate, self)

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
            bmp.SetRGB((0, 0, 16, 16), 255, 255, 255)
            bmp.SetRGB((6, 4, 8, 8), r, v, b)
        else:
            bmp = wx.EmptyImage(tailleImages[0], tailleImages[1], True)
            bmp.SetRGBRect((0, 0, 16, 16), 255, 255, 255)
            bmp.SetRGBRect((6, 4, 8, 8), r, v, b)
        return bmp.ConvertToBitmap()

    def Remplissage(self):

        self.nbreCategories = len(self.listeCategories)
        if self.nbreCategories == 0:
            return
        self.nbreBranches = 0
        self.Boucle(0, self.root)

    def Boucle(self, IDparent, itemParent):
        """ Boucle de remplissage du TreeCtrl """
        for item in self.listeCategories :
            if item[2] == IDparent:

                # Création de la branche
                newItem = self.AppendItem(itemParent, item[1])
                if 'phoenix' in wx.PlatformInfo:
                    self.SetItemData(newItem, item[0])
                else:
                    self.SetPyData(newItem, item[0])
                exec("self.SetItemImage(newItem, self.img" + str(item[0]) + ", wx.TreeItemIcon_Normal)") 
                self.nbreBranches += 1
                
                # Sélectionne déjà la catégorie si c'est une tâche à modifier
                if self.GetGrandParent().IDmodif != 0 and self.GetGrandParent().mode == "planning" :
                    if self.GetGrandParent().donneesModif[5] == item[0] :
                        self.selection = item[0]
                        self.SelectItem(newItem, True)
                    
                if self.GetGrandParent().IDmodif != 0 and self.GetGrandParent().mode == "modele" :
                    if self.GetGrandParent().listeDonnees[7] == item[0] :
                        self.selection = item[0]
                        self.SelectItem(newItem, True)

                # Recherche des branches enfants
                self.Boucle(item[0], newItem)

    def Importation(self):
        """ Récupération de la liste des catégories dans la base """

        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        req = "SELECT * FROM cat_presences"
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        DB.Close()

        return listeCategories               
            
                
    def OnItemExpanded(self, event):
        item = event.GetItem()
        if item:
            #print ("OnItemExpanded: %s\n" % self.GetItemText(item))
            pass

    def OnItemCollapsed(self, event):
        item = event.GetItem()
        if item:
            #print ("OnItemCollapsed: %s\n" % self.GetItemText(item))
            pass

    def OnSelChanged(self, event):
        self.item = event.GetItem()
        textItem = self.GetItemText(self.item)
        if 'phoenix' in wx.PlatformInfo:
            data = self.GetItemData(self.item)
        else:
            data = self.GetPyData(self.item)
        self.selection = data
        event.Skip()

    def OnActivate(self, event):
        if self.item:
            #print ("OnActivate: %s\n" % self.GetItemText(self.item))
            pass


        
class Dialog(wx.Dialog):
    def __init__(self, parent, listeDonnees=[], IDmodif=0, mode="planning", panelPlanning=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.panelPlanning = panelPlanning
        self.panel = Panel(self, listeDonnees=listeDonnees, IDmodif=IDmodif, mode=mode, panelPlanning=self.panelPlanning)
        
        # Propriétés
        if IDmodif == 0 :
            self.SetTitle(_(u"Saisie d'une tâche"))
        else:
            self.SetTitle(_(u"Modification d'une tâche"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_PNG))
        self.SetIcon(_icon)
        self.SetMinSize((440, 445))
        
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
    listeDonnees = [
            ( 2, datetime.date(2008, 1, 1)),
            ( 2, datetime.date(2008, 1, 15)),
            ]
    dlg = Dialog(None, listeDonnees)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
