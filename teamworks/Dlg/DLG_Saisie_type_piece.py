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


class Dialog(wx.Dialog):
    def __init__(self, parent, ID=-1, title=_(u"Saisie d'un type de pièce"), IDtype_piece=0):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDtype_piece = IDtype_piece
        
        self.panel_base = wx.Panel(self, -1)
        self.sizer_duree_staticbox = wx.StaticBox(self.panel_base, -1, _(u"2. Durée de validité"))
        self.sizer_diplomes_staticbox = wx.StaticBox(self.panel_base, -1, _(u"3. Qualifications associés"))
        self.sizer_nom_staticbox = wx.StaticBox(self.panel_base, -1, _(u"1. Nom du type de pièce (ex : Diplôme BAFA ou Certificat médical)"))
        self.label_nom = wx.StaticText(self.panel_base, -1, "Nom :")
        self.text_nom = wx.TextCtrl(self.panel_base, -1, "")
        self.radio_duree_1 = wx.RadioButton(self.panel_base, -1, _(u"Validité illimitée"), style=wx.RB_GROUP)
        self.radio_duree_2 = wx.RadioButton(self.panel_base, -1, _(u"Validité limitée : "))
        self.label_jours = wx.StaticText(self.panel_base, -1, "Jours :")
        self.spin_jours = wx.SpinCtrl(self.panel_base, -1, "", min=0, max=100)
        self.label_mois = wx.StaticText(self.panel_base, -1, "Mois :")
        self.spin_mois = wx.SpinCtrl(self.panel_base, -1, "", min=0, max=100)
        self.label_annees = wx.StaticText(self.panel_base, -1, _(u"Années :"))
        self.spin_annees = wx.SpinCtrl(self.panel_base, -1, "", min=0, max=100)
        self.radio_diplomes_1 = wx.RadioButton(self.panel_base, -1, _(u"Pour tous les employés"), style=wx.RB_GROUP)
        self.radio_diplomes_2 = wx.RadioButton(self.panel_base, -1, _(u"Pour les employés possédant la ou les qualifications suivantes :"))
        
        #self.list_diplomes = wx.ListCtrl(self.panel_base, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.ImportationDiplomes()
        self.list_diplomes = wx.CheckListBox(self.panel_base, -1, choices=self.ListeDiplomesPourLBox)
        # ----------------------------------------------------------------------------------------------
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()

        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDuree, self.radio_duree_1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDuree, self.radio_duree_2)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDiplomes, self.radio_diplomes_1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDiplomes, self.radio_diplomes_2)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

        # Règle les RadioBox à l'ouverture de la fenêtre
        self.OnRadioDuree("")
        self.OnRadioDiplomes("")

        # Si Modification -> importation des données
        if IDtype_piece == 0 :
            self.SetTitle(_(u"Saisie d'un nouveau type de pièce"))
        else:
            self.SetTitle(_(u"Modification d'un type de pièce"))
            self.Importation()

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un type de pièce"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.text_nom.SetToolTip(wx.ToolTip(_(u"Saisissez ici un nom de type de pièce. Par exemple : 'Diplôme B.A.F.A.'...")))
        self.radio_duree_1.SetToolTip(wx.ToolTip(_(u"Sélectionnez 'Illimitée' si le type de pièce est valable à vie. Comme le diplôme du BAFA par exemple...")))
        self.radio_duree_2.SetToolTip(wx.ToolTip(_(u"Sélectionnez 'Limitée' si vous pouvez définir une durée pour le type de pièce. \nCette durée peut être approximative. Par exemple, pour un certificat valable \n1 an et 6 mois en général, vous devez saisir '1' dans la case Années et '6' dans la case mois")))
        self.spin_jours.SetMinSize((60, -1))
        self.spin_mois.SetMinSize((60, -1))
        self.spin_annees.SetMinSize((60, -1))
        self.radio_diplomes_1.SetToolTip(wx.ToolTip(_(u"Avec cette option, toutes les personnes employées devront fournir ce type de pièce quelque soit leur poste et leurs diplômes.")))
        self.radio_diplomes_2.SetToolTip(wx.ToolTip(_(u"Sélectionnez les diplômes que vous souhaitez associer avec cette pièce")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide sur cette fenêtre")))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        sizer_diplomes = wx.StaticBoxSizer(self.sizer_diplomes_staticbox, wx.VERTICAL)
        grid_sizer_diplomes = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        sizer_duree = wx.StaticBoxSizer(self.sizer_duree_staticbox, wx.VERTICAL)
        grid_sizer_duree1 = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_duree2 = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_duree3 = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        sizer_nom = wx.StaticBoxSizer(self.sizer_nom_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.text_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.AddGrowableCol(1)
        sizer_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_nom, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_duree1.Add(self.radio_duree_1, 0, 0, 0)
        grid_sizer_duree2.Add(self.radio_duree_2, 0, 0, 0)
        grid_sizer_duree3.Add(self.label_jours, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_duree3.Add(self.spin_jours, 0, 0, 0)
        grid_sizer_duree3.Add(self.label_mois, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_duree3.Add(self.spin_mois, 0, 0, 0)
        grid_sizer_duree3.Add(self.label_annees, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_duree3.Add(self.spin_annees, 0, 0, 0)
        grid_sizer_duree2.Add(grid_sizer_duree3, 1, wx.LEFT|wx.EXPAND, 20)
        grid_sizer_duree1.Add(grid_sizer_duree2, 1, wx.EXPAND, 0)
        sizer_duree.Add(grid_sizer_duree1, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_duree, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_diplomes.Add(self.radio_diplomes_1, 0, 0, 0)
        grid_sizer_diplomes.Add(self.radio_diplomes_2, 0, 0, 0)
        grid_sizer_diplomes.Add(self.list_diplomes, 1, wx.LEFT|wx.EXPAND, 20)
        grid_sizer_diplomes.AddGrowableRow(2)
        grid_sizer_diplomes.AddGrowableCol(0)
        sizer_diplomes.Add(grid_sizer_diplomes, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_diplomes, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((15, 15), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()

    def OnRadioDuree(self, event):
        if self.radio_duree_1.GetValue() == True:
            self.label_jours.Enable(False)
            self.spin_jours.Enable(False)
            self.label_mois.Enable(False)
            self.spin_mois.Enable(False)
            self.label_annees.Enable(False)
            self.spin_annees.Enable(False)
        else:
            self.label_jours.Enable(True)
            self.spin_jours.Enable(True)
            self.label_mois.Enable(True)
            self.spin_mois.Enable(True)
            self.label_annees.Enable(True)
            self.spin_annees.Enable(True)

    def OnRadioDiplomes(self, event):
        if self.radio_diplomes_1.GetValue() == True:
            self.list_diplomes.Enable(False)
        else:
            self.list_diplomes.Enable(True)

    def ImportationDiplomes(self):
        self.ListeDiplomesData = []
        self.ListeDiplomesPourLBox = []
        
        DB = GestionDB.DB()
        req = "SELECT * FROM types_diplomes ORDER BY nom_diplome"
        DB.ExecuterReq(req)
        listeDiplomes = DB.ResultatReq()
        DB.Close()

        for typeDiplome in listeDiplomes:
            key = typeDiplome[0]
            nom = typeDiplome[1]

            # Création d'une liste pour remplir le listBox
            self.ListeDiplomesData.append((key, nom))
            self.ListeDiplomesPourLBox.append(nom)

    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(50)

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):

        # Vérification des données saisies
        textNom = self.text_nom.GetValue()
        if textNom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement donner un nom à ce nouveau type de pièce."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.text_nom.SetFocus()
            return

        jours = int(self.spin_jours.GetValue())
        mois = int(self.spin_mois.GetValue())
        annees = int(self.spin_annees.GetValue())

        if jours == 0 and mois == 0 and annees == 0 and self.radio_duree_2.GetValue() == True:
            dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné une durée de validité limitée. \nVous devez donc saisir un nombre de jours et/ou de mois et/ou d'années."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.spin_jours.SetFocus()
            return

        if self.radio_diplomes_2.GetValue() == True:
            NbreCoches = 0
            NbreItems = len(self.ListeDiplomesData)
            for index in range(0, NbreItems):
                if self.list_diplomes.IsChecked(index):
                    NbreCoches += 1
            if NbreCoches == 0:
                dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné d'associer des diplômes. Vous devez donc sélectionner un ou plusieurs diplômes dans la liste proposée."), "Information", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.spin_jours.SetFocus()
                return
            
        # Procédure d'enregistrement des données
        self.Sauvegarde()

        # MàJ du listCtrl du panel de configuration
        self.parent.listCtrl_TypesPieces.MAJListeCtrl()

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
        
        

        # ------------------------- SAUVEGARDE ET IMPORTATION ----------------------------------

    def Sauvegarde(self):
        """ Sauvegarde des données dans la base de données """
        
        varIDtype_piece = self.IDtype_piece
        varNom_Piece = self.text_nom.GetValue()

        # Durée validité
        if self.radio_duree_1.GetValue() == True:
            VarDureeValidite = "j0-m0-a0"
        else:
            VarDureeValidite = "j%d-m%d-a%d" % (int(self.spin_jours.GetValue()), int(self.spin_mois.GetValue()), int(self.spin_annees.GetValue()),)

        # Associations diplomes
        VarIDtypesDiplomes = []
        if self.radio_diplomes_1.GetValue() == True:
            VarIDtypesDiplomes.append(0)
        else:
            # Recherche des diplomes cochés
            NbreItems = len(self.ListeDiplomesData)
            for index in range(0, NbreItems):
                if self.list_diplomes.IsChecked(index):
                    VarIDtypesDiplomes.append(self.ListeDiplomesData[index][0])


        # Enregistrement des données de la table TYPES_PIECES ----------------------------
        listeDonnees = [    ("nom_piece",       varNom_Piece),
                            ("duree_validite",  VarDureeValidite),
                        ]
        
        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()

        if varIDtype_piece == 0:
            # Enregistrement d'une nouvelle coordonnée
            newID = DB.ReqInsert("types_pieces", listeDonnees)
            varIDtype_piece = newID
        else:
            # Modification de la coordonnée
            DB.ReqMAJ("types_pieces", listeDonnees, "IDtype_piece", varIDtype_piece)


        # Enregistrement des données de la table DIPLOMES_PIECES --------------------------
        
        for IDtype_diplome in VarIDtypesDiplomes:

            # Recherche d'abord si cette association existe déjà dans la base de données
            req = "SELECT * FROM diplomes_pieces WHERE IDtype_diplome=%d AND IDtype_piece=%d" % (IDtype_diplome, varIDtype_piece)
            DB.ExecuterReq(req)
            resultat = DB.ResultatReq()

            if len(resultat) == 0 :

                # On enregistre l'association dans la base
                listeDonnees = [    ("IDtype_diplome",  IDtype_diplome),
                                    ("IDtype_piece",    varIDtype_piece),
                                ]
                
                DB.ReqInsert("diplomes_pieces", listeDonnees)


        # Suppression des associations déjà existantes de la table DIPLOMES_PIECES qui ont été décochées
        req = "SELECT * FROM diplomes_pieces WHERE IDtype_piece=%d" % varIDtype_piece
        DB.ExecuterReq(req)
        resultat = DB.ResultatReq()

        for item in resultat:
            if item[1] not in VarIDtypesDiplomes:
                # Si pas dans la liste -> suppression de l'association
                req = "DELETE FROM diplomes_pieces WHERE IDdiplome_piece=%d" % item[0]
                DB.ExecuterReq(req)

        DB.Commit()
        DB.Close()
                

    def Importation(self,):
        """ Importation des donnees de la base """

        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        req = "SELECT * FROM types_pieces WHERE IDtype_piece = %d" % self.IDtype_piece
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        if len(donnees) > 0 : 
            donnees = donnees[0]
        else:
            return
        
        # Placement des données dans les contrôles
        varNomPiece = donnees[1]
        self.text_nom.SetValue(varNomPiece)
        
        varDureeValidite = donnees[2]
        posM = varDureeValidite.find("m")
        posA = varDureeValidite.find("a")
        jours = int(varDureeValidite[1:posM-1])
        mois = int(varDureeValidite[posM+1:posA-1])
        annees = int(varDureeValidite[posA+1:])

        if jours == 0 and mois == 0 and annees == 0:
            self.radio_duree_1.SetValue(True)
            self.radio_duree_2.SetValue(False)
        else:
            self.radio_duree_1.SetValue(False)
            self.radio_duree_2.SetValue(True)
            self.spin_jours.SetValue(jours)
            self.spin_mois.SetValue(mois)
            self.spin_annees.SetValue(annees)

        # Réglages des radioBox pour la durée de validité
        self.OnRadioDuree("")

        # Recherche des associations dans la base de données
        listeDiplomes = []
        req = "SELECT * FROM diplomes_pieces WHERE IDtype_piece = %d" % self.IDtype_piece
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()

        for item in donnees:
            listeDiplomes.append(item[1])

        if len(listeDiplomes) == 0:
            return

        if listeDiplomes[0] == 0:
            self.radio_diplomes_1.SetValue(True)
            self.radio_diplomes_2.SetValue(False)
        else:
            self.radio_diplomes_1.SetValue(False)
            self.radio_diplomes_2.SetValue(True)
            # On coche les diplomes
            index = 0
            for item in self.ListeDiplomesData:
                if item[0] in listeDiplomes:
                    self.list_diplomes.Check(index)
                index += 1

        # Réglages des radioBox pour les diplomes associés
        self.OnRadioDiplomes("")



            
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, -1, IDtype_piece=0)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
