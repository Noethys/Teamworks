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
import wx.lib.mixins.listctrl  as  listmix
import GestionDB
import FonctionsPerso
import CTRL_Questionnaire


class Panel(wx.Panel):
    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID, style=wx.TAB_TRAVERSAL)
        
        # Titre et intro
        self.barreTitre = FonctionsPerso.BarreTitre(self,  _(u"Le questionnaire"), u"")
        texteIntro = _(u"Vous pouvez ici concevoir des questionnaires personnalisés pour les fiches\nindividuelles. Commencez par créer des catégories puis paramétrez des\nquestions basées sur les contrôles de votre choix en fonction des données à\nsaisir : texte, liste, entier, etc...")
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)

        # Questionnaire
        self.ctrl_questionnaire = CTRL_Questionnaire.CTRL(self, type="individu", menuActif=True, afficherInvisibles=True)
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_monter = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Fleche_haut.png", wx.BITMAP_TYPE_ANY))
        self.bouton_descendre = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Fleche_bas.png", wx.BITMAP_TYPE_ANY))

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonMonter, self.bouton_monter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDescendre, self.bouton_descendre)

        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter une catégorie ou une question"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier la catégorie ou la question sélectionnée"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer la catégorie ou la question sélectionnée"))
        self.bouton_monter.SetToolTipString(_(u"Cliquez ici pour monter la catégorie ou la question sélectionnée"))
        self.bouton_descendre.SetToolTipString(_(u"Cliquez ici pour descendre la catégorie ou la question sélectionnée"))

##        self.label_conclusion = wx.StaticText(self, -1, "Remarques...")

        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base2 = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.barreTitre, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.label_introduction, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        grid_sizer_base2.Add(self.ctrl_questionnaire, 1, wx.EXPAND, 0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=10)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_boutons.Add((5, 5), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_monter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_descendre, 0, 0, 0)
        grid_sizer_base2.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        grid_sizer_base2.AddGrowableRow(0)
        grid_sizer_base2.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_base2, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
##        grid_sizer_base.Add(self.label_conclusion, 0, 0, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.SetAutoLayout(True)

    def OnBoutonAjouter(self, event): 
        self.ctrl_questionnaire.Ajouter()

    def OnBoutonModifier(self, event): 
        self.ctrl_questionnaire.Modifier()

    def OnBoutonSupprimer(self, event):
        self.ctrl_questionnaire.Supprimer()

    def OnBoutonMonter(self, event): 
        self.ctrl_questionnaire.Monter()

    def OnBoutonDescendre(self, event): 
        self.ctrl_questionnaire.Descendre()
    
    def MAJpanel(self):
        self.ctrl_questionnaire.MAJ()



class MyFrame(wx.Frame):
    def __init__(self, parent, title="" ):
        wx.Frame.__init__(self, parent, -1, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.MakeModal(True)
        
        self.panel_base = wx.Panel(self, -1)
        self.panel_contenu = Panel(self.panel_base)
        self.panel_contenu.barreTitre.Show(False)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self.panel_base, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_annuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        self.SetMinSize((450, 450))
        self.SetSize((450, 450))

    def __set_properties(self):
        self.SetTitle(_(u"Paramétrage des questionnaires"))
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.bouton_annuler.SetToolTipString(_(u"Cliquez pour annuler et fermer"))
        self.bouton_annuler.SetSize(self.bouton_annuler.GetBestSize())
        

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.ALL|wx.EXPAND, 0)
        sizer_pages.Add(self.panel_contenu, 1, wx.EXPAND | wx.TOP, 10)
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
        self.Centre()
        self.sizer_pages = sizer_pages

    def OnClose(self, event):
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        event.Skip()
        
    def Onbouton_aide(self, event):
        FonctionsPerso.Aide(24)
            
    def Onbouton_annuler(self, event):
        # Si frame Creation_contrats ouverte, on met à jour le listCtrl Classification
        self.MAJparents()
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()
        
    def Onbouton_ok(self, event):
        # Si frame Creation_contrats ouverte, on met à jour le listCtrl Classification
        self.MAJparents()
        # Fermeture
        self.MakeModal(False)
        FonctionsPerso.SetModalFrameParente(self)
        self.Destroy()     

    def MAJparents(self):
        if FonctionsPerso.FrameOuverte("FicheIndividuelle") != None :
            self.GetParent().ImportListeSituations()

        
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()