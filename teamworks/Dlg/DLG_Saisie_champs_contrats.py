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

class MyFrame(wx.Frame):
    def __init__(self, parent, title="" , IDchamp=0):
        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)
        self.parent = parent
        self.panel_base = wx.Panel(self, -1)
        self.sizer_contenu_staticbox = wx.StaticBox(self.panel_base, -1, "")
        self.label_nom = wx.StaticText(self.panel_base, -1, "Nom du champ :")
        self.text_nom = wx.TextCtrl(self.panel_base, -1, "")
        self.label_description = wx.StaticText(self.panel_base, -1, "Description :")
        self.text_description = wx.TextCtrl(self.panel_base, -1, "", style=wx.TE_MULTILINE)
        self.label_defaut = wx.StaticText(self.panel_base, -1, _(u"Valeur par défaut :"))
        self.text_defaut = wx.TextCtrl(self.panel_base, -1, "")
        self.label_exemple = wx.StaticText(self.panel_base, -1, _(u"Exemples de valeur :"))
        self.text_exemple = wx.TextCtrl(self.panel_base, -1, "")
        self.label_motCle = wx.StaticText(self.panel_base, -1, _(u"Mot-clé :"))
        self.text_motCle = wx.TextCtrl(self.panel_base, -1, "")
        self.label_motCle_aide = wx.StaticText(self.panel_base, -1, "(En majuscules et sans espaces)")
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.IDchamp = IDchamp
        if IDchamp != 0 : 
            self.Importation()
            
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.text_motCle.Bind(wx.EVT_KILL_FOCUS, self.OnTextMotCle)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un champ personnalisé"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.text_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici le nom complet du champ. Il doit être explicite.")))
        self.text_description.SetToolTip(wx.ToolTip(_(u"[Optionnel] Vous pouvez saisir une description détaillée du champ qui facilitera la saisie.")))
        self.text_defaut.SetToolTip(wx.ToolTip(_(u"[Optionnel] Saisissez ici la valeur qui apparaîtra par défaut lors d'un saisie")))
        self.text_motCle.SetToolTip(wx.ToolTip(_(u"Saisissez ici un mot-clé qui sera utilisé pour le publipostage lors de l'impression des contrats. Ce mot-clé doit être unique, en majuscule et sans caractères spéciaux.")))
        self.label_motCle_aide.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip("Cliquez ici pour valider la saisie"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip("Cliquez ici pour annuler la saisie"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        sizer_contenu = wx.StaticBoxSizer(self.sizer_contenu_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=5, cols=2, vgap=10, hgap=10)
        grid_sizer_motCle = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_contenu.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.text_nom, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_description, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.text_description, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_defaut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.text_defaut, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_exemple, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.text_exemple, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_motCle, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_motCle.Add(self.text_motCle, 0, 0, 0)
        grid_sizer_motCle.Add(self.label_motCle_aide, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(grid_sizer_motCle, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        sizer_contenu.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.Centre()

    def OnTextMotCle(self, event):
        texte = self.text_motCle.GetValue()
        if texte == "" : return
        resultat = ""
        incoherences = ""
        # Vérifie chaque caractère
        for lettre in texte :
            if lettre in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789" :
                resultat += lettre.upper()
            else:
                resultat += lettre
                incoherences += "'" + lettre + "', "
        self.text_motCle.SetValue(resultat)
        # Signale une erreur
        if incoherences != "" :
            incoherences = incoherences[:-2]
            txt = _(u"Le mot-clé que vous avez saisi n'est pas valide. Les caractères suivants ne sont pas valides : ") + incoherences + _(u"\n\nRappel : Ce mot-clé doit être en majuscules, ne peut comporter que des lettres ou des chiffres. Les espaces, accents ou autres caractères spéciaux ne sont pas acceptés.")
            dlg = wx.MessageDialog(self, txt, "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            return

    def Importation(self):
        DB = GestionDB.DB()
        req = "SELECT * FROM contrats_champs WHERE IDchamp=%d" % self.IDchamp
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()[0]
        DB.Close()
        if len(donnees) == 0: return
        # Place les valeurs dans les controles
        self.text_nom.SetValue(donnees[1])
        self.text_description.SetValue(donnees[2])
        self.text_defaut.SetValue(donnees[4])
        self.text_motCle.SetValue(donnees[3])
        self.text_exemple.SetValue(donnees[5])

    def Sauvegarde(self):
        """ Sauvegarde des données dans la base de données """
        
        # Récupération des valeurs des controles
        nom = self.text_nom.GetValue()
        description = self.text_description.GetValue()
        defaut = self.text_defaut.GetValue()
        motCle = self.text_motCle.GetValue()
        exemple = self.text_exemple.GetValue()

        DB = GestionDB.DB()
        # Création de la liste des données
        listeDonnees = [    ("nom",   nom),  
                                    ("description",    description),
                                    ("mot_cle",    motCle),
                                    ("defaut",    defaut),
                                    ("exemple",    exemple), ]
        if self.IDchamp == 0:
            # Enregistrement
            newID = DB.ReqInsert("contrats_champs", listeDonnees)
            ID = newID
        else:
            # Modification
            DB.ReqMAJ("contrats_champs", listeDonnees, "IDchamp", self.IDchamp)
            ID = self.IDchamp
        DB.Commit()
        DB.Close()
        return ID
    
    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
    
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(20)
        
    def OnBoutonAnnuler(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        # Récupération des valeurs des controles
        nom = self.text_nom.GetValue()
        description = self.text_description.GetValue()
        defaut = self.text_defaut.GetValue()
        motCle = self.text_motCle.GetValue()
        exemple = self.text_exemple.GetValue()
        
        # Vérifie que les valeurs ont été saisies
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom pour le champ."), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_nom.SetFocus()
            return
        
        if description == "" :
            txt = _(u"Vous n'avez pas saisi de description. Ce n'est pas obligatoire mais fortement conseillé pour faciliter ensuite la saisie du champ.\n\nVoulez-vous saisir une description ?")
            dlgConfirm = wx.MessageDialog(self, txt, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            reponse = dlgConfirm.ShowModal()
            dlgConfirm.Destroy()
            if reponse == wx.ID_YES:
                self.text_description.SetFocus()
                return

        if exemple == "" :
            txt = _(u"Vous n'avez pas saisi de valeurs d'exemple. Ce n'est pas obligatoire mais fortement conseillé pour faciliter ensuite la saisie du champ.\n\nVoulez-vous saisir une ou plusieurs valeurs d'exemple ?")
            dlgConfirm = wx.MessageDialog(self, txt, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            reponse = dlgConfirm.ShowModal()
            dlgConfirm.Destroy()
            if reponse == wx.ID_YES:
                self.text_description.SetFocus()
                return
                    
        if motCle == "" :
            txt = _(u"Vous devez saisir un mot-clé.\n\nCe mot-clé sera nécessaire lors de l'impression des contrats lors de la procédure de publipostage sous Word.")
            dlg = wx.MessageDialog(self, txt, "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.text_motCle.SetFocus()
            return
        
        # Vérifie la validité du mot-clé
        incoherences = ""
        for lettre in motCle :
            if lettre not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" :
                incoherences += "'" + lettre + "', "
        if incoherences != "" :
            incoherences = incoherences[:-2]
            txt = _(u"Le mot-clé que vous avez saisi n'est pas valide. Les caractères suivants ne sont pas valides : ") + incoherences + _(u"\n\nRappel : Ce mot-clé doit être en majuscules, ne peut comporter que des lettres ou des chiffres. Les espaces, accents ou autres caractères spéciaux ne sont pas acceptés.")
            dlg = wx.MessageDialog(self, txt, "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Sauvegarde
        self.Sauvegarde()
        
        # MAJ du listCtrl des valeurs de points
        if FonctionsPerso.FrameOuverte("panel_config_champsContrats") != None :
            #self.GetGrandParent().GetParent().panel_contenu.MAJ_ListCtrl()
            self.GetParent().MAJ_ListCtrl()
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    
    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "", IDchamp=1)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
