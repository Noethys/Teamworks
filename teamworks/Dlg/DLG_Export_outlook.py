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
import FonctionsPerso
import  wx.lib.scrolledpanel as scrolled
import win32com.client

COULEUR_SYNCHRO = (176, 251, 168)
COULEUR_MODIF = (255, 230, 169)
COULEUR_NON_SYNCHRO = (255, 169, 169)


class LibOutlook() :
    def __init__(self):
        # Chargement de Outlook
        self.echec = False
        try : 
            self.Outlook = win32com.client.Dispatch("Outlook.Application")
            self.echec = False
        except :
            print("pas de outlook")
            self.echec = True
        
    def Test(self):
        """ Teste si Outlook n'est pas verrouillé """
        try :
            # Test de lecture des contacts
            MAPI = self.Outlook.GetNamespace("MAPI")
            print("win32com.client.constants:", win32com.client.constants)
            dossierContacts = MAPI.GetDefaultFolder(10)  # win32com.client.constants.olFolderContacts
            nbreContacts = len(dossierContacts.Items)
            for i in range(nbreContacts):
                item = dossierContacts.Items.Item(i+1)
                test = item.Email1Address
            return True
        except :
            return False
        
    def Suppression(self, nometprenom):
        # Suppression d'un contact
        MAPI = self.Outlook.GetNamespace("MAPI")
        dossierContacts = MAPI.GetDefaultFolder(10)   # win32com.client.constants.olFolderContacts
        for i in range(len(dossierContacts.Items)):
            item = dossierContacts.Items.Item(i+1)
            if item.LastNameAndFirstName == nometprenom :
                item.Delete()
                break
                
    def Lecture(self):
        # Lecture des contacts
        MAPI = self.Outlook.GetNamespace("MAPI")
        dossierContacts = MAPI.GetDefaultFolder(10)   # win32com.client.constants.olFolderContacts
        
        dictContacts = {}

        for i in range(len(dossierContacts.Items)):
            item = dossierContacts.Items.Item(i+1)
            contact = {}
            
            # Généralités
            contact["civilite"] = item.Title
            contact["nom"] = item.LastName
            contact["prenom"] = item.FirstName
            contact["nom complet"] = item.FullName
            contact["nom et prenom"] = item.LastNameAndFirstName
            contact["file as"] = item.FileAs
            
            contact["anniversaire"] = item.Anniversary
            contact["categories"] = item.Categories

            # Adresses Mail
            contact["email1"] = item.Email1Address
            contact["email2"] = item.Email2Address
            contact["email3"] = item.Email3Address

            # Téléphones
            contact["fixe1"] = item.HomeTelephoneNumber
            contact["fixe2"] = item.Home2TelephoneNumber
            contact["fax"] = item.HomeFaxNumber
            contact["mobile"] = item.MobileTelephoneNumber

            # Adresse
            contact["ville"] = item.HomeAddressCity
            contact["pays"] = item.HomeAddressCountry
            contact["cp"] = item.HomeAddressPostalCode
            contact["adresse"] = item.HomeAddressStreet
            
            contact["mailing ville"] = item.MailingAddressCity
            contact["mailing pays"] = item.MailingAddressCountry
            contact["mailing cp"] = item.MailingAddressPostalCode
            contact["mailing adresse"] = item.MailingAddressStreet
            
            dictContacts[i+1] = contact
        
        return dictContacts

    def Enregistrement(self, civilite, nom, prenom, anniversaire, email1, email2, email3, fixe1, fixe2, fax, mobile, ville, pays, cp, adresse):
        # Enregistrement d'un contact sous Outlook
        contact = self.Outlook.CreateItem(2) # 2=outlook contact item
        contact.Title = civilite
        contact.FirstName = prenom
        contact.LastName = nom
##        contact.Anniversary = anniversaire
        contact.Email1Address = email1
        contact.Email2Address = email2
        contact.Email3Address = email3
        contact.HomeTelephoneNumber = fixe1
        contact.Home2TelephoneNumber = fixe2
        contact.HomeFaxNumber = fax
        contact.MobileTelephoneNumber = mobile
        contact.HomeAddressCity = ville
        contact.HomeAddressCountry = pays
        contact.HomeAddressPostalCode = cp
        contact.HomeAddressStreet = adresse
        contact.Categories = "TeamWorks"
        contact.Save()
        return True







class PanelContacts(scrolled.ScrolledPanel):
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent, -1)
        print("1")
        self.outlook = LibOutlook()
        print(self.outlook)
        self.dictContacts = self.outlook.Lecture()
        
        self.listeContacts = self.Import_Donnees()
        gridSizer = wx.FlexGridSizer(cols=6, vgap=2, hgap=2)
        
        # Création des labels
        label_nom = wx.StaticText(self, -1, _(u"Nom et prénom"))
        label_adresse = wx.StaticText(self, -1, _(u"Adresse"))
        label_coords = wx.StaticText(self, -1, _(u"Coordonnées"))
        label_datenaiss = wx.StaticText(self, -1, _(u"Date de naiss."))
        
        font = wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL)
        label_nom.SetFont(font)
        label_adresse.SetFont(font)
        label_coords.SetFont(font)
        label_datenaiss.SetFont(font)
        
        gridSizer.Add((5, 5), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTRE, border=0)
        gridSizer.Add((5, 5), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTRE, border=0)
        gridSizer.Add(label_nom, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTRE, border=0)
        gridSizer.Add(label_adresse, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTRE, border=0)
        gridSizer.Add(label_coords, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTRE, border=0)
        gridSizer.Add(label_datenaiss, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTRE, border=0)

        for IDpersonne, civilite, nom, prenom, date_naiss, adresse_resid, cp_resid, ville_resid, emails, fixes, fax, mobile in self.listeContacts:
            
            # Création des contrôles
            exec("self.bouton_synchro_" + str(IDpersonne) + " = wx.BitmapButton(self, 10000+IDpersonne, wx.Bitmap('Images/16x16/Ok_2.png', wx.BITMAP_TYPE_ANY))")
            exec("self.bouton_synchro_" + str(IDpersonne) + ".SetBitmapDisabled(wx.Bitmap('Images/16x16/Ok_3.png', wx.BITMAP_TYPE_ANY))")
            exec("self.bouton_synchro_" + str(IDpersonne) + ".SetToolTip(wx.ToolTip(u'Cliquez ici pour synchroniser la fiche de ' + prenom + ' ' + nom + '.'))")
            exec("self.bouton_suppr_" + str(IDpersonne) + " = wx.BitmapButton(self, 20000+IDpersonne, wx.Bitmap('Images/16x16/Supprimer_2.png', wx.BITMAP_TYPE_ANY))")
            exec("self.bouton_suppr_" + str(IDpersonne) + ".SetBitmapDisabled(wx.Bitmap('Images/16x16/Supprimer_3.png', wx.BITMAP_TYPE_ANY))")
            exec("self.bouton_suppr_" + str(IDpersonne) + ".SetToolTip(wx.ToolTip(u'Cliquez ici pour supprimer la fiche de ' + prenom + ' ' + nom + ' de Outlook.'))")
            
            coords = []
            texte_coords = ""
            for email in emails : coords.append(email)
            for fixe in fixes : coords.append(fixe)
            coords.append(fax)
            coords.append(mobile)
            for coord in coords :
                if coord != "" : texte_coords += coord + ", "
            texte_coords = texte_coords[:-2]
            
            exec("self.text_nom_" + str(IDpersonne) + " = wx.TextCtrl(self, -1, nom + ', ' + prenom, size=(190,-1))")
            exec("self.text_adresse_" + str(IDpersonne) + " = wx.TextCtrl(self, -1, adresse_resid + ' ' + cp_resid + ' ' + ville_resid, size=(250,-1))")
            exec("self.text_coords_" + str(IDpersonne) + " = wx.TextCtrl(self, -1, texte_coords, size=(200,-1))")
            exec("self.text_datenaiss_" + str(IDpersonne) + " = wx.TextCtrl(self, -1, date_naiss, size=(75,-1))")
            
            # Définition de l'état
            etat = "non synchro"
            for key, valeurs in self.dictContacts.items():
                if valeurs["nom et prenom"] == nom + ", " + prenom :
                    # Ce contact est déjà dans Outlook
                    etat = "synchro"
            
            # Etat des contrôles
            self.Affiche_controles(IDpersonne, etat)
            
            # Layout des contrôles
            exec("gridSizer.Add(self.bouton_synchro_" + str(IDpersonne) + ", flag=wx.ALIGN_CENTER_VERTICAL, border=0)")
            exec("gridSizer.Add(self.bouton_suppr_" + str(IDpersonne) + ", flag=wx.ALIGN_CENTER_VERTICAL, border=0)")
            exec("gridSizer.Add(self.text_nom_" + str(IDpersonne) + ", flag=wx.ALIGN_CENTER_VERTICAL, border=0)")
            exec("gridSizer.Add(self.text_adresse_" + str(IDpersonne) + ", flag=wx.ALIGN_CENTER_VERTICAL, border=0)")
            exec("gridSizer.Add(self.text_coords_" + str(IDpersonne) + ", flag=wx.ALIGN_CENTER_VERTICAL, border=0)")
            exec("gridSizer.Add(self.text_datenaiss_" + str(IDpersonne) + ", flag=wx.ALIGN_CENTER_VERTICAL, border=0)")
            
            # Bind
            exec("self.Bind(wx.EVT_BUTTON, self.OnBoutonSynchro, self.bouton_synchro_" + str(IDpersonne) + ")")
            exec("self.Bind(wx.EVT_BUTTON, self.OnBoutonSuppr, self.bouton_suppr_" + str(IDpersonne) + ")")

        self.SetSizer(gridSizer)
        self.SetAutoLayout(1)
        self.SetupScrolling()
        
        
    def Affiche_controles(self, IDpersonne, etat):
        if etat == "synchro" :
            exec("self.bouton_synchro_" + str(IDpersonne) + ".Enable(False)")
            exec("self.bouton_suppr_" + str(IDpersonne) + ".Enable(True)")
            exec("self.text_nom_" + str(IDpersonne) + ".SetBackgroundColour(COULEUR_SYNCHRO)") # Vert
            exec("self.text_adresse_" + str(IDpersonne) + ".SetBackgroundColour(COULEUR_SYNCHRO)") # Vert
            exec("self.text_coords_" + str(IDpersonne) + ".SetBackgroundColour(COULEUR_SYNCHRO)") # Vert
            exec("self.text_datenaiss_" + str(IDpersonne) + ".SetBackgroundColour(COULEUR_SYNCHRO)") # Vert
        if etat == "modif" :
            exec("self.bouton_synchro_" + str(IDpersonne) + ".Enable(True)")
            exec("self.bouton_suppr_" + str(IDpersonne) + ".Enable(True)")
            exec("self.text_nom_" + str(IDpersonne) + ".SetBackgroundColour(COULEUR_MODIF)") # Orange
            exec("self.text_adresse_" + str(IDpersonne) + ".SetBackgroundColour(COULEUR_MODIF)") # Orange
            exec("self.text_coords_" + str(IDpersonne) + ".SetBackgroundColour(COULEUR_MODIF)") # Orange
            exec("self.text_datenaiss_" + str(IDpersonne) + ".SetBackgroundColour(COULEUR_MODIF)") # Orange
        if etat == "non synchro" :
            exec("self.bouton_synchro_" + str(IDpersonne) + ".Enable(True)")
            exec("self.bouton_suppr_" + str(IDpersonne) + ".Enable(False)")
            exec("self.text_nom_" + str(IDpersonne) + ".SetBackgroundColour(COULEUR_NON_SYNCHRO)") # Rouge
            exec("self.text_adresse_" + str(IDpersonne) + ".SetBackgroundColour(COULEUR_NON_SYNCHRO)") # Rouge
            exec("self.text_coords_" + str(IDpersonne) + ".SetBackgroundColour(COULEUR_NON_SYNCHRO)") # Rouge
            exec("self.text_datenaiss_" + str(IDpersonne) + ".SetBackgroundColour(COULEUR_NON_SYNCHRO)") # Rouge
        self.Refresh()
        

    def OnBoutonSynchro(self, event):
        IDpersonne = event.GetId() - 10000
        self.Synchro(IDpersonne)
        self.Affiche_controles(IDpersonne, "synchro")
    
    def OnBoutonSuppr(self, event):
        IDpersonne = event.GetId() - 20000
        exec("nometprenom = self.text_nom_" + str(IDpersonne) + ".GetValue()")
        self.outlook.Suppression(nometprenom)
        self.Affiche_controles(IDpersonne, "non synchro")

    def Synchro(self, IDpersonne) :
        for ID, civilite, nom, prenom, date_naiss, adresse, cp, ville, emails, fixes, fax, mobile in self.listeContacts:
            if ID == IDpersonne :
                # Préparation des données
                anniversaire = "25/06/1981"
                pays = "France"
        
                if len(emails) == 0 :
                    email1 = ""
                    email2 = ""
                    email3 = ""
                elif len(emails) == 1 :
                    email1 = emails[0]
                    email2 = ""
                    email3 = ""
                elif len(emails) == 2 :
                    email1 = emails[0]
                    email2 = emails[1]
                    email3 = ""
                else :
                    email1 = emails[0]
                    email2 = emails[1]
                    email3 = emails[2]
                    
                if len(fixes) == 0 :
                    fixe1 = ""
                    fixe2 = ""
                elif len(fixes) == 1 :
                    fixe1 = fixes[0]
                    fixe2 = ""
                else :
                    fixe1 = fixes[0]
                    fixe2 = fixes[1]
                
                # Enregistrement des données
                self.outlook.Enregistrement(civilite, nom, prenom, anniversaire, email1, email2, email3, fixe1, fixe2, fax, mobile, ville, pays, cp, adresse)
                break
            
    def SynchroTout(self):
        for IDpersonne, civilite, nom, prenom, date_naiss, adresse, cp, ville, emails, fixes, fax, mobile in self.listeContacts:
            exec("etat = self.bouton_synchro_" + str(IDpersonne) + ".IsEnabled()")
            if etat == True :
                self.Synchro(IDpersonne)
                self.Affiche_controles(IDpersonne, "synchro")

    def SupprTout(self):
        for IDpersonne, civilite, nom, prenom, date_naiss, adresse, cp, ville, emails, fixes, fax, mobile in self.listeContacts:
            exec("etat = self.bouton_synchro_" + str(IDpersonne) + ".IsEnabled()")
            if etat == False :
                self.outlook.Suppression(nom + ", " + prenom)
                self.Affiche_controles(IDpersonne, "non synchro")
            
    def Import_Donnees(self):
        """ Importe les champs de la base de données """
        DB = GestionDB.DB() 
        
        listeContacts = []
       
        # Base personnes
        req = """
            SELECT IDpersonne, civilite, nom, prenom, date_naiss, adresse_resid, cp_resid, ville_resid
            FROM personnes;
        """
        DB.ExecuterReq(req)
        listePersonnes = DB.ResultatReq()
        
        for personne in listePersonnes :
        
            IDpersonne = personne[0]
            civilite = personne[1]
            nom = personne[2]
            prenom = personne[3]
            date_naiss = personne[4]
            if date_naiss == None : date_naiss = ""
            if date_naiss != "" : date_naiss = FonctionsPerso.DateEngFr(date_naiss)
            adresse_resid = personne[5]
            cp_resid = str(personne[6])
            ville_resid = personne[7]
            
            # Adaptation des données
            if civilite == "Mr" : civilite = "M."
            if civilite == "Mme" : civilite = "Mme"
            if civilite == "Melle" : civilite = "Melle"
            
            # Base coordonnées
            req = """
                SELECT categorie, texte
                FROM coordonnees WHERE IDpersonne=%d;
            """ % IDpersonne
            DB.ExecuterReq(req)
            listeCoords = DB.ResultatReq()
            
            emails = []
            fixes = []
            fax = ""
            mobile = ""
            
            for categorie, texte in listeCoords :
                if categorie == "Mobile" : 
                    mobile = texte
                if categorie == "Fixe" :
                    fixes.append(texte)
                if categorie == "Email" :
                    emails.append(texte)
                if categorie == "Fax" :
                    fax = texte

            # Création de la liste
            listeContacts.append( [IDpersonne, civilite, nom, prenom, date_naiss, adresse_resid, cp_resid, ville_resid, emails, fixes, fax, mobile] )

        DB.Close()
        return listeContacts
    
    


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        
        
class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.panel_base = wx.Panel(self, -1)
        self.sizer_grid_staticbox = wx.StaticBox(self.panel_base, -1, "Champs")
        self.label_intro = wx.StaticText(self.panel_base, -1, _(u"Synchronisez vos contacts Outlook en cliquant sur les boutons ci-dessous :"))
               
        # Préparation de la grid
        self.gridChamps = PanelContacts(self.panel_base)
        
        self.label_synchro = wx.StaticText(self.panel_base, -1, _(u"Synchro."))
        self.label_modif = wx.StaticText(self.panel_base, -1, _(u"Synchro mais modifié"))
        self.label_non_synchro = wx.StaticText(self.panel_base, -1, _(u"Non synchro."))
        
        self.label_synchro.SetBackgroundColour(COULEUR_SYNCHRO)
        self.label_modif.SetBackgroundColour(COULEUR_MODIF)
        self.label_non_synchro.SetBackgroundColour(COULEUR_NON_SYNCHRO)
        
        self.bouton_synchroTout = wx.Button(self.panel_base, -1, _(u"Tout synchroniser"))
        self.bouton_supprTout = wx.Button(self.panel_base, -1, _(u"Tout désynchroniser"))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Fermer"), cheminImage=Chemins.GetStaticPath("Images/32x32/Fermer.png"))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)
        self.Bind(wx.EVT_BUTTON, self.OnSynchroTout, self.bouton_synchroTout)
        self.Bind(wx.EVT_BUTTON, self.OnSupprTout, self.bouton_supprTout)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
                
    def __set_properties(self):
        self.SetTitle(_(u"Exportation des contacts vers Outlook"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip("Cliquez ici pour annuler et fermer"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        sizer_grid = wx.StaticBoxSizer(self.sizer_grid_staticbox, wx.VERTICAL)
        
        grid_sizer_2 = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_2.Add(self.gridChamps, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        
        grid_sizer_commandes.Add( self.label_synchro, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_commandes.Add( self.label_modif, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add( self.label_non_synchro, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add( (5, 5), 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_commandes.Add(self.bouton_synchroTout, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_commandes.Add(self.bouton_supprTout, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_commandes.AddGrowableCol(3)
        
        grid_sizer_2.Add(grid_sizer_commandes, 1, wx.ALL|wx.EXPAND, 0)
        grid_sizer_2.AddGrowableRow(0)
        grid_sizer_2.AddGrowableCol(0)
        
        sizer_grid.Add(grid_sizer_2, 1, wx.ALL|wx.EXPAND, 0)
        
        grid_sizer_base.Add(sizer_grid, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        self.SetMinSize((570, 400))
        self.SetSize((570, 550))
        self.CenterOnScreen()
    
    def Onbouton_aide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("ExporterlespersonnesdansMSOutl")

    def Onbouton_annuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnSynchroTout(self, event):
        self.gridChamps.SynchroTout()
        event.Skip()
        
    def OnSupprTout(self, event):
        self.gridChamps.SupprTout()
        event.Skip()
        


if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
