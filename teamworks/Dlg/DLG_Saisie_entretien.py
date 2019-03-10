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
import datetime
import FonctionsPerso
import wx.lib.masked as masked
if 'phoenix' in wx.PlatformInfo:
    from wx.adv import BitmapComboBox
else :
    from wx.combo import BitmapComboBox


class MyFrame(wx.Frame):
    def __init__(self, parent, IDentretien=None, IDcandidat=None, IDpersonne=None):
        wx.Frame.__init__(self, parent, -1, title="", style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)
        self.IDentretien = IDentretien
        self.IDcandidat = IDcandidat
        self.IDpersonne = IDpersonne
        
        self.panel = wx.Panel(self, -1)
        self.sizer_contenu_staticbox = wx.StaticBox(self.panel, -1, "")
        self.label_date = wx.StaticText(self.panel, -1, _(u"Date :"))
        self.ctrl_date = wx.DatePickerCtrl(self.panel, -1, style=wx.DP_DROPDOWN)
        self.label_heure = wx.StaticText(self.panel, -1, _(u"Heure :"))
        self.ctrl_heure = masked.TextCtrl(self.panel, -1, "", size=(60, -1), style=wx.TE_CENTRE, mask = "##:##", validRegex   = "[0-2][0-9]:[0-5][0-9]")
        self.ctrl_heure.SetCtrlParameters(invalidBackgroundColour = "PINK")
        self.label_avis = wx.StaticText(self.panel, -1, _(u"Avis :"))
        listeImages = [ (_(u"Avis inconnu"), "Smiley_question.png"), (_(u"Pas convaincant"), "Smiley_nul.png"), (_(u"Mitigé"), "Smiley_bof.png"), (_(u"Bien"), "Smiley_bien.png"), (_(u"Très bien"), "Smiley_genial.png"),]
        self.ctrl_avis = BitmapComboBox(self.panel, listeImages=listeImages)
        self.label_remarques = wx.StaticText(self.panel, -1, _(u"Commentaire :"))
        self.ctrl_remarques = wx.TextCtrl(self.panel, -1, "", style=wx.TE_MULTILINE)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
        
        if self.IDentretien != None : 
            self.Importation()
            
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def __set_properties(self):
        nom_complet = self.GetNomCandidat(self.IDcandidat, self.IDpersonne)
        if self.IDentretien == None :
            type = _(u"Saisie")
        else:
            type = _(u"Modification")
        if nom_complet == " None" : 
            self.SetTitle(_(u"%s d'un entretien") % type)
        else:
            self.SetTitle(_(u"%s d'un entretien pour %s") % (type, nom_complet))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.ctrl_date.SetToolTip(wx.ToolTip(_(u"Saisissez la date de l'entretien")))
        self.ctrl_heure.SetToolTip(wx.ToolTip(_(u"Saisissez l'heure de l'entretien")))
        self.ctrl_avis.SetToolTip(wx.ToolTip(_(u"Sélectionnez une appréciation de l'entretien")))
        self.ctrl_remarques.SetToolTip(wx.ToolTip(_(u"Saisissez l'avis complet émis après l'entretien")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider la saisie des données")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((450, 330))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        sizer_contenu = wx.StaticBoxSizer(self.sizer_contenu_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_date = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_contenu.Add(self.label_date, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date.Add(self.ctrl_date, 0, 0, 0)
        grid_sizer_date.Add((20, 20), 0, 0, 0)
        grid_sizer_date.Add(self.label_heure, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_date.Add(self.ctrl_heure, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_date, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_avis, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_avis, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_remarques, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_contenu.Add(self.ctrl_remarques, 0, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(2)
        grid_sizer_contenu.AddGrowableCol(1)
        sizer_contenu.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.panel.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.Centre()

    def OnContextMenu(self, event):
        pass
        
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
    
    def Importation(self):
        DB = GestionDB.DB()
        req = "SELECT IDentretien, IDcandidat, IDpersonne, date, heure, avis, remarques FROM entretiens WHERE IDentretien=%d" % self.IDentretien
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()[0]
        DB.Close()
        if len(donnees) == 0: return
        # Récupération des données
        IDentretien, IDcandidat, IDpersonne, date, heure, avis, remarques = donnees
        # Date
        self.SetDatePicker(self.ctrl_date, datetime.date(year=int(date[:4]), month=int(date[5:7]), day=int(date[8:10])))
        # Heure
        self.ctrl_heure.SetValue(heure)
        # Avis
        self.ctrl_avis.SetSelection(avis)
        # Remarques
        self.ctrl_remarques.SetValue(remarques)


    def Sauvegarde(self):
        """ Sauvegarde des données dans la base de données """
        
        # Récupération ds valeurs saisies
        date = self.GetDatePickerValue(self.ctrl_date)
        heure = self.ctrl_heure.GetValue()
        avis = self.ctrl_avis.GetSelection()
        remarques = self.ctrl_remarques.GetValue()

        DB = GestionDB.DB()
        # Création de la liste des données
        listeDonnees = [    ("IDcandidat",   self.IDcandidat),  
                                    ("IDpersonne",   self.IDpersonne),
                                    ("date",   date),
                                    ("heure",   heure),
                                    ("avis",   avis),
                                    ("remarques",   remarques),
                                    ]
        if self.IDentretien == None :
            # Enregistrement d'une nouvelle valeur
            newID = DB.ReqInsert("entretiens", listeDonnees)
            ID = newID
        else:
            # Modification de la valeur
            DB.ReqMAJ("entretiens", listeDonnees, "IDentretien", self.IDentretien)
            ID = self.IDentretien
        DB.Commit()
        DB.Close()
        return ID

    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def OnBoutonAide(self, event):
##        FonctionsPerso.Aide(39)
        dlg = wx.MessageDialog(self, _(u"L'aide du module Recrutement est en cours de rédaction.\nElle sera disponible lors d'une mise à jour ultérieure."), "Aide indisponible", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBoutonAnnuler(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    def OnBoutonOk(self, event):
        """ Validation des données saisies """
        
        heure = self.ctrl_heure.GetValue()
        if heure == "" or heure == "  :  " :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure"), "Erreur", wx.OK)  
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure.SetFocus()
            return
        
        # Sauvegarde
        self.Sauvegarde()
        
        # MAJ parents
        parent = self.GetParent()
        if parent.GetName() == "OL_entretiens" or parent.GetName() == "OL_gadget_entretiens":
            parent.MAJ()
        
        if parent.GetName() == "OL_gadget_entretiens" :
            parent.GetGrandParent().GetGrandParent().MAJpanel()
            
        try :
            if parent.GetGrandParent().GetParent().GetName() == "Recrutement" :
                parent.GetGrandParent().GetParent().gadget_entretiens.MAJ()
                parent.GetGrandParent().GetParent().gadget_informations.MAJ()
        except :
            pass
        
        try :
            if self.GetGrandParent().GetParent().GetName() == "panel_resume" :
                panelRecrutement = self.GetGrandParent().GetGrandParent().GetGrandParent()
                panelRecrutement.MAJpanel(MAJpanelResume=False)
                self.GetGrandParent().GetParent().MAJlabelsPages("entretiens")
        except :
            pass
            
            
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()

    def GetNomCandidat(self, IDcandidat=None, IDpersonne=None):
        # Récupération des données
        DB = GestionDB.DB()
        if IDpersonne == None or IDpersonne == 0 : 
            req = """SELECT civilite, nom, prenom
            FROM candidats WHERE IDcandidat=%d; """ % IDcandidat
        else:
            req = """SELECT civilite, nom, prenom
            FROM personnes WHERE IDpersonne=%d; """ % IDpersonne
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return ""
        civilite, nom, prenom = listeDonnees[0]
        return u"%s %s" % (nom, prenom)
    

class BitmapComboBox(BitmapComboBox):
    def __init__(self, parent, listeImages=[], size=(-1,  -1) ):
        BitmapComboBox.__init__(self, parent, size=size, style=wx.CB_READONLY)
        # Remplissage des items avec les images
        for texte, nomImage in listeImages :
            img = wx.Bitmap(Chemins.GetStaticPath("Images/22x22/%s" % nomImage), wx.BITMAP_TYPE_ANY)
            self.Append(texte, img, texte)
        # Sélection par défaut
        self.Select(0)
        


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, IDentretien=None)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
