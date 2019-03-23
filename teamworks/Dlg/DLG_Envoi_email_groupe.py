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
import os
import wx.lib.agw.hyperlink as hl
import GestionDB
from Dlg import DLG_Selection_periode


class MyDialog(wx.Dialog):
    def __init__(self, parent, title=""):
        wx.Dialog.__init__(self, parent, -1, title=title, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.parent = parent
        self.listeAdresses = []
        
        self.label_intro = wx.StaticText(self, -1, _(u"Veuillez sélectionner les destinataires :"))
        
        self.staticbox = wx.StaticBox(self, -1, _(u"Catégorie de destinataires"))
        self.radio_salaries = wx.RadioButton(self, -1, _(u"Salariés"))
        self.radio_candidats = wx.RadioButton(self, -1, _(u"Candidats"))
        
        # CheckListBox
        self.checkListBox = wx.CheckListBox(self,  choices=[], size=(50, 50))
        
        # Hyperlink cocher les présents
        self.hyperlink_presents = self.Build_Hyperlink()
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioCategorie, self.radio_salaries )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioCategorie, self.radio_candidats )
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        self.MAJ_liste()
        
    def __set_properties(self):
        self.SetTitle(_(u"Envoi d'un mail groupé"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip("Cliquez ici pour valider"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip("Cliquez ici pour annuler la saisie"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.SetMinSize((500, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 1, wx.ALL|wx.EXPAND, 10)
        
        static_sizer = wx.StaticBoxSizer(self.staticbox, wx.VERTICAL)
        grid_sizer_categorie = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_categorie.Add(self.radio_salaries, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_categorie.Add(self.radio_candidats, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        static_sizer.Add(grid_sizer_categorie, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(static_sizer, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        grid_sizer_base.Add(self.checkListBox, 1, wx.EXPAND | wx.LEFT|wx.RIGHT|wx.TOP, 10)
        grid_sizer_base.Add(self.hyperlink_presents, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM | wx.ALIGN_RIGHT, 10)
        grid_sizer_base.Add((10, 10), 1, wx.EXPAND | wx.ALL, 0)
        
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()       
    
    def OnRadioCategorie(self, event):
        self.MAJ_liste() 
        self.hyperlink_presents.Enable(self.radio_salaries.GetValue())
        
    def MAJ_liste(self):
        """ Importation de la liste des personnes ou de salariés"""
        if self.radio_salaries.GetValue() == True :
            
            # Récupération de la liste des salariés
            DB = GestionDB.DB()        
            req = """SELECT IDpersonne, nom, prenom FROM personnes ORDER BY nom, prenom; """
            DB.ExecuterReq(req)
            listePersonnes = DB.ResultatReq()
            DB.Close()
            # Récupération des adresses Emails
            DB = GestionDB.DB()        
            req = """SELECT texte, IDpersonne FROM coordonnees WHERE categorie='Email'; """
            DB.ExecuterReq(req)
            listeCoords = DB.ResultatReq()
            DB.Close()
        
        else:
            
            # Récupération de la liste des candidats
            DB = GestionDB.DB()        
            req = """SELECT IDcandidat, nom, prenom FROM candidats ORDER BY nom, prenom; """
            DB.ExecuterReq(req)
            listePersonnes = DB.ResultatReq()
            DB.Close()
            # Récupération des adresses Emails
            DB = GestionDB.DB()        
            req = """SELECT texte, IDcandidat FROM coords_candidats WHERE categorie='Email'; """
            DB.ExecuterReq(req)
            listeCoords = DB.ResultatReq()
            DB.Close()
        
        
        # Création de la liste pour le listBox et du dict de données
        self.listeDonnees = []
        self.dictDonnees = {}
        self.checkListBox.Clear()
        index = 0
        for IDpersonne, nom, prenom in listePersonnes :
            mail = ""
            for texte, IDperso in listeCoords :
                if IDpersonne == IDperso : 
                    mail = texte
                    break
                else:
                    mail = ""
            # Formatage du label
            if mail != "" :
                texteMail = "  > " + mail 
            else:
                texteMail = ""
            label = nom + ", " + prenom + texteMail
            # Creation liste et dict
            self.listeDonnees.append(label)
            self.dictDonnees[index] = (IDpersonne, nom, prenom, mail)
            index += 1
        
        self.checkListBox.SetItems(self.listeDonnees)

    
    def Build_Hyperlink(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self, -1, _(u"Sélectionner les présents sur une période donnée"), URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLACK", "BLACK", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner les personnes présentes sur une période donnée")))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink(self, event):
        """ Sélectionner les personnes présentes sur une période donnée """
        dlg = DLG_Selection_periode.SelectionPeriode(self)
        if dlg.ShowModal() == wx.ID_OK:
            listePersonnesPresentes = dlg.GetPersonnesPresentes()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        # Sélection dans la listBox
        for index, valeurs in self.dictDonnees.items():
            IDpersonne = valeurs[0]
            if IDpersonne in listePersonnesPresentes :
                self.checkListBox.Check(index, True)
            else:
                self.checkListBox.Check(index, False)
        # S'il n'y a aucune personne présente sur la période sélectionnée
        if len(listePersonnesPresentes) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune personne présente sur la période que vous avez sélectionné."), _(u"Erreur de saisie"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Envoyerunmailgroup")

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        if 'phoenix' in wx.PlatformInfo:
            selections = self.checkListBox.GetCheckedItems()
        else:
            selections = self.checkListBox.GetChecked()
        
        # Validation de la sélection
        if len(selections) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez fait aucune sélection"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Création de la liste des adresses mail
        self.listeAdresses = []
        listeAdresses = []
        listeSansAdresses = []
        for index in selections :
            IDpersonne, nom, prenom, mail = self.dictDonnees[index]
            if mail == "" :
                listeSansAdresses.append( prenom + " " + nom )
            else :
                listeAdresses.append(mail)
        
        # Si aucune des personnes sélectionnées n'a d'adresse
        if len(selections) == len(listeSansAdresses) :
            dlg = wx.MessageDialog(self, _(u"Aucune des personnes sélectionnées ne possède d'adresse internet !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Avertit qu'il y a des personnes sans adresse
        if len(listeSansAdresses) != 0 :
            # Création du texte du messageBox
            message = _(u"Parmi les ") + str(len(selections)) + _(u" personnes sélectionnées, ") + str(len(listeSansAdresses)) + _(u" ne possèdent pas d'adresse internet : \n")
            for texteNom in listeSansAdresses :
                message += "\n    - " + texteNom
            message += _(u"\n\nSouhaitez-vous quand même continuer pour les ") + str(len(listeAdresses)) + _(u" personne(s) possédant une adresse ?")
            # Affiche de la messageBox
            dlg = wx.MessageDialog(self, message, _(u"Adresses internet manquantes"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            if reponse == wx.ID_NO or reponse == wx.ID_CANCEL:
                dlg.Destroy()
                return
            else: dlg.Destroy()
        
        self.listeAdresses = listeAdresses
        
        # Ferme la boîte de dialogue
        self.EndModal(wx.ID_OK)  

    def GetAdresses(self):
        return self.listeAdresses


    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyDialog(None, "")
    frame_1.ShowModal()
    app.MainLoop()
