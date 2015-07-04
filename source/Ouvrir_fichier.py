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
import os

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
        
        self.label_fichier = wx.StaticText(self, -1, _(u"Fichier :"), size=(-1, -1), style=wx.ALIGN_RIGHT)
        self.ctrl_fichier = wx.TextCtrl(self, -1, "", size=(-1, -1))
        
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
        
        # Nom du fichier
        grid_sizer_base.Add(self.label_fichier, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 0)
        grid_sizer_base.Add(self.ctrl_fichier, 1, wx.EXPAND | wx.ALL, 0)
        
        grid_sizer_base.AddGrowableCol(1)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        
        self.ctrl_port.SetToolTipString(_(u"Le numéro de port est 3306 par défaut."))
        self.ctrl_hote.SetToolTipString(_(u"Indiquez ici le nom du serveur hôte."))
        self.ctrl_user.SetToolTipString(_(u"Indiquez ici le nom de l'utilisateur. Ce nom doit avoir été validé par le créateur du fichier."))
        self.ctrl_mdp.SetToolTipString(_(u"Indiquez ici le mot de passe nécessaire à la connexion à MySQL"))
        self.ctrl_fichier.SetToolTipString(_(u"Indiquez ici le nom du fichier (base de données) à laquelle vous souhaitez vous connectez."))
        
        
class MyDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, title=_(u"Ouverture d'un fichier"))
        self.parent = parent
        
        self.label_intro = wx.StaticText(self, -1, _(u"Veuillez sélectionner le fichier à ouvrir :"))
        self.sizer_type_staticbox = wx.StaticBox(self, -1, _(u"Type de fichier"))
        self.sizer_contenu_staticbox = wx.StaticBox(self, -1, "Nom du fichier")
        
        # Radio Local/Réseau
        self.radio_local = wx.RadioButton(self, -1, _(u"Local"), style = wx.RB_GROUP )
        self.radio_reseau = wx.RadioButton(self, -1, _(u"Réseau") )
        
        # ListBox Fichier LOCAL
        self.listeFichiers = self.CreateListeFichiers()
        self.listbox = wx.ListBox(self,  choices=self.listeFichiers, style=wx.LB_SINGLE)
        self.listbox.SetMinSize((200, 160))
        
        # Panel Fichier RESEAU
        self.panelReseau = PanelReseau(self)
        
        # Boutons de commande
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        self.panelReseau.Show(False)
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioLocal, self.radio_local)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioReseau, self.radio_reseau)
        
    def __set_properties(self):
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler la saisie"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.radio_local.SetToolTipString(_(u"Le mode local est utilisé pour une utilisation mono-poste"))
        self.radio_reseau.SetToolTipString(_(u"Le mode réseau est utilisateur pour une utilisation multipostes. \nMySQL doit être obligatoirement installé et configuré avant utilisation."))
        self.SetMinSize((350, 300))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
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
        grid_sizer_contenu = wx.FlexGridSizer(rows=5, cols=1, vgap=0, hgap=0)
        
        grid_sizer_contenu.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 10)
        grid_sizer_contenu.Add(self.panelReseau, 1, wx.EXPAND | wx.ALL, 10)
        grid_sizer_contenu.AddGrowableCol(0)
        sizer_contenu.Add(grid_sizer_contenu, 1, wx.EXPAND | wx.ALL, 0)
        
        grid_sizer_base.Add(sizer_contenu, 1, wx.EXPAND | wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)
        
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        sizer_base.Add(self, 1, wx.EXPAND, 0)
##        self.SetSizer(sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.Centre()       
    
    def OnRadioLocal(self, event):
        self.listbox.Show(True)
        self.panelReseau.Show(False)
        self.Layout()

    def OnRadioReseau(self, event):
        self.listbox.Show(False)
        self.panelReseau.Show(True)
        self.Layout()
    
    def CreateListeFichiers(self):
        """ Trouver les fichiers présents dur le DD """
        listeFichiersTmp = os.listdir("Data/")
        listeFichiers = []
        for fichier in listeFichiersTmp :
            # Nouvelles versions de fichier
            if fichier[-10:] == "_TDATA.dat" : listeFichiers.append(fichier[:-10])
            # Anciennes versions de fichier
            if fichier[-4:] == ".twk" : listeFichiers.append(fichier[:-4])
        listeFichiers.sort()
        return listeFichiers
                
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(47)

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        # Validation de la sélection
        
        # Version LOCAL
        if self.radio_local.GetValue() == True :
            selections = self.listbox.GetSelections()
            if len(selections) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous n'avez fait aucune sélection"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
        
        # Version RESEAU
        if self.radio_reseau.GetValue() == True :
            port = self.panelReseau.ctrl_port.GetValue()
            hote = self.panelReseau.ctrl_hote.GetValue()
            user = self.panelReseau.ctrl_user.GetValue()
            mdp = self.panelReseau.ctrl_mdp.GetValue()
            fichier = self.panelReseau.ctrl_fichier.GetValue()
            
            try :
                port = int(port)
            except Exception, err:
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
            
            if fichier == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom de fichier."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.panelReseau.ctrl_fichier.SetFocus()
                return
            
        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetNomFichier(self):
        # Version LOCAL
        if self.radio_local.GetValue() == True :
            selections = self.listbox.GetSelections()
            nomFichier = self.listeFichiers[selections[0]]
            nomFichier = nomFichier.decode("iso-8859-15")
            return nomFichier
    
        # Version RESEAU
        if self.radio_reseau.GetValue() == True :
            port = self.panelReseau.ctrl_port.GetValue()
            hote = self.panelReseau.ctrl_hote.GetValue()
            user = self.panelReseau.ctrl_user.GetValue()
            mdp = self.panelReseau.ctrl_mdp.GetValue()
            fichier = self.panelReseau.ctrl_fichier.GetValue()
            nomFichier = _(u"%s;%s;%s;%s[RESEAU]%s") % (port, hote, user, mdp, fichier)
            return nomFichier
            
    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyDialog(None)
    frame_1.ShowModal()
    app.MainLoop()
