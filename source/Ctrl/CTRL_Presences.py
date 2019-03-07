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
import sys
from wx.lib.splitter import MultiSplitterWindow
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import GestionDB
import datetime
import FonctionsPerso

from Ctrl import CTRL_Planning
from Ctrl import CTRL_Calendrier_tw
from Dlg import DLG_Application_modele

selectionPersonnes = []     # liste de IDpersonne sélectionnés
selectionDates = []     # liste des dates sélectionnées

# Couleurs
couleurFondPanneau = (122, 161, 230)
couleurFondWidgets = (214, 223, 247)
  
        
class PanelCalendrier(CTRL_Calendrier_tw.Panel):
    def __init__(self, parent, ID=-1):
        CTRL_Calendrier_tw.Panel.__init__(self, parent, ID, bordHaut=35, bordBas=15, bordLateral=15)
        self.texteTitre = _(u"Calendrier")
        self.calendrier.SetBackgroundColour(couleurFondWidgets)
        self.SetBackgroundColour((122, 161, 230))
        
        self.dictCouleurs = { "colFond" : (255, 255, 255), "colNormal" : (255, 255, 255), "colWE" : (220, 223, 227), "colSelect" : (255, 162, 0), "colSurvol" : (0, 0, 0), "colFontJours" : (0, 0, 0), "colVacs" : (255, 255, 187), "colFontPresents" : (255, 0, 0), "colFeries" : (200, 200, 200) }
        
        # Couleurs des éléments du calendrier
        self.calendrier.couleurFond = self.dictCouleurs["colFond"]
        self.calendrier.couleurNormal = self.dictCouleurs["colNormal"]
        self.calendrier.couleurWE = self.dictCouleurs["colWE"]
        self.calendrier.couleurSelect = self.dictCouleurs["colSelect"]
        self.calendrier.couleurSurvol = self.dictCouleurs["colSurvol"]
        self.calendrier.couleurFontJours = self.dictCouleurs["colFontJours"]
        self.calendrier.couleurVacances = self.dictCouleurs["colVacs"]
        self.calendrier.couleurFontJoursAvecPresents = self.dictCouleurs["colFontPresents"]
        self.calendrier.couleurFerie = self.dictCouleurs["colFeries"]
        
        
        # Création fond
        self.espaceBord = 10
        self.coinArrondi = 5
        self.hauteurTitre = 17
        self.couleurFondDC = self.GetBackgroundColour()
        self.couleurFondCadre = (214, 223, 247)
        self.couleurFondTitre = (70, 70, 70)
        self.couleurBord = (70, 70, 70)
        self.couleurTexteTitre = (255, 255, 255)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)      
         
    def OnPaint(self, event):
        dc= wx.PaintDC(self)
        dc= wx.BufferedDC(dc)
        largeurDC, hauteurDC= self.GetSizeTuple()
        
        # paint le fond
        dc.SetBackground(wx.Brush(self.couleurFondDC))
        dc.Clear()       
        
        # Cadre du groupe
        dc.SetBrush(wx.Brush(self.couleurFondCadre))
        dc.DrawRoundedRectangle(0+self.espaceBord, 0+self.espaceBord, largeurDC-(self.espaceBord*2), hauteurDC-(self.espaceBord*2), self.coinArrondi)
        # Barre de titre
        dc.SetBrush(wx.Brush(self.couleurFondTitre))
        dc.DrawRoundedRectangle(0+self.espaceBord, 0+self.espaceBord, largeurDC-(self.espaceBord*2), self.hauteurTitre+self.coinArrondi, self.coinArrondi)
        # Dégradé
        dc.GradientFillLinear((self.espaceBord+1, self.espaceBord+7, largeurDC-(self.espaceBord*2)-2, self.hauteurTitre-2), (214, 223, 247), (0, 0, 0), wx.NORTH)
        # Cache pour enlever l'arrondi inférieur de la barre de titre
        dc.SetBrush(wx.Brush(self.couleurFondCadre))
        dc.SetPen(wx.Pen(self.couleurFondCadre, 0))
        dc.DrawRectangle(self.espaceBord+1, self.espaceBord+self.hauteurTitre+1, largeurDC-(self.espaceBord*2)-2, self.coinArrondi+5)
        # Titre
        font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD) 
        dc.SetFont(font)
        dc.SetTextForeground(self.couleurTexteTitre)
        dc.DrawText(self.texteTitre, self.espaceBord+7, self.espaceBord+2)

    def OnEraseBackground(self, event):
        pass  
        
    def SetSelectionDates(self, listeDates):
        global selectionDates
        selectionDates = listeDates

    def GetSelectionDates(self):
        return selectionDates



class CTRL_Annee(wx.SpinCtrl):
    def __init__(self, parent):
        wx.SpinCtrl.__init__(self, parent, -1, min=1950, max=2999)
        self.parent = parent
        self.SetMinSize((60, -1))
        self.SetToolTip(wx.ToolTip(_(u"Sélectionnez une année")))
        annee_actuelle = datetime.date.today().year
        self.SetAnnee(annee_actuelle)

    def SetAnnee(self, annee=None):
        self.SetValue(annee)

    def GetAnnee(self):
        return self.GetValue()



class PanelCalendrierArchive(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID)

        # Création Widgets
        self.calendrier = Calendrier.Calendrier(self, -1)
        self.calendrier.SetBackgroundColour(couleurFondPanneau)
        # Attribution des couleurs au calendrier
        self.calendrier.couleurNormal = couleurFondWidgets
        self.calendrier.couleurWE = (198, 211, 249)
        self.calendrier.couleurSelect = (255, 162, 0)
        
        self.listeMois = [_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre")]
        self.combo_mois = wx.ComboBox(self, -1, "" , (-1, -1) , (-1, -1), self.listeMois , wx.CB_READONLY)
        
        self.spin = wx.SpinButton(self, -1, size=(30, 20),  style=wx.SP_HORIZONTAL)
        self.spin.SetRange(-1, 1)
        
        self.ctrl_annee = CTRL_Annee(self)
        
        dateJour = datetime.datetime.today()
        numMois = dateJour.month
        numAnnee = dateJour.year
        self.combo_mois.SetSelection(numMois-1)
        self.ctrl_annee.SetAnnee(numAnnee)
        
        self.MAJPeriodeCalendrier()
        # Sélection de Aujourdh'ui
        self.calendrier.SelectJours( [datetime.date.today(),] )
        
        self.bouton_CalendrierAnnuel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calendrier_jour.png"), wx.BITMAP_TYPE_PNG), size=(28, 21))
        self.bouton_CalendrierAnnuel.SetToolTipString(_(u"Cliquez ici pour afficher le calendrier annuel"))
        
        self.barreTitre = FonctionsPerso.BarreTitre(self, _(u"Calendrier"), _(u"Ceci est l'info-bulle !"))

        # Layout
        sizer =  wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.barreTitre, 0, wx.EXPAND, 0)
        sizerOptions = wx.FlexGridSizer(rows=1, cols=8, vgap=0, hgap=5)
        sizerOptions.Add(self.bouton_CalendrierAnnuel, 0)
        sizerOptions.Add(self.combo_mois, 0, wx.EXPAND, 0)
        sizerOptions.Add(self.ctrl_annee, 0)
        sizerOptions.Add(self.spin, 0)
        sizerOptions.AddGrowableCol(1)
        
        sizer.Add(sizerOptions, 0, wx.EXPAND|wx.ALL, 10)
        sizer.Add(self.calendrier, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)
        
        self.SetSizer(sizer)
        
        # Bind
        self.Bind(wx.EVT_SPIN, self.OnSpin, self.spin)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuel, self.bouton_CalendrierAnnuel)
        self.Bind(wx.EVT_COMBOBOX, self.OnComboMois, self.combo_mois)
        self.ctrl_annee.Bind(wx.EVT_SPINCTRL, self.OnComboAnnee)
                
    def MAJselectionDates(self, listeDates) :
        global selectionDates
        selectionDates = listeDates
        self.GetGrandParent().GetParent().MAJpanelPlanning()
        self.GetGrandParent().GetParent().panelPersonnes.listCtrlPersonnes.CreateCouleurs()

    def OnSpin(self, event):
        x = event.GetPosition()
        if self.combo_mois.IsEnabled() == True :
            # Changement du mois
            mois = self.combo_mois.GetSelection() + 1
            annee = self.ctrl_annee.GetAnnee()
            mois = mois + x
            if mois == 0 :
                mois = 12
                annee = annee - 1
            if mois == 13 :
                mois = 1
                annee = annee + 1
            self.combo_mois.SetSelection(mois-1)
            self.ctrl_annee.SetAnnee(annee)
        else:
            # Changement de l'année uniquement
            annee = self.ctrl_annee.GetAnnee() + x
            self.ctrl_annee.SetAnnee(annee)
        self.spin.SetValue(0)
        self.MAJPeriodeCalendrier()
        
    def OnBoutonAnnuel(self, event) :
        if self.calendrier.GetTypeCalendrier() == "mensuel" :
            self.calendrier.SetTypeCalendrier("annuel")
            self.combo_mois.Enable(False)
            self.bouton_CalendrierAnnuel.SetToolTipString(_(u"Cliquez ici pour afficher le calendrier mensuel"))
            self.GetGrandParent().SetSashPosition(450, True)
            self.GetParent().SetSashPosition(0, 400)
        else:
            self.calendrier.SetTypeCalendrier("mensuel")
            self.combo_mois.Enable(True)
            self.bouton_CalendrierAnnuel.SetToolTipString(_(u"Cliquez ici pour afficher le calendrier annuel"))
            self.GetGrandParent().SetSashPosition(230, True)
            self.GetParent().SetSashPosition(0, 220)
    
    def MAJPeriodeCalendrier(self) :
        mois = self.combo_mois.GetSelection() + 1
        annee = int(self.combo_annee.GetValue())
        self.calendrier.SetMoisAnneeCalendrier(mois, annee)
        
    def OnComboMois(self, event) :
        self.MAJPeriodeCalendrier()

    def OnComboAnnee(self, event) :
        self.MAJPeriodeCalendrier()
 
    def MAJpanel(self):
        self.calendrier.MAJpanel()
        
    def MAJcontrolesNavigation(self, mois, annee):
        self.combo_mois.SetSelection(mois-1)
        self.ctrl_annee.SetAnnee(annee)
        


# ===========================================================================================================================


class ListCtrl_Legendes(wx.ListCtrl):
    def __init__(self, parent, ID=-1):
        wx.ListCtrl.__init__(self, parent, ID, size=(-1, -1), style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_SINGLE_SEL|wx.NO_BORDER)
        self.parent = parent
        self.popupIndex = -1

        self.SetBackgroundColour(couleurFondWidgets)
       
        self.InsertColumn(0, _(u"Catégories"))
        self.SetColumnWidth(0, 130)
        self.InsertColumn(1, _(u"Temps"), wx.LIST_FORMAT_RIGHT)
        self.SetColumnWidth(1, 60)        

        # Création des items
        self.Remplissage()

        # Binds
##        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
##        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        #self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        #self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
    
    def Importation(self):
        self.DictCategories = self.GetGrandParent().GetGrandParent().panelPlanning.DCplanning.dictCategories
        
        # ImageList
        self.il = wx.ImageList(16,16)
        for key, valeurs in self.DictCategories.iteritems() :
            r, v, b = self.FormateCouleur(valeurs[3])
            exec("self.img" + str(key) + " = self.il.Add(self.CreationImage((16, 16), r, v, b, key))")
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)     
        
    def Remplissage(self):
        """ Remplissage du ListCtrl """
        
        self.Importation()
        
        # S'il existe des items, on les efface d'abord
        if self.GetItemCount() != 0:
            self.DeleteAllItems()
            
        # Création des items
        index = 0
        totalMinutes = 0
        for key, valeurs in self.DictCategories.iteritems():
            if valeurs[4] != 0 :
                nomCategorie = valeurs[0]
                texteCouleur = valeurs[3]
                dureeMinutes = valeurs[4]
                totalMinutes += dureeMinutes
                # Format du temps secondes->minutes
                if dureeMinutes != 0 :
                    nbreHeures = dureeMinutes/60
                    nbreMinutes = dureeMinutes-(nbreHeures*60)
                    if len(str(nbreMinutes))==1 : nbreMinutes = str("0") + str(nbreMinutes)
                    duree = str(nbreHeures) + "h" + str(nbreMinutes)
                else:
                    duree = ""
                
                # Création de l'item
                self.InsertStringItem(index, nomCategorie)
                self.SetStringItem(index, 1, duree)
                # Intégration de l'image
                exec("self.SetItemImage(index, self.img" + str(key) + ")")

                # Intégration du data ID
                self.SetItemData(index, key)
                index += 1
                
        # Création du total des durées
        if totalMinutes != 0 :
            nbreHeures = totalMinutes/60
            nbreMinutes = totalMinutes-(nbreHeures*60)
            if len(str(nbreMinutes))==1 : nbreMinutes = str("0") + str(nbreMinutes)
            duree = str(nbreHeures) + "h" + str(nbreMinutes)
            self.InsertStringItem(index, "Total")
            self.SetStringItem(index, 1, str(duree))
            self.SetItemData(index, 0)
            item = self.GetItem(index)
            item.SetTextColour(couleurFondPanneau)
            self.SetItem(item)
                
    def MAJ(self):
        self.Remplissage()    
                   
    def OnItemSelected(self, event):
        """ Item cliqué """
        # Désactivation de la capture de la souris pour le popup
        if self.HasCapture():
            self.ReleaseMouse()
        event.Skip()

    def OnItemActivated(self, event):
        """ Item double-cliqué """
        self.DestroyPopup()
        self.parent.ModifierCoord()
        event.Skip()
        
    def OnSize(self, event):
        # La largeur de la colonne 0 s'adapte à la largeur du listCtrl
        size = self.GetSize()
        self.SetColumnWidth(0, size.x-82)
        event.Skip()

    def OnMouseMotion(self, event):
	index = self.HitTest(event.GetPosition())[0]
            
	if index == -1:
            if self.popupIndex != -1 :
                self.DestroyPopup()
            return
        
	item = self.GetItem(index, 0)
       
        pos = self.ClientToScreen(event.GetPosition()) # Position du curseur sur l'écran
        decalage = (10, -50)

        tailleCtrl = self.GetSize()

        # Si le Popup est au bord du ListCtrl, on le ferme
        posInListCtrl = event.GetPosition() # Position du curseur dans le ListCtrl
        if self.popupIndex != -1:
            if posInListCtrl[0] < 4 or posInListCtrl[1] < 4 :
                self.DestroyPopup()
                return

        # Si on était déjà sur l'item , on ne fait que bouger le popup 
        if self.popupIndex == index :
            self.Popup.Position(pos, decalage)

        if self.popupIndex != index and self.popupIndex != -1:
            self.DestroyPopup()

        # Sinon, création d'un popup
        if self.popupIndex != index and posInListCtrl[0] > 3 and posInListCtrl[1] > 3:
            key = self.GetItemData(index)
            self.popupIndex = index
            self.Popup = TestPopup(self, key=key)
            self.Popup.Position(pos, decalage)
            self.Popup.Show(True)
            self.CaptureMouse()

    def DestroyPopup(self):
        """ Destruction de la fenêtre Popup """
        if self.HasCapture():
            self.ReleaseMouse()

        try:
            self.Popup
            self.Popup.Destroy()
            self.popupIndex = -1
        except:
            pass
            
            

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel du ListCtrl."""

       
        # Création du menu contextuel
        menuPop = wx.Menu()

        menuPop.Append(400, _(u"Ajouter1"), "aide sur ajouter1", wx.ITEM_RADIO)
        menuPop.Append(401, _(u"Ajouter2"), "aide sur ajouter2", wx.ITEM_RADIO)
        menuPop.Append(402, _(u"Ajouter3"), "aide sur ajouter3", wx.ITEM_RADIO)
        
        menuPop.AppendSeparator()


        menuPop.AppendRadioItem(301, "IDLE", "a Python shell using tcl/tk as GUI")
        menuPop.AppendRadioItem(302, "IDLE", "a Python shell using tcl/tk as GUI")
        menuPop.AppendRadioItem(303, "IDLE", "a Python shell using tcl/tk as GUI")

        menuPop.AppendSeparator()

       
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Menu_Ajouter(self, event):
        self.parent.AjouterCoord()
        
    def Menu_Modifier(self, event):
        self.parent.ModifierCoord()

    def Menu_Supprimer(self, event):
        self.parent.SupprimerCoord()

    def Menu_Envoyer_Email(self, event):
        print "Envoie Email"
        
        destinataire = _(u"ggamer@wanadoo.fr")
        sujet = _(u"Test")
        message = _(u"Salut ca va")
        pieceJointe = "c:\attachment1.txt;c:\attachment2"
        EnvoiMails.mailto_url(destinataire, sujet, message)

    def FormateCouleur(self, texte):
        pos1 = texte.index(",")
        pos2 = texte.index(",", pos1+1)
        r = int(texte[1:pos1])
        v = int(texte[pos1+2:pos2])
        b = int(texte[pos2+2:-1])
        return (r, v, b)

    def CreationImage(self, tailleImages, r, v, b, IDcategorie):
        """ Création des images pour le TreeCtrl """
        bmp = wx.EmptyImage(tailleImages[0], tailleImages[1], True)
        colFond = couleurFondWidgets
        bmp.SetRGBRect((0, 0, 16, 16), colFond[0], colFond[1], colFond[2])
        bmp.SetRGBRect((3, 3, 10, 10), 0, 0, 0)
        bmp.SetRGBRect((4, 4, 8, 8), r, v, b)
        return bmp.ConvertToBitmap()

  
class TestPopup(wx.PopupWindow):
    """Adds a bit of text and mouse movement to the wx.PopupWindow"""
    def __init__(self, parent, style=wx.SIMPLE_BORDER, key=0):
        wx.PopupWindow.__init__(self, parent, style)
        
        # Récupération des données
        self.parent = parent
        """valeurs = self.parent.DictCoords[key]
        categorie = valeurs[2]
        texte = valeurs[3]
        intitule = valeurs[4]
        
        # Intégration de l'image
        if categorie == "Fixe":
            img = wx.Bitmap("Images/32x32/Maison.png", wx.BITMAP_TYPE_PNG)
        if categorie == "Mobile":
            img = wx.Bitmap("Images/32x32/Mobile.png", wx.BITMAP_TYPE_PNG)
        if categorie == "Fax":
            img = wx.Bitmap("Images/32x32/Fax.png", wx.BITMAP_TYPE_PNG)
        if categorie == "Email":
            img = wx.Bitmap("Images/32x32/Mail.png", wx.BITMAP_TYPE_PNG)"""

        # Création des widgets
        self.panel_base = wx.Panel(self, -1)
        self.label_coords = wx.StaticText(self.panel_base, -1, "Bonjour !")
        self.label_Intitu = wx.StaticText(self.panel_base, -1, "Ca va ?")

        self.label_coords.SetForegroundColour(wx.Colour(255, 0, 0))
        self.label_coords.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

        # Mise en page
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(rows=1, cols=2, vgap=0, hgap=0)
        grid_sizer_2 = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_2.Add(self.label_coords, 0, wx.TOP, 5)
        grid_sizer_2.Add(self.label_Intitu, 0, 0, 0)
        grid_sizer_2.AddGrowableCol(0)
        grid_sizer_1.Add(grid_sizer_2, 1, wx.RIGHT, 5)
        self.panel_base.SetSizer(grid_sizer_1)
        grid_sizer_1.AddGrowableRow(0)
        grid_sizer_1.AddGrowableCol(1)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        wx.CallAfter(self.Refresh)



class PanelLegendes(FonctionsPerso.PanelArrondi):
    def __init__(self, parent, ID=-1):
        FonctionsPerso.PanelArrondi.__init__(self, parent, ID, texteTitre = _(u"Légende"))

        # Création Widgets
        self.listCtrlLegendes = ListCtrl_Legendes(self, -1)
##        self.barreTitre = FonctionsPerso.BarreTitre(self, _(u"Légende"), _(u"Ceci est l'info-bulle !"), arrondis=True, couleurFondPanel=self.GetParent().GetBackgroundColour())
        
        # Layout
        #box = wx.StaticBox(self, -1, "This is a wx.StaticBox")
        #sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer = wx.BoxSizer(wx.VERTICAL)
##        sizer.Add(self.barreTitre, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 10)
        sizer.Add((19, 19), 0, wx.EXPAND, 0)
        sizer.Add(self.listCtrlLegendes, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.TOP, 12)
        self.SetSizer(sizer)
    
    def MAJpanel(self):
        self.listCtrlLegendes.MAJ()


# =========================================================================================================





class listCtrl_Personnes(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.NO_BORDER)
        CheckListCtrlMixin.__init__(self)
        self.parent = parent
        
        self.SetBackgroundColour(couleurFondWidgets)
        self.Remplissage()
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        #self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
        #self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self.list)

    def Remplissage(self):

        self.ClearAll()

        # Création des colonnes
        self.InsertColumn(0, "Personnes")

        # Remplissage avec les valeurs
        for key, valeurs in self.parent.dictPersonnes.iteritems():
            if valeurs[3] == True :
                if self.parent.triCritere == "prenom" :
                    txt = valeurs[1] + " " + valeurs[0]
                else:
                    txt = valeurs[0] + " " + valeurs[1]
                index = self.InsertStringItem(sys.maxint, txt)
                self.SetItemData(index, key)
                # Sélection
                if valeurs[4] == True :
                    self.CheckItem(index)                    

        # Ajustement tailles colonnes
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)

        # Tri
        self.SortItems(self.columnSorter)

    def CreateCouleurs(self, cocheAussi = True):
        # Couleur si animateur présent sur la période sélectionnée
        listePresents = self.GetGrandParent().GetGrandParent().panelPlanning.listePresents
        
        for index in range(self.GetItemCount()) :
            item = self.GetItem(index)
            key = self.GetItemData(index)
            if  key in listePresents :
                item.SetTextColour(wx.RED)
                self.SetItem(item)
                self.RefreshItem(index)
                if cocheAussi == True : self.CheckItem(index, True)
            else:
                item.SetTextColour(wx.BLACK)
                self.SetItem(item)
                self.RefreshItem(index)
                if cocheAussi == True : self.CheckItem(index, False)
                
    def columnSorter(self, key1, key2):
        if self.parent.triOrdre == "decroissant" :
            key1, key2 = key2, key1
        if self.parent.triCritere == "presence" :
            item1 = self.parent.dictPersonnes[key1][2]
            item2 = self.parent.dictPersonnes[key2][2]
        else:
            item1 = self.parent.dictPersonnes[key1][0] + " " + self.parent.dictPersonnes[key1][1]
            item2 = self.parent.dictPersonnes[key2][0] + " " + self.parent.dictPersonnes[key2][1]
	if item1 == item2:  
	    return 0
	elif item1 < item2: 
	    return -1
	else:           
	    return 1

    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)

    # this is called by the base class when an item is checked/unchecked
    def OnCheckItem(self, index, flag):
        IDpersonne = self.GetItemData(index)
        global selectionPersonnes
        if flag:
            self.parent.dictPersonnes[IDpersonne][4] = True
            if IDpersonne not in selectionPersonnes :
                selectionPersonnes.append(IDpersonne)
            
        else:
            self.parent.dictPersonnes[IDpersonne][4] = False
            if IDpersonne in selectionPersonnes :
                selectionPersonnes.remove(IDpersonne)
        
        # MAJ du DC planning
        self.GetGrandParent().GetGrandParent().MAJpanelPlanning()

    def OnContextMenu(self, event):
        self.parent.Menu_Personnes(event)
    
    def GetListePersonnes(self):
        return selectionPersonnes
    

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,-1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent

        self.SetDescriptiveText(_(u"Rechercher une personne"))
        self.ShowSearchButton(True)
        self.ShowCancelButton(True)

        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnSearch(self, evt):
        self.Recherche(self.GetValue())
            
    def OnCancel(self, evt):
        self.SetValue("")

    def OnDoSearch(self, evt):
        self.Recherche(self.GetValue())
        
    def Recherche(self, txtSearch):
        dictPersonnes = self.parent.dictPersonnes
        txtSearch = txtSearch.upper()
        
        # Recherche dans le dictPersonnes
        for key, valeurs in dictPersonnes.iteritems():
            if self.parent.triCritere == "prenom" :
                txt = valeurs[1] + " " + valeurs[0]
            else:
                txt = valeurs[0] + " " + valeurs[1]
            txtItem = txt.upper()
            if txtSearch in txtItem :
                dictPersonnes[key][3] = True
            else:
                dictPersonnes[key][3] = False
            
        # MAJ du listCtrl
        self.parent.MAJlistCtrl()
        


class PanelPersonnes(FonctionsPerso.PanelArrondi):
    def __init__(self, parent, ID=-1):
        FonctionsPerso.PanelArrondi.__init__(self, parent, ID, texteTitre=_(u"Personnes"))

        self.triCritere = FonctionsPerso.Parametres(mode="get", categorie="presences", nom="tri_critere", valeur="presence")
        self.triOrdre = FonctionsPerso.Parametres(mode="get", categorie="presences", nom="tri_ordre", valeur="decroissant")

        # Création Widgets
        self.imgMenu = wx.StaticBitmap(self, bitmap=wx.Bitmap(Chemins.GetStaticPath("Images/16x16/MiniFleche_bas_nr.png"), wx.BITMAP_TYPE_PNG))
        self.imgMenu.SetBackgroundColour(couleurFondWidgets)
        self.imgMenu.SetToolTipString(_(u"Cliquez ici pour afficher le menu des options d'affichage de la liste"))
        self.txtOptions = wx.StaticText(self, -1, "")
        self.txtOptions.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.txtOptions.SetBackgroundColour(couleurFondWidgets)
        self.txtOptions.SetToolTipString(_(u"Cliquez ici pour afficher le menu des options d'affichage de la liste"))
        self.MAJtexteOptions()
        
##        self.barreTitre = FonctionsPerso.BarreTitre(self, _(u"Liste des personnes"), _(u"Ceci est l'info-bulle !"), arrondis=True, couleurFondPanel=self.GetParent().GetBackgroundColour())

        self.dictPersonnes = self.Import_Personnes()
        self.listCtrlPersonnes = listCtrl_Personnes(self)
        self.barreRecherche = BarreRecherche(self)

        self.imgMenu.Bind(wx.EVT_MOTION, self.OnMotion_imgMenu)
        self.imgMenu.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow_imgMenu)
        self.imgMenu.Bind(wx.EVT_LEFT_DOWN, self.Menu_Personnes)
        self.txtOptions.Bind(wx.EVT_MOTION, self.OnMotion_imgMenu)
        self.txtOptions.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow_imgMenu)
        self.txtOptions.Bind(wx.EVT_LEFT_DOWN, self.Menu_Personnes)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
##        sizer.Add(self.barreTitre, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
        sizer.Add((18, 18), 0, wx.EXPAND, 0)
        
        sizerOptions = wx.BoxSizer(wx.HORIZONTAL)
        sizerOptions.Add(self.imgMenu, 0)
        sizerOptions.Add(self.txtOptions, wx.TOP, 1)
        sizer.Add(sizerOptions, 0, wx.LEFT|wx.RIGHT|wx.TOP, 11)
        sizer.Add(self.listCtrlPersonnes, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 16)
        sizer.Add(self.barreRecherche, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 16)
        self.SetSizer(sizer)    
        
    def MAJtexteOptions(self):
        """ Creation du StaticText options d'affichage """
        if self.triOrdre == "croissant" : txt = _(u"Tri asc. selon ")
        if self.triOrdre == "decroissant" : txt = _(u"Tri desc. selon ")

        if self.triCritere == "presence" : txt += _(u"la dernière présence")
        if self.triCritere == "nom" : txt += _(u"le nom")
        if self.triCritere == "prenom" : txt += _(u"le prénom")

        self.txtOptions.SetLabel(txt)

    def OnMotion_imgMenu(self, event):
        self.imgMenu.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/MiniFleche_bas_rg.png"), wx.BITMAP_TYPE_PNG))
        event.Skip()

    def OnLeaveWindow_imgMenu(self, event):
        self.imgMenu.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/MiniFleche_bas_nr.png"), wx.BITMAP_TYPE_PNG))
        event.Skip()

    def MAJpanel(self):
        # MAJ du texte options
        self.MAJtexteOptions()
        # MAJ du listCtrl
        self.dictPersonnes = self.Import_Personnes()
        self.listCtrlPersonnes.Remplissage()
        self.listCtrlPersonnes.CreateCouleurs(True)
       
    def Menu_Personnes(self, event):
        """Ouverture du menu contextuel du ListCtrl."""
        
        # Création du menu contextuel
        menu = wx.Menu()

        smTri = wx.Menu()
        smTri.Append(110, _(u"Dernière présence"), _(u"Trier selon la dernière présence"), wx.ITEM_RADIO)
        smTri.Append(120, _(u"Nom"), _(u"Trier selon le nom"), wx.ITEM_RADIO)
        smTri.Append(130, _(u"Prénom"), _(u"Trier selon le prénom"), wx.ITEM_RADIO)
        if self.triCritere == "presence" : smTri.Check(110, True)
        if self.triCritere == "nom" : smTri.Check(120, True)
        if self.triCritere == "prenom" : smTri.Check(130, True)
        menu.AppendMenu(10, "Tri par", smTri)
        

        smOrdre = wx.Menu()
        smOrdre.Append(210, _(u"Ordre croissant"), _(u"Trier par ordre croissant"), wx.ITEM_RADIO)
        smOrdre.Append(220, _(u"Ordre décroissant"), _(u"Trier par ordre décroissant"), wx.ITEM_RADIO)
        if self.triOrdre == "croissant" : smOrdre.Check(210, True)
        if self.triOrdre == "decroissant" : smOrdre.Check(220, True)
        menu.AppendMenu(20, "Ordre de tri", smOrdre)

        menu.AppendSeparator()
        
        menu.Append(30, _(u"Afficher toute la liste"), _(u"Tout afficher"))
        
        menu.AppendSeparator()
        
        menu.Append(40, _(u"Tout sélectionner"), _(u"Tout sélectionner"))
        menu.Append(50, _(u"Tout désélectionner"), _(u"Tout désélectionner")) 
        
        index = self.listCtrlPersonnes.GetFirstSelected()
        if index != -1:
            IDpersonne = int(self.listCtrlPersonnes.GetItemData(index))
            nomPersonne = self.listCtrlPersonnes.GetItem(index, 0).GetText()
            texte = _(u"Sélectionner uniquement ") + nomPersonne
            menu.Append(55, texte, texte)
             
        menu.Append(60, _(u"Sélectionner les personnes présentes"), _(u"Sélectionner les personnes présentes sur les jours sélectionnés"))
        
        menu.AppendSeparator()
        
        menu.Append(70, _(u"Appliquer un modèle aux personnes sélectionnées"), _(u"Appliquer un modèle aux personnes sélectionnées"))
        
        index = self.listCtrlPersonnes.GetFirstSelected()
        if index != -1:
            IDpersonne = int(self.listCtrlPersonnes.GetItemData(index))
            nomPersonne = self.listCtrlPersonnes.GetItem(index, 0).GetText()
            menu.AppendSeparator()
            texte = _(u"Afficher la liste des présences de ") + nomPersonne
            menu.Append(80, texte, texte)
            
            texte = _(u"Imprimer un planning annuel pour ") + nomPersonne
            menu.Append(90, texte, texte)

        self.Bind(wx.EVT_MENU, self.Menu_110, id=110)
        self.Bind(wx.EVT_MENU, self.Menu_120, id=120)
        self.Bind(wx.EVT_MENU, self.Menu_130, id=130)
        self.Bind(wx.EVT_MENU, self.Menu_210, id=210)
        self.Bind(wx.EVT_MENU, self.Menu_220, id=220)
        self.Bind(wx.EVT_MENU, self.Menu_30, id=30)
        self.Bind(wx.EVT_MENU, self.Menu_40, id=40)
        self.Bind(wx.EVT_MENU, self.Menu_50, id=50)
        self.Bind(wx.EVT_MENU, self.Menu_55, id=55)
        self.Bind(wx.EVT_MENU, self.Menu_60, id=60)
        self.Bind(wx.EVT_MENU, self.Menu_70, id=70)
        self.Bind(wx.EVT_MENU, self.Menu_80, id=80)
        self.Bind(wx.EVT_MENU, self.Menu_90, id=90)
        
        self.PopupMenu(menu)
        menu.Destroy()

    def MAJlistCtrl(self):
        self.listCtrlPersonnes.Remplissage()
        self.listCtrlPersonnes.CreateCouleurs(False)
        
        
    def Menu_110(self, event):
        self.triCritere = "presence"
        self.MAJtexteOptions()
        FonctionsPerso.Parametres(mode="set", categorie="presences", nom="tri_critere", valeur=self.triCritere)
        self.MAJlistCtrl()

    def Menu_120(self, event):
        self.triCritere = "nom"
        self.MAJtexteOptions()
        FonctionsPerso.Parametres(mode="set", categorie="presences", nom="tri_critere", valeur=self.triCritere)
        self.MAJlistCtrl()

    def Menu_130(self, event):
        self.triCritere = "prenom"
        self.MAJtexteOptions()
        FonctionsPerso.Parametres(mode="set", categorie="presences", nom="tri_critere", valeur=self.triCritere)
        self.MAJlistCtrl()

    def Menu_210(self, event):
        self.triOrdre = "croissant"
        self.MAJtexteOptions()
        FonctionsPerso.Parametres(mode="set", categorie="presences", nom="tri_ordre", valeur=self.triOrdre)
        self.MAJlistCtrl()

    def Menu_220(self, event):
        self.triOrdre = "decroissant"
        self.MAJtexteOptions()
        FonctionsPerso.Parametres(mode="set", categorie="presences", nom="tri_ordre", valeur=self.triOrdre)
        self.MAJlistCtrl()
    
    def Menu_30(self, event):
        """ Afficher tout """
        for key, valeurs in self.dictPersonnes.iteritems():
            self.dictPersonnes[key][3] = True
        self.MAJlistCtrl()

    def Menu_40(self, event):
        """ Tout sélectionner """
##        global selectionPersonnes
##        selectionPersonnes = []
##        for key, valeurs in self.dictPersonnes.iteritems():
##            self.dictPersonnes[key][4] = True
##            selectionPersonnes.append(key)
##        self.MAJlistCtrl()
        
        for index in range(self.listCtrlPersonnes.GetItemCount()) :
            item = self.listCtrlPersonnes.GetItem(index)
            self.listCtrlPersonnes.CheckItem(index, True)

    def Menu_50(self, event):
        """ Tout désélectionner """
##        global selectionPersonnes
##        selectionPersonnes = []
##        for key, valeurs in self.dictPersonnes.iteritems():
##            self.dictPersonnes[key][4] = False
##        self.MAJlistCtrl()
##        self.GetGrandParent().GetParent().MAJpanelPlanning()
        
        for index in range(self.listCtrlPersonnes.GetItemCount()) :
            item = self.listCtrlPersonnes.GetItem(index)
            self.listCtrlPersonnes.CheckItem(index, False)

    def Menu_55(self,event):
        """ Sélectionne uniquement la personne sélectionnée """
        indexSelect = self.listCtrlPersonnes.GetFirstSelected()
        IDpersonne = int(self.listCtrlPersonnes.GetItemData(indexSelect))
        
        for index in range(self.listCtrlPersonnes.GetItemCount()) :
            item = self.listCtrlPersonnes.GetItem(index)
            if index == indexSelect :
                etat = True
            else:
                etat = False
            self.listCtrlPersonnes.CheckItem(index, etat)
        
    def Menu_60(self,event):
        """ Sélectionne uniquement les personnes présentes sur les jours sélectionnés """
        listePresents = self.GetGrandParent().GetParent().panelPlanning.listePresents
        listCtrl = self.listCtrlPersonnes
        for index in range(listCtrl.GetItemCount()) :
            item = listCtrl.GetItem(index)
            key = listCtrl.GetItemData(index)
            if  key in listePresents :
                listCtrl.CheckItem(index, True)
            else:
                listCtrl.CheckItem(index, False)
                
    def Menu_70(self,event):
        """ Application d'un modèle aux personnes sélectionnées dans le listCtrl personnes """
        selectionPersonnes = []
        for index in range(self.listCtrlPersonnes.GetItemCount()) :
            if self.listCtrlPersonnes.IsChecked(index) == True :
                key = self.listCtrlPersonnes.GetItemData(index)
                selectionPersonnes.append(key)
        
        if len(selectionPersonnes) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord cocher un ou plusieurs noms de personnes dans la liste."), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy() 
            return
        
        # Récupération des dates du calendrier
        selectionDates = self.GetGrandParent().GetParent().GetSelectionDates()
        selectionDates.sort()
        if len(selectionDates) != 0 :
            dateMin = selectionDates[0]
            dateMax = selectionDates[-1]
            selectionDates=(dateMin, dateMax)
        else:
            selectionDates=(None, None)
    
        frm_application = DLG_Application_modele.frm_application_modele(self, selectionPersonnes=selectionPersonnes, selectionDates=selectionDates )
        frm_application.Show()

    def Menu_80(self,event):
        """ Ouvre la liste des présences de la personne sélectionnée """
        index = self.listCtrlPersonnes.GetFirstSelected()
        IDpersonne = int(self.listCtrlPersonnes.GetItemData(index))
        from Ctrl import CTRL_Page_presences
        frm_liste = CTRL_Page_presences.MyFrame(self, IDpersonne=IDpersonne)
        frm_liste.Show()
        
    def Menu_90(self,event):
        """ Imprime le plannign annuel """
        index = self.listCtrlPersonnes.GetFirstSelected()
        IDpersonne = int(self.listCtrlPersonnes.GetItemData(index))
        from Dlg import DLG_Impression_calendrier_annuel
        dlg = DLG_Impression_calendrier_annuel.MyDialog(None, IDpersonne=IDpersonne, autoriser_choix_personne=False)
        dlg.ShowModal()       
        
    def Import_Personnes(self):
        """ Importe les noms des personnes de la base """
        
        req = """
            SELECT personnes.IDpersonne, personnes.nom, personnes.prenom, Max(presences.date) AS MaxDedate
            FROM personnes LEFT JOIN presences ON personnes.IDpersonne = presences.IDpersonne
            GROUP BY personnes.IDpersonne, personnes.nom, personnes.prenom
            ORDER BY Max(presences.date);
        """
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()

        # Transformation de la liste en dict
        dictPersonnes = {}
        for personne in listeDonnees :
            dictPersonnes[personne[0]] = [personne[1], personne[2], personne[3], True, False] # Nom, prénom, DateDernièrePrésence, Affiché, Sélectionné
        
        return dictPersonnes

        
# =========================================================================================================

class PanelPresences(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, name="panel_presences")
        self.init = False 
        
    def InitPage(self):
        # Création des splitter
        self.splitterV = wx.SplitterWindow(self, -1, style=wx.SP_3D | wx.SP_NO_XP_THEME | wx.SP_LIVE_UPDATE)
        self.splitterH = MultiSplitterWindow(self.splitterV, -1, style= wx.SP_NOSASH | wx.SP_LIVE_UPDATE)
        self.splitterH.SetOrientation(wx.VERTICAL)
        self.splitterH.SetBackgroundColour(couleurFondPanneau)
        # Création du panel Planning
        self.panelPlanning = CTRL_Planning.PanelPlanning(self.splitterV, -1)
        # Création du panel Calendrier
        self.panelCalendrier = PanelCalendrier(self.splitterH, -1)
        self.panelCalendrier.SetMinSize((200, 220))
        self.splitterH.AppendWindow(self.panelCalendrier, 220)
        # Création du panel Légendes
        self.panelLegendes = PanelLegendes(self.splitterH, -1)
        #self.panelLegendes.SetMinSize((300, 200))
        self.splitterH.AppendWindow(self.panelLegendes, 160)
        # Création du panel Personnes
        self.panelPersonnes = PanelPersonnes(self.splitterH, -1)
        self.panelPersonnes.SetMinSize((200, 200))
        self.splitterH.AppendWindow(self.panelPersonnes, 200)

        self.splitterH.SetMinimumPaneSize(100)
        
        self.__do_layout()
        
        # Affichage des présences d'aujourd'hui
        self.panelCalendrier.MAJselectionDates(listeDates=selectionDates)

        self.init = True
        
    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        self.splitterV.SplitVertically(self.splitterH, self.panelPlanning, 240)
        sizer_base.Add(self.splitterV, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)

##    def OnSashChanging(self, evt):
##        print evt.GetSashPosition()
##        # This is one way to control the sash limits
##        if evt.GetSashPosition() <= 232 :
##            evt.Veto()
            
    def SetSelectionDates(self, selecDates) :
        global selectionDates
        selectionDates = selecDates

    def GetSelectionDates(self) :
        return selectionDates
        
    def SetSelectionPersonnes(self, selecPersonnes) :
        global selectionPersonnes
        selectionPersonnes = selecPersonnes
        
    def GetSelectionPersonnes(self) :
        return selectionPersonnes
        
    def MAJpanelPlanning(self, reinitSelectionPersonnes=False) :
        """ Met à jour le DC Planning """
        global selectionPersonnes, selectionDates
        modeAffichage = CTRL_Planning.modeAffichage
        if reinitSelectionPersonnes==True :
            selectionPersonnes = self.panelPlanning.RecherchePresents(selectionDates)
        
        self.panelPlanning.ReInitPlanning(modeAffichage, selectionPersonnes, selectionDates)
        self.panelPlanning.DCplanning.MAJ_listCtrl_Categories()
        self.panelPlanning.DCplanning.MAJAffichage()
    
    def MAJpanel(self, listeElements=[], reinitSelectionPersonnes=False) :
        """ Met à jour les éléments du panel présences """
        # Elements possibles : [] pour tout, planning, listCtrl_personnes, legendes, calendrier
        if self.init == False :
            self.InitPage()
        
        if "planning" in listeElements or listeElements==[] : 
            self.panelPlanning.DCplanning.Init_valeurs_defaut()
            self.panelPlanning.RechargeDictCategories()
            self.MAJpanelPlanning(reinitSelectionPersonnes=True)
        if "listCtrl_personnes" in listeElements or listeElements==[] : 
            self.panelPersonnes.MAJpanel()
        if "legendes" in listeElements or listeElements==[] : 
            self.panelLegendes.MAJpanel()
        if "calendrier" in listeElements or listeElements==[] : 
            self.panelCalendrier.MAJpanel()

        

class TestFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: TestPlanning.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.statusbar = self.CreateStatusBar(2, 0)
        self.statusbar.SetStatusWidths( [360, -1] )
        panel = PanelPresences(self)
        
        self.__set_properties()
        self.__do_layout()
        # end wxGlade


    def __set_properties(self):
        # begin wxGlade: TestPlanning.__set_properties
        self.SetTitle(_(u"Panel Présences"))
        self.SetSize((1000, 800))
##        self.statusbar.SetStatusWidths([-1])
##        # statusbar fields
##        statusbar_fields = [""]
##        for i in range(len(statusbar_fields)):
##            self.statusbar.SetStatusText(statusbar_fields[i], i)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: TestPlanning.__do_layout
        self.Centre()
        
        # end wxGlade

# end of class TestPlanning

    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frameTest = TestFrame(None, -1, "")
    app.SetTopWindow(frameTest)
    frameTest.Show()
    app.MainLoop()
