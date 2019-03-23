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
import wx.lib.agw.hyperlink as hl
from Data import DATA_Tables


class PanelReseau(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, style=wx.TAB_TRAVERSAL)
        
        self.label_port = wx.StaticText(self, -1, _(u"Port :"), size=(-1, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_port = wx.TextCtrl(self, -1, "3306", size=(45, -1))
        
        self.label_hote = wx.StaticText(self, -1, _(u"Hôte :"), size=(-1, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_hote = wx.TextCtrl(self, -1, "", size=(-1, -1))
        
        self.label_user = wx.StaticText(self, -1, _(u"Utilisateur :"), size=(-1, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_user = wx.TextCtrl(self, -1, "", size=(-1, -1))
        
        self.label_mdp = wx.StaticText(self, -1, _(u"Mot de passe :"), size=(-1, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_mdp = wx.TextCtrl(self, -1, "", size=(-1, -1), style=wx.TE_PASSWORD)
        
        self.__do_layout()

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=2, vgap=10, hgap=10)
        
        # Port
        grid_sizer_base.Add(self.label_port, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 0)
        grid_sizer_base.Add(self.ctrl_port, 0, wx.ALL, 0)
        
        # Hote
        grid_sizer_base.Add(self.label_hote, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 0)
        grid_sizer_base.Add(self.ctrl_hote, 1, wx.EXPAND | wx.ALL, 0)
        
        # User
        grid_sizer_base.Add(self.label_user, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 0)
        grid_sizer_base.Add(self.ctrl_user, 1, wx.EXPAND | wx.ALL, 0)
        
        # Mot de passe
        grid_sizer_base.Add(self.label_mdp, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 0)
        grid_sizer_base.Add(self.ctrl_mdp, 1, wx.EXPAND | wx.ALL, 0)
                
        grid_sizer_base.AddGrowableCol(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        
        self.ctrl_port.SetToolTip(wx.ToolTip(_(u"Le numéro de port est 3306 par défaut.")))
        self.ctrl_hote.SetToolTip(wx.ToolTip(_(u"Indiquez ici le nom du serveur hôte.")))
        self.ctrl_user.SetToolTip(wx.ToolTip(_(u"Indiquez ici le nom de l'utilisateur. Ce nom doit avoir été validé par le créateur du fichier.")))
        self.ctrl_mdp.SetToolTip(wx.ToolTip(_(u"Indiquez ici le mot de passe nécessaire à la connexion à MySQL")))


class MyDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, title=_(u"Création d'un fichier"))       
        self.parent = parent
        
        import locale
        self.locale = wx.Locale(wx.LANGUAGE_FRENCH)
        
        try : locale.setlocale(locale.LC_ALL, 'FR')
        except : pass

        self.label_intro = wx.StaticText(self, -1, _(u"Veuillez saisir un nom pour votre nouveau fichier :"))
        self.sizer_type_staticbox = wx.StaticBox(self, -1, _(u"Type de fichier"))
        self.sizer_contenu_staticbox = wx.StaticBox(self, -1, _(u"Nom du fichier"))
        self.sizer_reseau_staticbox = wx.StaticBox(self, -1, _(u"Connexion au réseau"))
        
        self.listeTablesImportation = DATA_Tables.TABLES_IMPORTATION_OPTIONNELLES
        
        # Radio Local/Réseau
        self.radio_local = wx.RadioButton(self, -1, _(u"Local"), style = wx.RB_GROUP )
        self.radio_reseau = wx.RadioButton(self, -1, _(u"Réseau") )
        
        # Nom à saisir
        self.label_nom = wx.StaticText(self, -1, _(u"Nom de fichier :"))
        self.text_nom = wx.TextCtrl(self, -1, "")
        
        # Sélection des tables à importer
        self.checkbox_details = wx.CheckBox(self, -1, _(u"Importer les données par défaut"))
        self.checkbox_details.SetValue(True)
        self.hyperlink_details = self.Build_Hyperlink()
        
        # Panel Fichier RESEAU
        self.panelReseau = PanelReseau(self)
        self.panelReseau.Enable(False)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioLocal, self.radio_local)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioReseau, self.radio_reseau)
        
    def __set_properties(self):
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.checkbox_details.SetToolTip(wx.ToolTip(_(u"Il est recommandé de conserver cette case\n cochée afin d'importer les données par défaut")))
        self.text_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom de votre nouveau fichier.\nExemples : 'CLSH Lannilis', 'Colo Auvergne' ou 'Mon fichier à moi'...")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler la saisie")))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.radio_local.SetToolTip(wx.ToolTip(_(u"Le mode local est utilisé pour une utilisation mono-poste")))
        self.radio_reseau.SetToolTip(wx.ToolTip(_(u"Le mode réseau est utilisateur pour une utilisation multipostes. \nMySQL doit être obligatoirement installé et configuré avant utilisation.")))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 1, wx.LEFT|wx.TOP|wx.RIGHT|wx.EXPAND, 10)
        
        # Radios Local/réseau
        sizer_type = wx.StaticBoxSizer(self.sizer_type_staticbox, wx.VERTICAL)
        grid_sizer_radio = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_radio.Add(self.radio_local, 1, wx.EXPAND | wx.TOP|wx.BOTTOM, 5)
        grid_sizer_radio.Add(self.radio_reseau, 1, wx.EXPAND | wx.TOP|wx.BOTTOM, 5)
        sizer_type.Add(grid_sizer_radio, 1, wx.LEFT|wx.RIGHT, 10)
        grid_sizer_base.Add(sizer_type, 1, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        sizer_contenu = wx.StaticBoxSizer(self.sizer_contenu_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
                
        grid_sizer_contenu.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.text_nom, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add((5, 5), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        
        sizer_details = wx.BoxSizer(wx.HORIZONTAL)
        sizer_details.Add(self.checkbox_details, 0, 0, 0)
        sizer_details.Add(self.hyperlink_details, 0, 0, 0)
        grid_sizer_contenu.Add(sizer_details, 1, wx.ALL|wx.EXPAND, 0)
        
        grid_sizer_contenu.AddGrowableCol(1)
        sizer_contenu.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        # Réseau
        sizer_reseau = wx.StaticBoxSizer(self.sizer_reseau_staticbox, wx.VERTICAL)
        sizer_reseau.Add(self.panelReseau, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_reseau, 1, wx.RIGHT|wx.LEFT|wx.BOTTOM|wx.EXPAND, 10)
        
        # Boutons de commande
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        
        grid_sizer_base.AddGrowableCol(0)
        #grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        sizer_base.Add(self, 1, wx.EXPAND, 0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CentreOnScreen()
        self.grid_sizer_base = grid_sizer_base

    def OnRadioLocal(self, event):
        self.panelReseau.Enable(False)

    def OnRadioReseau(self, event):
        self.panelReseau.Enable(True)
        
    def Build_Hyperlink(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self, -1, _(u"(Détails)"), URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLUE", "BLUE", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner les données à importer")))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
    
    def OnLeftLink(self, event):
        """ Sélectionner les données à importer """
        # Préparation de la liste des données
        listeDonnees = []
        listePreSelections = []
        index = 0
        for nomCategorie, tables, selection in self.listeTablesImportation :
            listeDonnees.append(nomCategorie)
            if selection == True :
                listePreSelections.append(index)
            index += 1
                                          
        # Boîte de dialogue sélections multiples
        titre = _(u"Importation des données")
        message = _(u"Sélectionnez les données que vous souhaitez importer :")
        dlg = wx.MultiChoiceDialog(self, message, titre, listeDonnees, wx.CHOICEDLG_STYLE)
        # Coche ceux qui doivent être déjà sélectionnés dans la liste
        dlg.SetSelections(listePreSelections)
        
        # Résultats
        if dlg.ShowModal() == wx.ID_OK:
            listeSelections = dlg.GetSelections()
            index = 0
            for categorie in self.listeTablesImportation :
                if index in listeSelections :
                    self.listeTablesImportation[index][2] = True
                else:
                    self.listeTablesImportation[index][2] = False
                index += 1
            
            if len(listeSelections) == 0 :
                self.checkbox_details.SetValue(False)
                
        else:
            return
        dlg.Destroy()
        
                
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Creerunnouveaufichier")

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        
        # Validation du nom saisi
        if self.text_nom.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom de fichier valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.text_nom.SetFocus()
            return
        
        # Traitement du checkbox
        if self.checkbox_details.GetValue() == False :
            
            # Demande de confirmation pour le refus d'importer les données par défaut
            dlg = wx.MessageDialog(self, _(u"Etes-vous sûr de ne pas vouloir importer les données par défaut ?"), _(u"Importation des données"), wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES :
                dlg.Destroy()
            else:
                dlg.Destroy()
                return
            
            # Désactivation des données importées par défaut
            index = 0
            for categorie in self.listeTablesImportation :
                self.listeTablesImportation[index][2] = False
                index += 1
                
        # Version RESEAU
        if self.radio_reseau.GetValue() == True :
            port = self.panelReseau.ctrl_port.GetValue()
            hote = self.panelReseau.ctrl_hote.GetValue()
            user = self.panelReseau.ctrl_user.GetValue()
            mdp = self.panelReseau.ctrl_mdp.GetValue()
            
            try :
                port = int(port)
            except Exception as err:
                dlg = wx.MessageDialog(self, _(u"Le numéro de port n'est pas valide. \n\nErreur : %s") % err, _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.panelReseau.ctrl_port.SetFocus()
                return
            
            if hote == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom pour le serveur hôte."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.panelReseau.ctrl_hote.SetFocus()
                return
            
            if user == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom d'utilisateur."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.panelReseau.ctrl_user.SetFocus()
                return
            
            if mdp == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir un mot de passe."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.panelReseau.ctrl_mdp.SetFocus()
                return
            
            # Teste la connexion Réseau
            dictResultats = GestionDB.TestConnexionMySQL(typeTest="connexion", nomFichier=self.GetNomFichier() )
            if dictResultats["connexion"][0] == False :
                erreur = dictResultats["connexion"][1]
                dlg = wx.MessageDialog(self, _(u"La connexion au réseau MySQL est impossible. \n\nErreur : %s") % erreur, "Erreur de connexion", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        # Fermeture
        self.EndModal(wx.ID_OK)


    def GetNomFichier(self):
        # Version LOCAL
        if self.radio_local.GetValue() == True :
            nomFichier = self.text_nom.GetValue()
            return nomFichier
    
        # Version RESEAU
        if self.radio_reseau.GetValue() == True :
            port = self.panelReseau.ctrl_port.GetValue()
            hote = self.panelReseau.ctrl_hote.GetValue()
            user = self.panelReseau.ctrl_user.GetValue()
            mdp = self.panelReseau.ctrl_mdp.GetValue()
            fichier = self.text_nom.GetValue()
            nomFichier = _(u"%s;%s;%s;%s[RESEAU]%s") % (port, hote, user, mdp, fichier)
            return nomFichier
    
    def GetListeTables(self):
        listeDonnees = self.listeTablesImportation
        return listeDonnees
    
    
    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyDialog(None)
    frame_1.ShowModal()
    app.MainLoop()
