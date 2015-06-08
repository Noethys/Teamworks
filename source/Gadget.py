#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import FonctionsPerso
import  wx.calendar
import GestionDB
import datetime
import Calendrier

class PanelGadget(wx.Panel):
    def __init__(self, parent, couleurFondPanel, index, size=wx.DefaultSize):
        # L'index est la position du gadget dans la listeGadgets
        wx.Panel.__init__(self, parent, -1, size=size, name="panel_gadget")
        index = int(index)
        self.index = index
        self.couleurFondPanel = couleurFondPanel
        
        # Données gadgets
        self.nomGadget = parent.listeGadgets[index][0]
        self.paramGadget = parent.listeGadgets[index][1]
        self.texteTitre = self.paramGadget["label"]

        # Paramètres Cadre Gadget
        self.espaceBord = 5
        self.coinArrondi = 5
        self.hauteurTitre = 17
        
        # Couleurs
        self.couleurFondDC = self.couleurFondPanel
        self.couleurFondCadre = (214, 223, 247)
        self.couleurFondTitre = (70, 70, 70)
        self.couleurBord = (70, 70, 70)
        self.couleurDegrade = (130, 190, 235)
        self.couleurTexteTitre = (255, 255, 255)
        
        # Importation du contenu
        self.GetContenu(self.nomGadget)

##        # Titre
##        titre = wx.StaticText(self, -1, self.paramGadget["label"])
##        font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD) 
##        titre.SetFont(font)
##        titre.SetBackgroundColour(self.couleurFondTitre)
##        titre.SetForegroundColour(self.couleurTexteTitre)
        
        # Boutons
        self.img_config = wx.StaticBitmap(self, -1, wx.Bitmap("Images/16x16/Gadget_config.png", wx.BITMAP_TYPE_ANY))
        self.img_fermer = wx.StaticBitmap(self, -1, wx.Bitmap("Images/16x16/Gadget_fermer.png", wx.BITMAP_TYPE_ANY))
        self.img_config.SetToolTipString(u"Cliquez ici pour accéder aux options de ce gadget")
        self.img_fermer.SetToolTipString(u"Cliquez ici pour fermer ce gadget")
        if self.paramGadget["config"] == False : self.img_config.Show(False)
        
        # Layout
        grid_sizer_titre = wx.FlexGridSizer(rows=1, cols=3, vgap=0, hgap=0)        
##        grid_sizer_titre.Add( titre, 1, wx.ALL|wx.EXPAND, 0)
        grid_sizer_titre.Add( (5, 5), 1, wx.ALL|wx.EXPAND, 0)
        grid_sizer_titre.Add( self.img_config , 1, wx.ALL|wx.EXPAND, 0)
        grid_sizer_titre.Add( self.img_fermer , 1, wx.ALL|wx.EXPAND, 0)
        grid_sizer_titre.AddGrowableCol(0)
        
        grid_sizer = wx.FlexGridSizer(rows=3, cols=3, vgap=0, hgap=0)
        
        grid_sizer.Add((5, 5), 0, 0, 0)
        grid_sizer.Add(grid_sizer_titre, 1, wx.EXPAND|wx.ALL, 5+2)
        grid_sizer.Add((5, 5), 0, 0, 0)

        grid_sizer.Add((5, 5), 0, 0, 0)
        grid_sizer.Add(self.contenu, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5+1)
        grid_sizer.Add((5, 5), 0, 0, 0)

        grid_sizer.Add((5, 5), 0, 0, 0)
        grid_sizer.Add((5, 5), 0, 0, 0)
        grid_sizer.Add((5, 5), 0, 0, 0)
        
        grid_sizer.AddGrowableRow(1)
        grid_sizer.AddGrowableCol(1)

        self.SetSizer(grid_sizer)
        grid_sizer.Fit(self)
        self.Layout()
        
        self.SetSize(size)
        
        # Bind
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.img_config.Bind(wx.EVT_LEFT_DOWN, self.OnConfigGadget)
        self.img_fermer.Bind(wx.EVT_LEFT_DOWN, self.OnFermerGadget)         
         
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

##        # Titre du groupe
##        dc.SetBrush(wx.Brush(self.couleurFondTitre))
##        dc.DrawRoundedRectangle(0+self.espaceBord, 0+self.espaceBord, largeurDC-(self.espaceBord*2), self.hauteurTitre, self.coinArrondi)
##        pen = wx.Pen(self.couleurFondTitre, 5)
##        pen.SetCap(wx.CAP_BUTT) # Enlève l'arrondi aux bouts de la ligne
##        dc.SetPen(pen)
##        dc.DrawLine(1+self.espaceBord, self.hauteurTitre+2, largeurDC-self.espaceBord-1, self.hauteurTitre+2)
        
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
        

    def OnSize(self, event):
        self.Refresh() 
        event.Skip()

    def OnEraseBackground(self, event):
        pass 
        
    def OnFermerGadget(self, event):
        dictParametres = { "affichage" : False }
        self.SaveConfig(dictParametres)
        self.GetParent().Fermer_Gadget(self.nomGadget)

    def OnConfigGadget(self, event):
        self.contenu.Config()
        #event.Skip()

    def SaveConfig(self, parametres={}):
        """ Sauvegarde la liste des gadgets dans le configUser.dat """

        # Enregistrement dans la listeGadgets du panel
        for key, valeur in parametres.iteritems() :
            self.GetParent().listeGadgets[self.index][1][key] = valeur
        
        # Sauvegarde de la listeGadgets dans la table Gadgets
        listeDonnees = []
        dictParametres = {}
        
        nomGadget = self.GetParent().listeGadgets[self.index][0]
        dictGadget = self.GetParent().listeGadgets[self.index][1]

        for key, valeur in dictGadget.iteritems() :
            # Paramètres de base
            if key == "label" : listeDonnees.append( ("label", valeur) )
            elif key == "taille" : listeDonnees.append( ("taille", str(valeur)) )
            elif key == "affichage" : listeDonnees.append( ("affichage", str(valeur)) )
            elif key == "ordre" : listeDonnees.append( ("ordre", valeur) )
            elif key == "config" : listeDonnees.append( ("config", str(valeur)) )
            else:
                # Autres paramètres :
                dictParametres[key] = valeur
        
        if len(dictParametres) > 0 :
            listeDonnees.append( ("parametres", str(dictParametres)) )
        
        # Initialisation de la connexion avec la Base de données
        DB = GestionDB.DB()
        DB.ReqMAJ("gadgets", listeDonnees, "nom", nomGadget, IDestChaine=True)
        DB.Close()
       

    def GetContenu(self, nomGadget) :
        """ Le contenu peut être un panel ou un controle """
        
        if nomGadget == "dossiers_incomplets" :
            self.contenu = Gadget_DossiersIncomplets(self)  # Dossiers incomplets
        
        if nomGadget == "horloge" : 
            self.contenu = Gadget_Horloge(self) # horloge
        
        if nomGadget == "notes" :
            self.contenu = Gadget_BlocNotes(self)  # Bloc-notes
      
        if nomGadget == "updater" :
            self.contenu = Gadget_Updater(self) # Updater

        if nomGadget == "calendrier" :
            self.contenu = Gadget_Calendrier(self) # Calendrier
        

        
# --------------------------------------------------------------------------------------------------------------

class Gadget_BlocNotes(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, name="panel_gadget_blocnotes")
        self.parent = parent
        dictParam = self.parent.paramGadget
        # Widgets
        if dictParam["multipages"] == True :
            style=wx.TE_MULTILINE|wx.NO_BORDER
        else:
            style=wx.TE_MULTILINE|wx.NO_BORDER|wx.TE_NO_VSCROLL
        self.texte = wx.TextCtrl(self, -1, dictParam["texte"], style = style)
        couleurFond = dictParam["couleur_fond"]
        self.texte.SetBackgroundColour(couleurFond)
        self.parent.couleurFondCadre = couleurFond
        couleurPolice = dictParam["couleur_police"]
        self.texte.SetForegroundColour(couleurPolice)
        font = wx.Font(dictParam["taillePolice"], dictParam["familyPolice"], dictParam["stylePolice"], dictParam["weightPolice"], False, dictParam["nomPolice"])
        self.texte.SetFont(font)
        # Layout
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.texte, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        # Bind
        self.texte.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        
        # Archive des paramètres : {"texte" : u"Hello !", "taillePolice" : 10, "familyPolice" : 74, "stylePolice" : 90, "weightPolice" : 90 , "nomPolice" : "Segoe Print", "multipages" : False, "couleur_fond" : (255, 255, 187), "couleur_police" : (255, 0, 0) }

    def OnKillFocus(self, event):
        """ Sauvegarde du texte """
        dictParametres = { "texte" : self.texte.GetValue() }
        self.parent.SaveConfig(dictParametres)

    def Config(self):
        import parametres_blocnotes
        frame_config = parametres_blocnotes.MyFrame(None)
        frame_config.Show()

# ----------------------------------------------------------------------------------------------------------------

class Gadget_DossiersIncomplets(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, name="panel_gadget_dossiersincomplets")
        self.parent = parent
        dictParam = self.parent.paramGadget
        
        # Import
        import Gadget_pb_personnes as pbPersonnes
                
        # Widgets
        self.tree = pbPersonnes.TreeCtrl(self)

        # Paramètres
        self.tree.couleurFond = dictParam["couleur_fond"]
        self.tree.couleurPersonne = dictParam["couleurPersonne"]
        self.tree.couleurType = dictParam["couleurType"]
        self.tree.couleurProbleme = dictParam["couleurProbleme"]
        self.tree.couleurTraits = dictParam["couleurTraits"]
        self.tree.expandPersonnes = dictParam["expandPersonnes"]
        self.tree.expandTypes = dictParam["expandTypes"]
        self.parent.couleurFondCadre = dictParam["couleur_fond"]
        
        self.tree.MAJ_treeCtrl()

        # Layout
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.tree, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
                
    def Config(self):
        import parametres_dossiers
        frame_config = parametres_dossiers.MyFrame(None)
        frame_config.Show()
                   

# ----------------------------------------------------------------------------------------------------------------


class Gadget_Horloge(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, name="panel_gadget_horloge")
        self.parent = parent
        dictParam = self.parent.paramGadget
        
        # Import
        import wx.lib.analogclock as clock
        
        # Données
        couleurFace = dictParam["couleur_face"]
        couleurFond = dictParam["couleur_fond"]
        
        # Widgets
        self.horloge = clock.AnalogClock(self, size=(160,160))
        self.horloge.SetBackgroundColour(couleurFond)
        self.parent.couleurFondCadre = couleurFond
        self.horloge.SetFaceFillColour(couleurFace)
        
        # Layout
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.horloge, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)

    def Config(self):
        import parametres_horloge
        frame_config = parametres_horloge.MyFrame(None)
        frame_config.Show()


# ----------------------------------------------------------------------------------------------------------------


class Gadget_Updater(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, name="panel_gadget_updater")
        self.parent = parent
        dictParam = self.parent.paramGadget
        couleurFondUpdater = (128, 221, 128)
        self.parent.couleurFondCadre = couleurFondUpdater
        
        # Widgets
        self.texte = wx.StaticText(self, -1, u"Une nouvelle version du logiciel est disponible !\n\nCliquez ci-dessous pour la télécharger et l'installer dès maintenant. Cette procédure est automatisée.")   
        self.SetBackgroundColour(couleurFondUpdater)
        
        self.bouton_telecharger = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Telecharger_L140.png", wx.BITMAP_TYPE_ANY), size=(-1, 60))
        self.bouton_telecharger.SetToolTipString(u"Cliquez ici pour télécharger et installer\nla nouvelle version de TeamWorks")
        
        #font = wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL) 
        #self.contenu.SetFont(font)
        
        # Layout
        self.sizer = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        self.sizer.Add(self.texte, 1, wx.EXPAND)
        self.sizer.Add(self.bouton_telecharger, 1, wx.EXPAND|wx.RIGHT, 5)
        self.sizer.AddGrowableRow(0)
        self.sizer.AddGrowableCol(0)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        
        # Bind
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTelecharger, self.bouton_telecharger)

    def Config(self):
        pass
    
    def OnBoutonTelecharger(self, event):
        topWindow = wx.GetApp().GetTopWindow()
        topWindow.MenuUpdater(None)
        
# ----------------------------------------------------------------------------------------------------------------------------

class Gadget_Calendrier(Calendrier.Panel):
    def __init__(self, parent, ID=-1):
        Calendrier.Panel.__init__(self, parent, ID, afficheBoutonAnnuel=False, afficheAujourdhui=False)
        self.parent = parent
        
        #dictParam = { "colFond" : (255, 255, 255), "colNormal" : (214, 223, 247), "colWE" : (198, 211, 249), "colSelect" : (255, 162, 0), "colSurvol" : (0, 0, 0), "colFontJours" : (0, 0, 0), "colVacs" : (255, 255, 187), "colFontPresents" : (255, 0, 0), "colFeries" : (180, 180, 180) }
        dictParam = self.GetParent().paramGadget
        
        # Couleur du fond
        self.calendrier.SetBackgroundColour(dictParam["colFond"])
        self.SetBackgroundColour(dictParam["colFond"])
        self.parent.couleurFondCadre = dictParam["colFond"]
        # Couleurs des éléments du calendrier
        self.calendrier.couleurFond = dictParam["colFond"]
        self.calendrier.couleurNormal = dictParam["colNormal"]
        self.calendrier.couleurWE = dictParam["colWE"]
        self.calendrier.couleurSelect = dictParam["colSelect"]
        self.calendrier.couleurSurvol = dictParam["colSurvol"]
        self.calendrier.couleurFontJours = dictParam["colFontJours"]
        self.calendrier.couleurVacances = dictParam["colVacs"]
        self.calendrier.couleurFontJoursAvecPresents = dictParam["colFontPresents"]
        self.calendrier.couleurFerie = dictParam["colFeries"]

    def Config(self):
        import parametres_calendrier
        frame_config = parametres_calendrier.MyFrame(None)
        frame_config.Show()
     

# ----------------------------------------------------------------------------------------------------------------------------


##class Gadget_CalendrierArchive(wx.Panel):
##    def __init__(self, parent):
##        wx.Panel.__init__(self, parent, -1, name="panel_gadget_calendrier")
##        self.parent = parent
##        dictParam = self.parent.paramGadget
##        
##        # Traduction du calendrier
##        import locale
##        self.locale = wx.Locale(wx.LANGUAGE_FRENCH)
##        locale.setlocale(locale.LC_ALL, 'FR')
##        
##        
##        dictParam = { "afficheVacs" : True, "colPoliceVacs" : (255, 255, 255), "colFondVacs" : (100, 50, 50), "colPoliceMois" : (100, 100, 100), "colFondMois" : (255, 50, 50), "colFondJours" : (0, 50, 200)   }
##        
##        # Widgets
##        self.calendrier = wx.calendar.CalendarCtrl(self, -1, wx.DateTime_Now(), style = wx.calendar.CAL_MONDAY_FIRST| wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION)
##
##        # Affichage des vacances
##        if dictParam["afficheVacs"] == True :
##            self.calendrier.EnableHolidayDisplay(True)
##            self.calendrier.SetHolidayColours(dictParam["colPoliceVacs"], dictParam["colFondVacs"]) 
##        
##            # Récupération des jours de vacances
##            DB = GestionDB.DB()        
##            req = """SELECT IDperiode, annee, nom, date_debut, date_fin
##            FROM periodes_vacances ORDER BY date_debut; """
##            DB.ExecuterReq(req)
##            listeJoursVacs = DB.ResultatReq()
##            DB.Close()
##            
##            self.calendrier.SetHoliday( 5 )
##        
##        # Application des couleurs
##        self.calendrier.SetHeaderColours(dictParam["colPoliceMois"], dictParam["colFondMois"])
##        self.calendrier.SetBackgroundColour(dictParam["colFondJours"])
##        
##        # Layout
##        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
##        self.sizer.Add(self.calendrier, 1, wx.EXPAND)
##        self.SetSizer(self.sizer)
##        self.SetAutoLayout(True)
##
##    def Config(self):
##        pass
        
# --------------------------------------------------------------------------------------------------------------------------------
        
        
class MyFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, title="", name="frm_gadgets", style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.panel = wx.Panel(self, -1)
                
        couleurFondPanel = wx.Colour(122, 161, 230)
        self.panel.SetBackgroundColour(couleurFondPanel)
               
        # Gadget
        self.panelGadget = PanelGadget(self.panel, couleurFondPanel, "dossiers_incomplets")
        
        # Layout
        sizer = wx.FlexGridSizer(rows=1, cols=3, vgap=0, hgap=0)
        sizer.Add( (20, 20) , 1, wx.ALL|wx.EXPAND, 0)
        sizer.Add( (20, 20) , 1, wx.ALL|wx.EXPAND, 0)
        sizer.Add( (20, 20) , 1, wx.ALL|wx.EXPAND, 0)
        sizer.Add( (20, 20) , 1, wx.ALL|wx.EXPAND, 0)
        
        sizer.Add( self.panelGadget, 1, wx.ALL|wx.EXPAND, 0 )
        
        sizer.Add( (20, 20) , 1, wx.ALL|wx.EXPAND, 0)
        sizer.Add( (20, 20) , 1, wx.ALL|wx.EXPAND, 0)
        sizer.AddGrowableRow(1)
        sizer.AddGrowableCol(1)
        self.panel.SetSizer(sizer)
        
        


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()