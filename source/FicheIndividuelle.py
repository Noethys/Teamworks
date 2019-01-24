#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import PageGeneralites
import PageQuestionnaire
import PageQualifications
import PageContrats
import PagePresences
import PageFrais
import PageScenarios
import PageCandidatures
import FonctionsPerso
import datetime
import GestionDB
from wx.lib.ticker import Ticker
import Editeur_photo
import os
import CTRL_Photo

from PIL import Image

try: import psyco; psyco.full()
except: pass



##import wx.lib.agw.flatnotebook as fnb
##
##class Notebook(fnb.FlatNotebook):
##    def __init__(self, parent, id=-1, IDpersonne = 0):
##        fnb.FlatNotebook.__init__(self, parent, id)#, agwStyle=bookStyle)
##        self.SetAGWWindowStyleFlag(fnb.FNB_RIBBON_TABS)
##        self.IDpersonne = IDpersonne
##
##        # ImageList pour le NoteBook
##        il = wx.ImageList(16, 16)
##        self.img1 = il.Add(wx.Bitmap("Images/16x16/Identite.png", wx.BITMAP_TYPE_PNG))
##        self.img2 = il.Add(wx.Bitmap("Images/16x16/BlocNotes.png", wx.BITMAP_TYPE_PNG))
##        self.img3 = il.Add(wx.Bitmap("Images/16x16/Document.png", wx.BITMAP_TYPE_PNG))
##        self.img4 = il.Add(wx.Bitmap("Images/16x16/Presences.png", wx.BITMAP_TYPE_PNG))
##        self.img5 = il.Add(wx.Bitmap("Images/16x16/Scenario.png", wx.BITMAP_TYPE_PNG))
##        self.img6 = il.Add(wx.Bitmap("Images/16x16/Calculatrice.png", wx.BITMAP_TYPE_PNG))
##        self.img7 = il.Add(wx.Bitmap("Images/16x16/Candidature.png", wx.BITMAP_TYPE_PNG))
##        self.img8 = il.Add(wx.Bitmap("Images/16x16/Document2.png", wx.BITMAP_TYPE_PNG))
##        self.AssignImageList(il)
##
##        self.GetGrandParent().nouvelleFiche = False
##        
##        listePages = [
##            (PageQualifications.Panel_Statut(self, -1, IDpersonne=self.IDpersonne), _(u"G�n�ralit�s")),
##            (PageQuestionnaire.Panel(self, -1, IDpersonne=self.IDpersonne), _(u"Questionnaire")),
##            (PageContrats.Panel_Contrats(self, -1, IDpersonne=self.IDpersonne), _(u"Contrats")),
##            (PagePresences.Panel(self, -1, IDpersonne=self.IDpersonne), _(u"Pr�sences")),
##            ]
##        
##        index = 0
##        for panel, titre in listePages :
##            self.AddPage(panel, titre)
##            self.SetPageImage(index, index)
##            index += 1



class Notebook(wx.Notebook):
    def __init__(self, parent, id=-1, IDpersonne = 0):
        wx.Notebook.__init__(self, parent, id, style=
                             wx.BK_DEFAULT
                             #wx.BK_TOP 
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             # | wx.NB_MULTILINE
                             )
        
        self.IDpersonne = IDpersonne
        
        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        self.img1 = il.Add(wx.Bitmap("Images/16x16/Identite.png", wx.BITMAP_TYPE_PNG))
        self.img2 = il.Add(wx.Bitmap("Images/16x16/BlocNotes.png", wx.BITMAP_TYPE_PNG))
        self.img3 = il.Add(wx.Bitmap("Images/16x16/Document.png", wx.BITMAP_TYPE_PNG))
        self.img4 = il.Add(wx.Bitmap("Images/16x16/Presences.png", wx.BITMAP_TYPE_PNG))
        self.img5 = il.Add(wx.Bitmap("Images/16x16/Scenario.png", wx.BITMAP_TYPE_PNG))
        self.img6 = il.Add(wx.Bitmap("Images/16x16/Calculatrice.png", wx.BITMAP_TYPE_PNG))
        self.img7 = il.Add(wx.Bitmap("Images/16x16/Candidature.png", wx.BITMAP_TYPE_PNG))
        self.img8 = il.Add(wx.Bitmap("Images/16x16/Document2.png", wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        # Page G�n�ralit�s
        self.pageGeneralites = PageGeneralites.Panel_general(self, -1, IDpersonne=self.IDpersonne)
        self.AddPage(self.pageGeneralites, _(u"G�n�ralit�s"))
        self.SetPageImage(0, self.img1)
        
        # Enregistre la fiche si nouvelle personne et d�termination du nouvel IDpersonne
        if self.IDpersonne == 0 :
            self.GetGrandParent().nouvelleFiche = True
            self.pageGeneralites.Sauvegarde()
            self.IDpersonne = self.pageGeneralites.IDpersonne
        else:
            self.GetGrandParent().nouvelleFiche = False

        # Page Questionnaire
        self.pageQuestionnaire = PageQuestionnaire.Panel(self, -1, IDpersonne=self.IDpersonne)
        self.AddPage(self.pageQuestionnaire, _(u"Questionnaire"))
        self.SetPageImage(1, self.img8)

        # Page Qualifications
        self.pageStatut = PageQualifications.Panel_Statut(self, -1, IDpersonne=self.IDpersonne)
        self.AddPage(self.pageStatut, _(u"Qualifications"))
        self.SetPageImage(2, self.img2)
        
        # Page Contrats
        self.pageContrats = PageContrats.Panel_Contrats(self, -1, IDpersonne=self.IDpersonne)
        self.AddPage(self.pageContrats, _(u"Contrats"))
        self.SetPageImage(3, self.img3)
        
        # Page Pr�sences
        self.pagePresences = PagePresences.Panel(self, IDpersonne=self.IDpersonne)
        self.AddPage(self.pagePresences, _(u"Pr�sences"))
        self.SetPageImage(4, self.img4)
        
        # Page Sc�narios
        self.pageScenarios = PageScenarios.Panel(self, IDpersonne=self.IDpersonne)
        self.AddPage(self.pageScenarios, _(u"Sc�narios"))
        self.SetPageImage(5, self.img5)
        
        # Page Frais
        self.pageFrais = PageFrais.Panel(self, IDpersonne=self.IDpersonne)
        self.AddPage(self.pageFrais, _(u"Frais"))
        self.SetPageImage(6, self.img6)
        
        # Page Candidatures
        self.pageCandidatures = PageCandidatures.Panel(self, IDpersonne=self.IDpersonne)
        self.AddPage(self.pageCandidatures, _(u"Recrutement"))
        self.SetPageImage(7, self.img7)
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        
    def AfficheAutresPages(self, etat=True):
        """ Affiche les autres pages que G�n�ralit�s """
        if etat==True and self.GetPageCount()>1 :
            # On ne fait rien
            pass
        if etat==True and self.GetPageCount()<=1 :
            # On ajoute les pages
            self.AddPage(self.pageStatut, _(u"Questionnaire"))
            self.SetPageImage(1, self.img8)
            self.AddPage(self.pageStatut, _(u"Qualifications"))
            self.SetPageImage(2, self.img2)
            self.AddPage(self.pageContrats, _(u"Contrats"))
            self.SetPageImage(3, self.img3)
            self.AddPage(self.pagePresences, _(u"Pr�sences"))
            self.SetPageImage(4, self.img4)
            self.AddPage(self.pageScenarios, _(u"Sc�narios"))
            self.SetPageImage(5, self.img5)
            self.AddPage(self.pageFrais, _(u"Frais"))
            self.SetPageImage(6, self.img6)
            self.AddPage(self.pageCandidatures, _(u"Recrutement"))
            self.SetPageImage(7, self.img7)
            
        if etat==False and self.GetPageCount()>1 :
            # On enl�ve les pages
            self.RemovePage(7)
            self.RemovePage(6)
            self.RemovePage(5)
            self.RemovePage(4)
            self.RemovePage(3)
            self.RemovePage(2)
            self.RemovePage(1)
            
            
        
    def OnPageChanged(self, event):
        oldPage = event.GetOldSelection()
        newPage = event.GetSelection()
        page = self.GetPage(newPage)
        page.Refresh()
        # Si on quitte la page 0 (g�n�ralit�s), on sauvegarde les donn�es saisies sur la page
        if oldPage == 0 :
            self.GetGrandParent().AnnulationImpossible = True
            self.GetGrandParent().bitmap_button_annuler.Enable(False)
            self.pageGeneralites.Sauvegarde()
        event.Skip()
        
        
        
        
class MyFrame(wx.Frame):
    def __init__(self, parent, id=-1, titre=_(u"Fiche individuelle"), IDpersonne=0):
        wx.Frame.__init__(self, parent, id, titre, name="FicheIndividuelle", style=wx.DEFAULT_FRAME_STYLE)
        self.MakeModal(True)

        self.IDpersonne = IDpersonne
        self.contratEnCours = None
        self.AnnulationImpossible = False
        self.barre_problemes = None
        self.photo = None
        
        import locale
        self.locale = wx.Locale(wx.LANGUAGE_FRENCH)
        
        try : locale.setlocale(locale.LC_ALL, 'FR')
        except : pass
        
        self.panel_1 = wx.Panel(self, -1)
        self.label_hd_CatId = wx.StaticText(self.panel_1, -1, u"")
        self.static_line_1 = wx.StaticLine(self.panel_1, -1)
        self.label_hd_nomPrenom = wx.StaticText(self.panel_1, -1, _(u"NOM, Pr�nom"))
        self.label_hd_adresse = wx.StaticText(self.panel_1, -1, _(u"R�sidant 42 rue des oiseaux 29870 LANNILIS"))
        self.label_hd_naiss = wx.StaticText(self.panel_1, -1, _(u"Date et lieu de naissance inconnus"))
        self.bitmap_photo = CTRL_Photo.CTRL_Photo(self.panel_1, style=wx.SUNKEN_BORDER)
        self.bitmap_photo.SetPhoto(IDindividu=None, nomFichier="Images/128x128/Personne.png", taillePhoto=(128, 128), qualite=100)

        self.bitmap_button_aide = CTRL_Bouton_image.CTRL(self.panel_1, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bitmap_button_Ok = CTRL_Bouton_image.CTRL(self.panel_1, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bitmap_button_annuler = CTRL_Bouton_image.CTRL(self.panel_1, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
            
        # NoteBook
        self.notebook = Notebook(self.panel_1, IDpersonne=self.IDpersonne)
        if self.nouvelleFiche == True :
            self.notebook.AfficheAutresPages(False)  
        
        # Recherche s'il y a un contrat en cours ou � venir pour savoir s'il faut afficher la barre des probl�mes
        if self.IDpersonne in FonctionsPerso.Recherche_ContratsEnCoursOuAVenir() :
            self.barre_problemes = True
        else:
            self.barre_problemes = False
        
        # R�cup�ration de la liste des probl�mes de la personne
        self.bitmap_problemes_G = wx.StaticBitmap(self.panel_1, -1, wx.Bitmap("Images/Special/Problemes_G.png", wx.BITMAP_TYPE_PNG))
        self.bitmap_problemes_D = wx.StaticBitmap(self.panel_1, -1, wx.Bitmap("Images/Special/Problemes_D.png", wx.BITMAP_TYPE_PNG))
        self.txtDefilant = Ticker(self.panel_1,  size=(-1, 18), fgcolor=(255, 255, 255), bgcolor=(255, 60, 60))
        self.txtPbPersonne = self.Recup_txt_pb_personne() 
        self.txtDefilant.SetText(self.txtPbPersonne)
        
        # Mise � jour des infos du bandeau sup�rieur de la fiche
        self.MaJ_header()
            
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bitmap_button_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bitmap_button_Ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bitmap_button_annuler)
        self.txtDefilant.Bind(wx.EVT_MOTION, self.OnMotionTxtDefilant)
        self.txtDefilant.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveTxtDefilant)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
##        self.bitmap_photo.Bind(wx.EVT_LEFT_DOWN, self.MenuPhoto)
##        self.bitmap_photo.Bind(wx.EVT_RIGHT_DOWN, self.MenuPhoto)
##        
##        # Charge la photo de la personne
##        self.Charge_photo()
        
        
        self.__set_properties()
        self.__do_layout()
        
        self.Affichage_barre_problemes()


    def __set_properties(self):
        self.SetTitle("Fiche individuelle")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.label_hd_CatId.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_hd_nomPrenom.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.bitmap_photo.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.txtDefilant.SetToolTipString(_(u"Cette barre d'information recense les points\n� contr�ler sur le dossier de cette personne."))
        self.bitmap_photo.SetToolTipString("Cliquez sur le bouton droit de votre souris pour modifier cette image")
        self.bitmap_button_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bitmap_button_aide.SetSize(self.bitmap_button_aide.GetBestSize())
        self.bitmap_button_Ok.SetToolTipString("Cliquez ici pour valider")
        self.bitmap_button_Ok.SetSize(self.bitmap_button_Ok.GetBestSize())
        self.bitmap_button_annuler.SetToolTipString("Cliquez ici pour annuler")
        self.bitmap_button_annuler.SetSize(self.bitmap_button_annuler.GetBestSize())
        self.SetMinSize((720, 600))
        
    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=10)
        grid_sizer_header = wx.FlexGridSizer(rows=1, cols=2, vgap=0, hgap=0)
        sizer_header_textes = wx.BoxSizer(wx.VERTICAL)
        sizer_header_textes.Add(self.label_hd_CatId, 0, wx.ALIGN_RIGHT, 0)
        sizer_header_textes.Add(self.static_line_1, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 5)
        
        sizer_header_textes.Add(self.label_hd_nomPrenom, 0, wx.BOTTOM, 10)
        sizer_header_textes.Add(self.label_hd_adresse, 0, 0, 0)
        sizer_header_textes.Add(self.label_hd_naiss, 0, 0, 0)
        
        grid_sizer_problemes = wx.FlexGridSizer(rows=1, cols=3, vgap=0, hgap=0)
        grid_sizer_problemes.Add(self.bitmap_problemes_G, 0, 0, 0)
        grid_sizer_problemes.Add(self.txtDefilant, 0, wx.EXPAND, 0)
        grid_sizer_problemes.Add(self.bitmap_problemes_D, 0, 0, 0)
        grid_sizer_problemes.AddGrowableCol(1)
        sizer_header_textes.Add(grid_sizer_problemes, 0, wx.EXPAND|wx.TOP, 20)
        
        grid_sizer_header.Add(sizer_header_textes, 1, wx.EXPAND, 0)
        grid_sizer_header.Add(self.bitmap_photo, 0, wx.LEFT, 10)
        grid_sizer_header.AddGrowableCol(0)
        grid_sizer_1.Add(grid_sizer_header, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_1.Add(self.notebook, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bitmap_button_aide, 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bitmap_button_Ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bitmap_button_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableRow(0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_1.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.panel_1.SetSizer(grid_sizer_1)
        grid_sizer_1.AddGrowableRow(1)
        grid_sizer_1.AddGrowableCol(0)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        self.CentreOnScreen()

        self.sizer_header_textes = sizer_header_textes

    def Affichage_barre_problemes(self):
        """ Permet d'afficher ou non la barre des probl�mes """
        if self.txtPbPersonne == "" or self.barre_problemes == False :
            self.bitmap_problemes_G.Show(False)
            self.bitmap_problemes_D.Show(False)
            self.txtDefilant.Show(False)
            self.txtDefilant.Stop()
        else:
            self.bitmap_problemes_G.Show(True)
            self.bitmap_problemes_D.Show(True)
            self.txtDefilant.Show(True)
            self.txtDefilant.Start()
        
    def MAJ_barre_problemes(self):
        """ Recherche le texte de la barre des problemes """
        if self.barre_problemes == None : return
        if self.barre_problemes == False : 
            self.Affichage_barre_problemes()
        else:
            self.txtPbPersonne = self.MAJ_txt_pb_personne() 
            self.txtDefilant.SetText(self.txtPbPersonne)
            self.Affichage_barre_problemes()

   
        
    def Recup_txt_pb_personne(self):
        """ R�cup�re un texte de la liste des probl�mes de la personne """
        dictNomsPersonnes, dictProblemesPersonnes = FonctionsPerso.Recup_liste_pb_personnes()
        if dictProblemesPersonnes.has_key(self.IDpersonne):
            txtProblemes = ""
            for labelCategorie, listeProblemes in dictProblemesPersonnes[self.IDpersonne].iteritems() :
                txtProblemes += labelCategorie + " ("
                for labelProbleme in listeProblemes :
                    txtProblemes += labelProbleme + ", "
                txtProblemes = txtProblemes[:-2] + ")       "
            return txtProblemes
        else:
            return ""

    def MAJ_txt_pb_personne(self):
        """ R�cup�re un texte de la liste des probl�mes de la personne """
        civilite = self.notebook.pageGeneralites.combo_box_civilite.GetStringSelection()
        nom= self.notebook.pageGeneralites.text_nom.GetValue()
        nom_jfille = self.notebook.pageGeneralites.text_ctrl_nomjf.GetValue()
        prenom = self.notebook.pageGeneralites.text_prenom.GetValue()

        # Validation date de naissance
        temp = self.notebook.pageGeneralites.text_date_naiss.GetValue()
        if temp == "  /  /    ":
            date_naiss = None
        else:
            jour = int(temp[:2])
            mois = int(temp[3:5])
            annee = int(temp[6:10])
            date_naiss = datetime.date(annee, mois, jour)
        
        cp_naiss = self.notebook.pageGeneralites.text_cp_naiss.GetValue()
        ville_naiss = self.notebook.pageGeneralites.text_ville_naiss.GetValue()
        pays_naiss = self.notebook.pageGeneralites.IDpays_naiss
        nationalite = self.notebook.pageGeneralites.IDpays_nation
        num_secu = self.notebook.pageGeneralites.text_numsecu.GetValue()
        adresse_resid = self.notebook.pageGeneralites.text_adresse.GetValue()
        cp_resid = self.notebook.pageGeneralites.text_cp.GetValue()
        ville_resid = self.notebook.pageGeneralites.text_ville.GetValue()
        
        # Validation IDSituation
        try:
            temp = self.notebook.pageGeneralites.combo_box_situation.GetClientData(self.notebook.pageGeneralites.combo_box_situation.GetSelection())
            if temp == None or temp == '':
                IDsituation = 0
            else:
                IDsituation = temp
        except:
            IDsituation = 0
        
        infosPersonne = ((self.IDpersonne, civilite, nom, nom_jfille, prenom, date_naiss, cp_naiss, ville_naiss, pays_naiss, nationalite, num_secu, adresse_resid, cp_resid, ville_resid, IDsituation),)
        dictNomsPersonnes, dictProblemesPersonnes = FonctionsPerso.Recherche_problemes_personnes(listeIDpersonnes = (self.IDpersonne,), infosPersonne=infosPersonne)
        if dictProblemesPersonnes.has_key(self.IDpersonne):
            txtProblemes = ""
            for labelCategorie, listeProblemes in dictProblemesPersonnes[self.IDpersonne].iteritems() :
                txtProblemes += labelCategorie + " ("
                for labelProbleme in listeProblemes :
                    txtProblemes += labelProbleme + ", "
                txtProblemes = txtProblemes[:-2] + ")       "
            return txtProblemes
        else:
            return ""
                
    def MaJ_header(self):
        # M�J de l'affichage de ID :
        if self.IDpersonne == 0:
            ID = "Attribution de l'ID en cours"
        else:
            ID = self.IDpersonne
        # M�J de l'affichage du contrat en cours :
        if self.contratEnCours == None :
            txtContrat = _(u"Aucun contrat en cours")
        else:
            date_debut = FonctionsPerso.DateEngFr(self.contratEnCours[1])
            if self.contratEnCours[2] == "2999-01-01" :
                txtContrat = _(u"Contrat en cours : ") + self.contratEnCours[0] + " depuis le " + date_debut + _(u" (Dur�e ind.)")
            else:
                date_fin = FonctionsPerso.DateEngFr(self.contratEnCours[2])
                date_rupture = FonctionsPerso.DateEngFr(self.contratEnCours[3])
                if date_rupture != "//" : date_fin = date_rupture
                txtContrat = _(u"Contrat en cours : ") + self.contratEnCours[0] + " du " + date_debut + " au " + date_fin
            
        # Affichage
        self.label_hd_CatId.SetLabel(txtContrat + " | ID : " + str(ID))
        try : self.sizer_header_textes.Layout()
        except : pass

    def OnMotionTxtDefilant(self, event):
        self.txtDefilant.Stop()
        event.Skip()

    def OnLeaveTxtDefilant(self, event):
        self.txtDefilant.Start()
        event.Skip()
        
    def OnBoutonAide(self, event):
        FonctionsPerso.Aide(57)

    def OnBoutonOk(self, event):
        self.AnnulationImpossible = False
        self.Fermer(save=True)        
        event.Skip()

    def OnBoutonAnnuler(self, event): 
        # Test d'importation des donn�es de la base
        if self.AnnulationImpossible == True :
            self.Fermer(save=True)
        else:
            self.Fermer(save=False)
        event.Skip()

    def OnClose(self, event):
        if self.AnnulationImpossible == True :
            self.Fermer(save=True)
        else:
            self.Fermer(save=False)
        event.Skip()

    def Fermer(self, save=True):
        """ Fermeture """
        if save == False :
            # Annulation impossible
##            if self.AnnulationImpossible == True :
##                txtMessage = _(u"D�sol�, il m'est impossible d'annuler maintenant. Vous devez donc cliquer sur le bouton 'Ok'. \n\nVoulez-vous que je le fasse pour vous maintenant ?")
##                dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Annulation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
##                reponse = dlgConfirm.ShowModal()
##                dlgConfirm.Destroy()
##                if reponse == wx.ID_NO:
##                    return
            
            # Annule la cr�ation d'une nouvelle fiche
            if self.nouvelleFiche == True :
                db = GestionDB.DB()
                # Suppression des coordonn�es d�j� saisies
                db.ReqDEL("coordonnees", "IDpersonne", self.IDpersonne)
                # Suppression de la personne dans la base
                db.ReqDEL("personnes", "IDpersonne", self.IDpersonne)
                
        else :
            # Sauvegarde des donn�es
            # V�rifie que les infos principales sont saisies :
            if self.Verifie_validite_donnees() == True :                
                self.notebook.pageGeneralites.Sauvegarde()
                self.notebook.pageQuestionnaire.Sauvegarde()
            else:
                return
         
        # Recherche si un parent est � mettre � jour
        frm = FonctionsPerso.FrameOuverte("Personnes")
        if frm != None :
            frm.listCtrl_personnes.MAJ(IDpersonne=self.IDpersonne)
            frm.panel_dossiers.tree_ctrl_problemes.MAJ_treeCtrl()
        # Fin
        self.MakeModal(False)
        self.Destroy()
    
    def Verifie_validite_donnees(self):
        # V�rifie Civilit�        
        if self.notebook.pageGeneralites.combo_box_civilite.GetStringSelection() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir obligatoirement une civilit� !"), "Information", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.notebook.pageGeneralites.combo_box_civilite.SetFocus()
            return False
        # V�rifie Nom        
        if self.notebook.pageGeneralites.text_nom.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir obligatoirement un nom de famille !"), "Information", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.notebook.pageGeneralites.text_nom.SetFocus()
            return False
        # V�rifie Pr�nom        
        if self.notebook.pageGeneralites.text_prenom.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir obligatoirement un pr�nom !"), "Information", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.notebook.pageGeneralites.text_prenom.SetFocus()
            return False
        return True
    
##    def Ajoute_image(self):
##        """ Permet la s�lection et le retouchage d'une photo pour la personne """
##        # S�lection d'une image
##        self.repCourant = os.getcwd()
##        
##        wildcard = "Photo JPEG (*.jpg)|*.jpg|"     \
##           "All files (*.*)|*.*"
##                
##        # R�cup�ration du chemin des documents
##        sp = wx.StandardPaths.Get()
##        cheminDefaut = sp.GetDocumentsDir()
##        # Ouverture dela fen�tre de dialogue
##        dlg = wx.FileDialog(
##            self, message=_(u"Choisissez une photo"),
##            defaultDir=cheminDefaut, 
##            defaultFile="",
##            wildcard=wildcard,
##            style=wx.OPEN
##            )
##        if dlg.ShowModal() == wx.ID_OK:
##            nomFichierCourt = dlg.GetFilename()
##            nomFichierLong = dlg.GetPath()
##            dlg.Destroy()
##        else:
##            dlg.Destroy()
##            return
##        
##        # Recadre la photo
##        frm = Editeur_photo.MyFrame(self, IDpersonne=self.IDpersonne, image=nomFichierLong)
##        frm.Show()
##
##    def RecupIDfichier(self):
##        """ R�cup�re le code identifiant unique du fichier """
##        DB = GestionDB.DB()        
##        req = "SELECT codeIDfichier FROM divers WHERE IDdivers=1;"
##        DB.ExecuterReq(req)
##        donnees = DB.ResultatReq()
##        DB.Close()
##        codeIDfichier = donnees[0][0]
##        return codeIDfichier
##    
##    def Charge_photo(self):
##        """ Charge la photo de la personne """
##        self.photo = None
##        nomFichier = "Photos/" + self.RecupIDfichier() + str(self.IDpersonne) + ".jpg"
##        # On regarde s'il y a une photo pr�sente dans le r�pertoire Photos pour cette personne
##        if os.path.isfile(nomFichier):
##            # Recherche si un cadre de d�co est rattach�
##            nomCadre = FonctionsPerso.RecupNomCadrePersonne(self.IDpersonne)
##            if nomCadre != None :
##                # V�rifie que le cadre d�co existe dans le r�pertoire
##                if os.path.isfile("Images/CadresPhotos/" + nomCadre + ".png") :
##                    bmp = FonctionsPerso.CreationPhotoPersonne(IDpersonne=self.IDpersonne, nomFichierPhoto=nomFichier, tailleFinale = (128, 128), qualiteBmp = 50)
##                else:
##                    nomCadre = None
##        
##            # Si pas de cadre de d�co
##            if nomCadre == None or nomCadre == "" :
##                bmp = wx.Bitmap(nomFichier, wx.BITMAP_TYPE_ANY)
##                bmp = bmp.ConvertToImage()
##                bmp = bmp.Rescale(width=128, height=128, quality=80) 
##                bmp = bmp.ConvertToBitmap()
##                
##            # Met la photo dans le StaticBitmap
##            self.bitmap_photo.SetBitmap(bmp)
##            self.photo = nomFichier
##
##    def MenuPhoto(self, event):
##        """Ouverture du menu contextuel de la photo """
##        
##        # Cr�ation du menu contextuel
##        menuPop = wx.Menu()
##
##        # Item Ajouter
##        item = wx.MenuItem(menuPop, 10, _(u"Importer une photo"))
##        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Menu_Ajouter, id=10)
##
##        # Item Modifier
##        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
##        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Menu_Modifier, id=20)
##        if self.photo == None : item.Enable(False)
##
##        # Item Supprimer
##        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
##        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Menu_Supprimer, id=30)
##        if self.photo == None : item.Enable(False)
##        
##        menuPop.AppendSeparator()
##        
##         # Item Imprimer
##        item = wx.MenuItem(menuPop, 40, _(u"Imprimer la photo"))
##        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.Menu_Imprimer, id=40)
##        if self.photo == None : item.Enable(False)
##        
##        menuPop.AppendSeparator()
##        
##        # Choix d'un cadre de d�coration
##        nomCadrePersonne = self.RecupNomCadrePersonne()
##        sousmenu1 = wx.Menu()
##        indexID = 500
##        for nomCadre in FonctionsPerso.GetListeCadresPhotos() :
##            sousmenu1.Append(indexID, nomCadre.decode("iso-8859-15"), _(u"Choisir le cadre de d�coration '") + nomCadre.decode("iso-8859-15") + _(u"' pour cette personne"), wx.ITEM_RADIO)
##            if nomCadre.decode("iso-8859-15") == nomCadrePersonne :
##                sousmenu1.Check(indexID, True)
##            self.Bind(wx.EVT_MENU, self.Menu_ChoixCadre, id=indexID)
##            indexID += 1
##        menuPop.AppendMenu(50, _(u"Choisir un cadre de d�coration"), sousmenu1)
##        self.PopupMenu(menuPop)
##        menuPop.Destroy()
##        
##    def Menu_ChoixCadre(self, event):
##        index = event.GetId() - 500
##        if index == 0 : 
##            nomCadre = ""
##        else :
##            nomCadre = FonctionsPerso.GetListeCadresPhotos()[index]
##            nomCadre = nomCadre.decode("iso-8859-15")
##        # Sauvegarde le choix du cadre
##        listeDonnees = [("cadre_photo", nomCadre),]
##        DB = GestionDB.DB()
##        DB.ReqMAJ("personnes", listeDonnees, "IDpersonne", self.IDpersonne)
##        DB.Close()
##        # MAJ de la photo affich�e
##        self.Charge_photo()
##
##    def RecupNomCadrePersonne(self):
##        """ R�cup�re le code identifiant unique du fichier """
##        DB = GestionDB.DB()        
##        req = "SELECT cadre_photo FROM personnes WHERE IDpersonne=%d;" % self.IDpersonne
##        DB.ExecuterReq(req)
##        donnees = DB.ResultatReq()
##        DB.Close()
##        cadre_photo = donnees[0][0]
##        return cadre_photo
##    
##    def Menu_Ajouter(self, event):
##        self.Ajoute_image()
##        
##    def Menu_Modifier(self, event):
##        frm = Editeur_photo.MyFrame(self, IDpersonne=self.IDpersonne, image=self.photo)
##        frm.Show()
##
##    def Menu_Supprimer(self, event):
##        """ Suppression de la photo """
##        txtMessage = _(u"Souhaitez-vous vraiment supprimer cette photo ?")
##        dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Confirmation de suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
##        reponse = dlgConfirm.ShowModal()
##        dlgConfirm.Destroy()
##        if reponse == wx.ID_NO:
##            return
##        # Suppression de la photo du DD
##        if os.path.isfile(self.photo):
##            os.remove(self.photo)
##        # Recharge l'image par d�faut
##        self.photo = None
##        self.notebook.pageGeneralites.MAJ_Photo()
##        
##    def Menu_Imprimer(self, event):
##        """ Impression de la photo de la personne """
##        # R�cup�ration de la liste des personnes
##        DB = GestionDB.DB()        
##        req = """SELECT IDpersonne, nom, prenom FROM personnes WHERE IDpersonne=%d; """ % self.IDpersonne
##        DB.ExecuterReq(req)
##        donnees = DB.ResultatReq()[0]
##        DB.Close()
##        # Ouverture de la frame d'impression des photos  
##        import Impression_photo
##        frame = Impression_photo.MyFrame(None, listePersonnes=[[self.IDpersonne, donnees[1], donnees[2], None],])
##        frame.Show()
##
##    def wxtopil(self, image):
##        """Convert wx.Image to PIL Image."""
##        pil = Image.new('RGB', (image.GetWidth(), image.GetHeight()))
##        pil.fromstring(image.GetData())
##        return pil










if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()

##    dlgSaisie = wx.TextEntryDialog(None, _(u"Entrez un ID :"), "Choix de l'ID", "0", style=wx.OK|wx.CANCEL)
##    reponse = dlgSaisie.ShowModal()
##    if reponse == wx.ID_OK:
##        ID = int(dlgSaisie.GetValue())
##    dlgSaisie.Destroy()
    
    fiche = MyFrame(None, -1, "", IDpersonne=1)
    app.SetTopWindow(fiche)
    fiche.Show()
    app.MainLoop()
