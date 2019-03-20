#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-19 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
import os
import xlsxwriter
from Dlg import DLG_Selection_liste
import FonctionsPerso


def Excel(parent, labels_colonnes=[], liste_valeurs=[], tableau=None):
    if tableau == None:
        dlg = DLG_Selection_liste.Dialog(parent, labels_colonnes, liste_valeurs, type="exportExcel")
        if dlg.ShowModal() == wx.ID_OK:
            listeSelections = dlg.GetSelections()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False

    nomFichier = "ExportExcel.xlsx"

    # Demande à l'utilisateur le nom de fichier et le répertoire de destination
    wildcard = "Fichiers Excel (*.xlsx)|*.xlsx|Tous les fichiers (*.*)|*.*"
    sp = wx.StandardPaths.Get()
    cheminDefaut = sp.GetDocumentsDir()
    dlg = wx.FileDialog(
        parent, message=_(u"Veuillez sélectionner le répertoire de destination et le nom du fichier"),
        defaultDir=cheminDefaut,
        defaultFile=nomFichier,
        wildcard=wildcard,
        style=wx.FD_SAVE
    )
    dlg.SetFilterIndex(2)
    if dlg.ShowModal() == wx.ID_OK:
        cheminFichier = dlg.GetPath()
        dlg.Destroy()
    else:
        dlg.Destroy()
        return

    # Le fichier de destination existe déjà :
    if os.path.isfile(cheminFichier) == True:
        dlg = wx.MessageDialog(None, _(u"Un fichier portant ce nom existe déjà. \n\nVoulez-vous le remplacer ?"), "Attention !", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse == wx.ID_NO:
            return False

    # Création d'un classeur et d'une feuille
    workbook = xlsxwriter.Workbook(cheminFichier)
    worksheet = workbook.add_worksheet()

    # Depuis une liste de sélections
    if tableau == None:
        # Création des labels de colonnes
        x = 0
        y = 0
        for labelCol, alignement, largeur, nomChamp in labels_colonnes:
            worksheet.write(x, y, labelCol)
            worksheet.set_column(y, y, largeur * 0.2)
            y += 1

        x = 1
        y = 0
        for valeurs in liste_valeurs:
            if int(valeurs[0]) in listeSelections:
                for valeur in valeurs:
                    worksheet.write(x, y, valeur)
                    y += 1
                x += 1
                y = 0

    # Depuis une grid
    if tableau != None:
        # Remplissage de la feuille
        nbreColonnes = tableau.GetNumberCols()
        nbreLignes = tableau.GetNumberRows()

        for numLigne in range(0, nbreLignes):
            for numCol in range(0, nbreColonnes):
                valeurCase = tableau.GetCellValue(numLigne, numCol)
                worksheet.write(numLigne, numCol, valeurCase)

    # Finalisation du fichier xlsx
    workbook.close()

    # Confirmation de création du fichier et demande d'ouverture directe dans Excel
    txtMessage = _(u"Le fichier Excel a été créé avec succès. Souhaitez-vous l'ouvrir dès maintenant ?")
    dlgConfirm = wx.MessageDialog(parent, txtMessage, _(u"Confirmation"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
    reponse = dlgConfirm.ShowModal()
    dlgConfirm.Destroy()
    if reponse == wx.ID_NO:
        return
    else:
        FonctionsPerso.LanceFichierExterne(cheminFichier)
