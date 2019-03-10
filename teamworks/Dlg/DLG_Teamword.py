#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
"""
        listeValeurs = [ ("{NOM}", _(u"DUPOND")), ("{PRENOM}", _(u"Noémie")), ]
        
        POUR FAIRE UN APERCU AVEC VALEURS :
        self.Publipostage_preview(listeValeurs)
        
        POUR FAIRE UNE IMPRESSION AVEC VALEURS :
        self.Publipostage_impression(listeValeurs, nbre_exemplaires=1, nom_imprimante=None)
        
        POUR ENVOYER UN EMAIL AVEC VALEURS :
        self.Publipostage_mail(listeValeurs)

"""
import wx
from Utils import UTILS_Adaptations
import wx.aui
import wx.richtext as rt
from wx.html import HtmlEasyPrinting
import FonctionsPerso
import os
from Dlg import DLG_Saisie_url
from Dlg import DLG_Parametres_mail


REPERTOIRE_IMAGES = Chemins.GetStaticPath("Images/Teamword/")
IMAGES = {
    "nouveau" : "nouveau.png", 
    "ouvrir" : "ouvrir.png",
    "sauvegarder" : "sauvegarder.png",
    "couper" : "couper.png",
    "copier" : "copier.png",
    "coller" : "coller.png",
    "annuler" : "annuler.png",
    "repeter" : "repeter.png",
    "gras" : "gras.png",
    "italique" : "italique.png",
    "souligne" : "souligne.png",
    "aligner_gauche" : "aligner_gauche.png",
    "aligner_centre" : "aligner_centre.png",
    "aligner_droit" : "aligner_droit.png",
    "retrait_gauche" : "retrait_gauche.png",
    "retrait_droit" : "retrait_droit.png",
    "police" : "police.png",
    "police_couleur" : "police_couleur.png",
    "augmenter_police" : "augmenter_police.png",
    "diminuer_police" : "diminuer_police.png",
    "importer_image" : "importer_image.png",
    "espaceParagrapheMoins" : "espaceParagrapheMoins.png",
    "espaceParagraphePlus" : "espaceParagraphePlus.png",
    "interligne_simple" : "interligne_simple.png",
    "interligne_demi" : "interligne_demi.png",
    "interligne_double" : "interligne_double.png",
    "imprimer" : "imprimer.png",
    "apercu" : "Apercu.png",
    "mail" : "mail.png",
    "rechercher" : "rechercher.png",
    "remplacer" : "remplacer.png",
    "inserer_url" : "url.png",
    }
    

class Printer(HtmlEasyPrinting):
    def __init__(self, source="", titre=""):
        HtmlEasyPrinting.__init__(self)
        self.source = source
        self.titre = titre

    def Print(self):
        if self.titre != "" : self.SetHeader(self.titre)
        self.PrintText(self.source, self.titre)

    def Preview(self):
        if self.titre != "" : self.SetHeader(self.titre)
        HtmlEasyPrinting.PreviewText(self, self.source)


class PanelMotsCles(wx.Panel):
    def __init__(self, parent, id=-1, listeMotsCles=[]):
        wx.Panel.__init__(self, parent, id, style=wx.TAB_TRAVERSAL, name="panel_motscles")
        self.SetBackgroundColour((122, 161, 230))
        self.listeMotsCles = listeMotsCles
        
        texteIntro = _(u"Double-cliquez sur les mot-clés disponibles dans la liste ci-dessous pour les incorporer directement dans votre document.")
        self.label_introduction = FonctionsPerso.StaticWrapText(self, -1, texteIntro)
        
        self.ctrl_motscles = wx.ListBox(self, -1, choices=self.listeMotsCles, style=wx.SIMPLE_BORDER)
        self.ctrl_motscles.SetBackgroundColour((214, 223, 247))
        
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_introduction, 1, wx.EXPAND | wx.TOP|wx.LEFT|wx.RIGHT, 10)
        grid_sizer_base.Add(self.ctrl_motscles, 1, wx.EXPAND | wx.ALL, 10)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.SetAutoLayout(True)
        
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnInsertMotcle, self.ctrl_motscles)
        
    def OnInsertMotcle(self, event):
        index = event.GetSelection()
        motcle = self.listeMotsCles[index]
        self.GetParent().rtc.WriteText(motcle)




class MyRichTextCtrl(rt.RichTextCtrl):
    def __init__(self, parent, id=-1, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER):
        rt.RichTextCtrl.__init__(self, parent, id=id, style=style)
    
    def GetCheminFichier(self):
        return self.GetFilename()
        
    def GetNomFichier(self):
        cheminFichier = self.GetCheminFichier()
        if cheminFichier == "" :
            return _(u"Nouveau Document")
        else:
            nomFichier = os.path.basename(cheminFichier)
            return nomFichier
        
        
        
        
class MyFrame(wx.Frame):
    def __init__(self, parent, motsCles=[], size=(800, 600)):
        wx.Frame.__init__(self, parent, -1, title=_(u"Teamword"), name="frm_Teamword", size=size, style=wx.DEFAULT_FRAME_STYLE|wx.CLIP_CHILDREN)
        wx.Locale(wx.LANGUAGE_FRENCH)
        self.motsCles = motsCles # [_(u"{CIVILITE}"), _(u"{NOM}"), _(u"{PRENOM}"),]
        
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        
        self.AddRTCHandlers()
        self.MakeMenuBar()
        self.toolbar1 = self.MakeToolBar1()
        self.toolbar2 = self.MakeToolBar2()
        self.ActiveOutils(False)
        
        self.CreateStatusBar()
        self.SetStatusText(_(u"Bienvenue dans l'éditeur de texte de Teamworks"))
        
        # Création du notebook
        self.nb = wx.aui.AuiNotebook(self, style=wx.aui.AUI_NB_BOTTOM | wx.aui.AUI_NB_DEFAULT_STYLE)
        self.pages = []
        self.rtc = None
        
        # Création du RichTextCtrl
##        rtc = MyRichTextCtrl(self)
##        self.nb.AddPage(rtc, rtc.GetNomFichier())
##        wx.CallAfter(self.rtc.SetFocus)
        
##        textAttr = rt.RichTextAttr()
##        textAttr.SetFontFaceName(self.nomPolice)
##        textAttr.SetFontSize(self.taillePolice)
##        self.rtc.SetBasicStyle(textAttr)
        
##        print self.rtc.GetBasicStyle()
        
        self.positionDepartRecherche = 0
        
        # Création des panels détachables
        self.panelMotscles = PanelMotsCles(self, listeMotsCles=self.motsCles)
        self.panelMail = DLG_Parametres_mail.Panel(self)
        
        # Création des panels amovibles
        self._mgr.AddPane(self.panelMotscles, wx.aui.AuiPaneInfo().
                          Name("motscles").Caption(_(u"Liste des mots-clés")).
                          Left().Layer(1).Position(1).CloseButton(True).MaximizeButton(True).MinSize((160, -1)))
        
        self._mgr.AddPane(self.panelMail, wx.aui.AuiPaneInfo().
                          Name("mail").Caption(_(u"Paramètres d'envoi par mail")).
                          Right().Layer(1).Position(1).CloseButton(True).MaximizeButton(True).MinSize((250, -1)))
        
        # Création du panel central
        self._mgr.AddPane(self.nb, wx.aui.AuiPaneInfo().Name("editor").
                          CenterPane())
        
        # Création des barres d'outils
        self._mgr.AddPane(self.toolbar1, wx.aui.AuiPaneInfo().
                          Name("toolbar1").Caption("barre d'outils 1").
                          ToolbarPane().Top().
                          LeftDockable(False).RightDockable(False))
        
        self._mgr.AddPane(self.toolbar2, wx.aui.AuiPaneInfo().
                          Name("toolbar12").Caption("barre d'outils 2").
                          ToolbarPane().Top().Row(1).
                          LeftDockable(False).RightDockable(False))
        
        
        self._mgr.GetPane("editor").Show()
        if len(self.motsCles) > 0 :
            self._mgr.GetPane("motscles").Show()
        else:
            self._mgr.GetPane("motscles").Hide()
        
        self._mgr.GetPane("mail").Hide()
        self._mgr.Update()
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        # Boîte de dialogue Rechercher
        self.Bind(wx.EVT_FIND, self.OnFind)
        self.Bind(wx.EVT_FIND_NEXT, self.OnFind)
        self.Bind(wx.EVT_FIND_REPLACE, self.OnFind)
        self.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnFind)
        self.Bind(wx.EVT_FIND_CLOSE, self.OnFindClose)
        # Notebook
        self.nb.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChanged) 
        self.nb.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClose)

        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.CenterOnScreen()
        
    def OnPageChanged(self, event):
        index = event.GetSelection()
        page = self.nb.GetPage(index)
        self.rtc = page
        event.Skip()

    def OnClose(self, event):
        self.Quitter()

    def OnFileCreate(self, evt):
##        buffer = self.rtc.GetBuffer()
##        p = buffer.GetChildren()[0]
##        image = p.FindObjectAtPosition(0)
##        image.SetMargins(30, 30, 30, 30)
##        print image.GetRect()
##        print image.GetImage()
##        print image.GetImageBlock()
        
        self.CreateNewFile()
        
        
    def CreateNewFile(self, cheminModele=None):
        # Création du richTextCtrl
        rtc = MyRichTextCtrl(self)
        # Ouverture d'un modèle
        if cheminModele != None :
            rtc.LoadFile(cheminModele, type=wx.richtext.RICHTEXT_TYPE_ANY)
            rtc.SetFilename("")
        # Création de la page notebook
        self.nb.AddPage(rtc, rtc.GetNomFichier())
        self.nb.SetSelection(self.nb.GetPageCount()-1)
        wx.CallAfter(rtc.SetFocus)
        self.ActiveOutils(True)
                
    def OnPageClose(self, event):
        etat = self.CloseFile()
        if etat == False :
            event.Veto()
                
    def OnFileClose(self, evt):
        etat = self.CloseFile()
        if etat == True :
            self.nb.DeletePage(self.nb.GetSelection()) 
    
    def CloseFile(self, rtc=None, enregistrer=True):
        if rtc == None :
            rtc = self.rtc
        if enregistrer==True and rtc.IsModified() and rtc.IsEmpty() == False :
            dlg = wx.MessageDialog(self, _(u"Le document n'a pas été sauvegardé depuis la dernière modification.\n\nSouhaitez-vous le sauvegarder maintenant ?"),  _(u"Fermeture du document"), wx.ICON_QUESTION | wx.YES_NO | wx.CANCEL | wx.YES_DEFAULT)
            resultat = dlg.ShowModal()
            dlg.Destroy() 
            if resultat == wx.ID_YES :
                self.SauvegarderFichier()
            elif resultat == wx.ID_NO  :
                pass
            else :
                return False
        if self.nb.GetPageCount() == 1 : 
            self.rtc = None
            self.ActiveOutils(False)
            self._mgr.GetPane("mail").Hide()
            self._mgr.Update()
        return True

    def OnFileOpen(self, evt):
        
        wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=False)
        dlg = wx.FileDialog(self, _(u"Choisissez un fichier à ouvrir"), wildcard=wildcard, style=wx.OPEN)
        dlg.SetFilterIndex(2)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path:
                fileType = types[dlg.GetFilterIndex()]
                self.OpenFile(path)
        dlg.Destroy()
    
    def OpenFile(self, cheminFichier=""):
        # Création du richTextCtrl
        rtc = MyRichTextCtrl(self)
        rtc.LoadFile(cheminFichier, type=wx.richtext.RICHTEXT_TYPE_ANY)
        # Création de la page notebook
        self.nb.AddPage(rtc, rtc.GetNomFichier())
        self.nb.SetSelection(self.nb.GetPageCount()-1)
        wx.CallAfter(rtc.SetFocus)
        # Active menu et toolbar
        self.ActiveOutils(True)
        
    def OnFileSave(self, evt):
        self.SauvegarderFichier()
        
    def SauvegarderFichier(self):
        if not self.rtc.GetFilename():
            self.FileSaveAs()
            return
        self.rtc.SaveFile()
    
    def OnFileSaveAs(self, event):
        self.FileSaveAs()
        
    def FileSaveAs(self, cheminFichier=None):
        if cheminFichier == None :
            wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=True)
            dlg = wx.FileDialog(self, _(u"Sauvegardez le fichier"), wildcard=wildcard, style=wx.SAVE)
            dlg.SetFilterIndex(3)
            if dlg.ShowModal() == wx.ID_OK:
                cheminFichier = dlg.GetPath()
                if cheminFichier :
                    fileType = types[dlg.GetFilterIndex()]
                    ext = rt.RichTextBuffer.FindHandlerByType(fileType).GetExtension()
                    if not cheminFichier.endswith(ext):
                        cheminFichier += '.' + ext
                dlg.Destroy()
            else:
                dlg.Destroy()
                return False            
        self.rtc.SaveFile(cheminFichier, wx.richtext.RICHTEXT_TYPE_ANY)
        self.nb.SetPageText(self.nb.GetSelection(), self.rtc.GetNomFichier())
        

    def OnFileExit(self, evt):
        self.Quitter() 
    
    def Quitter(self, enregistrer=True):
        # Ferme tous les fichiers ouverts
        for index in range(0, self.nb.GetPageCount()) :
            rtc = self.nb.GetPage(index)
            if enregistrer == True :
                self.CloseFile(rtc)
##            if self.OnFileClose(None) == False :
##                return False
##            self.Close(True)
        # Quitter Teamword
        self._mgr.UnInit()
        del self._mgr
        self.Destroy()
        
    def OnAide(self, event):
        dlg = wx.MessageDialog(self, _(u"L'aide pour ce nouveau module est en cours de rédaction."), _(u"Aide indisponible"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return
        FonctionsPerso.Aide(37)
    
    def OnFileViewHTML(self, evt):
        # Get an instance of the html file handler, use it to save the
        # document to a StringIO stream, and then display the
        # resulting html text in a dialog with a HtmlWindow.
        handler = rt.RichTextHTMLHandler()
        handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_MEMORY)
        handler.SetFontSizeMapping([7,9,11,12,14,22,100])

        import cStringIO
        stream = cStringIO.StringIO()
        if not handler.SaveStream(self.rtc.GetBuffer(), stream):
            return
        
        source = stream.getvalue()
        head = """
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /> 
</head>
        """
        source = source.replace("<head></head>", head)
        source = source.decode("utf-8")
        
        import wx.html
        dlg = wx.Dialog(self, title="HTML", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        html = wx.html.HtmlWindow(dlg, size=(500,400), style=wx.BORDER_SUNKEN)
        html.SetPage(source)
        btn = wx.Button(dlg, wx.ID_CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(btn, 0, wx.ALL|wx.CENTER, 10)
        dlg.SetSizer(sizer)
        sizer.Fit(dlg)

        dlg.ShowModal()

        handler.DeleteTemporaryImages()
    
    def GetHtmlText(self, imagesIncluses=True):
        # Récupération de la source HTML
        handler = rt.RichTextHTMLHandler()
        if imagesIncluses == True : 
            handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_BASE64)
        else:
            handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_MEMORY)
        handler.SetFontSizeMapping([7,9,11,12,14,22,100])
        import cStringIO
        stream = cStringIO.StringIO()
        if self.rtc == None and self.nb.GetPageCount()>0 :
            self.rtc = self.nb.GetPage(self.nb.GetSelection())
        if not handler.SaveStream(self.rtc.GetBuffer(), stream):
            return False
        source = stream.getvalue()
        head = """
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /> 
</head>
        """
        source = source.replace("<head></head>", head)
        source = source.decode("utf-8")
        return source
        
    def OnMail(self, event):
        self._mgr.GetPane("mail").Show()
        self._mgr.Update()
                
    def Mailer(self, listeValeurs=[], adresseExpediteur="",listeDestinataires=[],
                    listeDestinairesCC=[], objet="", listePiecesJointes=[], nomServeur="") :
        # Récupération de la source HTML
        handler = rt.RichTextHTMLHandler()
        handler.SetFlags(rt.RICHTEXT_HANDLER_SAVE_IMAGES_TO_BASE64)
        handler.SetFontSizeMapping([7,9,11,12,14,22,100])
        import cStringIO
        stream = cStringIO.StringIO()
        if not handler.SaveStream(self.rtc.GetBuffer(), stream):
            return False
        texteHtml = stream.getvalue()
        head = """
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /> 
</head>
        """
        texteHtml = texteHtml.replace("<head></head>", head)
        texteHtml = texteHtml.decode("utf-8")
        
        # Intégration de la couleur de fond de page
        couleurFond = "#000000"
        texteHtml = texteHtml.replace("<body>", """<body bgcolor="%s">""" % couleurFond)
        
        # Intégration des valeurs si mots-clés
        if len(listeValeurs) != 0 :
            texteHtml = self.RemplacementMotscles(texteHtml, listeValeurs)

        # Crée le mail
        FonctionsPerso.Envoi_mail_smtp(adresseExpediteur, listeDestinaires, listeDestinairesCC, objet, texteHtml, listePiecesJointes, nomServeur)
        
        # Efface les images temporaires
        handler.DeleteTemporaryImages() 
    
    def RemplaceMotsclesPreview(self, texteHtml="", listeValeurs=[]):
        for motCle, valeur in listeValeurs :
            texteHtml = texteHtml.replace(motCle, valeur)
        return texteHtml
    
    def Publipostage_impression(self, nbre_exemplaires=1, nom_imprimante=None):
        """ Fonction d'impression sans boîte de dialogue pour le publipostage """
        # Initialisation de l'impression
        printout = wx.richtext.RichTextPrintout()
        printout.SetRichTextBuffer(self.rtc.GetBuffer()) 
        data = wx.PrintDialogData() 
        data.SetAllPages(True)
        data.SetCollate(True) # Pour assembler les pages
        # définit les paramètres de l'impression
        datapr = wx.PrintData()
        datapr.SetNoCopies(nbre_exemplaires)
        if nom_imprimante != None :
            datapr.SetPrinterName(nom_imprimante)
        data.SetPrintData(datapr)
        # Impression
        printer = wx.Printer(data) 
        printer.Print(self, printout, False) 
        
        # Ancienne version
##        texteHtml = self.GetHtmlText()
##        if len(listeValeurs) > 0 :
##            texteHtml = self.RemplaceMotsclesPreview(texteHtml, listeValeurs)
##        printout = wx.html.HtmlPrintout() 
##        printout.SetHtmlText(texteHtml) 
##        data = wx.PrintDialogData() 
##        data.SetAllPages(True)
##        data.SetCollate(True) # Pour assembler les pages
##        # définit les paramètres de l'impression
##        datapr = wx.PrintData()
##        datapr.SetNoCopies(nbre_exemplaires)
##        if nom_imprimante != None :
##            datapr.SetPrinterName(nom_imprimante)
##        data.SetPrintData(datapr)
##        # Impression
##        printer = wx.Printer(data) 
##        printer.Print(self, printout, False) # Mettre True pour afficher boîte de dialogue
        
    def OnPreview(self, event):
        self.Preview()
    
    def Publipostage_preview(self) :
        self.Preview()
        
    def Preview(self):
##        rtp = rt.RichTextPrinting("Print test")
##        buf = self.rtc.GetBuffer()
##        rtp.PrintBuffer(buf)
##        return
        printout1 = wx.richtext.RichTextPrintout()
        printout1.SetRichTextBuffer(self.rtc.GetBuffer()) 
        printout2 = wx.richtext.RichTextPrintout()
        printout2.SetRichTextBuffer(self.rtc.GetBuffer()) 
        data = wx.PrintDialogData() 
        data.SetAllPages(True)
        data.SetCollate(True) # Pour assembler les pages
        # définit les paramètres de l'impression
        datapr = wx.PrintData()
        data.SetPrintData(datapr)
        # Impression
        preview = wx.PrintPreview(printout1, printout2, data)
        if not preview.Ok():
            print("Probleme dans le preview du richTextCtrl.")
            return
        pfrm = wx.PreviewFrame(preview, self, _(u"Aperçu avant impression"))
        pfrm.Initialize()
        pfrm.SetPosition(self.GetPosition())
        pfrm.SetSize(self.GetSize())
        pfrm.Show(True)       
        
    
##        # Ancienne version
##        texteHtml=self.GetHtmlText()
##        if len(listeValeurs) != 0 :
##            texteHtml = self.RemplacementMotscles(texteHtml, listeValeurs)
##        p = Printer(texteHtml)
##        p.Preview()
    
    def OnPrint(self, event):
        printout = wx.richtext.RichTextPrintout() #wx.html.HtmlPrintout() 
        printout.SetRichTextBuffer(self.rtc.GetBuffer()) 
        data = wx.PrintDialogData() 
        data.SetAllPages(True)
        data.SetCollate(True) # Pour assembler les pages
        # définit les paramètres de l'impression
        datapr = wx.PrintData()
##        datapr.SetNoCopies(nbre_exemplaires)
##        if nom_imprimante != None :
##            datapr.SetPrinterName(nom_imprimante)
        data.SetPrintData(datapr)
        # Impression
        printer = wx.Printer(data) 
        printer.Print(self, printout, True) 
        
##        rtp = rt.RichTextPrinting("Print test")
##        rtp.PageSetup()
##        rtp.PrintBuffer(self.rtc.GetBuffer())
##        return
##
##        p = Printer(source=self.GetHtmlText())
##        p.Print()
        
    def OnRechercher(self, event):
        self.positionDepartRecherche = 0
        data = wx.FindReplaceData()
        dlg = wx.FindReplaceDialog(self, data, _(u"Rechercher"))
        dlg.data = data
        dlg.Show(True)

    def OnRemplacer(self, event):
        self.positionDepartRecherche = 0
        data = wx.FindReplaceData()
        dlg = wx.FindReplaceDialog(self, data, _(u"Rechercher et remplacer"), wx.FR_REPLACEDIALOG)
        dlg.data = data
        dlg.Show(True)
        
    def Rechercher(self, texteRecherche="") :
        positionDepart = self.positionDepartRecherche
        listeRanges = []
        precedentRange = rt.RichTextRange(0, 0)
        for position in range(positionDepart, self.rtc.GetLastPosition()) :
            self.rtc.SelectWord(position)
            mot = self.rtc.GetStringSelection()
            longueurMot= len(mot)
            actualRange = self.rtc.GetSelectionRange()
            if actualRange != precedentRange :
                # Inclus aussi les accolades dans la recherche
                try :
                    motComplet = self.rtc.GetRange(actualRange.GetStart()-1, actualRange.GetEnd()+1) 
                except :
                    motComplet = ""
                if motComplet != "" :
                    if motComplet[0] == "{" and motComplet[-1] == "}" :
                        mot = motComplet
                        actualRange = rt.RichTextRange(actualRange.GetStart()-1, actualRange.GetEnd()+1)
                if mot == texteRecherche :
                    # Le mot a été trouvé :
                    self.rtc.ShowPosition(actualRange.GetEnd())
                    return actualRange
                precedentRange = actualRange
        return None
    
    def RemplaceMotscles(self, listeValeurs=[]) :
        # Remplacement durant édition
        for motCle, valeur in listeValeurs :
            actualRange = ""
            nbreRemplacements = 0
            self.positionDepartRecherche = 0
            while actualRange != None :
                # Recherche
                actualRange = self.Rechercher(motCle)
                if actualRange != None :
                    # Remplacement du mot
                    r1 = rt.RichTextRange(actualRange.GetStart(), actualRange.GetEnd())
                    self.rtc.Delete(r1)
                    self.rtc.SetInsertionPoint(actualRange.GetStart())
                    self.rtc.WriteText(valeur)
                    #self.rtc.Replace(actualRange.GetStart()-1, actualRange.GetEnd(), valeur)
                    self.positionDepartRecherche = actualRange.GetStart() + len(valeur) + 1
                    nbreRemplacements += 1
        self.rtc.SetInsertionPoint(0)
        self.rtc.ShowPosition(0)
    
    def OnFind(self, event):
        map = {
            wx.wxEVT_COMMAND_FIND : "FIND",
            wx.wxEVT_COMMAND_FIND_NEXT : "FIND_NEXT",
            wx.wxEVT_COMMAND_FIND_REPLACE : "REPLACE",
            wx.wxEVT_COMMAND_FIND_REPLACE_ALL : "REPLACE_ALL",
            }
        et = event.GetEventType()
        if et in map:
            evtType = map[et]
        else:
            evtType = "**Unknown Event Type**"
        if et in [wx.wxEVT_COMMAND_FIND_REPLACE, wx.wxEVT_COMMAND_FIND_REPLACE_ALL]:
            replaceTxt = "Replace text: %s" % event.GetReplaceString()
        else:
            replaceTxt = ""
##        print "%s -- Find text: %s   Replace text: %s  Flags: %d" % (evtType, event.GetFindString(), replaceTxt, event.GetFlags())
        
        if et != wx.wxEVT_COMMAND_FIND_REPLACE_ALL :
            
            # Processus de recherche
            texteRecherche = event.GetFindString()
            actualRange = self.Rechercher(texteRecherche)
            if actualRange != None :
                self.positionDepartRecherche = actualRange.GetEnd() + 1
            else:
                dlg = wx.MessageDialog(self, _(u"Aucun résultat n'a été trouvé."), _(u"Recherche"), wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            
            # Remplacement unique
            if et == wx.wxEVT_COMMAND_FIND_REPLACE :
                if actualRange != None :
                    # Remplacement du mot
                    texteRemplacement = event.GetReplaceString()
                    self.rtc.Replace(actualRange.GetStart(), actualRange.GetEnd(), texteRemplacement)
        
        else:
            
            # Remplacement multiple
            texteRecherche = event.GetFindString()
            texteRemplacement = event.GetReplaceString()
            actualRange = ""
            nbreRemplacements = 0
            while actualRange != None :
                # Recherche
                actualRange = self.Rechercher(texteRecherche)
                if actualRange != None :
                    self.positionDepartRecherche = actualRange.GetEnd() + 1
                    # Remplacement du mot
                    self.rtc.Replace(actualRange.GetStart(), actualRange.GetEnd(), texteRemplacement)
                    nbreRemplacements += 1
            if nbreRemplacements == 0 :
                texteInfo = _(u"Aucun remplacement n'a été effectué.")
            else:
                texteInfo = _(u"%d remplacements ont été effectués.") % nbreRemplacements
            dlg = wx.MessageDialog(self, texteInfo, _(u"Remplacement terminé"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()


    def OnFindClose(self, evt):
        self.positionDepartRecherche = 0
        evt.GetDialog().Destroy()

# ---------------------------------------

    def OnURL(self, evt):
        wx.MessageBox(evt.GetString(), "URL Clicked")
        

##    def OnFileOpen(self, evt):
##        # This gives us a string suitable for the file dialog based on
##        # the file handlers that are loaded
##        wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=False)
##        dlg = wx.FileDialog(self, "Choose a filename",
##                            wildcard=wildcard,
##                            style=wx.OPEN)
##        if dlg.ShowModal() == wx.ID_OK:
##            path = dlg.GetPath()
##            if path:
##                fileType = types[dlg.GetFilterIndex()]
##                self.rtc.LoadFile(path, fileType)
##        dlg.Destroy()
##
##        
##    def OnFileSave(self, evt):
##        if not self.rtc.GetFilename():
##            self.OnFileSaveAs(evt)
##            return
##        self.rtc.SaveFile()
##
##        
##    def OnFileSaveAs(self, evt):
##        wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=True)
##
##        dlg = wx.FileDialog(self, "Choose a filename",
##                            wildcard=wildcard,
##                            style=wx.SAVE)
##        if dlg.ShowModal() == wx.ID_OK:
##            path = dlg.GetPath()
##            if path:
##                fileType = types[dlg.GetFilterIndex()]
##                ext = rt.RichTextBuffer.FindHandlerByType(fileType).GetExtension()
##                if not path.endswith(ext):
##                    path += '.' + ext
##                self.rtc.SaveFile(path, fileType)
##        dlg.Destroy()
        
    
      
    def OnBold(self, evt):
        self.rtc.ApplyBoldToSelection()
        
    def OnItalic(self, evt): 
        self.rtc.ApplyItalicToSelection()
        
    def OnUnderline(self, evt):
        self.rtc.ApplyUnderlineToSelection()
        
    def OnAlignLeft(self, evt):
        self.rtc.ApplyAlignmentToSelection(wx.TEXT_ALIGNMENT_LEFT)
        
    def OnAlignRight(self, evt):
        self.rtc.ApplyAlignmentToSelection(wx.TEXT_ALIGNMENT_RIGHT)
        
    def OnAlignCenter(self, evt):
        self.rtc.ApplyAlignmentToSelection(wx.TEXT_ALIGNMENT_CENTRE)
        
    def OnIndentMore(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LEFT_INDENT)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetLeftIndent(attr.GetLeftIndent() + 100)
            attr.SetFlags(wx.TEXT_ATTR_LEFT_INDENT)
            self.rtc.SetStyle(r, attr)
       
        
    def OnIndentLess(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LEFT_INDENT)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

        if attr.GetLeftIndent() >= 100:
            attr.SetLeftIndent(attr.GetLeftIndent() - 100)
            attr.SetFlags(wx.TEXT_ATTR_LEFT_INDENT)
            self.rtc.SetStyle(r, attr)

        
    def OnParagraphSpacingMore(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_PARA_SPACING_AFTER)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetParagraphSpacingAfter(attr.GetParagraphSpacingAfter() + 20);
            attr.SetFlags(wx.TEXT_ATTR_PARA_SPACING_AFTER)
            self.rtc.SetStyle(r, attr)

        
    def OnParagraphSpacingLess(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_PARA_SPACING_AFTER)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            if attr.GetParagraphSpacingAfter() >= 20:
                attr.SetParagraphSpacingAfter(attr.GetParagraphSpacingAfter() - 20);
                attr.SetFlags(wx.TEXT_ATTR_PARA_SPACING_AFTER)
                self.rtc.SetStyle(r, attr)

        
    def OnLineSpacingSingle(self, evt): 
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(10)
            self.rtc.SetStyle(r, attr)
 
                
    def OnLineSpacingHalf(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(15)
            self.rtc.SetStyle(r, attr)

        
    def OnLineSpacingDouble(self, evt):
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
        ip = self.rtc.GetInsertionPoint()
        if self.rtc.GetStyle(ip, attr):
            r = rt.RichTextRange(ip, ip)
            if self.rtc.HasSelection():
                r = self.rtc.GetSelectionRange()

            attr.SetFlags(wx.TEXT_ATTR_LINE_SPACING)
            attr.SetLineSpacing(20)
            self.rtc.SetStyle(r, attr)


    def OnFont(self, evt):
        if not self.rtc.HasSelection():
            dlg = wx.MessageDialog(self, _(u"Vous devez d'abord sélectionner un texte."), _(u"Police"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        r = self.rtc.GetSelectionRange()
        fontData = wx.FontData()
        fontData.EnableEffects(False)
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_FONT)
        if self.rtc.GetStyle(self.rtc.GetInsertionPoint(), attr):
            fontData.SetInitialFont(attr.GetFont())

        dlg = wx.FontDialog(self, fontData)
        if dlg.ShowModal() == wx.ID_OK:
            fontData = dlg.GetFontData()
            font = fontData.GetChosenFont()
            if font:
                attr.SetFlags(wx.TEXT_ATTR_FONT)
                attr.SetFont(font)
                self.rtc.SetStyle(r, attr)
        dlg.Destroy()


    def OnColour(self, evt):
        colourData = wx.ColourData()
        attr = rt.RichTextAttr()
        attr.SetFlags(wx.TEXT_ATTR_TEXT_COLOUR)
        if self.rtc.GetStyle(self.rtc.GetInsertionPoint(), attr):
            colourData.SetColour(attr.GetTextColour())

        dlg = wx.ColourDialog(self, colourData)
        if dlg.ShowModal() == wx.ID_OK:
            colourData = dlg.GetColourData()
            colour = colourData.GetColour()
            if colour:
                if not self.rtc.HasSelection():
                    self.rtc.BeginTextColour(colour)
                else:
                    r = self.rtc.GetSelectionRange()
                    attr.SetFlags(wx.TEXT_ATTR_TEXT_COLOUR)
                    attr.SetTextColour(colour)
                    self.rtc.SetStyle(r, attr)
        dlg.Destroy()
        


    def OnUpdateBold(self, evt):
        if self.rtc == None : return
        evt.Check(self.rtc.IsSelectionBold())
    
    def OnUpdateItalic(self, evt):
        if self.rtc == None : return
        evt.Check(self.rtc.IsSelectionItalics())
    
    def OnUpdateUnderline(self, evt): 
        if self.rtc == None : return
        evt.Check(self.rtc.IsSelectionUnderlined())
    
    def OnUpdateAlignLeft(self, evt):
        if self.rtc == None : return
        evt.Check(self.rtc.IsSelectionAligned(wx.TEXT_ALIGNMENT_LEFT))
        
    def OnUpdateAlignCenter(self, evt):
        if self.rtc == None : return
        evt.Check(self.rtc.IsSelectionAligned(wx.TEXT_ALIGNMENT_CENTRE))
        
    def OnUpdateAlignRight(self, evt):
        if self.rtc == None : return
        evt.Check(self.rtc.IsSelectionAligned(wx.TEXT_ALIGNMENT_RIGHT))
    
    def ForwardEvent(self, evt):
        if self.rtc == None : return
        self.rtc.ProcessEvent(evt)

    def OnInsererURL(self, event):
        dlg = DLG_Saisie_url.MyDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            label = dlg.GetLabel()
            URL = dlg.GetURL()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        urlStyle = rt.RichTextAttr()
        urlStyle.SetTextColour(wx.BLUE)
        urlStyle.SetFontUnderlined(True)
        self.rtc.BeginStyle(urlStyle)
        self.rtc.BeginURL(URL)
        self.rtc.WriteText(label)
        self.rtc.EndURL()
        self.rtc.EndStyle()

    def OnImporterImage(self, event):
        # Sélection d'une image
        self.repCourant = os.getcwd()
        wildcard = "Image JPEG (*.jpg)|*.jpg|"     \
                        "Image PNG (*.png)|*.png|"     \
                        "Image GIF (*.gif)|*.gif|"     \
           "All files (*.*)|*.*"
        # Récupération du chemin des documents
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        # Ouverture de la fenêtre de dialogue
        dlg = wx.FileDialog(
            self, message=_(u"Choisissez une image"),
            defaultDir=cheminDefaut, 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN
            )
        if dlg.ShowModal() == wx.ID_OK:
            nomFichierCourt = dlg.GetFilename()
            nomFichierLong = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # Recadre la photo
        from Dlg import DLG_Editeur_photo2
        dlg = DLG_Editeur_photo2.MyDialog(self, image=nomFichierLong, titre=_(u"Redimensionnez l'image si vous le souhaitez"))
        if dlg.ShowModal() == wx.ID_OK:
            bmp = dlg.GetBmp()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return 
        
        self.rtc.WriteBitmap(bmp, bitmapType=wx.BITMAP_TYPE_BMP)
        
        
    def EcritTexteTest(self):
        self.rtc.Freeze()
        self.rtc.BeginSuppressUndo()

        self.rtc.BeginParagraphSpacing(0, 20)

        self.rtc.BeginAlignment(wx.TEXT_ALIGNMENT_CENTRE)
        self.rtc.BeginBold()

        self.rtc.BeginFontSize(14)
        self.rtc.WriteText("Welcome to wxRichTextCtrl, {NOM} {PRENOM} {AGE} a wxWidgets control for editing and presenting styled text and images")
        self.rtc.EndFontSize()
        self.rtc.Newline()

        self.rtc.BeginItalic()
        self.rtc.WriteText("by {NOM} {PRENOM} {AGE} ans")
        self.rtc.EndItalic()

        self.rtc.EndBold()

        self.rtc.Newline()
        img1 = wx.Bitmap(Chemins.GetStaticPath("Images/Special/Logo_accueil.png"), wx.BITMAP_TYPE_ANY)
        self.rtc.WriteBitmap(img1)

        self.rtc.Newline()
        self.rtc.Newline()

        self.rtc.WriteText("What can you do with this thing? ")
##        self.rtc.WriteImage(images._rt_smiley.GetImage())
        self.rtc.WriteText(" Well, you can change text ")
        
        self.rtc.EndAlignment()
        
        self.rtc.BeginTextColour((255, 0, 0))
        self.rtc.WriteText("colour, like this red bit.")
        self.rtc.EndTextColour()

        self.rtc.BeginTextColour((0, 0, 255))
        self.rtc.WriteText(" And this blue bit.")
        self.rtc.EndTextColour()

        self.rtc.WriteText(" Naturally you can make things {NOM} {PRENOM} {AGE} ")
        self.rtc.BeginBold()
        self.rtc.WriteText("bold ")
        self.rtc.EndBold()
        self.rtc.BeginItalic()
        self.rtc.WriteText("or italic ")
        self.rtc.EndItalic()
        self.rtc.BeginUnderline()
        self.rtc.WriteText("or underlined.")
        self.rtc.EndUnderline()

        self.rtc.BeginFontSize(14)
        self.rtc.WriteText(" Different font sizes on the same line is allowed, too.")
        self.rtc.EndFontSize()

        self.rtc.WriteText(" Next we'll show an indented paragraph.")

        self.rtc.BeginLeftIndent(60)
        self.rtc.Newline()

        self.rtc.WriteText("It was in January, the most down-trodden month of an Edinburgh winter. An attractive woman came into the cafe, which is nothing remarkable.")
        self.rtc.EndLeftIndent()

        self.rtc.Newline()

        self.rtc.WriteText("Next, we'll show a first-line indent, achieved using BeginLeftIndent(100, -40).")

        self.rtc.BeginLeftIndent(100, -40)
        self.rtc.Newline()

        self.rtc.WriteText("It was in January, the most down-trodden month of an Edinburgh winter. An attractive woman came into the cafe, which is nothing remarkable.")
        self.rtc.EndLeftIndent()

        self.rtc.Newline()

        self.rtc.WriteText("Numbered bullets are possible, again using sub-indents:")

        self.rtc.BeginNumberedBullet(1, 100, 60)
        self.rtc.Newline()

        self.rtc.WriteText("This is my first item. Note that wxRichTextCtrl doesn't automatically do numbering, but this will be added later.")
        self.rtc.EndNumberedBullet()

        self.rtc.BeginNumberedBullet(2, 100, 60)
        self.rtc.Newline()

        self.rtc.WriteText("This is my second item.")
        self.rtc.EndNumberedBullet()

        self.rtc.Newline()

        self.rtc.WriteText("The following paragraph is right-indented:")

        self.rtc.BeginRightIndent(200)
        self.rtc.Newline()

        self.rtc.WriteText("It was in January, the most down-trodden month of an Edinburgh winter. An attractive woman came into the cafe, which is nothing remarkable.")
        self.rtc.EndRightIndent()

        self.rtc.Newline()

        self.rtc.WriteText("The following paragraph is right-aligned with 1.5 line spacing:")

        self.rtc.BeginAlignment(wx.TEXT_ALIGNMENT_RIGHT)
        self.rtc.BeginLineSpacing(wx.TEXT_ATTR_LINE_SPACING_HALF)
        self.rtc.Newline()

        self.rtc.WriteText("It was in January, the most down-trodden month of an Edinburgh winter. An attractive woman came into the cafe, which is nothing remarkable.")
        self.rtc.EndLineSpacing()
        self.rtc.EndAlignment()

        self.rtc.Newline()
        self.rtc.WriteText("Other notable features of wxRichTextCtrl include:")

        self.rtc.BeginSymbolBullet('*', 100, 60)
        self.rtc.Newline()
        self.rtc.WriteText("Compatibility with wxTextCtrl API")
        self.rtc.EndSymbolBullet()

        self.rtc.BeginSymbolBullet('*', 100, 60)
        self.rtc.Newline()
        self.rtc.WriteText("Easy stack-based BeginXXX()...EndXXX() style setting in addition to SetStyle()")
        self.rtc.EndSymbolBullet()

        self.rtc.BeginSymbolBullet('*', 100, 60)
        self.rtc.Newline()
        self.rtc.WriteText("XML loading and saving")
        self.rtc.EndSymbolBullet()

        self.rtc.BeginSymbolBullet('*', 100, 60)
        self.rtc.Newline()
        self.rtc.WriteText("Undo/Redo, with batching option and Undo suppressing")
        self.rtc.EndSymbolBullet()

        self.rtc.BeginSymbolBullet('*', 100, 60)
        self.rtc.Newline()
        self.rtc.WriteText("Clipboard copy and paste")
        self.rtc.EndSymbolBullet()

        self.rtc.BeginSymbolBullet('*', 100, 60)
        self.rtc.Newline()
        self.rtc.WriteText("wxRichTextStyleSheet with named character and paragraph styles, and control for applying named styles")
        self.rtc.EndSymbolBullet()

        self.rtc.BeginSymbolBullet('*', 100, 60)
        self.rtc.Newline()
        self.rtc.WriteText("A design that can easily be extended to other content types, ultimately with text boxes, tables, controls, and so on")
        self.rtc.EndSymbolBullet()

        self.rtc.BeginSymbolBullet('*', 100, 60)
        self.rtc.Newline()

        # Make a style suitable for showing a URL
        urlStyle = rt.RichTextAttr()
        urlStyle.SetTextColour(wx.BLUE)
        urlStyle.SetFontUnderlined(True)
        self.rtc.BeginStyle(urlStyle)
        self.rtc.BeginURL("http://wxPython.org/")
        self.rtc.WriteText("The wxPython Web Site")
        self.rtc.EndURL();
        self.rtc.EndStyle();
        self.rtc.Bind(wx.EVT_TEXT_URL, self.OnURL)
        
        self.rtc.Newline()
        self.rtc.WriteText("Note: this sample content was generated programmatically from within the MyFrame constructor in the demo. The images were loaded from inline XPMs. Enjoy wxRichTextCtrl!")

        self.rtc.EndParagraphSpacing()

        self.rtc.EndSuppressUndo()
        self.rtc.Thaw()
        
    def ActiveOutils(self, etat=True):
        # Menu
        menuBar = self.GetMenuBar() 
        for id in range(300, 323+1):
            menuBar.Enable(id, etat)
        menuBar.Enable(wx.ID_CUT, etat)
        menuBar.Enable(wx.ID_COPY, etat)
        menuBar.Enable(wx.ID_PASTE, etat)
        menuBar.Enable(wx.ID_CLEAR, etat)
        menuBar.Enable(wx.ID_UNDO, etat)
        menuBar.Enable(wx.ID_REDO, etat) 
        menuBar.Enable(wx.ID_SELECTALL, etat)
        # Toolbar 1
        for id in range(100, 105+1):
            self.toolbar1.EnableTool(id, etat)
        self.toolbar1.EnableTool(wx.ID_CUT, etat)
        self.toolbar1.EnableTool(wx.ID_COPY, etat)
        self.toolbar1.EnableTool(wx.ID_PASTE, etat)
        self.toolbar1.EnableTool(wx.ID_UNDO, etat)
        self.toolbar1.EnableTool(wx.ID_REDO, etat) 
        # Toolbar 2
        for id in range(200, 222+1):
            self.toolbar2.EnableTool(id, etat)
        
        
        
        
    def MakeMenuBar(self):
        def doBind(item, handler, updateUI=None):
            self.Bind(wx.EVT_MENU, handler, item)
            if updateUI is not None:
                self.Bind(wx.EVT_UPDATE_UI, updateUI, item)
        
        fileMenu = UTILS_Adaptations.Menu()
        doBind( fileMenu.Append(400, _(u"Nouveau\tCtrl+N"), _(u"Créer un nouveau document")), self.OnFileCreate )
        doBind( fileMenu.Append(401, _(u"Ouvrir\tCtrl+O"), _(u"Ouvrir un document")), self.OnFileOpen )
        doBind( fileMenu.Append(322, _(u"Fermer"), _(u"Fermer le document")), self.OnFileClose )
        doBind( fileMenu.Append(300, _(u"Sauvegarder\tCtrl+S"), _(u"Sauvegarder")), self.OnFileSave )
        doBind( fileMenu.Append(301, _(u"Sauvegarder sous..."), _(u"Sauvegarder sous...")), self.OnFileSaveAs )
        fileMenu.AppendSeparator()
        doBind( fileMenu.Append(323, _(u"Envoyer par Email"), _(u"Envoyer par Email...")), self.OnMail )
        fileMenu.AppendSeparator()
        doBind( fileMenu.Append(302, _(u"Aperçu avant impression"), _(u"Aperçu avant impression")), self.OnPreview)
        doBind( fileMenu.Append(303, _(u"Imprimer"), _(u"Imprimer")), self.OnPrint)
        fileMenu.AppendSeparator()
        doBind( fileMenu.Append(403, _(u"Quitter\tCtrl+Q"), _(u"Quitter Teamword")), self.OnFileExit )
        
        editMenu = UTILS_Adaptations.Menu()
        doBind( editMenu.Append(wx.ID_UNDO, _(u"Annuler\tCtrl+Z")), self.ForwardEvent, self.ForwardEvent)
        doBind( editMenu.Append(wx.ID_REDO, _(u"Répéter\tCtrl+Y")), self.ForwardEvent, self.ForwardEvent )
        editMenu.AppendSeparator()
        doBind( editMenu.Append(wx.ID_CUT, _(u"Couper\tCtrl+X")), self.ForwardEvent, self.ForwardEvent )
        doBind( editMenu.Append(wx.ID_COPY, _(u"Copier\tCtrl+C")), self.ForwardEvent, self.ForwardEvent)
        doBind( editMenu.Append(wx.ID_PASTE, _(u"Coller\tCtrl+V")), self.ForwardEvent, self.ForwardEvent)
        doBind( editMenu.Append(wx.ID_CLEAR, _(u"Supprimer\tDel")), self.ForwardEvent, self.ForwardEvent)
        editMenu.AppendSeparator()
        doBind( editMenu.Append(304, _(u"Rechercher\tCtrl+F"), _(u"Rechercher")), self.OnRechercher )
        doBind( editMenu.Append(305, _(u"Remplacer\tCtrl+H"), _(u"Remplacer")), self.OnRemplacer )
        editMenu.AppendSeparator()
        doBind( editMenu.Append(wx.ID_SELECTALL, _(u"Tout sélectionner\tCtrl+A")), self.ForwardEvent, self.ForwardEvent )
        
        #doBind( editMenu.AppendSeparator(),  )
        #doBind( editMenu.Append(-1, "&Find...\tCtrl+F"),  )
        #doBind( editMenu.Append(-1, "&Replace...\tCtrl+R"),  )

        formatMenu = UTILS_Adaptations.Menu()
        doBind( formatMenu.Append(306, _(u"Police...")), self.OnFont)
        formatMenu.AppendSeparator()
        doBind( formatMenu.AppendCheckItem(307, _(u"Gras\tCtrl+B")), self.OnBold, self.OnUpdateBold)
        doBind( formatMenu.AppendCheckItem(308, _(u"Italique\tCtrl+I")), self.OnItalic, self.OnUpdateItalic)
        doBind( formatMenu.AppendCheckItem(309, _(u"Souligné\tCtrl+U")), self.OnUnderline, self.OnUpdateUnderline)
        formatMenu.AppendSeparator()
        doBind( formatMenu.AppendCheckItem(310, _(u"Aligner à gauche")), self.OnAlignLeft, self.OnUpdateAlignLeft)
        doBind( formatMenu.AppendCheckItem(311, _(u"Centrer")), self.OnAlignCenter, self.OnUpdateAlignCenter)
        doBind( formatMenu.AppendCheckItem(312, _(u"Aligner à droite")), self.OnAlignRight, self.OnUpdateAlignRight)
        formatMenu.AppendSeparator()
        doBind( formatMenu.Append(313, _(u"Diminuer le retrait")), self.OnIndentMore)
        doBind( formatMenu.Append(314, _(u"Augmenter le retrait")), self.OnIndentLess)
        formatMenu.AppendSeparator()
        doBind( formatMenu.Append(315, _(u"Augmenter l'espacement des paragraphes")), self.OnParagraphSpacingMore)
        doBind( formatMenu.Append(316, _(u"Dininuer l'espacement des paragraphes")), self.OnParagraphSpacingLess)
        formatMenu.AppendSeparator()
        doBind( formatMenu.Append(317, _(u"Interligne simple")), self.OnLineSpacingSingle)
        doBind( formatMenu.Append(318, _(u"Interligne 1.5")), self.OnLineSpacingHalf)
        doBind( formatMenu.Append(319, _(u"Interligne double")), self.OnLineSpacingDouble)
        
        insertionMenu = UTILS_Adaptations.Menu()
        doBind( insertionMenu.Append(320, _(u"Insérer une URL")), self.OnInsererURL)
        doBind( insertionMenu.Append(321, _(u"Insérer une image")), self.OnImporterImage)
                
        aideMenu = UTILS_Adaptations.Menu()
        doBind( aideMenu.Append(404, _(u"Aide\tF1")), self.OnAide)
        
        mb = wx.MenuBar()
        mb.Append(fileMenu, _(u"Fichier"))
        mb.Append(editMenu, _(u"Edition"))
        mb.Append(formatMenu, _(u"Format"))
        mb.Append(insertionMenu, _(u"Insertion"))
        mb.Append(aideMenu, _(u"Aide"))
        self.SetMenuBar(mb)

    def CreateImage(self, nomImage):
        return wx.Bitmap(REPERTOIRE_IMAGES + IMAGES[nomImage], wx.BITMAP_TYPE_ANY)
        
    def MakeToolBar1(self):
        def doBind(item, handler, updateUI=None):
            self.Bind(wx.EVT_TOOL, handler, item)
            if updateUI is not None:
                self.Bind(wx.EVT_UPDATE_UI, updateUI, item)
        
        tbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.TB_FLAT | wx.TB_NODIVIDER)
        tbar.SetToolBitmapSize(wx.Size(16,16))
        doBind( tbar.AddTool(405, self.CreateImage("nouveau"), shortHelpString=u")Créer un nouveau document"), self.OnFileCreate)
        doBind( tbar.AddTool(406, self.CreateImage("ouvrir"), shortHelpString=_(u"Ouvrir un document")), self.OnFileOpen)
        doBind( tbar.AddTool(100, self.CreateImage("sauvegarder"), shortHelpString=_(u"Sauvegarder le document")), self.OnFileSave)
        tbar.AddSeparator()
        doBind( tbar.AddTool(101, self.CreateImage("mail"), shortHelpString=_(u"Envoyer par mail")), self.OnMail)
        tbar.AddSeparator()
        doBind( tbar.AddTool(102, self.CreateImage("imprimer"), shortHelpString=_(u"Imprimer le document")), self.OnPrint)
        doBind( tbar.AddTool(103, self.CreateImage("apercu"), shortHelpString=u")Aperçu avant impression"), self.OnPreview)
        tbar.AddSeparator()
        doBind( tbar.AddTool(wx.ID_CUT, self.CreateImage("couper"), shortHelpString=_(u"Couper")), self.ForwardEvent, self.ForwardEvent)
        doBind( tbar.AddTool(wx.ID_COPY, self.CreateImage("copier"), shortHelpString=_(u"Copier")), self.ForwardEvent, self.ForwardEvent)
        doBind( tbar.AddTool(wx.ID_PASTE, self.CreateImage("coller"), shortHelpString=_(u"Coller")), self.ForwardEvent, self.ForwardEvent)
        tbar.AddSeparator()
        doBind( tbar.AddTool(wx.ID_UNDO, self.CreateImage("annuler"), shortHelpString=_(u"Annuler")), self.ForwardEvent, self.ForwardEvent)
        doBind( tbar.AddTool(wx.ID_REDO, self.CreateImage("repeter"), shortHelpString=_(u"Répéter")), self.ForwardEvent, self.ForwardEvent)
        tbar.AddSeparator()
        doBind( tbar.AddTool(104, self.CreateImage("rechercher"), shortHelpString=_(u"Rechercher dans ce document")), self.OnRechercher)
        doBind( tbar.AddTool(105, self.CreateImage("remplacer"), shortHelpString=_(u"Rechercher et remplacer...")), self.OnRemplacer)

#doBind( editMenu.AppendSeparator(),  )
        #doBind( editMenu.Append(-1, "&Find...\tCtrl+F"),  )
        #doBind( editMenu.Append(-1, "&Replace...\tCtrl+R"),  )
        
        tbar.Realize()
        return tbar

    def MakeToolBar2(self):
        def doBind(item, handler, updateUI=None):
            self.Bind(wx.EVT_TOOL, handler, item)
            if updateUI is not None:
                self.Bind(wx.EVT_UPDATE_UI, updateUI, item)
        
        tbar = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.TB_FLAT | wx.TB_NODIVIDER)
        tbar.SetToolBitmapSize(wx.Size(16,16))
        
        doBind( tbar.AddTool(200, self.CreateImage("police"), shortHelpString=_(u"Police")), self.OnFont)
        doBind( tbar.AddTool(201, self.CreateImage("police_couleur"), shortHelpString=_(u"Couleur de la police")), self.OnColour)
        tbar.AddSeparator()
        doBind( tbar.AddTool(202, self.CreateImage("gras"), isToggle=True, shortHelpString=_(u"Gras")), self.OnBold, self.OnUpdateBold)
        doBind( tbar.AddTool(203, self.CreateImage("italique"), isToggle=True, shortHelpString=_(u"Italique")), self.OnItalic, self.OnUpdateItalic)
        doBind( tbar.AddTool(204, self.CreateImage("souligne"), isToggle=True, shortHelpString=_(u"Souligné")), self.OnUnderline, self.OnUpdateUnderline)
        tbar.AddSeparator()
        doBind( tbar.AddTool(205, self.CreateImage("aligner_gauche"), isToggle=True, shortHelpString=_(u"Aligner à gauche")), self.OnAlignLeft, self.OnUpdateAlignLeft)
        doBind( tbar.AddTool(206, self.CreateImage("aligner_centre"), isToggle=True, shortHelpString=_(u"Centrer")), self.OnAlignCenter, self.OnUpdateAlignCenter)
        doBind( tbar.AddTool(207, self.CreateImage("aligner_droit"), isToggle=True, shortHelpString=_(u"Aligner à droite")), self.OnAlignRight, self.OnUpdateAlignRight)
        tbar.AddSeparator()
        doBind( tbar.AddTool(208, self.CreateImage("retrait_gauche"), shortHelpString=_(u"Diminuer le retrait")), self.OnIndentLess)
        doBind( tbar.AddTool(209, self.CreateImage("retrait_droit"), shortHelpString=_(u"Augmenter le retrait")), self.OnIndentMore)
        tbar.AddSeparator()
        doBind( tbar.AddTool(210, self.CreateImage("espaceParagraphePlus"), shortHelpString=_(u"Augmenter l'espacement des paragraphes")), self.OnParagraphSpacingMore)
        doBind( tbar.AddTool(211, self.CreateImage("espaceParagrapheMoins"), shortHelpString=_(u"Dininuer l'espacement des paragraphes")), self.OnParagraphSpacingLess)
        tbar.AddSeparator()
        doBind( tbar.AddTool(212, self.CreateImage("interligne_simple"), shortHelpString=_(u"Interligne simple")), self.OnLineSpacingSingle)
        doBind( tbar.AddTool(213, self.CreateImage("interligne_demi"), shortHelpString=_(u"Interligne 1.5")), self.OnLineSpacingHalf)
        doBind( tbar.AddTool(214, self.CreateImage("interligne_double"), shortHelpString=_(u"Interligne double")), self.OnLineSpacingDouble)
        tbar.AddSeparator()
        doBind( tbar.AddTool(221, self.CreateImage("inserer_url"), shortHelpString=_(u"Insérer une URL")), self.OnInsererURL)
        doBind( tbar.AddTool(222, self.CreateImage("importer_image"), shortHelpString=_(u"Insérer une image")), self.OnImporterImage)

        tbar.Realize()
        return tbar

    def AddRTCHandlers(self):
        # make sure we haven't already added them.
        if rt.RichTextBuffer.FindHandlerByType(rt.RICHTEXT_TYPE_HTML) is not None:
            return
        # This would normally go in your app's OnInit method.  I'm
        # not sure why these file handlers are not loaded by
        # default by the C++ richtext code, I guess it's so you
        # can change the name or extension if you wanted...
        rt.RichTextBuffer.AddHandler(rt.RichTextHTMLHandler())
        rt.RichTextBuffer.AddHandler(rt.RichTextXMLHandler())
        # ...like this
        rt.RichTextBuffer.AddHandler(rt.RichTextXMLHandler(name="Teamword", ext="twd", type=99))
        # This is needed for the view as HTML option since we tell it
        # to store the images in the memory file system.
        wx.FileSystem.AddHandler(wx.MemoryFSHandler())




class Publipostage_Teamword():
    """ Procédure de publipostage TEAMWORD """
    def __init__(self, parent): 
        # Chargement
        self.erreur = None
    
    def OuvertureLogiciel(self):
        try : 
            self.Twd = MyFrame(None)
##            self.Twd.Show() 
        except Exception as err :
            print("Erreur dans l'ouverture de Teamword : %s" % err)
            self.erreur = _(u"Impossible d'ouvrir Teamword")
            self.QuitterLogiciel()
        
    def CreationDocument(self, cheminModele=None):
        """ Création d'un nouveau document """
        try :
            # Création d'un nouveau document
            self.Twd.CreateNewFile(cheminModele)
            #self.doc = self.Word.ActiveDocument
        except Exception as err :
            print("Erreur dans creation du nouveau du document : %s" % err)
            self.erreur = _(u"Impossible de créer un nouveau du document")
            self.QuitterLogiciel()
    
    def RemplacementValeurs(self, listeValeurs=[]):
        """ Remplacements des mots-clés par les valeurs """
        try :
            self.Twd.RemplaceMotscles(listeValeurs)
        except Exception as err :
            print("Erreur dans le remplacement des valeurs du document : %s" % err)
            self.erreur = _(u"Impossible de remplacer les valeurs")
            self.QuitterLogiciel()
            
    def SauvegardeDocument(self, cheminDoc=None):
        """ Sauvegarde du document """
        try :
            self.Twd.FileSaveAs(cheminDoc)
        except Exception as err :
            print("Erreur dans la sauvegarde du document : %s" % err)
            self.erreur = _(u"Impossible de sauvegarder le document")
            self.QuitterLogiciel()
            
    def ImprimerDocument(self, nom_imprimante=None, nbre_exemplaires=1):
        """ Impression du document """
        try :
            # Impression
            Publipostage_impression(nbre_exemplaires, nom_imprimante)
        except Exception as err :
            print("Erreur dans l'impression du document : %s" % err)
            self.erreur = _(u"Impossible d'imprimer le document")
            self.QuitterLogiciel()
            
    def ApercuDocument(self):
        """ Apercu du document """
        try :
##            self.Twd.Show()
            pass
        except Exception as err :
            print("Erreur dans la creation de l'apercu du document : %s" % err)
            self.erreur = _(u"Impossible de créer un aperçu du document")
            self.QuitterLogiciel()
    
    def FermerDocument(self):
        """ Fermeture du document """
        try : 
            self.Twd.CloseFile()
        except Exception as err :
            print("Erreur dans la fermeture du document : %s" % err)
            self.erreur = _(u"Impossible de fermer le document")
            self.QuitterLogiciel()
            
    def QuitterLogiciel(self):
        """ Quitter Word """
        try :
            self.Twd.Quitter()
        except Exception as err :
            print("Erreur dans la fermeture de Teamword : %s" % err)
            self.erreur = _(u"Impossible de quitter Teamword")            



            
            




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None)
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
    
