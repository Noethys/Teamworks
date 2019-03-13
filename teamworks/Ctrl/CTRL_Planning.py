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
import six
import datetime
import time
import GestionDB
import wx.lib.colourdb
from Dlg import DLG_Saisie_presence
from Dlg import DLG_Application_modele
import FonctionsPerso
import operator
import sys
from Utils import UTILS_Fichiers
from Utils import UTILS_Adaptations

if 'phoenix' in wx.PlatformInfo:
    CURSOR = wx.Cursor
else :
    CURSOR = wx.StockCursor

# Déclaration de variables à modifier au choix

heureMin = datetime.time(7, 00)
heureMax = datetime.time(20, 00)

hauteurBarre = 15 # 15 ou 26        # Hauteur en pixel d'une barre
ecartLignes = 5                     # Ecart en pixels entre les lignes
modeTexte = 1                       # Mode d'affichage de la barre : 1=ligneUnique 2=Multiligne
hauteurTitreGroupe = 30             # Hauteur en pixels du titre d'un cadre Groupe
pasScroll = 20                          # Pas de Scroll

tailleFontHeure = 7                 # Taille de font du texte heures debut et fin d'une barre
tailleFontIntitule = 7              # Taille de font du texte intitulé d'une barre

couleurFontHeures = (0, 0, 0)       # Couleur de la font des heures
couleurFontIntitule = (0, 0, 0)   # Couleur de la font des intitulés
     # Couleur du texte d'un entete de ligne sélectionné

couleurBordDefaut = (0, 0, 0)       # Couleur par défaut du bord d'une barre
couleurBackground = (255, 255, 255) # Couleur du background du DC

modeAffichage = 2   # Mode d'affichage : Dates / personnes / etc...

# Valeurs à ne pas changer :
varScroll = 0
largeurEnteteLigne = 0              # Largeur de l'entete de lignes
afficher_temps_ligne = True
afficher_temps_groupe = True
afficher_nbre_presents = True
hauteurBarreNbrePresents = 4
largeurFinLigne = 38                # Largeur de l'espace laissé à la fin de chaque ligne pour le temps de la journée
coordLigne = (0, 0)                 # Coordonnées XG et XD d'une ligne
selectionsLignes = []                         # Liste des sélections d'entetes de lignes

couleurFondSem = (255, 255, 255)    # Couleur d'un jour normal du lundi au vendredi
couleurFondWE = (220, 223, 227)     # Couleur des samedis et dimanche
couleurVacances = (255, 255, 220)   # Couleur des cases dates d'ouverture de la structure
couleurFeries = (200, 200, 200)

couleurBordNormal = (255, 255, 255)       # Couleur des bords des barres
couleurBordSelect = (55, 228, 9)    # Couleur du bord de la case si celle-ci est sélectionnée
couleurBordSurvol = (30, 60, 255)   # Couleur du bord de la case si celle-ci est survolée

# Couleurs
couleurTxtGroupe = (255, 255, 255)                      # Couleur du txt de titre d'un groupe
couleurBarreTitreGroupe = (130, 170, 235)           # Couleur du rectangle d'un titre de groupe
couleurFondGroupe = (214, 223, 247)                 # Couleur du fond d'un groupe
couleurBordGroupe = (122, 161, 230)                     # Couleur du bord d'un groupe
couleurLineGroupe = (122, 161, 230)                              # Couleur de la ligne de la barre de titre de groupe
couleurTxtLigne = (87,126,224)                          # Couleur du txt de l'entete de ligne
couleurLigne = (228, 233, 246)                          # Couleur d'une ligne
couleurLigneSelect = (255, 162, 0)                         # Couleur d'une ligne sélectionnée
couleurTxtLigneSelect = (255, 162, 0)                     # Couleur de txt d'un entete de ligne sélectionné

afficher_contrats = False






def HeuresEnCoords(heure):
    """ Transforme une heure donnée en coordonnées pixels """
    global heureMin, heureMax
    HMin = datetime.timedelta(hours=heureMin.hour, minutes=heureMin.minute)
    HMax = datetime.timedelta(hours=heureMax.hour, minutes=heureMax.minute)
    n = ((HMax - HMin).seconds)/60.0/5.0 # Soit n créneaux de 5 minutes
    gradMin = coordLigne[0] 
    gradMax = coordLigne[1] 
    EcartGrad = gradMax - gradMin
    PixelsPar5Mins = EcartGrad / n
    heure2 = datetime.timedelta(hours=heure.hour, minutes=heure.minute)
    delta = heure2-HMin
    z = delta.seconds/60.0/5.0
    z2 = z * PixelsPar5Mins
    z2 += gradMin
    return z2

def CoordEnHeures(coordX):
    """ Transforme des coordonnées pixels en Heures """
    global heureMin, heureMax
    HMin = datetime.timedelta(hours=heureMin.hour, minutes=heureMin.minute)
    HMax = datetime.timedelta(hours=heureMax.hour, minutes=heureMax.minute)
    n = ((HMax - HMin).seconds)/60.0/5 # Soit n créneaux de 5 minutes
    gradMin = coordLigne[0] 
    gradMax = coordLigne[1]
    EcartGrad = gradMax - gradMin
    PixelsPar5Mins = EcartGrad / n
    z = (coordX-gradMin) / PixelsPar5Mins * 5
    resultatH = HMin + datetime.timedelta(minutes=int(z))
    resultatH = DeltaEnTime(resultatH)
    return resultatH

def AroundHeure(heure):
    """ Arrondit une heure datetime.time donnée aux 5 minutes inférieures ou supérieures """
    minutes = heure.minute
    newMinutes = round((minutes/5)*5, 2)
    resultatH = datetime.time(heure.hour, int(newMinutes))
    return resultatH

def DeltaEnTime(varTimedelta) :
    """ Transforme une variable TIMEDELTA en heure datetime.time """
    heureStr = time.strftime("%H:%M",time.gmtime(varTimedelta.seconds))
    heureFin = StrEnDatetime(heureStr)
    return heureFin

def StrEnDatetime(texteHeure):
    texteHeure = texteHeure[:5]
    posTemp = texteHeure.index(":")
    heuresTemp = int(texteHeure[:posTemp])
    minutesTemp =  int(texteHeure[posTemp+1:])
    heure = datetime.time(heuresTemp, minutesTemp)
    return heure

def StrEnDatetimeDate(texteDate):
    annee = texteDate[:4]
    mois = texteDate[5:7]
    jour = texteDate[8:10]
    date = datetime.date(int(annee), int(mois), int(jour))
    return date

def DatetimeDateEnStr(date):
    """ Transforme un datetime.date en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = ("Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche")
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateStr = listeJours[date.weekday()] + " " + str(date.day) + " " + listeMois[date.month-1] + " " + str(date.year)
    return dateStr




# ---------- GRADUATIONS -------------------------------------------------------------------------------

def AdditionHeures(heureBase, temps, operation="+"):
    """ Additionne ou soustrait des heures ou format datetime.time """   
    heureDebut = datetime.timedelta(hours=heureBase.hour, minutes=heureBase.minute)
    temps = datetime.timedelta(hours=temps.hour, minutes=temps.minute)
    if operation == "+" :
        newHeure = heureDebut + temps
    else:
        newHeure = heureDebut - temps

    heureStr = time.strftime("%H:%M",time.gmtime(newHeure.seconds))
    posTemp = heureStr.index(":")
    heuresTemp = int(heureStr[:posTemp])
    minutesTemp =  int(heureStr[posTemp+1:])  
    
    if heuresTemp > 23:
        print("stop")
        
    heureFin = datetime.time(heuresTemp, minutesTemp)
    return heureFin


class Graduations(wx.ScrolledWindow):

    def __init__(self,parent,ID=-1):
        wx.ScrolledWindow.__init__(self, parent, -1, (0, 0), size=wx.DefaultSize, style=wx.NO_BORDER)
        
        # create a PseudoDC to record our drawing
        if 'phoenix' in wx.PlatformInfo:
            self.pdc = wx.adv.PseudoDC()
        else :
            self.pdc = wx.PseudoDC()
        self.DoDrawing(self.pdc)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x:None)

    def ConvertEventCoords(self, event):
        xView, yView = self.GetViewStart()
        xDelta, yDelta = self.GetScrollPixelsPerUnit()
        return (event.GetX() + (xView * xDelta),
            event.GetY() + (yView * yDelta))
 
    def OffsetRect(self, r):
        xView, yView = self.GetViewStart()
        xDelta, yDelta = self.GetScrollPixelsPerUnit()
        r.OffsetXY(-(xView*xDelta),-(yView*yDelta))
        
    def HeuresEnEntier(self, texteHeure="07:00"):
        """ Transforme une heure string ou datetime.time en entier de type 2075"""
        if type(texteHeure) == datetime.time :
            heures = str(texteHeure.hour)
            minutes = int(texteHeure.minute)
        elif type(texteHeure) == str :
            posTemp = texteHeure.index(":")
            heures = str(texteHeure[0:posTemp])
            minutes = int(texteHeure[posTemp+1:5])
        minutes = str(minutes * 100 //60)
        if len(minutes) == 1 : minutes = "0" + minutes
        heure = str(heures + minutes)
        return int(heure)
        
    def DrawGraduations(self, dc, heureMi="7:00", heureMa="23:30", posY=0):
        """ Dessin des graduations """
        # paramètres Graduations
        graduationMin = self.HeuresEnEntier(heureMi) 
        graduationMax = self.HeuresEnEntier(heureMa) 
        graduationStep = 25
        tailleFont = 7
        hautTraitHeures = 6
        hautTraitDHeures = 4
        hautTraitQHeures = 3

        if graduationMax == 0 : graduationMax = 2400

        # Initialisation pour la graduation
        listeGraduations = range(graduationMin, graduationMax+graduationStep, graduationStep)
        nbreGraduations = len(listeGraduations)
        largeurDc = coordLigne[1] - coordLigne[0] #dc.GetSizeTuple()[0]
        step = largeurDc / round(nbreGraduations-1,1)

        # Création de la graduation
        j = k = etape = 0
        i=coordLigne[0]

        dc.SetPen(wx.Pen("black"))
        dc.SetTextForeground("black")
        font = self.GetFont()
        font.SetPointSize(tailleFont)
        dc.SetFont(font)
        
        for etape in range(nbreGraduations):
            
            if k==4 : k = 0
            if k == 1 or k == 3: hauteurTrait = hautTraitQHeures    # 1/4 d'heures
            if k == 2 : hauteurTrait = hautTraitDHeures    # Demi-Heures
            if k == 0 :
                hauteurTrait = hautTraitHeures
                texte = str(listeGraduations[j]/100)+"h"
                largTexte, hautTexte = self.GetTextExtent(texte)
                # Dessin du texte
                dc.DrawText(texte, i-(largTexte/2), posY)
            # Dessin du trait
            dc.DrawLine(i, posY+hautTexte+hautTraitHeures-hauteurTrait, i, posY+hautTexte+hautTraitHeures)
            i = i + step
            j = j + 1
            k = k + 1
                   
    def OnPaint(self, event):
        # Create a buffered paint DC.  It will create the real
        # wx.PaintDC and then blit the bitmap to it when dc is
        # deleted.  
        dc = wx.BufferedPaintDC(self)
        # use PrepateDC to set position correctly
        self.PrepareDC(dc)
        # we need to clear the dc BEFORE calling PrepareDC
        colFond = wx.SystemSettings.GetColour(30) #self.GetBackgroundColour()
        bg = wx.Brush(colFond)
        dc.SetBackground(bg)
        dc.Clear()
        # create a clipping rect from our position and size
        # and the Update Region
        xv, yv = self.GetViewStart()
        dx, dy = self.GetScrollPixelsPerUnit()
        x, y   = (xv * dx, yv * dy)
        rgn = self.GetUpdateRegion()
        rgn.Offset(x,y)
        r = rgn.GetBox()
        # draw to the dc using the calculated clipping rect
        self.pdc.DrawToDCClipped(dc,r)
        
    def DoDrawing(self, dc):
        dc.RemoveAll()
        if 'phoenix' not in wx.PlatformInfo:
            dc.BeginDrawing()
        self.DrawGraduations(dc, heureMin, heureMax)
        if 'phoenix' not in wx.PlatformInfo:
            dc.EndDrawing()
        
    def MAJAffichage(self):
        self.DoDrawing(self.pdc)
        self.Refresh()



# --------------------------------------------------------------------------------------------------------------------------------------
# ----------- TEST DC -----------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------



class WidgetPlanning(wx.ScrolledWindow):

    def __init__(self, parent, listePresences, dictCategories, dictGroupes, dictLignes):
        wx.ScrolledWindow.__init__(self, parent, -1, (0, 0), size=wx.DefaultSize, name="panel_widgetPlanning", style=wx.NO_BORDER)
    
        self.parent = parent

        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)

        self.maxWidth =0
        self.maxHeight  = 0
        self.SetScrollRate(20,20)

        self.selectBarre = None
        self.selectLigne = None
        self.contraintes = None
        self.selectEcart = None
        self.selectModif = False
        
                
        # Initialise les valeurs par défaut
        self.Init_valeurs_defaut()
        
        # Initialisation des données
        self.InitPlanning(listePresences, dictCategories, dictGroupes, dictLignes)
        
        # Récupération des périodes de vacances et des jours fériés
        self.joursVacances, self.listePeriodesVacs = self.Importation_Vacances()
        self.listeFeriesFixes, self.listeFeriesVariables = self.Importation_Feries()
        self.dictContrats = self.Importation_Contrats()
        
        # create a PseudoDC to record our drawing
        if 'phoenix' in wx.PlatformInfo:
            self.pdc = wx.adv.PseudoDC()
        else:
            self.pdc = wx.PseudoDC()
        self.dictIDs = {}
        self.DoDrawing(self.pdc)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x:None)
        #self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        
        # vars for handling mouse clicks
        self.dragid = -1
        self.lastpos = (0,0)

        self.Bind(wx.EVT_SIZE, self.OnSize)
    
    def Init_valeurs_defaut(self):
        """ Initialise les valeurs par défaut """
        # Afficher les légendes
        global hauteurBarre
        afficher_legendes = FonctionsPerso.Parametres(mode="get", categorie="planning", nom="afficher_legendes", valeur=False)
        if afficher_legendes == True :
            hauteurBarre = 26
        else:
            hauteurBarre = 15
            
        # Afficher les contrats
        global afficher_contrats
        afficher_contrats = FonctionsPerso.Parametres(mode="get", categorie="planning", nom="afficher_contrats", valeur=False)

        # Afficher les temps en fin de ligne
        global afficher_temps_ligne
        afficher_temps_ligne = FonctionsPerso.Parametres(mode="get", categorie="planning", nom="afficher_temps_ligne", valeur=True)
        
        # Afficher les temps en tete de groupe
        global afficher_temps_groupe
        afficher_temps_groupe = FonctionsPerso.Parametres(mode="get", categorie="planning", nom="afficher_temps_groupe", valeur=True)       

        # Afficher les nbre de présents
        global afficher_nbre_presents
        afficher_nbre_presents = FonctionsPerso.Parametres(mode="get", categorie="planning", nom="afficher_nbre_presents", valeur=True)       
        
        # Définir amplitude horaire affichée par défaut
        global heureMin, heureMax
        heureMinStr = FonctionsPerso.Parametres(mode="get", categorie="planning", nom="heureMin", valeur="7:00")
        heureMaxStr = FonctionsPerso.Parametres(mode="get", categorie="planning", nom="heureMax", valeur="20:00")
        heureMinTuple = heureMinStr.split(":")
        heureMaxTuple = heureMaxStr.split(":")
        heureMin = datetime.time(int(heureMinTuple[0]), int(heureMinTuple[1]))
        heureMax = datetime.time(int(heureMaxTuple[0]), int(heureMaxTuple[1]))

    def ConvertEventCoords(self, event):
        xView, yView = self.GetViewStart()
        xDelta, yDelta = self.GetScrollPixelsPerUnit()
        return (event.GetX() + (xView * xDelta),
            event.GetY() + (yView * yDelta))

    def ConvertCoords(self, x, y):
        xView, yView = self.GetViewStart()
        xDelta, yDelta = self.GetScrollPixelsPerUnit()
        return (x - (xView * xDelta), y - (yView * yDelta))
             
    def OffsetRect(self, r):
        xView, yView = self.GetViewStart()
        xDelta, yDelta = self.GetScrollPixelsPerUnit()
        if 'phoenix' in wx.PlatformInfo:
            r.Offset(-(xView*xDelta),-(yView*yDelta))
        else :
            r.OffsetXY(-(xView*xDelta),-(yView*yDelta))


        
    def MAJAffichage(self):
        self.DoDrawing(self.pdc)
        self.Refresh()
                   
    def OnPaint(self, event):
        # Create a buffered paint DC.  It will create the real
        # wx.PaintDC and then blit the bitmap to it when dc is
        # deleted.  
        dc = wx.BufferedPaintDC(self)
        # use PrepateDC to set position correctly
        self.PrepareDC(dc)
        # we need to clear the dc BEFORE calling PrepareDC
        colFond = wx.SystemSettings.GetColour(30) #self.GetBackgroundColour()
        bg = wx.Brush(colFond)
        dc.SetBackground(bg)
        dc.Clear()
        # create a clipping rect from our position and size
        # and the Update Region
        xv, yv = self.GetViewStart()
        dx, dy = self.GetScrollPixelsPerUnit()
        x, y   = (xv * dx, yv * dy)
        rgn = self.GetUpdateRegion()
        rgn.Offset(x,y)
        r = rgn.GetBox()
        
        # draw to the dc using the calculated clipping rect
        self.pdc.DrawToDCClipped(dc,r)

    def DoDrawing(self, dc):
        """ Creation du dessin dans le PseudoDC """
        dc.RemoveAll()
        if 'phoenix' not in wx.PlatformInfo:
            dc.BeginDrawing()

        if 'phoenix' in wx.PlatformInfo:
            tailleDC = self.GetSize()[0]-20,  self.GetSize()[1]
        else:
            tailleDC = self.GetSizeTuple()[0] - 20, self.GetSizeTuple()[1]

            # Calcul de la largeur des entetes de lignes et des lignes
        self.CalcLargeurEnteteLigne(dc)
        self.CalcCoordLignes(tailleDC)
        self.parent.DCgraduations.MAJAffichage()
                
        # Dessin des groupes
        self.DrawGroupes(dc, tailleDC)
        
        # Dessin des présences
        # dc, heureDebut, heureFin, IDcategorie, intitule, posG, posD, posYhaut, posYbas
        for IDpresence, valeurs in self.dictPresences.items() :
            self.dictPresences[IDpresence][7]  = HeuresEnCoords(valeurs[3]) 
            self.dictPresences[IDpresence][8] = HeuresEnCoords(valeurs[4])
            self.DrawBarre(dc, IDpresence, valeurs[3], valeurs[4], valeurs[5], valeurs[6], valeurs[7], valeurs[8], valeurs[9], valeurs[10])

        # Dessine le Nbre de présents par tranche d'heures
        if afficher_nbre_presents == True :
            for keyGroupe, valeurs in self.dictGroupes.items() :
                self.DessineNbrePresents(dc, IDobjet=None, keyGroupe=keyGroupe)

        if 'phoenix' not in wx.PlatformInfo:
            dc.EndDrawing()

 
    def DrawBarre(self, dc, IDpresence, heureDebut, heureFin, IDcategorie, intitule, posG, posD, posYhaut, posYbas, IDobjet=None, mode="screen"):
        """ Dessine une barre """
        y = posYhaut
        h = hauteurBarre
        if mode =="screen":
            if IDobjet == None : IDobjet = wx.NewId()
            dc.SetId(IDobjet)
        
        # Paramètres du dessin
        couleurFondBarre = self.FormateCouleur(self.dictCategories[IDcategorie][3])
        dc.SetBrush(wx.Brush(couleurFondBarre))
        dc.SetPen(wx.Pen(couleurBordDefaut, 1))
       
        # Dessin de la case
        dc.DrawRectangle(posG, y, posD-posG, h)
        
        # Dessin Heures
        dc.SetTextForeground(couleurFontHeures)
        font = self.GetFont()
        font.SetPointSize(tailleFontHeure)
        dc.SetFont(font)
        # Heure Debut
        texteDebut = str(heureDebut)[:5]
        texteDebut = self.AdapteTexteHeure(dc, texteDebut, posD-posG-8)
        if heureDebut < heureMin :
            texteDebut = "<<< " + texteDebut
            dc.SetPen(wx.Pen(couleurFondBarre, 1))
            dc.DrawLine(posG, y, posG, y + h -1)
        dc.DrawText(texteDebut, posG + 3, y + 2)
        # Heure Fin
        texteFin = str(heureFin)[:5]
        texteFin = self.AdapteTexteHeure(dc, texteFin, posD-posG-8)
        largTexte, hautTexte = self.GetTextExtent(texteFin)
        dc.DrawText(texteFin, posD - largTexte , y + 2)
        # Dessin Légende
        if hauteurBarre > 25 :
            dc.SetTextForeground(couleurFontIntitule)
            font = self.GetFont()
            font.SetPointSize(tailleFontIntitule)
            dc.SetFont(font)

            global modeTexte
            if modeTexte == 1 :
                yIntitule = y + 2
                largTexte, hautTexte = self.GetTextExtent(texteDebut)
                xIntitule = posG + 3 + largTexte + 5 
            else:
                xIntitule = posG + 3
                yIntitule = y + 13
            intitule2 = self.AdapteTexteIntitule(dc, intitule, posD - posG-4)
            dc.DrawText(intitule2, xIntitule, yIntitule)
        
        # Petit dessin dans le coin gauche supérieure pour signaler une légende existante
        if intitule != "" :
            dc.SetBrush(wx.Brush((255, 0, 0)))
            dc.SetPen(wx.Pen((0, 0, 0), 1))
            dc.DrawPolygon([(posG, y), (posG+5, y), (posG, y+5)])
                
        if mode =="screen":    
            # Traitement pour le PseudoDC
            r = wx.Rect(posG, y, posD-posG, h)
            dc.SetIdBounds(IDobjet,r) 
            # Mémorisation dans le dict de IDs
            self.dictIDs[IDobjet] = ("tache", IDpresence)
    
    def Impression(self):
        print("lancement de l'impression...")
        
        if len(self.listePresences) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune présence à imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Met à jour les données du planning à partir du panel présences
        self.GetGrandParent().GetParent().MAJpanelPlanning()
        
        # Demande le type d'impression à l'utilisateur
        from Dlg import DLG_Selection_type_document
        listeBoutons = [
            (Chemins.GetStaticPath("Images/BoutonsImages/Imprimer_presences_texteB.png"), _(u"Cliquez ici pour imprimer au format texte")),
            (Chemins.GetStaticPath("Images/BoutonsImages/Imprimer_presences_graph1B.png"), _(u"Cliquez ici pour imprimer sous forme graphique au format portrait")),
            (Chemins.GetStaticPath("Images/BoutonsImages/Imprimer_presences_graph2B.png"), _(u"Cliquez ici pour imprimer sous forme graphique au format paysage")),
            ]
        dlg = DLG_Selection_type_document.Dialog(self, size=(650, 335), listeBoutons=listeBoutons, type="presences")
        if dlg.ShowModal() == wx.ID_OK:
            ChoixType = dlg.GetChoix()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        
        if ChoixType == 1 :
            # Type texte
            impress = ImpressionPDFvTexte(self.dictCategories, self.dictGroupes, self.dictLignes, self.listePresences, self.dictPresences, self.maxWidth ,self.maxHeight)
        if ChoixType == 2 :
            # Type Graph Portrait
            impress = ImpressionPDFvGraph("portrait", self.dictCategories, self.dictGroupes, self.dictLignes, self.listePresences, self.dictPresences, self.maxWidth ,self.maxHeight)
        if ChoixType == 3 :
            # Type Graph Paysage
            impress = ImpressionPDFvGraph("paysage", self.dictCategories, self.dictGroupes, self.dictLignes, self.listePresences, self.dictPresences, self.maxWidth ,self.maxHeight)
                                  
    def InitPlanning(self, listePresences, dictCategories, dictGroupes, dictLignes) :
        self.dictCategories = dictCategories
        self.dictGroupes = dictGroupes
        self.dictLignes = dictLignes
        self.listePresences = self.InitListePresences(listePresences)
        
        # Création du dictPresences
        self.dictPresences = {}
        self.dictInfosLignes = {}
        self.dictInfosGroupes = {}
        for item in self.listePresences :
            self.dictPresences[item[0]] = [item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10]]
            # Création du dict des IDprésences par ligne
            keyLigne = (item[1], item[2])
            if keyLigne in self.dictInfosLignes:
                self.dictInfosLignes[keyLigne]["presencesLigne"].append(item[0])
            else:
                self.dictInfosLignes[keyLigne] = { "presencesLigne" : [item[0],] , "IDobjet" : None, "keyGroupe" : None, "IDobjetGroupe" : None }

        # Recherche des keyGroupe de chaque ligne :
        for keyGroupe, valeursGroupe in self.dictGroupes.items() :
            for valeursLigne in valeursGroupe[4] :
                keyLigne = (valeursLigne[0], valeursLigne[1])
                if keyLigne in self.dictInfosLignes :
                    self.dictInfosLignes[keyLigne]["keyGroupe"] = keyGroupe
        
        
    def OnSize(self, event):
        w  = self.GetSize()[0] - 20
        self.SetSizeDC(w=w)
        self.MAJAffichage()
        event.Skip()
    
    def SetSizeDC(self, w=None, h=None):
        if w != None : self.maxWidth = w
        if h != None : self.maxHeight  = h
        self.SetVirtualSize((self.maxWidth ,self.maxHeight))

    def InitListePresences(self, listePresences):
        """ Crée une liste des présences avec leurs coordonnées X """
        global heureMin, heureMax
        newListe = []
        for item in listePresences :
            # Création de la liste initiale
            date = StrEnDatetimeDate(item[2])
            heureDebut = StrEnDatetime(item[3])
            heureFin = StrEnDatetime(item[4])
            posG = HeuresEnCoords(heureDebut)   
            posD = HeuresEnCoords(heureFin)
            posH = self.dictLignes[(item[1], date)][1]
            posB = posH + hauteurBarre
            valeur = [item[0], item[1], date, heureDebut, heureFin, item[5], item[6], posG, posD, posH, posB]
            newListe.append(valeur)

            # Ajuste les graduations en fonction des horaires donnés
            if heureDebut < heureMin : heureMin = datetime.time(heureDebut.hour, 00)
            if heureFin > heureMax : heureMax = heureFin
        
        return newListe

    
##    def draw(self, dc):
##        dc.SetBackground(wx.Brush(couleurBackground))
##        dc.Clear()
##
##        # Création du planning
##        try: test = len(self.listePresences)
##        except : return
##        
##        self.DrawPlanning(dc)


##    def MAJListePresences(self):
##        """ MAJ des coordonnées de toute la liste des présences """
##        index = 0
##
##        for item in self.listePresences :
##            posG = HeuresEnCoords(item[3]) 
##            posD = HeuresEnCoords(item[4])
##            self.listePresences[index][7] = posG
##            self.listePresences[index][8] = posD
##            index += 1     
                    
                    
##    def DrawPlanning(self, dc):
##        """ Dessine la totalité du planning """
##        chrono1 = time.clock()
##        self.MAJListePresences()
##
##        tailleDC = self.GetSizeTuple()
##
##        # Calcul de la largeur des entetes de lignes et des lignes
##        self.CalcLargeurEnteteLigne(dc)
##        self.CalcCoordLignes(tailleDC)
##        self.parent.DCgraduations.update()
##
##        # Dessin des groupes
##        self.DrawGroupes(dc, tailleDC)
##
##        index = 0
##        # Dessin des présences
##        for item in self.listePresences :
##            self.listePresences[index][7]  = HeuresEnCoords(item[3]) 
##            self.listePresences[index][8] = HeuresEnCoords(item[4])
##            self.DrawBarre(dc,item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10])
##            index += 1
##                
##        chrono2 = time.clock()
##        #print "index=", index, "chrono=", chrono2 - chrono1

    
    def DrawGroupes(self, dc, tailleDC, mode="screen"):
        """ Dessine les groupes """
        self.dictInfosGroupes = {}

        # Dessin des groupes
        dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial'))
        for key, valeurs in self.dictGroupes.items() :
            self.dictInfosGroupes[key] = {}
            if mode == "screen" :
                IDobjet = wx.NewId()
                dc.SetId(IDobjet)
        
            # Détermine la couleur de fond du groupe
            couleurFond = couleurFondGroupe

            # Dessine le groupe
            dc.SetPen(wx.Pen(couleurBordGroupe, 1))
            posH, posB = valeurs[1], valeurs[2]
                
            texte = valeurs[0]
            posY = posH 
            hauteurGroupe = posB 
            # Cadre du groupe
            dc.SetBrush(wx.Brush(couleurFond))
            dc.DrawRoundedRectangle(10, posY+8-1, tailleDC[0]-20, hauteurGroupe-posY-1, 5)
            # Titre du groupe
            dc.SetBrush(wx.Brush(couleurBarreTitreGroupe))
            dc.DrawRoundedRectangle(10, posY, tailleDC[0]-20, 17, 5)
            dc.SetPen(wx.Pen(couleurLineGroupe, 2))
            dc.DrawLine(10, posY + 16, tailleDC[0]-11, posY + 16)
            dc.SetTextForeground(couleurTxtGroupe)
            dc.DrawText(texte, 40, posY+1)

        # Dessin des lignes
        listeTexteEntetes = []
        largeurEntetes = 0
        
        for key, valeurs in self.dictLignes.items() :
            if mode == "screen" :
                IDobjet = wx.NewId()
                dc.SetId(IDobjet)
        
            dc.SetBrush(wx.Brush((230, 230, 230)))
            dc.SetPen(wx.Pen((230, 230, 230), 1))
            dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
            posY = valeurs[1] 
            posX = largeurEnteteLigne+30
            largeur = tailleDC[0]-50-largeurEnteteLigne
            if afficher_temps_ligne == True :
                largeur = largeur - largeurFinLigne
            hauteur = hauteurBarre
            # Définit la brush de la ligne
            if key in selectionsLignes : 
                couleurLigneTmp = couleurLigneSelect
            else:
                couleurLigneTmp = couleurFondSem
                # Recherche de quelle couleur doit être la ligne
                texteDate = key[1]
                # Si c'est un jour de vacances
                if texteDate in self.joursVacances:
                    couleurLigneTmp = couleurVacances
                # Si c'est un jour de Week-end
                jourSemaine = texteDate.isoweekday()
                if jourSemaine == 6 or jourSemaine == 7: 
                    couleurLigneTmp = couleurFondWE
                # Si c'est un jour férié
                if (texteDate.day, texteDate.month) in self.listeFeriesFixes :
                    couleurLigneTmp = couleurFeries
                else:
                    if texteDate in self.listeFeriesVariables :
                        couleurLigneTmp = couleurFeries
                        
            # Dessin de la ligne
            dc.SetBrush(wx.Brush(couleurLigneTmp))
            dc.DrawRectangle(posX, posY, largeur, hauteur)
            
            # Rayures si hors contrat
            if afficher_contrats == True :
                IDpersonne = key[0]
                if IDpersonne in self.dictContrats :
                    listeContrats = self.dictContrats[IDpersonne]
                    contrat = False
                    for IDcontrat, date_debut, date_fin in listeContrats :
                        texteDate = key[1]
                        if date_debut <= str(texteDate) <= date_fin : 
                            contrat = True
                    if contrat == False :
                        dc.SetBrush(wx.Brush( (200, 200, 200) , wx.BDIAGONAL_HATCH))
                        dc.DrawRectangle(posX, posY, largeur, hauteur)

            # Création du texte d'entete de ligne
            texteLigne = valeurs[2]
            largeurTexte, hauteurTexte = self.GetTextExtent(texteLigne)
            posYTxt = (hauteurBarre/2) - (hauteurTexte/2) + posY
            posXTxt = largeurEnteteLigne - largeurTexte + 20 # 20 est la taille du bord gauche du DC
            dc.SetTextForeground(couleurTxtLigne)
            if key in selectionsLignes : dc.SetTextForeground(couleurTxtLigneSelect)
            dc.DrawText(texteLigne, posXTxt, posYTxt)
            
            # Dessin du label temps total de la ligne
            if afficher_temps_ligne == True :
                self.DessineLabelTempsLigne(dc, IDobjet=None, keyLigne=key)
            
        # Dessin du label temps total de chaque groupe
        if afficher_temps_groupe == True :
            for keyGroupe, valeurs in self.dictGroupes.items() :
                self.DessineLabelTempsGroupe(dc, IDobjet=None, keyGroupe=keyGroupe)

                
    
    def DessineLabelTempsLigne(self, dc, keyLigne, IDobjet=None, refresh=False, mode="screen"):
        if keyLigne in self.dictInfosLignes :
            dureeMinutes = 0
            for IDpresence in self.dictInfosLignes[keyLigne]["presencesLigne"] :
                valeurs = self.dictPresences[IDpresence]
                HMin = datetime.timedelta(hours=valeurs[3].hour, minutes=valeurs[3].minute)
                HMax = datetime.timedelta(hours=valeurs[4].hour, minutes=valeurs[4].minute)
                duree = ((HMax - HMin).seconds)//60
                dureeMinutes += duree
                
                nbreHeures = dureeMinutes//60
                nbreMinutes = dureeMinutes-(nbreHeures*60)
                if len(str(nbreMinutes))==1 : nbreMinutes = str("0") + str(nbreMinutes)
                dureeTotale = str(nbreHeures) + "h" + str(nbreMinutes)
            
            labelTempsLigne = dureeTotale
            if 'phoenix' in wx.PlatformInfo:
                largeurDC = self.GetSize()[0]-20
            else:
                largeurDC = self.GetSizeTuple()[0]-20
            posX = largeurDC-50
            posY = self.dictLignes[keyLigne][1]
            largeurTexte, hauteurTexte = self.GetTextExtent(labelTempsLigne)
            posY = (hauteurBarre/2) - (hauteurTexte/2) + posY
            
            if mode =="screen":
                if IDobjet == None : 
                    IDobjet = wx.NewId()
                else:
                    dc.ClearId(IDobjet)
                dc.SetId(IDobjet)
                self.dictInfosLignes[keyLigne]["IDobjet"] = IDobjet
            
            dc.SetTextForeground(couleurTxtLigne)
            dc.SetFont(wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
            self.pdc.DrawText(labelTempsLigne, posX, posY)
            
            # Mémorisation dans le dict de IDs
            if mode =="screen": 
                r = (posX, posY, 30, 15)
                dc.SetIdBounds(IDobjet, r) 
                self.dictIDs[IDobjet] = ("tempsLigne", keyLigne)
            
            # MAJ de l'affichage
            if refresh == True :
                posXtmp, posY = self.ConvertCoords(posX, posY)
                r = (posX, posY, 30, 15)
                self.RefreshRect(r, False)

    def DessineLabelTempsGroupe(self, dc, keyGroupe, IDobjet=None, refresh=False, mode="screen"):
        # Calcul du temps total du groupe
        dureeMinutes = 0
        for ligne in self.dictGroupes[keyGroupe][4] :
            keyLigne = (ligne[0], ligne[1])
            if keyLigne in self.dictInfosLignes :
                for IDpresence in self.dictInfosLignes[keyLigne]["presencesLigne"] :
                    valeurs = self.dictPresences[IDpresence]
                    HMin = datetime.timedelta(hours=valeurs[3].hour, minutes=valeurs[3].minute)
                    HMax = datetime.timedelta(hours=valeurs[4].hour, minutes=valeurs[4].minute)
                    duree = ((HMax - HMin).seconds)//60
                    dureeMinutes += duree
                    
        nbreHeures = dureeMinutes//60
        nbreMinutes = dureeMinutes-(nbreHeures*60)
        if len(str(nbreMinutes))==1 : nbreMinutes = str("0") + str(nbreMinutes)
        dureeTotale = str(nbreHeures) + "h" + str(nbreMinutes)
        
        labelTempsGroupe = dureeTotale
        if 'phoenix' in wx.PlatformInfo:
            largeurDC = self.GetSize()[0]-20
        else:
            largeurDC = self.GetSizeTuple()[0]-20
        posX = largeurDC-50
        posY = self.dictGroupes[keyGroupe][1] + 3
        
        if mode =="screen":
            if IDobjet == None : 
                IDobjet = wx.NewId()
            else:
                dc.ClearId(IDobjet)
            dc.SetId(IDobjet)
            self.dictInfosGroupes[keyGroupe]["IDobjetTempsGroupe"] = IDobjet

        dc.SetTextForeground(couleurFondGroupe)
        dc.SetFont(wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))        
        self.pdc.DrawText(labelTempsGroupe, posX, posY)
        
        # Mémorisation dans le dict de IDs
        if mode =="screen": 
            r = (posX, posY, 30, 15)
            dc.SetIdBounds(IDobjet, r) 
            self.dictIDs[IDobjet] = ("tempsGroupe", keyGroupe)
        
        # MAJ de l'affichage
        if refresh == True :
            posXtmp, posY = self.ConvertCoords(posX, posY)
            r = (posX, posY, 30, 15)
            self.RefreshRect(r, False)

    def DessineNbrePresents(self, dc, keyGroupe, IDobjet=None, refresh=False, mode="screen"):
        # Calcul du nbre de présents durant la journée
        listeBarres = []
        listePositions = []
        for ligne in self.dictGroupes[keyGroupe][4] :
            keyLigne = (ligne[0], ligne[1])
            if keyLigne in self.dictInfosLignes :
                for IDpresence in self.dictInfosLignes[keyLigne]["presencesLigne"] :
                    valeurs = self.dictPresences[IDpresence]
                    posG = valeurs[7] 
                    posD = valeurs[8]
                    listeBarres.append( (posG, posD) )
                    if [posG, 0] not in listePositions : listePositions.append( [posG, 0] )
                    if [posD, 0] not in listePositions : listePositions.append( [posD, 0] )
                    
        if len(listeBarres) == 0 : return        
        
        # Traitement de la liste pour trouver les nbre de présents par tranche horaire
        listePositions.sort()
        for posG, posD in listeBarres :
            index = 0
            for position, nbre in listePositions :
                if position >= posG and position < posD:
                    listePositions[index][1] += 1
                index += 1
        
        posYTitreGroupe = self.dictGroupes[keyGroupe][1] + 4
        posY = posYTitreGroupe + hauteurTitreGroupe - 10
        
        if mode =="screen":
            if IDobjet == None : 
                IDobjet = wx.NewId()
            else:
                dc.ClearId(IDobjet)
            dc.SetId(IDobjet)
            self.dictInfosGroupes[keyGroupe]["IDobjetNbrePresents"] = IDobjet
            self.dictIDs[IDobjet] = ("barreNbrePresents", keyGroupe)
        
        couleur = couleurBordGroupe
        dc.SetTextForeground(couleur)
        dc.SetFont(wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))        
        
        index = 0
        for position, nbre in listePositions :
            dc.SetPen(wx.Pen(couleur, 1))
            dc.DrawLine(position, posY-2, position, posY+3) # Ligne verticale
            if index < len(listePositions)-1 and nbre > 0 :
                positionSuivante = listePositions[index+1][0]
                dc.DrawLine(position, posY, positionSuivante, posY) # Ligne horizontale
                texte = str(nbre)
                largTexte, hautTexte = self.GetTextExtent(texte)
                positionTexte = ((position + positionSuivante) / 2.0 ) - (largTexte/2.0)+1
                dc.SetPen(wx.Pen(couleurFondGroupe, 0))
                dc.SetBrush(wx.Brush(couleurFondGroupe))
                dc.DrawRectangle(positionTexte-1, posY-5, largTexte+1, hautTexte-2)
                self.pdc.DrawText(texte, positionTexte, posY-6)
            index += 1
        
        premierePosition = listePositions[0][0]
        dernierePosition = listePositions[-1][0]
        
        # Mémorisation dans le dict de IDs
        if mode =="screen": 
            r = (premierePosition, posY-7, dernierePosition-premierePosition+5, 15)
            dc.SetIdBounds(IDobjet, r) 
            self.dictIDs[IDobjet] = ("nbrePresents", keyGroupe)
                
        # MAJ de l'affichage
        if refresh == True :
            tmp, posY = self.ConvertCoords(premierePosition, posY)
            if 'phoenix' in wx.PlatformInfo:
                largeurDC = self.GetSize()[0]
            else:
                largeurDC = self.GetSizeTuple()[0]
            r = (0, posY-7, largeurDC, 15)
            self.RefreshRect(r, False)
            

    def OnLeftDown(self, event):
##        x, y = event.GetPosition()
##        print x, y
        x,y = self.ConvertEventCoords(event)

        # Recherche la barre correspondant aux points x, y
        listeObjets = self.pdc.FindObjectsByBBox(x, y)
        IDpresence = 0
        if len(listeObjets) != 0 :
            IDobjet = listeObjets[0]
            if self.dictIDs[IDobjet][0] == "tache" :
                IDpresence = self.dictIDs[IDobjet][1]
                self.selectBarre = self.HitTestBarre(x, IDpresence, IDobjet)
                self.selectLigne = self.HitTestLigne(x, y)
                # Recherche des contraintes de la barre sélectionnée
                index = self.selectBarre[1]
                self.contraintes = self.ContraintesBarre(IDpresence)
                # Change la forme du curseur
                self.SetCurseur(self.selectBarre)
                # Texte dans statusBar
                self.CreateTexteStatusBar()
                event.Skip()
                return
        
        # Recherche si titre de groupe touché :
        resultat = self.HitTestTitreGroupe(x, y)
        if resultat == True : event.Skip() ; return
        
        # Recherche si entete de ligne touché :
        self.HitTestEnteteLigne(x, y)
        event.Skip()

    def HitTestBarre(self, x, IDpresence, IDobjet):
        """ Recherche la barre cliquée """
        # Récupère les caractéristiques de la barre
        barre = self.dictPresences[IDpresence]
        posG = barre[7]
        posD = barre[8]
        posH = barre[9]
        posB = barre[10]

        # Recherche la position cliquée dans la barre
        tailleBarre = posD - posG
        tailleRegion = tailleBarre /4
        regionGauche = posG + tailleRegion
        regionMilieu = posG + (tailleRegion*3)
        if x <= regionGauche :
            region = "gauche"
        elif x <= regionMilieu :
            region = "milieu"
        else:
            region = "droite"
        
        return IDpresence, region, IDobjet
       
    def HitTestEnteteLigne(self, x, y) :
        global selectionsLignes
        if (20 <= x <= (largeurEnteteLigne + 20)) :
            for key, valeurs in self.dictLignes.items() :
                posY = valeurs[1] + varScroll
                if ((posY+hauteurBarre) >= y >= posY) :
                    if key not in selectionsLignes :
                        selectionsLignes.append(key)
                    else:
                        selectionsLignes.remove(key)
                    self.MAJAffichage()

    def HitTestLigne(self, x, y) :
        """ Est utilise pour le menu contextuel """
        if (coordLigne[0] <= x <= coordLigne[1]) :            
            for key, valeurs in self.dictLignes.items() :
                posY = valeurs[1]
                if ((posY+hauteurBarre) >= y >= posY) :
                    return key
                    break
        return None
    
    def HitTestTitreGroupe(self, x, y) :
        """ Pour sélectionner toutes les lignes d'un groupe """
        # Recherche d'un titre de groupe
        if 'phoenix' in wx.PlatformInfo:
            val = self.GetSize()[0]-30
        else:
            val = self.GetSizeTuple()[0]-30
        if (10<= x <= val) :
            for key, valeurs in self.dictGroupes.items() :
                posYH = valeurs[1]
                posYB = posYH + 16
                if (posYH <= y <= posYB) :
                    global selectionsLignes
                    for IDpersonne, date, a, b in self.dictGroupes[key][4] :
                        ligne = (IDpersonne, date)
                        if ligne not in selectionsLignes :
                            selectionsLignes.append(ligne)
                        else:
                            selectionsLignes.remove(ligne)
                    self.MAJAffichage()
                    return True
        return False
                            
    def SelectAllLignes(self):
        global selectionsLignes
        for key, valeurs in self.dictLignes.items() :                
            if key not in selectionsLignes :
                selectionsLignes.append(key)
        self.MAJAffichage()
        
    def DeselectAllLignes(self):
        global selectionsLignes
        selectionsLignes = []
        self.MAJAffichage()        
        
    def OnDLeftDown(self, event):
        """ Double-click bouton gauche -> ajout d'une présence """
        x,y = self.ConvertEventCoords(event)

        # Recherche d'une barre
        listeObjets = self.pdc.FindObjectsByBBox(x, y)
        IDpresence = 0
        if len(listeObjets) != 0 :
            IDobjet = listeObjets[0]
            if self.dictIDs[IDobjet][0] == "tache" :
                IDpresence = self.dictIDs[IDobjet][1]
                self.selectBarre = self.HitTestBarre(x, IDpresence, IDobjet)
                self.Modifier(self.selectBarre[0])
                event.Skip()
                return
            
        # Recherche d'une ligne
        for key, valeurs in self.dictLignes.items() :
            posYH = valeurs[1] + varScroll
            posXG = coordLigne[0]
            posXD = coordLigne[1]
            posYB = hauteurBarre + posYH
            if (posYH <= y <= posYB) and (posXG <= x <= posXD) :
                #texte = str(key) + "-" + str(valeurs)
                self.Ajouter([(key[0], key[1])])
                return
            
        event.Skip()

    def OnLeftUp(self, event):
        if self.selectModif == True :
            ID = self.SauvegardeModif()
            # MAJ du listCtrl des durées par catégorie
            self.MAJ_listCtrl_Categories()
        self.selectModif = False
        self.selectBarre = None
        self.selectLigne = None
        self.contraintes = None
        self.selectEcart = None
        self.SetCurseur(None)
        try : wx.GetApp().GetTopWindow().SetStatusText("",0)
        except : pass
        event.Skip()

    def MAJ_listCtrl_Categories(self):
        """ Calcule les temps dans le dictCategories """
        for key, valeurs in self.dictCategories.items() :
            self.dictCategories[key][4] = 0
        for key, valeurs in self.dictPresences.items() :
            HMin = datetime.timedelta(hours=valeurs[3].hour, minutes=valeurs[3].minute)
            HMax = datetime.timedelta(hours=valeurs[4].hour, minutes=valeurs[4].minute)
            duree = ((HMax - HMin).seconds)//60
            self.dictCategories[valeurs[5]][4] += duree
            
        self.GetParent().GetGrandParent().panelLegendes.listCtrlLegendes.MAJ()
        
    def SetCurseur(self, varSelectBarre):
        """ Change la forme du curseur lors d'un dragging """
        if varSelectBarre == None:
            self.SetCursor(CURSOR(wx.CURSOR_ARROW))
            return
        if varSelectBarre[1] == "gauche" or varSelectBarre[1] == "droite" :
            self.SetCursor(CURSOR(wx.CURSOR_SIZEWE))
        elif varSelectBarre[1] == "milieu":
            self.SetCursor(CURSOR(wx.CURSOR_SIZING))

    def OnLeaveWindow(self, event):
        self.SetCurseur(None)
        self.selectBarre = None
        self.selectLigne = None
        self.CreateTexteStatusBar()
        try : wx.GetApp().GetTopWindow().SetStatusText("", 1)
        except : pass
        event.Skip()
 
    def CreateTexteStatusBar(self):
        """ Ecrit du texte dans la barre de status de la fenêtre parente """
        if self.selectBarre != None :
            IDpresence = self.selectBarre[0]
            # Calcul de la durée
            valeurs = self.dictPresences[IDpresence]
            HMin = datetime.timedelta(hours=valeurs[3].hour, minutes=valeurs[3].minute)
            HMax = datetime.timedelta(hours=valeurs[4].hour, minutes=valeurs[4].minute)
            dureeMinutes = ((HMax - HMin).seconds)//60
            nbreHeures = dureeMinutes//60
            nbreMinutes = dureeMinutes-(nbreHeures*60)
            if len(str(nbreMinutes))==1 : nbreMinutes = str("0") + str(nbreMinutes)
            dureeStr = str(nbreHeures) + "h" + str(nbreMinutes)
            heure_debut = six.text_type(self.dictPresences[IDpresence][3])[:5]
            heure_fin = six.text_type(self.dictPresences[IDpresence][4])[:5]
            IDcategorie = self.dictPresences[IDpresence][5]
            categorieStr = self.dictCategories[IDcategorie][0]
            intitule = six.text_type(self.dictPresences[IDpresence][6])
            if intitule != "" : categorieStr = u"%s | %s" % (categorieStr, intitule)
            texteStatusBar = u"%s-%s (%s) : %s" % (heure_debut, heure_fin, dureeStr, categorieStr)
        else:
            texteStatusBar = ""
        try : 
            wx.GetApp().GetTopWindow().SetStatusText(texteStatusBar, 0)
            txtAide = _(u"Accédez aux fonctions de gestion des tâches en cliquant sur le bouton droit de votre souris")
            wx.GetApp().GetTopWindow().SetStatusText(txtAide, 1)
        except : pass
        
               
    def OnMotion(self, event):
        """ Dragging des barres """
##        self.SetFocus()
        x, y = event.GetPosition()
        if event.Dragging() and event.LeftIsDown() and self.selectBarre != None:
            # Déplacement de la barre
            self.MoveBarre(x)
            self.selectModif = True
            # Texte dans StatusBar
            self.CreateTexteStatusBar()
            # MAJ du DC
            self.RedrawBarre()
            # MAJ du label temps en fin de ligne
            keyLigne=self.selectLigne
            keyGroupe = self.dictInfosLignes[keyLigne]["keyGroupe"]
            if afficher_temps_ligne == True :
                self.DessineLabelTempsLigne(self.pdc, keyLigne, IDobjet=self.dictInfosLignes[keyLigne]["IDobjet"], refresh=True)
            # MAJ du label temps en fin de entete de groupe
            if afficher_temps_groupe == True :
                self.DessineLabelTempsGroupe(self.pdc, keyGroupe, IDobjet=self.dictInfosGroupes[keyGroupe]["IDobjetTempsGroupe"], refresh=True)
            # MAJ de la barre du nbre de présents
            if afficher_nbre_presents == True :
                self.DessineNbrePresents(self.pdc, keyGroupe, IDobjet=self.dictInfosGroupes[keyGroupe]["IDobjetNbrePresents"], refresh=True)
            event.Skip()
        elif event.LeftIsDown()==False:
            """ Affiche dans la statusBar de la barre survolée """
            x,y = self.ConvertEventCoords(event)
            listeObjets = self.pdc.FindObjectsByBBox(x, y)
            if len(listeObjets) != 0 :
                IDobjet = listeObjets[0]
                if IDobjet in self.dictIDs :
                    if self.dictIDs[IDobjet][0] == "tache" :
                        IDpresence = self.dictIDs[IDobjet][1]
                        selectTemp = self.HitTestBarre(x, IDpresence, IDobjet)
                        if selectTemp == self.selectBarre : return
                        self.selectBarre = selectTemp
                        self.CreateTexteStatusBar()
            else:
                if self.selectBarre != None :
                    self.selectBarre = None
                    self.selectLigne = None
                    self.CreateTexteStatusBar()
        else:
            self.selectBarre = None
            self.selectLigne = None
            
        event.Skip()

    def RedrawBarre(self):
        IDpresence, region, IDobjet = self.selectBarre
        valeurs = self.dictPresences[IDpresence]
        dc = self.pdc
        r1 = dc.GetIdBounds(IDobjet) 
        # Efface l'id de la liste des objets du pseudoDC
        dc.ClearId(IDobjet)
        # Redessine la barre
        self.DrawBarre(dc, IDpresence, valeurs[3], valeurs[4], valeurs[5], valeurs[6], valeurs[7], valeurs[8], valeurs[9], valeurs[10], IDobjet)
        r2 = dc.GetIdBounds(IDobjet)
        # Redessine uniquement la zone modifiée
        r = r1.Union(r2)
        self.OffsetRect(r)
        self.RefreshRect(r, False)

    def MoveBarre(self, x):
        """ Fonction de déplacement d'une barre """
        IDpresence = self.selectBarre[0]
        region = self.selectBarre[1]

        # Attribution des nouvelles valeurs
        if region == "droite" :
            if self.selectEcart == None :
                self.selectEcart = x - self.dictPresences[IDpresence][8]
            heureD = AroundHeure(CoordEnHeures(x-self.selectEcart))
            coord = HeuresEnCoords(heureD)
            if heureD < self.contraintes[2] or heureD > self.contraintes[3] :
                xMouse = self.dictPresences[IDpresence][8]+self.selectEcart+1
                yMouse = self.ScreenToClientXY(xMouse, wx.GetMousePosition()[1])[1]
                self.WarpPointer(xMouse, yMouse)
                return            
            self.dictPresences[IDpresence][4] = heureD
            self.dictPresences[IDpresence][8] = coord

        if region == "gauche" :
            if self.selectEcart == None :
                self.selectEcart = x - self.dictPresences[IDpresence][7]
            heureG = AroundHeure(CoordEnHeures(x-self.selectEcart))
            coord = HeuresEnCoords(heureG)
            if heureG < self.contraintes[0] or heureG > self.contraintes[1] : 
                xMouse = self.dictPresences[IDpresence][7]+self.selectEcart+1
                yMouse = self.ScreenToClientXY(xMouse, wx.GetMousePosition()[1])[1]
                self.WarpPointer(xMouse, yMouse)
                return
            self.dictPresences[IDpresence][3] = heureG
            self.dictPresences[IDpresence][7] = coord

        if region == "milieu" :
            if self.selectEcart == None :
                self.selectEcart = (x-self.dictPresences[IDpresence][7], self.dictPresences[IDpresence][8]-x)
            # Calcul de la durée
            heureDbis = self.dictPresences[IDpresence][4] 
            heureGbis = self.dictPresences[IDpresence][3]           
            duree = datetime.datetime(1,1,1, heureDbis.hour, heureDbis.minute, 00) - datetime.datetime(1,1,1, heureGbis.hour, heureGbis.minute, 00) 

            # posG
            heureG = AroundHeure(CoordEnHeures(x-self.selectEcart[0]))
            coordG = HeuresEnCoords(heureG)
            if heureG < self.contraintes[0] :
                xMouse = self.dictPresences[IDpresence][7]+self.selectEcart[0]
                yMouse = self.ScreenToClientXY(xMouse, wx.GetMousePosition()[1])[1]
                self.WarpPointer(xMouse, yMouse)
                return
            # posD
            heureDtmp = datetime.datetime(1,1,1, heureG.hour, heureG.minute, 00) + duree
            heureD = datetime.time(heureDtmp.hour, heureDtmp.minute)
            coordD = HeuresEnCoords(heureD)
            
            # Ancienne méthode
##            heureD = AroundHeure(CoordEnHeures(x+self.selectEcart[1]))
##            coordD = HeuresEnCoords(heureD)
            
            if heureD > self.contraintes[3] : 
                xMouse = self.dictPresences[IDpresence][8]-self.selectEcart[1]+1
                yMouse = self.ScreenToClientXY(xMouse, wx.GetMousePosition()[1])[1]
                self.WarpPointer(xMouse, yMouse)
                return
            # Mémorisation des nouvelles valeurs
            self.dictPresences[IDpresence][3] = heureG
            self.dictPresences[IDpresence][7] = coordG
            self.dictPresences[IDpresence][4] = heureD
            self.dictPresences[IDpresence][8] = coordD

    def ContraintesBarre(self, IDpresence):
        """ Définit les contraintes de déplacement de la barre déplacée quand elle est cliquée pour la 1ere fois"""
        
        # Récupère les caractéristiques de la barre
        IDpersonne = self.dictPresences[IDpresence][1]
        date = self.dictPresences[IDpresence][2]
        heureDebut = self.dictPresences[IDpresence][3]
        heureFin = self.dictPresences[IDpresence][4]
        
        # Création d'une liste des présences du même jour et du même animateur
        listeHeuresDebut = []
        listeHeuresFin = []
        for key, valeurs in self.dictPresences.items() :
            if valeurs[1] == IDpersonne and valeurs[2] == date :
                listeHeuresDebut.append(valeurs[3])
                listeHeuresFin.append(valeurs[4])
        listeHeuresDebut.sort()
        listeHeuresFin.sort()
                
        # Recherche de l'heure Max du coté droit
        heureDMax = heureMax
        for item in listeHeuresDebut :
            if item >= heureFin :
                heureDMax = item
                break  
        # Recherche l'heure minimum du cote droit
        Htemp = datetime.timedelta(hours=heureDebut.hour, minutes=heureDebut.minute)
        tempsMinimum = datetime.timedelta(hours=0, minutes=15) # 15 correspond ici au temps minimum d'une barre -> Changement possible
        newHeure = Htemp + tempsMinimum
        heureDMin = DeltaEnTime(newHeure)
        
        # Recherche de l'heure Min du cote gauche
        heureGMin = heureMin
        for item in listeHeuresFin :
            if item <= heureDebut :
                heureGMin = item
        # Recherche l'heure max du cote gauche
        Htemp = datetime.timedelta(hours=heureFin.hour, minutes=heureFin.minute)
        tempsMinimum = datetime.timedelta(hours=0, minutes=15) # 15 correspond ici au temps minimum d'une barre -> Changement possible
        newHeure = Htemp - tempsMinimum
        heureGMax = DeltaEnTime(newHeure)
        
        return heureGMin, heureGMax, heureDMin, heureDMax
         

    def FormateCouleur(self, texte):
        pos1 = texte.index(",")
        pos2 = texte.index(",", pos1+1)
        r = int(texte[1:pos1])
        v = int(texte[pos1+2:pos2])
        b = int(texte[pos2+2:-1])
        return (r, v, b)

 

    def AdapteTexteHeure(self, dc, texte, tailleBarre):
        """ Raccourcit le texte de l'heure en fonction de la taille donnée """
        if (self.GetTextExtent(texte)[0]*2) < tailleBarre : return texte
        return ""

    def AdapteTexteIntitule(self, dc, texte, tailleMaxi):
        """ Raccourcit le texte de l'intitulé en fonction de la taille donnée """
        # Pas de retouche nécessaire
        if self.GetTextExtent(texte)[0] < tailleMaxi : return texte

        # Renvoie aucun texte si tailleMaxi trop petite
        if tailleMaxi <= self.GetTextExtent("W...")[0] : return ""

        # Retouche nécessaire
        tailleTexte = self.GetTextExtent(texte)[0]
        texteTemp = ""
        texteTemp2 = ""
        for lettre in texte :
            texteTemp += lettre
            if self.GetTextExtent(texteTemp +"...")[0] < tailleMaxi :
               texteTemp2 = texteTemp 
            else:
                return texteTemp2 + "..."     
        


    def CalcCoordLignes(self, tailleDC):
        global coordLigne
        xG = largeurEnteteLigne+30
        xD = tailleDC[0]-50-largeurEnteteLigne + xG 
        if afficher_temps_ligne == True :
            xD = xD - largeurFinLigne
        coordLigne = (xG, xD)

    def CalcLargeurEnteteLigne(self, dc):
        """ Calcule la largeur en pixel du texte des entetes de lignes """
        global largeurEnteteLigne
        dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))

        largeurTemp = 0
        for key, valeurs in self.dictLignes.items():
            largeur, hauteur = self.GetTextExtent(valeurs[2])
            if largeur > largeurTemp : largeurTemp = largeur
        largeurEnteteLigne = largeurTemp            



    def SauvegardeModif(self):
        """ Sauvegarde des données modifiées dans la base de données """
        if self.selectBarre == None : return
        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        # Création de la liste des données
        IDpresence = self.selectBarre[0]
        item = self.dictPresences[IDpresence]
        listeDonnees = [    ("heure_debut",     str(item[3])[:5]),
                            ("heure_fin",       str(item[4])[:5]),
                            ("IDcategorie",     item[5]),
                            ("intitule",        item[6]),
                        ]
        # Modification de la présence
        DB.ReqMAJ("presences", listeDonnees, "IDpresence", IDpresence)
        DB.Commit()
        DB.Close()
        return item[0]

    def SauvegardeNouveau(self):
        """ Sauvegarde des données dans la base de données """

        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        # Création de la liste des données
        item = self.selectBarre
        listeDonnees = [    ("IDpersonne",      item[1]),
                            ("date",            item[2]),
                            ("heure_debut",     item[3]),
                            ("heure_fin",       item[4]),
                            ("IDcategorie",     item[5]),
                            ("intitule",        item[6]),
                        ]
        # Enregistrement d'une nouvelle présence
        ID = DB.ReqInsert("presences", listeDonnees)
        DB.Commit()
        DB.Close()
        return ID

    def Ajouter(self, selection):
        """ Ajouter une présence avec le form de saisie des présences """
        dlg = DLG_Saisie_presence.Dialog(None, selection, panelPlanning=self)
        dlg.ShowModal()
        dlg.Destroy()


    def Modifier(self, IDpresence):
        """ Modifier une présence avec le form de saisie des présences """
        dlg = DLG_Saisie_presence.Dialog(None, IDmodif=IDpresence, panelPlanning=self)
        dlg.ShowModal()
        dlg.Destroy()

    def Supprimer(self, IDpresence, txt):
        """ Supprimer une tâche """
        dlg = wx.MessageDialog(self, txt,  _(u"Suppression d'une tâche"), wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
        if dlg.ShowModal() == wx.ID_NO :
            print("suppression annulee")
            dlg.Destroy() 
            return
        dlg.Destroy()
        # Suppression du type de pièce
        DB = GestionDB.DB()
        DB.ReqDEL("presences", "IDpresence", IDpresence)
        DB.Close()
        self.MAJafterModif()

    def OnContextMenu(self, event):
        x,y = self.ConvertEventCoords(event)
        
        if len(self.dictLignes) == 0 : return
        
        self.Context = None
        self.ligne = None
        index = None
        
        # Recherche la ligne correspondant aux points x, y
        self.ligne = self.HitTestLigne(x, y)
        if self.ligne != None :            
            # Recherche la barre correspondant aux points x, y
            listeObjets = self.pdc.FindObjectsByBBox(x, y)
            IDpresence = 0
            if len(listeObjets) != 0 :
                IDobjet = listeObjets[0]
                if self.dictIDs[IDobjet][0] == "tache" :
                    IDpresence = self.dictIDs[IDobjet][1]
                    self.Context = self.HitTestBarre(x, IDpresence, IDobjet)
                
            if self.Context == None :
                IDpresence = None
                self.Context = x
            else:
                IDpresence = self.Context[0]
            
        menu = UTILS_Adaptations.Menu()
        
        if self.ligne != None :
            if IDpresence == None  : 
                
                # Menu Ajouter
                self.popupID1 = wx.NewId()
                self.Bind(wx.EVT_MENU, self.OnMenuAjouter, id=self.popupID1)
                menu.Append(self.popupID1, _(u"Enregistrer une tâche unique ici"))
                #menu.Enable(self.popupID1, False)
            
            else:

                # Menu Modifier
                self.popupID1 = wx.NewId()
                self.Bind(wx.EVT_MENU, self.OnMenuModifier, id=self.popupID1)
                menu.Append(self.popupID1, _(u"Modifier"))

                # Menu Supprimer
                self.popupID2 = wx.NewId()
                self.Bind(wx.EVT_MENU, self.OnMenuSupprimer, id=self.popupID2)
                menu.Append(self.popupID2, _(u"Supprimer"))

                # Menu Modifier la légende
                if self.dictPresences[IDpresence][6] == "" :
                    texte3 = _(u"Ajouter une légende")
                else:
                    texte3 = _(u"Modifier la légende")
                self.popupID3 = wx.NewId()
                self.Bind(wx.EVT_MENU, self.OnMenuModifLegende, id=self.popupID3)
                menu.Append(self.popupID3, texte3)
           
                # Création du sous-menu Catégories
                self.SousMenuCategories(0, menu, _(u"Changer de catégorie"), None)
                
            menu.AppendSeparator()
            
        # Gestion des saisie de présences et des sélections
        if len(selectionsLignes) != 0 :
            
            # Menu Saisir une tâche pour les lignes sélectionnées
            self.popupIDSaisie = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnMenuSaisie, id=self.popupIDSaisie)
            if len(selectionsLignes) == 1:
                txt = _(u"Enregistrer une tâche pour la ligne sélectionnée")
            else:
                txt = _(u"Enregistrer une tâche pour les ") + str(len(selectionsLignes)) + _(u" lignes sélectionnées")
            menu.Append(self.popupIDSaisie, txt)
            
            # Menu Supprimer toutes les tâches des des lignes sélectionnées
            self.popupIDSupprimerAll = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnMenuSupprimerLignes, id=self.popupIDSupprimerAll)
            if len(selectionsLignes) == 1:
                txt = _(u"Supprimer toutes les tâches de la ligne sélectionnée")
            else:
                txt = _(u"Supprimer toutes les tâches des ") + str(len(selectionsLignes)) + _(u" lignes sélectionnées")
            menu.Append(self.popupIDSupprimerAll, txt)
            
            menu.AppendSeparator()
            
            # Menu Appliquer un modèle
            self.popupIDAppliquerModele = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnMenuAppliquerModele, id=self.popupIDAppliquerModele)
            if len(selectionsLignes) == 1:
                txt = _(u"Appliquer un modèle à la ligne sélectionnée")
            else:
                txt = _(u"Appliquer un modèle aux ") + str(len(selectionsLignes)) + _(u" lignes sélectionnées")
            menu.Append(self.popupIDAppliquerModele, txt)
            
            menu.AppendSeparator()
        
        # Menu Tout sélectionner
        self.popupIDSelectAll = wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnMenuSelectAll, id=self.popupIDSelectAll)
        menu.Append(self.popupIDSelectAll, _(u"Sélectionner toutes les lignes"))
            
        # Menu Tout désélectionner
        self.popupIDDeselectAll = wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnMenuDeselectAll, id=self.popupIDDeselectAll)
        menu.Append(self.popupIDDeselectAll, _(u"Désélectionner toutes les lignes"))
        
       
        # Finalisation du menu
        self.PopupMenu(menu)           
        menu.Destroy()
        self.Context = None
        self.ligne = None
        #self.update()

    def OnMenuSaisie(self, event):
        self.SaisiePresences()
        
    def OnMenuSupprimerLignes(self, event):
        self.SupprimerPresencesLignes()
    
    def OnMenuSelectAll(self, event):
        self.SelectAllLignes()
        
    def OnMenuDeselectAll(self, event):
        self.DeselectAllLignes()

    def OnMenuAjouter(self, event):
        dlg = DLG_Saisie_presence.Dialog(None, [self.ligne], panelPlanning=self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnMenuModifier(self, event):
        IDpresence = self.Context[0]
        self.Modifier(IDpresence)
        #event.Skip()

    def OnMenuSupprimer(self, event):
        IDpresence = self.Context[0]
        heureDebut = str(self.dictPresences[IDpresence][3])[:5]
        heureFin = str(self.dictPresences[IDpresence][4])[:5]
        date = DatetimeDateEnStr(self.dictPresences[IDpresence][2])
        txt = _(u"Souhaitez-vous vraiment supprimer la tâche du %s de %s à %s ?") % (date, heureDebut, heureFin)
        self.Supprimer(IDpresence, txt)
        #event.Skip()

    def OnMenuModifLegende(self, event):
        """ Ajouter ou modifier une légende """
        IDpresence = self.Context[0]
        legendeDefaut = self.dictPresences[IDpresence][6]
        heureDebut = str(self.dictPresences[IDpresence][3])[:5]
        heureFin = str(self.dictPresences[IDpresence][4])[:5]
        date = DatetimeDateEnStr(self.dictPresences[IDpresence][2])
        intro = _(u"Saisissez une légende pour la tâche du %s de %s à %s :") % (date, heureDebut, heureFin)

        dlg = wx.TextEntryDialog(self, intro, _(u"Saisie d'une légende"), legendeDefaut)
        if dlg.ShowModal() == wx.ID_OK:
            varLegende = dlg.GetValue()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return

        # Sauvegarde
        listeDonnees = [("intitule",  varLegende),]
        DB = GestionDB.DB()
        # Modification de la présence
        DB.ReqMAJ("presences", listeDonnees, "IDpresence", IDpresence)
        DB.Commit()
        DB.Close()

        # MAJ de l'affichage
        self.dictPresences[IDpresence][6] = varLegende
        self.MAJAffichage()
        
        event.Skip()

    def OnMenuChoixCategorie(self, event):
        IDcategorie = event.GetId()
        IDpresence = self.Context[0]

        # Sauvegarde
        listeDonnees = [("IDcategorie",  IDcategorie),]
        DB = GestionDB.DB()
        # Modification de la présence
        DB.ReqMAJ("presences", listeDonnees, "IDpresence", IDpresence)
        DB.Commit()
        DB.Close()

        # MAJ de l'affichage
        self.dictPresences[IDpresence][5] = IDcategorie
        self.MAJ_listCtrl_Categories()
        self.MAJAffichage()
        

    def OnMenuAppliquerModele(self, event):
        """ Appliquer un modèle aux lignes sélectionnées """
        selectionPersonnes = []
        selectionDates = []
        for ligne in selectionsLignes :
            if ligne[0] not in selectionPersonnes :
                selectionPersonnes.append(ligne[0])
            selectionDates.append(ligne[1])
                
        selectionDates.sort()
        if len(selectionDates) != 0 :
            dateMin = selectionDates[0]
            dateMax = selectionDates[-1]
            selectionDates=(dateMin, dateMax)
        else:
            selectionDates=(None, None)
   
        dlg = DLG_Application_modele.Dialog(self, selectionLignes=selectionsLignes, selectionPersonnes=selectionPersonnes, selectionDates=selectionDates )
        dlg.ShowModal()
        dlg.Destroy()

    def SousMenuCategories(self, IDparent, menu, titre, couleurTitre):
        # make a submenu avec self.dictCategories
        sm = UTILS_Adaptations.Menu()

        if IDparent != 0 :
            index, texte = IDparent,titre
            setattr(self, "popupID%s" % index, index)
            item = wx.MenuItem(menu, getattr(self, "popupID%s" % index), texte)
            couleur = self.FormateCouleur(couleurTitre)
            r, v, b = couleur[0], couleur[1], couleur[2]
            bmp = self.CreationImage((16, 16), r, v, b, index)
            item.SetBitmap(bmp)
            sm.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.OnMenuChoixCategorie, id=getattr(self, "popupID%s" % index))
            sm.AppendSeparator()

        nbre = 0
        for key, valeurs in self.dictCategories.items() :
            if valeurs[1] == IDparent:

                # Recherche s'il y a des sous-menus :
                enfantsExists = False
                for key2, valeurs2 in self.dictCategories.items() :
                    if valeurs2[1] == key : enfantsExists = True

                if enfantsExists == False :
                    # Si pas d'enfants, on crée un item dans le menu
                    nbre += 1
                    index, texte = key, valeurs[0]
                    setattr(self, "popupID%s" % index, index)
                    item = wx.MenuItem(menu, getattr(self, "popupID%s" % index), texte)
                    couleur = self.FormateCouleur(valeurs[3])
                    r, v, b = couleur[0], couleur[1], couleur[2]
                    bmp = self.CreationImage((16, 16), r, v, b, index)
                    item.SetBitmap(bmp)
                    sm.AppendItem(item)
                    self.Bind(wx.EVT_MENU, self.OnMenuChoixCategorie, id=getattr(self, "popupID%s" % index))
                else:
                    # Si un ou plusieurs enfants existente, on crée un sous-menu
                    self.SousMenuCategories(key, sm, valeurs[0], valeurs[3])

            
        # Rattachement de ce menu au menu parent
        if nbre != 0 :
            index, texte = 4, titre
            setattr(self, "popupID%s" % index, wx.NewId())
            menu.AppendMenu(getattr(self, "popupID%s" % index), texte, sm)
                  

    def CreationImage(self, tailleImages, r, v, b, IDcategorie):
        """ Création des images pour le TreeCtrl """
        if 'phoenix' in wx.PlatformInfo:
            bmp = wx.Image(tailleImages[0], tailleImages[1], True)
            bmp.SetRGB((0, 0, 16, 16), r, v, b)
        else:
            bmp = wx.EmptyImage(tailleImages[0], tailleImages[1], True)
            bmp.SetRGBRect((0, 0, 16, 16), r, v, b)
        # Si c'est la couleur déjà sélectionnée :
        if self.dictPresences[self.Context[0]][5] == IDcategorie :
            if 'phoenix' in wx.PlatformInfo:
                bmp.SetRGB((4, 4, 8, 8), 0, 0, 0)
            else:
                bmp.SetRGBRect((4, 4, 8, 8), 0, 0, 0)
        return bmp.ConvertToBitmap()
    
    def SaisiePresences(self):
        """ Saisie de présences à partir des lignes sélectionnées """ 
        dlg = DLG_Saisie_presence.Dialog(self, selectionsLignes)
        dlg.ShowModal()
        dlg.Destroy()

    def SupprimerPresencesLignes(self):
        """ Supprime toutes les tâches des lignes sélectionnées """
        nbreLignes = len(selectionsLignes)
        
        # Recherche des ID des présences contenues dans les lignes sélectionnées
        listeIDpresences = []
        for ligne in selectionsLignes :
            IDpersonne1 = ligne[0]
            date1 = ligne[1]
            for key, presence in self.dictPresences.items() :
                IDpresence = presence[0]
                IDpersonne2 = presence[1]
                date2 = presence[2]
                
                if IDpersonne1 == IDpersonne2 :
                    if date1 == date2 :
                        if IDpresence not in listeIDpresences :
                            listeIDpresences.append(IDpresence)
        
        if len(listeIDpresences) == 0 : 
            dlg = wx.MessageDialog(self, _(u"Il n'existe aucune tâche à supprimer sur la ou les lignes sélectionnées !"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy() 
            return
        
        if nbreLignes == 1 :
            txt = _(u"Souhaitez-vous vraiment supprimer toutes les tâches de la ligne sélectionnée ?")
        else:
            txt = _(u"Souhaitez-vous vraiment supprimer toutes les tâches des ") + str(nbreLignes) + _(u" lignes sélectionnées ?")
        dlg = wx.MessageDialog(self, txt ,  _(u"Suppression de toutes les tâches"), wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
        if dlg.ShowModal() == wx.ID_NO :
            print("suppression annulle")
            dlg.Destroy() 
            return
        
        dlg.Destroy()
        
        # Suppression
        DB = GestionDB.DB()
        if len(listeIDpresences) == 1 : cond = "(%d)" % listeIDpresences[0]
        else : cond = str(tuple(listeIDpresences))
        DB.ExecuterReq("DELETE FROM presences WHERE IDpresence IN %s" % cond)
        DB.Commit()
        DB.Close()
        
        self.MAJafterModif()
        
        
        
    def ClearSelectionsLignes(self):
        global selectionsLignes
        selectionsLignes = []
        
    def MAJafterModif(self):
        """ Met à jour l'affichage du DC suite à une MODIF ou un AJOUT de présences """
        self.ClearSelectionsLignes()
        self.GetParent().GetGrandParent().MAJpanelPlanning(reinitSelectionPersonnes=False)
        self.GetParent().GetGrandParent().panelPersonnes.listCtrlPersonnes.CreateCouleurs(cocheAussi = False)

    def Importation_Vacances(self):
        """ Importation des dates de vacances """

        req = "SELECT * FROM periodes_vacances ORDER BY date_debut;"
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeVacances1 = DB.ResultatReq()
        DB.Close()
        
        listeVacances2 = []
        listePeriodesVacs = []
        
        for id, nom, annee, date_debut, date_fin in listeVacances1 :
            datedebut = datetime.date(int(date_debut[:4]), int(date_debut[5:7]), int(date_debut[8:10]))
            datefin = datetime.date(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]))
            listeVacances2.append(datedebut)
            listeTemp = []
            for x in range((datefin-datedebut).days) :
                # Ajout à la liste des jours de vacances (qui sert au coloriage de la case)
                datedebut = datedebut + datetime.timedelta(days=1)        
                listeVacances2.append(datedebut)
                listeTemp.append(datedebut)
            # Ajout au dictionnaire des vacances (qui sert à sélectionner une période de vacs dans le calendrier)
            listePeriodesVacs.append( (annee, nom, tuple(listeTemp)) )
        
        return listeVacances2, listePeriodesVacs
    
    def Importation_Feries(self):
        """ Importation des dates de vacances """
        req = "SELECT * FROM jours_feries;"
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeFeriesTmp = DB.ResultatReq()
        DB.Close()
        
        listeFeriesFixes = []
        listeFeriesVariables = []
        for ID, type, nom, jour, mois, annee in listeFeriesTmp :
            if type =="fixe" :
                date = (jour, mois)
                listeFeriesFixes.append(date)            
            else:
                date = datetime.date(annee, mois, jour)
                listeFeriesVariables.append(date)
        return listeFeriesFixes, listeFeriesVariables
    
    def Importation_Contrats(self):
        """ Importation des contrats des personnes """
        req = "SELECT IDcontrat, IDpersonne, date_debut, date_fin FROM contrats;"
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeContrats = DB.ResultatReq()
        DB.Close()
        # Liste en dictionnaire :
        dictContrats = {}
        for IDcontrat, IDpersonne, date_debut, date_fin in listeContrats :
            if IDpersonne in dictContrats : 
                dictContrats[IDpersonne].append( (IDcontrat, date_debut, date_fin) )
            else:
                dictContrats[IDpersonne] = [ (IDcontrat, date_debut, date_fin), ]
        return dictContrats
    
    
class BarreOptions(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style = wx.NO_BORDER)
        self.parent = parent
##        self.SetBackgroundColour("white")
        
        # Widgets        
        self.txtRadio = wx.StaticText( self, -1, " Grouper par :" )
        self.radio1 = wx.RadioButton( self, -1, "Dates", style = wx.RB_GROUP )
        self.radio2 = wx.RadioButton( self, -1, "Personnes" )
        
        self.boutonOutils = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Outils.png"), wx.BITMAP_TYPE_PNG) )
        self.txtOutils = wx.StaticText( self, -1, _(u"Outils") )
        self.boutonOutils.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher le menu des outils du planning")))
        self.txtOutils.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher le menu des outils du planning")))
        
        self.boutonOptions = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Options.png"), wx.BITMAP_TYPE_PNG) )
        self.txtOptions = wx.StaticText( self, -1, _(u"Options d'affichage") )
        self.boutonOptions.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher le menu des options d'affichage du planning")))
        self.txtOptions.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher le menu des options d'affichage du planning")))
        
        self.boutonAide = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Aide.png"), wx.BITMAP_TYPE_PNG) )
        self.txtAide = wx.StaticText( self, -1, "Aide " )
        self.boutonAide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher l'aide")))
        self.txtAide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher l'aide")))

        # Bind
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio1, self.radio1 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio2, self.radio2 )
        
        self.boutonOutils.Bind(wx.EVT_MOTION, self.OnMotion_Outils)
        self.boutonOutils.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow_Outils)
        self.boutonOutils.Bind(wx.EVT_LEFT_DOWN, self.Menu_Outils)
        self.txtOutils.Bind(wx.EVT_MOTION, self.OnMotion_Outils)
        self.txtOutils.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow_Outils)
        self.txtOutils.Bind(wx.EVT_LEFT_DOWN, self.Menu_Outils)
        
        self.boutonOptions.Bind(wx.EVT_MOTION, self.OnMotion_Options)
        self.boutonOptions.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow_Options)
        self.boutonOptions.Bind(wx.EVT_LEFT_DOWN, self.Menu_Options)
        self.txtOptions.Bind(wx.EVT_MOTION, self.OnMotion_Options)
        self.txtOptions.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow_Options)
        self.txtOptions.Bind(wx.EVT_LEFT_DOWN, self.Menu_Options)
        
        self.boutonAide.Bind(wx.EVT_MOTION, self.OnMotion_Aide)
        self.boutonAide.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow_Aide)
        self.boutonAide.Bind(wx.EVT_LEFT_DOWN, self.Com_Aide)
        self.txtAide.Bind(wx.EVT_MOTION, self.OnMotion_Aide)
        self.txtAide.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow_Aide)
        self.txtAide.Bind(wx.EVT_LEFT_DOWN, self.Com_Aide)

        
        # Layout
        sizer = wx.FlexGridSizer(rows=1, cols=12, vgap=0, hgap=0)
        sizer.Add( self.txtRadio, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 3 )
        sizer.Add( self.radio1, 0, wx.ALL, 3 )
        sizer.Add( self.radio2, 0, wx.ALL, 3 )
        sizer.Add( (10, 10), 0, wx.ALL, 3 )
        sizer.Add( self.boutonOutils, 0, wx.ALL, 2 )
        sizer.Add( self.txtOutils, 0, wx.ALL, 3 )
        sizer.Add( (3, 10), 0, wx.ALL, 3 )
        sizer.Add( self.boutonOptions, 0, wx.ALL, 2 )
        sizer.Add( self.txtOptions, 0, wx.ALL, 3 )
        sizer.Add( (3, 10), 0, wx.ALL, 3 )
        sizer.Add( self.boutonAide, 0, wx.ALL, 2 )
        sizer.Add( self.txtAide, 0, wx.ALL, 3 )
        sizer.AddGrowableCol(3)
        self.SetSizer(sizer)
        
        
    
    def OnRadio1(self, event):
        global modeAffichage
        modeAffichage = 2
        self.GetGrandParent().GetParent().MAJpanelPlanning()
        self.GetGrandParent().GetParent().MAJpanelPlanning()

    def OnRadio2(self, event):
        global modeAffichage
        modeAffichage = 3
        self.GetGrandParent().GetParent().MAJpanelPlanning()
        self.GetGrandParent().GetParent().MAJpanelPlanning()

    def OnMotion_Outils(self, event):
        self.boutonOutils.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Outils_2.png"), wx.BITMAP_TYPE_PNG))
        self.txtOutils.SetForegroundColour(wx.RED)
        self.txtOutils.Refresh()
        event.Skip()

    def OnLeaveWindow_Outils(self, event):
        self.boutonOutils.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Outils.png"), wx.BITMAP_TYPE_PNG))
        self.txtOutils.SetForegroundColour(wx.BLACK)
        self.txtOutils.Refresh()
        event.Skip()

    def OnMotion_Options(self, event):
        self.boutonOptions.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Options_2.png"), wx.BITMAP_TYPE_PNG))
        self.txtOptions.SetForegroundColour(wx.RED)
        self.txtOptions.Refresh()
        event.Skip()

    def OnLeaveWindow_Options(self, event):
        self.boutonOptions.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Options.png"), wx.BITMAP_TYPE_PNG))
        self.txtOptions.SetForegroundColour(wx.BLACK)
        self.txtOptions.Refresh()
        event.Skip()
        
    def OnMotion_Aide(self, event):
        self.boutonAide.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Aide_2.png"), wx.BITMAP_TYPE_PNG))
        self.txtAide.SetForegroundColour(wx.RED)
        self.txtAide.Refresh()
        event.Skip()

    def OnLeaveWindow_Aide(self, event):
        self.boutonAide.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Aide.png"), wx.BITMAP_TYPE_PNG))
        self.txtAide.SetForegroundColour(wx.BLACK)
        self.txtAide.Refresh()
        event.Skip()
    
    def Com_Aide(self, event):
        FonctionsPerso.Aide(1)

    def Menu_Outils(self, event):
        """Ouverture du menu contextuel des outils du planning """
        
        # Création du menu contextuel
        menu = UTILS_Adaptations.Menu()
        
        # Commande Imprimer
        IDitem = 10
        item = wx.MenuItem(menu, IDitem, _(u"Imprimer le planning affiché"), _(u"Imprimer le planning affiché"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_10, id=IDitem)
        
        # Commande Autres impressions
        IDitem = 40
        item = wx.MenuItem(menu, IDitem, _(u"Imprimer d'autres types de plannings"), _(u"Imprimer d'autres types de plannings"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_40, id=IDitem)
        
        menu.AppendSeparator()
        
        # Commande Stats simples
        IDitem = 20
        item = wx.MenuItem(menu, IDitem, _(u"Statistiques"), _(u"Afficher les statistiques des présences"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Stats.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_20, id=IDitem)
        
        # Commande Scénarios
        IDitem = 30
        item = wx.MenuItem(menu, IDitem, _(u"Gestion des scénarios"), _(u"Gestion des scénarios"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Scenario.png"), wx.BITMAP_TYPE_PNG))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_30, id=IDitem)
                
        self.PopupMenu(menu)
        menu.Destroy()


    def Menu_Options(self, event):
        """Ouverture du menu contextuel des options d'affichage du planning """
        
        # Création du menu contextuel
        menu = UTILS_Adaptations.Menu()
        
        # Affichage des légendes
        IDitem = 210
        menu.Append(IDitem, _(u"Afficher les légendes"), _(u"Affiche ou non les légendes des présences"), wx.ITEM_CHECK)
        if hauteurBarre == 26 :
            menu.Check(IDitem, True)
        self.Bind(wx.EVT_MENU, self.Menu_210, id=IDitem)
        
        # Affichage des périodes de contrats
        IDitem = 220
        menu.Append(IDitem, _(u"Afficher les périodes de contrats"), _(u"Affiche ou non les périodes des contrats des personnes sélectionnées"), wx.ITEM_CHECK)
        if afficher_contrats == True :
            menu.Check(IDitem, True)
        self.Bind(wx.EVT_MENU, self.Menu_220, id=IDitem)
        
        # Affichage des temps de fin de ligne
        IDitem = 230
        menu.Append(IDitem, _(u"Afficher les temps de fin de ligne"), _(u"Affiche ou non les temps de fin de ligne"), wx.ITEM_CHECK)
        if afficher_temps_ligne == True :
            menu.Check(IDitem, True)
        self.Bind(wx.EVT_MENU, self.Menu_230, id=IDitem)
        
        # Affichage des temps en tete de groupe
        IDitem = 240
        menu.Append(IDitem, _(u"Afficher les temps en tête de groupe"), _(u"Affiche ou non les temps en tête de groupe"), wx.ITEM_CHECK)
        if afficher_temps_groupe == True :
            menu.Check(IDitem, True)
        self.Bind(wx.EVT_MENU, self.Menu_240, id=IDitem)
        
        # Affichage du nbre de présents
        IDitem = 250
        menu.Append(IDitem, _(u"Afficher la barre quantitative"), _(u"Affiche ou non la barre quantitative"), wx.ITEM_CHECK)
        if afficher_nbre_presents == True :
            menu.Check(IDitem, True)
        self.Bind(wx.EVT_MENU, self.Menu_250, id=IDitem)
        
        menu.AppendSeparator()
        
        # Commande Imprimer
        IDitem = 260
        item = wx.MenuItem(menu, IDitem, _(u"Définir l'amplitude horaire affichée par défaut"), _(u"Définir l'amplitude horaire affichée par défaut"))
        menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_260, id=IDitem)
        
        self.PopupMenu(menu)
        menu.Destroy()


    def Menu_10(self, event):
        """ Imprimer le planning """
        self.GetParent().DCplanning.Impression()
    
    def Menu_40(self, event):
        """ Autres types de planning """
        # Demande le type d'impression à l'utilisateur
        from Dlg import DLG_Selection_type_document
        listeBoutons = [
            (Chemins.GetStaticPath("Images/BoutonsImages/Imprimer_planning_mensuel.png"), _(u"Cliquez ici pour imprimer un planning mensuel")),
            (Chemins.GetStaticPath("Images/BoutonsImages/Imprimer_planning_annuel.png"), _(u"Cliquez ici pour imprimer un planning annuel pour une personne")),
            ]
        dlg = DLG_Selection_type_document.Dialog(self, size=(650, 335), listeBoutons=listeBoutons, type="presences")
        if dlg.ShowModal() == wx.ID_OK:
            ChoixType = dlg.GetChoix()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        
        if ChoixType == 1 :
            # Type Planning mensuel
            from Dlg import DLG_Impression_calendrier_mensuel
            dlg = DLG_Impression_calendrier_mensuel.MyDialog(None)
            dlg.ShowModal()      
        if ChoixType == 2 :
            # Type Planning annuel
            from Dlg import DLG_Impression_calendrier_annuel
            dlg = DLG_Impression_calendrier_annuel.MyDialog(None)
            dlg.ShowModal()        

    def Menu_20(self, event):
        """ Afficher les stats """
        topWindow = wx.GetApp().GetTopWindow() 
        try : topWindow.SetStatusText(_(u"Chargement du module des statistiques en cours. Veuillez patientez..."))
        except : pass
        panelPresences = self.GetGrandParent().GetParent()
        # Récupération des dates du calendrier
        listeDatesCalendrier = panelPresences.panelCalendrier.GetSelectionDates()
        listeDates = []
        for dateDD in listeDatesCalendrier :
            listeDates.append(str(dateDD))
        # Récupération des personnes de la liste de personnes
        listePersonnes = panelPresences.panelPersonnes.listCtrlPersonnes.GetListePersonnes()
        from Dlg import DLG_Statistiques
        dlg = DLG_Statistiques.Dialog(self, listeDates=listeDates, listePersonnes=listePersonnes)
        dlg.ShowModal()
        dlg.Destroy()
        topWindow = wx.GetApp().GetTopWindow() 
        try : topWindow.SetStatusText(u"")
        except : pass

    def Menu_30(self, event):
        """ Gestion des scénarios """
        from Dlg import DLG_Scenario_gestion
        dlg = DLG_Scenario_gestion.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def Menu_210(self, event):
        """ Afficher légendes """
        global hauteurBarre, modeTexte
        if hauteurBarre == 26 :
            hauteurBarre = 15
            modeTexte = 1
            etat = False
        else:
            hauteurBarre = 26
            modeTexte = 2
            etat = True
        # MAJ du planning
        self.GetGrandParent().GetParent().MAJpanelPlanning()
        # Mémorisation du paramètre
        FonctionsPerso.Parametres(mode="set", categorie="planning", nom="afficher_legendes", valeur=etat)

    def Menu_220(self, event):
        """ Afficher contrats """
        global afficher_contrats
        if afficher_contrats == True :
            afficher_contrats = False
        else:
            afficher_contrats = True
        # MAJ du planning
        self.GetGrandParent().GetParent().MAJpanelPlanning()
        # Mémorisation du paramètre
        FonctionsPerso.Parametres(mode="set", categorie="planning", nom="afficher_contrats", valeur=afficher_contrats)

    def Menu_230(self, event):
        """ Afficher les temps en fin de ligne """
        global afficher_temps_ligne
        if afficher_temps_ligne == True :
            afficher_temps_ligne = False
        else:
            afficher_temps_ligne = True
        # MAJ du planning
        self.GetGrandParent().GetParent().MAJpanelPlanning()
        # Mémorisation du paramètre
        FonctionsPerso.Parametres(mode="set", categorie="planning", nom="afficher_temps_ligne", valeur=afficher_temps_ligne)

    def Menu_240(self, event):
        """ Afficher les temps en tete de groupe """
        global afficher_temps_groupe
        if afficher_temps_groupe == True :
            afficher_temps_groupe = False
        else:
            afficher_temps_groupe = True
        # MAJ du planning
        self.GetGrandParent().GetParent().MAJpanelPlanning()
        # Mémorisation du paramètre
        FonctionsPerso.Parametres(mode="set", categorie="planning", nom="afficher_temps_groupe", valeur=afficher_temps_groupe)

    def Menu_250(self, event):
        """ Afficher le nbre de présents """
        global afficher_nbre_presents
        if afficher_nbre_presents == True :
            afficher_nbre_presents = False
        else:
            afficher_nbre_presents = True
        # MAJ du planning
        self.GetGrandParent().GetParent().MAJpanelPlanning()
        # Mémorisation du paramètre
        FonctionsPerso.Parametres(mode="set", categorie="planning", nom="afficher_nbre_presents", valeur=afficher_nbre_presents)

    def Menu_260(self, event):
        """ Afficher le nbre de présents """
        global heureMin, heureMax
        from Dlg import DLG_Saisie_heures
        dlg = DLG_Saisie_heures.MyDialog(self, heureMin, heureMax)
        if dlg.ShowModal() == wx.ID_OK:
            heureMin = dlg.GetHeureMin()
            heureMax = dlg.GetHeureMax()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        
        # MAJ du planning
        self.GetGrandParent().GetParent().MAJpanelPlanning()
        
        # Transformation des heures en string
        heureMinStr = "%s:%s" % (heureMin.hour, heureMin.minute)
        heureMaxStr = "%s:%s" % (heureMax.hour, heureMax.minute)
        
        # Mémorisation du paramètre
        FonctionsPerso.Parametres(mode="set", categorie="planning", nom="heureMin", valeur=heureMinStr)
        FonctionsPerso.Parametres(mode="set", categorie="planning", nom="heureMax", valeur=heureMaxStr)


# --------------- PANEL -----------------------------------------------------------------------------

class PanelPlanning(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID)
        
        # Création du DC des graduations
        self.DCgraduations = Graduations(self)

        # Création du DC Planning
        self.dictCategories = self.ImportCategories()
        # >>>>>>>> A changer <<<<<<< :
        listeDates = []     # datetime.date(2008, 01, 19), datetime.date(2008, 01, 20)
        listeIDPersonne = []    # [1, 2, 3, 4]

        dictGroupes, dictLignes, listePresences = self.InitPlanning(modeAffichage, listeIDPersonne, listeDates)
        self.listePresents = self.RecherchePresents(listeDates)
        
        self.joursVacances = self.Importation_Vacances()
        self.listeFeriesFixes, self.listeFeriesVariables = self.Importation_Feries()
        
        self.DCplanning = WidgetPlanning(self, listePresences, self.dictCategories, dictGroupes, dictLignes)

        self.MAJ_DictCategories(listePresences)
        
        self.barreOptions = BarreOptions(self)
        
        self.barreTitre = FonctionsPerso.BarreTitre(self, _(u"Le planning"), _(u"Le planning"))

        # Layout
        sizer =  wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.barreTitre, 0, wx.EXPAND, 0)
        grid_sizer = wx.FlexGridSizer(rows=3, cols=1, hgap=0, vgap=0)
        grid_sizer.Add(self.DCgraduations, 0, wx.EXPAND|wx.ALL, 10)
        grid_sizer.Add(self.DCplanning, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        grid_sizer.Add(self.barreOptions, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer.AddGrowableRow(1)
        grid_sizer.AddGrowableCol(0)
        sizer.Add(grid_sizer, 1, wx.EXPAND, 0)
        self.SetSizer(sizer)
        self.Layout()

    
    def SetModeAffichage(self, numMode) :
        global modeAffichage
        modeAffichage = numMode

    def GetModeAffichage(self) :
        return modeAffichage
        
    def InitPlanning(self, modeAffich, listeIDPersonne, listeDates) :
        listeDates.sort()
        if modeAffich == 1 : return self.ImportGroupes_Mode1(listeIDPersonne, listeDates)
        if modeAffich == 2 : return self.ImportGroupes_Mode2(listeIDPersonne, listeDates)
        if modeAffich == 3 : return self.ImportGroupes_Mode3(listeIDPersonne, listeDates)
        
    def ReInitPlanning(self, modeAffich, listeIDPersonne, listeDates) :
        # Initialisation des données
        dictGroupes, dictLignes, listePresences = self.InitPlanning(modeAffichage, listeIDPersonne, listeDates)
        self.listePresents = self.RecherchePresents(listeDates)
        if len(dictGroupes) != 0 :
            YFinDessin = dictGroupes[len(dictGroupes)][2]
            self.DCplanning.SetSizeDC(h=YFinDessin)
        
        # Récupération des périodes de vacances et des jours fériés
        self.DCplanning.joursVacances, self.DCplanning.listePeriodesVacs = self.DCplanning.Importation_Vacances()
        self.DCplanning.listeFeriesFixes, self.DCplanning.listeFeriesVariables = self.DCplanning.Importation_Feries()
        self.DCplanning.dictContrats = self.DCplanning.Importation_Contrats()
        
        #self.dictCategories = self.ImportCategories()
        self.MAJ_DictCategories(listePresences)

        self.DCplanning.InitPlanning(listePresences, self.dictCategories, dictGroupes, dictLignes)


    def ImportPresences(self, listeDates, listePersonnes):
        """ Récupération des présences dans la base """

        # Création de la liste des conditions de dates
        strDates = ""
        for date in listeDates :
            strDates += "date='" + date + "' Or "
        strDates = strDates[:-4]
        # Création de la liste des conditions de IDpersonne
        strPersonnes = ""
        for IDpersonne in listePersonnes :
            strPersonnes += "IDpersonne=" + str(IDpersonne) + " Or "
        strPersonnes = strPersonnes[:-4]
        # Création du str final de conditions
        if len(strDates)!=0 and len(strPersonnes)!=0 :
            conditions = "WHERE (" + strDates + ") AND (" + strPersonnes + ")"
        if len(strDates)!=0 and len(strPersonnes)==0 :
            conditions = "WHERE " + strDates
        if len(strDates)==0 and len(strPersonnes)!=0 :
            conditions = "WHERE " + strPersonnes
        if len(strDates)==0 and len(strPersonnes)==0 :
            conditions = ""  

        # Requete SQL
        DB = GestionDB.DB()
        req = """
        SELECT *
        FROM presences %s;
        """ % conditions
        DB.ExecuterReq(req)
        listeValeurs = DB.ResultatReq()
        DB.Close()
        return listeValeurs

    def RecherchePresents(self, listeDates):
        """ Recherche les ID des personnes présentes sur la période de dates données """

        listeConditions = [str(date) for date in listeDates] 
        if len(listeConditions) == 0 : listeConditions = "('3000-10-10')"
        elif len(listeConditions) == 1 : listeConditions = "('%s')" % listeConditions[0]
        else : listeConditions = str(tuple(listeConditions))

        DB = GestionDB.DB()
        req = """
        SELECT Count(presences.IDpersonne) AS CompteDeIDpersonne, presences.IDpersonne
        FROM presences INNER JOIN personnes ON presences.IDpersonne = personnes.IDpersonne
        WHERE presences.date IN %s
        GROUP BY presences.IDpersonne;
        """ % listeConditions
        
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        
        listeIDpersonnes = []
        for nbrePresences, ID in listeTemp :
            listeIDpersonnes.append(ID)
        
        return listeIDpersonnes

    def ImportGroupes_Mode1(self, listeIDPersonne, listeDates):
        """ Récupération des présences dans la base
        > MODE 1
        > Groupe = DATES | Lignes = PERSONNES | Uniquement les présents chaque jour
        """
        print("mode 1")
        listeConditions = [str(date) for date in listeDates] 
        if len(listeConditions) == 0 : listeConditions = "('3000-10-10')"
        elif len(listeConditions) == 1 : listeConditions = "('%s')" % listeConditions[0]
        else : listeConditions = str(tuple(listeConditions))
        
        DB = GestionDB.DB()
        req = """
        SELECT presences.date, presences.IDpersonne, nom AS nomPersonne
        FROM presences INNER JOIN personnes ON presences.IDpersonne = personnes.IDpersonne
        GROUP BY presences.date, presences.IDpersonne, nom
        HAVING presences.date IN %s
        ORDER BY presences.date, nom;
        """ % listeConditions
        
        DB.ExecuterReq(req)
        listeLignes = DB.ResultatReq()
        DB.Close()

        # Importation des noms des personnes pour les entetes de lignes
        dictPersonnes = self.ImportPersonnes()

        dictGroupes = {}
        prevIDpersonne = None
        prevDate = None
        IDGroupe = 0
        posY = 10
        nbreLignesGroupe = 0
        
        for ligne in listeLignes :
            date = ligne[0]
            IDpersonne = ligne[1]

            datetimeDate = StrEnDatetimeDate(date)

            if datetimeDate != prevDate :
                # Clôture du précédent groupe
                if IDGroupe != 0 :
                    dictGroupes[IDGroupe][2] = posY
                    dictGroupes[IDGroupe][3] = nbreLignesGroupe
                    posY += 22
                
                # Création d'un nouveau groupe
                IDGroupe += 1
                prevDate = datetimeDate
                posYEnteteGroupe = posY
                posY += hauteurTitreGroupe
                titreGroupe = DatetimeDateEnStr(datetimeDate)
                dictGroupes[IDGroupe] = [titreGroupe, posYEnteteGroupe, None, 0, [] ] # [titreGroupe, posY_debut, posY_fin, nbreLignes, listeLignes]
                nbreLignesGroupe = 0

            # Création d'une ligne
            prevIDpersonne = IDpersonne
            nbreLignesGroupe += 1

            # Calcul des positions verticales du groupe et de ses lignes
            dictGroupes[IDGroupe][4].sort #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< A voir
            posYLigne = posY
            posY += hauteurBarre + ecartLignes
            texteLigne = dictPersonnes[IDpersonne][0] + " " + dictPersonnes[IDpersonne][1]
            dictGroupes[IDGroupe][4].append((IDpersonne, datetimeDate, posYLigne, texteLigne))

        # Clôture le dernier groupe
        dictGroupes[IDGroupe][2] = posY
        dictGroupes[IDGroupe][3] = nbreLignesGroupe

        # Création du dictionnaire des lignes
        dictLignes = self.CreationDictLignes(dictGroupes)

        # Création d'une liste temporaire des dates au format "2008-01-15"
        listeDatesTemp = []
        for date in listeDates :
            listeDatesTemp.append(str(date))

        # Création de la liste des présences
        listePresences = []
        if len(dictLignes) != 0 :
            listePresences = self.ImportPresences(listeDatesTemp, listeIDPersonne)
                                  
        return dictGroupes, dictLignes, listePresences



    def ImportGroupes_Mode2(self, listeIDPersonne, listeDates):
        """ Récupération des présences dans la base
        > MODE 2
        > Groupe = DATES | Lignes = PERSONNES | Toutes les personnes demandées chaque jour demandé
        """

        # Importation des noms des personnes pour les entetes de lignes
        try : dictPersonnes
        except : dictPersonnes = self.ImportPersonnes()

        # Création de la liste des personnes
        listePersonnes = []
        for IDpersonne in listeIDPersonne :
            nomPersonne = dictPersonnes[IDpersonne][0] + " " + dictPersonnes[IDpersonne][1]
            listePersonnes.append((nomPersonne, IDpersonne))
        listePersonnes.sort()


        dictGroupes = {}
        posY = 10
        IDgroupe = 1
        for date in listeDates :
            nbreLignes = len(listePersonnes)
            hauteurGroupeTemp = hauteurTitreGroupe
            if afficher_nbre_presents == True :
                hauteurGroupeTemp += hauteurBarreNbrePresents
            dictGroupes[IDgroupe] = [DatetimeDateEnStr(date), posY, posY+hauteurGroupeTemp+(nbreLignes*(hauteurBarre+ecartLignes)), nbreLignes, [] ] # [titreGroupe, posY_debut, posY_fin, nbreLignes]
            posY += hauteurGroupeTemp

            # Création des lignes du groupe            
            for personne in listePersonnes :
                IDpersonne = personne[1]
                texteLigne = personne[0]
                dictGroupes[IDgroupe][4].append((IDpersonne, date, posY, texteLigne))
                posY += hauteurBarre+ecartLignes

            # Clôture du groupe
            IDgroupe += 1
            posY += 22

        # Création du dictionnaire des lignes
        dictLignes = self.CreationDictLignes(dictGroupes)

        # Création d'une liste temporaire des dates au format "2008-01-15"
        listeDatesTemp = []
        for date in listeDates :
            listeDatesTemp.append(str(date))

        # Création de la liste des présences
        listePresences = []
        if len(dictLignes) != 0 :
            listePresences = self.ImportPresences(listeDatesTemp, listeIDPersonne)
        
        self.RecherchePresents(listeDates)
                                  
        return dictGroupes, dictLignes, listePresences

    
    def ImportGroupes_Mode3(self, listeIDPersonne, listeDates):
        """ Récupération des présences dans la base
        > MODE 3
        > Groupe = PERSONNES | Lignes = DATES | Toutes les personnes demandées chaque jour demandé
        """

        # Importation des noms des personnes pour les entetes de lignes
        try : dictPersonnes
        except : dictPersonnes = self.ImportPersonnes()

        # Création de la liste des personnes
        listePersonnes = []
        for IDpersonne in listeIDPersonne :
            nomPersonne = dictPersonnes[IDpersonne][0] + " " + dictPersonnes[IDpersonne][1]
            listePersonnes.append((nomPersonne, IDpersonne))
        listePersonnes.sort()
        
        dictGroupes = {}
        posY = 10
        IDgroupe = 1
        for personne in listePersonnes :
            nbreLignes = len(listeDates)
            IDpersonne = personne[1]
            nomPersonne = personne[0]
            hauteurGroupeTemp = hauteurTitreGroupe
            if afficher_nbre_presents == True :
                hauteurGroupeTemp += hauteurBarreNbrePresents
            dictGroupes[IDgroupe] = [nomPersonne, posY, posY+hauteurGroupeTemp+(nbreLignes*(hauteurBarre+ecartLignes)), nbreLignes, [] ] # [titreGroupe, posY_debut, posY_fin, nbreLignes, listeLignes]
            posY += hauteurGroupeTemp

            # Création des lignes du groupe            
            for date in listeDates :
                dictGroupes[IDgroupe][4].append((IDpersonne, date, posY, DatetimeDateEnStr(date)))
                posY += hauteurBarre+ecartLignes

            # Clôture du groupe
            IDgroupe += 1
            posY += 22
        
        # Création du dictionnaire des lignes
        dictLignes = self.CreationDictLignes(dictGroupes)

        # Création d'une liste temporaire des dates au format "2008-01-15"
        listeDatesTemp = []
        for date in listeDates :
            listeDatesTemp.append(str(date))

        # Création de la liste des présences
        listePresences = []
        if len(dictLignes) != 0 :
            listePresences = self.ImportPresences(listeDatesTemp, listeIDPersonne)

                          
        return dictGroupes, dictLignes, listePresences



    def CreationDictLignes(self, dictGroupes):
        """ Créée un dict des lignes à partir du dictGroupes """
        dictLignes = {}
        for IDgroupe, groupe in dictGroupes.items() :
            for ligne in groupe[4] :
                IDpersonne = ligne[0]
                datetimeDate = ligne[1]
                posYLigne = ligne[2]
                texteLigne = ligne[3]
                dictLignes[(IDpersonne, datetimeDate)] = [IDgroupe, posYLigne, texteLigne, False]       # [IDgroupe, posYligne, texte, Sélectionné]
                
        return dictLignes

    def MAJ_DictCategories(self, listePresences):
        """ Ajoute les temps dans le dictCategories """
        for presence in listePresences :
            HMin = datetime.timedelta(hours=int(presence[3][:2]), minutes=int(presence[3][3:]))
            HMax = datetime.timedelta(hours=int(presence[4][:2]), minutes=int(presence[4][3:]))
            duree = ((HMax - HMin).seconds)//60
            self.dictCategories[presence[5]][4] += duree
       

    def ImportPersonnes(self):
        """ Récupération des noms des personnes """
        DB = GestionDB.DB()
        req = "SELECT IDpersonne, nom, prenom FROM personnes"
        DB.ExecuterReq(req)
        listePersonnes = DB.ResultatReq()
        DB.Close()
        # Transformation de la liste en dict
        dictPersonnes = {}
        for item in listePersonnes :
            dictPersonnes[item[0]] = (item[1], item[2])
        # Renvoie le dict
        return dictPersonnes

    def RechargeDictCategories(self):
        self.dictCategories = self.ImportCategories()
##        print "MAJ dict categorie du DCplanning !"
        
    def ImportCategories(self):
        """ Récupération des catégories de présences dans la base """
        DB = GestionDB.DB()
        req = "SELECT * FROM cat_presences"
        DB.ExecuterReq(req)
        listecategories = DB.ResultatReq()
        DB.Close()
        # Transformation de la liste en dict
        dictCategories = {}
        for cat in listecategories :
            dictCategories[cat[0]] = [cat[1], cat[2], cat[3], cat[4], 0] # 0=temps en minutes
        # Renvoie le dict
        return dictCategories



    def Importation_Vacances(self):
        """ Importation des dates de vacances """
        req = "SELECT * FROM periodes_vacances ORDER BY date_debut;"
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeVacances1 = DB.ResultatReq()
        DB.Close()
        
        listeVacances2 = []
        for id, nom, annee, date_debut, date_fin in listeVacances1 :
            datedebut = datetime.date(int(date_debut[:4]), int(date_debut[5:7]), int(date_debut[8:10]))
            datefin = datetime.date(int(date_fin[:4]), int(date_fin[5:7]), int(date_fin[8:10]))
            listeVacances2.append(datedebut)
            for x in range((datefin-datedebut).days) :
                datedebut = datedebut + datetime.timedelta(days=1)        
                listeVacances2.append(datedebut)
                
        return listeVacances2
    
    def Importation_Feries(self):
        """ Importation des dates de vacances """
        req = "SELECT * FROM jours_feries;"
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeFeriesTmp = DB.ResultatReq()
        DB.Close()
        
        listeFeriesFixes = []
        listeFeriesVariables = []
        for ID, type, nom, jour, mois, annee in listeFeriesTmp :
            if type =="fixe" :
                date = (jour, mois)
                listeFeriesFixes.append(date)            
            else:
                date = datetime.date(annee, mois, jour)
                listeFeriesVariables.append(date)
        return listeFeriesFixes, listeFeriesVariables

# -------------- IMPRESSION PDF Format GRAPH ---------------------------------------------------------------------

class ImpressionPDFvGraph():
    def __init__(self, orientation, dictCategories, dictGroupes, dictLignes, listePresences, dictPresences, maxWidth, maxHeight) :
        
##        print "largeurEnteteLigne=", largeurEnteteLigne
##        print "coordLigne =", coordLigne
##        print "hauteurBarre=", hauteurBarre
##        print "ecartLignes =", ecartLignes
##        print "modeTexte =", modeTexte
##        print "hauteurTitreGroupe=", hauteurTitreGroupe
##        print "dictCategories =", dictCategories
##        print "dictGroupes =", dictGroupes
##        print "dictLignes =", dictLignes
##        print "listePresences =", listePresences
##        print "dictPresences =", dictPresences
        
        from Utils import UTILS_Impression_presences_graph
        UTILS_Impression_presences_graph.Impression(orientation, dictCategories, dictGroupes, dictLignes, listePresences, dictPresences, coordLigne, hauteurBarre, ecartLignes, modeTexte)

# -------------- IMPRESSION PDF Format TEXTE ---------------------------------------------------------------------

class ImpressionPDFvTexte():
    def __init__(self, dictCategories, dictGroupes, dictLignes, listePresences, dictPresences, maxWidth, maxHeight) :
        
        # IDcategorie (nom, IDcat_parent, ordre, couleur, totalHeures)
        # [titreGroupe, posY_debut, posY_fin, nbreLignes, listeLignes]
        #  dictLignes[(IDpersonne, datetimeDate)] = [IDgroupe, posYLigne, texteLigne, False]       # [IDgroupe, posYligne, texte, Sélectionné]
        # IDpresence, IDpersonne, date, heureDebut, heureFin, IDcategorie, intitule, posG, posD, posYhaut, posYbas

        
        if len(dictGroupes) == 0 : 
            dlg = wx.MessageDialog(None, _(u"Vous devez sélectionner au moins une date dans le calendrier !"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy() 
            return
        
        # Tri de la liste des présences par heure de début
        if len(listePresences) != 0 :
            listePresences = sorted(listePresences, key=operator.itemgetter(3))
        
        # Création du PDF
        
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.units import inch, cm
        from reportlab.lib import colors

        PAGE_HEIGHT=defaultPageSize[1]
        PAGE_WIDTH=defaultPageSize[0]
        nomDoc = UTILS_Fichiers.GetRepTemp("impression_planning.pdf")
        if "win" in sys.platform : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc)
        story = []
        
        # Style du tableau
        style = TableStyle([('GRID', (0,0), (-1,-2), 0.25, colors.black),
                            ('VALIGN', (0,0), (-1,-1), 'TOP'), # Centre verticalement toutes les cases
                            ('ALIGN', (0,0), (-1,-1), 'LEFT'), # Titre du groupe à gauche
                            ('ALIGN', (0,1), (0,-1), 'RIGHT'), # Colonne dates alignée à droite
                            ('ALIGN', (1,1), (1,-2), 'LEFT'), # Colonne tâches alignée à gauche
                            ('ALIGN', (2,1), (2,-1), 'CENTRE'), # Colonne temps alignée au centre
##                            ('SPAN',(0,-1),(1,-1)), # Fusionne les 2 lignes du bas pour faire case Total
                            ('ALIGN', (0,-1), (1,-1), 'RIGHT'), # Met à droite le mot 'Total :'
                            ('SPAN',(0,0),(2,0)), # Fusionne les 3 lignes du haut pour faire le titre du groupe
                            ('FONT',(0,0),(-1,-1), "Helvetica", 8), # Donne la police de caract. + taille de police 
                            ('FONT',(0,0),(0,0), "Helvetica-Bold", 8), # Donne la police de caract. + taille de police du titre de groupe
                            ('FONT',(0,-1),(-1,-1), "Helvetica", 6), # Donne la police de caract. + taille de police de la ligne de total
                            ('BACKGROUND', (0,0), (2,0), colors.moccasin), # Donne la couleur de fond du titre de groupe
                            ])
            
        largeursColonnes = (150, 320, 50)
                            
                            
        # Création des groupes
        for index in range(1, len(dictGroupes)+1) :
            titreGroupe, posY_debut, posY_fin, nbreLignes, listeLignes = dictGroupes[index]
            
            # Création du titre
            if type(titreGroupe) != six.text_type :
                titreGroupe = titreGroupe.decode("iso-8859-15")
            dataTableau = [(titreGroupe, "" , ""),]
            
            # Création de chaque ligne
            totalTemps = 0
            for IDpersonne_ligne, datetime_date, posY, titre_ligne in listeLignes :
                
                # Récupération des présences de la ligne
                txtTaches = ""
                txtTemps = ""
                
                for IDpresence, IDpersonne_presence, date, heureDebut, heureFin, IDcategorie, intitule, posG, posD, posYhaut, posYbas in listePresences :
                    if date == datetime_date and IDpersonne_ligne == IDpersonne_presence :
                        if intitule != "" : intitule = " (" + intitule + ")"
                        txtTaches = txtTaches + self.formateHeure(heureDebut) + " - " + self.formateHeure(heureFin)  + " : " + dictCategories[IDcategorie][0] + intitule + "\n"
                        # Calcul du temps
                        HMin = datetime.timedelta(hours=heureDebut.hour, minutes=heureDebut.minute)
                        HMax = datetime.timedelta(hours=heureFin.hour, minutes=heureFin.minute)
                        temps = ((HMax - HMin).seconds)//60
                        totalTemps += temps
                        txtTemps = txtTemps + self.minutesEnHeures(temps) + "\n"
            
                # Intégration des lignes et des présences dans le tableau
                if type(titre_ligne) != six.text_type :
                    titre_ligne = titre_ligne.decode("iso-8859-15")
                dataTableau.append( (titre_ligne, txtTaches[:-1], txtTemps[:-1]) )
            
            # Création de la ligne de total
            dataTableau.append( ("","Total :", self.minutesEnHeures(totalTemps)) )
            
            # Création du tableau
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(style)
            story.append(tableau)
            story.append(Spacer(0,12))
        
        # Création des totaux de catégories
        dataTableau = [("", _(u"Total par catégorie"), ""),]
        totalTemps = 0
        for IDcategorie, valeurs in dictCategories.items() :
            nomCategorie = valeurs[0]
            temps = valeurs[4]
            if temps != 0 :
                totalTemps += temps
                dataTableau.append( ("", nomCategorie, self.minutesEnHeures(temps)) )
        dataTableau.append( ("", _(u"Total des heures :"), self.minutesEnHeures(totalTemps)) )
        
        style = TableStyle([('GRID', (1,0), (2,-2), 0.25, colors.black),
                            ('VALIGN', (0,0), (-1,-1), 'TOP'), # Centre verticalement toutes les cases
                            ('ALIGN', (1,0), (2,0), 'LEFT'), # Titre du groupe à gauche
                            ('ALIGN', (1,1), (1,-1), 'RIGHT'), # Colonne nom alignée à droite
                            ('ALIGN', (2,1), (2,-1), 'CENTRE'), # Colonne temps alignée au centre
                            ('SPAN',(1,0),(2,0)), # Fusionne les 2 colonnes du haut pour faire le titre du groupe
                            ('FONT',(0,0),(-1,-1), "Helvetica", 8), # Donne la police de caract. + taille de police 
                            ('FONT',(0,0),(0,0), "Helvetica-Bold", 8), # Donne la police de caract. + taille de police du titre de groupe
                            ('FONT',(0,-1),(-1,-1), "Helvetica", 6), # Donne la police de caract. + taille de police de la ligne de total
                            ('BACKGROUND', (1,0), (2,0), colors.beige), # Donne la couleur de fond du titre de groupe
                            ])
        largeursColonnes = (300, 170, 50)
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(style)
        story.append(tableau)
            
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
##        os.startfile(nomDoc)
        FonctionsPerso.LanceFichierExterne(nomDoc)
        

    def formateHeure(self, heure):
        heures = heure.hour
        minutes = heure.minute
        if len(str(minutes))==1 : minutes = str("0") + str(minutes)
        txt = str(heures) + "h" + str(minutes)
        return txt

    def minutesEnHeures(self, dureeMinutes) :
        if dureeMinutes != 0 :
            nbreHeures = dureeMinutes//60
            nbreMinutes = dureeMinutes-(nbreHeures*60)
            if len(str(nbreMinutes))==1 : nbreMinutes = str("0") + str(nbreMinutes)
            duree = str(nbreHeures) + "h" + str(nbreMinutes)
        else:
            duree = ""
        return duree




# --------------- FRAME DE TEST ---------------------------------------------------------------------

class TestPlanning(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: TestPlanning.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.statusbar = self.CreateStatusBar(1, 0)
    
        panel = PanelPlanning(self)
        
        
        self.__set_properties()
        self.__do_layout()
        # end wxGlade
##        panel.DCplanning.update()

    def __set_properties(self):
        # begin wxGlade: TestPlanning.__set_properties
        self.SetTitle("Test de Planning")
        self.SetSize((700, 600))
        self.statusbar.SetStatusWidths([-1])
        # statusbar fields
        statusbar_fields = ["frame_2_statusbar"]
        for i in range(len(statusbar_fields)):
            self.statusbar.SetStatusText(statusbar_fields[i], i)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: TestPlanning.__do_layout
        self.Centre()
        
        # end wxGlade

# end of class TestPlanning



    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frameTest = TestPlanning(None, -1, "")
    app.SetTopWindow(frameTest)
    frameTest.Show()
    app.MainLoop()
