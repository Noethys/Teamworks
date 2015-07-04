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
import os


class Panel(wx.Panel):
    def __init__(self, parent, ID=-1, size=(-1, -1), activer_a=True, activer_cci=True, activer_bouton_envoyer=True):
        wx.Panel.__init__(self, parent, ID, name="panel_param_mail", size=size, style=wx.TAB_TRAVERSAL)
        self.listePiecesJointes = []
        self.label_exp = wx.StaticText(self, -1, _(u"Exp. :"))
        self.ctrl_exp = wx.Choice(self, -1, choices=[], size=(50, -1))
        self.bouton_exp = wx.Button(self, -1, "...", size=(20, 20))
        self.label_a = wx.StaticText(self, -1, _(u"A :"))
        self.ctrl_a = wx.TextCtrl(self, -1, "")
        self.bouton_a = wx.Button(self, -1, "...", size=(20, 20))
        self.label_cci = wx.StaticText(self, -1, _(u"Cci :"))
        self.ctrl_cci = wx.TextCtrl(self, -1, "")
        self.bouton_cci = wx.Button(self, -1, "...", size=(20, 20))
        self.label_objet = wx.StaticText(self, -1, _(u"Objet :"))
        self.ctrl_objet = wx.TextCtrl(self, -1, "")
        self.label_joindre = wx.StaticText(self, -1, _(u"Joindre :"))
        self.ctrl_joindre = wx.ListBox(self, -1, choices=[], style=wx.LB_MULTIPLE)
        self.bouton_joindre_ajouter = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_joindre_supprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_envoyer = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer l'Email"), cheminImage="Images/32x32/Emails_exp.png")
        
        self.activer_a = activer_a
        self.activer_bouton_envoyer = activer_bouton_envoyer
        
        if activer_a == False :
            self.label_a.Show(False)
            self.ctrl_a.Show(False)
            self.bouton_a.Show(False)
        if activer_cci == False :
            self.label_cci.Show(False)
            self.ctrl_cci.Show(False)
            self.bouton_cci.Show(False)
        if activer_bouton_envoyer == False :
            self.bouton_envoyer.Show(False)
        
        self.__set_properties()
        self.__do_layout()
        
        self.MAJ_ctrl_expediteur()
        
        self.Bind(wx.EVT_BUTTON, self.OnboutonExpediteur, self.bouton_exp)
        self.Bind(wx.EVT_BUTTON, self.OnboutonA, self.bouton_a)
        self.Bind(wx.EVT_BUTTON, self.OnboutonCCI, self.bouton_cci)
        self.Bind(wx.EVT_BUTTON, self.OnboutonJoindre, self.bouton_joindre_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnboutonSupprPiece, self.bouton_joindre_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnboutonEnvoyer, self.bouton_envoyer)

    def __set_properties(self):
        self.ctrl_exp.SetToolTipString(_(u"Selectionnez votre adresse mail d'expéditeur"))
        self.bouton_exp.SetToolTipString(_(u"Cliquez ici pour acceder à la gestion des adresses d'expéditeur"))
        self.ctrl_a.SetToolTipString(_(u"Saisissez ici les adresses des destinataires espacées par des points-virgules"))
        self.bouton_a.SetToolTipString(_(u"Cliquez ici sélectionner des adresses mail de salariés ou de candidats"))
        self.ctrl_cci.SetToolTipString(_(u"Saisissez ici les adresses des destinataires CCi (les destinataires n'ont pas connaissance des adresses des autres destinataires) espacées par des points-virgules"))
        self.bouton_cci.SetToolTipString(_(u"Cliquez ici sélectionner des adresses mail de salariés ou de candidats"))
        self.ctrl_objet.SetToolTipString(_(u"Saisissez l'objet du message"))
        self.ctrl_joindre.SetToolTipString(_(u"Liste des pièces à joindre"))
        self.bouton_joindre_ajouter.SetToolTipString(_(u"Cliquez sur pour ajouter une pièce jointe"))
        self.bouton_joindre_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer la piece jointe sélectionnée dans la liste"))
        self.bouton_envoyer.SetToolTipString(_(u"Cliquez ici pour envoyer le mail"))


    def __do_layout(self):
        grid_sizer = wx.FlexGridSizer(rows=6, cols=2, vgap=5, hgap=5)
        grid_sizer_joindre = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_joindre = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        
        grid_sizer_exp = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer.Add(self.label_exp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT, 10)
        grid_sizer_exp.Add(self.ctrl_exp, 0, wx.EXPAND, 10)
        grid_sizer_exp.Add(self.bouton_exp, 0, 0, 0)
        grid_sizer_exp.AddGrowableCol(0)
        grid_sizer.Add(grid_sizer_exp, 1, wx.EXPAND|wx.RIGHT|wx.TOP, 10)
        
        grid_sizer_a = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer.Add(self.label_a, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
        grid_sizer_a.Add(self.ctrl_a, 0, wx.EXPAND, 10)
        grid_sizer_a.Add(self.bouton_a, 0, 0, 0)
        grid_sizer_a.AddGrowableCol(0)
        grid_sizer.Add(grid_sizer_a, 1, wx.EXPAND|wx.RIGHT, 10)
                
        grid_sizer_cci = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer.Add(self.label_cci, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
        grid_sizer_cci.Add(self.ctrl_cci, 0, wx.EXPAND, 10)
        grid_sizer_cci.Add(self.bouton_cci, 0, 0, 0)
        grid_sizer_cci.AddGrowableCol(0)
        grid_sizer.Add(grid_sizer_cci, 1, wx.EXPAND|wx.RIGHT, 10)
                
        grid_sizer.Add(self.label_objet, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
        grid_sizer.Add(self.ctrl_objet, 0, wx.EXPAND|wx.RIGHT, 10)
        grid_sizer.Add(self.label_joindre, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
        grid_sizer_joindre.Add(self.ctrl_joindre, 0, wx.EXPAND, 0)
        grid_sizer_boutons_joindre.Add(self.bouton_joindre_ajouter, 0, 0, 0)
        grid_sizer_boutons_joindre.Add(self.bouton_joindre_supprimer, 0, 0, 0)
        grid_sizer_joindre.Add(grid_sizer_boutons_joindre, 1, wx.EXPAND, 0)
        grid_sizer_joindre.AddGrowableRow(0)
        grid_sizer_joindre.AddGrowableCol(0)
        grid_sizer.Add(grid_sizer_joindre, 1, wx.EXPAND|wx.RIGHT, 10)
        grid_sizer.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer.Add(self.bouton_envoyer, 0, wx.EXPAND|wx.RIGHT|wx.TOP|wx.BOTTOM, 10)
        self.SetSizer(grid_sizer)
        grid_sizer.Fit(self)
        grid_sizer.AddGrowableCol(1)
        
    def OnboutonExpediteur(self, event):
        import Config_AdressesMail
        frm = Config_AdressesMail.MyFrame(self)
        frm.Show()

    def MAJ_ctrl_expediteur(self):
        self.listeAdresses = []
        self.dictAdresses = {}
        # Récupération des données
        DB = GestionDB.DB()        
        req = """SELECT IDadresse, adresse, smtp, port, defaut, connexionssl
        FROM adresses_mail ORDER BY adresse; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Remplissage du
        sel = None
        index = 0
        for IDadresse, adresse, smtp, port, defaut, connexionssl in listeDonnees :
            self.listeAdresses.append(adresse)
            self.dictAdresses[index] = (IDadresse, adresse, smtp, port, defaut, connexionssl)
            if defaut == 1 : sel = index
            index += 1
        self.ctrl_exp.SetItems(self.listeAdresses)
        if sel != None : self.ctrl_exp.SetSelection(sel)
    
    def OnboutonJoindre(self, event):
        # Demande l'emplacement du fichier à joindre
        standardPath = wx.StandardPaths.Get()
        rep = standardPath.GetDocumentsDir()
        dlg = wx.FileDialog(self, message=_(u"Veuillez sélectionner le ou les fichiers à joindre"), defaultDir=rep, defaultFile="", style=wx.OPEN|wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            chemins = dlg.GetPaths()
        else:
            return
        dlg.Destroy()
        for chemin in chemins :
            self.AjoutePieceJointe(chemin)
    
    def AjoutePieceJointe(self, chemin):
        if chemin in self.listePiecesJointes :
            return
        nomFichier = os.path.basename(chemin)
        self.listePiecesJointes.append(chemin)
        self.ctrl_joindre.AppendAndEnsureVisible(nomFichier)
    
    def OnboutonSupprPiece(self, event):
        selections = self.ctrl_joindre.GetSelections()
        if len(selections) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune pièce jointe à enlever de la liste !"), "Erreur", wx.OK| wx.ICON_ERROR)  
            dlg.ShowModal()
            dlg.Destroy()
            return
        for index in selections :
            self.listePiecesJointes.pop(index)
            self.ctrl_joindre.Delete(index)
            
    def OnboutonA(self, event):
        import Envoi_email_groupe
        dlg = Envoi_email_groupe.MyDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            listeAdresses = dlg.GetAdresses()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        self.ctrl_a.SetValue(u";".join(listeAdresses))
        
    def OnboutonCCI(self, event):
        import Envoi_email_groupe
        dlg = Envoi_email_groupe.MyDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            listeAdresses = dlg.GetAdresses()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        self.ctrl_cci.SetValue(u";".join(listeAdresses))
        
    def GetParametresPourPublipostage(self):
        """ Permet de récupérer les paramètres pour le publiposteur """
        indexExpediteur = self.ctrl_exp.GetSelection()
        adresseExpediteur = self.dictAdresses[indexExpediteur][1]
        serveur = self.dictAdresses[indexExpediteur][2]
        port = self.dictAdresses[indexExpediteur][3]
        connexionssl = self.dictAdresses[indexExpediteur][5]
        listeFichiersJoints = self.listePiecesJointes
        sujetMail = self.ctrl_objet.GetValue()
        
        dictParam = {}
        dictParam["adresseExpediteur"] = adresseExpediteur
        dictParam["serveur"] = serveur
        dictParam["port"] = port
        dictParam["connexionssl"] = connexionssl
        dictParam["sujetMail"] = sujetMail
        dictParam["listeFichiersJoints"] = listeFichiersJoints
        return dictParam
    
    def GetParametresPourEnvoi(self):
        """ Permet de récupérer les paramètres pour l'envoi direct """
        indexExpediteur = self.ctrl_exp.GetSelection()
        adresseExpediteur = self.dictAdresses[indexExpediteur][1]
        serveur = self.dictAdresses[indexExpediteur][2]
        port = self.dictAdresses[indexExpediteur][3]
        connexionssl = self.dictAdresses[indexExpediteur][5]
        listeDestinataires = self.ctrl_a.GetValue().split(";")
        if self.ctrl_cci.GetValue() != "" :
            listeDestinatairesCCI = self.ctrl_cci.GetValue().split(";")
        else:
            listeDestinatairesCCI = []
        texteMail = self.GetParent().GetHtmlText(imagesIncluses=True)
        listeFichiersJoints = self.listePiecesJointes
        sujetMail = self.ctrl_objet.GetValue()
        
        dictParam = {}
        dictParam["adresseExpediteur"] = adresseExpediteur
        dictParam["serveur"] = serveur
        dictParam["port"] = port
        dictParam["connexionssl"] = connexionssl
        dictParam["listeDestinataires"] = listeDestinataires
        dictParam["listeDestinatairesCCI"] = listeDestinatairesCCI
        dictParam["sujetMail"] = sujetMail
        dictParam["texteMail"] = texteMail
        dictParam["listeFichiersJoints"] = listeFichiersJoints
        return dictParam

    def OnboutonEnvoyer(self, event):
        """ Envoi du mail """
        etat = self.ValidationDonnees()
        if etat == False : return
        dictParam = self.GetParametresPourEnvoi()
        # Envoi du mail
        FonctionsPerso.Envoi_mail(dictParam["adresseExpediteur"], dictParam["listeDestinataires"], dictParam["listeDestinatairesCCI"], dictParam["sujetMail"], dictParam["texteMail"], dictParam["listeFichiersJoints"], dictParam["serveur"], dictParam["port"], dictParam["connexionssl"])
        # Fermeture du panel Mail
        self.GetParent()._mgr.GetPane("mail").Hide()
        self.GetParent()._mgr.Update()
        
        try :
            nomFrame = self.GetGrandParent().GetName()
        except :
            nomFrame = None
        if nomFrame == "frm_publiposteur" :
            frmTwd = self.GetParent()
            frmTwd.Destroy()
        
        
    def ValidationDonnees(self):
        """ Validation des données """
        
        # Adresse et serveur SMTP
        if self.ctrl_exp.GetSelection() == -1 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune adresse d'expéditeur !"), "Erreur", wx.OK| wx.ICON_ERROR)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_exp.SetFocus()
            return False
        
        # Destinataires
        if self.activer_a == True :
            if self.ctrl_a.GetValue() == "" :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune adresse de destinataire !"), "Erreur", wx.OK| wx.ICON_ERROR)  
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_a.SetFocus()
                return False
        
        # Contenu
        if self.ctrl_objet.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucun objet pour ce message !"), "Erreur", wx.OK| wx.ICON_ERROR)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_objet.SetFocus()
            return False
            
        return True
        
    def SetParamMail(self, adresseExpediteur, adresseDestinaire, sujetMail, listeFichiersJoints, serveur, port, connexionssl) :
        self.ctrl_exp.SetStringSelection(adresseExpediteur)
        self.ctrl_a.SetValue(adresseDestinaire)
        self.ctrl_objet.SetValue(sujetMail)
        for chemin in listeFichiersJoints :
            self.AjoutePieceJointe(chemin)
        
        
        
        

        