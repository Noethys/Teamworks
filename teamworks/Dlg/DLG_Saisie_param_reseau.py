#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Teamworks
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image



class Dialog(wx.Dialog):
    def __init__(self, parent, intro=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        
        if intro == None :
            intro = _(u"Veuillez saisir les param�tres de connexion :")

        self.box_contenu_staticbox = wx.StaticBox(self, -1, _(u"Param�tres de connexion"))
        self.label_intro = wx.StaticText(self, -1, intro)
        self.label_port = wx.StaticText(self, -1, _(u"Port :"))
        self.ctrl_port = wx.TextCtrl(self, -1, u"3306")
        self.label_hote = wx.StaticText(self, -1, _(u"H�te :"))
        self.ctrl_hote = wx.TextCtrl(self, -1, u"")
        self.label_utilisateur = wx.StaticText(self, -1, _(u"Utilisateur :"))
        self.ctrl_utilisateur = wx.TextCtrl(self, -1, u"")
        self.label_mdp = wx.StaticText(self, -1, _(u"Mot de passe :"))
        self.ctrl_mdp = wx.TextCtrl(self, -1, u"", style=wx.TE_PASSWORD)
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.SetTitle(_(u"Param�tres de connexion"))
        self.ctrl_port.SetMinSize((60, -1))
        self.ctrl_port.SetToolTip(wx.ToolTip("Saisissez ici le num�ro de port"))
        self.ctrl_hote.SetToolTip(wx.ToolTip("Saisissez ici l'h�te"))
        self.ctrl_utilisateur.SetToolTip(wx.ToolTip("Saisissez ici l'utilisateur"))
        self.ctrl_mdp.SetToolTip(wx.ToolTip("Saisissez ici le mot de passe"))
        self.bouton_aide.SetToolTip(wx.ToolTip("Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTip(wx.ToolTip("Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTip(wx.ToolTip("Cliquez ici pour annuler"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        box_contenu = wx.StaticBoxSizer(self.box_contenu_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 0, wx.ALL, 10)
        grid_sizer_contenu.Add(self.label_port, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_port, 0, 0, 0)
        grid_sizer_contenu.Add(self.label_hote, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_hote, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_utilisateur, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_utilisateur, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_mdp, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_mdp, 0, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        box_contenu.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetSize((400, -1))
        self.CenterOnScreen() 
        
    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event):
        port = self.ctrl_port.GetValue()
        hote = self.ctrl_hote.GetValue()
        user = self.ctrl_utilisateur.GetValue()
        mdp = self.ctrl_mdp.GetValue()
        
        # V�rification des infos saisies
        try :
            port = int(port)
        except Exception as err:
            dlg = wx.MessageDialog(self, _(u"Le num�ro de port n'est pas valide. \n\nErreur : %s") % err, _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_port.SetFocus()
            return
        
        if hote == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom pour le serveur h�te."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_hote.SetFocus()
            return
        
        if user == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un nom d'utilisateur."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_utilisateur.SetFocus()
            return
        
        if mdp == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir un mot de passe."), _(u"Erreur de saisie"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_mdp.SetFocus()
            return
                
        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetDictValeurs(self):
        port = int(self.ctrl_port.GetValue())
        hote = self.ctrl_hote.GetValue()
        utilisateur = self.ctrl_utilisateur.GetValue()
        mdp = self.ctrl_mdp.GetValue()
        dictValeurs = {"port":port, "host":hote, "hote":hote, "utilisateur":utilisateur, "user":utilisateur, "password":mdp, "mdp":mdp}
        return dictValeurs
      
      
    
def TestConnexion(dictValeurs={}):
    """ Test de connexion au r�seau MySQL """
    import MySQLdb
    try :
        connexion = MySQLdb.connect(host=dictValeurs["hote"],user=dictValeurs["utilisateur"], passwd=dictValeurs["mdp"], port=dictValeurs["port"], use_unicode=True) 
        cursor = connexion.cursor()
    except Exception as err :
        return False
    return True



if __name__ == _(u"__main__"):
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
