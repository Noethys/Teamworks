#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Utils import UTILS_Config
from Dlg import DLG_Financement
import webbrowser


def Aide(page=None):
    """ Ouverture de l'aide dans le navigateur """
    # None -> Renvoie vers le sommaire
    # "" -> Rubrique non disponible
    
    # R�cup�ration des codes de la licence
    identifiant = UTILS_Config.GetParametre("enregistrement_identifiant", defaut=None)
    code = UTILS_Config.GetParametre("enregistrement_code", defaut=None)
    
    # Redirection si aucune licence
    if identifiant == None and code == None :
        dlg = DLG_Financement.Dialog(None, code="documentation")
        dlg.ShowModal() 
        dlg.Destroy()
        return

    # Si aucune aide existe, propose de renvoyer vers le sommaire
    if page == "" :
        dlg = wx.MessageDialog(None, _(u"Cette rubrique d'aide n'est pas encore disponible.\n\nSouhaitez-vous �tre redirig� vers le sommaire de l'aide ?"), _(u"Pas de rubrique disponible"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

    # Cr�ation de l'URL
    listeOptions = []
    
    if identifiant != None and code != None :
        listeOptions.append("identifiant=%s" % identifiant)
        listeOptions.append("code=%s" % code)
        
    if page != None and page != "" :
        listeOptions.append("page=%s.php" % page)
        
    url = "https://www.teamworks.ovh/aide/html/identification.php"
    if len(listeOptions) > 0 :
        url += "?" + "&".join(listeOptions)
        
    # Ouverture du navigateur
    webbrowser.open(url)

    
if __name__ == "__main__":
    app = wx.App(0)
    Aide()
    app.MainLoop()
