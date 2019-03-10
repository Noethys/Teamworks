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
import os
from Dlg import DLG_Selection_periode
import wx.lib.agw.hyperlink as hl
from Utils import UTILS_Fichiers
if 'phoenix' in wx.PlatformInfo:
    from wx.adv import BitmapComboBox
else :
    from wx.combo import BitmapComboBox
import sys
from Ctrl import CTRL_Photo



class PanelPhoto(wx.Panel):
    def __init__(self, parent, IDpersonne=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.IDpersonne = IDpersonne
        
        # Choix décoration
        self.label_decoration = wx.StaticText(self, -1, _(u"Cadre de décoration :"), style=wx.ALIGN_RIGHT)
        listeCadres = FonctionsPerso.GetListeCadresPhotos()
        self.combobox_decoration = wx.Choice(self, -1, choices=listeCadres)
        
        # Recherche du cadre de décoration attribué à la personne
        cadrePhoto, textePhoto = CTRL_Photo.GetCadreEtTexte(self.IDpersonne)
        if cadrePhoto != None and cadrePhoto != "" :
            self.combobox_decoration.SetStringSelection(cadrePhoto)
        else:
            self.combobox_decoration.SetSelection(0)
        
        # Saisie du texte personnalisé
        self.label_texte_perso = wx.StaticText(self, -1, _(u"Texte personnalisé :"), style=wx.ALIGN_RIGHT)
        self.texte_perso = wx.TextCtrl(self, -1, textePhoto)
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_decoration, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.Add(self.combobox_decoration, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.Add(self.label_texte_perso, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.Add(self.texte_perso, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 0)
        grid_sizer_base.AddGrowableCol(3)
        self.SetSizer(grid_sizer_base)
        self.Layout()
        
        # Binds
        self.Bind(wx.EVT_CHOICE, self.OnChoixDecoration, self.combobox_decoration)
        self.Bind(wx.EVT_TEXT, self.OnTextePerso, self.texte_perso)
        
    def OnChoixDecoration(self, event):    
        # Sauvegarde du cadre de décoration
        cadrePhoto = self.combobox_decoration.GetStringSelection()
        if cadrePhoto == "Aucun" : cadrePhoto = ""
        DB = GestionDB.DB()
        DB.ReqMAJ("personnes", [("cadre_photo", cadrePhoto),], "IDpersonne", self.IDpersonne)
        DB.Close()
        # MAJ de l'image dans le listBook
        self.GetParent().RemplacePhoto(self.IDpersonne)
        
    def OnTextePerso(self, event):    
        # Sauvegarde du texte perso
        texte = self.texte_perso.GetValue()
        DB = GestionDB.DB()
        DB.ReqMAJ("personnes", [("texte_photo", texte),], "IDpersonne", self.IDpersonne)
        DB.Close()

      

class ListBookPhotos(wx.Listbook):
    def __init__(self, parent, id=-1):
        wx.Listbook.__init__(self, parent, id, style=wx.BK_TOP)
        self.listePersonnes = self.GetGrandParent().listePersonnes

        self.InitAll()
        
    def InitAll(self):
        # Efface les pages s'il y en a :
        if self.GetPageCount() != 0 :
            self.DeleteAllPages() 

        # ImageList
        self.tailleImages = 100
        self.il = wx.ImageList(self.tailleImages, self.tailleImages)
        index = 0
        for IDpersonne, nom, prenom, indexImage in self.listePersonnes :
            bmp = self.RecuperePhoto(IDpersonne)
            # Attribuer l'image
            indexImage = self.il.Add(bmp)
            # Place l'index de l'image attribué dans la liste de données
            self.listePersonnes[index][3] = indexImage
            index += 1
        self.AssignImageList(self.il)

        # Création des pages
        for IDpersonne, nom, prenom, indexImage in self.listePersonnes :
            page = PanelPhoto(self, IDpersonne=IDpersonne)
            self.AddPage(page, prenom, imageId=indexImage)

        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGING, self.OnPageChanging)
    
    
    def RemplacePhoto(self, IDpersonne):
        """ MAJ la photo dans le listImage du listBook """
        # Récupère l'index dans le listBook et l'index de la photo dans le listImages
        index = 0
        for IDpers, nom, prenom, indexImage in self.listePersonnes :
            if IDpers == IDpersonne : break
            index += 1
        il = self.GetImageList()
        # Re-créé l'image
        bmp = self.RecuperePhoto(IDpersonne)
        il.Replace(index, bmp)
        # Met à jour l'image de la page
        self.SetPageImage(index, index)
    
    def RecuperePhoto(self, IDpersonne):
        IDphoto, bmp = CTRL_Photo.GetPhoto(IDindividu=IDpersonne, taillePhoto=(self.tailleImages, self.tailleImages), qualite=50)
        if bmp == None :
            # Crée une image vide
            bmp = self.CreationPhotoVide(self.tailleImages)
        return bmp
    
    def CreationPhotoVide(self, taille):
        """ Création d'une photo vide """
        bmp = wx.EmptyBitmap(taille, taille)
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetBackground(wx.Brush("WHITE"))
        dc.Clear()
        texte = _(u"Pas de photo")
        largeurTexte, hauteurTexte = self.GetTextExtent(texte)
        xTexte = (taille/2.0) - (largeurTexte/2.0)
        yTexte = taille/2.0 - hauteurTexte
        dc.SetTextForeground("GREY")
        dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
        dc.DrawText(texte, xTexte, yTexte)
        return bmp
    
    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        #self.log.write('OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        #self.log.write('OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()
        
    def MAJ(self):
        self.InitAll()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, listePersonnes=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.panel_base = wx.Panel(self, -1)
        self.listePersonnes = listePersonnes

        self.dictAffichage = {
            "nom_police" : "Arial",
            "nom_style" : wx.FONTWEIGHT_BOLD,
            "nom_taille" : 10,
            "nom_couleur" : (255, 0, 0),
            "type_nom" : 0,

            "texte_perso_police" : "Arial",
            "texte_perso_style" : wx.NORMAL,
            "texte_perso_taille" : 10,
            "texte_perso_couleur" : (255, 0, 0),

            "disposition_page" : 0,
            "nbre_copies" : 1,
            "bordure" : True,
            #"couleur_fond" : None,
            }

        # Données
        self.ImportationDonnees()
        
        # Paramètres de la page
        self.staticbox_page = wx.StaticBox(self.panel_base, -1, _(u"Paramètres de la page"))
        self.ctrl_disposition = BitmapComboBox(self.panel_base, size=(320,-1), style=wx.CB_READONLY)
        
        # Images pour le bitmapComboBox
        listePhotos = [ (0, _(u"Pleine page (15.9cm x 15.9cm)")), (1, _(u"2 photos par page (10.9cm x 10.9cm)")), (2, _(u"4 photos par page (8.1cm x 8.1cm)")), (3, _(u"12 photos par page (5.3cm x 5.3cm)")), (4, _(u"20 photos par page (3.8cm x 3.8cm)")), (5, _(u"35 photos par page (3.1cm x 3.1cm)"))]
        for ID, nom in listePhotos :
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/80x80/photo" + str(ID) + ".png"), wx.BITMAP_TYPE_PNG)
            self.ctrl_disposition.Append(nom, bmp, ID)
        self.ctrl_disposition.Select(self.dictAffichage["disposition_page"])
        
        # Paramètres de l'impression
        self.staticbox_param = wx.StaticBox(self.panel_base, -1, _(u"Paramètres de l'impression"))

        self.label_bordure = wx.StaticText(self.panel_base, -1, _(u"Bordures :"), style=wx.ALIGN_RIGHT)
        self.bordure = wx.CheckBox(self.panel_base, -1, u"")
        self.bordure.SetValue(self.dictAffichage["bordure"])
        self.label_nbre_copies = wx.StaticText(self.panel_base, -1, _(u"Nbre de copies :"), style=wx.ALIGN_RIGHT)
        self.nbre_copies = wx.SpinCtrl(self.panel_base, -1, "", size=(60, -1))
        self.nbre_copies.SetRange(1,100)
        self.nbre_copies.SetValue(self.dictAffichage["nbre_copies"])
        
        # Liste des photos
        self.sizer_grid_staticbox = wx.StaticBox(self.panel_base, -1, _(u"Paramètres des photos"))
        self.label_intro = wx.StaticText(self.panel_base, -1, _(u"Sélectionnez les paramètres de votre choix et cliquez sur 'Aperçu'."))
        self.listBook = ListBookPhotos(self.panel_base)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aperçu"), cheminImage=Chemins.GetStaticPath("Images/32x32/Apercu.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Fermer"), cheminImage=Chemins.GetStaticPath("Images/32x32/Fermer.png"))
        
        self.bouton_ok.SetFocus()
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)

        self.Bind(wx.EVT_COMBOBOX, self.OnComboDisposition, self.ctrl_disposition)

            
    def __set_properties(self):
        self.SetTitle(_(u"Impression des photos"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip("Cliquez ici pour visualiser le document au format PDF"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip("Cliquez ici pour annuler et fermer"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Liste des personnes
        sizer_page = wx.StaticBoxSizer(self.staticbox_page, wx.VERTICAL)
        sizer_page.Add(self.ctrl_disposition, 1, wx.ALL|wx.EXPAND, 5) 
        grid_sizer_haut.Add(sizer_page, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 0)
        
        # Paramètres de l'impression
        sizer_param = wx.StaticBoxSizer(self.staticbox_param, wx.VERTICAL)
        grid_sizer_param = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
        
        grid_sizer_param.Add(self.label_bordure, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.bordure, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.label_nbre_copies, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_param.Add(self.nbre_copies, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_haut.AddGrowableCol(1)
        sizer_param.Add(grid_sizer_param, 1, wx.ALL|wx.EXPAND, 5) 
        grid_sizer_haut.Add(sizer_param, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 0)
        
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Liste des photos
        sizer_grid = wx.StaticBoxSizer(self.sizer_grid_staticbox, wx.VERTICAL)
        sizer_grid.Add(self.listBook, 1, wx.ALL|wx.EXPAND, 5)
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
        self.SetMinSize((570, 500))
        self.Centre()
    
    def OnComboDisposition(self, evt):
        bcb = evt.GetEventObject()
        idx = evt.GetInt()
        st  = bcb.GetString(idx)
        cd  = bcb.GetClientData(idx)
        self.dictAffichage["disposition_page"] = cd
        
    def OnBoutonCouleurNom(self, event):
        reponse = event.GetValue()
        self.nom_couleur = (reponse[0], reponse[1], reponse[2])
        self.MajBoutonPoliceNom()
        
    def MajBoutonPoliceNom(self):
        font = wx.Font(9, wx.DEFAULT, wx.NORMAL, self.dictAffichage["nom_style"], False, self.dictAffichage["nom_police"])
        self.bouton_nom_police.SetFont(font)
        self.bouton_nom_police.SetLabel(self.dictAffichage["nom_police"] + ", " + str(self.dictAffichage["nom_taille"]) + " points")

    def OnBoutonPoliceNom(self, event):
        font = wx.Font(self.dictAffichage["nom_taille"], wx.DEFAULT, wx.NORMAL, self.dictAffichage["nom_style"], False, self.dictAffichage["nom_police"])
        data = wx.FontData()
        data.EnableEffects(False)
        data.SetInitialFont(font)
        dlg = wx.FontDialog(self, data)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            font = data.GetChosenFont()
            self.dictAffichage["nom_taille"] = font.GetPointSize()
            self.dictAffichage["nom_police"] = font.GetFaceName()
            self.dictAffichage["nom_style"] = font.GetWeight()
            self.MajBoutonPoliceNom()

    def OnBoutonCouleurTextePerso(self, event):
        reponse = event.GetValue()
        self.texte_perso_couleur = (reponse[0], reponse[1], reponse[2])
        self.MajBoutonPoliceTextePerso()
        
    def MajBoutonPoliceTextePerso(self):
        font = wx.Font(9, wx.DEFAULT, wx.NORMAL, self.dictAffichage["texte_perso_style"], False, self.dictAffichage["texte_perso_police"])
        self.bouton_texte_perso_police.SetFont(font)
        self.bouton_texte_perso_police.SetLabel(self.dictAffichage["texte_perso_police"] + ", " + str(self.dictAffichage["texte_perso_taille"]) + " points")

    def OnBoutonPoliceTextePerso(self, event):
        font = wx.Font(self.dictAffichage["texte_perso_taille"], wx.DEFAULT, wx.NORMAL, self.dictAffichage["texte_perso_style"], False, self.dictAffichage["texte_perso_police"])
        data = wx.FontData()
        data.EnableEffects(False)
        data.SetInitialFont(font)
        dlg = wx.FontDialog(self, data)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            font = data.GetChosenFont()
            self.dictAffichage["texte_perso_taille"] = font.GetPointSize()
            self.dictAffichage["texte_perso_police"] = font.GetFaceName()
            self.dictAffichage["texte_perso_style"] = font.GetWeight()
            self.MajBoutonPoliceTextePerso()
            
    def ImportationDonnees(self):
        """ Importation de la liste des personnes """
        # Récupération de la liste des personnes
        DB = GestionDB.DB()        
        req = """SELECT IDpersonne, nom, prenom FROM personnes ORDER BY nom, prenom; """
        DB.ExecuterReq(req)
        listePersonnes = DB.ResultatReq()
        DB.Close()
        # Création de la liste pour le listBox et du dict de données
        self.listeDonnees = []
        self.dictDonnees = {}
        index = 0
        for IDpersonne, nom, prenom in listePersonnes :
            label = nom + " " + prenom
            self.listeDonnees.append(label)
            self.dictDonnees[index] = (IDpersonne, nom, prenom, None)
            index += 1

    def Build_Hyperlink(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self.panel_base, -1, _(u"Sélectionner les présents d'une période"), URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLACK", "BLACK", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner les personnes présentes sur une période donnée")))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink(self, event):
        """ Sélectionner les personnes présentes sur une période donnée """
        dlg = DLG_Selection_periode.SelectionPeriode(self)
        if dlg.ShowModal() == wx.ID_OK:
            listePersonnesPresentes = dlg.GetPersonnesPresentes()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        # Sélection dans la listBox
        for index, valeurs in self.dictDonnees.items():
            IDpersonne = valeurs[0]
            if IDpersonne in listePersonnesPresentes :
                self.checkListBox.Check(index, True)
            else:
                self.checkListBox.Check(index, False)
        # S'il n'y a aucune personne présente sur la période sélectionnée
        if len(listePersonnesPresentes) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune personne présente sur la période que vous avez sélectionné."), _(u"Erreur de saisie"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
    def Onbouton_aide(self, event):
        FonctionsPerso.Aide(30)

    def Onbouton_annuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def Onbouton_ok(self, event):
        """ Affichage du PDF """
        self.dictAffichage["nbre_copies"] = self.nbre_copies.GetValue()
        self.dictAffichage["bordure"] = self.bordure.GetValue()
        pdf = CreationPDF(self.listePersonnes, self.dictAffichage)






# ---------------------------------------------------------------------------------------------------------------------------------------------------------

class DialogSelectionPersonnes(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        self.panel_base = wx.Panel(self, -1)
        self.label_intro = wx.StaticText(self.panel_base, -1, _(u"Veuillez sélectionner les personnes pour lesquelles vous souhaitez imprimer la photo :"))
        
        # Données
        self.ImportationDonnees()
        
        # CheckListBox
        self.checkListBox = wx.CheckListBox(self.panel_base,  choices=self.listeDonnees)
        
        # Hyperlink cocher les présents
        self.hyperlink_presents = self.Build_Hyperlink()
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.SetTitle(_(u"Impression de photos"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip("Cliquez ici pour valider"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTip(wx.ToolTip("Cliquez ici pour annuler la saisie"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        self.SetMinSize((420, 380))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 1, wx.LEFT|wx.TOP|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add(self.checkListBox, 1, wx.EXPAND | wx.LEFT|wx.RIGHT|wx.TOP, 10)
        grid_sizer_base.Add(self.hyperlink_presents, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM | wx.ALIGN_RIGHT, 10)
        grid_sizer_base.Add((10, 10), 1, wx.EXPAND | wx.ALL, 0)
        
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.panel_base.SetSizer(grid_sizer_base)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.Centre()       
    
    def ImportationDonnees(self):
        """ Importation de la liste des personnes """
        # Récupération de la liste des personnes
        DB = GestionDB.DB()        
        req = """SELECT IDpersonne, nom, prenom FROM personnes ORDER BY nom, prenom; """
        DB.ExecuterReq(req)
        listePersonnes = DB.ResultatReq()
        DB.Close()
        # Création de la liste pour le listBox et du dict de données
        self.listeDonnees = []
        self.dictDonnees = {}
        index = 0
        for IDpersonne, nom, prenom in listePersonnes :
            label = nom + ", " + prenom
            # Creation liste et dict
            self.listeDonnees.append(label)
            self.dictDonnees[index] = (IDpersonne, nom, prenom)
            index += 1
    
    def Build_Hyperlink(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self.panel_base, -1, _(u"Sélectionner les présents sur une période donnée"), URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLACK", "BLACK", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner les personnes présentes sur une période donnée")))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink(self, event):
        """ Sélectionner les personnes présentes sur une période donnée """
        dlg = DLG_Selection_periode.SelectionPeriode(self)
        if dlg.ShowModal() == wx.ID_OK:
            listePersonnesPresentes = dlg.GetPersonnesPresentes()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        # Sélection dans la listBox
        for index, valeurs in self.dictDonnees.items():
            IDpersonne = valeurs[0]
            if IDpersonne in listePersonnesPresentes :
                self.checkListBox.Check(index, True)
            else:
                self.checkListBox.Check(index, False)
        # S'il n'y a aucune personne présente sur la période sélectionnée
        if len(listePersonnesPresentes) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune personne présente sur la période que vous avez sélectionné."), _(u"Erreur de saisie"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(30)

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        if 'phoenix' in wx.PlatformInfo:
            selections = self.checkListBox.GetCheckedItems()
        else:
            selections = self.checkListBox.GetChecked()
        
        # Validation de la sélection
        if len(selections) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez fait aucune sélection"), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Création de la liste des personnes sélectionnées
        listePersonnes = []
        for index in selections :
            IDpersonne, nom, prenom = self.dictDonnees[index]
            listePersonnes.append([IDpersonne, nom, prenom, None])

        # Ouverture de la frame des paramètres d'impression des photos
        dlg = Dialog(None, listePersonnes=listePersonnes)
        dlg.ShowModal()
        dlg.Destroy()
        
        # Fermeture
        self.EndModal(wx.ID_OK)






# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class CreationPDF():
    def __init__(self, listePersonnes=[], dictAffichage={}):
        """ Imprime les photos """
        self.listePersonnes = listePersonnes
        
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.units import inch, cm
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, portrait, landscape
        from reportlab.lib.utils import ImageReader
        self.hauteur_page = defaultPageSize[1]
        self.largeur_page = defaultPageSize[0]
        self.inch = inch
        
        modesPage = {
            0 : { "orientation" : "portrait", "tailleImageTmp" : 3000, "tailleImageFinal" : 450, "nbreColonnes" : 1, "padding" : 20, "taille_nom" : 34, "taille_texte" : 18 },
            1 : { "orientation" : "paysage", "tailleImageTmp" : 2000, "tailleImageFinal" : 310, "nbreColonnes" : 2, "padding" : 20, "taille_nom" : 20, "taille_texte" : 12 },
            2 : { "orientation" : "portrait", "tailleImageTmp" : 2000, "tailleImageFinal" : 230, "nbreColonnes" : 2, "padding" : 10, "taille_nom" : 18, "taille_texte" : 10 },
            3 : { "orientation" : "portrait", "tailleImageTmp" : 2000, "tailleImageFinal" : 150, "nbreColonnes" : 3, "padding" : 5, "taille_nom" : 14, "taille_texte" : 8 },
            4 : { "orientation" : "portrait", "tailleImageTmp" : 2000, "tailleImageFinal" : 110, "nbreColonnes" : 4, "padding" : 5, "taille_nom" : 10, "taille_texte" : 7 },
            5 : { "orientation" : "portrait", "tailleImageTmp" : 2000, "tailleImageFinal" : 90, "nbreColonnes" : 5, "padding" : 4, "taille_nom" : 9, "taille_texte" : 6 },
            }
        
        modePage = dictAffichage["disposition_page"]
        nbreCopies = dictAffichage["nbre_copies"]
        parametres = modesPage[modePage]
        tailleImageTmp = parametres["tailleImageTmp"]
        tailleImageFinal = parametres["tailleImageFinal"]
        nbreColonnes = parametres["nbreColonnes"]
        orientation = parametres["orientation"]
        padding = parametres["padding"]
        taille_nom = parametres["taille_nom"]
        taille_texte = parametres["taille_texte"]
        
        # Initialisation du PDF
        if orientation == "portrait" : 
            taillePage = portrait(A4)
        else:
            taillePage = landscape(A4)
        nomDoc = UTILS_Fichiers.GetRepTemp("photoPersonnes.pdf")
        if "win" in sys.platform : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=taillePage)
        story = []

        # Style du tableau
        styleTemp = [
                            #('GRID', (0,0), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
                            ('VALIGN', (0,0), (-1,-1), 'TOP'), # Centre verticalement toutes les cases
                            ('ALIGN', (0,0), (-1,-1), 'CENTRE'), # Colonne ID centrée
                            ]
        
##        if dictAffichage["couleur_fond"] != None :
##            styleTemp.append(('BACKGROUND', (0, 0), (-1, -1), colors.black))
        
        # Nbre de copies
        if nbreCopies > 1 :
            self.listePersonnesTmp = []
            for donnees in self.listePersonnes :
                for x in range(0, nbreCopies) :
                    self.listePersonnesTmp.append(donnees)
            self.listePersonnes = self.listePersonnesTmp
        
        self.listePersonnesTmp = []
        dictPhotos = {}
        for IDpersonne, nom, prenom, bmp in self.listePersonnes :
            IDphoto, bmp = CTRL_Photo.GetPhoto(IDindividu=IDpersonne, taillePhoto=(tailleImageTmp, tailleImageTmp), qualite=100)
            if bmp != None :
                # Création de la photo dans le répertoire Temp
                nomFichier = UTILS_Fichiers.GetRepTemp("photoTmp%d.jpg" % IDpersonne)
                bmp.SaveFile(nomFichier, type=wx.BITMAP_TYPE_JPEG)
                img = Image(nomFichier, width=tailleImageFinal, height=tailleImageFinal)
                dictPhotos[IDpersonne] = img
                self.listePersonnesTmp.append((IDpersonne, nom, prenom))
                
        if len(self.listePersonnesTmp) == 0 :
            dlg = wx.MessageDialog(None, _(u"Il n'existe aucune photo pour la ou les personnes sélectionnées !"), _(u"Mot de passe erroné"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        # Création des largeurs de colonnes
        largeursColonnes = []
        for numCol in range(0, nbreColonnes) :
            largeursColonnes.append(tailleImageFinal + (padding*2))
        
        # Calcul du nbre de lignes du tableau
        nbreLignes = (len(self.listePersonnesTmp) * 1.0) / nbreColonnes 
        if int(nbreLignes) != nbreLignes : 
            nbreLignes = int(nbreLignes) + 1
        else:
            nbreLignes = int(nbreLignes)
            
        # Création du tableau vide
        dataTableau = []
        for numLigne in range(0, nbreLignes*3):
            ligne = []
            for numCol in range(0, nbreColonnes):
                ligne.append("")
            dataTableau.append(ligne)
        
        # Remplissage du tableau
        index = 0
        numCol = 0
        numLigne = 0
        for IDpersonne, nom, prenom in self.listePersonnesTmp :
            dataTableau[numLigne][numCol] = dictPhotos[IDpersonne]
            dataTableau[numLigne+1][numCol] = prenom
            dataTableau[numLigne+2][numCol] = FonctionsPerso.RecupTextePhotoPersonne(IDpersonne)
            
            # Style des photos
            styleTemp.append(('TOPPADDING', (0, numLigne), (-1, numLigne), padding))
            styleTemp.append(('BOTTOMPADDING', (0, numLigne), (-1, numLigne), padding))
            # Style du nom
            styleTemp.append(('FONT',(0, numLigne+1),(-1, numLigne+1), "Helvetica-Bold", taille_nom))
            # Style du texte personnalisé
            styleTemp.append(('FONT',(0, numLigne+2),(-1, numLigne+2), "Helvetica", taille_texte))
            styleTemp.append(('BOTTOMPADDING', (0, numLigne+2), (-1, numLigne+2), padding))
            # Style de la bordure de la carte
            if dictAffichage["bordure"] == True :
                styleTemp.append(('BOX', (numCol, numLigne), (numCol, numLigne+2), 0.25, colors.black))
            
            index += 1
            if numCol < nbreColonnes-1 :
                numCol += 1
            else:
                numCol = 0
                numLigne += 3
        
        style = TableStyle(styleTemp)
        
        # Création du tableau
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(style)
        story.append(tableau)
        story.append(Spacer(0,20))
            
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = DialogSelectionPersonnes(None)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
