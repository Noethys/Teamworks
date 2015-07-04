#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import os
import re
import urllib2
import time

from ObjectListView import ObjectListView, FastObjectListView, ColumnDefn, Filter, CTRL_Outils
from ObjectListView import EVT_CELL_EDIT_STARTING, EVT_CELL_EDIT_FINISHING


def DetectionChaines() :
    
##    for nomFichier in os.listdir(os.getcwd()) :
##        fichier = urllib2.urlopen("https://raw.githubusercontent.com/Noethys/Noethys/master/source/%s" % nomFichier, timeout=10)
##        texte = fichier.read()
##        fichier.close()    
##    return {}

    
    listeFichiers = os.listdir(os.getcwd())
    listeFichiersTrouves = []
    dictChaines = {}
    
    exp = re.compile(r"u\".*?\"")
    
    for nomFichier in listeFichiers :
    
            if nomFichier.endswith("py") and nomFichier.startswith("DATA_") == False and nomFichier not in ("CreateurMAJ.py", "CreateurANNONCES.py") :
                #print "%s..." % nomFichier
                
                # Ouverture du fichier
                fichier = open(nomFichier, "r")
                texte = "\n".join(fichier.readlines())
                fichier.close() 
                
                # Analyse du fichier
                listeChaines = re.findall(exp, texte)
                for chaine in listeChaines :      
                    chaine = chaine#[2:-1]
                                  
                    valide = False
                    for caract in "abceghijklmopqrtvwxyz" :
                        if caract in chaine.lower() :
                            valide = True
                    if len(chaine) <= 4 :
                        valide = False
                    if "Images/" in chaine :
                        valide = False
                    
                    if valide == True :
                        if dictChaines.has_key(chaine) == False :
                            dictChaines[chaine] = []
                        dictChaines[chaine].append(nomFichier)
                        
    print "Nbre chaines =", len(dictChaines)                     
    return dictChaines








class Track(object):
    def __init__(self, dictDonnees={}):
        self.chaine = dictDonnees["chaine"]
        self.traduction = dictDonnees["traduction"]
        self.listeFichiers = dictDonnees["listeFichiers"]
        self.nbreFichiers = len(self.listeFichiers)
        self.listeFichiersStr = ", ".join(self.listeFichiers)


class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        dictChaines = DetectionChaines() 
        
        # Regroupement des prestations par label
        listeListeView = []
        for chaine, listeFichiers in dictChaines.iteritems() :
            dictDonnees = {"chaine" : chaine, "traduction" : "", "listeFichiers" : listeFichiers}
            listeListeView.append(Track(dictDonnees))
        return listeListeView

    def InitObjectListView(self):
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        liste_Colonnes = [
            ColumnDefn(_(_(u"Texte")), "left", 200, "chaine", typeDonnee="texte", isEditable=False), 
            ColumnDefn(_(_(u"Traduction")), "left", 200, "traduction", typeDonnee="texte", isEditable=True), 
            ColumnDefn(_(_(u"Nbre Fichiers")), "left", 80, "nbreFichiers", typeDonnee="entier", isEditable=False), 
            ColumnDefn(_(_(u"Fichiers")), "left", 200, "listeFichiersStr", typeDonnee="texte", isEditable=False),
            ]
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)

        self.SetEmptyListMsg(_(_(u"Aucun texte")))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)

        self.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK # ObjectListView.CELLEDIT_DOUBLECLICK
       
    def MAJ(self):
        self.InitModel()
        self.InitObjectListView()
        self._ResizeSpaceFillingColumns() 
        self.CocheTout()

    def Selection(self):
        return self.GetSelectedObjects()
    
    def CocheTout(self, event=None):
        for track in self.donnees :
            self.Check(track)
            self.RefreshObject(track)
        
    def CocheRien(self, event=None):
        for track in self.donnees :
            self.Uncheck(track)
            self.RefreshObject(track)

    def GetTracksCoches(self):
        return self.GetCheckedObjects()
            
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """            
        # Création du menu contextuel
        menuPop = wx.Menu()
                
        # Tout sélectionner
        item = wx.MenuItem(menuPop, 20, _(_(u"Tout cocher")))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheTout, id=20)

        # Tout dé-sélectionner
        item = wx.MenuItem(menuPop, 30, _(_(u"Tout décocher")))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheRien, id=30)
        
        menuPop.AppendSeparator()
        
        # Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(_(u"Aperçu avant impression")))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Imprimer
        item = wx.MenuItem(menuPop, 50, _(_(u"Imprimer")))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Export Texte
        item = wx.MenuItem(menuPop, 600, _(_(u"Exporter au format Texte")))
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Export Excel
        item = wx.MenuItem(menuPop, 700, _(_(u"Exporter au format Excel")))
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Impression(self, mode="preview"):
        if self.donnees == None or len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, _(_(u"Il n'y a aucune donnée à imprimer !")), _(_(u"Erreur")), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(_(u"Liste des prestations")), intro="", total="", format="A", orientation=wx.LANDSCAPE)
        if mode == "preview" :
            prt.Preview()
        else:
            prt.Print()
        
    def Apercu(self, event):
        self.Impression("preview")

    def Imprimer(self, event):
        self.Impression("print")

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(_(u"Liste des prestations")))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(_(u"Liste des prestations")))


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ()
        self.bouton1 = wx.Button(panel, -1, "Go")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton1, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.Bind(wx.EVT_BUTTON, self.OnBouton1, self.bouton1)

    def OnBouton1(self, event):
        # Get chaines
        tracks = self.myOlv.GetTracksCoches() 
        
        dictFichiers = {}
        for track in tracks :
            for nomFichier in track.listeFichiers :
                if dictFichiers.has_key(nomFichier) == False :
                    dictFichiers[nomFichier] = []
                if track.chaine not in dictFichiers[nomFichier] :
                    dictFichiers[nomFichier].append(track.chaine)
        
        indexFichier = 0
        for nomFichier, listeChaines in dictFichiers.iteritems() :
            print "%d/%d  : %s..." % (indexFichier, len(dictFichiers), nomFichier)
                
            # Ouverture des fichiers
            fichier = open(nomFichier, "r")
            nouveauFichier = open("New/%s" % nomFichier, "w")
            
            for ligne in fichier :
                # Remplacement des chaines
                for chaine in listeChaines :
                    if chaine in ligne : 
                        nouvelleChaine = "_(%s)" % chaine
                        ligne = ligne.replace(chaine, nouvelleChaine)
                    
                # Ecriture du nouveau fichier
                nouveauFichier.write(ligne)
                                    
            # Clôture des fichiers
            fichier.close()
            nouveauFichier.close()
            
##            time.sleep(0.1) 
            
            indexFichier += 1
            
        print "fini !!!!!!!!!!!!!!!!!"



    def OnBouton2(self, event):
        # Get chaines
        tracks = self.myOlv.GetTracksCoches() 
        listeChaines = []
        for track in tracks :
            listeChaines.append(track.chaine)
        
        # Get fichiers
        listeFichiers = os.listdir(os.getcwd())
        indexFichier = 0
        for nomFichier in listeFichiers :
            if nomFichier.endswith("py") and nomFichier.startswith("DATA_") == False and nomFichier not in ("CreateurMAJ.py", "CreateurANNONCES.py") :
                print "%d/%d :  %s..." % (indexFichier, len(listeFichiers), nomFichier)
                
                # Ouverture des fichiers
                fichier = open(nomFichier, "r")
                nouveauFichier = open("New/%s" % nomFichier, "w")
                
                idx = None
                indexLigne = 0
                for ligne in fichier :
                    # Remplacement des chaines
                    
                    for chaine in listeChaines :
##                        chaine = chaine.decode("iso-8859-15")
##                        ligne = ligne.encode("iso-8859-15")

                        if chaine in ligne : 
                            nouvelleChaine = u"_(%s)" % chaine
                            ligne = ligne.replace(chaine, nouvelleChaine)
                    
                    # Ecriture du nouveau fichier
                    nouveauFichier.write(ligne)
                    
                    # Insertion de l'import
##                    if "Licence GNU GPL" in ligne :
##                        idx = indexLigne + 2
##                    
##                    if idx == indexLigne :
##                        nouveauFichier.write("from UTILS_Traduction import _\n")

                    indexLigne += 1
                    
                    
                # Clôture des fichiers
                fichier.close()
                nouveauFichier.close()
                
            indexFichier += 1
                
        print "fini !!!!!!!!!!!!!!!!!"



def AjoutImport():
    listeFichiers = os.listdir(os.getcwd() + "/New")
    indexFichier = 0
    for nomFichier in listeFichiers :
        if nomFichier.endswith("py") and nomFichier.startswith("DATA_") == False and nomFichier not in ("CreateurMAJ.py", "CreateurANNONCES.py") :
            print "%d/%d :  %s..." % (indexFichier, len(listeFichiers), nomFichier)
            
            # Ouverture des fichiers
            fichier = open("New/" + nomFichier, "r")
            nouveauFichier = open("New/New/%s" % nomFichier, "w")
            
            idx = None
            indexLigne = 0
            for ligne in fichier :
                nouveauFichier.write(ligne)
                
                # Insertion de l'import
                if "Licence GNU GPL" in ligne :
                    idx = indexLigne + 2
                
                if idx == indexLigne :
                    nouveauFichier.write("from UTILS_Traduction import _\n")

                indexLigne += 1
                
                
            # Clôture des fichiers
            fichier.close()
            nouveauFichier.close()
            
        indexFichier += 1
            
    print "fini !!!!!!!!!!!!!!!!!"

                    
    
if __name__ == '__main__':
##    AjoutImport() 
    
    app = wx.App(0)
    frame_1 = MyFrame(None)
    frame_1.SetSize((900, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
