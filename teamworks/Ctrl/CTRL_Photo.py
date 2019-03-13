#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
import six
from PIL import Image
import os
import FonctionsPerso
import GestionDB
from Utils import UTILS_Fichiers
from Utils import UTILS_Adaptations



def GetPhoto(IDindividu=None, nomFichier=None, taillePhoto=(128, 128), qualite=wx.IMAGE_QUALITY_HIGH):
    qualite=wx.IMAGE_QUALITY_HIGH
    """ Retourne la photo d'un individu """
    IDphoto = None
    bmp = None
    
    if IDindividu != None :
        # Recherche d'une image dans la base de données
        db = GestionDB.DB(suffixe="PHOTOS")
        req = "SELECT IDphoto, photo FROM photos WHERE IDindividu=%d;" % IDindividu 
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) > 0 :
            IDphoto, bufferPhoto = listeDonnees[0]
            # Transformation du buffer en wx.bitmap
            io = six.BytesIO(bufferPhoto)
            if 'phoenix' in wx.PlatformInfo:
                img = wx.Image(io, wx.BITMAP_TYPE_JPEG)
            else:
                img = wx.ImageFromStream(io, wx.BITMAP_TYPE_JPEG)
            bmp = img.ConvertToBitmap()
            
            # Récupération du cadre de décoration
            cadrePhoto, textePhoto = GetCadreEtTexte(IDindividu)
            if cadrePhoto != None and cadrePhoto != "" :
                photo = bmp
                # Application du masque
                tailleInitiale = bmp.GetSize()
                # Création du dc temporaire
                if 'phoenix' in wx.PlatformInfo:
                    bmp = wx.Bitmap(tailleInitiale[0], tailleInitiale[1])
                else:
                    bmp = wx.EmptyBitmap(tailleInitiale[0], tailleInitiale[1])
                dc = wx.MemoryDC()
                dc.SelectObject(bmp)

                dc = wx.GraphicsContext.Create(dc)
                dc.PushState() 

                # Dessin de la photo
                l, h = photo.GetSize() 
                dc.DrawBitmap(photo, 0, 0, l, h)
                
                # Dessin du cadre de décoration
                fichierCadre = u"Images/CadresPhotos/%s.png" % cadrePhoto
                if os.path.isfile(fichierCadre):
                    masque = wx.Bitmap(fichierCadre, wx.BITMAP_TYPE_PNG)
                    l, h = masque.GetSize() 
                    dc.DrawBitmap(masque, 0, 0, l, h)
                
                dc.PopState() 
    
    if bmp == None and nomFichier != None :
        # Recherche d'une image sur le disque dur
        if os.path.isfile(nomFichier):
            bmp = wx.Bitmap(nomFichier, wx.BITMAP_TYPE_ANY) # "Images/128x128/Femme.png"        
    
    if bmp != None :
        # Redimensionnement
        img = bmp.ConvertToImage()
        img = img.Rescale(width=taillePhoto[0], height=taillePhoto[1], quality=qualite) 
        bmp = img.ConvertToBitmap()

    return (IDphoto, bmp)
        

def GetCadreEtTexte(IDindividu=None):
    """ Récupère le nom du cadre de déco + le texte de la photo """
    if IDindividu == None :
        return "", ""
    DB = GestionDB.DB()        
    req = "SELECT cadre_photo, texte_photo FROM personnes WHERE IDpersonne=%d;" % IDindividu
    DB.ExecuterReq(req)
    donnees = DB.ResultatReq()
    DB.Close()
    if len(donnees) > 0 :
        cadrePhoto = donnees[0][0]
        textePhoto = donnees[0][1]
    else:
        cadrePhoto = None
        textePhoto = u""
    if textePhoto == None : 
        textePhoto = u""
    return cadrePhoto, textePhoto


class CTRL_Photo(wx.StaticBitmap):
    def __init__(self, parent, IDindividu=None, size=(128, 128), style=0):
        wx.StaticBitmap.__init__(self, parent, id=-1, size=size, style=style)
        self.parent = parent
        self.IDphoto = None
        self.IDindividu = IDindividu
        self.nomFichier = None
        self.taillePhoto = (128, 128)
        
        self.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.SetToolTip(wx.ToolTip(_(u"Cliquez sur le bouton droit de votre souris\npour accéder aux fonctions photo")))
        
        self.Bind(wx.EVT_LEFT_DOWN, self.MenuPhoto)
        self.Bind(wx.EVT_RIGHT_DOWN, self.MenuPhoto)

    
    def SetPhoto(self, IDindividu=None, nomFichier=None, taillePhoto=(128, 128), qualite=wx.IMAGE_QUALITY_HIGH) :
        qualite = wx.IMAGE_QUALITY_HIGH
        self.IDindividu = IDindividu
        self.nomFichier = nomFichier
        self.taillePhoto = taillePhoto
        
        # Récupération de la photo
        IDphoto, bmp = GetPhoto(IDindividu, nomFichier, taillePhoto, qualite)
        if bmp != None :
            self.SetBitmap(bmp)
            self.IDphoto = IDphoto
            
    def GetIDphoto(self):
        return self.IDphoto

    def MenuPhoto(self, event):
        """Ouverture du menu contextuel de la photo """
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Importer une photo"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Importer_photo.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
        
        # Item Capturer à partir d'une caméra
        item = wx.MenuItem(menuPop, 20, _(u"Capturer une photo à partir d'une webcam"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Webcam.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Capturer, id=20)

         # Item Imprimer
        item = wx.MenuItem(menuPop, 40, _(u"Imprimer la photo"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Imprimer, id=40)
        if self.IDphoto == None : item.Enable(False)

        menuPop.AppendSeparator() 
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)
        if self.IDphoto == None : item.Enable(False)
        
        menuPop.AppendSeparator()
        
        # Choix d'un cadre de décoration
        nomCadrePersonne, textePhoto = GetCadreEtTexte(self.IDindividu)
        sousmenu1 = UTILS_Adaptations.Menu()
        indexID = 500
        for nomCadre in FonctionsPerso.GetListeCadresPhotos() :
            if six.PY2:
                nomCadre = nomCadre.decode("iso-8859-15")
            sousmenu1.Append(indexID, nomCadre, _(u"Choisir le cadre de décoration '") + nomCadre + _(u"' pour cette personne"), wx.ITEM_RADIO)
            if nomCadre == nomCadrePersonne :
                sousmenu1.Check(indexID, True)
            self.Bind(wx.EVT_MENU, self.Menu_ChoixCadre, id=indexID)
            indexID += 1
        menuPop.AppendMenu(50, _(u"Choisir un cadre de décoration"), sousmenu1)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
            
    def Menu_Ajouter(self, event):
        self.Ajoute_image()

    def Ajoute_image(self):
        """ Permet la sélection et le retouchage d'une photo pour la personne """
        # Sélection d'une image
        self.repCourant = os.getcwd()

        wildcard = "Toutes les images (*.bmp; *.gif; *.jpg; *.png)|*.bmp; *.gif; *.jpg; *.png|Image JPEG (*.jpg)|*.jpg|Image PNG (*.png)|*.png|Image GIF (*.gif)|*.gif|Tous les fichiers (*.*)|*.*"
                
        # Récupération du chemin des documents
        sp = wx.StandardPaths.Get()
        cheminDefaut = sp.GetDocumentsDir()
        # Ouverture dela fenêtre de dialogue
        dlg = wx.FileDialog(
            self, message=_(u"Choisissez une photo"),
            defaultDir=cheminDefaut, 
            defaultFile="", 
            wildcard=wildcard,
            style=wx.FD_OPEN,
            )
        if dlg.ShowModal() == wx.ID_OK:
            nomFichierCourt = dlg.GetFilename()
            nomFichierLong = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        self.ChargeEditeurPhoto(nomFichierLong)
    
    def ChargeEditeurPhoto(self, nomFichierLong=""):
        """ Editeur de photo """
        # Récupératon du cadre et du texte
        cadrePhoto, textePhoto = GetCadreEtTexte(self.IDindividu)
        
        # Recadre la photo
        from Dlg import DLG_Editeur_photo
        dlg = DLG_Editeur_photo.Dialog(None, image=nomFichierLong)#, tailleCadre=(128, 128))
        dlg.SetCadreDecoration(cadrePhoto)
        dlg.SetTexte(textePhoto)
        if dlg.ShowModal() == wx.ID_OK:
            buffer = dlg.GetBuffer()
            bmp = buffer.read()
            tailleBmp = len(buffer.getvalue())
            cadrePhoto = dlg.GetCadre()
            textePhoto = dlg.GetTexte() 
            dlg.Destroy()
            # Recherche si une photo existe déjà pour cet individu
            DB = GestionDB.DB(suffixe="PHOTOS")
            req = "SELECT IDphoto, photo FROM photos WHERE IDindividu=%d;" % self.IDindividu 
            DB.ExecuterReq(req)
            listePhotos = DB.ResultatReq()
            if len(listePhotos) == 0 :
                IDphoto = DB.InsertPhoto(IDindividu=self.IDindividu, blobPhoto=bmp)
            else:
                IDphoto = DB.MAJPhoto(IDphoto=listePhotos[0][0], IDindividu=self.IDindividu, blobPhoto=bmp)
            DB.Close()
            # Applique la photo
            self.SetPhoto(self.IDindividu)
            # Sauvegarde du cadre de décoration et du texte personnalisé
            DB = GestionDB.DB()
            listeDonnees = [("cadre_photo", cadrePhoto), ("texte_photo", textePhoto)]
            DB.ReqMAJ("personnes", listeDonnees, "IDpersonne", self.IDindividu)
            DB.Close()
        else:
            dlg.Destroy()
            return

    def Menu_Capturer(self, event):
        self.Capture_image()

    def Capture_image(self):
        """ Capture la photo à partir d'une caméra """
        from Dlg import DLG_Capture_video
        dlg = DLG_Capture_video.Dialog(self)
        resultat = dlg.ShowModal() 
        dlg.Destroy()
        if resultat == wx.ID_OK:
            self.ChargeEditeurPhoto(UTILS_Fichiers.GetRepTemp("capture_video.jpg"))

    def Menu_Supprimer(self, event):
        """ Suppression de la photo """
        txtMessage = _(u"Souhaitez-vous vraiment supprimer cette photo ?")
        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        reponse = dlgConfirm.ShowModal()
        dlgConfirm.Destroy()
        if reponse == wx.ID_NO:
            return
        # Suppression de la photo 
        DB = GestionDB.DB(suffixe="PHOTOS")
        DB.ReqDEL("photos", "IDindividu", self.IDindividu)
        DB.Close()
        # Recherche la civilité de l'individu
        DB = GestionDB.DB()
        req = "SELECT civilite FROM personnes WHERE IDpersonne=%d;" % self.IDindividu 
        DB.ExecuterReq(req)
        civilite = DB.ResultatReq()[0][0]
        if civilite == None : return
        DB.Close()
        if civilite == "Mr" :
            img = "Homme.png"
        elif civilite == "Mme" or civilite == "Melle":
            img = "Femme.png"
        else :
            img = "Personne.png"
        nomFichier=u"Images/128x128/%s" % img
        # Applique l'image par défaut
        self.SetPhoto(self.IDindividu, nomFichier)
        
    def Menu_Imprimer(self, event):
        """ Impression de la photo de la personne """
        # Récupération de la liste des personnes
        DB = GestionDB.DB()        
        req = """SELECT IDpersonne, nom, prenom FROM personnes WHERE IDpersonne=%d; """ % self.IDindividu
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()[0]
        DB.Close()
        # Ouverture de la frame d'impression des photos  
        from Dlg import DLG_Impression_photo
        dlg = DLG_Impression_photo.Dialog(None, listePersonnes=[[self.IDindividu, donnees[1], donnees[2], None],])
        dlg.ShowModal()
        dlg.Destroy()

    def Menu_ChoixCadre(self, event):
        index = event.GetId() - 500
        if index == 0 : 
            nomCadre = ""
        else :
            nomCadre = FonctionsPerso.GetListeCadresPhotos()[index]
            if six.PY2:
                nomCadre = nomCadre.decode("iso-8859-15")
        # Sauvegarde le choix du cadre
        DB = GestionDB.DB()
        DB.ReqMAJ("personnes", [("cadre_photo", nomCadre),], "IDpersonne", self.IDindividu)
        DB.Close()
        # MAJ de la photo affichée
        self.SetPhoto(IDindividu=self.IDindividu, nomFichier=self.nomFichier, taillePhoto=self.taillePhoto)

    def wxtopil(self, image):
        """Convert wx.Image to PIL Image."""
        pil = Image.new('RGB', (image.GetWidth(), image.GetHeight()))
        pil.frombytes(image.GetData())
        return pil




class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL_Photo(panel, style=wx.SUNKEN_BORDER)
        
        IDpersonne = 13
        nomFichier = "Images/128x128/Personne.png"
        self.ctrl.SetPhoto(IDpersonne, nomFichier, taillePhoto=(128, 128))

        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 0, wx.ALL, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(400, 200))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()