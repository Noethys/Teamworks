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
import six
import GestionDB

DICT_PROCEDURES = {
    "A2000": _(u"Conversion de la version 1 � la version 2 de Teamworks"),
    "D1062": _(u"Cr�ation des tables DATA"),
    }

# -------------------------------------------------------------------------------------------------------------------------

def Procedure(code=""):
    # Recherche si proc�dure existe
    if (code in DICT_PROCEDURES) == False :
        dlg = wx.MessageDialog(None, _(u"D�sol�, cette proc�dure n'existe pas..."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return
    titre = DICT_PROCEDURES[code]
    # Demande de confirmation de lancement
    dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment lancer la proc�dure suivante ?\n\n   -> %s   ") % titre, _(u"Lancement de la proc�dure"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
    reponse = dlg.ShowModal() 
    dlg.Destroy()
    if reponse != wx.ID_YES :
        return
    # Lancement
    print("Lancement de la procedure '%s'..." % code)
    try :
        exec("%s()" % code)
    except Exception as err :
        dlg = wx.MessageDialog(None, _(u"D�sol�, une erreur a �t� rencontr�e :\n\n-> %s  ") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return
    # Fin
    dlg = wx.MessageDialog(None, _(u"La proc�dure s'est termin�e avec succ�s."), _(u"Proc�dure termin�e"), wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()
    print("Fin de la procedure '%s'." % code)
    return

# -------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------


def A2000(nomFichier=None):
    """ Conversion vers version 2 de Teamworks """
    import os 
    from Data import DATA_Tables as Tables
    print("Conversion A2000 : TW1 -> TW2...")
    
    DB = GestionDB.DB(nomFichier=nomFichier)
    
    # R�cup�ration du nom du fichier
    nomFichier = DB.nomFichier
    
    # R�cup�ration de l'IDfichier
    req = """SELECT codeIDfichier
    FROM divers WHERE IDdivers=1;"""
    DB.ExecuterReq(req)
    listeTemp = DB.ResultatReq()
    IDfichier = listeTemp[0][0]
    DB.Close()
    
    # Cr�ation du fichier PHOTOS
    print("Creation table Photos...")
    DB = GestionDB.DB(suffixe="PHOTOS", nomFichier=nomFichier, modeCreation=True)
    DB.CreationTables(Tables.DB_PHOTOS)
    DB.Close()
    
    # Cr�ation de la base DOCUMENTS
    print("Creation table Documents...")
    DB = GestionDB.DB(suffixe="DOCUMENTS", nomFichier=nomFichier, modeCreation=True)
    DB.CreationTables(Tables.DB_DOCUMENTS)
    DB.Close()

    # R�cup�ration des photos du r�pertoire pour les mettre dans la table PHOTOS
    listeFichiersPhotos = os.listdir("Photos")
    DB = GestionDB.DB(suffixe="PHOTOS", nomFichier=nomFichier)
    print("Recherche et transfert des photos existantes...")
    for nomPhoto in listeFichiersPhotos :
        if IDfichier in nomPhoto and nomPhoto.endswith(".jpg") :
            IDpersonne = int(nomPhoto[len(IDfichier):-4])
            # R�cup�ration de la photo
            img = wx.Image("Photos/%s" % nomPhoto)
            buffer = six.BytesIO()
            img.SaveStream(buffer, wx.BITMAP_TYPE_JPEG)
            buffer.seek(0)
            blob = buffer.read()
            # Insertion de la photo dans la table PHOTOS
            IDphoto = DB.InsertPhoto(IDindividu=IDpersonne, blobPhoto=blob)
    DB.Close()

    print("Fin de la conversion A2000.")
    
def D1051(nomFichier=None):
    """ Cr�ation des champs dans la table DOCUMENTS """
    DB = GestionDB.DB(suffixe="DOCUMENTS", nomFichier=nomFichier) 
    DB.AjoutChamp("documents", "type", "VARCHAR(50)")
    DB.AjoutChamp("documents", "label", "VARCHAR(400)")
    DB.AjoutChamp("documents", "IDreponse", "INTEGER")
    DB.Close()

def D1062():
    """ Cr�ation des champs dans la table DOCUMENTS """
    from Data import DATA_Tables as Tables
    DB = GestionDB.DB()
    DB.CreationTables(Tables.DB_DATA)
    DB.Close()






if __name__ == _(u"__main__"):
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    # TEST D'UNE PROCEDURE :
    D1062()
    app.MainLoop()
