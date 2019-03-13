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
from Ctrl import CTRL_Bouton_image
import wx.lib.mixins.listctrl  as  listmix
import GestionDB
import datetime
import FonctionsPerso
from Dlg import DLG_Saisie_presence
from Ctrl import CTRL_Calendrier_tw
from Dlg import DLG_Application_modele
from Utils import UTILS_Adaptations



class Panel(wx.Panel):
    def __init__(self, parent, id=-1, IDpersonne=0):
        wx.Panel.__init__(self, parent, id, name="panel_pagePresences", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDpersonne = IDpersonne

        # Widgets
        self.staticBox_staticbox = wx.StaticBox(self, -1, _(u"Présences"))
        self.listCtrl = ListCtrl(self, IDpersonne=self.IDpersonne)
        self.listCtrl.SetMinSize((20, 20)) 
        
        self.barreRecherche = BarreRecherche(self)
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_stats = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Stats.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_modele = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calendrier3jours.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_recherche = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe_plus.png"), wx.BITMAP_TYPE_PNG))

        self.__set_properties()
        self.__do_layout()
        
        self.barreRecherche.Show(False)

    def __set_properties(self):

        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir une tâche")))
        self.bouton_ajouter.SetSize(self.bouton_ajouter.GetBestSize())
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la tâche sélectionnée")))
        self.bouton_modifier.SetSize(self.bouton_modifier.GetBestSize())
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la tâche sélectionnée")))
        self.bouton_supprimer.SetSize(self.bouton_supprimer.GetBestSize())
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer une feuille d'heures")))
        self.bouton_imprimer.SetSize(self.bouton_imprimer.GetBestSize())
        self.bouton_stats.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher les statistiques de présences")))
        self.bouton_stats.SetSize(self.bouton_stats.GetBestSize())
        self.bouton_modele.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour appliquer un modèle de présences")))
        self.bouton_modele.SetSize(self.bouton_modele.GetBestSize())
        self.bouton_recherche.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour faire apparaître ou disparaître la barre de recherche")))
        self.bouton_recherche.SetSize(self.bouton_recherche.GetBestSize())
        self.barreRecherche.SetToolTip(wx.ToolTip(_(u"Saisissez ici '2008', 'Toussaint 2008', 'Samedi 15 décembre 2008', etc...")))
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjout, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModif, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSuppr, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonStats, self.bouton_stats)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModele, self.bouton_modele)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRecherche, self.bouton_recherche)

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        staticBox = wx.StaticBoxSizer(self.staticBox_staticbox, wx.VERTICAL)
        grid_sizer = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
       
        # Dossier
        grid_sizer.Add(self.listCtrl, 1, wx.EXPAND, 0)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=9, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add( (5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_stats, 0, 0, 0)
        grid_sizer_boutons.Add( (5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modele, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_recherche, 0, 0, 0)
        grid_sizer.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        
        grid_sizer.AddGrowableRow(0)
        grid_sizer.AddGrowableCol(0)
        staticBox.Add(grid_sizer, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticBox, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.TOP|wx.EXPAND, 5)
        
        grid_sizer.Add(self.barreRecherche, 1, wx.EXPAND, 0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)

        self.grid_sizer = grid_sizer

    def OnBoutonAjout(self, event):
        self.Ajouter()
        event.Skip()

    def Ajouter(self):
        dlg = Dialog_saisie(self, IDpersonne=self.IDpersonne)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonModif(self, event):
        self.Modifier()
        event.Skip()

    def Modifier(self):
        """ Modification de d'une présence """
        index = self.listCtrl.GetFirstSelected()
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une tâche à modifier dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDpresence = int(self.listCtrl.getColumnText(index, 0))
        # Ouverture de la frame saisie de présences
        from Dlg import DLG_Saisie_presence
        dlg = DLG_Saisie_presence.Dialog(self, IDmodif=IDpresence)
        dlg.panel.sizer_1.Hide(False)
        dlg.panel.sizer_donnees_staticbox.Hide()
        dlg.panel.grid_sizer_base.Layout()
        dlg.SetMinSize((400, 320))
        dlg.SetSize((400, 320))
        dlg.ShowModal()
        dlg.Destroy()
        self.listCtrl.indexEnCours = index

    def OnBoutonSuppr(self, event):
        self.Supprimer()
        pass
        
    def Supprimer(self):
        """ Suppression d'une tâche """
        index = self.listCtrl.GetFirstSelected()

        # Vérifie qu'un item a bien été sélectionné
        if index == -1:
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner une tâche à supprimer dans la liste."), "Information", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation
        date = self.listCtrl.GetItem(index, 3).GetText()
        if date == "" :
            date = self.listCtrl.GetItem(index-1, 3).GetText()
            if date == "" :
                date = self.listCtrl.GetItem(index-2, 3).GetText()
                if date == "" :
                    date = self.listCtrl.GetItem(index-3, 3).GetText()
                    if date == "" :
                        date = self.listCtrl.GetItem(index-4, 3).GetText()
        horaires = self.listCtrl.GetItem(index, 5).GetText()
        textePresence = date + " : " + horaires
        txtMessage = six.text_type((_(u"Voulez-vous vraiment supprimer cette tâche ? \n\n> ") + textePresence))
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        
        IDpresence = int(self.listCtrl.getColumnText(index, 0))

        # Suppression
        DB = GestionDB.DB()
        DB.ReqDEL("presences", "IDpresence", IDpresence)

        # MàJ du listCtrl de la fiche individuelle
        if index > 0 : self.listCtrl.indexEnCours = index - 1
        else: self.listCtrl.indexEnCours = 0
        self.MAJpanel()
    
    def OnBoutonImprimer(self, event):
        from Dlg import DLG_Impression_calendrier_annuel
        dlg = DLG_Impression_calendrier_annuel.MyDialog(self, IDpersonne=self.IDpersonne, autoriser_choix_personne=False)
        dlg.ShowModal()
    
    def OnBoutonStats(self, event):
        """ Afficher les stats de présences de la personne """
        topWindow = wx.GetApp().GetTopWindow() 
        try : topWindow.SetStatusText(_(u"Chargement du module des statistiques en cours. Veuillez patientez..."))
        except : pass
        print("lancement fonction Stats...")
        try :
            from Dlg import DLG_Statistiques
            dlg = DLG_Statistiques.Dialog(self, listeDates=[], listePersonnes=[self.IDpersonne,])
            dlg.ShowModal()
            dlg.Destroy()
        except Exception as err :
            print("Erreur d'ouverture de la frame Stats : ", Exception, err)
        try : topWindow.SetStatusText(u"")
        except : pass
        
    def OnBoutonModele(self, event):
        self.AppliquerModele()
        event.Skip()
    
    def AppliquerModele(self):
        """ Appliquer un modèle de présence """
        dlg = Dialog_application_modele(self, IDpersonne=self.IDpersonne)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnBoutonRecherche(self, event):
        self.Rechercher()
        event.Skip()
    
    def Rechercher(self):
        """ Rechercher une date, une période, un mois ou une année """
        if self.barreRecherche.IsShown() :
            self.barreRecherche.Show(False)
            self.bouton_recherche.SetBitmapLabel(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe_plus.png"), wx.BITMAP_TYPE_PNG))
            self.barreRecherche.SetValue("")
            self.listCtrl.Rechercher(txtSearch="")
        else:
            self.barreRecherche.Show(True)
            self.bouton_recherche.SetBitmapLabel(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe_moins.png"), wx.BITMAP_TYPE_PNG))
        self.grid_sizer.Layout()
        self.Refresh()
        
    def MAJpanel(self):
        self.listCtrl.MAJListeCtrl()
     


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,-1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent

        self.SetDescriptiveText(_(u"Rechercher une date, une période de vacances, un mois ou une année..."))
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
        self.parent.listCtrl.Rechercher(txtSearch)
        

# ------------------------------------        SAISIE PRESENCE             --------------------------------------------------------------------------

class Dialog_saisie(wx.Dialog):
    def __init__(self, parent, title=_(u"Saisie de présences"), IDpersonne=0):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDpersonne = IDpersonne
        self.panel_base = wx.Panel(self, -1, name="panel_saisiePresences_FicheInd")
        
        # Panel Calendrier
        self.panel_calendrier = wx.Panel(self.panel_base, -1)
        self.calendrier = CTRL_Calendrier_tw.Panel(self.panel_calendrier, afficheBoutonAnnuel=True)
        self.staticbox_calendrier = wx.StaticBox(self.panel_calendrier, -1, _(u"Dates"))
        sizer_calendrier = wx.StaticBoxSizer(self.staticbox_calendrier, wx.VERTICAL)
        sizer_calendrier.Add(self.calendrier, 1, wx.ALL|wx.EXPAND, 5)
        self.label_dates = wx.StaticText(self.panel_calendrier, -1, _(u"> Aucune date sélectionnée"))
        self.label_dates.SetForegroundColour((150, 150, 150))
        sizer_calendrier.Add(self.label_dates, 0, wx.ALL, 5)
        self.panel_calendrier.SetSizer(sizer_calendrier)
        self.calendrier.calendrier.SelectJours( [] )

        # Saisie Présences
        self.panel_saisiePresences = DLG_Saisie_presence.Panel(self.panel_base)
        self.panel_saisiePresences.sizer_1.Hide(False)
        self.panel_saisiePresences.sizer_donnees_staticbox.Hide()
        self.panel_saisiePresences.grid_sizer_base.Layout()
        
        # Layout général
        sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=0, hgap=0)
        sizer_base.Add(self.panel_calendrier, 1, wx.EXPAND|wx.TOP|wx.BOTTOM|wx.LEFT, 10)
        sizer_base.Add(self.panel_saisiePresences, 1, wx.EXPAND, 0)
        sizer_base.AddGrowableCol(0)
        sizer_base.AddGrowableRow(0)
        self.panel_base.SetSizer(sizer_base)
        self.Layout()
        self.CenterOnScreen()
        self.SetMinSize((640, 330))
        self.SetSize((640, 330))
        
        # Bind
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def OnClose(self, event):
        self.Fermer()
        event.Skip()
        
    def Fermer(self):
        self.parent.MAJpanel()
        self.EndModal(wx.ID_OK)

    def SendDates(self, listeDates=[]):
        # Envoie des dates au panel de saisie des présences
        listeDonnees = []
        for date in listeDates :
            listeDonnees.append( (self.IDpersonne, date) )
        self.panel_saisiePresences.CreationDictDonnees(listeDonnees)
        # Met à jour le label_dates
        nbreDates = len(listeDates)
        if nbreDates == 0 : texte = _(u"> Aucune date sélectionnée")
        if nbreDates == 1 : texte = _(u"> 1 date sélectionnée")
        if nbreDates > 1 : texte = u"> " + str(nbreDates) + _(u" dates sélectionnées")
        self.label_dates.SetLabel(texte)




# ------------------------------------        APPLICATION MODELE             --------------------------------------------------------------------------


class Dialog_application_modele(wx.Dialog):
    def __init__(self, parent, title=_(u"Application d'un modèle"), IDpersonne=0):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDpersonne = IDpersonne
        self.panel_base = wx.Panel(self, -1, name="panel_applicModele_FicheInd")

        self.selectionLignes = []
        self.selectionPersonnes = [IDpersonne,]
        self.selectionDates = (None, None)

        # Panel Calendrier
        self.panel_calendrier = wx.Panel(self.panel_base, -1)
        self.calendrier = CTRL_Calendrier_tw.Panel(self.panel_calendrier, afficheBoutonAnnuel=True)
        self.staticbox_calendrier = wx.StaticBox(self.panel_calendrier, -1, _(u"Veuillez sélectionner une ou plusieurs dates"))
        sizer_calendrier = wx.StaticBoxSizer(self.staticbox_calendrier, wx.VERTICAL)
        sizer_calendrier.Add(self.calendrier, 1, wx.ALL|wx.EXPAND, 5)
        self.label_dates = wx.StaticText(self.panel_calendrier, -1, _(u"> Aucune date sélectionnée"))
        self.label_dates.SetForegroundColour((150, 150, 150))
        sizer_calendrier.Add(self.label_dates, 0, wx.ALL, 5)
        self.panel_calendrier.SetSizer(sizer_calendrier)
        self.calendrier.calendrier.SelectJours( [] )

        # Saisie Présences
        self.panel_applicModele = DLG_Application_modele.Panel(self.panel_base, selectionPersonnes=self.selectionPersonnes)
        self.panel_applicModele.list_ctrl_personnes.Show(False)
        self.panel_applicModele.label_personnes.Show(False)
        self.panel_applicModele.grid_sizer_manuel.Layout()
        self.panel_applicModele.sizer_parametres_staticbox.SetLabel(_(u"Choix de la période"))
        
        # Layout général
        sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=0, hgap=0)
        sizer_base.Add(self.panel_calendrier, 1, wx.EXPAND|wx.TOP|wx.BOTTOM|wx.LEFT, 10)
        sizer_base.Add(self.panel_applicModele, 1, wx.EXPAND, 0)
        sizer_base.AddGrowableCol(0)
        sizer_base.AddGrowableRow(0)
        self.panel_base.SetSizer(sizer_base)
        self.Layout()
        self.SetMinSize((720, 400))
        self.SetSize((720, 400))
        self.CenterOnScreen()

    def Fermer(self):
        self.parent.MAJpanel()
        self.EndModal(wx.ID_CANCEL)

    def SendDates(self, listeDates=[]):
        # Envoie des dates au panel d'application des modèles
        selectionLignes = []
        for date in listeDates :
            selectionLignes.append( (self.IDpersonne, date) )
        self.selectionLignes = selectionLignes
        if len(selectionLignes) == 0 :
            self.selectionDates = (None, None)
        elif len(selectionLignes) == 1 :
            self.selectionDates = (listeDates[0], listeDates[0])
        elif len(selectionLignes) > 1 :
            self.selectionDates = (listeDates[0], listeDates[-1])
        
        # Envoi des données
        self.panel_applicModele.selectionLignes = self.selectionLignes
        self.panel_applicModele.selectionPersonnes = self.selectionPersonnes
        self.panel_applicModele.selectionDates = self.selectionDates

        # Réglages du panel application des Modeles
        self.panel_applicModele.SetLabelRadio1()

            
        # Met à jour le label_dates
        nbreDates = len(listeDates)
        if nbreDates == 0 : texte = _(u"> Aucune date sélectionnée")
        if nbreDates == 1 : texte = _(u"> 1 date sélectionnée")
        if nbreDates > 1 : texte = u"> " + str(nbreDates) + _(u" dates sélectionnées")
        self.label_dates.SetLabel(texte)






# ----------- LISTCTRL  ---------------------------------------------------------------------------------------------------

class ListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent, IDpersonne=0):
        wx.ListCtrl.__init__( self, parent, -1, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_SINGLE_SEL|wx.LC_VRULES)
        
        self.IDpersonne = IDpersonne
        self.parent = parent
        self.selection = None
        self.txtSearch = ""
        
        self.Importation_categories()
        self.Importation_vacances()

        # Initialisation des images
        tailleIcones = 22
        self.il = wx.ImageList(tailleIcones, tailleIcones)
        # Images AZ et ZA
        self.imgTriAz= self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/22x22/Tri_az.png"), wx.BITMAP_TYPE_PNG))
        self.imgTriZa= self.il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/22x22/Tri_za.png"), wx.BITMAP_TYPE_PNG))
        # Images des couleurs de Catégories
        for key, valeurs in self.dictCategories.items() :
            r, v, b = self.FormateCouleur(valeurs[1])
            setattr(self, "img%s" % key, self.il.Add(self.CreationImage((22, 22), r, v, b, key)))
        # Finalisation ImageList
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        #adding some attributes (colourful background for each item rows)
        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour("#EEF4FB") # Vert = #F0FBED

        # Remplissage du ListCtrl
        self.Remplissage()
        
        #events
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

        self.indexEnCours = self.nbreLignes-1
        self.SetSelection(index=self.indexEnCours, selection=False)

    def FormateCouleur(self, texte):
        pos1 = texte.index(",")
        pos2 = texte.index(",", pos1+1)
        r = int(texte[1:pos1])
        v = int(texte[pos1+2:pos2])
        b = int(texte[pos2+2:-1])
        return (r, v, b)
    
    def CreationImage(self, tailleImages, r, v, b, IDcategorie):
        """ Création des images pour le TreeCtrl """
        colFond = (255, 255, 255)
        if 'phoenix' in wx.PlatformInfo:
            bmp = wx.Image(tailleImages[0], tailleImages[1], True)
            bmp.SetRGB((0, 0, tailleImages[0], tailleImages[1]), colFond[0], colFond[1], colFond[2])
            bmp.SetRGB((0, 5, 12, 12), r, v, b)
        else:
            bmp = wx.EmptyImage(tailleImages[0], tailleImages[1], True)
            bmp.SetRGBRect((0, 0, tailleImages[0], tailleImages[1]), colFond[0], colFond[1], colFond[2])
            bmp.SetRGBRect((0, 5, 12, 12), r, v, b)
        return bmp.ConvertToBitmap()
    
    def OnSize(self, event):
        self.Refresh()
        event.Skip()

    def Remplissage(self):
        
        # Récupération des données dans la base de données
        self.Importation()
        
        # Création des colonnes
        self.nbreColonnes = 7
        self.InsertColumn(0, u"")
        self.SetColumnWidth(0, 22)
        self.InsertColumn(1, _(u"attribut"))
        self.SetColumnWidth(1, 0)
        self.InsertColumn(2, _(u"categorie"))
        self.SetColumnWidth(2, 0)
        self.InsertColumn(3, _(u"Date"))
        self.SetColumnWidth(3, 170)
        self.InsertColumn(4, _(u"Vacances"))
        self.SetColumnWidth(4, 65)
        self.InsertColumn(5, _(u"Horaires"))
        self.SetColumnWidth(5, 85)
        self.InsertColumn(6, _(u"Durée"))
        self.SetColumnWidth(6, 45)
        self.InsertColumn(7, _(u"Intitulé"))
        self.SetColumnWidth(7, 300)

        #These two should probably be passed to init more cleanly
        #setting the numbers of items = number of elements in the dictionary
        self.itemDataMap = self.donnees
        self.itemIndexMap = list(self.donnees.keys())
        self.SetItemCount(self.nbreLignes)
        
        #mixins
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)

        #sort by genre (column 1), A->Z ascending order (1)
        self.SortListItems(3, 1)


##    def OnItemSelected(self, event):
##        self.parent.bouton_modifier.Enable(True)
##        self.parent.bouton_supprimer.Enable(True)
##        if self.GetFirstSelected() == -1: return False
##        index = self.GetFirstSelected()
##        key = int(self.getColumnText(index, 0))
##        self.selection = key
##        
##    def OnItemDeselected(self, event):
##        self.parent.bouton_modifier.Enable(False)
##        self.parent.bouton_supprimer.Enable(False)
##        self.selection = None
##        
##    def SetSelection(self, IDpays=0) :
##        self.selection = IDpays
##        # Recherche de l'index du pays dans le listCtrl
##        for key, valeurs in self.donnees.iteritems() :
##            if valeurs[0] == IDpays : 
##                self.Focus(key-1)
##                self.Select(key-1)
##                return


    def Importation_categories(self):
        DB = GestionDB.DB() 
        # Récupération des catégorie de présences
        req = """SELECT IDcategorie, nom_categorie, couleur FROM cat_presences;"""
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        DB.Close()
        # Transformation de la liste des catégories en dictionnaire
        self.dictCategories = {}
        for IDcategorie, nom_categorie, couleur in listeCategories :
            self.dictCategories[IDcategorie] = (nom_categorie, couleur)

    def Importation_vacances(self):
        DB = GestionDB.DB() 
        # Récupération des périodes de vacances
        req = """SELECT IDperiode, nom, annee, date_debut, date_fin FROM periodes_vacances;"""
        DB.ExecuterReq(req)
        self.listeVacances = DB.ResultatReq()
        DB.Close()
            
    def Importation(self):
        DB = GestionDB.DB() 
        # Récupération des présences
        req = """SELECT IDpresence, date, heure_debut, heure_fin, IDcategorie, intitule
        FROM presences WHERE IDpersonne=%d ORDER BY date, heure_debut ; """ % self.IDpersonne
        DB.ExecuterReq(req)
        listePresences = DB.ResultatReq()
        DB.Close()
        # Formatage de la liste des présences
        self.donnees = {}
        attribut = 0
        datePrecedente = None
        index = 1
        
        for IDpresence, date, heure_debut, heure_fin, IDcategorie, intitule in listePresences :
            # Données
            horaires = self.FormateHeure(heure_debut) + "-" + self.FormateHeure(heure_fin)
            duree = self.CalculeDuree(heure_debut, heure_fin)
            texte = self.dictCategories[IDcategorie][0]
            if intitule != "" : texte += " (" + intitule + ")"
            if self.txtSearch != "" : 
                dateComplete = self.FormateDate(date)
                dateFrancaise = date[8:10] + "/" + date[5:7] + "/" + date [0:4]

            else : 
                dateComplete = ""
            
            # Date en période de vacances ?
            vacances = ""
            for IDperiode, nom, annee, date_debut, date_fin in self.listeVacances :
                if date_debut <= date <= date_fin :
                    vacances = nom + " " + annee
            
            # Attribut de couleur 1 date sur 2
            if datePrecedente != date :
                if attribut == 0 : 
                    attribut = 1
                else : 
                    attribut = 0
                    
            # Si une recherche est en cours : filtrage des données...
            if self.txtSearch != "" :
                if FonctionsPerso.EnleveAccents(self.txtSearch).upper() in FonctionsPerso.EnleveAccents(dateFrancaise).upper() : valide = True
                elif FonctionsPerso.EnleveAccents(self.txtSearch).upper() in FonctionsPerso.EnleveAccents(dateComplete).upper() : valide = True
                elif FonctionsPerso.EnleveAccents(self.txtSearch).upper() in FonctionsPerso.EnleveAccents(vacances).upper() : valide = True
                elif FonctionsPerso.EnleveAccents(self.txtSearch).upper() in FonctionsPerso.EnleveAccents(texte).upper() : valide = True
                else : valide = False
            else :
                valide = True
            
            if valide == True :
                self.donnees[index] = (IDpresence, attribut, IDcategorie, date, vacances, horaires, duree, texte)
                datePrecedente = date
                index += 1

        self.nbreLignes = len(self.donnees)
        
        # Label du staticBox
        if self.txtSearch == "" : 
            if self.nbreLignes == 0 : texteLabel = _(u"Aucune présence")
            if self.nbreLignes == 1 : texteLabel = _(u"1 présence")
            if self.nbreLignes > 1 : texteLabel = str(self.nbreLignes) + _(u" présences")
        else:
            if self.nbreLignes == 0 : texteLabel = _(u"Aucune présence trouvée avec le filtre '") + self.txtSearch + "'"
            if self.nbreLignes == 1 : texteLabel = _(u"Un présence trouvée avec le filtre '") + self.txtSearch + "'"
            if self.nbreLignes > 1 : texteLabel = str(self.nbreLignes) + _(u" présences trouvées avec le filtre '") + self.txtSearch + "'"
        self.parent.staticBox_staticbox.SetLabel(texteLabel)
        
        
    def FormateHeure(self, heure):
        heures=int(heure[:2])
        minutes=int(heure[3:])
        if minutes >= 10 : texte = str(heures) + "h" + str(minutes)
        else: texte = str(heures) + "h0" + str(minutes)
        return texte
        
    def FormateDate(self, dateCourte):
        """ Transforme une date de type str '2008/12/04' en date complète de type Lundi 4 décembre 2008 """
        annee = dateCourte[:4]
        mois = dateCourte[5:7]
        jour = dateCourte[8:10]
        date = datetime.date(int(annee), int(mois), int(jour))
        listeJours = ("Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche")
        listeMois = ("janvier", _(u"février"), "mars", "avril", "mai", "juin", "juillet", _(u"août"), "septembre", "octobre", "novembre", _(u"décembre"))
        dateStr = listeJours[date.weekday()] + " " + str(date.day) + " " + listeMois[date.month-1] + " " + str(date.year)
        return dateStr


    def CalculeDuree(self, heureMin, heureMax) :
        HMin = datetime.timedelta(hours=int(heureMin[:2]), minutes=int(heureMin[3:]))
        HMax = datetime.timedelta(hours=int(heureMax[:2]), minutes=int(heureMax[3:]))
        totalMinutes = ((HMax - HMin).seconds)/60
        nbreHeures = totalMinutes/60
        nbreMinutes = totalMinutes-(nbreHeures*60)
        if len(str(nbreMinutes))==1 : nbreMinutes = str("0") + str(nbreMinutes)
        duree = str(nbreHeures) + "h" + str(nbreMinutes)
        return duree
                    
    def MAJListeCtrl(self):
        self.ClearAll()
        self.Remplissage()
        self.resizeLastColumn(0)
        listmix.ColumnSorterMixin.__init__(self, self.nbreColonnes)
        self.SetSelection(self.indexEnCours)
    
    def SetSelection(self, index=0, selection=True) :
        self.EnsureVisible(index)
        if selection == True :
            self.Select(index)
           
    def OnItemActivated(self, event):
        self.parent.Modifier()
        
    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    #---------------------------------------------------
    # These methods are callbacks for implementing the
    # "virtualness" of the list...

    def OnGetItemText(self, item, col):
        """ Affichage des valeurs dans chaque case du ListCtrl """
        index=self.itemIndexMap[item]
        valeur = six.text_type(self.itemDataMap[index][col])
        # Formate les dates
        if col == 3 :
            dateStr = self.FormateDate(valeur)
            if index > 1 :
                # Texte de la ligne précédente
                datePrecedente = six.text_type(self.itemDataMap[index-1][col])
                if valeur == datePrecedente : return ""
            if type(dateStr) != six.text_type :
                dateStr = dateStr.decode("iso-8859-15")
            return dateStr
        return valeur

    def OnGetItemImage(self, item):
        """ Affichage des images en début de ligne """
        index=self.itemIndexMap[item]
        IDcategorie = self.itemDataMap[index][2]
        img = eval("self.img" + str(IDcategorie))
        return img


    def OnGetItemAttr(self, item):
        """ Application d'une couleur de fond pour un jour sur deux """
        index=self.itemIndexMap[item]
        valeur = six.text_type(self.itemDataMap[index][1])
        if valeur == "1" : return self.attr1
        else : return None

       
    #-----------------------------------------------------------
    # Matt C, 2006/02/22
    # Here's a better SortItems() method --
    # the ColumnSorterMixin.__ColumnSorter() method already handles the ascending/descending,
    # and it knows to sort on another column if the chosen columns have the same value.

    def SortItems(self,sorter=FonctionsPerso.cmp):
        items = list(self.itemDataMap.keys())
        items = FonctionsPerso.SortItems(items, sorter)
        self.itemIndexMap = items
        # redraw the list
        self.Refresh()

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.imgTriAz, self.imgTriZa)

    # ---------------------------------------------------------

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        
        if self.GetFirstSelected() == -1:
            return False
        index = self.GetFirstSelected()
        key = int(self.getColumnText(index, 0))
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Modifier, id=20)

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Menu_Ajouter(self, event):
        self.parent.Ajouter()
        
    def Menu_Modifier(self, event):
        self.parent.Modifier()

    def Menu_Supprimer(self, event):
        self.parent.Supprimer()
        
        
    def Rechercher(self, txtSearch):
        """ Rechercher une date, un mois, une vacance, etc... """
        self.txtSearch = txtSearch
        self.MAJListeCtrl()
        
        
        
class Dialog(wx.Dialog):
    def __init__(self, parent, title=_(u"Liste de présences"), IDpersonne=1):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDpersonne = IDpersonne
        self.panel_base = wx.Panel(self, -1)
        self.panel_contenu = Panel(self.panel_base, IDpersonne=IDpersonne)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)

    def __set_properties(self):
        # Récupération de l'identité de la personne
        try :
            DB = GestionDB.DB() 
            req = """SELECT nom, prenom FROM personnes WHERE IDpersonne=%d; """ % self.IDpersonne
            DB.ExecuterReq(req)
            identite = DB.ResultatReq()[0]
            DB.Close()
            self.SetTitle(_(u"Liste des présences de ") + identite[1] + " " + identite[0])
        except :
            self.SetTitle(_(u"Liste des présences"))
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler et fermer")))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.ALL|wx.EXPAND, 0)
        sizer_pages.Add(self.panel_contenu, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.BOTTOM|wx.RIGHT|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        self.sizer_pages = sizer_pages
        
        self.bouton_annuler.Show(False)
        self.SetMinSize((450, 350))
        self.SetSize((750, 550))
        self.CenterOnScreen()

    def Onbouton_aide(self, event):
        print("aide")
            
    def Onbouton_annuler(self, event):
        self.EndModal(wx.ID_CANCEL)
        
    def Onbouton_ok(self, event):
        # Met à jour le panel présences
        try :
            if self.GetGrandParent().GetGrandParent().GetName() == "panel_presences" :
                self.GetGrandParent().GetGrandParent().MAJpanel(reinitSelectionPersonnes=True)
        except : pass
        
        # Fermeture
        self.EndModal(wx.ID_OK)

if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None, "")
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()