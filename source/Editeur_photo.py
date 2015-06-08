#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

import wx
import Image
import cStringIO
import GestionDB
import FonctionsPerso
import GestionDB



def pil2wx(image):
    """Convert a PIL image to wx image format"""
    imagewx=wx.EmptyImage(image.size[0], image.size[1])
    imagewx.SetData(image.tostring('raw', 'RGB'))
    return imagewx

def load_image(fn):
    """Read a file into PIL Image object. Return the image and file size"""
    buf=cStringIO.StringIO()
    f=open(fn,"rb")
    while 1:
        rdbuf=f.read(8192)
        if not rdbuf: break
        buf.write(rdbuf)
    f.close()
    buf.seek(0)
    image=Image.open(buf).convert("RGB")
    return image,len(buf.getvalue())

def save_image_buf(image,q=90):
    """Save a PIL Image into a byte buffer as a JPEG with the given quality.
    Return the buffer and file size.
    """
    buf=cStringIO.StringIO()
    image.save(buf,format='JPEG',quality=q)
    buf.seek(0)
    return buf,len(buf.getvalue())

def save_image_file(fn,buf):
    """Save a byte buffer to a file"""
    f=open(fn,"wb")
    while 1:
        rdbuf=buf.read(8192)
        if not rdbuf: break
        f.write(rdbuf)
    f.close()

def wxtopil(image):
    """Convert wx.Image to PIL Image."""
    pil = Image.new('RGB', (image.GetWidth(), image.GetHeight()))
    pil.fromstring(image.GetData())
    return pil



class ImgBox(wx.Window):
    def __init__(self, parent, id=-1, image=None):
        wx.Window.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, wx.NO_FULL_REPAINT_ON_RESIZE |wx.SUNKEN_BORDER)
        
        self.fichierImageSource = image
        self.InitImage()

        # Binds
        wx.EVT_PAINT(self, self.evt_paint)
        wx.EVT_SIZE(self, self.evt_size)
        wx.EVT_KEY_DOWN(self, self.evt_key)
        wx.EVT_LEFT_DOWN(self, self.evt_mouse)
        wx.EVT_LEFT_UP(self, self.evt_mouse)
        wx.EVT_MOTION(self, self.evt_mouse)
        wx.EVT_LEAVE_WINDOW(self, self.OnLeaveWindow)
        
    def InitImage(self):
        # Chargement de l'image source
        self.sourcePIL, self.origsize = load_image(self.fichierImageSource)
        # Transforme l'image PIL en wx.Image
        self.source = pil2wx(self.sourcePIL)
        # Initialise les valeurs
        self.posxPhoto = None
        self.posyPhoto = None
        self.zoom = None
        self.dragging = False
        self.largeurDC = None
        self.hauteurDC = None
        
        self.tailleCadre = 384
        
        
    def ReinitImage(self):
        self.InitImage()
        self.evt_size(None)
        
    def InitValeursPhoto(self):
        """ Calcule la position et la taille initiale de la photo (au milieu) """
        largeurDC, hauteurDC = self.GetClientSizeTuple()
        largeurImg, hauteurImg = self.source.GetSize()
        # Calcule le zoom en fonction de la taille de la photo
        largeurMax = self.tailleCadre * 1.0 #min(largeurDC, hauteurDC) / 2.0
        margeSupp = 0
        zoomTmp = (largeurMax+margeSupp) / min(largeurImg, hauteurImg)
        # Transmet la valeur du zoom au slider
        valeurSliderZoom = round(zoomTmp*1000)
        self.GetGrandParent().slider_zoom.SetValue(int(valeurSliderZoom))
        self.zoom = valeurSliderZoom / 1000.0
        # Calcule la position de la photo au centre du dc
        self.ResizePhoto()
        self.posxPhoto = (largeurDC / 2.0) 
        self.posyPhoto = (hauteurDC / 2.0)



    def Draw(self,dc):
        """Draw the image bitmap and decoration on the buffered DC"""
        dc.SetBackground(wx.BLACK_BRUSH)
        dc.Clear()
        dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
        
        # Dessin de la photo
        largeurImg, hauteurImg = self.bmp.GetSize()
        dc.DrawBitmap(self.bmp, self.posxPhoto - (largeurImg / 2.0), self.posyPhoto - (hauteurImg / 2.0), 0)
        
        # D�finit la position et la taille du cadre de s�lection
        coeffReduction = 2.0
        largeurDC, hauteurDC = self.GetClientSizeTuple()
        self.posxCadre = (largeurDC / 2.0) - (self.tailleCadre / 2.0)
        self.posyCadre = (hauteurDC / 2.0) - (self.tailleCadre / 2.0)
        
        # M�morise la s�lection de la photo avant de dessiner le cadre
        self.selection = dc.GetAsBitmap((self.posxCadre, self.posyCadre, self.tailleCadre, self.tailleCadre))
        
        # Dessin du masque de d�coration
        nomCadre = self.GetGrandParent().GetCadreDecoration()
        if nomCadre != None :
            self.bmpMasque = wx.Bitmap("Images/CadresPhotos/" + nomCadre + ".png", wx.BITMAP_TYPE_PNG)
            dc.DrawBitmap(self.bmpMasque, self.posxCadre, self.posyCadre)
        
        # Dessine le cadre de s�lection
        dc.SetPen(wx.CYAN_PEN)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(self.posxCadre, self.posyCadre, self.tailleCadre, self.tailleCadre)
        dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
        dc.SetTextForeground("CYAN")
        dc.DrawText(u"Cadre de s�lection", self.posxCadre+3, self.posyCadre+1) 
        
        # Dessine l'aper�u
        posxApercu, posyApercu, tailleApercu = (10, 10, 100)
        self.apercu = self.selection.ConvertToImage()
        self.apercu = self.apercu.Rescale(width=tailleApercu, height=tailleApercu, quality=50) 
        self.apercu = self.apercu.ConvertToBitmap()
        dc.DrawBitmap(self.apercu, posxApercu, posyApercu, 0)
        dc.SetTextForeground("RED")
        if nomCadre == None :
            texteApercu = u"Aper�u"
        else:
            texteApercu = u"Aper�u sans d�co."
        dc.DrawText(texteApercu, posxApercu+3, posyApercu+1) 
        
        # Dessine le cadre de l'aper�u
        dc.SetPen(wx.RED_PEN)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(posxApercu, posyApercu, tailleApercu, tailleApercu)

    def evt_paint(self, event):
        """Paint event handler with double buffering"""
        dc = wx.BufferedPaintDC(self, self._Buffer)

    def evt_size(self,event):
        """ OnSize """
        ancLargeurDC, ancHauteurDC = self.largeurDC, self.hauteurDC
        self.largeurDC, self.hauteurDC = self.GetClientSizeTuple()
        # Initialise la taille et la position initiale de la photo
        if self.posxPhoto == None : 
            self.InitValeursPhoto()
        else :
        # Redimensionne la photo 
            self.ResizePhoto()
            # D�termine le nouveau point central de la photo
            self.posxPhoto = self.posxPhoto + (self.largeurDC-ancLargeurDC)/2
            self.posyPhoto = self.posyPhoto + (self.hauteurDC-ancHauteurDC)/2
        # Redessine toute l'image
        self._Buffer = wx.EmptyBitmap(self.largeurDC, self.hauteurDC)
        self.UpdateDrawing()


    def ResizePhoto(self):
        """ Redimensionne la photo"""
        largeurImg, hauteurImg = self.source.GetSize()
        # R�duction de l'image
        newLargeur = largeurImg * self.zoom
        newHauteur = hauteurImg * self.zoom
        # Redimensionne l'image
        source = self.source.Scale(newLargeur, newHauteur)
        self.bmp=wx.BitmapFromImage(source)
    
    def UpdateDrawing(self):
        """Create the device context and draw the window contents"""
        dc = wx.BufferedDC(wx.ClientDC(self), self._Buffer)
        dc.BeginDrawing()
        self.Draw(dc)
        dc.EndDrawing()

    def Zoom(self, valeurZoom):
        """ Zoom """
        self.zoom = valeurZoom
        self.ResizePhoto()
        self.UpdateDrawing()
        
    def Rotation(self, VersDroite=True):
        """ Rotation de la photo """
        # Rotation
        self.source = self.source.Rotate90(VersDroite)
        # R�duction de l'image
        largeurImg, hauteurImg = self.source.GetSize()
        newLargeur = largeurImg * self.zoom
        newHauteur = hauteurImg * self.zoom
        source = self.source.Scale(newLargeur, newHauteur)
        self.bmp=wx.BitmapFromImage(source)
        # MAJ de l'affichage de la photo
        self.UpdateDrawing()

    def evt_mouse(self,event):
        """ Gestion du d�placement de la photo """
        eventType=event.GetEventType()
        posx, posy = event.GetPosition()
        # Left Down
        if eventType == wx.wxEVT_LEFT_DOWN:
            self.dragging = True
            self.posxDrag, self.posyDrag = self.posxPhoto - posx, self.posyPhoto - posy
            self.SetCursor(wx.StockCursor(wx.CURSOR_SIZING))
        # Left Up
        elif eventType == wx.wxEVT_LEFT_UP:
            self.dragging = False
            self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        # Motion
        elif eventType == wx.wxEVT_MOTION:
            if self.dragging == True :
                self.posxPhoto = posx + self.posxDrag
                self.posyPhoto = posy + self.posyDrag
                self.UpdateDrawing()

    def OnLeaveWindow(self, event):
        pass #self.dragging = False

    def evt_key(self, event):
        """ Touches clavier """
        keyCode = event.GetKeyCode()
        print keyCode

    def SaveImage(self):
        # Param�tres de sauvegarde
        jpeg_quality = 90
        
        # Cr�ation du nom de fichier
        nomFichier = "Photos/"
        codeIDfichier = self.RecupIDfichier()
        IDpersonne = self.GetGrandParent().IDpersonne
        nomFichier += codeIDfichier + str(IDpersonne) + ".jpg"
        
        # R�cup�ration de l'image dans le cadre de s�lection
        tailleImg = self.selection.GetSize()
        imgTemp = self.selection.GetSubBitmap( (0, 0, tailleImg[0], tailleImg[1]) ) 
        imgFinale = wxtopil(imgTemp.ConvertToImage())
        
        # Sauvegarde
        try:
            buf, bytes=save_image_buf(imgFinale, jpeg_quality)
            ok=1
            if ok:
                save_image_file(nomFichier,buf)
                print "Saved image to %s (%.f kB)" % (nomFichier, bytes/1024)
        except:
                print "Failed to save image!"
                return None
        return nomFichier
        
    def RecupIDfichier(self):
        """ R�cup�re le code identifiant unique du fichier """
        DB = GestionDB.DB()        
        req = "SELECT codeIDfichier FROM divers WHERE IDdivers=1;"
        DB.ExecuterReq(req)
        donnees = DB.ResultatReq()
        DB.Close()
        codeIDfichier = donnees[0][0]
        return codeIDfichier


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------



class MyFrame(wx.Frame):
    def __init__(self, parent, IDpersonne=0, image=None):
        wx.Frame.__init__(self, parent, -1, name="frm_photo", style=wx.DEFAULT_FRAME_STYLE)
        self.panel = wx.Panel(self, -1)
        self.IDpersonne = IDpersonne
        
        # Widgets
        self.imgbox = ImgBox(self.panel,-1, image=image)
        
        self.staticBox_rotation = wx.StaticBox(self.panel, -1, u"Rotation")
        self.bouton_rotation_gauche = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/22x22/RotationGauche.png", wx.BITMAP_TYPE_PNG))
        self.bouton_rotation_droite = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/22x22/RotationDroite.png", wx.BITMAP_TYPE_PNG))
        
        self.staticBox_zoom = wx.StaticBox(self.panel, -1, u"Zoom")
        self.slider_zoom = wx.Slider(self.panel, -1,  500, 1, 1000, size=(-1, -1), style=wx.SL_HORIZONTAL)
        self.img_loupe_plus = wx.StaticBitmap(self.panel, -1, wx.Bitmap("Images/22x22/ZoomPlus.png", wx.BITMAP_TYPE_ANY))
        self.img_loupe_moins = wx.StaticBitmap(self.panel, -1, wx.Bitmap("Images/22x22/ZoomMoins.png", wx.BITMAP_TYPE_ANY))
        
        self.staticBox_decoration = wx.StaticBox(self.panel, -1, u"Cadre de d�coration")
        listeCadres = FonctionsPerso.GetListeCadresPhotos()
        self.combobox_decoration = wx.Choice(self.panel, -1, choices=listeCadres)
        
        nom_cadre_perso = FonctionsPerso.RecupNomCadrePersonne(self.IDpersonne)
        if nom_cadre_perso != None and nom_cadre_perso != "" :
            self.combobox_decoration.SetStringSelection(nom_cadre_perso)
        else:
            self.combobox_decoration.SetSelection(0)
        
        self.staticBox_texte_photo = wx.StaticBox(self.panel, -1, u"Texte personnalis�")
        textePhoto = FonctionsPerso.RecupTextePhotoPersonne(self.IDpersonne)
        self.texte_photo = wx.TextCtrl(self.panel, -1, textePhoto)
        
        self.staticBox_reinit = wx.StaticBox(self.panel, -1, u"R�initialisation")
        self.bouton_reinit = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/22x22/Photo.png", wx.BITMAP_TYPE_ANY), size=(70, -1))
        
        # Boutons
        self.bouton_aide = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self.panel, -1, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRotationGauche, self.bouton_rotation_gauche)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRotationDroite, self.bouton_rotation_droite)
        self.Bind(wx.EVT_SCROLL, self.OnScrollSlider, self.slider_zoom)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonReinit, self.bouton_reinit)
        self.Bind(wx.EVT_CHOICE, self.OnChoixDecoration, self.combobox_decoration)
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        
    def __set_properties(self):
        self.SetTitle(u"Editeur de photo")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider l'image")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        
        self.bouton_rotation_gauche.SetToolTipString(u"Cliquez ici pour effectuer une rotation de 90�\n dans le sens inverse des aiguilles d'une montre")
        self.bouton_rotation_droite.SetToolTipString(u"Cliquez ici pour effectuer une rotation de 90�\n dans le sens des aiguilles d'une montre")
        self.slider_zoom.SetToolTipString(u"Ajustez avec cette fonction zoom\nla taille de la photo")
        self.bouton_reinit.SetToolTipString(u"Cliquez ici pour r�initialiser la position\net la taille de la photo initiale")
        
        self.SetMinSize((700, 600))

    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        
        # DC
        grid_sizer_base.Add(self.imgbox, 1, wx.LEFT|wx.TOP|wx.RIGHT|wx.EXPAND, 10)
        
        # Panneau de contr�le
        sizer_commandes = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        
        # Rotation
        staticBox_rotation = wx.StaticBoxSizer(self.staticBox_rotation, wx.HORIZONTAL)
        staticBox_rotation.Add(self.bouton_rotation_gauche, 0, wx.ALL, 2)
        staticBox_rotation.Add(self.bouton_rotation_droite, 0, wx.ALL, 2)
        sizer_commandes.Add(staticBox_rotation, 1, wx.EXPAND, 0)
        
        # Zoom
        staticBox_zoom = wx.StaticBoxSizer(self.staticBox_zoom, wx.HORIZONTAL)
        staticBox_zoom.Add(self.img_loupe_moins, 0, wx.ALL, 2)
        staticBox_zoom.Add(self.slider_zoom, 1, wx.EXPAND | wx.ALL, 2)
        staticBox_zoom.Add(self.img_loupe_plus, 0, wx.ALL, 2)
        sizer_commandes.Add(staticBox_zoom, 1, wx.EXPAND, 0)
        
        # Cadre de d�coration
        staticBox_decoration = wx.StaticBoxSizer(self.staticBox_decoration, wx.HORIZONTAL)
        staticBox_decoration.Add(self.combobox_decoration, 0, wx.ALL, 2)
        sizer_commandes.Add(staticBox_decoration, 1, wx.EXPAND, 0)
        
        # Texte personnalis�
        staticBox_texte_photo = wx.StaticBoxSizer(self.staticBox_texte_photo, wx.HORIZONTAL)
        staticBox_texte_photo.Add(self.texte_photo, 0, wx.ALL, 2)
        sizer_commandes.Add(staticBox_texte_photo, 1, wx.EXPAND, 0)
        
        # Reinit
        staticBox_reinit = wx.StaticBoxSizer(self.staticBox_reinit, wx.HORIZONTAL)
        staticBox_reinit.Add(self.bouton_reinit, 0, wx.ALL, 2)
        sizer_commandes.Add(staticBox_reinit, 1, wx.EXPAND, 0)
        
        grid_sizer_base.Add(sizer_commandes, 1, wx.EXPAND | wx.ALL, 10)
        
        sizer_commandes.AddGrowableRow(0)
        sizer_commandes.AddGrowableCol(1)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.panel.SetSizer(grid_sizer_base)
        sizer_base.Add(self.panel, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        self.Centre()
        
    def Fermer(self):
        self.MakeModal(False)
        self.Destroy()
        
    def OnClose(self, event):
        self.MakeModal(False)
        event.Skip()
        
    def OnBoutonAnnuler(self, event):
        # Fermeture
        self.Fermer()
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(42)

    def OnBoutonOk(self, event):        
        # Sauvegarde de l'image
        nomImage = self.imgbox.SaveImage()
        # Sauvegarde du cadre de d�coration
        cadrePhoto = self.combobox_decoration.GetStringSelection()
        if cadrePhoto == u"Aucun" : cadrePhoto = ""
        listeDonnees = [("cadre_photo", cadrePhoto),]
        DB = GestionDB.DB()
        DB.ReqMAJ("personnes", listeDonnees, "IDpersonne", self.IDpersonne)
        DB.Close()
        # Sauvegarde du texte personnalis�
        textePhoto = self.texte_photo.GetValue()
        listeDonnees = [("texte_photo", textePhoto),]
        DB = GestionDB.DB()
        DB.ReqMAJ("personnes", listeDonnees, "IDpersonne", self.IDpersonne)
        DB.Close()
        # MAJ de la fiche individuelle
        try :
            if self.GetParent().GetName() == "FicheIndividuelle" :
                self.GetParent().Charge_photo()
        except : 
            pass
        # Fermeture
        self.Fermer()
        
    def OnBoutonRotationGauche(self, event):
        self.imgbox.Rotation(False)

    def OnBoutonRotationDroite(self, event):
        self.imgbox.Rotation(True)

    def OnScrollSlider(self, event):
        """ On Slider """
        valeurZoom = self.slider_zoom.GetValue()/1000.0
        self.imgbox.Zoom(valeurZoom)
    
    def OnBoutonReinit(self, event):
        self.combobox_decoration.SetSelection(0)
        self.imgbox.ReinitImage()        
        
    def GetCadreDecoration(self):
        if self.combobox_decoration.GetSelection() == 0 : return None
        selection = self.combobox_decoration.GetStringSelection()
        return selection
    
    def OnChoixDecoration(self, event):
        self.imgbox.UpdateDrawing()




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame = MyFrame(None, IDpersonne=1, image="Photos/20090529142759BMW1.jpg")
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
