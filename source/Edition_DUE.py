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
import GestionDB
import  wx.grid as gridlib
import FonctionsPerso
from reportlab.pdfgen import canvas
import Attente
import threading
import thread
import os
import sys

styles = {
    1 : (_(u"Texte normal"), 11.35, 20, 0),
    2 : (_(u"Grande case"), 11.35, 20, 2.25),
    3 : (_(u"Petite case à cocher"), 6, 6, 0),
    4 : (_(u"Case à cocher ombrée"), 10, 20, 0),
    5 : (_(u"Texte normal 2"), 12, 20, 2.25),
    }#  (Label du style, largeur, hauteur, espacement
    
    
categories = {
    1 : (_(u"Etablissement employeur")),
    2 : (_(u"Futur salarié")),
    3 : (_(u"Autres éléments")),
    }#  (Label de la catégorie)
    
    
champs = [
    ["NUM_SIRET", _(u"Numéro Siret"), "texte", 1, u"", True,  
     (
        (1, 14, "num", 2, (115.8, 119)),
        )
    ],
    ["CODE_APE", _(u"Code APE"), "texte", 1, u"", True, 
     (
        (1, 4, "alpha", 2, (400.5, 119)),
        )
    ],
    ["CIVILITE_EMPLOYEUR", _(u"Civilité de l'employeur"), "radio", 1, u"", True, 
     (
         (_(u"M."), "x", 3, (116.5, 136)),
         (_(u"Mme"), "x", 3, (135.5, 136)),
         (_(u"Melle"), "x", 3, (162, 136)),
        (_(u"Non renseigné"), " ", 3, (162, 136)),
         )
    ],
    ["DENOMINATION", _(u"Dénomination de l'employeur"), "texte", 1, u"", True, 
     (
         (1, 32, "alpha", 1, (189.4, 144.3)),
         )
    ],
    ["ADRESSE_ETABLISS", _(u"Adresse de l'établissement"), "texte", 1, u"", True, 
     (
         (1, 39, "alpha", 1, (110, 165)),
         )
    ],
    ["CP_ETABLISS", _(u"Code postal de l'établissement"), "texte", 1, u"", True, 
     (
         (1, 5, "alpha", 2, (110, 184)),
         )
    ],
    ["VILLE_ETABLISS", _(u"Ville de l'établissement"), "texte", 1, u"", True, 
     (
         (1, 32, "alpha", 1, (189.4, 184)),
         )
    ],
    ["ADRESSE_CORRESP", _(u"Adresse de correspondance"), "texte", 1, u"", True, 
     (
         (1, 39, "alpha", 1, (110, 205)),
         )
    ],
    ["CP_CORRESP", _(u"Code postal Adresse de correspondance"), "texte", 1, u"", True, 
     (
         (1, 5, "alpha", 2, (110, 224)),
         )
    ],
    ["VILLE_CORRESP", _(u"Ville de l'adresse de correspondance"), "texte", 1, u"", True, 
     (
         (1, 32, "alpha", 1, (189.4, 224)),
         )
    ],
    ["TEL_EMPLOYEUR", _(u"Numéro de téléphone Employeur"), "texte", 1, u"", True, 
     (
         (1, 10, "num", 2, (185.6, 250)),
         )
    ],
    ["FAX_EMPLOYEUR", _(u"Numéro de fax Employeur"), "texte", 1, u"", True, 
     (
         (1, 10, "num", 2, (418.6, 250)),
         )
    ],
    ["CIVILITE_SALARIE", _(u"Civilité du salarié"), "radio", 2, u"", False, 
     (
         (_(u"M."), "x", 3, (116.5, 294)),
         (_(u"Mme"), "x", 3, (135.5, 294)),
         (_(u"Melle"), "x", 3, (162, 294)),
         )
    ],
    ["NOMNAISS_SALARIE", _(u"Nom de naissance"), "texte", 2, u"", False, 
     (
         (1, 13, "alpha", 1, (192, 296)),
         )
    ],
    ["NOMMARITAL_SALARIE", _(u"Nom marital"), "texte", 2, u"", False, 
     (
         (1, 13, "alpha", 1, (405, 296)),
         )
    ],
    ["PRENOM_SALARIE", _(u"Prénoms (dans l'ordre de l'état civil)"), "texte", 2, u"", False, 
     (
         (1, 31, "alpha", 1, (116, 316)),
         )
    ],
    ["SEXE_SALARIE", _(u"Sexe"), "radio", 2, u"", False, 
     (
        (_(u"Masculin"), "M", 2, (511, 319)),
        (_(u"Féminin"), "F", 2, (511, 319)),
         )
    ],
    ["NUMSECU_SALARIE", _(u"Numéro de sécurité sociale"), "texte", 2, u"", False, 
     (
         (1, 1, "num", 2, (115, 341)),
         (2, 3, "num", 2, (132.5, 341)),
         (4, 5, "num", 2, (162, 341)),
         (6, 7, "num", 2, (192, 341)),
         (8, 10, "num", 2, (222, 341)),
         (11, 13, "num", 2, (266, 341)),
         (14, 15, "num", 2, (311, 341)),
         )
    ],
    ["DATENAISS_SALARIE", _(u"Date de naissance (format JJMMAAAA)"), "texte", 2, u"", False, 
     (
         (1, 2, "num", 2, (440, 341)),
         (3, 4, "num", 2, (470, 341)),
         (5, 8, "num", 2, (500.5, 341)),
         )
    ],
    ["NATIONALITE1_SALARIE", _(u"Nationalité"), "radio", 2, u"", False, 
     (
         (_(u"Française"), "x", 4, (116, 366)),
         (_(u"Etrangère"), "x", 4, (176.5, 366)),
         )
    ],
    ["NATIONALITE2_SALARIE", _(u"Si étrangère, quelle nationalité ?"), "texte", 2, u"", False, 
     (
         (1, 24, "alpha", 1, (280.5, 365)),
         )
    ],
    ["DEPARTNAISS_SALARIE", _(u"Numéro de département de naissance"), "texte", 2, u"", False, 
     (
         (1, 3, "alpha", 2, (110, 387)),
         )
    ],
    ["VILLENAISS_SALARIE", _(u"Ville de naissance"), "texte", 2, u"", False, 
     (
         (1, 35, "alpha", 1, (155.7, 387)),
         )
    ],
    ["PAYSNAISS_SALARIE", _(u"Pays de naissance"), "texte", 2, u"", False, 
     (
         (1, 35, "alpha", 1, (393.5, 387)),
         )
    ],
    ["ADRESSE_SALARIE", _(u"Adresse"), "texte", 2, u"", False, 
     (
         (1, 39, "alpha", 1, (110, 411)),
         )
    ],
    ["CP_SALARIE", _(u"Code postal"), "texte", 2, u"", False, 
     (
         (1, 5, "alpha", 2, (110, 433)),
         )
    ],
    ["VILLE_SALARIE", _(u"Ville"), "texte", 2, u"", False, 
     (
         (1, 32, "alpha", 1, (189, 433)),
         )
    ],
    ["DATE_EMBAUCHE", _(u"Date d'embauche (format JJMMAAAA)"), "texte", 2, u"", False, 
     (
         (1, 2, "num", 2, (200, 460.5)),
         (3, 4, "num", 2, (231, 460.5)),
         (5, 8, "num", 2, (261, 460.5)),
         )
    ],
    ["HEURE_EMBAUCHE", _(u"Heure d'embauche (format HHMM)"), "texte", 2, u"", True, 
     (
         (1, 2, "num", 2, (497, 460.5)),
         (3, 4, "num", 2, (528, 460.5)),
         )
    ],
    ["SANTE_CODE", _(u"Service de santé au travail (Code)"), "texte", 3, u"", True, 
     (
         (1, 3, "alpha", 2, (103.5, 514)),
         )
    ],
    ["SANTE_NOM", _(u"Service de santé (Nom et adresse)"), "texte", 3, u"", True, 
     (
         (1, 28, "alpha", 1, (147.5, 514)),
         (29, 56, "alpha", 1, (147.5, 534)),
         )
    ],
    ["SANTE_ENTREPRISE", _(u"Service de santé au travail de l'entreprise ?"), "radio", 3, _(u"Non"), True, 
     (
         (_(u"Oui"), "x", 4, (480.5, 524)),
         (_(u"Non"), " ", 4, (480.5, 524)),
         )
    ],
    ["EFFECTIF_AVANT_1", _(u"Effectif de l'établissement avant embauche"), "texte", 3, u"", True, 
     (
         (1, 4, "num", 2, (194, 557)),
         )
    ],
    ["PREMIER_SALARIE", _(u"S'agit-il du premier salarié avant l'embauche"), "radio", 3, _(u"Non"), True, 
     (
         (_(u"Oui"), "x", 4, (264, 577)),
         (_(u"Non"), "x", 4, (301, 576)),
         )
    ],
    ["EFFECTIF_AVANT_2", _(u"Si oui, effectif avant l'embauche"), "texte", 3, u"", True, 
     (
         (1, 5, "num", 2, (203, 598)),
         )
    ],
    ["ACTIVITE_PRINCIPALE", _(u"Activité exercée dans l'établissement"), "texte", 3, u"", True, 
     (
         (1, 36, "alpha", 5, (42, 614)),
         )
    ],
    ["NATURE_EMPLOI", _(u"Nature de l'emploi et qualification"), "texte", 3, u"", True, 
     (
         (1, 2, "alpha", 2, (159, 632)),
         )
    ],
    ["PERIODE_ESSAI", _(u"Durée de la période d'essai (en jours)"), "texte", 3, u"", False, 
     (
         (1, 2, "num", 2, (403, 633)),
         )
    ],
    ["SITUATION_SALARIE", _(u"Situation du salarié avant l'embauche"), "texte", 3, u"", True, 
     (
         (1, 1, "alpha", 2, (180, 654)),
         )
    ],
    ["DUREE_TRAVAIL_HEBDO", _(u"Durée du travail hebdomadaire (en heures)"), "texte", 3, u"", True, 
     (
         (1, 2, "num", 2, (218, 674)),
         )
    ],
    ["DUREE_TRAVAIL_MENS", _(u"OU durée du travail mensuel (en heures)"), "texte", 3, u"", True, 
     (
         (1, 3, "num", 2, (330, 674)),
         )
    ],
    ["DUREE_TRAVAIL_ANNU", _(u"OU durée du travail annuelle (en heures)"), "texte", 3, u"", True, 
     (
         (1, 4, "num", 2, (469.5, 674)),
         )
    ],
    ["CONTRAT_NOUVELLES", _(u"Contrat Nouvelles Embauches ?"), "radio", 3, _(u"Non"), True, 
     (
         (_(u"Oui"), "x", 4, (35, 695)),
         (_(u"Non"), " ", 4, (35, 695)),
         )
    ],
    ["CONTRAT_TYPE", _(u"Type de contrat"), "radio", 3, u"", False, 
     (
         (_(u"Contrat à durée indéterminée"), "x", 4, (35, 716)),
         (_(u"Contrat à durée déterminée"), "x", 4, (171, 716)),
         )
    ],
    ["DATE_FIN_CONTRAT", _(u"Si CDD, date de fin de contrat"), "texte", 3, u"", False, 
     (
         (1, 2, "num", 2, (442, 717)),
         (3, 4, "num", 2, (470, 717)),
         (5, 8, "num", 2, (500, 717)),
         )
    ],
    ["AGENT_TITULAIRE", _(u"S'agit-il d'un agent titulaire (fonction publique)"), "radio", 3, _(u"Non"), False, 
     (
         (_(u"Oui"), "x", 4, (487, 760.5)),
         (_(u"Non"), "x", 4, (523, 760.5)),
         )
    ],
    ]#  (Code, Label, type de contrôle, IDcategorie, valeur, Sauvegarder ?,
            # (caractDebut, caractFin, type de données, IDstyle, (x, y))
            
            

# --------------------------------------------------------------------------------------------------------------------------------------------------------------

class CreationPDF(threading.Thread) :
    def __init__(self, parent, listeChamps) :
        self.parent = parent
        self.listeChamps = listeChamps
        self.nomDocument = _(u"Temp/Impression_DUE")
        if "win" in sys.platform : self.nomDocument = self.nomDocument.replace("/", "\\")
        threading.Thread.__init__(self)
##        self.Creation()
        
    def Dessin_texte(self, c, valeur, controles) :
        """ Dessine les textes """
        for caractDebut, caractFin, typeDonnee, IDstyle, position in controles :
            # Récupération des données
            labelStyle, tailleX, tailleY, espacement = styles[IDstyle]
            x, y = position
            y = 842-y # Ajustement pour changement de système de coordonnées
            # Découpage du texte
            texte = valeur[caractDebut-1:caractFin]
            # Création du message
            taillePolice = tailleX
            c.setFont("Helvetica", taillePolice)
            xTemp = 0
            numLettre = 0
            for lettre in texte :
                xTemp = numLettre * (tailleX + espacement)
                c.drawCentredString(xTemp + x + (taillePolice/2), y + 2, lettre)
                numLettre += 1
                    
    def Dessin_radio(self, c, valeur, controles) :
        """ Dessine des contrôles radio """
        for label, txtValeur, IDstyle, position in controles :
            if valeur == label :
                # Récupération des données
                labelStyle, tailleX, tailleY, espacement = styles[IDstyle]
                x, y = position
                y = 842-y # Ajustement pour changement de système de coordonnées
                texte = txtValeur
                # Création du message
                taillePolice = tailleX
                c.setFont("Helvetica", taillePolice)
                xTemp = 0
                numLettre = 0
                for lettre in texte :
                    xTemp = numLettre * (tailleX + espacement)
                    c.drawCentredString(xTemp + x + (taillePolice/2), y + 2, lettre)
                    numLettre += 1

    def run(self) :
        """ Processus de création du PDF """  
        # Initialisation
        cheminFichier = self.nomDocument + ".pdf"
        c = canvas.Canvas(cheminFichier, pageCompression = 1)
        # Création du fond
        img = c.drawImage("Images/Special/Form_due_ursaff.jpg", -10, 0, 595, 842, preserveAspectRatio=True)
        # Dessin à partir de la liste de données :
        for code, label, typeControle, IDcategorie, valeur, sauvegarder, controles in self.listeChamps :
            # Si typeControle = "texte"
            if typeControle == "texte" :
                self.Dessin_texte(c, valeur, controles)
            # Si typeControle = "radio"
            if typeControle == "radio" :
                self.Dessin_radio(c, valeur, controles)
        # Sauvegarde sur le disque dur
        c.save()
        
        try: 
            if "linux" not in sys.platform :
                self.parent.frmAttente.stop()
            # Ouverture du fichier
            FonctionsPerso.LanceFichierExterne(cheminFichier)
        except :
            pass
        
        
class Grid(gridlib.Grid): 
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent, -1, size=(200, 200), style=wx.WANTS_CHARS)
        self.moveTo = None
        
        self.listeValeurs = champs
        self.dictCategories = categories
        self.dictValeurs = {}

        self.Bind(wx.EVT_IDLE, self.OnIdle)
        
        # Création de la grille
        nbreLignes = len(self.listeValeurs) + len(self.dictCategories)
        self.CreateGrid(nbreLignes, 2)
        self.SetColSize(0, 240)
        self.SetColSize(1, 250)
        self.SetColLabelValue(0, "")
        self.SetColLabelValue(1, "")
        self.SetRowLabelSize(1)
        self.SetColLabelSize(1)
        
        # Remplissage avec les données
        IDcategorieEnCours = 0
        key = 0
        for valeurs in self.listeValeurs :
            
            # Récupération des valeurs
            code = valeurs[0]
            label = valeurs[1] + " :"
            type = valeurs[2]
            IDcategorie = valeurs[3]
            valeur = valeurs[4]
            sauvegarde = valeurs[5]
            controles = valeurs[6]
            
            # Indique que la valeur sera sauvegardée
            if sauvegarde == True : label = label[:-2] + " * :"
            
            if IDcategorieEnCours != IDcategorie :
                # Création d'une ligne CATEGORIE
                IDcategorieEnCours = IDcategorie
                self.SetRowLabelValue(key, "")
                self.SetCellValue(key, 0, self.dictCategories[IDcategorie])
                self.SetCellFont(key, 0, wx.Font(8, wx.DEFAULT , wx.NORMAL, wx.BOLD))
                self.SetCellBackgroundColour(key, 0, "#C5DDFA")
                self.SetReadOnly(key, 0, True)
                self.SetCellAlignment(key, 0, wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
                self.SetCellValue(key, 1, "")
                self.SetCellBackgroundColour(key, 1, "#C5DDFA")
                self.SetReadOnly(key, 1, True)
                # Mémorisation dans le dictionnaire des données
                self.dictValeurs[key] = valeurs
                key += 1
                
            # Création d'une ligne de données
            
            # Entete de ligne
            self.SetRowLabelValue(key, "")
            
            # Création de la cellule LABEL
            self.SetCellValue(key, 0, label)
            self.SetCellBackgroundColour(key, 0, "#EEF4FB")
            self.SetReadOnly(key, 0, True)
            self.SetCellAlignment(key, 0, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
            
            # Création de la cellule VALEUR
            if type == "texte" :
                nbreCaract = controles[-1][1]
                editor = gridlib.GridCellTextEditor()
                editor.SetParameters(str(nbreCaract))
                self.SetCellEditor(key, 1, editor)
                self.SetCellValue(key, 1, valeur[:nbreCaract])
            
            if type == "radio" :
                listeDonnees = []
                for controle in controles :
                    listeDonnees.append(controle[0])
                editor = gridlib.GridCellChoiceEditor( listeDonnees , False)
                self.SetCellEditor(key, 1, editor)
                self.SetCellValue(key, 1, valeur)
            
            # Mémorisation dans le dictionnaire des données
            self.dictValeurs[key] = valeurs
            key += 1
            
        # test all the events
        self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        
        self.moveTo = (1, 1)

    def OnCellChange(self, evt):
       
        # Modification de la valeur dans le dict de données
        numRow = evt.GetRow()
        valeur = self.GetCellValue(numRow, 1)
        self.dictValeurs[numRow][4] = valeur
        code = self.dictValeurs[numRow][0]
        save = self.dictValeurs[numRow][5]
        
        if save == False : return
        
##        # Vérification de la valeur
##        if valeur == "" :
##            self.moveTo = evt.GetRow(), evt.GetCol()
##            dlg = wx.MessageDialog(self, _(u"Vous n'avez saisi aucune donnée. \n\nVoulez-vous laisser ce champ vide ?"),  _(u"Vérification"), wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
##            if dlg.ShowModal() == wx.ID_NO :
##                pass
        
        DB = GestionDB.DB()
        
        # Vérifie si le code existe déjà dans la base
        req = """SELECT IDvaleur, code, valeur FROM due_valeurs WHERE code='%s';""" % code
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        
        if len(listeDonnees) == 0 :
            # Enregistrement de la valeur
            listeDonnees = [("code",  code), ("valeur",  valeur)]
            newID = DB.ReqInsert("due_valeurs", listeDonnees)
            DB.Close()
        else:
            # MAJ de la valeur
            IDvaleur = listeDonnees[0][0]
            listeDonnees = [("code",  code), ("valeur",  valeur)]
            DB.ReqMAJ("due_valeurs", listeDonnees, "IDvaleur", IDvaleur)
            DB.Close()


    def OnIdle(self, evt):
        if self.moveTo != None:
            self.SetGridCursor(self.moveTo[0], self.moveTo[1])
            self.moveTo = None

        evt.Skip()



# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        
class MyFrame(wx.Frame):
    def __init__(self, parent, title="", IDcontrat=0):
        wx.Frame.__init__(self, parent, -1, title=title, name="frm_edition_due", style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.IDcontrat = IDcontrat
        
        self.panel_base = wx.Panel(self, -1)
        self.sizer_grid_staticbox = wx.StaticBox(self.panel_base, -1, "Champs")
        self.label_intro = wx.StaticText(self.panel_base, -1, _(u"Vérifiez, modifiez ou ajoutez les données puis cliquez sur 'Ok'."))
        self.label_info = wx.StaticText(self.panel_base, -1, _(u"Remarque : Les champs marqués d'un astérique * sont mémorisés."))
        font = wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.label_info.SetFont(font)
               
        # Préparation de la grid
        self.Import_Donnees()
        self.gridChamps = Grid(self.panel_base)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
                
    def __set_properties(self):
        self.SetTitle(_(u"Edition d'une déclaration préalable à l'embauche"))
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString("Cliquez ici pour visualiser le document au format PDF")
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString("Cliquez ici pour annuler et fermer")
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        sizer_grid = wx.StaticBoxSizer(self.sizer_grid_staticbox, wx.VERTICAL)
        sizer_grid.Add(self.gridChamps, 1, wx.ALL|wx.EXPAND, 5)
        sizer_grid.Add(self.label_info, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)
        grid_sizer_base.Add(sizer_grid, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
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
        self.Centre()


    def Onbouton_aide(self, event):
        FonctionsPerso.Aide(2)

    def Onbouton_annuler(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
            
    def Onbouton_ok(self, event):
        """ Affichage du PDF """
        if "linux" not in sys.platform :
            self.frmAttente = Attente.MyFrame(None, label=_(u"Création du document PDF en cours..."))
            self.frmAttente.Show()
            self.frmAttente.MakeModal(True)
        
        pdf = CreationPDF(self, champs)
        pdf.start()

            
        
    def Import_Donnees(self):
        """ Importe les champs de la base de données """
        
        IDcontrat = self.IDcontrat
        DB = GestionDB.DB()   
        
        # Import des données enregistrées dans la base
        req = """
            SELECT IDvaleur, code, valeur
            FROM due_valeurs;
        """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        
        # Intégration des données à la liste des champs
        index = 0
        global champs
        for IDvaleur, code, valeur in listeDonnees :
            index = 0
            for champ in champs :
                if champ[0] == code :
                    champs[index][4] = valeur
                index += 1
        
        # Base Contrats
        req = """
            SELECT IDpersonne, IDclassification, IDtype, valeur_point, date_debut, date_fin, essai
            FROM contrats WHERE IDcontrat=%d;
        """ % IDcontrat
        DB.ExecuterReq(req)
        listeContrat = DB.ResultatReq()[0]
        
        IDpersonne = listeContrat[0]
        IDclassification = listeContrat[1]
        IDtype = listeContrat[2]
        IDvaleur_point = listeContrat[3]
        date_debut = listeContrat[4]
        if date_debut != "" : date_debut = FonctionsPerso.DateEngFr(date_debut)
        date_fin = listeContrat[5]
        if date_fin != "" : date_fin = FonctionsPerso.DateEngFr(date_fin)
        date_debut = date_debut.replace("/", "")
        date_fin = date_fin.replace("/", "")
        essai = str(listeContrat[6])
        
        # Base contrats_class
        req = """
            SELECT nom
            FROM contrats_class WHERE IDclassification=%d;
        """ % IDclassification
        DB.ExecuterReq(req)
        listeClassification = DB.ResultatReq()[0]
        
        classification = listeClassification[0]
                
        # Base contrats_types
        req = """
            SELECT nom, nom_abrege, duree_indeterminee
            FROM contrats_types WHERE IDtype=%d;
        """ % IDtype
        DB.ExecuterReq(req)
        listeType = DB.ResultatReq()[0]
        
        type = listeType[0]
        type_CDI = listeType[2]
        
        if type_CDI == "non" :
            type_contrat = _(u"Contrat à durée déterminée")
        else:
            type_contrat = "" #_(u"Contrat à durée indéterminée")
                
        # Base valeurs_point
        req = """
            SELECT valeur, date_debut
            FROM valeurs_point WHERE IDvaleur_point=%d;
        """ % IDvaleur_point
        DB.ExecuterReq(req)
        listeValeursPoint = DB.ResultatReq()[0]
        
        valeur_point = listeValeursPoint[0]
        
        # Base personnes
        req = """
            SELECT civilite, nom, nom_jfille, prenom, date_naiss, cp_naiss, ville_naiss, nationalite, num_secu, adresse_resid, cp_resid, ville_resid, IDsituation, pays_naiss
            FROM personnes WHERE IDpersonne=%d;
        """ % IDpersonne
        DB.ExecuterReq(req)
        listePersonne = DB.ResultatReq()[0]
        
        civilite = listePersonne[0]
        nom = listePersonne[1]
        nom_jfille = listePersonne[2]
        prenom = listePersonne[3]
        date_naiss = listePersonne[4]
        if date_naiss == None : date_naiss = ""
        if date_naiss != "" : date_naiss = FonctionsPerso.DateEngFr(date_naiss)
        cp_naiss = listePersonne[5]
        if cp_naiss != "" and cp_naiss != None and cp_naiss != "     " :
            cp_naiss = "%05d" % cp_naiss
        else:
            cp_naiss = ""
        ville_naiss = listePersonne[6]
        IDnationalite = listePersonne[7]
        num_secu = listePersonne[8]
        adresse_resid = listePersonne[9]
        cp_resid = listePersonne[10]
        if cp_resid != "" and cp_resid != None and cp_resid != "     " :
            cp_resid = "%05d" % cp_resid
        else:
            cp_resid = ""
        ville_resid = listePersonne[11]
        IDsituation = listePersonne[12]
        IDpays_naiss = listePersonne[13]
        
        # Adaptation des données
        if civilite == "Mr" : 
            civilite = "M."
            sexe = _(u"Masculin")
            nomNaiss = nom
            nomMarital = ""
        if civilite == "Mme" : 
            civilite = "Mme"
            sexe = _(u"Féminin")
            nomNaiss = nom_jfille
            nomMarital = nom
        if civilite == "Melle" : 
            civilite = "Melle"
            sexe = _(u"Féminin")
            nomNaiss = nom
            nomMarital = ""
        num_secu = num_secu.replace(" ", "")
        date_naiss = date_naiss.replace("/", "")
        depart_naiss = cp_naiss[:2]
        
        # Base coordonnées
        req = """
            SELECT categorie, texte
            FROM coordonnees WHERE IDpersonne=%d AND (categorie='Fixe' or categorie='Mobile');
        """ % IDpersonne
        DB.ExecuterReq(req)
        listeCoords = DB.ResultatReq()
        
        if len(listeCoords) == 0 :
            telephone = "Aucun"
        else : 
            listeCoords.sort()
            telephone = listeCoords[0][1]
            
        # Nationalité
        req = """
            SELECT nationalite
            FROM pays WHERE IDpays=%d;
        """ % IDnationalite
        DB.ExecuterReq(req)
        listePays = DB.ResultatReq()
        nationalite = listePays[0][0]
        if nationalite == _(u"Française") :
            nationalite1 = _(u"Française")
            nationalite2 = ""
        else:
            nationalite1 = _(u"Etrangère")
            nationalite2 = nationalite
        
        # Pays de naissance
        req = """
            SELECT nom
            FROM pays WHERE IDpays=%d;
        """ % IDpays_naiss
        DB.ExecuterReq(req)
        listePays = DB.ResultatReq()
        pays_naiss = listePays[0][0]
                
        # Intégration des données à la liste des valeurs
        listeDonnees = {}
        
        listeDonnees["CIVILITE_SALARIE"] = civilite
        listeDonnees["NOMNAISS_SALARIE"] = nomNaiss
        listeDonnees["NOMMARITAL_SALARIE"] = nomMarital
        listeDonnees["PRENOM_SALARIE"] = prenom
        listeDonnees["SEXE_SALARIE"] = sexe
        listeDonnees["NUMSECU_SALARIE"] = num_secu
        listeDonnees["DATENAISS_SALARIE"] = date_naiss
        listeDonnees["DEPARTNAISS_SALARIE"] = depart_naiss
        listeDonnees["VILLENAISS_SALARIE"] = ville_naiss
        listeDonnees["PAYSNAISS_SALARIE"] = pays_naiss
        listeDonnees["NATIONALITE1_SALARIE"] = nationalite1
        listeDonnees["NATIONALITE2_SALARIE"] = nationalite2
        listeDonnees["ADRESSE_SALARIE"] = adresse_resid
        listeDonnees["CP_SALARIE"] = cp_resid
        listeDonnees["VILLE_SALARIE"] = ville_resid
        listeDonnees["DATE_EMBAUCHE"] = date_debut
        listeDonnees["PERIODE_ESSAI"] = essai
        listeDonnees["DATE_FIN_CONTRAT"] = date_fin
        listeDonnees["CONTRAT_TYPE"] = type_contrat 

        index = 0
        for code, valeur in listeDonnees.iteritems() :
            index = 0
            for champ in champs :
                if champ[0] == code :
                    champs[index][4] = valeur
                index += 1


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "", IDcontrat=1)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
