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
import wx.lib.masked as masked
import GestionDB
import FonctionsPerso


class FrameCoords(wx.Frame):
    def __init__(self, parent, ID, title, size, IDcoord=0, IDpersonne=0):
        # begin wxGlade: FrameCoords.__init__
        wx.Frame.__init__(self, parent, ID, title=_(u"Coordonnées"), style=wx.DEFAULT_FRAME_STYLE)

        self.parent = parent
        self.IDpersonne = IDpersonne
        self.IDcoord = IDcoord
        
        # Nom de la table
        if self.parent.GetName() == "panel_candidat" : self.nomTable = "coords_candidats"
        if self.parent.GetName() == "panel_generalites" : self.nomTable = "coordonnees"
        
        self.panel_frame = wx.Panel(self, -1)
        self.sizer_infos_staticbox = wx.StaticBox(self.panel_frame, -1, _(u"2. Saisissez les informations"))
        self.sizer_categories_staticbox = wx.StaticBox(self.panel_frame, -1, _(u"1. Sélectionnez une catégorie"))
        self.categorieSelect = ""

        self.MakeModal(True)

        # Boutons        
        self.bouton_fixe = wx.BitmapButton(self.panel_frame, -1, wx.Bitmap("Images/32x32/Maison_NB.png", wx.BITMAP_TYPE_ANY))
        self.bouton_mobile = wx.BitmapButton(self.panel_frame, -1, wx.Bitmap("Images/32x32/Mobile_NB.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fax = wx.BitmapButton(self.panel_frame, -1, wx.Bitmap("Images/32x32/Fax_NB.png", wx.BITMAP_TYPE_ANY))
        self.bouton_email = wx.BitmapButton(self.panel_frame, -1, wx.Bitmap("Images/32x32/Mail_NB.png", wx.BITMAP_TYPE_ANY))
        
        
        self.label_fixe = wx.StaticText(self.panel_frame, -1, "Fixe")
        self.label_mobile = wx.StaticText(self.panel_frame, -1, "Mobile")
        self.label_fax = wx.StaticText(self.panel_frame, -1, "Fax")
        self.label_email = wx.StaticText(self.panel_frame, -1, "Email")
        
        self.label_info_mail = wx.StaticText(self.panel_frame, -1, _(u"Email :"))
        self.text_info_mail = wx.TextCtrl(self.panel_frame, -1, "")
        self.label_info_tel = wx.StaticText(self.panel_frame, -1, _(u"N° Fixe :"))
        self.text_info_tel = masked.TextCtrl(self.panel_frame, -1, "", style=wx.TE_CENTRE, mask = "##.##.##.##.##.")

        self.label_info_mail.Hide()
        self.text_info_mail.Hide()
                
        self.label_intitule = wx.StaticText(self.panel_frame, -1, _(u"Intitulé :"))
        self.text_intitule = wx.TextCtrl(self.panel_frame, -1, "")
        self.bouton_Ok = CTRL_Bouton_image.CTRL(self.panel_frame, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_Annuler = CTRL_Bouton_image.CTRL(self.panel_frame, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        self.Bind(wx.EVT_BUTTON, self.OnBouton_Fixe, self.bouton_fixe)
        self.Bind(wx.EVT_BUTTON, self.OnBouton_Mobile, self.bouton_mobile)
        self.Bind(wx.EVT_BUTTON, self.OnBouton_Fax, self.bouton_fax)
        self.Bind(wx.EVT_BUTTON, self.OnBouton_Email, self.bouton_email)
        self.Bind(wx.EVT_BUTTON, self.OnBouton_Ok, self.bouton_Ok)
        self.Bind(wx.EVT_BUTTON, self.OnBouton_Annuler, self.bouton_Annuler)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        # Si c'est une modification, on importe les données
        if self.IDcoord != 0:
            self.Importation()
        else:
            # Désactivation des champs
            self.ActivationChamps(False)


    def __set_properties(self):
        # begin wxGlade: FrameCoords.__set_properties
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_fixe.SetSize(self.bouton_fixe.GetBestSize())
        self.bouton_mobile.SetSize(self.bouton_mobile.GetBestSize())
        self.bouton_fax.SetSize(self.bouton_fax.GetBestSize())
        self.bouton_email.SetSize(self.bouton_email.GetBestSize())
        self.bouton_Ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_Ok.SetSize(self.bouton_Ok.GetBestSize())
        self.bouton_Annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.bouton_Annuler.SetSize(self.bouton_Annuler.GetBestSize())
        self.text_info_tel.SetToolTipString(_(u"Saisissez ici un numéro de téléphone"))
        self.text_info_mail.SetToolTipString(_(u"Saisissez ici une adresse Mail valide"))
        self.text_intitule.SetToolTipString(_(u"Vous pouvez, si vous le souhaitez, saisir ici un intitulé. Ex : 'Contact à Rennes' ou 'Domicile des parents'..."))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: FrameCoords.__do_layout
        sizer_frame = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=15, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        sizer_infos = wx.StaticBoxSizer(self.sizer_infos_staticbox, wx.VERTICAL)
        grid_sizer_infos = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        sizer_categories = wx.StaticBoxSizer(self.sizer_categories_staticbox, wx.VERTICAL)
        grid_sizer_categories = wx.FlexGridSizer(rows=2, cols=4, vgap=5, hgap=10)
        grid_sizer_categories.Add(self.bouton_fixe, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_categories.Add(self.bouton_mobile, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_categories.Add(self.bouton_fax, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_categories.Add(self.bouton_email, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_categories.Add(self.label_fixe, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_categories.Add(self.label_mobile, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_categories.Add(self.label_fax, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_categories.Add(self.label_email, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_categories.AddGrowableCol(0)
        grid_sizer_categories.AddGrowableCol(1)
        grid_sizer_categories.AddGrowableCol(2)
        grid_sizer_categories.AddGrowableCol(3)
        sizer_categories.Add(grid_sizer_categories, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(sizer_categories, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        grid_sizer_infos.Add(self.label_info_mail, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infos.Add(self.text_info_mail, 0, wx.EXPAND, 0) #######################

        grid_sizer_infos.Add(self.label_info_tel, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infos.Add(self.text_info_tel, 0, wx.EXPAND, 0) #######################
        
        grid_sizer_infos.Add(self.label_intitule, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_infos.Add(self.text_intitule, 0, wx.EXPAND, 0)
        grid_sizer_infos.AddGrowableCol(1)
        sizer_infos.Add(grid_sizer_infos, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(sizer_infos, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add((15, 15), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_Ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_Annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.panel_frame.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        sizer_frame.Add(self.panel_frame, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_frame)
        self.SetMinSize((280, 250))
        grid_sizer_base.Fit(self)
        self.Layout()
        self.Centre()
        # end wxGlade
        self.grid_sizer_infos = grid_sizer_infos

# end of class FrameCoords

    def OnBouton_Fixe(self, event):
        # Apparence des boutons
        self.bouton_fixe.SetBitmapLabel(wx.Bitmap("Images/32x32/Maison_Bleu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_mobile.SetBitmapLabel(wx.Bitmap("Images/32x32/Mobile_NB.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fax.SetBitmapLabel(wx.Bitmap("Images/32x32/Fax_NB.png", wx.BITMAP_TYPE_ANY))
        self.bouton_email.SetBitmapLabel(wx.Bitmap("Images/32x32/Mail_NB.png", wx.BITMAP_TYPE_ANY))

        # Activation des champs
        self.ActivationChamps(True)
        self.label_info_tel.SetLabel(_(u"N° Fixe :"))        
        self.text_info_tel.SetFocus()
        self.categorieSelect = "Fixe"
        self.label_info_mail.Hide()
        self.text_info_mail.Hide()
        self.label_info_tel.Show()
        self.text_info_tel.Show()
        self.grid_sizer_infos.Layout()
        
    
    def OnBouton_Mobile(self, event):
        # Apparence des boutons
        self.bouton_fixe.SetBitmapLabel(wx.Bitmap("Images/32x32/Maison_NB.png", wx.BITMAP_TYPE_ANY))
        self.bouton_mobile.SetBitmapLabel(wx.Bitmap("Images/32x32/Mobile_Bleu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fax.SetBitmapLabel(wx.Bitmap("Images/32x32/Fax_NB.png", wx.BITMAP_TYPE_ANY))
        self.bouton_email.SetBitmapLabel(wx.Bitmap("Images/32x32/Mail_NB.png", wx.BITMAP_TYPE_ANY))

        # Activation des champs
        self.ActivationChamps(True)
        self.label_info_tel.SetLabel(_(u"N° Mobile :"))
        self.text_info_tel.SetFocus()
        self.categorieSelect = "Mobile"
        self.label_info_mail.Hide()
        self.text_info_mail.Hide()
        self.label_info_tel.Show()
        self.text_info_tel.Show()
        self.grid_sizer_infos.Layout()

    def OnBouton_Fax(self, event):
        # Apparence des boutons
        self.bouton_fixe.SetBitmapLabel(wx.Bitmap("Images/32x32/Maison_NB.png", wx.BITMAP_TYPE_ANY))
        self.bouton_mobile.SetBitmapLabel(wx.Bitmap("Images/32x32/Mobile_NB.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fax.SetBitmapLabel(wx.Bitmap("Images/32x32/Fax_Bleu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_email.SetBitmapLabel(wx.Bitmap("Images/32x32/Mail_NB.png", wx.BITMAP_TYPE_ANY))

        # Activation des champs
        self.ActivationChamps(True)
        self.label_info_tel.SetLabel(_(u"N° Fax :"))
        self.text_info_tel.SetFocus()
        self.categorieSelect = "Fax"
        self.label_info_mail.Hide()
        self.text_info_mail.Hide()
        self.label_info_tel.Show()
        self.text_info_tel.Show()
        self.grid_sizer_infos.Layout()

    def OnBouton_Email(self, event):
        # Apparence des boutons
        self.bouton_fixe.SetBitmapLabel(wx.Bitmap("Images/32x32/Maison_NB.png", wx.BITMAP_TYPE_ANY))
        self.bouton_mobile.SetBitmapLabel(wx.Bitmap("Images/32x32/Mobile_NB.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fax.SetBitmapLabel(wx.Bitmap("Images/32x32/Fax_NB.png", wx.BITMAP_TYPE_ANY))
        self.bouton_email.SetBitmapLabel(wx.Bitmap("Images/32x32/Mail_Bleu.png", wx.BITMAP_TYPE_ANY))

        # Activation des champs
        self.ActivationChamps(True)
        self.text_info_mail.SetFocus()
        self.categorieSelect = "Email"
        self.label_info_tel.Hide()
        self.text_info_tel.Hide()
        self.label_info_mail.Show()
        self.text_info_mail.Show()
        self.grid_sizer_infos.Layout()

        

    def ActivationChamps(self, etat=False):
        if etat == True :
            self.label_info_tel.Enable(True)
            self.text_info_tel.Enable(True)
            self.label_info_mail.Enable(True)
            self.text_info_mail.Enable(True)
            self.label_intitule.Enable(True)
            self.text_intitule.Enable(True)
        else:
            self.label_info_tel.Enable(False)
            self.text_info_tel.Enable(False)
            self.label_info_mail.Enable(False)
            self.text_info_mail.Enable(False)
            self.label_intitule.Enable(False)
            self.text_intitule.Enable(False)
        

    def InitSaisieInfo(self):
        """ Remplissage initial du contrôle text_info """
        if self.categorieSelect == "Email" or self.categorieSelect == "":
            self.text_info.SetValue("")
        else:
            self.text_info.SetValue("  .  .  .  .  .")

    def OnSaisieInfo(self, event):
        """ Formatages des numéros de téléphone """
        text = event.GetString()
        taille = len(text)
        if taille == 0:
            return
        
        if self.categorieSelect == "Email" :
            return

        lettre = text[-1]
        pos = taille-1
        chaineFormat = "  .  .  .  .  ."
        print  text, lettre, pos
        
 
        # Validation du caractère
        if lettre == "." and (pos==2 or pos ==5 or pos==8 or pos==11 or pos==14):
            return
        elif lettre == ".":
            resultat = text[0:-1]
            self.text_info.SetValue(resultat)
            self.text_info.SetInsertionPoint(taille-1)
        
        if lettre.isdigit() == False and lettre != ".":
            resultat = text[0:-1]
            self.text_info.SetValue(resultat)
            self.text_info.SetInsertionPoint(taille-1)

    def OnBouton_Annuler(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    def OnCloseWindow(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()

    def OnBouton_Ok(self, event):
        """ Validation de la saisie """
        if self.categorieSelect == "":
            message = _(u"Vous devez commencer par sélectionner une catégorie.")
            wx.MessageBox(message, "Erreur de saisie")
            return

        # Validation de l'email
        if self.categorieSelect == "Email" :
            text = self.text_info_mail.GetValue()
            # Vérifie si Email vide
            if text == "":
                message = _(u"Vous devez saisir une adresse Email valide.")
                wx.MessageBox(message, "Erreur de saisie")
                self.text_info_mail.SetFocus()
                return
            # Vérifie si Email valide
            posAt = text.find("@")
            if posAt == -1:
                message = _(u"L'adresse Email que vous avez saisie n'est pas valide.")
                wx.MessageBox(message, "Erreur de saisie")
                self.text_info_mail.SetFocus()
                return
            posPoint = text.rfind(".")
            if posPoint < posAt :
                message = _(u"L'adresse Email que vous avez saisie n'est pas valide.")
                wx.MessageBox(message, "Erreur de saisie")
                self.text_info_mail.SetFocus()
                return

        # Validation du téléphone
        if self.categorieSelect != "Email" :
            text = self.text_info_tel.GetValue()
            # Vérifie si Tél vide
            if text == "" or text == "  .  .  .  .  .":
                message = _(u"Vous devez saisir un numéro de téléphone valide.")
                wx.MessageBox(message, "Erreur de saisie")
                self.text_info_tel.SetFocus()
                return
            # Vérifie si Téléphone valide
            posChiffres = [0, 1, 3, 4, 6, 7, 9, 10, 12, 13]
            for position in posChiffres:
                if text[position].isdigit() == False:
                    message = _(u"Le numéro de téléphone ne semble pas valide.")
                    wx.MessageBox(message, "Erreur de saisie")
                    self.text_info_tel.SetFocus()
                    return

        # Si les test de validation sont positifs
        self.Sauvegarde()
        
        # MAJ du de la fiche candidat
        if self.parent.GetName() == "panel_candidat" :
            self.parent.ctrl_coords.Remplissage()
        
        # MàJ du listCtrl Coords de la fiche individuelle
        if self.parent.GetName() == "panel_generalites" :
            self.parent.list_ctrl_coords.Remplissage()
            self.parent.MAJ_barre_problemes()

        # Fermeture du frame
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    def Sauvegarde(self):
        """ Sauvegarde des données dans la base de données """
        varIDpersonne = self.IDpersonne
        varCategorie = self.categorieSelect
        if varCategorie == "Email":
            varTexte = self.text_info_mail.GetValue()
        else:
            varTexte = self.text_info_tel.GetValue()
        varDIntitule = self.text_intitule.GetValue()

        # Préparation des données
        if self.nomTable == "coordonnees" : 
            texte = "IDpersonne"
        else: 
            texte = "IDcandidat"
        listeDonnees = [    (texte,  varIDpersonne),
                            ("categorie",   varCategorie),
                            ("texte",       varTexte),
                            ("intitule",    varDIntitule),
                        ]
        
        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()

        if self.IDcoord == 0:
            # Enregistrement d'une nouvelle coordonnée
            DB.ReqInsert(self.nomTable, listeDonnees)
        else:
            # Modification de la coordonnée
            DB.ReqMAJ(self.nomTable, listeDonnees, "IDcoord", self.IDcoord)

    def Importation(self,):
        """ Importation des donnees de la base """

        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        req = "SELECT * FROM %s WHERE IDcoord = %d" % (self.nomTable, self.IDcoord)
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()[0]
        DB.Close()
        
        # Placement des données dans les contrôles
        self.categorieSelect = donnees[2]
        self.text_intitule.SetValue(donnees[4])

        if self.categorieSelect == "Fixe":
            self.OnBouton_Fixe("")
            self.text_info_tel.SetValue(donnees[3])
        if self.categorieSelect == "Mobile":
            self.OnBouton_Mobile("")
            self.text_info_tel.SetValue(donnees[3])
        if self.categorieSelect == "Fax":
            self.OnBouton_Fax("")
            self.text_info_tel.SetValue(donnees[3])
        if self.categorieSelect == "Email":
            self.OnBouton_Email("")
            self.text_info_mail.SetValue(donnees[3])
            
     
            

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frameCoords = FrameCoords(None, -1, _(u"Coordonnées"), size=(280, 290))
    app.SetTopWindow(frameCoords)
    frameCoords.Show()
    app.MainLoop()
