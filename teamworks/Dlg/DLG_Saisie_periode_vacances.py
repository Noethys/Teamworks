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
import FonctionsPerso


class MyFrame(wx.Frame):
    def __init__(self, parent, title="" , IDperiode=0):
        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)
        self.parent = parent
        self.panel_base = wx.Panel(self, -1)
        
        self.sizer_periode_staticbox = wx.StaticBox(self.panel_base, -1, _(u"Nom de la période"))
        choices = [_(u"Février"), _(u"Pâques"), _(u"Eté"), _(u"Toussaint"), _(u"Noël")]
        self.label_nom = wx.StaticText(self.panel_base, -1, _(u"Nom :"))
        self.choice_nom = wx.Choice(self.panel_base, -1, choices=choices, size=(100, -1))
        self.label_annee = wx.StaticText(self.panel_base, -1, _(u"Année :"))
        self.text_annee = wx.TextCtrl(self.panel_base, -1, "", style=wx.TE_CENTRE, size=(50, -1))
        
        self.sizer_dates_staticbox = wx.StaticBox(self.panel_base, -1, _(u"Dates de la période"))
        self.label_dateDebut = wx.StaticText(self.panel_base, -1, u"Du")
        self.datepicker_dateDebut = wx.DatePickerCtrl(self.panel_base, -1, style=wx.DP_DROPDOWN)
        self.label_dateFin = wx.StaticText(self.panel_base, -1, _(u"au"))
        self.datepicker_dateFin = wx.DatePickerCtrl(self.panel_base, -1, style=wx.DP_DROPDOWN)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        
        self.IDperiode = IDperiode
        if IDperiode != 0 : 
            self.Importation()

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def __set_properties(self):
        self.SetTitle(_(u"Gestion des périodes de vacances"))
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.choice_nom.SetToolTipString(_(u"Choisissez ici le nom de la période"))
        self.text_annee.SetToolTipString(_(u"Saisissez ici l'année de la période. Ex. : '2008'"))
        self.datepicker_dateDebut.SetToolTipString(_(u"Saisissez ici la date de début de la période"))
        self.datepicker_dateFin.SetToolTipString(_(u"Saisissez ici la date de fin de la période"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler la saisie"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        
        sizer_contenu_1 = wx.StaticBoxSizer(self.sizer_periode_staticbox, wx.VERTICAL)
        grid_sizer_contenu_1 = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_contenu_1.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu_1.Add(self.choice_nom, 0, 0, 0)
        grid_sizer_contenu_1.Add(self.label_annee, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu_1.Add(self.text_annee, 0, 0, 0)
        sizer_contenu_1.Add(grid_sizer_contenu_1, 1, wx.ALL|wx.EXPAND, 10)
        
        sizer_contenu_2 = wx.StaticBoxSizer(self.sizer_dates_staticbox, wx.VERTICAL)
        grid_sizer_contenu_2 = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_contenu_2.Add(self.label_dateDebut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu_2.Add(self.datepicker_dateDebut, 0, 0, 0)
        grid_sizer_contenu_2.Add(self.label_dateFin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu_2.Add(self.datepicker_dateFin, 0, 0, 0)
        sizer_contenu_2.Add(grid_sizer_contenu_2, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(sizer_contenu_1, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_contenu_2, 1, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.Centre()


    def Importation(self):
        DB = GestionDB.DB()
        req = "SELECT * FROM periodes_vacances WHERE IDperiode=%d" % self.IDperiode
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()[0]
        DB.Close()
        if len(donnees) == 0: return
        # Place la valeur dans le controle nom période
        self.SelectChoice(self.choice_nom, donnees[1])
        # Place la valeur dans le controle annee
        self.text_annee.SetValue(str(donnees[2]))
        # Place la date de début dans le cdatePicker 
        jour = int(donnees[3][8:10])
        mois = int(donnees[3][5:7])-1
        annee = int(donnees[3][:4])
        date = wx.DateTime()
        date.Set(jour, mois, annee)
        self.datepicker_dateDebut.SetValue(date)
        # Place la date de fin dans le cdatePicker 
        jour = int(donnees[4][8:10])
        mois = int(donnees[4][5:7])-1
        annee = int(donnees[4][:4])
        date = wx.DateTime()
        date.Set(jour, mois, annee)
        self.datepicker_dateFin.SetValue(date)

    def SelectChoice(self, controle, data):
        nbreItems = controle.GetCount()
        index = 0
        for item in range(nbreItems) :
            if controle.GetString(index) == data :
                controle.SetSelection(index)
                return
            index += 1

    def GetChoiceValue(self, controle):
        selection = controle.GetSelection()
        if selection != -1 : 
            IDselection = controle.GetString(selection)
        else:
            IDselection = None
        return IDselection
    
    def Sauvegarde(self):
        """ Sauvegarde des données dans la base de données """
        
        # Récupération ds valeurs saisies
        varNom = self.GetChoiceValue(self.choice_nom)
        varAnnee = self.text_annee.GetValue()
        varDateDebut = self.datepicker_dateDebut.GetValue()
        varTxtDateDebut = str(datetime.date(varDateDebut.GetYear(), varDateDebut.GetMonth()+1, varDateDebut.GetDay()))
        varDateFin = self.datepicker_dateFin.GetValue()
        varTxtDateFin = str(datetime.date(varDateFin.GetYear(), varDateFin.GetMonth()+1, varDateFin.GetDay()))
        
        DB = GestionDB.DB()
        # Création de la liste des données
        listeDonnees = [    ("nom",   varNom),  
                                    ("annee",    varAnnee), 
                                    ("date_debut",    varTxtDateDebut), 
                                    ("date_fin",    varTxtDateFin), ]
        if self.IDperiode == 0:
            # Enregistrement d'une nouvelle valeur
            newID = DB.ReqInsert("periodes_vacances", listeDonnees)
            ID = newID
        else:
            # Modification des valeurs
            DB.ReqMAJ("periodes_vacances", listeDonnees, "IDperiode", self.IDperiode)
            ID = self.IDperiode
        DB.Commit()
        DB.Close()
        return ID

    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(9)

    def OnBoutonAnnuler(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    def OnBoutonOk(self, event):
        """ Validation des données saisies """

        # Vérifie que des valeurs ont été saisies
        valeur = self.GetChoiceValue(self.choice_nom)
        if valeur == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner un nom de période dans la liste proposée !"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.choice_nom.SetFocus()
            return

        valeur = self.text_annee.GetValue()
        if valeur == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une année valide."), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_annee.SetFocus()
            return
        # Vérifie que la valeur est bien constituée de chiffres uniquement
        incoherences = ""
        for lettre in valeur :
            if lettre not in "0123456789." : incoherences += "'"+ lettre + "', "
        if len(incoherences) != 0 :
            dlg = wx.MessageDialog(self, _(u"L'année que vous avez saisie n'est pas correcte."), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_annee.SetFocus()
            return
        valeur = int(valeur)
        if valeur < 1000 or valeur > 3000 :
            dlg = wx.MessageDialog(self, _(u"L'année que vous avez saisie n'est pas correcte."), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_annee.SetFocus()
            return
        
        date_debut = self.datepicker_dateDebut.GetValue() # self.GetDatePickerValue(self.datepicker_date_debut)
        date_fin = self.datepicker_dateFin.GetValue() # self.GetDatePickerValue(self.datepicker_date_fin)
        # Vérifie que la date de fin est supérieure à la date de début de contrat
        if date_debut > date_fin :
            dlg = wx.MessageDialog(self, _(u"La date de fin de vacances doit être supérieure à la date de début !"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.datepicker_dateFin.SetFocus()
            return
        
        # Sauvegarde
        self.Sauvegarde()
        # MAJ du listCtrl des valeurs de points
        if FonctionsPerso.FrameOuverte("panel_config_periodes_vacs") != None :
            self.GetParent().MAJ_ListCtrl()
            
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    
    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "", IDperiode=1)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
