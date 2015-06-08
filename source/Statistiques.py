#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import GestionDB
import datetime
import time
import FonctionsPerso
import  wx.grid as gridlib
import calendar
import wx.lib.hyperlink as hl
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import os
import sys

try: import psyco; psyco.full()
except: pass

import Selection_periode

import matplotlib
matplotlib.interactive(False)
matplotlib.use('wxagg')
from numpy import arange, sqrt, array, asarray, ones, exp, convolve, linspace
try :
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas
    from matplotlib.pyplot import setp
    import matplotlib.dates as mdates
    import matplotlib.mlab as mlab
except Exception, err :
    print "Erreur d'import : ", Exception, err

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateEngEnDateDD(dateEng):
    """ Tranforme une date anglaise en datetime.date """
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DatetimeDateEnStr(date):
    """ Transforme un datetime.date en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = ("Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche")
    listeMois = (u"janvier", u"février", u"mars", u"avril", u"mai", u"juin", u"juillet", u"août", u"septembre", u"octobre", u"novembre", u"décembre")
    dateStr = listeJours[date.weekday()] + " " + str(date.day) + " " + listeMois[date.month-1] + " " + str(date.year)
    return dateStr





class PanelGraph(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        
        self.figure = Figure(figsize=(1, 1))
        self.canvas = Canvas(self, -1, self.figure)
        self.SetColor( (255,255,255) )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas,1,wx.EXPAND|wx.ALL, 0)
        self.SetSizer(sizer)
    
    def Save_image(self):
##        nomFichier = "Temp/testImage.png"
##        self.figure.savefig(nomFichier, dpi=None, facecolor='w', edgecolor='w',
##            orientation='portrait', papertype=None, format="png",
##            transparent=False)

        """ save figure image to file"""
        file_choices = "PNG (*.png)|*.png|" \
                       "PS (*.ps)|*.ps|" \
                       "EPS (*.eps)|*.eps|" \
                       "BMP (*.bmp)|*.bmp"
        
        standardPath = wx.StandardPaths.Get()
        save_destination = standardPath.GetDocumentsDir()

        dlg = wx.FileDialog(self, message=u"Enregistrer le graphe sous...",
                            defaultDir = save_destination, defaultFile="graphe.png",
                            wildcard=file_choices, style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path,dpi=300)
            if (path.find(save_destination) ==  0):
                path = path[len(save_destination)+1:]
            message = u"Le graphe a été sauvegardé avec succès dans le répertoire \n%s" % path
            dlg = wx.MessageDialog(self, message, u"Sauvegarde", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            
    def Save_image_temp(self):
        self.canvas.print_figure("Temp/grapheTemp.png",dpi=300)
    
    def Clipboard_image(self):
        self.canvas.Copy_to_Clipboard()
        message = u"Le graphe a été envoyé dans le presse-papiers."
        dlg = wx.MessageDialog(self, message, u"Presse-papiers", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
    def convertCouleur(self, RGB) :
        couleur = []
        for valeur in RGB :
            couleur.append(valeur/255.0)
        return couleur

    def SetColor(self, rgbtuple=None):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ).Get()
        clr = [c/255. for c in rgbtuple]
        self.figure.set_facecolor(clr)
        self.figure.set_edgecolor(clr)
        self.canvas.SetBackgroundColour(wx.Colour(*rgbtuple))

    def FormateHeure(self, valeur, mode=None):
        # Si mode == None : récupère la valeur du ctrl ctrl_modeHeure de la frame
        if mode == None : 
            modeTmp = self.GetGrandParent().ctrl_modeHeure.GetSelection()
            if modeTmp == 0 :
                mode = "normal"
            else:
                mode = "decimal"
        if valeur == None or valeur == "" and mode == "decimal" : return 0.00
        if valeur == None or valeur == "" and mode != "decimal" : return "0h00"
        hr, mn = valeur[1:].split(":")
        if mode == "decimal" :
            # Mode décimal
            minDecimal = int(mn)*100/60
            texte = "%s.%s" % (hr, minDecimal)
            resultat = float(texte)
        else:
            # Mode Heure
            if hr == "00" : hr = "0"
            resultat = u"%sh%s" % (hr, mn)
        return resultat
    
    def MAJ(self) :
        self.figure.clear()
        # Choisit le graph demandé
        numGraph = self.GetGrandParent().ctrl_choix_graph.GetSelection() + 1
        if numGraph == 1 : 
            self.GetGrandParent().ctrl_tableau.InitDonnees(mode_detail=0)
            self.CreateGraph1(afficheTableau=False, polaire=False)
        if numGraph == 2 : 
            self.GetGrandParent().ctrl_tableau.InitDonnees(mode_detail=0)
            self.CreateGraph1(afficheTableau=True, polaire=False)
        if numGraph == 3 : 
            self.GetGrandParent().ctrl_tableau.InitDonnees(mode_detail=0)
            self.CreateGraph1(afficheTableau=False, polaire=True)
        if numGraph == 4 : 
            self.GetGrandParent().ctrl_tableau.InitDonnees(mode_detail=0)
            self.CreateGraph3()
        if numGraph == 5 : 
            self.GetGrandParent().ctrl_tableau.InitDonnees(mode_detail=1)
            self.CreateGraph4(total=True)
        if numGraph == 6 : 
            self.GetGrandParent().ctrl_tableau.InitDonnees(mode_detail=1)
            self.CreateGraph4(total=False)
        if numGraph == 7 : 
            self.GetGrandParent().ctrl_tableau.InitDonnees(mode_detail=0)
            self.CreateGraph5()

        
    def CreateGraph1(self, afficheTableau=False, polaire=False) :
        """ Création des barres avec ou sans table de données """
        
        ctrlTableau = self.GetGrandParent().ctrl_tableau

        dictLignes = ctrlTableau.dictLignes
        dictColonnes = ctrlTableau.dictColonnes
        dictDetails = ctrlTableau.dictDetails
        dictCategories = ctrlTableau.dictCategories
        listePersonnes = ctrlTableau.listePersonnes
        listeCategories = ctrlTableau.listeCategories

        #-------------------------------------------------------------------------------------------------------
        #  PREPARATION DES DONNEES DU GRAPH
        
        data = []
        dataTableau = []
        colLabels = []
        rowLabels = []
        listeCouleurs = []
        
        for IDcategorie in listeCategories :
            # Labels des lignes du tableau
            nom_colonne = dictCategories[IDcategorie][0]
            rowLabels.append(nom_colonne)
            # liste des couleurs
            exec("couleur_colonne=" + dictCategories[IDcategorie][3])
            listeCouleurs.append(self.convertCouleur(couleur_colonne))
            
            dataTemp = []
            dataTableauTemp = []
            for nomPersonne, IDpersonne in listePersonnes :
                # Labels des colonnes
                if nomPersonne not in colLabels :
                    colLabels.append(nomPersonne)
                # Valeurs du graph
                valeursExists = False
                if dictLignes.has_key(IDpersonne) :
                    if dictLignes[IDpersonne].has_key("total") :
                        if dictLignes[IDpersonne]["total"].has_key(IDcategorie) :
                            heures = dictLignes[IDpersonne]["total"][IDcategorie]
                            dataTemp.append(self.FormateHeure(heures, "decimal"))
                            dataTableauTemp.append(self.FormateHeure(heures, None))
                            valeursExists = True
                if valeursExists == False :
                    dataTemp.append(0)
                    dataTableauTemp.append(self.FormateHeure("+00:00", None))
                
            data.append(dataTemp)
            dataTableau.append(dataTableauTemp)

        
        #-------------------------------------------------------------------------------------------------------
        #  CREATION DU GRAPH
        
        ax = self.figure.add_subplot(1, 1, 1, polar=polaire)
        
        # Création du graph
        rows = len(data)
        ind = arange(len(colLabels)) + 0.25  # the x locations for the groups
        cellText = []
        width = 0.5
        yoff = array([0.0] * len(colLabels)) 
        listeBarresLegende = []
        for row in xrange(rows):
            couleur = dictCategories[IDcategorie][3]
            dataTmp = []
            for valeur in data[row] :
                if valeur == 0 : valeur = 0.00001
                dataTmp.append(valeur)
            barres = ax.bar(ind, dataTmp, width, bottom=yoff, color=listeCouleurs[row])
            listeBarresLegende.append(barres[0])
            yoff = yoff + data[row]
            cellText.append(['%1.1f' % (x/1000.0) for x in yoff])

        # Création du tableau de valeurs sous le graph
        if afficheTableau == True :
            listeCouleurs.reverse()
            data.reverse()
            rowLabels.reverse()
##            colLabels2 = []
##            for colLabel in colLabels :
##                nomPersonne = colLabel.replace(" ", "\n")
##                colLabels2.append(nomPersonne)
            if len(data) > 0 :
                the_table = ax.table(cellText=dataTableau,
                                  rowLabels=rowLabels, 
                                  rowColours=listeCouleurs,
                                  colLabels=colLabels,
                                  loc='bottom')
                the_table.set_fontsize(8)
            listeCouleurs.reverse()
            rowLabels.reverse()
            ax.set_xticks([])
            labelsy = ax.get_yticklabels()
            if polaire == True :
                setp(labelsy, rotation=0, fontsize=8)
            # Espaces autour du graph
            self.figure.subplots_adjust(left=0.22, bottom=0.26, right=None, wspace=None, hspace=None)
        else:
            ind = arange(len(colLabels)) 
            ax.set_xticks(ind + width) 
            if polaire == True :
                colLabels2 = []
                for colLabel in colLabels :
                    nomPersonne = colLabel.replace(" ", "\n")
                    colLabels2.append(nomPersonne)
                ax.set_xticklabels(colLabels2)
            else:
                ax.set_xticklabels(colLabels)
            labelsx = ax.get_xticklabels()
            labelsy = ax.get_yticklabels()
            if polaire == True :
                setp(labelsx, rotation=0, fontsize=9)
                setp(labelsy, rotation=0, fontsize=8)
            else:
                setp(labelsx, rotation=45, fontsize=9, horizontalalignment='right')
            if polaire == False :
                # Espaces autour du graph
                self.figure.subplots_adjust(left=0.125, bottom=0.22, right=None, wspace=None, hspace=None)
            else:
                self.figure.subplots_adjust(left=0.1, bottom=0.1, right=None, wspace=None, hspace=None)
        # Légende, titre et axes
        if polaire == False :
            ax.set_ylabel("Heures")
            labels = ax.get_yticklabels()
            setp(labels, rotation=0, fontsize=9) 
            titreGraph = u"Répartition des heures par personne et par catégorie"
##            ax.set_title(titreGraph)
        else:
            titreGraph = u"Répartition des heures par\npersonne et par catégorie"
##            self.figure.suptitle(titreGraph, fontsize=13, x=0.09, y=0.94, horizontalalignment = 'left')

        # Légende
        if polaire == True :
            localisationLegende = (1.2, 0.2)
        else:
            localisationLegende = "best"
        if len(data) != 0 :
            listeBarresLegende.reverse()
            rowLabels.reverse()
            legend = ax.legend( listeBarresLegende, rowLabels, loc=localisationLegende, labelspacing=0.1, fancybox=True )
            setp(legend.get_texts(), fontsize='small')
##            legend.get_frame().set_alpha(0.5)
        
        # Affiche les grilles
        ax.grid(True)

        # Re-dessine le canvas
        ax.figure.canvas.draw()
        
    
    def CreateGraph3(self) :
        """ Création des camemberts """
        
        ctrlTableau = self.GetGrandParent().ctrl_tableau

        dictLignes = ctrlTableau.dictLignes
        dictColonnes = ctrlTableau.dictColonnes
        dictDetails = ctrlTableau.dictDetails
        dictCategories = ctrlTableau.dictCategories
        listePersonnes = ctrlTableau.listePersonnes
        listeCategories = ctrlTableau.listeCategories
        
        # Recherche les valeurs du quadrillage des subplots
        nbreGraphs = len(listePersonnes)
        if nbreGraphs == 2 : 
            quadrillageX = 1
            quadrillageY = 2
        else:
            racine = sqrt(nbreGraphs)
            if racine != int(racine) :
                quadrillageX = int(racine) + 1
                quadrillageY = quadrillageX
            else:
                quadrillageX = int(racine)
                quadrillageY = quadrillageX
            
        dictHeures = {}
        indexSubPlot = 1
        
        for nomPersonne, IDpersonne in listePersonnes :
            listeLabels = []
            listeHeures = []
            listeCouleurs = []
            if dictLignes.has_key(IDpersonne) :
                if dictLignes[IDpersonne].has_key("total") :
                    for IDcategorie, valeur in dictLignes[IDpersonne]["total"].iteritems() :
                        if IDcategorie != "total" :
                            labelCategorie = dictCategories[IDcategorie][0]
                            exec("couleur_categorie=" + dictCategories[IDcategorie][3])
                            listeCouleurs.append(self.convertCouleur(couleur_categorie))
                            listeLabels.append(labelCategorie)
                            listeHeures.append(self.FormateHeure(valeur, "decimal"))
        
            # Création du graphique
            ax = self.figure.add_subplot(quadrillageX, quadrillageY, indexSubPlot)
            cam = ax.pie(listeHeures, labels=listeLabels, colors=listeCouleurs, autopct='%1.1f%%', shadow=False)
            title = ax.set_title(u"%s" % nomPersonne, weight="bold", horizontalalignment = 'center', position=(0.5, 0.97))
            setp(title, rotation=0, fontsize=9)
            ax.set_aspect(1)
            labels, labelsPourcent = cam[1], cam[2]
            setp(labels, rotation=0, fontsize=8) 
            setp(labelsPourcent, rotation=0, fontsize=7) 
            
            # Espaces autour du graph
            self.figure.subplots_adjust(left=0.125, bottom=0.1, right=None, wspace=0.30, hspace=0.30)
        
            indexSubPlot += 1
            
        # Re-dessine le canvas
        self.figure.canvas.draw()
    
    
    
    def CreateGraph4(self, total=False) :
        ctrlTableau = self.GetGrandParent().ctrl_tableau
        dictDetails = ctrlTableau.dictDetails
        dictColonnes = ctrlTableau.dictColonnes
        dictCategories = ctrlTableau.dictCategories
        
        # Si aucune donnée :
        if len(dictDetails) == 0 :
            self.figure.canvas.draw()
            return
        
        ax = self.figure.add_subplot(111)
        years  = mdates.YearLocator()   # every year
        months = mdates.MonthLocator()  # every month
        yearsFmt = mdates.DateFormatter('%Y')
        
        listeDonnees = []
        listeDates = []
        listeHeures = []
            
        # Total des heures
        for dateStr, valeurs in dictDetails.iteritems() :
            date = DateEngEnDateDD(dateStr)
            nbreHeures = dictDetails[dateStr]["totalColonne"]
            listeDonnees.append( (date, self.FormateHeure(nbreHeures, "decimal") ) ) 
        listeDonnees.sort()
        
        for date, nbreHeures in listeDonnees :
            listeDates.append(date)
            listeHeures.append(nbreHeures)
        
        if total == True :
            
            ax.plot(listeDates, listeHeures, color='blue', label="Nbre d'heures total")
            
            # Moyenne
            def moving_average(x, n, type='simple'):
                """compute an n period moving average. type is 'simple' | 'exponential'"""
                x = asarray(x)
                if type=='simple':
                    weights = ones(n)
                else:
                    weights = exp(linspace(-1., 0., n))
                weights /= weights.sum()
                a =  convolve(x, weights, mode='full')[:len(x)]
                a[:n] = a[n]
                return a
            if len(listeHeures) > 20 :
                ma20 = moving_average(listeHeures, 20, type='simple')
                linema20, = ax.plot(listeDates, ma20, color='red', lw=2, label=u"Evolution moyenne")

        else :
            
            # Heures par catégorie
            for IDcategorie in dictColonnes.keys() :
                if IDcategorie != "total" :
                    listeDonneesTmp = []
                    for dateStr, valeurs in dictDetails.iteritems() :
                        if IDcategorie in valeurs.keys() :
                            date = DateEngEnDateDD(dateStr)
                            nbreHeures = dictDetails[dateStr][IDcategorie]
                            listeDonneesTmp.append( (date, self.FormateHeure(nbreHeures, "decimal") ) ) 
                    listeDonneesTmp.sort()
                    listeDatesTmp = []
                    listeHeuresTmp = []
                    for date, nbreHeures in listeDonneesTmp :
                        listeDatesTmp.append(date)
                        listeHeuresTmp.append(nbreHeures)
                    nomCategorie = dictCategories[IDcategorie][0]
                    couleurTxt = dictCategories[IDcategorie][3]
                    r, v, b = couleurTxt[1:-1].split(",")
                    couleurCategorie = self.convertCouleur( (int(r), int(v), int(b)) )
                    ax.plot(listeDatesTmp, listeHeuresTmp, color=couleurCategorie, lw=1.5, label=nomCategorie)
            
         # format the ticks
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(yearsFmt)
        ax.xaxis.set_minor_locator(months)

        datemin = datetime.date(min(listeDates).year, 1, 1)
        datemax = datetime.date(max(listeDates).year+1, 1, 1)
        ax.set_xlim(datemin, datemax)
        
        ax.set_ylabel("Heures")
        labels = ax.get_yticklabels()
        setp(labels, rotation=0, fontsize=9) 
            
        # Légende
        props = matplotlib.font_manager.FontProperties(size=10)
        leg = ax.legend(loc='best', shadow=False, fancybox=True, prop=props)
        leg.get_frame().set_alpha(0.5)

        ax.grid(True)

        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        self.figure.autofmt_xdate()

        # Re-dessine le canvas
        self.figure.canvas.draw()

    def CreateGraph5(self) :
        """ Barres 3D """
        pass
##        from mpl_toolkits.mplot3d import axes3d
##        from matplotlib import cm
##        import numpy as np
##        
##        ctrlTableau = self.GetGrandParent().ctrl_tableau
##        dictLignes = ctrlTableau.dictLignes
##        dictColonnes = ctrlTableau.dictColonnes
##        dictDetails = ctrlTableau.dictDetails
##        dictCategories = ctrlTableau.dictCategories
##        listePersonnes = ctrlTableau.listePersonnes
##        listeCategories = ctrlTableau.listeCategories
##        
##        ax = axes3d.Axes3D(self.figure)
##        indexX = 0.5
##        for IDcategorie in listeCategories :
##            
##            indexY = 1
##            Ytmp = []
##            Ztmp = []
##                
##            for nomPersonne, IDpersonne in listePersonnes :
##                # Recherche du total d'heures
##                if dictLignes.has_key(IDpersonne) :
##                    if dictLignes[IDpersonne]["total"].has_key(IDcategorie) :
##                        nbreHeures = self.FormateHeure(dictLignes[IDpersonne]["total"][IDcategorie], "decimal")
##                    else:
##                        nbreHeures = 0.0
##                else:
##                    nbreHeures = 0.0
##
##                Ytmp.append(indexY)
##                Ztmp.append(int(nbreHeures))
##                indexY += 1
##
##            xpos = np.array(Ytmp)
##            ypos = (np.zeros(len(Ytmp)) + 0.5) + indexX
##            zpos = np.zeros(len(xpos))
##            dx = np.zeros(len(xpos)) +0.5
##            dy = np.zeros(len(xpos)) +0.8
##            dz = np.array(Ztmp) + 0.001
##                        
##            # Recherche de la couleur
##            couleurTxt = dictCategories[IDcategorie][3]
##            r, v, b = couleurTxt[1:-1].split(",")
##            couleurCategorie = self.convertCouleur( (int(r), int(v), int(b)) )
##            
##            # Dessin des barres
##            ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=couleurCategorie)
##                
##            Ytmp.append(indexY)
##            indexX += 1
##
##        # Re-dessine le canvas
##        self.figure.canvas.draw()
     
       

class MyFrame(wx.Frame):
    def __init__(self, parent, listeDates=[], periode = None, listePersonnes=[]):
        wx.Frame.__init__(self, parent, -1, title=u"Statistiques", style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)
        
        self.parent = parent
        self.listeDates = listeDates
        self.periode = ("%d-01-01" % datetime.date.today().year, "%d-12-31" % datetime.date.today().year)
        self.listePersonnes = listePersonnes
        self.mode_affichage = 0
        
        self.panel = wx.Panel(self, -1)
        
        # StaticBox
        self.staticbox_mode = wx.StaticBox(self.panel, -1, u"Mode d'affichage")
        self.staticbox_periode = wx.StaticBox(self.panel, -1, u"Période")
        self.staticbox_options = wx.StaticBox(self.panel, -1, u"Options d'affichage")
        self.staticbox_personnes = wx.StaticBox(self.panel, -1, u"Personnes")
        self.staticbox_tableau = wx.StaticBox(self.panel, -1, u"Statistiques")
        
        # Mode d'affichage
        self.bouton_mode_tableau = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/32x32/Tableau.png", wx.BITMAP_TYPE_ANY))
        self.bouton_mode_graph = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/32x32/GraphNB.png", wx.BITMAP_TYPE_ANY))
        
        # Période
        self.radio_dates = wx.RadioButton(self.panel, -1, u"Dates sélectionnées", size=(300, -1), style = wx.RB_GROUP)
        self.radio_periode = wx.RadioButton(self.panel, -1, u"Une période :")
        date_debut, date_fin = self.periode
        self.hyperlink_periode = self.Build_Hyperlink_periode(date_debut, date_fin)
        
        if len(self.listeDates) > 0 :
            self.radio_dates.SetValue(True)
            if len(self.listeDates) == 1 :
                self.radio_dates.SetLabel(u"La date sélectionnée dans le planning")
            else:
                self.radio_dates.SetLabel(u"Les %d dates sélectionnées dans le planning" % len(self.listeDates))
            self.hyperlink_periode.Enable(False)
        else:
            self.radio_periode.SetValue(True)
            self.radio_dates.Enable(False)
            self.radio_dates.SetLabel(u"Aucune date disponible")
        
        # Options d'affichage
        
        # Choix graph
        self.label_choix_graph = wx.StaticText(self.panel, -1, u"Graphe :")
        self.ctrl_choix_graph = wx.Choice(self.panel, -1, size=(490, -1), choices = [
            u"1. Répartition des heures par personne et par catégorie (Histogramme)", 
            u"2. Répartition des heures par personne et par catégorie (Histogramme + tableau de données)", 
            u"3. Répartition des heures par personne et par catégorie (Histogramme polaire)", 
            u"4. Répartition des heures par personne et par catégorie (Secteurs)", 
            u"5. Evolution annuelle du total des heures des personnes sélectionnées (Courbes)", 
            u"6. Evolution annuelle des heures des personnes sélectionnées par catégorie (Courbes)", 
##            u"7. GraphTest", 
            ])
        self.ctrl_choix_graph.SetSelection(0)
        
        # Choix affichage détail
        self.label_detail = wx.StaticText(self.panel, -1, u"Détail :")
        self.ctrl_detail = wx.Choice(self.panel, -1, choices = [u"Aucun", u"Jour", u"Mois", u"Année"])
        self.ctrl_detail.SetSelection(0)
        
        # Choix Groupement
        self.label_groupement = wx.StaticText(self.panel, -1, u"Grouper par :")
        self.ctrl_groupement = wx.Choice(self.panel, -1, choices = [u"Personne", u"Jour"])
        self.ctrl_groupement.SetSelection(0)
        self.ctrl_groupement.Enable(False)
        
        # Choix affichage heure/décimal
        self.label_modeHeure = wx.StaticText(self.panel, -1, u"Mode minutes :")
        self.ctrl_modeHeure = wx.Choice(self.panel, -1, choices = [u"Normal", u"Décimal"])
        self.ctrl_modeHeure.SetSelection(0)
        
        # Personnes
        self.ctrl_personnes = listCtrl_Personnes(self.panel, listePersonnes=self.listePersonnes)
        self.ctrl_personnes.SetMinSize((20, 20)) 
        
        # Commandes listes personnes
        self.hyperlink_select_all = self.Build_Hyperlink_select_all()
        self.label_separation = wx.StaticText(self.panel, -1, u"|")
        self.hyperlink_deselect_all = self.Build_Hyperlink_deselect_all()
        self.hyperlink_presents = self.Build_Hyperlink_presents()
        
        # Tableau
        self.ctrl_tableau = Tableau(self.panel)
        self.ctrl_graph = PanelGraph(self.panel)
        self.ctrl_graph.Show(False)
        self.label_choix_graph.Show(False)
        self.ctrl_choix_graph.Show(False)
        
        # Boutons
        self.bouton_aide = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_excel= wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/BoutonsImages/Export_excel.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer_tableau = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/BoutonsImages/Imprimer_tableau.png", wx.BITMAP_TYPE_ANY))
        self.bouton_save_image = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/BoutonsImages/Enregistrer_graphe.png", wx.BITMAP_TYPE_ANY))
        self.bouton_clipboard_image = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/BoutonsImages/Clipboard_image.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer_image = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/BoutonsImages/Imprimer_graphe.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fermer = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
##        self.ctrl_tableau.InitTableau()
        
        # Binds
        self.Bind(wx.EVT_CHOICE, self.OnChoiceGroupement, self.ctrl_groupement )
        self.Bind(wx.EVT_CHOICE, self.OnChoiceDetail, self.ctrl_detail)
        self.Bind(wx.EVT_CHOICE, self.OnChoiceModeHeure, self.ctrl_modeHeure)
        self.Bind(wx.EVT_CHOICE, self.OnChoiceGraph, self.ctrl_choix_graph)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton, self.radio_dates)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton, self.radio_periode)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimerTableau, self.bouton_imprimer_tableau)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSaveImage, self.bouton_save_image)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonClipboardImage, self.bouton_clipboard_image)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimerImage, self.bouton_imprimer_image)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModeTableau, self.bouton_mode_tableau)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModeGraph, self.bouton_mode_graph)
        
        self.bouton_save_image.Show(False)
        self.bouton_clipboard_image.Show(False)
        self.bouton_imprimer_image.Show(False)
        self.grid_sizer_boutons.AddGrowableCol(2)
        self.grid_sizer_options.Layout()
        self.grid_sizer_boutons.Layout()
        
    def __set_properties(self):
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_fermer.SetToolTipString(u"Cliquez ici pour fermer")
        self.bouton_excel.SetToolTipString(u"Cliquez ici pour exporter les données des statistiques au format Excel")
        self.bouton_save_image.SetToolTipString(u"Cliquez ici pour enregistrer le graphe au format image")
        self.bouton_clipboard_image.SetToolTipString(u"Cliquez ici pour envoyer le graphe dans le presse-papiers")
        self.bouton_imprimer_image.SetToolTipString(u"Cliquez ici pour publier le graphe au format PDF")
        self.bouton_imprimer_tableau.SetToolTipString(u"Cliquez ici pour publier le tableau au format PDF")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        grid_sizer_gauche = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        grid_sizer_haut_gauche = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Mode d'affichage
        sizerStaticBox_mode = wx.StaticBoxSizer(self.staticbox_mode, wx.HORIZONTAL)
        sizerStaticBox_mode.Add(self.bouton_mode_tableau, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.BOTTOM, 5)
        sizerStaticBox_mode.Add(self.bouton_mode_graph, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_haut_gauche.Add(sizerStaticBox_mode, 1, wx.EXPAND|wx.ALL, 0)
                
        # Période
        sizerStaticBox_periode = wx.StaticBoxSizer(self.staticbox_periode, wx.VERTICAL)
        grid_sizer_periode1 = wx.FlexGridSizer(rows=1, cols=3, vgap=0, hgap=0)
        grid_sizer_periode1.Add(self.radio_dates, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizerStaticBox_periode.Add(grid_sizer_periode1, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_periode2 = wx.FlexGridSizer(rows=1, cols=3, vgap=0, hgap=0)
        grid_sizer_periode2.Add(self.radio_periode, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_periode2.Add(self.hyperlink_periode, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        sizerStaticBox_periode.Add(grid_sizer_periode2, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_haut_gauche.Add(sizerStaticBox_periode, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_haut_gauche.AddGrowableCol(1)
        grid_sizer_gauche.Add(grid_sizer_haut_gauche, 1, wx.EXPAND|wx.ALL, 0)
        
        # Options
        sizerStaticBox_options = wx.StaticBoxSizer(self.staticbox_options, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=15, vgap=5, hgap=5)
        
        grid_sizer_options.Add(self.label_choix_graph, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_options.Add(self.ctrl_choix_graph, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_options.Add(self.label_detail, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_options.Add(self.ctrl_detail, 1, wx.EXPAND|wx.ALL, 0)

        grid_sizer_options.Add(self.label_groupement, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
        grid_sizer_options.Add(self.ctrl_groupement, 1, wx.EXPAND|wx.ALL, 0)

        grid_sizer_options.Add(self.label_modeHeure, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)
        grid_sizer_options.Add(self.ctrl_modeHeure, 1, wx.EXPAND|wx.ALL, 0)
        self.grid_sizer_options = grid_sizer_options
        sizerStaticBox_options.Add(grid_sizer_options, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_gauche.Add(sizerStaticBox_options, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_haut.Add(grid_sizer_gauche, 1, wx.EXPAND|wx.ALL, 0)
        
                
        # Personnes
        sizerStaticBox_personnes = wx.StaticBoxSizer(self.staticbox_personnes, wx.VERTICAL)
        grid_sizer_personnes = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_personnes.Add(self.ctrl_personnes, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_commandes_liste = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=0)
        grid_sizer_commandes_liste.Add(self.hyperlink_select_all, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_commandes_liste.Add(self.label_separation, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_commandes_liste.Add(self.hyperlink_deselect_all, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_commandes_liste.Add( (5, 5), 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_commandes_liste.Add(self.hyperlink_presents, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_commandes_liste.AddGrowableCol(3)
        grid_sizer_personnes.Add(grid_sizer_commandes_liste, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_personnes.AddGrowableRow(0)
        grid_sizer_personnes.AddGrowableCol(0)
        sizerStaticBox_personnes.Add(grid_sizer_personnes, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_haut.Add(sizerStaticBox_personnes, 1, wx.EXPAND|wx.ALL, 0)
        
        grid_sizer_base.Add(grid_sizer_haut, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 10)
        
        # Tableau
        sizerStaticBox_tableau = wx.StaticBoxSizer(self.staticbox_tableau, wx.HORIZONTAL)
        grid_sizer_tableau = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_tableau.Add(self.ctrl_tableau, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_tableau.Add(self.ctrl_graph, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_tableau.AddGrowableRow(0)
        grid_sizer_tableau.AddGrowableCol(0)
        grid_sizer_tableau.AddGrowableRow(1)
        self.grid_sizer_tableau = grid_sizer_tableau
        sizerStaticBox_tableau.Add(grid_sizer_tableau, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(sizerStaticBox_tableau, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=8, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_excel, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer_tableau, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_save_image, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_clipboard_image, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer_image, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(5)
        
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        
        self.panel.SetSizer(grid_sizer_base)
        self.Layout()
        
        self.SetSize((970, 700))
        self.CentreOnScreen()
        
        self.grid_sizer_boutons = grid_sizer_boutons
        
        
    def Build_Hyperlink_periode(self, date_debut, date_fin) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        dateTemp = str(date_debut)
        labelDebut = str(dateTemp[8:10]) + "/" + str(dateTemp[5:7]) + "/" + str(dateTemp[:4])
        dateTemp = str(date_fin)
        labelFin = str(dateTemp[8:10]) + "/" + str(dateTemp[5:7]) + "/" + str(dateTemp[:4])
        textePeriode = "Du " + labelDebut + " au " + labelFin
        hyper = hl.HyperLinkCtrl(self.panel, -1, textePeriode, URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink_periode)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLUE", "BLUE", "RED")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(u"Cliquez ici pour sélectionner une autre période"))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink_periode(self, event):
        """ Sélectionner les personnes présentes sur une période donnée """
        dlg = Selection_periode.SelectionPeriode(self)  
        if dlg.ShowModal() == wx.ID_OK:
            date_min, date_max = dlg.GetDates()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        dateTemp = str(date_min)
        labelDebut = str(dateTemp[8:10]) + "/" + str(dateTemp[5:7]) + "/" + str(dateTemp[:4])
        dateTemp = str(date_max)
        labelFin = str(dateTemp[8:10]) + "/" + str(dateTemp[5:7]) + "/" + str(dateTemp[:4])
        textePeriode = "Du " + labelDebut + " au " + labelFin
        self.hyperlink_periode.SetLabel(textePeriode)
        self.periode = (date_min, date_max)
        self.MAJdonnees()

    def Build_Hyperlink_select_all(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self.panel, -1, u"Tout sélect.", URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink_select_all)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLUE", "BLUE", "RED")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(u"Cliquez ici pour sélectionner toutes les personnes de la liste"))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink_select_all(self, event):
        """ Sélectionner toutes les personnes de la liste """
        self.ctrl_personnes.SelectAll()

    def Build_Hyperlink_deselect_all(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self.panel, -1, u"Tout désélect.", URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink_deselect_all)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLUE", "BLUE", "RED")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(u"Cliquez ici pour désélectionner toutes les personnes de la liste"))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink_deselect_all(self, event):
        """ Désélectionner toutes les personnes de la liste """
        self.ctrl_personnes.DeselectAll()
        

    def Build_Hyperlink_presents(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self.panel, -1, u"Sélectionner les présents", URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink_presents)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLUE", "BLUE", "RED")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(u"Cliquez ici pour sélectionner uniquement les personnes présentes sur la période"))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink_presents(self, event):
        """ Désélectionner toutes les personnes présentes """
        self.ctrl_personnes.GetPresents()
        
    def OnBoutonModeTableau(self, event):
        if self.mode_affichage == 1 :
            self.bouton_mode_tableau.SetBitmapLabel(wx.Bitmap("Images/32x32/Tableau.png", wx.BITMAP_TYPE_ANY))
            self.bouton_mode_graph.SetBitmapLabel(wx.Bitmap("Images/32x32/GraphNB.png", wx.BITMAP_TYPE_ANY))
            self.mode_affichage = 0
            self.MAJdonnees()
            self.ctrl_tableau.Show(True)
            self.ctrl_graph.Show(False)
            self.grid_sizer_tableau.Layout()
            self.ActiveControles()
            
        
    def OnBoutonModeGraph(self, event):            
        if self.mode_affichage == 0 :
            self.bouton_mode_tableau.SetBitmapLabel(wx.Bitmap("Images/32x32/TableauNB.png", wx.BITMAP_TYPE_ANY))
            self.bouton_mode_graph.SetBitmapLabel(wx.Bitmap("Images/32x32/Graph.png", wx.BITMAP_TYPE_ANY))
            self.mode_affichage = 1
            self.MAJdonnees()
            self.ctrl_graph.Show(True)
            self.ctrl_tableau.Show(False)
            self.grid_sizer_tableau.Layout()
            self.ActiveControles()
            
            
    def OnChoiceGraph(self, event):
        self.MAJdonnees()
            
            
    def ActiveControles(self) :
        if self.mode_affichage == 0 :
            self.label_choix_graph.Show(False)
            self.ctrl_choix_graph.Show(False)
            self.label_detail.Show(True)
            self.ctrl_detail.Show(True)
            self.label_groupement.Show(True)
            self.ctrl_groupement.Show(True)
            self.label_modeHeure.Show(True)
            self.ctrl_modeHeure.Show(True)
            self.bouton_excel.Show(True)
            self.bouton_imprimer_tableau.Show(True)
            self.bouton_save_image.Show(False)
            self.bouton_clipboard_image.Show(False)
            self.bouton_imprimer_image.Show(False)

        else:
            self.label_choix_graph.Show(True)
            self.ctrl_choix_graph.Show(True)
            self.label_detail.Show(False)
            self.ctrl_detail.Show(False)
            self.label_groupement.Show(False)
            self.ctrl_groupement.Show(False)
            self.label_modeHeure.Show(False)
            self.ctrl_modeHeure.Show(False)
            self.bouton_excel.Show(False)
            self.bouton_imprimer_tableau.Show(False)
            self.bouton_save_image.Show(True)
            self.bouton_clipboard_image.Show(True)
            self.bouton_imprimer_image.Show(True)
        self.grid_sizer_options.Layout()
        self.grid_sizer_boutons.Layout()

        
    def OnChoiceDetail(self, event):
        mode_detail = self.ctrl_detail.GetSelection()
        if mode_detail == 0 :
            self.ctrl_groupement.SetSelection(0)
            self.ctrl_groupement.Enable(False)
            self.ctrl_groupement.SetSelection(0)
        else:
            self.ctrl_groupement.SetString(1, self.ctrl_detail.GetStringSelection()) 
            self.ctrl_groupement.Enable(True)
            if self.ctrl_groupement.GetSelection() == -1 :
                self.ctrl_groupement.SetSelection(1)
            
        self.MAJdonnees()

    def OnChoiceGroupement(self, event):
        self.MAJdonnees()
        
    def OnChoiceModeHeure(self, event):
        self.MAJdonnees()
        
    def OnRadioButton(self, event):
        if self.radio_dates.GetValue() == 0 :
            self.hyperlink_periode.Enable(True)
        else:
            self.hyperlink_periode.Enable(False)
        self.MAJdonnees()
        
        
        
    def GetListePersonnes(self):
        DB = GestionDB.DB()
        req = "SELECT IDpersonne, nom, prenom FROM personnes ORDER BY nom, prenom;"
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listePersonnes = []
        dictPersonnes = {}
        if len(listeDonnees) != 0 : 
            index = 0
            for IDpersonne, nom, prenom in listeDonnees :
                listePersonnes.append( (u"%s %s" % (nom, prenom)) )
                dictPersonnes[index] = (IDpersonne, nom, prenom)
                index += 1
        return listePersonnes, dictPersonnes
                
    def SetDatePicker(self, controle, date) :
        """ Met une date au format datetime dans un datePicker donné """
        annee = int(date.year)
        mois = int(date.month)-1
        jour = int(date.day)
        date = wx.DateTime()
        date.Set(jour, mois, annee)
        controle.SetValue(date)
        
    def GetDatePickerValue(self, controle):
        """ Renvoie la date au format datetime d'un datePicker """
        date_tmp = controle.GetValue()
        return datetime.date(date_tmp.GetYear(), date_tmp.GetMonth()+1, date_tmp.GetDay())
    
    def GetDatesPeriode(self):
        date_debut = self.GetDatePickerValue(self.ctrl_date_debut)
        date_fin = self.GetDatePickerValue(self.ctrl_date_fin)
        return date_debut, date_fin

    def GetIDpersonne(self):
        """ Renvoie l'IDpersonne de la liste des personnes """
        index = self.ctrl_personne.GetSelection()
        if index == -1 : return None
        IDpersonne = self.dictPersonnes[index][0]
        return IDpersonne

    def SetPersonne(self, IDpersonne=None):
        """ Sélectionne une personne à partir de son ID dans la liste des personnes """
        if IDpersonne == None : return
        for index, valeurs in self.dictPersonnes.iteritems() :
            ID = valeurs[0]
            if IDpersonne == ID :
                self.ctrl_personne.SetSelection(index)
    
    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(59)
    
    def TestGraph(self):
        # TEST DE GRAPHS
##        import matplotlib
##        import pylab      
        
##        import numpy as np
##        import matplotlib.pyplot as plt
        
        def convertCouleur(RGB) :
            couleur = []
            for valeur in RGB :
                couleur.append(valeur/255.0)
            return couleur
        
        # -----------------------------------------------------------------------------------------------------
        
        def CreationGraph() :
            # Création du graph
            rows = len(data)
            ind = arange(len(colLabels)) + 0.3  # the x locations for the groups
            cellText = []
            width = 0.5
            yoff = array([0.0] * len(colLabels)) 
            for row in xrange(rows):
                couleur = dictCategories[IDcategorie][3]
                ax.bar(ind, data[row], width, bottom=yoff, color=listeCouleurs[row])
                yoff = yoff + data[row]
    ##            cellText.append(['%1.1f' % (x/1000.0) for x in yoff])

            # Création du tableau de valeurs sous le graph
            if afficheTableau == True :
                listeCouleurs.reverse()
                data.reverse()
                the_table = ax.table(cellText=data,
                                  rowLabels=rowLabels, 
                                  rowColours=listeCouleurs,
                                  colLabels=colLabels,
                                  loc='bottom')
                ax.set_xticks([])
            else:
                ind = arange(len(colLabels)) 
                ax.set_xticks(ind + width) 
                ax.set_xticklabels(colLabels)
                labels = ax.get_xticklabels()
                plt.setp(labels, rotation=45, fontsize=9, horizontalalignment='right')
            
            # Légende, titre et axes
            ax.set_ylabel("Heures")
            labels = ax.get_yticklabels()
            plt.setp(labels, rotation=0, fontsize=9)        
            ax.set_title(titreGraph)
        
        # -----------------------------------------------------------------------------------------------------
        
        dictLignes = self.ctrl_tableau.dictLignes
        dictColonnes = self.ctrl_tableau.dictColonnes
        dictDetails = self.ctrl_tableau.dictDetails
        dictCategories = self.ctrl_tableau.dictCategories
        listePersonnes = self.ctrl_tableau.listePersonnes
        listeCategories = self.ctrl_tableau.listeCategories
        
##        print dictLignes
##        print listePersonnes
##        print dictDetails
##        print "----------------------------------------------------------------------------------------"
        
        afficheTableau = False

        #-------------------------------------------------------------------------------------------------------
        #  PREPARATION DES DONNEES DU GRAPH
        
        data = []
        colLabels = []
        rowLabels = []
        listeCouleurs = []
        nbreGraphs = 1
        
        # Mode : Sans détail
        if self.ctrl_detail.GetSelection() == 0 :
                
            for IDcategorie in listeCategories :
                # Labels des lignes du tableau
                nom_colonne = dictCategories[IDcategorie][0]
                rowLabels.append(nom_colonne)
                # liste des couleurs
##                exec("couleur_colonne=" + dictCategories[IDcategorie][3])
                couleur_colonne= (255, 0, 0)
                listeCouleurs.append(convertCouleur(couleur_colonne))
                
                dataTemp = []
                for nomPersonne, IDpersonne in listePersonnes :
                    # Labels des colonnes
                    if nomPersonne not in colLabels :
                        colLabels.append(nomPersonne)
                    # Valeurs du graph
                    valeursExists = False
                    if dictLignes.has_key(IDpersonne) :
                        if dictLignes[IDpersonne].has_key("total") :
                            if dictLignes[IDpersonne]["total"].has_key(IDcategorie) :
                                heures = dictLignes[IDpersonne]["total"][IDcategorie]
                                dataTemp.append(self.FormateHeure(heures, "decimal"))
                                valeursExists = True
                    if valeursExists == False :
                        dataTemp.append(0)
                    
                data.append(dataTemp)
            
            titreGraph = u"Répartition des heures par personne et par catégorie"
            
        
        # Mode : Avec détail et Groupement par période :
        if self.ctrl_detail.GetSelection() > 0 and self.ctrl_groupement.GetSelection() == 0 :
            
            listeGroupes = dictDetails.keys()
            nbreGraphs = len(listeGroupes)
            
            # Recherche les valeurs du quadrillage des subplots
            racine = sqrt(nbreGraphs)
            if racine != int(racine) :
                valQuadrillage = int(racine) + 1
            else:
                valQuadrillage = int(racine)
            
            # Création du graph
            fig = plt.figure()
            
            index = 1
            for codeGroupe in listeGroupes :
                
                for IDcategorie in listeCategories :
                    # Labels des lignes du tableau
                    nom_colonne = dictCategories[IDcategorie][0]
                    rowLabels.append(nom_colonne)
                    # liste des couleurs
    ##                exec("couleur_colonne=" + dictCategories[IDcategorie][3])
                    couleur_colonne= (255, 0, 0)
                    listeCouleurs.append(convertCouleur(couleur_colonne))
                    
                    dataTemp = []
                    for nomPersonne, IDpersonne in listePersonnes :
                        # Labels des colonnes
                        if nomPersonne not in colLabels :
                            colLabels.append(nomPersonne)
                        # Valeurs du graph
                        valeursExists = False
                        if dictLignes.has_key(IDpersonne) :
                            if dictLignes[IDpersonne].has_key(codeGroupe) :
                                if dictLignes[IDpersonne][codeGroupe].has_key(IDcategorie) :
                                    heures = dictLignes[IDpersonne][codeGroupe][IDcategorie]
                                    dataTemp.append(self.FormateHeure(heures, "decimal"))
                                    valeursExists = True
                        if valeursExists == False :
                            dataTemp.append(0)
                        
                    data.append(dataTemp)
                
                # Espaces autour du graph pour afficher le tableau correctement
                # fig.axes([0.3, 0.25, 0.6, 0.65]) 
                
                ax = fig.add_subplot(valQuadrillage, valQuadrillage, index)
                titreGraph = codeGroupe
                self.CreationSubGraph()
                
                index += 1
        
        
        #-------------------------------------------------------------------------------------------------------
        #  CREATION DU GRAPH
        
##        # Recherche les valeurs du quadrillage des subplots
##        racine = np.sqrt(nbreGraphs)
##        if racine != int(racine) :
##            valQuadrillage = int(racine) + 1
##        else:
##            valQuadrillage = int(racine)
##        
##        # Création du graph
##        fig = plt.figure()
##        
##        # Espaces autour du graph pour afficher le tableau correctement
##        # fig.axes([0.3, 0.25, 0.6, 0.65]) 
##        for index in range(1, nbreGraphs+1) :
##            ax = fig.add_subplot(valQuadrillage, valQuadrillage, index)
##            CreationGraph()

        plt.show()


    def OnBoutonFermer(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    def OnBoutonExcel(self, event):
        if "linux" in sys.platform :
            dlg = wx.MessageDialog(self, u"Désolé, cette fonction n'est pas disponible sous Linux.", u"Fonction indisponible", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.ExportExcel()
    
    def OnBoutonSaveImage(self, event):
        self.ctrl_graph.Save_image()

    def OnBoutonClipboardImage(self, event):
        self.ctrl_graph.Clipboard_image()

    def OnBoutonImprimerImage(self, event):
        # Enregistrement de l'image dans repertoire Temp
        self.ctrl_graph.Save_image_temp()
        # Création du PDF
        from reportlab.pdfgen import canvas as canvasPDF
        from reportlab.lib.pagesizes import A4
        hauteur, largeur = A4
        cheminFichier = "Temp/grapheTemp.pdf"
        if "win" in sys.platform : cheminFichier = cheminFichier.replace("/", "\\")
        c = canvasPDF.Canvas(cheminFichier, pagesize=(largeur, hauteur), pageCompression = 1)
        img = c.drawImage("Temp/grapheTemp.png", 0, 0, width=largeur, height=hauteur, preserveAspectRatio=True)
        c.save()
        FonctionsPerso.LanceFichierExterne(cheminFichier)

    def OnBoutonImprimerTableau(self, event):
        """ Impression tableau de données """
        avecCouleurs = True
        
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        hauteur, largeur = A4
                
        # Initialisation du PDF
        nomDoc = "Temp/tableauStatsTemp.pdf"
        if "win" in sys.platform : nomDoc = nomDoc.replace("/", "\\")
        tailleMarge = 40
        doc = SimpleDocTemplate(nomDoc, pagesize=(largeur, hauteur), leftMargin=tailleMarge, rightMargin=tailleMarge, topMargin=tailleMarge, bottomMargin=tailleMarge, )
        story = []
        
        # Récupération des données du tableau
        tableau = self.ctrl_tableau
        nbreColonnes = tableau.GetNumberCols()
        nbreLignes = tableau.GetNumberRows()
        
        # Initialisation du tableau
        dataTableau = []
        listeCouleurs = []
        
        # Création des colonnes
        largeursColonnes = []
        largeurColonne = 55
        largeurColonneLabel = 140
        for col in range(0, nbreColonnes) :
            if col == 0 : largeursColonnes.append(largeurColonneLabel)
            else: largeursColonnes.append(largeurColonne)
        
        listeStyles = [
                            ('GRID', (0,0), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
                            ('VALIGN', (0, 0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                            ('ALIGN', (0, 0), (-1, 0), 'CENTRE'), # Centre les labels de colonne
                            ('ALIGN', (1, 1), (-1,- 1), 'RIGHT'), # Valeurs à gauche
                            ('ALIGN', (0, 1), (0, -1), 'CENTRE'), # Colonne Label Ligne centrée
                            ('FONT',(0, 0),(-1,-1), "Helvetica", 8), # Donne la police de caract. + taille de police de la ligne de total
                            ]
                            
        # Création des lignes
        for numLigne in range(0, nbreLignes) :
            valeursLigne = []
            for numCol in range(0, nbreColonnes) :
                valeurCase = tableau.GetCellValue(numLigne, numCol)
                couleurCase = tableau.GetCellBackgroundColour(numLigne, numCol)
                if couleurCase != (255, 255, 255, 255) and avecCouleurs == True :
                    r, g, b = self.ConvertCouleur(couleurCase)
                    listeStyles.append( ('BACKGROUND', (numCol, numLigne), (numCol, numLigne), (r, g, b) ) )
                if numLigne == 0 :
                    valeurCase = valeurCase.replace(" ", "\n")
                valeursLigne.append(valeurCase)
            dataTableau.append(valeursLigne)
    
        # Style du tableau
        style = TableStyle(listeStyles)
        
        # Création du tableau
        tableau = Table(dataTableau, largeursColonnes,  hAlign='LEFT')
        tableau.setStyle(style)
        story.append(tableau)
        story.append(Spacer(0,20))
            
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)
        
    def ConvertCouleur(self, couleur):
        r, g, b = couleur
        return r/255.0, g/255.0, b/255.0
        
    def ExportExcel(self):
        """ Export de la liste au format Excel """
        
        # Demande à l'utilisateur le nom de fichier et le répertoire de destination
        nomFichier = "ExportExcel.xls"
        wildcard = "Fichier Excel (*.xls)|*.xls|" \
                        "All files (*.*)|*.*"
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        dlg = wx.FileDialog(
            self, message = u"Veuillez sélectionner le répertoire de destination et le nom du fichier", defaultDir=cheminDefaut, 
            defaultFile = nomFichier, 
            wildcard = wildcard, 
            style = wx.SAVE
            )
        dlg.SetFilterIndex(2)
        if dlg.ShowModal() == wx.ID_OK:
            cheminFichier = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # Le fichier de destination existe déjà :
        if os.path.isfile(cheminFichier) == True :
            dlg = wx.MessageDialog(None, u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?", "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            if dlg.ShowModal() == wx.ID_NO :
                return False
                dlg.Destroy()
            else:
                dlg.Destroy()
                
        # Export
        import pyExcelerator
        # Création d'un classeur
        wb = pyExcelerator.Workbook()
        # Création d'une feuille
        ws1 = wb.add_sheet("Statistiques")
        
        # Remplissage de la feuille
        tableau = self.ctrl_tableau
        nbreColonnes = tableau.GetNumberCols()
        nbreLignes = tableau.GetNumberRows()
        
        for numLigne in range(0, nbreLignes) :
            for numCol in range(0, nbreColonnes) :
                valeurCase = tableau.GetCellValue(numLigne, numCol)
                ws1.write(numLigne, numCol, valeurCase)
                ws1.col(numCol).width = 7000
                
        # Finalisation du fichier xls
        wb.save(cheminFichier)
        
        # Confirmation de création du fichier et demande d'ouverture directe dans Excel
        txtMessage = u"Le fichier Excel a été créé avec succès. Souhaitez-vous l'ouvrir dès maintenant ?"
        dlgConfirm = wx.MessageDialog(self, txtMessage, u"Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        else:
            FonctionsPerso.LanceFichierExterne(cheminFichier)

    def MAJdonnees(self):
        if self.mode_affichage == 0 :
            # MAJ tableau
            self.ctrl_tableau.MAJ()
        else:
            # MAJ graph
            self.ctrl_graph.MAJ()



class Tableau(gridlib.Grid): 
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent, -1, size=(200, 200), style=wx.WANTS_CHARS)
        self.parent = parent.GetParent()
        self.moveTo = None
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        
        # Importation des catégories de présences
        self.dictCategories = self.Importation_categories()
        
        # Création Grid
        self.CreateGrid(0, 0)
        
        # Init Tableau
        self.InitTableau()

    
    def MAJ(self):
        if self.GetNumberRows() > 0 : 
            # Suppression des lignes du tableau
            self.DeleteRows(0, self.GetNumberRows())
        if self.GetNumberCols() > 0 : 
            # Suppression des colonnes du tableau
            self.DeleteCols(0, self.GetNumberCols())
        self.ClearGrid()
        self.InitTableau()
        self.Refresh()

    def GetPresents(self):        
        DB = GestionDB.DB()
        if self.modePeriode == "dates" :
            listeDates = self.parent.listeDates
            if len(listeDates) == 1 : listeDates = "('%s')" % listeDates[0]
            else : listeDates = str(tuple(listeDates))
            req = """SELECT IDpersonne, COUNT(IDpresence) FROM presences WHERE date IN %s GROUP BY IDpersonne ORDER BY date;""" % listeDates
        else:
            date_debut, date_fin = self.parent.periode
            req = "SELECT IDpersonne, COUNT(IDpresence) FROM presences WHERE '%s'<=date AND date<='%s' GROUP BY IDpersonne ORDER BY date;" % (date_debut, date_fin)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listePresents = []
        for IDpersonne, nbrePresences in listeDonnees :
            listePresents.append(IDpersonne)
        listePresents.sort()
        return listePresents
        
    def GetPresences(self):        
        DB = GestionDB.DB()
        listePersonnes = []
        for nom, ID in self.listePersonnes :
            listePersonnes.append(ID)
        if len(listePersonnes) == 1 : listePersonnes = "(%d)" % listePersonnes[0]
        else : listePersonnes = str(tuple(listePersonnes))
        if self.modePeriode == "dates" :
            listeDates = tuple(self.parent.listeDates)
            if len(listeDates) == 1 : listeDates = "('%s')" % listeDates[0]
            else : listeDates = str(tuple(listeDates))
            req = "SELECT IDpresence, IDpersonne, IDcategorie, date, heure_debut, heure_fin FROM presences WHERE IDpersonne IN %s AND date IN %s ORDER BY date;" % (listePersonnes, listeDates)
        else:
            date_debut, date_fin = self.parent.periode
            req = "SELECT IDpresence, IDpersonne, IDcategorie, date, heure_debut, heure_fin FROM presences WHERE IDpersonne IN %s AND '%s'<=date AND date<='%s' ORDER BY date;" % (listePersonnes, date_debut, date_fin)
        DB.ExecuterReq(req)
        listePresences = DB.ResultatReq()
        DB.Close()
        
        dictPresences = {}
        listePersonnes = []
        listeCategories = []
        
        for IDpresence, IDpersonne, IDcategorie, date, heure_debut, heure_fin in listePresences :
            # liste des personnes présentes
            if IDpersonne not in listePersonnes : listePersonnes.append(IDpersonne)
            # liste des catégories
            if IDcategorie not in listeCategories : listeCategories.append(IDcategorie)
            # dict des présences
            listePresences = (IDpresence, IDcategorie, date, heure_debut, heure_fin)
            if dictPresences.has_key(IDpersonne) :
                dictPresences[IDpersonne].append(listePresences)
            else:
                dictPresences[IDpersonne] = [listePresences,]
        
        return listePersonnes, listeCategories, dictPresences
        

    def OperationHeures(self, heureA=None, heureB=None, operation="addition"):
        # Préparation heure A
        if heureA == None :
            totalMinutesA = 0
        else:
            signeA = heureA[0]
            hrA, mnA = heureA[1:].split(":")
            hrA, mnA = int(hrA), int(mnA)
            totalMinutesA = (hrA*60) + mnA
            if signeA == "-" : totalMinutesA = -totalMinutesA
        # Préparation heure B
        if heureB == None :
            totalMinutesB = 0
        else:
            signeB = heureB[0]
            hrB, mnB = heureB[1:].split(":")
            hrB, mnB = int(hrB), int(mnB)
            totalMinutesB = (hrB*60) + mnB
            if signeB == "-" : totalMinutesB = -totalMinutesB
        # Opération
        if operation == "addition" : totalMinutes = totalMinutesA + totalMinutesB
        if operation == "soustraction" : totalMinutes = totalMinutesA - totalMinutesB
        # Formatage du résultat
        if totalMinutes >= 0 :
            nbreHeures = totalMinutes/60
            nbreMinutes = totalMinutes-(nbreHeures*60)
        else:
            nbreHeures = -(-totalMinutes/60)
            nbreMinutes = -(totalMinutes-(nbreHeures*60))
        if len(str(nbreMinutes))==1 : nbreMinutes = str("0") + str(nbreMinutes)
        duree = str(nbreHeures) + ":" + str(nbreMinutes)
        if nbreHeures>=0 : duree = "+%s" % duree
        return duree
    
    def InitDonnees(self, mode_detail):
        # Récupération des dates ou périodes
        self.listeDates = self.parent.listeDates
        self.periode = self.parent.periode
        if self.parent.radio_dates.GetValue() == True :
            self.modePeriode = "dates"
        else:
            self.modePeriode = "periode"
        
        # Récupération des options
        self.mode_groupement = self.parent.ctrl_groupement.GetSelection()
        self.mode_heure = self.parent.ctrl_modeHeure.GetSelection()
        
        # Récupération de la liste des personnes
        self.listePersonnes = self.parent.ctrl_personnes.GetSelections()

        # Importation
        self.listePersonnesPresentes, self.listeCategories, dictPresences = self.GetPresences()

        # Création des lignes
        dictLignes = {}
        dictColonnes = {}
        dictDetails = {}
        dictColonnes["total"] = "+00:00"
        nbreLabelsDetails = 0
        
        for nomPersonne, IDpersonne in self.listePersonnes :
            
            dictLignes[IDpersonne] = {}
            dictLignes[IDpersonne]["labelsDetails"] = []
            
            if IDpersonne not in self.listePersonnesPresentes :
                # Si pas de présence pour la personne :
                dictLignes[IDpersonne]["total"] = {}
                dictLignes[IDpersonne]["total"]["total"] = "+00:00"
                    
            else :
            
                for IDpresence, IDcategorie, date, heure_debut, heure_fin in dictPresences[IDpersonne] :
                    
                    dateDD = DateEngEnDateDD(date)
                    duree = self.OperationHeures("+" + heure_fin, "+" + heure_debut, "soustraction")
                    
                    # Création de la ligne de groupe
                    codeLigne = "total"
                    if dictLignes[IDpersonne].has_key(codeLigne) == False :
                        dictLignes[IDpersonne][codeLigne] = {}
                        
                    if dictLignes[IDpersonne][codeLigne].has_key(IDcategorie) :
                        dictLignes[IDpersonne][codeLigne][IDcategorie] = self.OperationHeures(dictLignes[IDpersonne][codeLigne][IDcategorie], duree, "addition")
                    else:
                        dictLignes[IDpersonne][codeLigne][IDcategorie] = duree
                    
                    # Création du total de la ligne de total
                    if dictLignes[IDpersonne][codeLigne].has_key("total") == False :
                        dictLignes[IDpersonne][codeLigne]["total"] = duree
                    else:
                        dictLignes[IDpersonne][codeLigne]["total"] = self.OperationHeures(dictLignes[IDpersonne][codeLigne]["total"], duree, "addition")
                    
                    # Création des lignes de détail
                    if mode_detail == 1 : codeLigne = str(dateDD) # Détail par jour
                    if mode_detail == 2 : codeLigne = "%d-%02d" % (dateDD.year, dateDD.month) # Détail par mois
                    if mode_detail == 3 : codeLigne = str(dateDD.year) # Détail par année
                    if mode_detail > 0 :
                        if dictLignes[IDpersonne].has_key(codeLigne) == False :
                            dictLignes[IDpersonne][codeLigne] = {}
                        if dictLignes[IDpersonne][codeLigne].has_key(IDcategorie) :
                            dictLignes[IDpersonne][codeLigne][IDcategorie] = self.OperationHeures(dictLignes[IDpersonne][codeLigne][IDcategorie], duree, "addition")
                        else:
                            dictLignes[IDpersonne][codeLigne][IDcategorie] = duree
                        if codeLigne not in dictLignes[IDpersonne]["labelsDetails"] : 
                            dictLignes[IDpersonne]["labelsDetails"].append(codeLigne)
                            nbreLabelsDetails += 1
                    
                        # Création du total de la ligne de détail
                        if dictLignes[IDpersonne][codeLigne].has_key("total") == False :
                            dictLignes[IDpersonne][codeLigne]["total"] = duree
                        else:
                            dictLignes[IDpersonne][codeLigne]["total"] = self.OperationHeures(dictLignes[IDpersonne][codeLigne]["total"], duree, "addition")
                        
                        # Pour le groupement par détail :
                        if dictDetails.has_key(codeLigne) == False :
                            dictDetails[codeLigne] = {}
                            dictDetails[codeLigne]["listePersonnes"] = [IDpersonne,]
                            dictDetails[codeLigne]["totalColonne"] = duree
                        else:
                            if IDpersonne not in dictDetails[codeLigne]["listePersonnes"] :
                                dictDetails[codeLigne]["listePersonnes"].append(IDpersonne)
                            dictDetails[codeLigne]["totalColonne"] = self.OperationHeures(dictDetails[codeLigne]["totalColonne"], duree, "addition")
                        if dictDetails[codeLigne].has_key(IDcategorie) :
                            dictDetails[codeLigne][IDcategorie] = self.OperationHeures(dictDetails[codeLigne][IDcategorie], duree, "addition")
                        else:
                            dictDetails[codeLigne][IDcategorie] = duree
                            
                    # Création du total de la colonne
                    if dictColonnes.has_key(IDcategorie) == False :
                        dictColonnes[IDcategorie] = { "total" : duree }
                    else:
                        dictColonnes[IDcategorie]["total"] = self.OperationHeures(dictColonnes[IDcategorie]["total"], duree, "addition")
                    if dictColonnes.has_key("total") == False :
                        dictColonnes["total"] = duree
                    else:
                        dictColonnes["total"] = self.OperationHeures(dictColonnes["total"], duree, "addition")
        
        # Pour les graphs
        self.dictLignes = dictLignes
        self.dictColonnes = dictColonnes
        self.dictDetails = dictDetails
        self.dictColonnes = dictColonnes
        self.nbreLabelsDetails = nbreLabelsDetails

    
    def InitTableau(self):
        
        mode_detail = self.parent.ctrl_detail.GetSelection()
        self.InitDonnees(mode_detail)

        # Création de la grille
        if self.mode_groupement == 0 :
            # Mode personnes
            if mode_detail == 0 :
                if len(self.listePersonnes) != 0 :
                    nbreLignes =  self.nbreLabelsDetails + len(self.listePersonnes) + 2
                else:
                    nbreLignes = 2
            else:
                if len(self.listePersonnes) != 0 :
                    nbreLignes =  self.nbreLabelsDetails + (len(self.listePersonnes)*2) + 3
                else:
                    nbreLignes = 3
        else:
            # Mode global
            if mode_detail == 0 :
                nbreLignes =  2
            else:
                listeGroupes = self.dictDetails.keys()
                nbreDetailsGroupes = 0
                for codeDetail in listeGroupes :
                    nbreDetailsGroupes += len(self.dictDetails[codeDetail]["listePersonnes"])
                nbreLignes =  len(listeGroupes)*2 + nbreDetailsGroupes + 3
                
        nbreColonnes = len(self.listeCategories) + 2 

        if self.GetNumberRows() == 0 : 
            # Création des lignes du tableau
            self.AppendRows(nbreLignes)
        if self.GetNumberCols() == 0 : 
            # Création des colonnes du tableau
            self.AppendCols(nbreColonnes)
            
        self.SetColSize(0, 170)
        self.SetColLabelValue(0, "")
        self.SetColLabelValue(1, "")
        self.SetRowLabelSize(1)
        self.SetColLabelSize(1)
        for x in range(0, nbreColonnes):
            self.SetColLabelValue(x, "")
        for x in range(0, nbreLignes):
            self.SetRowLabelValue(x, "")

        # Remplissage des entetes de colonnes :
        index_col = 1
        for IDcategorie in self.listeCategories :
            nom_colonne = self.dictCategories[IDcategorie][0]
            couleur_colonne = self.dictCategories[IDcategorie][3]
            exec("couleur_colonne=" + couleur_colonne)
            self.SetCellBackgroundColour(0, index_col, couleur_colonne)
            self.SetCellValue(0, index_col, nom_colonne)
            self.SetReadOnly(0, index_col, True)
            self.SetCellAlignment(0, index_col, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.SetRowSize(0, 50)
            self.SetColSize(index_col, 75)
            renderer = gridlib.GridCellAutoWrapStringRenderer()
            self.SetCellRenderer(0, index_col, renderer)
            index_col += 1
            
        # Ajout de la colonne TOTAL
        self.SetCellValue(0, index_col, u"Total")
        self.SetReadOnly(0, index_col, True)
        self.SetCellAlignment(0, index_col, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.SetRowSize(0, 50)
        self.SetColSize(index_col, 75)
        
        # ---------------------------------------------------------------------------------------------------------------------
        
        
        # Remplissage des lignes
        
        couleur_police_groupe = (255, 255, 255)
        couleur_fond_groupe = "#C0C0C0"
        
        
        if self.mode_groupement == 0 :
                
            indexLigne = 1
            for nomPersonne, IDpersonne in self.listePersonnes :
                listeCodesDetails = self.dictLignes[IDpersonne]["labelsDetails"]
                
                if mode_detail == 0 :
                    
                    # >>>>>>  Pas de détail
                    
                    # Création de la ligne de groupe
                    self.SetCellValue(indexLigne, 0, nomPersonne)
                    self.SetCellAlignment(indexLigne, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                    self.SetReadOnly(indexLigne, 0, True)
                    self.SetRowSize(indexLigne, 30)
                    
                    # Remplissage des totaux de catégories pour chaque personne
                    indexColonne = 1
                    for IDcategorie in self.listeCategories :
                        self.SetCellAlignment(indexLigne, indexColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                        self.SetReadOnly(indexLigne, indexColonne, True)
                        self.SetRowSize(indexLigne, 30)
                        if self.dictLignes[IDpersonne]["total"].has_key(IDcategorie) :
                            duree = self.dictLignes[IDpersonne]["total"][IDcategorie]
                            self.SetCellValue(indexLigne, indexColonne, self.FormateHeure(duree))
                             
                        indexColonne += 1
                        
                    # Total de la ligne de groupe
                    self.SetCellValue(indexLigne, indexColonne, self.FormateHeure(self.dictLignes[IDpersonne]["total"]["total"]))
                    self.SetCellAlignment(indexLigne, indexColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                    self.SetReadOnly(indexLigne, indexColonne, True)
                    font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD)
                    self.SetCellFont(indexLigne, indexColonne, font)
                
                else:
                    
                    # >>>>>>  Avec détail
                    
                    # Création de la ligne de groupe
                    self.SetCellValue(indexLigne, 0, nomPersonne)
                    self.SetRowSize(indexLigne, 8)
                    self.SetCellAlignment(indexLigne, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                    self.SetCellBackgroundColour(indexLigne, 0, couleur_fond_groupe)
                    self.SetReadOnly(indexLigne, 0, True)
                    self.SetCellTextColour(indexLigne, 0, couleur_police_groupe)
                    font = wx.Font(7, wx.NORMAL, wx.NORMAL, wx.NORMAL)
                    self.SetCellFont(indexLigne, 0, font)            
                    for x in range(1, len(self.listeCategories)+2):
                        self.SetCellBackgroundColour(indexLigne, x, couleur_fond_groupe)
                        self.SetReadOnly(indexLigne, x, True)
                    
                    # Création de la ligne de total de groupe
                    indexLigneTotal = indexLigne + len(listeCodesDetails) + 1

                    self.SetCellValue(indexLigneTotal, 0, "Total")
                    self.SetCellAlignment(indexLigneTotal, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                    self.SetReadOnly(indexLigneTotal, 0, True)
                    self.SetRowSize(indexLigneTotal, 30)
                    
                    
                    # Remplissage des totaux de catégories pour chaque personne
                    indexColonne = 1
                    for IDcategorie in self.listeCategories :
                        self.SetCellAlignment(indexLigneTotal, indexColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                        self.SetReadOnly(indexLigneTotal, indexColonne, True)
                        self.SetRowSize(indexLigneTotal, 30)
                        font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD)
                        self.SetCellFont(indexLigneTotal, indexColonne, font) 
                        if self.dictLignes[IDpersonne]["total"].has_key(IDcategorie) :
                            duree = self.dictLignes[IDpersonne]["total"][IDcategorie]
                            self.SetCellValue(indexLigneTotal, indexColonne, self.FormateHeure(duree))      
                            
                        indexColonne += 1
                        
                    # Total de la ligne de groupe
                    self.SetCellValue(indexLigneTotal, indexColonne, self.FormateHeure(self.dictLignes[IDpersonne]["total"]["total"]))
                    self.SetCellAlignment(indexLigneTotal, indexColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                    self.SetReadOnly(indexLigneTotal, indexColonne, True)
                    font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD)
                    self.SetCellFont(indexLigneTotal, indexColonne, font) 
                
                # Création du détail
                if mode_detail > 0 :
                    indexLigne += 1
                    
                for codeLigne in listeCodesDetails :
                    
                    # Entete de ligne détail
                    self.SetCellValue(indexLigne, 0, self.FormateLabelDetail(codeLigne))
                    self.SetCellAlignment(indexLigne, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                    self.SetReadOnly(indexLigne, 0, True)
                    self.SetRowSize(indexLigne, 30)
                    
                    # Valeurs de chaque catégorie
                    indexColonne = 1
                    for IDcategorie in self.listeCategories :
                        self.SetCellAlignment(indexLigne, indexColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                        self.SetReadOnly(indexLigne, indexColonne, True)
                        self.SetRowSize(indexLigne, 30)
                        if self.dictLignes[IDpersonne].has_key(codeLigne) :
                             if self.dictLignes[IDpersonne][codeLigne].has_key(IDcategorie) :
                                duree = self.dictLignes[IDpersonne][codeLigne][IDcategorie]
                                self.SetCellValue(indexLigne, indexColonne, self.FormateHeure(duree))
                                
                        indexColonne += 1
                    
                    # Total de la ligne de groupe
                    self.SetCellValue(indexLigne, indexColonne, self.FormateHeure(self.dictLignes[IDpersonne][codeLigne]["total"]))
                    self.SetCellAlignment(indexLigne, indexColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                    self.SetReadOnly(indexLigne, indexColonne, True)
                    self.SetRowSize(indexLigne, 30)
                    font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD)
                    self.SetCellFont(indexLigne, indexColonne, font) 
                    
                    indexLigne += 1
                    
                indexLigne += 1
       
        else:
            
            # Test de groupement par détail : <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            listeDetails = self.dictDetails.keys()
            listeDetails.sort()
            
##            print "-------------------------------------------------------------------------------------"
##            print "listeDetails:", listeDetails
##            for codeDetail in listeDetails :
##                print "Code détail : ", codeDetail, " -> ", self.dictDetails[codeDetail]
##                listePersonnes = self.dictDetails[codeDetail]["listePersonnes"]
##                for IDpersonne in listePersonnes :
##                    print "    IDpersonne=", IDpersonne, "| donnees =", self.dictLignes[IDpersonne][codeDetail]
    ##                for IDcategorie in self.listeCategories :
    ##                    print self.dictLignes[IDpersonne][codeDetail][IDcategorie]
            
            indexLigne = 1
            for codeDetail in listeDetails :
                listePersonnes = self.dictDetails[codeDetail]["listePersonnes"]

                if mode_detail == 0 :
                    
                    # >>>>>>  Pas de détail
                    
                    # Création de la ligne de groupe
                    self.SetCellValue(indexLigne, 0, self.FormateLabelDetail(codeDetail))
                    self.SetCellAlignment(indexLigne, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                    self.SetReadOnly(indexLigne, 0, True)
                    self.SetRowSize(indexLigne, 30)
                    
                    # Remplissage des totaux de catégories pour chaque personne
                    indexColonne = 1
                    for IDcategorie in self.listeCategories :
                        self.SetCellAlignment(indexLigne, indexColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                        self.SetReadOnly(indexLigne, indexColonne, True)
                        self.SetRowSize(indexLigne, 30)
                        totalLigne = "+00:00"
                        if self.dictDetails[codeDetail].has_key(IDcategorie) :
                            duree = self.dictDetails[codeDetail][IDcategorie]
                            totalLigne = self.OperationHeures(totalLigne, duree, "addition")
                            self.SetCellValue(indexLigne, indexColonne, self.FormateHeure(duree))
                             
                        indexColonne += 1
                        
                    # Total de la ligne de groupe
                    self.SetCellValue(indexLigne, indexColonne, self.FormateHeure(totalLigne)) # self.dictLignes[IDpersonne]["total"]["total"])
                    self.SetCellAlignment(indexLigne, indexColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                    self.SetReadOnly(indexLigne, indexColonne, True)
                    font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD)
                    self.SetCellFont(indexLigne, indexColonne, font) 
                
                else:
                    
                    # >>>>>>  Avec détail
                    
                    # Création de la ligne de groupe
                    self.SetCellValue(indexLigne, 0, self.FormateLabelDetail(codeDetail))
                    self.SetRowSize(indexLigne, 8)
                    self.SetCellAlignment(indexLigne, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                    self.SetCellBackgroundColour(indexLigne, 0, couleur_fond_groupe)
                    self.SetReadOnly(indexLigne, 0, True)
                    self.SetCellTextColour(indexLigne, 0, couleur_police_groupe)
                    font = wx.Font(7, wx.NORMAL, wx.NORMAL, wx.NORMAL)
                    self.SetCellFont(indexLigne, 0, font)            
                    for x in range(1, len(self.listeCategories)+2):
                        self.SetCellBackgroundColour(indexLigne, x, couleur_fond_groupe)
                        self.SetReadOnly(indexLigne, x, True)
                    
                    # Création de la ligne de total de groupe
                    indexLigneTotal = indexLigne + len(listePersonnes) + 1
                    
                    self.SetCellValue(indexLigneTotal, 0, "Total")
                    self.SetCellAlignment(indexLigneTotal, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                    self.SetReadOnly(indexLigneTotal, 0, True)
                    self.SetRowSize(indexLigneTotal, 30)
                    
                    # Remplissage des totaux de catégories pour chaque personne
                    indexColonne = 1
                    totalLigne = "+00:00"
                    for IDcategorie in self.listeCategories :
                        self.SetCellAlignment(indexLigneTotal, indexColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                        self.SetReadOnly(indexLigneTotal, indexColonne, True)
                        self.SetRowSize(indexLigneTotal, 30)
                        font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD)
                        self.SetCellFont(indexLigneTotal, indexColonne, font)
                        if self.dictDetails[codeDetail].has_key(IDcategorie) :
                            duree = self.dictDetails[codeDetail][IDcategorie]
                            totalLigne = self.OperationHeures(totalLigne, duree, "addition")
                            self.SetCellValue(indexLigneTotal, indexColonne, self.FormateHeure(duree))      
                            
                        indexColonne += 1
                        
                    # Total de la ligne de groupe
                    self.SetCellValue(indexLigneTotal, indexColonne, self.FormateHeure(totalLigne)) 
                    self.SetCellAlignment(indexLigneTotal, indexColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                    self.SetReadOnly(indexLigneTotal, indexColonne, True)
                    font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD)
                    self.SetCellFont(indexLigneTotal, indexColonne, font) 
                    
                # Création du détail
                if mode_detail > 0 :
                    indexLigne += 1
                
                listeNomsPersonnes = []
                for IDpersonne in listePersonnes :
                    for nomPersonne, ID in self.listePersonnes :
                        if ID == IDpersonne :
                            listeNomsPersonnes.append( (nomPersonne, ID) )
                            break
                listeNomsPersonnes.sort()
                
                for nomPersonne, IDpersonne in listeNomsPersonnes :
                    
                    # Entete de ligne détail
                    self.SetCellValue(indexLigne, 0, nomPersonne)
                    self.SetCellAlignment(indexLigne, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                    self.SetReadOnly(indexLigne, 0, True)
                    self.SetRowSize(indexLigne, 30)
                    
                    # Valeurs de chaque catégorie
                    indexColonne = 1
                    for IDcategorie in self.listeCategories :
                        self.SetCellAlignment(indexLigne, indexColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                        self.SetReadOnly(indexLigne, indexColonne, True)
                        self.SetRowSize(indexLigne, 30)
                        if self.dictLignes[IDpersonne].has_key(codeDetail) :
                             if self.dictLignes[IDpersonne][codeDetail].has_key(IDcategorie) :
                                duree = self.dictLignes[IDpersonne][codeDetail][IDcategorie]
                                self.SetCellValue(indexLigne, indexColonne, self.FormateHeure(duree))

                        indexColonne += 1
                    
                    # Total de la ligne de groupe
                    self.SetCellValue(indexLigne, indexColonne, self.FormateHeure(self.dictLignes[IDpersonne][codeDetail]["total"]))
                    self.SetCellAlignment(indexLigne, indexColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                    self.SetReadOnly(indexLigne, indexColonne, True)
                    self.SetRowSize(indexLigne, 30)
                    font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD)
                    self.SetCellFont(indexLigne, indexColonne, font)
                    
                    indexLigne += 1
                    
                indexLigne += 1
                
                
                
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        
        
        # Création du total de chaque colonne
        
        # Création de la ligne de groupe
        if mode_detail == 0 :
            # >>>> Sans détail
            self.SetCellValue(indexLigne, 0, "Total")
            self.SetCellAlignment(indexLigne, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.SetReadOnly(indexLigne, 0, True)
            self.SetRowSize(indexLigne, 30)
        else:
            # >>>> Avec détail
            self.SetCellValue(indexLigne, 0, "Total")
            self.SetRowSize(indexLigne, 8)
            self.SetCellAlignment(indexLigne, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.SetCellBackgroundColour(indexLigne, 0, couleur_fond_groupe)
            self.SetReadOnly(indexLigne, 0, True)
            self.SetCellTextColour(indexLigne, 0, couleur_police_groupe)
            font = wx.Font(7, wx.NORMAL, wx.NORMAL, wx.NORMAL)
            self.SetCellFont(indexLigne, 0, font)
            for x in range(1, len(self.listeCategories)+2):
                self.SetCellBackgroundColour(indexLigne, x, couleur_fond_groupe)
                self.SetReadOnly(indexLigne, x, True)
            indexLigne += 1
        
        self.SetCellValue(indexLigne, 0, "Total")
        self.SetCellAlignment(indexLigne, 0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.SetReadOnly(indexLigne, 0, True)
        self.SetRowSize(indexLigne, 30)
            
        indexColonne = 1
        for IDcategorie in self.listeCategories :
            if self.dictColonnes.has_key(IDcategorie) :
                 if self.dictColonnes[IDcategorie].has_key("total") :
                    duree = self.dictColonnes[IDcategorie]["total"]
                    self.SetCellValue(indexLigne, indexColonne, self.FormateHeure(duree))
                    self.SetCellAlignment(indexLigne, indexColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                    self.SetReadOnly(indexLigne, indexColonne, True)
                    font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD)
                    self.SetCellFont(indexLigne, indexColonne, font)
            indexColonne += 1
        
        # Total de la ligne de groupe
        if self.dictColonnes.has_key("total") :
            self.SetCellValue(indexLigne, indexColonne, self.FormateHeure(self.dictColonnes["total"]))
            self.SetCellAlignment(indexLigne, indexColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
            self.SetReadOnly(indexLigne, indexColonne, True)
            self.SetRowSize(indexLigne, 30)
            font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD)
            self.SetCellFont(indexLigne, indexColonne, font)

          
        self.moveTo = (self.GetNumberRows()-1, self.GetNumberCols()-1)

            
    
    def FormateHeure(self, label):
        if label == None or label == "" : return ""
        signe = label[0]
        hr, mn = label[1:].split(":")
##        if hr == "00" and mn == "00" : return 
        if signe == "+" : 
            signe = ""
        else:
            signe = "- "
        if self.mode_heure == 0 :
            # Mode Heure
            texte = u"%s%sh%s" % (signe, hr, mn)
        else:
            # Mode décimal
            minDecimal = int(mn)*100/60
            texte = u"%s%s.%s" % (signe, hr, minDecimal)
        return texte
    
    def FormateLabelDetail(self, label):
        # Formate noms de mois :
        if len(label) == 6 or len(label) == 7 :
            numAnnee, numMois = label.split("-")
            listeMois = ("Janvier", u"Février", "Mars", "Avril", "Mai", "Juin", "Juillet", u"Août", "Septembre", "Octobre", "Novembre", u"Décembre")
            texte = u"%s %s" % (listeMois[int(numMois)-1], numAnnee)
            return texte
        
        # Formate noms de jours :
        elif len(label) == 10 :
            dateDD = DateEngEnDateDD(label)
            dateStrFr = DatetimeDateEnStr(dateDD)
            return dateStrFr
        
        else :
            # Année
            return label
        

    def OnIdle(self, event):
        if self.moveTo != None:
            nbLignes = self.GetNumberRows()
            nbCols = self.GetNumberCols()
            self.SetGridCursor(nbLignes-1, nbCols-1)
            #self.SetGridCursor(self.moveTo[0], self.moveTo[1])
            self.moveTo = None
        event.Skip()
        
    def Importation_categories(self):
        DB = GestionDB.DB()
        req = "SELECT IDcategorie, nom_categorie, IDcat_parent, ordre, couleur FROM cat_presences"
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : return {}
        dictCategories = {}
        for IDcategorie, nom_categorie, IDcat_parent, ordre, couleur in listeDonnees :
            dictCategories[IDcategorie] = (nom_categorie, IDcat_parent, ordre, couleur)
        return dictCategories

    
        
        














class listCtrl_Personnes(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent, listePersonnes=[]):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.LC_NO_HEADER)
        CheckListCtrlMixin.__init__(self)
        self.parent = parent
        
        self.dictPersonnes = self.Import_Personnes()
        self.listePersonnes = listePersonnes
        self.Remplissage()
        self.activeCheck = True
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

    def Remplissage(self):
        self.ClearAll()
        # Création des colonnes
        self.InsertColumn(0, "Personnes")

        # Remplissage avec les valeurs
        self.activeCheck = False
        for key, valeurs in self.dictPersonnes.iteritems():
                index = self.InsertStringItem(sys.maxint, valeurs[0] + " " + valeurs[1])
                self.SetItemData(index, key)
                # Sélection
                if key in self.listePersonnes :
                    self.CheckItem(index)
                    
        self.activeCheck = True
        # Ajustement tailles colonnes
        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)

        # Tri
        self.SortItems(self.columnSorter)
                
    def columnSorter(self, key1, key2):
        item1 = self.dictPersonnes[key1][0] + " " + self.dictPersonnes[key1][1]
        item2 = self.dictPersonnes[key2][0] + " " + self.dictPersonnes[key2][1]
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
        if self.activeCheck == False : return
        
        IDpersonne = self.GetItemData(index)
        if flag:
            if IDpersonne not in self.listePersonnes :
                self.listePersonnes.append(IDpersonne)            
        else:
            if IDpersonne in self.listePersonnes :
                self.listePersonnes.remove(IDpersonne)
        
        # MAJ du tableau
        self.GetGrandParent().MAJdonnees()

    def Import_Personnes(self):
        """ Importe les noms des personnes de la base """
        req = "SELECT IDpersonne, nom, prenom FROM personnes ORDER BY nom;"
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        # Transformation de la liste en dict
        dictPersonnes = {}
        for personne in listeDonnees :
            dictPersonnes[personne[0]] = [personne[1], personne[2]] # Nom, prénom
        return dictPersonnes

    def GetSelections(self):
        listeDonnees = []
        for IDpersonne in self.listePersonnes :
            nomPersonne = self.dictPersonnes[IDpersonne][0] + " " + self.dictPersonnes[IDpersonne][1]
            listeDonnees.append( (nomPersonne, IDpersonne) )
        listeDonnees.sort()
        return listeDonnees

    def SelectAll(self):
        self.listePersonnes = self.dictPersonnes.keys()
        self.Remplissage()
        self.GetGrandParent().MAJdonnees()

    def DeselectAll(self):
        self.listePersonnes = []
        self.Remplissage()
        self.GetGrandParent().MAJdonnees()
    
    def GetPresents(self):
        listePresents = self.GetGrandParent().ctrl_tableau.GetPresents()
        if len(listePresents) == 0 :
            texte = u"Aucune personne n'est présente pour la période donnée."
            dlg = wx.MessageDialog(self, texte, u"Sélection des présents", wx.OK|wx.ICON_INFORMATION)  
            dlg.ShowModal()
            dlg.Destroy()
        else:
            self.listePersonnes = listePresents
            self.Remplissage()
            self.GetGrandParent().MAJdonnees()
        
        

# -----------------------------------------------------------------------------------------------------------------------------------------------------------





if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
