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

import  wx.html as  html
import  wx.lib.wxpTag   
import FonctionsPerso
import GestionDB
from Utils import UTILS_Config
from Utils import UTILS_Fichiers


# Liste des gadgets par défaut
LISTEGADGETSDEFAUT = [      ["dossiers_incomplets",  { "label" : _(u"Dossiers incomplets"), "taille" : (200, 200), "affichage" : True, "config" : False } ], 
                                                ["horloge", { "label" : _(u"Horloge"), "taille" : (200, 200), "affichage" : True, "config" : True, "couleur_face" : (214, 223, 247) } ],
                                                ["calendrier", { "label" : _(u"Calendrier"), "taille" : (200, 200), "affichage" : True, "config" : True } ],
                                                ["updater", { "label" : _(u"Mises à jour internet"), "taille" : (200, 200), "affichage" : True, "config" : False} ],
                                                ["notes", { "label" : _(u"Bloc-notes"), "taille" : (200, 200), "affichage" : True, "config" : True, "texte" : _(u"Hello !"), "taillePolice" : 10, "familyPolice" : 74, "stylePolice" : 90, "weightPolice" : 90 , "nomPolice" : "Segoe Print" } ],
                                                ] # nomGadget, dict de paramètres


def ImportListeGadgets():
    """ Récupération des données de la table GADGETS """
    DB = GestionDB.DB()
    req = "SELECT * FROM gadgets ORDER BY ordre;"
    DB.ExecuterReq(req)
    listeGadgetsTmp = DB.ResultatReq()
    DB.Close()
    # Formatage de la liste des gadgets
    listeGadgets = []
    for IDgadget, nom, label, description, taille, affichage, ordre, config, parametres in listeGadgetsTmp :
        dictTmp = {}
        dictTmp["nom"] = nom
        dictTmp["label"] = label
        dictTmp['taille'] = eval(taille)
        dictTmp['affichage'] = eval(affichage)
        dictTmp['ordre'] = ordre
        dictTmp['config'] = eval(config)
        if parametres != None and parametres != "" :
            # Rajout du dictionnaire de parametres
            dictTmpParam = eval(parametres)
            for key, valeur in dictTmpParam.items() :
                dictTmp[key] = valeur
        listeGadgets.append( [nom, dictTmp] )
    # Renvoie la liste
    return listeGadgets
            
def MajTableGadgets(nomGadget="", parametres={}):
    """ Enregistre les modifications de paramètres d'un gadget """
    listeDonnees = []
    dictParametres = {}
    
    for key, valeur in parametres.items() :
        # Paramètres de base
        if key == "label" : listeDonnees.append( ("label", valeur) )
        elif key == "taille" : listeDonnees.append( ("taille", str(valeur)) )
        elif key == "affichage" : listeDonnees.append( ("affichage", str(valeur)) )
        elif key == "ordre" : listeDonnees.append( ("ordre", valeur) )
        elif key == "config" : listeDonnees.append( ("config", str(valeur)) )
        else:
            # Autres paramètres :
            dictParametres[key] = valeur
        
    listeDonnees.append( ("parametres", str(list(dictParametres.values())[0])) )

    # Initialisation de la connexion avec la Base de données
    DB = GestionDB.DB()
    DB.ReqMAJ("gadgets", listeDonnees, "nom", nomGadget, IDestChaine=True)
    DB.Close()


            
class MyHtmlWindow(html.HtmlWindow):
    def __init__(self, parent, id, listeGadgets):
        html.HtmlWindow.__init__(self, parent, id, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
            
        self.couleur_fond = self.GetParent().couleur_fond
        self.listeGadgets = listeGadgets
        
##        # Création de la page
##        source = self.Source()
##        self.SetPage(source)
##        # Aligne tous les gagdets en haut
##        self.Alignement(c = self.GetInternalRepresentation())


    def OnLinkClicked(self, linkinfo):
        #self.log.WriteText('OnLinkClicked: %s\n' % linkinfo.GetHref())
        super(MyHtmlWindow, self).OnLinkClicked(linkinfo)

    def OnCellMouseHover(self, cell, x, y):
        #self.log.WriteText('OnCellMouseHover: %s, (%d %d)\n' % (cell, x, y))
        super(MyHtmlWindow, self).OnCellMouseHover(cell, x, y)

    def OnCellClicked(self, cell, x, y, evt):
        #self.log.WriteText('OnCellClicked: %s, (%d %d)\n' % (cell, x, y))
        if isinstance(cell, html.HtmlWordCell):
            sel = html.HtmlSelection()
            #self.log.WriteText('     %s\n' % cell.ConvertToText(sel))
        super(MyHtmlWindow, self).OnCellClicked(cell, x, y, evt)
                
    def Alignement(self, c):
        """ Aligne tout les gadgets en haut """
        while c:
            if isinstance(c, html.HtmlContainerCell):
                c.SetAlignVer(0) # Alignement ici
                self.Alignement(c.GetFirstChild())
            c = c.GetNext()
    
    def MAJ(self):
        # Création de la page
        source = self.Source()
        self.SetPage(source)
        # Aligne tous les gagdets en haut
        self.Alignement(c = self.GetInternalRepresentation())
        # Pour résoudre le bug d'alignement après MAJ
        self.SendSizeEvent()
        
    def Efface(self):
        """ Efface toute la page html """
        txt = "<html><head><title>Page accueil</title></head><body bgcolor='%s'></body></html>" % self.ConvertitCouleur(self.couleur_fond)
        self.SetPage(txt)
            
    def Source(self):
        """ Création de la source HTML """
        
        # Crée le HTML pour les gadgets
        txtGadgets = ""
        index = 0
        for nomGadget, parametres in self.listeGadgets :
            if parametres["affichage"] == True :
                txtGadgets += """
                <wxp module="Gadget" class="PanelGadget" width=%d height=%d >
                    <param name="couleurFondPanel" value="%s">
                    <param name="index" value="%d">
                </wxp> """ % (parametres["taille"][0], parametres["taille"][1], str(self.couleur_fond), index)
            index += 1
        
        # Crée le HTML pour la page complète
        txtSource = """
        <html>
        <head>
        <title>Page accueil</title>
        </head>
        <body bgcolor="%s">
        %s        
        </body></html>
        """ % (self.ConvertitCouleur(self.couleur_fond), txtGadgets)
        
        return txtSource
        
    def ConvertitCouleur(self, couleur):
        """ Convertit une couleur de format (0, 0, 0) au format #000000 """
        return "#%02X%02X%02X" % couleur

    def Fermer_Gadget(self, nomGadgetAFermer):
        """ Ferme un gadget """
        index = 0
        for nomGadget, parametres in self.listeGadgets :
            if nomGadget == nomGadgetAFermer : 
                self.listeGadgets[index][1]["affichage"] = False
            index += 1
        self.MAJ()

    def Ouvre_Gadget(self, nomGadgetAOuvrir):
        """ Ferme un gadget """
        index = 0
        for nomGadget, parametres in self.listeGadgets :
            if nomGadget == nomGadgetAOuvrir : 
                self.listeGadgets[index][1]["affichage"] = True
            index += 1
        self.MAJ()


class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, name="panel_accueil", style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.couleur_fond = (122, 161, 230)
        self.SetBackgroundColour(self.couleur_fond)
        
        # Récupère la liste des gadgets
        self.listeGadgets = self.GetListeGadgets()
        
        # Contrôles
        self.html = MyHtmlWindow(self, -1, self.listeGadgets)
        self.logo = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/Special/Logo_accueil.png"), wx.BITMAP_TYPE_ANY))
        
        # Layout
        grid_sizer_2 = wx.FlexGridSizer(rows=1, cols=2, vgap=0, hgap=0)
        grid_sizer_2.Add( (5, 5) , 1, wx.EXPAND, 0)
        grid_sizer_2.Add(self.logo, 1, wx.EXPAND, 0)
        grid_sizer_2.AddGrowableCol(0)
        
        grid_sizer_1 = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_1.Add(self.html, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(grid_sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_1.AddGrowableRow(0)
        grid_sizer_1.AddGrowableCol(0)
        self.SetSizer(grid_sizer_1)
        self.SetAutoLayout(True)
        
        # Bind
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, event):
        #self.Refresh() 
        event.Skip()
        
    def MAJ_Gadgets(self):
        self.Freeze()
        self.listeGadgets = self.GetListeGadgets()
        self.html.listeGadgets = self.listeGadgets
        self.html.MAJ()
        self.Thaw()

    def MAJpanel(self, listeElements=[]) :
        """ Met à jour les éléments du panel Accueil """
        # Elements possibles : [] pour tout
        if "exemple" in listeElements or listeElements==[] : 
            self.MAJ_Gadgets()
            

            
    def GetListeGadgets(self):
        """ Récupère la liste des gadgets """           
        listeGadgets = ImportListeGadgets()

        # Regarde quels gadgets sont à afficher : 
        
        # -> Affiche "les dossier incomplets" uniquement si un fichier est ouvert 
##        try :
##            topWindow = wx.GetApp().GetTopWindow()
##            nomWindow = topWindow.GetName()
##        except :
##            nomWindow = None
##        if nomWindow == "general" : 
##            nomFichierEnCours = topWindow.userConfig["nomFichier"]
##            if nomFichierEnCours == "" : 
##                affichage = False
##            else:
##                affichage = True
##            index = 0
##            for gadget in listeGadgets :
##                if gadget[0] == "dossiers_incomplets" : 
##                    listeGadgets[index][1]["affichage"] = affichage
##            index += 1
        
        
        # -> Affiche "L'updater" uniquement si une mise à jour existe existe sur internet 
        if self.GetGrandParent().MAJexiste == True :
            affichage = True
        else:
            affichage = False
        index = 0
        for gadget in listeGadgets :
            if gadget[0] == "updater" : 
                listeGadgets[index][1]["affichage"] = affichage
            index += 1        
        



        
        # Renvoie la liste des gadgets
        return listeGadgets








class AffichageGadgets():
    """ Boîte de dialogue d'affichage des gadgets pour barre de menus """
    def __init__(self, parent):
        
        """ Récupère la liste des gadgets dans la base de données """
        self.listeGadgets = ImportListeGadgets()
    
    def dialogue(self):
        listeNoms = []
        preSelection = []
        index = 0
        for nomGadget, parametres in self.listeGadgets :
            listeNoms.append(parametres["label"])
            if parametres["affichage"] == True : preSelection.append(index)
            index += 1
        
        # Boîte de dialogue
        message = _(u"Sélectionnez les gadgets que vous souhaitez afficher sur votre page d'accueil")
        dlg = wx.MultiChoiceDialog(None, message, _(u"Affichage des gadgets"), listeNoms, wx.CHOICEDLG_STYLE)
        # Coche ceux qui doivent être déjà sélectionnés dans la liste
        dlg.SetSelections(preSelection)
        # Résultats
        if dlg.ShowModal() == wx.ID_OK:
            resultats = dlg.GetSelections()
            
            # Enregistrement des sélections
            for index in range(len(self.listeGadgets)) :
                if index in resultats :
                    self.listeGadgets[index][1]["affichage"] = True
                else :
                    self.listeGadgets[index][1]["affichage"] = False
                index += 1
            
            # Sauvegarde dans le userConfig
            try :
                topWindow = wx.GetApp().GetTopWindow()
                nomWindow = topWindow.GetName()
            except :
                nomWindow = None
            if nomWindow == "general" : 
                # Si la frame 'General' est chargée, on y récupère le dict de config
                cfg = topWindow.userConfig
                cfg["listeGadgets"] = self.listeGadgets
            else:
                # Récupération du nom de la DB directement dans le fichier de config sur le disque dur
                cfg = UTILS_Config.FichierConfig(nomFichier=UTILS_Fichiers.GetRepUtilisateur("Config.dat"))
                cfg.SetItemConfig("listeGadgets", self.listeGadgets)
                
            # Fermeture
            dlg.Destroy()
            return True    
            
        else:
            dlg.Destroy()
            return False
        

class MyFrame(wx.Frame):
    """ Frame de test """
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, title="", name="frm_accueil", style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.panel =Panel(self)
        


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()