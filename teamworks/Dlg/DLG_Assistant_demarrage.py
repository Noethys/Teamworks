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
from wx.lib import platebtn


# Pour contrer bug sur platebtn lors de la fermeture de la fenêtre
class MyPlateBtn(platebtn.PlateButton):
    def __init__(self, *args, **kwds):
        platebtn.PlateButton.__init__(self, *args, **kwds)

    def _SetState(self, state):
        self._state['pre'] = self._state['cur']
        self._state['cur'] = state
        try:
            if wx.Platform == '__WXMSW__':
                self.Parent.RefreshRect(self.Rect, False)
            else:
                self.Refresh()
        except:
            pass



class Dialog(wx.Dialog):
    def __init__(self, parent, checkAffichage=False, afficherDernierFichier=True, nomDernierFichier=""):
        wx.Dialog.__init__(self, parent, -1, title=_(u"Assistant de démarrage"), size=(730, -1))
        self.parent = parent
        self.choix = None
        
        # Version Reseau
        if "[RESEAU]" in nomDernierFichier :
            nomDernierFichier = nomDernierFichier[nomDernierFichier.index("[RESEAU]"):]
        
        self.label_intro = wx.StaticText(self, -1, _(u"Bienvenue dans TeamWorks !"))
        
        # Boutons de commande spéciaux
        self.listeCommandes = [
            [ 1, "", wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Bienvenue_video.png"), wx.BITMAP_TYPE_ANY), _(u"Visionner une vidéo de présentation de TeamWorks") ],
            [ 2, "", wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Bienvenue_nouveau.png"), wx.BITMAP_TYPE_ANY), _(u"Créer un nouveau fichier") ],
            [ 3, "", wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Bienvenue_tutoriels.png"), wx.BITMAP_TYPE_ANY), _(u"Découvrir en détail les fonctions principales de TeamWorks") ],
            [ 4, "", wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Bienvenue_ouvrir.png"), wx.BITMAP_TYPE_ANY), _(u"Ouvrir un fichier existant") ],
            [ 5, "", wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Bienvenue_exemple.png"), wx.BITMAP_TYPE_ANY), _(u"Charger le fichier Exemple") ],
            [ 6, "", wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Bienvenue_dernier.png"), wx.BITMAP_TYPE_ANY), _(u"Charger le dernier fichier ouvert : %s") % nomDernierFichier ],
            ]

        self.listeBoutons = []
        for index, label, img, infobulle in self.listeCommandes :
            bouton = MyPlateBtn(self, index, label, img)
            bouton.SetToolTip(wx.ToolTip(infobulle))
            self.Bind(wx.EVT_BUTTON, self.OnBoutonCommande, bouton)
            bouton.SetPressColor(wx.Colour(255, 255, 245))
            self.listeBoutons.append(bouton)

        if afficherDernierFichier == False :
            bouton.Show(False)
            
        self.check_affichage = wx.CheckBox(self, -1, _(u"Ne plus afficher"))
        self.check_affichage.SetValue(checkAffichage)
        
        # Boutons classiques
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/BoutonsImages/Fermer_assistant.png"), wx.BITMAP_TYPE_ANY))
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        self.bouton_ok.SetFocus()
        
        
    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_aide.SetSize(self.bouton_aide.GetBestSize())
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer l'assistant et utiliser TeamWorks")))
        self.bouton_ok.SetSize(self.bouton_ok.GetBestSize())
        self.check_affichage.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour ne plus faire apparaître cet assistant au démarrage de TeamWorks. \nLe dernier fichier utilisé sera alors automatiquement chargé au démarrage. \n\nRemarque : Il vous sera toujours possible de recharger l'assistant à partir du menu 'fichier'.")))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=0, hgap=0)
        
        # Intro
        grid_sizer_base.Add(self.label_intro, 1, wx.LEFT|wx.TOP|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_base.Add((15, 15), 0, 0, 0)
        
        # Commandes
        grid_sizer_commandes = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        for bouton in self.listeBoutons :
            grid_sizer_commandes.Add(bouton, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(grid_sizer_commandes, 1, wx.EXPAND | wx.LEFT, 30)
        
        # Check Ne plus afficher
        grid_sizer_base.Add((15, 15), 0, 0, 0)
        grid_sizer_base.Add(self.check_affichage, 1, wx.EXPAND | wx.ALL, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=2, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)

        grid_sizer_base.AddGrowableCol(0)
##        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        sizer_base.Add(self, 1, wx.EXPAND, 0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.Centre()       

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Assistantdemarrage")
        
    def OnBoutonCommande(self, event):
        self.choix = event.GetId()
        # Ferme la boîte de dialogue
        self.bouton_ok.SetFocus()
        self.EndModal(wx.ID_OK)

    def OnBoutonOk(self, event):
        """ Démarrage direct de TeamWorks """
        self.choix = None
        # Ferme la boîte de dialogue
        self.EndModal(wx.ID_OK)

    def GetChoix(self):
        return self.choix

    def GetCheckAffichage(self):
        return self.check_affichage.GetValue()
    
    
    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = Dialog(None, checkAffichage=False)
    frm.ShowModal()
    app.MainLoop()
