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
import wx.lib.masked as masked
import GestionDB
import datetime
import FonctionsPerso
from Ctrl import CTRL_Vignettes_documents

class Dialog(wx.Dialog):
    def __init__(self, parent, title=_(u"Saisie des pi�ces"), IDpiece=0, IDpersonne=0, IDtypePiece=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDpersonne = IDpersonne
        self.IDpiece = IDpiece
        self.selection1 = ("NoSelect",) # Pour m�moriser la s�lection dans la liste des pi�ces � fournir
        self.selection2 = ("NoSelect",) # Pour m�moriser la s�lection dans la liste des autres pi�ces
        
        self.panel_base = wx.Panel(self, -1)
        self.sizer_date_debut_staticbox = wx.StaticBox(self.panel_base, -1, _(u"2. Saisissez la date de d�but"))
        self.sizer_date_fin_staticbox = wx.StaticBox(self.panel_base, -1, "3. Saisissez la date de fin")
        self.sizer_type_staticbox = wx.StaticBox(self.panel_base, -1, _(u"1. S�lectionnez un type de pi�ce"))
        self.radio_pieces_1 = wx.RadioButton(self.panel_base, -1, _(u"Dans la liste de pi�ces que la personne doit fournir :"), style = wx.RB_GROUP)
        
        self.list_ctrl_pieces = ListCtrl_Pieces(self.panel_base, -1)
        
        self.radio_pieces_2 = wx.RadioButton(self.panel_base, -1, _(u"Dans la liste des autres types de pi�ces :"))

        # Importe les dur�es de validit� des types de pi�ces
        self.RemplissageAutresTypes()

        self.combo_box_autres = wx.ComboBox(self.panel_base, -1, choices=self.ListeAutresPourCombo, style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.label_date_debut = wx.StaticText(self.panel_base, -1, "Date :")
        self.text_date_debut = masked.TextCtrl(self.panel_base, -1, "", style=wx.TE_CENTRE, mask = "##/##/####")
        self.radio_date_fin_1 = wx.RadioButton(self.panel_base, -1, "Date :", style = wx.RB_GROUP)
        self.text_date_fin = masked.TextCtrl(self.panel_base, -1, "", style=wx.TE_CENTRE, mask = "##/##/####")
        self.radio_date_fin_2 = wx.RadioButton(self.panel_base, -1, _(u"Validit� illimit�e"))

        # Pages captur�es
        self.sizer_pages_staticbox = wx.StaticBox(self.panel_base, -1, _(u"Documents associ�s"))
        self.ctrl_pages = CTRL_Vignettes_documents.CTRL(self.panel_base, IDpiece=self.IDpiece, style=wx.BORDER_SUNKEN)
        self.bouton_ajouter_page = wx.BitmapButton(self.panel_base, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_page = wx.BitmapButton(self.panel_base, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_visualiser_page = wx.BitmapButton(self.panel_base, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_zoom_plus = wx.BitmapButton(self.panel_base, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/zoom_plus.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_zoom_moins = wx.BitmapButton(self.panel_base, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/zoom_moins.png"), wx.BITMAP_TYPE_ANY))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()

        # D�sactive le combobox � l'ouverture de la frame
        self.combo_box_autres.Enable(False)

        # Si Modification -> importation des donn�es
        if IDpiece == 0 :
            self.SetTitle(_(u"Saisie d'une pi�ce"))
        else:
            self.SetTitle(_(u"Modification d'une pi�ce"))
            self.Importation()

        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPieces, self.radio_pieces_1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPieces, self.radio_pieces_2)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDateFin, self.radio_date_fin_1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioDateFin, self.radio_date_fin_2)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_TEXT, self.OnDateDebut, self.text_date_debut)
        self.Bind(wx.EVT_COMBOBOX, self.OnComboBoxAutres, self.combo_box_autres)

        self.Bind(wx.EVT_BUTTON, self.AjouterPage, self.bouton_ajouter_page)
        self.Bind(wx.EVT_BUTTON, self.SupprimerPage, self.bouton_supprimer_page)
        self.Bind(wx.EVT_BUTTON, self.VisualiserPage, self.bouton_visualiser_page)
        self.Bind(wx.EVT_BUTTON, self.ZoomPlus, self.bouton_zoom_plus)
        self.Bind(wx.EVT_BUTTON, self.ZoomMoins, self.bouton_zoom_moins)

        # Si c'est une saisie de pi�ce � partir du listeCtrl des pi�ces � fournir de la fiche individuelle
        if IDtypePiece != None :
            self.list_ctrl_pieces.SetIDtypePieceDefaut(IDtypePiece)

    def __set_properties(self):
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.radio_pieces_1.SetValue(1)
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.radio_pieces_2.SetToolTip(wx.ToolTip(_(u"Cliquez ici si la pi�ce que vous souhaitez enregistrer n'est pas dans la liste des pi�ces obligatoires � fournir")))
        self.list_ctrl_pieces.SetToolTip(wx.ToolTip(_(u"S�lectionnez un type de pi�ce en cliquant sur son nom")))
        self.text_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de d�but de validit�.\nRemarque : Il s'agit bien de la date d'emission de la pi�ce \n(par exemple, la date d'obtention d'un dipl�me) et non la date � laquelle vous avez re�ue la pi�ce")))
        self.text_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date d'expiration de la pi�ce")))
        self.radio_date_fin_1.SetToolTip(wx.ToolTip(_(u"Cliquez ici si la pi�ce a une dur�e de validit� limit�e dans le temps")))
        self.radio_date_fin_2.SetToolTip(wx.ToolTip(_(u"Cliquez ici si la pi�ce que vous souhaitez enregistrer a une dur�e de validit� illimit�e")))

        self.bouton_ajouter_page.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter un document")))
        self.bouton_supprimer_page.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le document s�lectionn�")))
        self.bouton_visualiser_page.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour visualiser le document s�lectionn�")))
        self.bouton_zoom_plus.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour agrandir les vignettes")))
        self.bouton_zoom_moins.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour r�duire les vignettes")))
        self.SetMinSize((640, 500)) 

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_horiz = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_gauche = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Listes de types de pi�ces
        sizer_type = wx.StaticBoxSizer(self.sizer_type_staticbox, wx.VERTICAL)
        grid_sizer_3 = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_3.Add(self.radio_pieces_1, 0, 0, 0)
        grid_sizer_3.Add(self.list_ctrl_pieces, 1, wx.LEFT|wx.EXPAND, 17)
        grid_sizer_3.Add(self.radio_pieces_2, 0, 0, 0)
        grid_sizer_3.Add(self.combo_box_autres, 0, wx.LEFT|wx.EXPAND, 17)
        grid_sizer_3.AddGrowableRow(1)
        grid_sizer_3.AddGrowableCol(0)
        sizer_type.Add(grid_sizer_3, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_gauche.Add(sizer_type, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 0)
        
        # Date d�but
        sizer_date_debut = wx.StaticBoxSizer(self.sizer_date_debut_staticbox, wx.VERTICAL)
        grid_sizer_date_debut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_date_debut.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date_debut.Add(self.text_date_debut, 0, 0, 0)
        sizer_date_debut.Add(grid_sizer_date_debut, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_dates = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_dates.Add(sizer_date_debut, 1, wx.EXPAND, 0)
        
        # Date de fin
        sizer_date_fin = wx.StaticBoxSizer(self.sizer_date_fin_staticbox, wx.VERTICAL)
        grid_sizer_date_fin_2 = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_date_fin_2.Add(self.radio_date_fin_1, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date_fin_2.Add(self.text_date_fin, 0, 0, 0)
        grid_sizer_date_fin_1 = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_date_fin_1.Add(grid_sizer_date_fin_2, 1, wx.EXPAND, 0)
        grid_sizer_date_fin_1.Add(self.radio_date_fin_2, 0, 0, 0)
        sizer_date_fin.Add(grid_sizer_date_fin_1, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_dates.Add(sizer_date_fin, 1, wx.EXPAND, 0)
        grid_sizer_dates.AddGrowableCol(0)
        grid_sizer_dates.AddGrowableCol(1)
        
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.Add(grid_sizer_dates, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 0)
        grid_sizer_horiz.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        # Pages
        sizer_pages = wx.StaticBoxSizer(self.sizer_pages_staticbox, wx.VERTICAL)
        
        grid_sizer_pages = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        grid_sizer_pages.Add(self.ctrl_pages, 0, wx.EXPAND, 0)
        grid_sizer_pages.AddGrowableRow(0)
        grid_sizer_pages.AddGrowableCol(0)
        
        grid_sizer_commandes_pages = wx.FlexGridSizer(rows=7, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes_pages.Add(self.bouton_ajouter_page, 0, 0, 0)
        grid_sizer_commandes_pages.Add(self.bouton_supprimer_page, 0, 0, 0)
        grid_sizer_commandes_pages.Add( (10, 10), 0, 0, 0)
        grid_sizer_commandes_pages.Add(self.bouton_visualiser_page, 0, 0, 0)
        grid_sizer_commandes_pages.Add( (10, 10), 0, 0, 0)
        grid_sizer_commandes_pages.Add(self.bouton_zoom_plus, 0, 0, 0)
        grid_sizer_commandes_pages.Add(self.bouton_zoom_moins, 0, 0, 0)
        grid_sizer_pages.Add(grid_sizer_commandes_pages, 1, wx.EXPAND, 0)
        sizer_pages.Add(grid_sizer_pages, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_horiz.Add(sizer_pages, 1, wx.ALL|wx.EXPAND, 0)
        grid_sizer_horiz.AddGrowableRow(0)
        grid_sizer_horiz.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_horiz, 1, wx.ALL|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((15, 15), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.Centre()

    def RemplissageAutresTypes(self):
        # Cr�e un dictionnaire des dates de validit� par d�faut des types de pi�ces
        self.DictTypesPieces = {}
        self.ListeAutresPieces = []
        self.ListeAutresPourCombo = []
        
        DB = GestionDB.DB()
        req = "SELECT * FROM types_pieces ORDER BY nom_piece"
        DB.ExecuterReq(req)
        listeTypes = DB.ResultatReq()
        DB.Close()

        for typePiece in listeTypes:
            key = typePiece[0]
            nom = typePiece[1]
            duree = typePiece[2]

            # Cr�ation d'un dict pour que le listCtrl acc�de aux dur�es de validit�
            self.DictTypesPieces[key] = duree

            # Cr�ation d'une liste pour remplir le comboBox des autres types
            if key not in list(self.list_ctrl_pieces.DictPieces.keys()):
                self.ListeAutresPieces.append((key, nom, duree))
                self.ListeAutresPourCombo.append(nom)

    def OnComboBoxAutres(self, event):

        index = event.GetSelection()
        key = int(self.ListeAutresPieces[index][0])

        self.selection2 = (index, key)

        # Si une date de d�but a d�j� �t� saisie, on proc�de � la recherche de la date de fin par d�faut
        if self.CalcValiditeDefaut(self.selection2) == False :
            # Mets le focus sur la date de d�but
            self.text_date_debut.SetFocus()
        

    def OnRadioPieces(self, event):
        if self.radio_pieces_1.GetValue() == True:
            self.combo_box_autres.Enable(False)
            self.list_ctrl_pieces.Enable(True)
        else:
            self.combo_box_autres.Enable(True)
            self.list_ctrl_pieces.Enable(False)

    def OnRadioDateFin(self, event):
        if self.radio_date_fin_1.GetValue() == True:
            self.text_date_fin.Enable(True)
        else:
            self.text_date_fin.Enable(False)

    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(29)

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        """ Bouton Ok """
        # V�rification des donn�es saisies

        # Validation du listCtrl
        if self.radio_pieces_1.GetValue() == True:
            if self.selection1 == ("NoSelect",):
                message = _(u"Vous devez s�lectionner un type de pi�ce dans la liste propos�e.")
                wx.MessageBox(message, "Erreur de saisie")
                return

        # Validation du comboBox
        if self.radio_pieces_2.GetValue() == True:
            if self.selection2 == ("NoSelect",):
                message = _(u"Vous devez s�lectionner un autre type de pi�ce dans la liste propos�e.")
                wx.MessageBox(message, "Erreur de saisie")
                self.combo_box_autres.SetFocus()
                return

        # Validation de la date de d�but
        textDate = self.text_date_debut.GetValue()
        if textDate == "  /  /    ":
            message = _(u"Vous devez saisir une date de d�but de validit�.")
            wx.MessageBox(message, "Erreur de saisie")
            self.text_date_debut.SetFocus()
            return
        validation = ValideDate(texte=textDate, date_min="01/01/1910", date_max="01/01/2099")
        if validation == False:
            self.text_date_debut.SetFocus()
            return

        # Validation de la date de fin
        if self.radio_date_fin_1.GetValue() == True:
            textDate = self.text_date_fin.GetValue()
            if textDate == "  /  /    ":
                message = _(u"Vous devez saisir une date de fin de validit�.")
                wx.MessageBox(message, "Erreur de saisie")
                self.text_date_fin.SetFocus()
                return
            # V�rifie la coh�rence de la date de fin
            validation = ValideDate(texte=textDate, date_min="01/01/1910", date_max="01/01/2099")
            if validation == False:
                self.text_date_fin.SetFocus()
                return
            # V�rifie que la date de fin est sup�rieure � la date de d�but
            dateDebut = self.text_date_debut.GetValue()
            dateFin = self.text_date_fin.GetValue()
            dateDebut = datetime.date(int(dateDebut[6:10]), int(dateDebut[3:5]), int(dateDebut[:2]))
            dateFin = datetime.date(int(dateFin[6:10]), int(dateFin[3:5]), int(dateFin[:2]))
            reste = str(dateFin - dateDebut)
            if reste != "0:00:00":
                jours = int(reste[:reste.index("day")])
                if jours < 0:
                    message = _(u"Vous devez saisir une date de fin de validit� sup�rieure � la date de d�but !")
                    wx.MessageBox(message, "Erreur de saisie")
                    self.text_date_fin.SetFocus()
                    return

        # Proc�dure d'enregistrement des donn�es
        self.Sauvegarde()

        # Sauvegarde des pages scann�es
        self.ctrl_pages.Sauvegarde(self.IDpiece) 

        # M�J des listCtrl de la fiche individuelle
        self.parent.list_ctrl_dossier.Remplissage()
        self.parent.list_ctrl_pieces.Remplissage()
        self.parent.MAJ_barre_problemes()

        # Fermeture de la fen�tre
        self.EndModal(wx.ID_OK)
        

    def OnDateDebut(self, event):
        texte = self.text_date_debut.GetValue()
        for caract in texte:
            if caract == " ":
                return
        if self.radio_pieces_1.GetValue() == True:
            self.CalcValiditeDefaut(self.selection1)
        else:
            self.CalcValiditeDefaut(self.selection2)
        event.Skip()

    def CalcValiditeDefaut(self, selection):

        dateDebut = self.text_date_debut.GetValue()

        if dateDebut == "  /  /    ":
            return False

        if selection[0] == "NoSelect":
            return False

        if self.radio_pieces_2.GetValue() == True:
            if self.combo_box_autres.GetSelection() == -1:
                return
        
        # Validation de la date de d�but
        validation = ValideDate(texte=dateDebut, date_min="01/01/1910", date_max="01/01/2099")
        if validation == False:
            self.text_date_debut.SetFocus()
            return

        # Recherche de la dur�e de validit� par d�faut de la pi�ce
        key = selection[1]
        duree = self.DictTypesPieces[key]
        posM = duree.find("m")
        posA = duree.find("a")
        jours = int(duree[1:posM-1])
        mois = int(duree[posM+1:posA-1])
        annees = int(duree[posA+1:])
        
        if jours==0 and mois==0 and annees==0:
            # Si illimit�
            dateFin = "2999-01-01"
            self.radio_date_fin_2.SetValue(1)
            self.text_date_fin.Enable(False)
            self.bouton_ok.SetFocus()
            
        else:
            # Si validit� limit�e
            dateJour = int(dateDebut[:2])
            dateMois = int(dateDebut[3:5])
            dateAnnee = int(dateDebut[6:10])
            dateDebut = datetime.date(dateAnnee, dateMois, dateJour)

            # Calcul des jours
            if jours != 0:
                dateFin = dateDebut + (datetime.timedelta(days = jours))
                dateJour = dateFin.day
                dateMois = dateFin.month
                dateAnnee = dateFin.year

            # Calcul des mois
            if mois != 0:
                dateMois = dateMois + mois
                if dateMois > 12:
                    division = divmod(dateMois, 12)
                    dateAnnee = dateAnnee + division[0]
                    dateMois = division[1]
                dateFin = datetime.date(dateAnnee, dateMois, dateJour)
                dateJour = dateFin.day
                dateMois = dateFin.month
                dateAnnee = dateFin.year

            # Calcul des ann�es
            if annees != 0:
                dateAnnee = dateAnnee + annees
                dateFin = datetime.date(dateAnnee, dateMois, dateJour)

            # Insertion de la date dans la case Date_Fin
            dateFinale = str(dateFin)
            dateFinale = dateFinale[8:10] + "/" + dateFinale[5:7] + "/" + dateFinale[:4]
            self.text_date_fin.SetValue(dateFinale)

            # Mets le focus sur la date de fin
            self.radio_date_fin_1.SetValue(1)
            self.text_date_fin.Enable(True)
            self.bouton_ok.SetFocus()


        # ------------------------- SAUVEGARDE ET IMPORTATION ----------------------------------

    def Sauvegarde(self):
        """ Sauvegarde des donn�es dans la base de donn�es """
        
        varIDpersonne = self.IDpersonne
        varIDpiece = self.IDpiece

        # IDTypePiece
        if self.radio_pieces_1.GetValue() == True:
            varIDtypePiece = self.selection1[1]
        else:
            varIDtypePiece = self.selection2[1]

        # Date_debut
        textDate = self.text_date_debut.GetValue()
        varDateDebut = datetime.date(int(textDate[6:10]), int(textDate[3:5]), int(textDate[:2]))

        # Date_Fin
        if self.radio_date_fin_2.GetValue() == True:
            varDateFin = datetime.date(2999, 1, 1)
        else:
            textDate = self.text_date_fin.GetValue()
            varDateFin = datetime.date(int(textDate[6:10]), int(textDate[3:5]), int(textDate[:2]))

        # Pr�paration des donn�es
        listeDonnees = [    ("IDpersonne",      varIDpersonne),
                            ("IDtype_piece",    varIDtypePiece),
                            ("date_debut",      varDateDebut),
                            ("date_fin",        varDateFin),
                        ]
        
        # Initialisation de la connexion avec la Base de donn�es
        DB = GestionDB.DB()

        if self.IDpiece == 0:
            # Enregistrement d'une nouvelle coordonn�e
            self.IDpiece = DB.ReqInsert("pieces", listeDonnees)
        else:
            # Modification de la coordonn�e
            DB.ReqMAJ("pieces", listeDonnees, "IDpiece", self.IDpiece)
            

    def Importation(self,):
        """ Importation des donnees de la base """

        # Initialisation de la connexion avec la Base de donn�es
        DB = GestionDB.DB()
        req = "SELECT * FROM pieces WHERE IDpiece = %s" % self.IDpiece
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()[0]
        DB.Close()
        
        # Placement des donn�es dans les contr�les
        varIDtypePiece = donnees[2]
        varDateDebut = donnees[3]
        varDateFin = donnees[4]

        # Placement du type de pi�ce
        if varIDtypePiece in list(self.list_ctrl_pieces.DictPieces.keys()):
            # Ce type de pi�ce est dans le ListCtrl
            self.radio_pieces_1.SetValue(1)
            self.radio_pieces_2.SetValue(0)
            self.list_ctrl_pieces.Enable(True)
            self.combo_box_autres.Enable(False)
            if 'phoenix' in wx.PlatformInfo:
                index = self.list_ctrl_pieces.FindItem(-1, varIDtypePiece)
            else:
                index = self.list_ctrl_pieces.FindItemData(-1, varIDtypePiece)
            self.selection1 = (index, varIDtypePiece)
            item = self.list_ctrl_pieces.GetItem(index)
            font = item.GetFont()
            font.SetWeight(wx.FONTWEIGHT_BOLD)
            item.SetFont(font)
            self.list_ctrl_pieces.SetItem(item)
            
        else:
            # Ce type de pi�ce est dans le ComboBox
            self.radio_pieces_1.SetValue(0)
            self.radio_pieces_2.SetValue(1)
            self.combo_box_autres.Enable(True)
            self.list_ctrl_pieces.Enable(False)
            index = 0
            for piece in self.ListeAutresPieces:
                if piece[0] == varIDtypePiece:
                    self.combo_box_autres.SetValue(piece[1])
                    break
                index += 1
            self.selection2 = (index, varIDtypePiece)

        # Placement de la date de d�but
        textDate = varDateDebut
        self.text_date_debut.SetValue(str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4]))

        # Placement de la date de fin
        if varDateFin == "2999-01-01":
            self.radio_date_fin_2.SetValue(True)
            self.text_date_fin.Enable(False)
        else:
            self.radio_date_fin_1.SetValue(True)
            self.text_date_fin.Enable(True)
            textDate = varDateFin
            self.text_date_fin.SetValue(str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4]))
                
    def AjouterPage(self, event):
        self.ctrl_pages.AjouterPage()

    def SupprimerPage(self, event):
        self.ctrl_pages.SupprimerPage(None)
    
    def VisualiserPage(self, event):
        self.ctrl_pages.VisualiserPage(None)
    
    def ZoomPlus(self, event):
        self.ctrl_pages.ZoomPlus()

    def ZoomMoins(self, event):
        self.ctrl_pages.ZoomMoins()


# ----------- LISTCTRL PIECES ---------------------------------------------------------------------------------------------------


class ListCtrl_Pieces(wx.ListCtrl):
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, id, size=(180, -1), style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_HRULES|wx.LC_SINGLE_SEL|wx.SUNKEN_BORDER)

        self.parent = parent
        self.IDpersonne = self.GetGrandParent().IDpersonne
        self.IDpiece = self.GetGrandParent().IDpiece

        # ImageList
        self.il = wx.ImageList(16,16)
        self.imgOk = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))
        self.imgAttention = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Attention.png"), wx.BITMAP_TYPE_PNG))
        self.imgPasOk = self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        # Colonnes
        self.InsertColumn(0, "")
        self.SetColumnWidth(0, 175)

        # Cr�ation des items
        self.Remplissage()

        # Binds
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnItemSelected)

    def Remplissage(self):
        """ Remplissage du ListCtrl """
        # Importation des donn�es
        self.Importation()

        # S'il existe des items, on les efface d'abord
        if self.GetItemCount() != 0:
            self.DeleteAllItems()
            
        # Cr�ation des items
        index = 0
        for key, valeurs in self.DictPieces.items():
            etat = valeurs[0]
            nomPiece = valeurs[1]
            # Cr�ation de l'item
            if 'phoenix' in wx.PlatformInfo:
                self.InsertItem(index, nomPiece)
            else:
                self.InsertStringItem(index, nomPiece)
            # Int�gration de l'image
            if etat == "Ok":
                self.SetItemImage(index, self.imgOk)
            if etat == "Attention":
                self.SetItemImage(index, self.imgAttention)
            if etat == "PasOk":
                self.SetItemImage(index, self.imgPasOk)
            # Int�gration du data ID
            self.SetItemData(index, key)
            index += 1

        # Tri dans l'ordre alphab�tique
        self.SortItems(self.ColumnSorter)

    def ColumnSorter(self, key1, key2):
        item1 = self.DictPieces[key1][1]
        item2 = self.DictPieces[key2][1]
        if item1 < item2:    
               return -1
        else:                   
               return 1

    def Importation(self):
        """ Importe les donn�es """

        date_jour = datetime.date.today()
        
        
        # Initialisation de la base de donn�es
        DB = GestionDB.DB()
        
        # Recherche des pi�ces SPECIFIQUES que la personne doit fournir...
        req = """
        SELECT types_pieces.IDtype_piece, types_pieces.nom_piece
        FROM diplomes INNER JOIN diplomes_pieces ON diplomes.IDtype_diplome = diplomes_pieces.IDtype_diplome INNER JOIN types_pieces ON diplomes_pieces.IDtype_piece = types_pieces.IDtype_piece
        WHERE diplomes.IDpersonne=%d;
        """ % self.IDpersonne
        DB.ExecuterReq(req)
        listePiecesAFournir = DB.ResultatReq()
        
        # pour mysql :
        if type( listePiecesAFournir) != list :
            listePiecesAFournir = list(listePiecesAFournir)
            
        # Recherche des pi�ces BASIQUES que la personne doit fournir...
        req = """
        SELECT diplomes_pieces.IDtype_piece, types_pieces.nom_piece
        FROM diplomes_pieces INNER JOIN types_pieces ON diplomes_pieces.IDtype_piece = types_pieces.IDtype_piece
        WHERE diplomes_pieces.IDtype_diplome=0;
        """ 
        DB.ExecuterReq(req)
        listePiecesBasiquesAFournir = DB.ResultatReq()
        
        listePiecesAFournir.extend(listePiecesBasiquesAFournir)
        
        # Recherche des pi�ces que la personne poss�de
        req = """
        SELECT types_pieces.IDtype_piece, pieces.date_debut, pieces.date_fin
        FROM types_pieces LEFT JOIN pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
        WHERE (pieces.IDpersonne=%d AND pieces.date_debut<='%s' AND pieces.date_fin>='%s')
        ORDER BY pieces.date_fin;
        """ % (self.IDpersonne, date_jour, date_jour)
        DB.ExecuterReq(req)
        listePieces = DB.ResultatReq()
        dictTmpPieces = {}
        for IDtype_piece, date_debut, date_fin in listePieces :
            dictTmpPieces[IDtype_piece] = (date_debut, date_fin)
        
        # Passe en revue toutes les pi�ces � fournir et regarde si la personne poss�de les pi�ces correspondantes
        self.DictPieces = {}
        for IDtype_piece, nom_piece in listePiecesAFournir :
            if (IDtype_piece in dictTmpPieces) == True :
                date_debut = dictTmpPieces[IDtype_piece][0]
                date_fin = dictTmpPieces[IDtype_piece][1]
                # Recherche la validit�
                date_fin = datetime.date(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]))
                reste = str(date_fin - date_jour)
                if reste != "0:00:00":
                    jours = int(reste[:reste.index("day")])
                    if jours < 15  and jours > 0:
                        etat = "Attention"
                    elif jours <= 0:
                        etat = "PasOk"
                    else:
                        etat = "Ok"
                else:
                    etat = "Attention"
            else:
                etat = "PasOk"
            self.DictPieces[IDtype_piece] = (etat, nom_piece)

##        # Initialisation de la base de donn�es
##        DB = GestionDB.DB()
##        self.DictPieces = {}
##        
##        # Recherche des pi�ces sp�cifiques
##        req = """
##        SELECT diplomes_pieces.IDtype_piece, types_pieces.nom_piece, Count(pieces.IDpiece) AS CompteDeIDpiece, Min(pieces.date_debut) AS MinDedate_debut, Max(pieces.date_fin) AS MaxDedate_fin, diplomes.IDpersonne 
##        FROM diplomes_pieces
##        INNER JOIN types_diplomes ON diplomes_pieces.IDtype_diplome = types_diplomes.IDtype_diplome
##        INNER JOIN types_pieces ON diplomes_pieces.IDtype_piece = types_pieces.IDtype_piece
##        INNER JOIN diplomes ON types_diplomes.IDtype_diplome = diplomes.IDtype_diplome
##        LEFT JOIN pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
##        GROUP BY diplomes.IDpersonne, diplomes_pieces.IDtype_piece, types_pieces.nom_piece
##        HAVING (((diplomes.IDpersonne)=%d) AND ((Min(pieces.date_debut))<='%s') AND ((Max(pieces.date_fin))>='%s')) OR (((diplomes.IDpersonne)=%d));
##        """ % (self.IDpersonne, date_jour, date_jour, self.IDpersonne)
##        DB.ExecuterReq(req)
##        listePiecesSpecif = DB.ResultatReq()
##        
##        print listePiecesSpecif
##
##        # Cr�ation du dictionnaire de donn�es pour les pi�ces sp�cifiques
##        for piece in listePiecesSpecif:
##            IDtype_piece = piece[0]
##            nom_piece = piece[1]
##            nbre_pieces = piece[2]
##            date_debut = piece[3]
##            date_fin = piece[4]
##            # Recherche la validit�
##            if nbre_pieces >0 :
##                date_fin = datetime.date(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]))
##                reste = str(date_fin - date_jour)
##                if reste != "0:00:00":
##                    jours = int(reste[:reste.index("day")])
##                    if jours < 15  and jours > 0:
##                        etat = "Attention"
##                    elif jours <= 0:
##                        etat = "PasOk"
##                    else:
##                        etat = "Ok"
##                else:
##                    etat = "Attention"
##            else:
##                etat = "PasOk"
##            self.DictPieces[IDtype_piece] = (etat, nom_piece)
##        
##        # Recherche des pi�ces basiques (communes � tous les employ�s)
##        req = """
##        SELECT types_pieces.IDtype_piece, types_pieces.nom_piece, Count(pieces.IDpiece) AS CompteDeIDpiece, Min(pieces.date_debut) AS MinDedate_debut, Max(pieces.date_fin) AS MaxDedate_fin, pieces.IDpersonne
##        FROM diplomes_pieces
##        INNER JOIN types_pieces ON diplomes_pieces.IDtype_piece = types_pieces.IDtype_piece
##        LEFT JOIN pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece GROUP BY types_pieces.IDtype_piece, types_pieces.nom_piece, diplomes_pieces.IDtype_diplome, pieces.IDpersonne
##        HAVING (((diplomes_pieces.IDtype_diplome)=0) AND ((Min(pieces.date_debut))<='%s' Or (Min(pieces.date_debut)) Is Null) AND ((Max(pieces.date_fin))>='%s' Or (Max(pieces.date_fin)) Is Null) AND ((pieces.IDpersonne)=%d Or (pieces.IDpersonne) Is Null)) OR (((diplomes_pieces.IDtype_diplome)=0));
##        """ % (date_jour, date_jour, self.IDpersonne)
##        DB.ExecuterReq(req)
##        listePiecesBase = DB.ResultatReq()
##        
##        print listePiecesBase
##        
##        # Cr�ation du dictionnaire de donn�es pour les pi�ces basiques (communes � tous les employ�s)
##        for piece in listePiecesBase:
##            IDtype_piece = piece[0]
##            nom_piece = piece[1]
##            nbre_pieces = piece[2]
##            date_debut = piece[3]
##            date_fin = piece[4]
##            # Recherche la validit�
##            if nbre_pieces >0 :
##                date_fin = datetime.date(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]))
##                reste = str(date_fin - date_jour)
##                if reste != "0:00:00":
##                    jours = int(reste[:reste.index("day")])
##                    if jours < 15 and jours > 0:
##                        etat = "Attention"
##                    elif jours <= 0:
##                        etat = "PasOk"
##                    else:
##                        etat = "Ok"
##                else:
##                    etat = "Attention"
##            else:
##                etat = "PasOk"
##            self.DictPieces[IDtype_piece] = (etat, nom_piece)
        
        # Fermeture de la base de donn�es
        DB.Close()

    def OnSize(self, event):
        # La largeur de la colonne s'adapte � la largeur du listCtrl
        size = self.GetSize()
        self.SetColumnWidth(0, size.x-30)
        event.Skip()

    def OnItemSelected(self, event):
        """ Item cliqu� """
        x = event.GetX()
        y = event.GetY()
        index, flags = self.HitTest((x, y))
        if index == -1 :
            return
        key = self.GetItemData(index)

        # Eleve le gras de la s�lection pr�c�dente
        if self.GetGrandParent().selection1[0] != "NoSelect":
            index1 = self.GetGrandParent().selection1[0]
            item = self.GetItem(index1)
            font = self.GetFont()
            font.SetWeight(wx.FONTWEIGHT_NORMAL)
            item.SetFont(font)
            self.SetItem(item)

        self.GetGrandParent().selection1 = (index, key)

        # Change la font de la s�lection
        item = self.GetItem(index)
        font = self.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        item.SetFont(font)
        self.SetItem(item)

        # Si une date de d�but a d�j� �t� saisie, on proc�de � la recherche de la date de fin par d�faut
        if self.GetGrandParent().CalcValiditeDefaut(self.GetGrandParent().selection1) == False :
            # Mets le focus sur la date de d�but
            self.GetGrandParent().text_date_debut.SetFocus()
            
    def SetIDtypePieceDefaut(self, IDtypePiece):
        """ Cette fonction sert � charger le type de pi�ce double-cliqu� dans les pi�ces manquantes
        du panel Qualifications de la fiche individuelle """
        # Recherche la pi�ce dans la liste propos�e
        index = self.FindItemData(-1, IDtypePiece)

        self.GetGrandParent().selection1 = (index, IDtypePiece)

        # Change la font de la s�lection
        item = self.GetItem(index)
        font = self.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        item.SetFont(font)
        self.SetItem(item)
        
        # Focus sur la date de d�but
        self.GetGrandParent().text_date_debut.SetFocus()


def ValideDate(texte, date_min="01/01/1900", date_max="01/01/2090"):
    """ Verificateur de validite de date """
    listeErreurs = []
    # On v�rifie si les cases ne sont pas vides
    if texte[0] == " " or texte[1] == " ":
        listeErreurs.append(_(u"le jour"))
    if texte[3] == " " or texte[4] == " ":
        listeErreurs.append(_(u"le mois"))
    if texte[6] == " " or texte[7] == " " or texte[8] == " " or texte[9] == " ":
        listeErreurs.append(_(u"l'ann�e"))
    
    if texte != "  /  /    ":

        # On v�rifie que les chiffres existent
        if _(u"le jour") not in listeErreurs:
            jour = int(texte[:2])
            if jour == 0 or jour > 31:
                listeErreurs.append(_(u"le jour"))

        if _(u"le mois") not in listeErreurs:
            mois = int(texte[3:5])
            if mois == 0 or mois > 12:
                listeErreurs.append(_(u"le mois"))
                
        if _(u"l'ann�e") not in listeErreurs:
            annee = int(texte[6:10])
            if annee < 1900 or annee > 2999:
                listeErreurs.append(_(u"l'ann�e"))
        
        # Test de la date avec le datetime
        try : testDate = datetime.date(year=int(texte[6:10]), month=int(texte[3:5]), day=int(texte[:2]))
        except : 
            wx.MessageBox(_(u"La date de d�but que vous avez saisie n'est pas valide"), "Erreur de date")
            return False
              
        # Affichage du message d'erreur
        
        if len(listeErreurs) != 0:
            # Message en cas de date incompl�te
            if len(listeErreurs) == 1:
                message = _(u"Une incoh�rence a �t� d�tect�e dans ") + listeErreurs[0]
            if len(listeErreurs) == 2:
                message = _(u"Des incoh�rences ont �t� d�tect�es dans ") + listeErreurs[0] + " et " + listeErreurs[1]
            if len(listeErreurs) == 3:
                message = _(u"Des incoh�rences ont �t� d�tect�es dans ") + listeErreurs[0]  + ", " + listeErreurs[1]  + " et " + listeErreurs[2]
            message = message + _(u" de la date que vous venez de saisir. Veuillez la v�rifier.")

            wx.MessageBox(message, "Erreur de date")
            return False
        else:
            # On v�rifie que les dates sont comprises dans l'intervalle donn� en param�tre
            date_min = int(str(date_min[6:10]) + str(date_min[3:5]) + str(date_min[:2]))
            date_max = int(str(date_max[6:10]) + str(date_max[3:5]) + str(date_max[:2]))
            date_sel = int(str(texte[6:10]) + str(texte[3:5]) + str(texte[:2]))

            if date_sel < date_min:
                message = _(u"La date que vous venez de saisir semble trop ancienne. Veuillez la v�rifier.")
                wx.MessageBox(message, "Erreur de date")
                return False
            if date_sel > date_max:
                message = _(u"La date que vous venez de saisir semble trop �lev�e. Veuillez la v�rifier.")
                wx.MessageBox(message, "Erreur de date")
                return False
            
    else:
        return True

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, -1, "", IDpersonne=10)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
