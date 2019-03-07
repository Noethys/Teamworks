#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:       Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ol import OL_contrats



class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Liste_contrats", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent

        intro = _(u"Vous pouvez ici consulter la liste de tous les contrats.")
        titre = _(u"Registre unique du personnel")
        self.SetTitle(titre)

        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage=Chemins.GetStaticPath("Images/32x32/Contrats.png"))
        self.ctrl_listview = OL_contrats.ListView(self, id=-1, modeAffichage="liste_contrats", activeMenuContextuel=False, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_listview.MAJ()
        self.ctrl_listview.SetMinSize((100, 100))
        self.ctrl_recherche = OL_contrats.CTRL_Outils(self, listview=self.ctrl_listview)

        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_texte = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_fermer = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Fermer_L72.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.ExportTexte, self.bouton_texte)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.ExportExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un aperçu de la liste")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste")))
        self.bouton_texte.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Texte")))
        self.bouton_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter la liste au format Excel")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((950, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        grid_sizer_gauche = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_gauche.Add(self.ctrl_listview, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)

        # Commandes
        grid_sizer_droit = wx.FlexGridSizer(rows=10, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_texte, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_excel, 0, 0, 0)

        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
