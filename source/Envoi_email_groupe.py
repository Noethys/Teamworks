#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import FonctionsPerso
import os
import wx.lib.hyperlink as hl
import GestionDB
import Selection_periode


class MyDialog(wx.Dialog):
    def __init__(self, parent, title=""):
        wx.Dialog.__init__(self, parent, -1, title=title, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.parent = parent
        self.listeAdresses = []
        
        self.label_intro = wx.StaticText(self, -1, u"Veuillez s�lectionner les destinataires :")
        
        self.staticbox = wx.StaticBox(self, -1, u"Cat�gorie de destinataires")
        self.radio_salaries = wx.RadioButton(self, -1, u"Salari�s")
        self.radio_candidats = wx.RadioButton(self, -1, u"Candidats")
        
        # CheckListBox
        self.checkListBox = wx.CheckListBox(self,  choices=[], size=(50, 50))
        
        # Hyperlink cocher les pr�sents
        self.hyperlink_presents = self.Build_Hyperlink()
        
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioCategorie, self.radio_salaries )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioCategorie, self.radio_candidats )
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        self.MAJ_liste()
        
    def __set_properties(self):
        self.SetTitle(u"Envoi d'un mail group�")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString("Cliquez ici pour valider")
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString("Cliquez ici pour annuler la saisie")
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
        """ Importation de la liste des personnes ou de salari�s"""
        if self.radio_salaries.GetValue() == True :
            
            # R�cup�ration de la liste des salari�s
            DB = GestionDB.DB()        
            req = """SELECT IDpersonne, nom, prenom FROM personnes ORDER BY nom, prenom; """
            DB.ExecuterReq(req)
            listePersonnes = DB.ResultatReq()
            DB.Close()
            # R�cup�ration des adresses Emails
            DB = GestionDB.DB()        
            req = """SELECT texte, IDpersonne FROM coordonnees WHERE categorie='Email'; """
            DB.ExecuterReq(req)
            listeCoords = DB.ResultatReq()
            DB.Close()
        
        else:
            
            # R�cup�ration de la liste des candidats
            DB = GestionDB.DB()        
            req = """SELECT IDcandidat, nom, prenom FROM candidats ORDER BY nom, prenom; """
            DB.ExecuterReq(req)
            listePersonnes = DB.ResultatReq()
            DB.Close()
            # R�cup�ration des adresses Emails
            DB = GestionDB.DB()        
            req = """SELECT texte, IDcandidat FROM coords_candidats WHERE categorie='Email'; """
            DB.ExecuterReq(req)
            listeCoords = DB.ResultatReq()
            DB.Close()
        
        
        # Cr�ation de la liste pour le listBox et du dict de donn�es
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
        hyper = hl.HyperLinkCtrl(self, -1, u"S�lectionner les pr�sents sur une p�riode donn�e", URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLACK", "BLACK", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(u"Cliquez ici pour s�lectionner les personnes pr�sentes sur une p�riode donn�e"))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink(self, event):
        """ S�lectionner les personnes pr�sentes sur une p�riode donn�e """
        dlg = Selection_periode.SelectionPeriode(self)  
        if dlg.ShowModal() == wx.ID_OK:
            listePersonnesPresentes = dlg.GetPersonnesPresentes()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        # S�lection dans la listBox
        for index, valeurs in self.dictDonnees.iteritems():
            IDpersonne = valeurs[0]
            if IDpersonne in listePersonnesPresentes :
                self.checkListBox.Check(index, True)
            else:
                self.checkListBox.Check(index, False)
        # S'il n'y a aucune personne pr�sente sur la p�riode s�lectionn�e
        if len(listePersonnesPresentes) == 0 :
            dlg = wx.MessageDialog(self, u"Il n'y a aucune personne pr�sente sur la p�riode que vous avez s�lectionn�.", u"Erreur de saisie", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(3)

    def OnBoutonOk(self, event):
        """ Validation des donn�es saisies """
        selections = self.checkListBox.GetChecked()
        
        # Validation de la s�lection
        if len(selections) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez fait aucune s�lection", u"Erreur de saisie", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Cr�ation de la liste des adresses mail
        self.listeAdresses = []
        listeAdresses = []
        listeSansAdresses = []
        for index in selections :
            IDpersonne, nom, prenom, mail = self.dictDonnees[index]
            if mail == "" :
                listeSansAdresses.append( prenom + " " + nom )
            else :
                listeAdresses.append(mail)
        
        # Si aucune des personnes s�lectionn�es n'a d'adresse
        if len(selections) == len(listeSansAdresses) :
            dlg = wx.MessageDialog(self, u"Aucune des personnes s�lectionn�es ne poss�de d'adresse internet !", u"Erreur de saisie", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Avertit qu'il y a des personnes sans adresse
        if len(listeSansAdresses) != 0 :
            # Cr�ation du texte du messageBox
            message = u"Parmi les " + str(len(selections)) + u" personnes s�lectionn�es, " + str(len(listeSansAdresses)) + u" ne poss�dent pas d'adresse internet : \n"
            for texteNom in listeSansAdresses :
                message += "\n    - " + texteNom
            message += u"\n\nSouhaitez-vous quand m�me continuer pour les " + str(len(listeAdresses)) + u" personne(s) poss�dant une adresse ?"
            # Affiche de la messageBox
            dlg = wx.MessageDialog(self, message, u"Adresses internet manquantes", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            if reponse == wx.ID_NO or reponse == wx.ID_CANCEL:
                dlg.Destroy()
                return
            else: dlg.Destroy()
        
        self.listeAdresses = listeAdresses
        
        # Ferme la bo�te de dialogue
        self.EndModal(wx.ID_OK)  

    def GetAdresses(self):
        return self.listeAdresses


    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyDialog(None, "")
    frame_1.ShowModal()
    app.MainLoop()
