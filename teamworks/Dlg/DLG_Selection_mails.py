#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
import re
import wx.lib.dialogs
import wx.lib.dialogs as dialogs
from Ol import OL_personnes
import wx.lib.agw.hyperlink as hl


class Hyperlink(hl.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="test", infobulle="test infobulle", URL="", size=(-1, -1), pos=(0, 0)):
        hl.HyperLinkCtrl.__init__(self, parent, id=id, label=label, URL=URL, size=size, pos=pos)
        self.SetBackgroundColour(wx.WHITE)
        # Construit l'hyperlink
        self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.EnableRollover(True)
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink)

    def OnLeftLink(self, event):
        if event.GetId() == 100: self.GetParent().listview.Rechercher()
        if event.GetId() == 200: self.GetParent().listview.AfficherTout()



class Page_Saisie_manuelle(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.maj_done = True

        # Contrôles
        self.ctrl = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
        self.ctrl.SetMinSize((10, 10))
        self.Bind(wx.EVT_TEXT, self.OnCheck, self.ctrl)
        self.ctrl.SetToolTip(wx.ToolTip(_(u"Saisissez manuellement des adresses emails en les séparant par des points-virgules (;)")))
        
        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.ctrl, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer)
        self.Layout()

    def MAJ(self):
        pass

    def OnCheck(self, event):
        self.parent.SetInfos("saisie_manuelle", self.GetDonnees())
    
    def GetAdresses(self):
        listeTemp = self.ctrl.GetValue().split(";")
        listeAdresses = []
        for texte in listeTemp :
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", texte) != None:
                listeAdresses.append(texte)
        return listeAdresses
    
    def Validation(self):
        return True
    
    def GetDonnees(self):
        texte = self.ctrl.GetValue()
        listeAdresses = self.GetAdresses() 
        dictDonnees = {
            "liste_adresses" : listeAdresses,
            "texte" : texte,
            }
        return dictDonnees
    
    def SetDonnees(self, dictDonnees={}):
        self.ctrl.SetValue(dictDonnees["texte"])
        self.OnCheck(None)
        
            
# -------------------------------------------------------------------------------------------------------------------------------------------

class OL_personnes_surcharge(OL_personnes.ListView):
    def __init__(self, *args, **kwds):
        OL_personnes.ListView.__init__(self, *args, **kwds)

    def OnCheck(self, track=None):
        self.GetParent().OnCheck(track)

    def SetIDcoches(self, listeID=[]):
        for track in self.donnees :
            if track.IDpersonne in listeID :
                self.Check(track)
                self.RefreshObject(track)


class Page_Individus(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.maj_done = False
        
        # Contrôles
        self.listview = OL_personnes_surcharge(self, id=-1,  name="OL_personnes", activeCheckBoxes=True, activeDoubleClic=False, activeMenuContextuel=False, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.listview.SetMinSize((10, 10))
        self.barre_recherche = OL_personnes.CTRL_Outils(self, listview=self.listview, afficherCocher=True)
        self.barre_recherche.SetBackgroundColour((255, 255, 255))

        # Commandes
        self.imgFiltrer = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_ANY))
        self.texteFiltrer = Hyperlink(self, id=100,  label=_(u"Rechercher"), infobulle=_(u"Rechercher"))
        self.imgActualiser = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Actualiser.png"), wx.BITMAP_TYPE_ANY))
        self.texteActualiser = Hyperlink(self, id=200, label=_(u"Afficher tout"), infobulle=_(u"Afficher tout"))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_base.Add(self.listview, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=9, vgap=0, hgap=0)
        grid_sizer_commandes.Add(self.barre_recherche, 0, wx.EXPAND, 0)
        grid_sizer_commandes.Add((10, 5), 0, 0, 0)

        grid_sizer_filtres = wx.FlexGridSizer(rows=1, cols=9, vgap=0, hgap=0)
        grid_sizer_filtres.Add(self.imgFiltrer, 0, wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_filtres.Add(self.texteFiltrer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_filtres.Add((10, 5), 0, 0, 0)
        grid_sizer_filtres.Add(self.imgActualiser, 0, wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_filtres.Add(self.texteActualiser, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_commandes.Add(grid_sizer_filtres, 1, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_commandes.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_commandes, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        self.Layout()

    def MAJ(self):
        if self.maj_done == False :
            self.listview.MAJ()
            self.maj_done = True

    def OnCheck(self, track):
        self.parent.SetInfos("individus", self.GetDonnees())
        
    def Validation(self):
        listeNonValides = []
        for track in self.listview.GetCheckedObjects() :
            if track.email in (None, "") :
                nom = track.nom
                if track.prenom not in (None, "") :
                    nom += u" " + track.prenom
                listeNonValides.append(nom)
        
        if len(listeNonValides) > 0 :
            image = wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Activite.png"), wx.BITMAP_TYPE_ANY)
            texteIntro = _(u"Attention, les %d destinataires sélectionnés suivants n'ont pas d'adresse valide :") % len(listeNonValides)
            texteDetail = "\n".join(listeNonValides)
            dlg = dialogs.MultiMessageDialog(self, texteIntro, caption=_(u"Avertissement"), msg2=texteDetail, style = wx.ICON_EXCLAMATION | wx.OK | wx.CANCEL, icon=None, btnLabels={wx.ID_OK : _(u"Continuer"), wx.ID_CANCEL:_(u"Annuler")})
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
            if reponse == wx.ID_CANCEL :
                return False
            
        return True

    def GetDonnees(self):
        listeID = []
        listeAdresses = []
        for track in self.listview.GetCheckedObjects() :
            if track.email not in (None, "") :
                ID = track.IDpersonne
                listeID.append(ID)
                for email in track.email.split(", "):
                    listeAdresses.append(email)
        listeFiltres = self.listview.listeFiltresColonnes
        dictDonnees = {
            "liste_adresses" : listeAdresses,
            "liste_ID" : listeID,
            "liste_filtres" : listeFiltres,
            }
        return dictDonnees
    
    def SetDonnees(self, dictDonnees={}):
        if self.maj_done == False :
            self.MAJ()
        self.barre_recherche.SetFiltres(dictDonnees["liste_filtres"])
        self.listview.SetIDcoches(dictDonnees["liste_ID"])
        self.OnCheck(None)
    
# ----------------------------------------------------------------------------------------------------------------------------------

def AjouteTexteImage(image=None, texte="", alignement="droite-bas", padding=0, taille_police=9):
    """ Ajoute un texte sur une image bitmap """
    # Création du bitmap
    largeurImage, hauteurImage = image.GetSize()
    if 'phoenix' in wx.PlatformInfo:
        bmp = wx.Bitmap(largeurImage, hauteurImage)
    else:
        bmp = wx.EmptyBitmap(largeurImage, hauteurImage)
    mdc = wx.MemoryDC(bmp)
    dc = wx.GCDC(mdc)
    mdc.SetBackgroundMode(wx.TRANSPARENT)
    mdc.Clear()

    # Paramètres
    dc.SetBrush(wx.Brush(wx.RED))
    dc.SetPen(wx.TRANSPARENT_PEN)
    dc.SetFont(wx.Font(taille_police, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
    dc.SetTextForeground(wx.WHITE)
    
    # Calculs
    largeurTexte, hauteurTexte = dc.GetTextExtent(texte)

    # Image
    mdc.DrawBitmap(image, 0, 0)
    
    # Rond rouge
    hauteurRond = hauteurTexte + padding * 2
    largeurRond = largeurTexte + padding * 2 + hauteurRond/2.0
    if largeurRond < hauteurRond :
        largeurRond = hauteurRond
        
    if "gauche" in alignement : xRond = 1
    if "droite" in alignement : xRond = largeurImage - largeurRond - 1
    if "haut" in alignement : yRond = 1
    if "bas" in alignement : yRond = hauteurImage - hauteurRond - 1

    if 'phoenix' in wx.PlatformInfo:
        dc.DrawRoundedRectangle(wx.Rect(xRond, yRond, largeurRond, hauteurRond), hauteurRond/2.0)
    else:
        dc.DrawRoundedRectangleRect(wx.Rect(xRond, yRond, largeurRond, hauteurRond), hauteurRond/2.0)

    # Texte
    xTexte = xRond + largeurRond / 2.0 - largeurTexte / 2.0
    yTexte = yRond + hauteurRond / 2.0 - hauteurTexte / 2.0 - 1
    dc.DrawText(texte, xTexte, yTexte)

    mdc.SelectObject(wx.NullBitmap)
    return bmp



class CTRL_Pages(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=-1)
        self.parent = parent
        self.donnees = {}
        self.SetPadding((10, 8)) 
        
        self.listePages = [
            {"code" : "individus", "label" : _(u"Individus"), "page" : Page_Individus(self), "image" : wx.Bitmap(Chemins.GetStaticPath(u"Images/32x32/Personnes.png"), wx.BITMAP_TYPE_PNG)},
            {"code" : "saisie_manuelle", "label" : _(u"Saisie manuelle"), "page" : Page_Saisie_manuelle(self), "image" : wx.Bitmap(Chemins.GetStaticPath(u"Images/32x32/Contrat.png"), wx.BITMAP_TYPE_PNG)},
            ]
            
        # Images
        self.imageList = wx.ImageList(32, 32)
        for dictPage in self.listePages :
            self.imageList.Add(dictPage["image"])
        self.AssignImageList(self.imageList)
        
        # Création des pages
        index = 0
        for dictPage in self.listePages :
            self.AddPage(dictPage["page"], dictPage["label"], imageId=index)
            index += 1

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def OnPageChanged(self, event):
        indexPage = event.GetSelection()
        page = self.GetPage(indexPage)
        if page.maj_done == False :
            self.MAJ_page(page)
        event.Skip()

    def MAJ_page(self, page=None):
        dlgAttente = wx.BusyInfo(_(u"Veuillez patienter..."), self.parent)
        page.MAJ()
        del dlgAttente

    def GetIndexPageByCode(self, code=""):
        index = 0
        for dictPage in self.listePages :
            if dictPage["code"] == code :
                return index
            index += 1
        return None
    
    def GetPageByCode(self, code=""):
        for dictPage in self.listePages :
            if dictPage["code"] == code :
                return dictPage["page"]
        return None
    
    def SetImage(self, code="", nbre=0):
        index = self.GetIndexPageByCode(code)
        bmp = self.listePages[index]["image"]
        if nbre > 0 :
            bmp = AjouteTexteImage(bmp, str(nbre))
        self.imageList.Replace(index, bmp)
        self.SetPageImage(index, index)
    
    def SetInfos(self, code="", dictDonnees={}):
        self.donnees[code] = dictDonnees
        # MAJ de l'image de la page
        nbreAdresses = len(dictDonnees["liste_adresses"])
        self.SetImage(code, nbreAdresses)
        # MAJ du label d'intro
        listeAdressesUniques = self.GetListeAdressesUniques()
        if len(listeAdressesUniques) == 0 :
            texte = self.parent.texte_intro
        elif len(listeAdressesUniques) == 1 :
            texte = _(u"Vous avez sélectionné 1 destinataire valide. Cliquez sur OK pour valider la sélection.")
        else :
            texte = _(u"Vous avez sélectionné %d destinataires valides. Cliquez sur OK pour valider la sélection.") % len(listeAdressesUniques)
        self.parent.ctrl_intro.SetLabel(texte)

    def GetListeAdressesUniques(self):
        listeAdressesUniques = []
        for code, dictDonnees in self.donnees.items() :
            for adresse in dictDonnees["liste_adresses"] :
                if adresse not in listeAdressesUniques :
                    listeAdressesUniques.append(adresse)
        return listeAdressesUniques
    
    def Validation(self):
        for dictPage in self.listePages :
            if dictPage["page"].Validation() == False :
                return False
        return True
    
    def GetDonnees(self):
        return self.donnees, self.GetListeAdressesUniques()
    
    def SetDonnees(self, donnees={}):
        for code, dictDonnees in donnees.items() :
            page = self.GetPageByCode(code)
            page.SetDonnees(dictDonnees)
            
        
        
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent   
        
        self.texte_intro = _(u"Sélectionnez des adresses Emails grâce aux contrôles ci-dessous...")
        self.ctrl_intro = wx.StaticText(self, -1, self.texte_intro)
        
        self.ctrl_pages = CTRL_Pages(self)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_detail = wx.Button(self, -1, _(u"Afficher la liste des adresses valides"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDetail, self.bouton_detail)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        # MAJ la première page
        page = self.ctrl_pages.GetPage(0)
        self.ctrl_pages.MAJ_page(page)

    def __set_properties(self):
        self.SetTitle(_(u"Sélection des destinataires"))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_detail.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher la liste des adresses valides")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((700, 550))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_intro, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_pages, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_detail, 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(2)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base
        self.CenterOnScreen() 

    def OnBoutonDetail(self, event):
        """ Affiche la liste détaillée des adresses valides """
        listeAdressesUniques = self.ctrl_pages.GetListeAdressesUniques()
        if len(listeAdressesUniques) == 0 :
            texte = _(u"Aucune adresse valide")
        else :
            texte = "\n".join(listeAdressesUniques)
        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, texte, _(u"Liste des adresses valides"))
        dlg.ShowModal()
        dlg.Destroy()
                    
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("EditeurdEmails")

    def OnBoutonOk(self, event): 
        # Validation des pages
        if self.ctrl_pages.Validation() == False :
            return False
        
        donnees, listeAdressesUniques = self.ctrl_pages.GetDonnees()
        if len(listeAdressesUniques) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune adresse valide.\n\nSouhaitez-vous tout de même valider ?"), _(u"Information"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False
        
        # Ferme la fenêtre
        self.EndModal(wx.ID_OK)

    def GetDonnees(self):
        return self.ctrl_pages.GetDonnees()
    
    def SetDonnees(self, donnees={}):
        self.ctrl_pages.SetDonnees(donnees)
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
