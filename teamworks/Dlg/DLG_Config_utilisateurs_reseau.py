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
import six
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import GestionDB
import FonctionsPerso
from Dlg import DLG_Saisie_utilisateur_reseau
from Utils import UTILS_Fichiers

LISTE_SUFFIXES = ("tdata", "tphotos", "tdocuments")


class Panel(wx.Panel):
    def __init__(self, parent, ID=-1, nomBase="" ):
        wx.Panel.__init__(self, parent, ID, style=wx.TAB_TRAVERSAL)
        self.nomBase = nomBase
        self.parent = parent
        
        self.active = self.ActiveAffichage()

        # Recherche de la base MySQL en cours
        if self.nomBase == "" :
            self.nomBase = self.RechercheBaseEnCours()
        
        self.barreTitre = FonctionsPerso.BarreTitre(self,  _(u"Gestion des utilisateurs réseau"), u"")
        texteIntro = _(u"Quand vous créez un fichier réseau pour Teamworks, il n'y a que vous, l'administrateur, qui avez le droit d'accéder au fichier. Vous devez donc créer des utilisateurs ou accorder une autorisation d'accès aux utilisateurs existants. Vous devez indiquer également les postes (hôtes) depuis lesquels ces utilisateurs sont autorisés à se connecter. Cochez les utilisateur autorisés à se connecter au fichier réseau chargé. Cliquez sur le bouton 'Aide' pour en savoir plus...")
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        self.listCtrl = ListCtrl(self, nomBase=self.nomBase)
        self.listCtrl.SetMinSize((20, 20)) 
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Aide.png"), wx.BITMAP_TYPE_ANY))
        if parent.GetName() != "treebook_configuration" :
            self.bouton_aide.Show(False)

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        if self.active == True :
            self.Enable(True)
        else:
            self.Enable(False)

        
    def __set_properties(self):
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un utilisateur réseau")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'utilisateur réseau sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'utilisateur réseau sélectionné dans la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base2 = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=10)
        grid_sizer_base.Add(self.barreTitre, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.label_introduction, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        grid_sizer_base2.Add(self.listCtrl, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add((5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.AddGrowableRow(3)
        grid_sizer_base2.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        grid_sizer_base2.AddGrowableRow(0)
        grid_sizer_base2.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_base2, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
##        grid_sizer_base.Add(self.label_conclusion, 0, 0, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.SetAutoLayout(True)

    def MAJpanel(self):
        self.nomBase = self.RechercheBaseEnCours()
        self.active = self.ActiveAffichage()
        self.listCtrl.MAJListeCtrl() 
        if self.active == True :
            self.Enable(True)
        else:
            self.Enable(False)
        
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Lagestiondesutilisateurs")
        
    def OnBoutonAjouter(self, event):
        dlg = DLG_Saisie_utilisateur_reseau.Dialog(self, nomUtilisateur="", nomHote="", nomBase=self.nomBase)
        dlg.ShowModal() 
        dlg.Destroy()
        self.listCtrl.MAJListeCtrl()

    def OnBoutonModifier(self, event):
        dlg = wx.MessageDialog(self, _(u"Actuellement, il n'est pas encore possible de modifier un utilisateur. \nVous devez donc supprimer l'utilisateur et le re-créer."), "Information", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()      
        
    def OnBoutonSupprimer(self, event):
        dlg = wx.MessageDialog(self, _(u"Actuellement, il n'est pas encore possible de modifier un utilisateur. \nVous devez donc supprimer l'utilisateur et le re-créer."), "Information", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()      
        
    def OnBoutonSupprimer(self, event):
        index = self.listCtrl.GetFirstSelected()

        # Vérifie qu'un item a bien été sélectionné
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un utilisateur à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        nom = self.listCtrl.listeDonnees[index][0]
        hote = self.listCtrl.listeDonnees[index][1]
        
        # Vérifie que ce n'est pas ROOT
        if nom == "root" :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer le compte administrateur !"), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Demande de confirmation
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer cet utilisateur ? \n\n> %s@%s") % (nom, hote)))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        # Suppression
        DB = GestionDB.DB()
        DB.ExecuterReq("USE mysql;")

        # Suppression de l'autorisation à la base en cours
        for suffixe in LISTE_SUFFIXES :
            req = "SELECT host, db, user FROM db WHERE user='%s' and db='%s' and host='%s';" % (nom, u"%s_%s" % (self.nomBase, suffixe), hote)
            DB.ExecuterReq(req)
            donnees = DB.ResultatReq()
            if len(donnees) > 0 :
                req = u"""REVOKE ALL ON %s.* FROM '%s'@'%s';
                """ % (u"%s_%s" % (self.nomBase, suffixe), nom, hote)
                DB.ExecuterReq(req)

        # Suppression de l'hôte :
        req = "DELETE FROM user WHERE user='%s' and host='%s';" % (nom, hote)
        DB.ExecuterReq(req)
        
        req = _(u"FLUSH PRIVILEGES;")
        DB.ExecuterReq(req)
        DB.Close()

        # MàJ du ListCtrl
        self.listCtrl.MAJListeCtrl()
        
    def ActiveAffichage(self):
        # Active le panneau si le fichier en cours est un fichier réseau
        if self.parent.GetName() != "treebook_configuration" :
            return True
        nomDB = FonctionsPerso.GetNomDB()
        if "[RESEAU]" in nomDB :
            port, hote, user, mdp = nomDB.split(";")
            if user == "root" :
                return True
            else:
                return False
        else:
            return False
        
    def RechercheBaseEnCours(self):
        nomFichier = ""
        try :
            topWindow = wx.GetApp().GetTopWindow()
            nomWindow = topWindow.GetName()
        except :
            nomWindow = None
        if nomWindow == "general" : 
            # Si la frame 'General' est chargée, on y récupère le dict de config
            nomFichier = topWindow.userConfig["nomFichier"]
        else:
            # Récupération du nom de la DB directement dans le fichier de config sur le disque dur
            from Utils import UTILS_Config
            cfg = UTILS_Config.FichierConfig()
            nomFichier = cfg.GetItemConfig("nomFichier")
        if "[RESEAU]" in nomFichier :
            nomFichier = nomFichier[nomFichier.index("[RESEAU]") + 8:]
        return nomFichier


class ListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent, nomBase = ""):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        CheckListCtrlMixin.__init__(self)
        self.parent = parent
        self.nomBase = nomBase
        
        if self.GetGrandParent().GetName() != "treebook_configuration" :
            self.Remplissage()
        
    def Remplissage(self, select=None):
        if self.parent.active == False :
            # Si l'utilisateur n'est pas administrateur : on arrete
            return
        
        self.listeDonnees = self.Importation()

        # Création des colonnes
        self.InsertColumn(0, _(u"Accès"))
        self.SetColumnWidth(0, 55)
        self.InsertColumn(1, _(u"Nom de l'utilisateur"))
        self.SetColumnWidth(1, 130)
        self.InsertColumn(2, _(u"Hôte de connexion"))
        self.SetColumnWidth(2, 300)
        self.InsertColumn(3, _(u"Mot de passe"))
        self.SetColumnWidth(3, 90)
        
        # Remplissage avec les valeurs
        self.remplissage = True
        indexListe = 0
        for user, host, password, autorisation in self.listeDonnees :
            if user == "root" : 
                autorisation = True
                
            if autorisation == True :
                autorisationStr = "Oui"
            else:
                autorisationStr = "Non"
            index = self.InsertStringItem(six.MAXSIZE, autorisationStr)
            
            if user == "root" :
                user = _(u"root (Administrateur)")
            self.SetStringItem(index, 1, user)
            
            if host == "%" : host = _(u"Connexion depuis n'importe quel hôte")
            elif host == "localhost" : host = _(u"Connexion uniquement depuis le serveur principal")
            else : host = _(u"Connexion uniquement depuis l'hôte %s") % host
            self.SetStringItem(index, 2, host)
            
            if password != "" and password != None : 
                password = "Oui"
            else:
                password = "Non"
            self.SetStringItem(index, 3, password)
            
            self.SetItemData(index, indexListe)
                
            # Check
            if autorisation == True :
                self.CheckItem(index) 
            
            indexListe += 1
        
        self.remplissage = False

    def MAJListeCtrl(self, select=None):
        self.ClearAll()
        self.Remplissage(select)

    def OnCheckItem(self, index, flag):
        """ Ne fait rien si c'est le remplissage qui coche la case ! """
        if self.remplissage == False :
            nom, hote = self.listeDonnees[index][0], self.listeDonnees[index][1]
            
            # Vérifie que ce n'est pas ROOT
            if nom == "root" :
                self.remplissage = True
                self.CheckItem(index) 
                self.remplissage = False
                dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas modifier le compte administrateur"), "Information", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        
            # Enregistre le changement d'autorisation
            if self.IsChecked(index) == False :
                self.SetAutorisation(False, nom, hote)
                self.listeDonnees[index][3] = False
                self.SetStringItem(index, 0, "Non")
            else:
                etat = self.SetAutorisation(True, nom, hote)
                self.listeDonnees[index][3] = True
                self.SetStringItem(index, 0, "Oui")

        else:
            pass

    def SetAutorisation(self, etat=True, nom="", hote=""):
        # Création de l'autorisation à la base en cours
        DB = GestionDB.DB()
        DB.ExecuterReq("USE mysql;")
        
        if etat == True :
            for suffixe in LISTE_SUFFIXES :
                req = u"""GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,DROP,ALTER,EXECUTE ON %s.* TO '%s'@'%s' ;
                """ % (u"%s_%s" % (self.nomBase, suffixe), nom, hote)
                DB.ExecuterReq(req)
        else:
            # Si l'autorisation existe déjà mais est décochée : on efface cette autorisation
            for suffixe in LISTE_SUFFIXES :
                req = "SELECT host, db, user FROM db WHERE user='%s' and db='%s' and host='%s';" % (nom, u"%s_%s" % (self.nomBase, suffixe), hote)
                DB.ExecuterReq(req)
                donnees = DB.ResultatReq()
                if len(donnees) > 0 :
                    req = u"""REVOKE ALL ON %s.* FROM '%s'@'%s';
                    """ % (u"%s_%s" % (self.nomBase, suffixe), nom, hote)
                    DB.ExecuterReq(req)            
        req = _(u"FLUSH PRIVILEGES;")
        DB.ExecuterReq(req)
        DB.Close()
        

    def Importation(self):
        # Importation des données de la liste
        DB = GestionDB.DB()
        
        # Recherche des utilisateurs MySQL
        req = "SELECT Host, User, Password FROM `mysql`.`user` ORDER BY User, Host;"
        DB.ExecuterReq(req)
        listeUtilisateurs = DB.ResultatReq()
                
        # Recherche des autorisations pour la base en cours
        req = "SELECT host, user FROM `mysql`.`db` WHERE Db='%s';" % _(u"%s_tdata") % self.nomBase
        DB.ExecuterReq(req)
        listeAutorisations = DB.ResultatReq()
        DB.Close()
        
        # Création de la liste de données
        listeDonnees = []
        for host, user, password in listeUtilisateurs :
            # Recherche s'il y a une autorisation pour la base en cours
            autorisation = False
            for hostTmp, userTmp in listeAutorisations :
                if host==hostTmp and user==userTmp :
                    autorisation = True
            listeDonnees.append([user, host, password, autorisation])
        return listeDonnees
        



class Dialog(wx.Dialog):
    def __init__(self, parent, title="", nomBase=""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        self.panel_base = wx.Panel(self, -1)
        self.panel_contenu = Panel(self.panel_base, nomBase=nomBase)
        self.panel_contenu.barreTitre.Show(False)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Fermer"), cheminImage=Chemins.GetStaticPath("Images/32x32/Fermer.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        self.bouton_annuler.Show(False)
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)

        self.SetMinSize((500, 350))
        self.SetSize((700, 400))
        self.CentreOnScreen()

    def __set_properties(self):
        self.SetTitle(_(u"Gestion des utilisateurs réseau"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler et fermer")))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.ALL|wx.EXPAND, 0)
        sizer_pages.Add(self.panel_contenu, 1, wx.EXPAND | wx.TOP, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        self.Centre()
        self.sizer_pages = sizer_pages

    def Onbouton_aide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Lagestiondesutilisateurs")
            
    def Onbouton_annuler(self, event):
        self.MAJparents()
        # Fermeture
        self.EndModal(wx.ID_CANCEL)
        
    def Onbouton_ok(self, event):
        self.MAJparents()
        # Fermeture
        self.EndModal(wx.ID_OK)

    def MAJparents(self):
        if self.parent == None and FonctionsPerso.FrameOuverte("panel_accueil") != None :
            # Mise à jour de la page d'accueil
            topWindow = wx.GetApp().GetTopWindow() 
            topWindow.toolBook.GetPage(0).MAJpanel() 
        
        
        
if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None, "")
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()