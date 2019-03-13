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
import six
from Ctrl import CTRL_Bouton_image
from PIL import Image
import FonctionsPerso



def pil2wx(image):
    """Convert a PIL image to wx image format"""
    imagewx=wx.EmptyImage(image.size[0], image.size[1])
    imagewx.SetData(image.tobytes('raw', 'RGB'))
    return imagewx

def load_image(fn):
    """Read a file into PIL Image object. Return the image and file size"""
    buf = six.BytesIO()
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
    buf = six.BytesIO()
    image.save(buf,format='JPEG',quality=q)
    buf.seek(0)
    return buf,len(buf.getvalue())

def wxtopil(image):
    """Convert wx.Image to PIL Image."""
    pil = Image.new('RGB', (image.GetWidth(), image.GetHeight()))
    pil.frombytes(image.GetData())
    return pil



class ImgBox(wx.Window):
    def __init__(self, parent, id=-1, image=None):
        wx.Window.__init__(self, parent, -1, wx.DefaultPosition, wx.DefaultSize, wx.NO_FULL_REPAINT_ON_RESIZE |wx.SUNKEN_BORDER)
        
        self.fichierImageSource = image
        self.InitImage()

        # Binds
        wx.EVT_PAINT(self, self.evt_paint)
        wx.EVT_SIZE(self, self.evt_size)
        
    def InitImage(self):
        # Chargement de l'image source
        self.sourcePIL, self.origsize = load_image(self.fichierImageSource)
        # Transforme l'image PIL en wx.Image
        self.source = pil2wx(self.sourcePIL)
        # Initialise les valeurs
        self.posxPhoto = None
        self.posyPhoto = None
        
        self.largeurDC = None
        self.hauteurDC = None
        
        self.tailleCadre = 384
        
    def ReinitImage(self):
        self.InitImage()
        self.evt_size(None)

    def Draw(self,dc):
        """Draw the image bitmap and decoration on the buffered DC"""
        dc.SetBackground(wx.BLACK_BRUSH)
        dc.Clear()
        dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Arial'))
        
        # Dessin de la photo
        largeurImg, hauteurImg = self.bmp.GetSize()
        largeurDC, hauteurDC = self.GetClientSizeTuple()
        dc.DrawBitmap(self.bmp, (largeurDC / 2.0)  - (largeurImg / 2.0), (hauteurDC / 2.0) - (hauteurImg / 2.0), 0)
        
    def evt_paint(self, event):
        """Paint event handler with double buffering"""
        dc = wx.BufferedPaintDC(self, self._Buffer)

    def evt_size(self,event):
        """ OnSize """
        self.ResizePhoto()
        largeurDC, hauteurDC = self.GetClientSizeTuple()
        # Redessine toute l'image
        self._Buffer = wx.EmptyBitmap(largeurDC, hauteurDC)
        self.UpdateDrawing()

    def ResizePhoto(self):
        """ Redimensionne la photo"""
        largeurImg, hauteurImg = self.source.GetSize()
        self.ratio = self.GetParent().slider_ratio.GetValue() / 100.0
        source = self.source.Scale(largeurImg * self.ratio, hauteurImg * self.ratio)
        self.bmp=wx.BitmapFromImage(source)
    
    def UpdateDrawing(self):
        """Create the device context and draw the window contents"""
        dc = wx.BufferedDC(wx.ClientDC(self), self._Buffer)
        dc.BeginDrawing()
        self.Draw(dc)
        dc.EndDrawing()

    def SetRatio(self):
        """ ratio """
        self.ResizePhoto()
        self.UpdateDrawing()
        
    def Rotation(self, VersDroite=True):
        """ Rotation de la photo """
        # Rotation
        self.source = self.source.Rotate90(VersDroite)
        # Réduction de l'image
        largeurImg, hauteurImg = self.source.GetSize()
        source = self.source.Scale(largeurImg * self.ratio, hauteurImg * self.ratio)
        self.bmp=wx.BitmapFromImage(source)
        # MAJ de l'affichage de la photo
        self.UpdateDrawing()

    def SaveImage(self):
        # Paramètres de sauvegarde
        jpeg_quality = 90
        
        # Création du nom de fichier
        nomFichier = "Photos/"
        codeIDfichier = self.RecupIDfichier()
        IDpersonne = self.GetGrandParent().IDpersonne
        nomFichier += codeIDfichier + str(IDpersonne) + ".jpg"
        
        # Récupération de l'image dans le cadre de sélection
        tailleImg = self.selection.GetSize()
        imgTemp = self.selection.GetSubBitmap( (0, 0, tailleImg[0], tailleImg[1]) ) 
        imgFinale = wxtopil(imgTemp.ConvertToImage())
        
        # Sauvegarde
        try:
            buf, bytes=save_image_buf(imgFinale, jpeg_quality)
            ok=1
            if ok:
                save_image_file(nomFichier,buf)
                print("Saved image to %s (%.f kB)" % (nomFichier, bytes/1024))
        except:
                print("Failed to save image!")
                return None
        return nomFichier
        


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------



class MyDialog(wx.Dialog):
    def __init__(self, parent, image=None, titre=_(u"Editeur photo")):
        wx.Dialog.__init__(self, parent, -1, title=titre, name="frm_photo", size=(700, 600))
        
        # Widgets
        self.imgbox = ImgBox(self,-1, image=image)
        
        self.staticBox_rotation = wx.StaticBox(self, -1, _(u"Rotation"))
        self.bouton_rotation_gauche = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/22x22/RotationGauche.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_rotation_droite = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/22x22/RotationDroite.png"), wx.BITMAP_TYPE_PNG))
        
        self.staticBox_ratio = wx.StaticBox(self, -1, _(u"Taille de l'image"))
        self.slider_ratio = wx.Slider(self, -1,  100, 1, 200, size=(-1, -1), style=wx.SL_HORIZONTAL)
        self.img_loupe_plus = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/22x22/zoomPlus.png"), wx.BITMAP_TYPE_ANY))
        self.img_loupe_moins = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/22x22/zoomMoins.png"), wx.BITMAP_TYPE_ANY))
                
        self.staticBox_reinit = wx.StaticBox(self, -1, _(u"Réinitialisation"))
        self.bouton_reinit = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/22x22/Photo.png"), wx.BITMAP_TYPE_ANY), size=(70, -1))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRotationGauche, self.bouton_rotation_gauche)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonRotationDroite, self.bouton_rotation_droite)
        self.Bind(wx.EVT_SCROLL, self.OnScrollSlider, self.slider_ratio)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonReinit, self.bouton_reinit)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.SetTitle(_(u"Editeur de photo"))
        if 'phoenix' in wx.PlatformInfo:
            _icon = wx.Icon()
        else :
            _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider l'image")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        
        self.bouton_rotation_gauche.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour effectuer une rotation de 90°\n dans le sens inverse des aiguilles d'une montre")))
        self.bouton_rotation_droite.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour effectuer une rotation de 90°\n dans le sens des aiguilles d'une montre")))
        self.slider_ratio.SetToolTip(wx.ToolTip(_(u"Ajustez avec cette fonction ratio\nla taille de la photo")))
        self.bouton_reinit.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour réinitialiser la position\net la taille de la photo initiale")))
        
    def __do_layout(self):
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        
        # DC
        grid_sizer_base.Add(self.imgbox, 1, wx.LEFT|wx.TOP|wx.RIGHT|wx.EXPAND, 10)
        
        # Panneau de contrôle
        sizer_commandes = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        
        # Rotation
        staticBox_rotation = wx.StaticBoxSizer(self.staticBox_rotation, wx.HORIZONTAL)
        staticBox_rotation.Add(self.bouton_rotation_gauche, 0, wx.ALL, 2)
        staticBox_rotation.Add(self.bouton_rotation_droite, 0, wx.ALL, 2)
        sizer_commandes.Add(staticBox_rotation, 1, wx.EXPAND, 0)
        
        # ratio
        staticBox_ratio = wx.StaticBoxSizer(self.staticBox_ratio, wx.HORIZONTAL)
        staticBox_ratio.Add(self.img_loupe_moins, 0, wx.ALL, 2)
        staticBox_ratio.Add(self.slider_ratio, 1, wx.EXPAND | wx.ALL, 2)
        staticBox_ratio.Add(self.img_loupe_plus, 0, wx.ALL, 2)
        sizer_commandes.Add(staticBox_ratio, 1, wx.EXPAND, 0)
        
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
        self.SetSizer(grid_sizer_base)
        sizer_base.Add(self, 1, wx.EXPAND, 0)
        self.Layout()
        self.CentreOnScreen()
        
    def Fermer(self):
        self.EndModal(wx.ID_CANCEL)

    def GetBmp(self):
        return self.imgbox.bmp
                
    def OnBoutonAide(self, event):
        dlg = wx.MessageDialog(self, _(u"L'aide pour ce nouveau module est en cours de rédaction."), _(u"Aide indisponible"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return

    def OnBoutonOk(self, event): 
        # Ferme la boîte de dialogue
        self.EndModal(wx.ID_OK)        
        
    def OnBoutonRotationGauche(self, event):
        self.imgbox.Rotation(False)

    def OnBoutonRotationDroite(self, event):
        self.imgbox.Rotation(True)

    def OnScrollSlider(self, event):
        """ On Slider """
        self.imgbox.SetRatio()
    
    def OnBoutonReinit(self, event):
        self.slider_ratio.SetValue(100)
        self.imgbox.ReinitImage()        



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frm = MyDialog(None, image="img.jpg")
    frm.ShowModal()
    app.MainLoop()
