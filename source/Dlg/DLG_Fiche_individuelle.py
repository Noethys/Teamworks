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
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Page_generalites
from Ctrl import CTRL_Page_questionnaire
from Ctrl import CTRL_Page_qualifications
from Ctrl import CTRL_Page_contrats
from Ctrl import CTRL_Page_presences
from Ctrl import CTRL_Page_frais
from Ctrl import CTRL_Page_scenarios
from Ctrl import CTRL_Page_candidatures
import FonctionsPerso
import datetime
import GestionDB
from wx.lib.ticker import Ticker
from Ctrl import CTRL_Photo



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
        self.img1 = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Identite.png"), wx.BITMAP_TYPE_PNG))
        self.img2 = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/BlocNotes.png"), wx.BITMAP_TYPE_PNG))
        self.img3 = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document.png"), wx.BITMAP_TYPE_PNG))
        self.img4 = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Presences.png"), wx.BITMAP_TYPE_PNG))
        self.img5 = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Scenario.png"), wx.BITMAP_TYPE_PNG))
        self.img6 = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calculatrice.png"), wx.BITMAP_TYPE_PNG))
        self.img7 = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Candidature.png"), wx.BITMAP_TYPE_PNG))
        self.img8 = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document2.png"), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        # Page Généralités
        self.pageGeneralites = CTRL_Page_generalites.Panel_general(self, -1, IDpersonne=self.IDpersonne)
        self.AddPage(self.pageGeneralites, _(u"Généralités"))
        self.SetPageImage(0, self.img1)
        
        # Enregistre la fiche si nouvelle personne et détermination du nouvel IDpersonne
        if self.IDpersonne == 0 :
            self.GetGrandParent().nouvelleFiche = True
            self.pageGeneralites.Sauvegarde()
            self.IDpersonne = self.pageGeneralites.IDpersonne
        else:
            self.GetGrandParent().nouvelleFiche = False

        # Page Questionnaire
        self.pageQuestionnaire = CTRL_Page_questionnaire.Panel(self, -1, IDpersonne=self.IDpersonne)
        self.AddPage(self.pageQuestionnaire, _(u"Questionnaire"))
        self.SetPageImage(1, self.img8)

        # Page Qualifications
        self.pageStatut = CTRL_Page_qualifications.Panel_Statut(self, -1, IDpersonne=self.IDpersonne)
        self.AddPage(self.pageStatut, _(u"Qualifications"))
        self.SetPageImage(2, self.img2)
        
        # Page Contrats
        self.pageContrats = CTRL_Page_contrats.Panel_Contrats(self, -1, IDpersonne=self.IDpersonne)
        self.AddPage(self.pageContrats, _(u"Contrats"))
        self.SetPageImage(3, self.img3)
        
        # Page Présences
        self.pagePresences = CTRL_Page_presences.Panel(self, IDpersonne=self.IDpersonne)
        self.AddPage(self.pagePresences, _(u"Présences"))
        self.SetPageImage(4, self.img4)
        
        # Page Scénarios
        self.pageScenarios = CTRL_Page_scenarios.Panel(self, IDpersonne=self.IDpersonne)
        self.AddPage(self.pageScenarios, _(u"Scénarios"))
        self.SetPageImage(5, self.img5)
        
        # Page Frais
        self.pageFrais = CTRL_Page_frais.Panel(self, IDpersonne=self.IDpersonne)
        self.AddPage(self.pageFrais, _(u"Frais"))
        self.SetPageImage(6, self.img6)
        
        # Page Candidatures
        self.pageCandidatures = CTRL_Page_candidatures.Panel(self, IDpersonne=self.IDpersonne)
        self.AddPage(self.pageCandidatures, _(u"Recrutement"))
        self.SetPageImage(7, self.img7)
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        
    def AfficheAutresPages(self, etat=True):
        """ Affiche les autres pages que Généralités """
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
            self.AddPage(self.pagePresences, _(u"Présences"))
            self.SetPageImage(4, self.img4)
            self.AddPage(self.pageScenarios, _(u"Scénarios"))
            self.SetPageImage(5, self.img5)
            self.AddPage(self.pageFrais, _(u"Frais"))
            self.SetPageImage(6, self.img6)
            self.AddPage(self.pageCandidatures, _(u"Recrutement"))
            self.SetPageImage(7, self.img7)
            
        if etat==False and self.GetPageCount()>1 :
            # On enlève les pages
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
        # Si on quitte la page 0 (généralités), on sauvegarde les données saisies sur la page
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
        self.label_hd_nomPrenom = wx.StaticText(self.panel_1, -1, _(u"NOM, Prénom"))
        self.label_hd_adresse = wx.StaticText(self.panel_1, -1, _(u"Résidant 42 rue des oiseaux 29870 LANNILIS"))
        self.label_hd_naiss = wx.StaticText(self.panel_1, -1, _(u"Date et lieu de naissance inconnus"))
        self.bitmap_photo = CTRL_Photo.CTRL_Photo(self.panel_1, style=wx.SUNKEN_BORDER)
        self.bitmap_photo.SetPhoto(IDindividu=None, nomFichier=Chemins.GetStaticPath("Images/128x128/Personne.png"), taillePhoto=(128, 128), qualite=100)

        self.bitmap_button_aide = CTRL_Bouton_image.CTRL(self.panel_1, texte=_(u"Aide"), cheminImage=Chemins.GetStaticPath("Images/32x32/Aide.png"))
        self.bitmap_button_Ok = CTRL_Bouton_image.CTRL(self.panel_1, texte=_(u"Ok"), cheminImage=Chemins.GetStaticPath("Images/32x32/Valider.png"))
        self.bitmap_button_annuler = CTRL_Bouton_image.CTRL(self.panel_1, texte=_(u"Annuler"), cheminImage=Chemins.GetStaticPath("Images/32x32/Annuler.png"))
            
        # NoteBook
        self.notebook = Notebook(self.panel_1, IDpersonne=self.IDpersonne)
        if self.nouvelleFiche == True :
            self.notebook.AfficheAutresPages(False)  
        
        # Recherche s'il y a un contrat en cours ou à venir pour savoir s'il faut afficher la barre des problèmes
        if self.IDpersonne in FonctionsPerso.Recherche_ContratsEnCoursOuAVenir() :
            self.barre_problemes = True
        else:
            self.barre_problemes = False
        
        # Récupération de la liste des problèmes de la personne
        self.bitmap_problemes_G = wx.StaticBitmap(self.panel_1, -1, wx.Bitmap(Chemins.GetStaticPath("Images/Special/Problemes_G.png"), wx.BITMAP_TYPE_PNG))
        self.bitmap_problemes_D = wx.StaticBitmap(self.panel_1, -1, wx.Bitmap(Chemins.GetStaticPath("Images/Special/Problemes_D.png"), wx.BITMAP_TYPE_PNG))
        self.txtDefilant = Ticker(self.panel_1,  size=(-1, 18), fgcolor=(255, 255, 255), bgcolor=(255, 60, 60))
        self.txtPbPersonne = self.Recup_txt_pb_personne() 
        self.txtDefilant.SetText(self.txtPbPersonne)
        
        # Mise à jour des infos du bandeau supérieur de la fiche
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
        _icon.CopyFromBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Logo.png"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.label_hd_CatId.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_hd_nomPrenom.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.bitmap_photo.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.txtDefilant.SetToolTipString(_(u"Cette barre d'information recense les points\nà contrôler sur le dossier de cette personne."))
        self.bitmap_photo.SetToolTipString("Cliquez sur le bouton droit de votre souris pour modifier cette image")
        self.bitmap_button_aide.SetToolTipString("Cliquez ici pour obtenir de l'aide")
        self.bitmap_button_aide.SetSize(self.bitmap_button_aide.GetBestSize())
        self.bitmap_button_Ok.SetToolTipString("Cliquez ici pour valider")
        self.bitmap_button_Ok.SetSize(self.bitmap_button_Ok.GetBestSize())
        self.bitmap_button_annuler.SetToolTipString("Cliquez ici pour annuler")
        self.bitmap_button_annuler.SetSize(self.bitmap_button_annuler.GetBestSize())
        self.SetMinSize((770, 600))
        
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
        """ Permet d'afficher ou non la barre des problèmes """
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
        """ Récupère un texte de la liste des problèmes de la personne """
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
        """ Récupère un texte de la liste des problèmes de la personne """
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
        # MàJ de l'affichage de ID :
        if self.IDpersonne == 0:
            ID = "Attribution de l'ID en cours"
        else:
            ID = self.IDpersonne
        # MàJ de l'affichage du contrat en cours :
        if self.contratEnCours == None :
            txtContrat = _(u"Aucun contrat en cours")
        else:
            date_debut = FonctionsPerso.DateEngFr(self.contratEnCours[1])
            if self.contratEnCours[2] == "2999-01-01" :
                txtContrat = _(u"Contrat en cours : ") + self.contratEnCours[0] + " depuis le " + date_debut + _(u" (Durée ind.)")
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
        # Test d'importation des données de la base
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
##                txtMessage = _(u"Désolé, il m'est impossible d'annuler maintenant. Vous devez donc cliquer sur le bouton 'Ok'. \n\nVoulez-vous que je le fasse pour vous maintenant ?")
##                dlgConfirm = wx.MessageDialog(self, txtMessage, _(u"Annulation"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
##                reponse = dlgConfirm.ShowModal()
##                dlgConfirm.Destroy()
##                if reponse == wx.ID_NO:
##                    return
            
            # Annule la création d'une nouvelle fiche
            if self.nouvelleFiche == True :
                db = GestionDB.DB()
                # Suppression des coordonnées déjà saisies
                db.ReqDEL("coordonnees", "IDpersonne", self.IDpersonne)
                # Suppression de la personne dans la base
                db.ReqDEL("personnes", "IDpersonne", self.IDpersonne)
                
        else :
            # Sauvegarde des données
            # Vérifie que les infos principales sont saisies :
            if self.Verifie_validite_donnees() == True :                
                self.notebook.pageGeneralites.Sauvegarde()
                self.notebook.pageQuestionnaire.Sauvegarde()
            else:
                return
         
        # Recherche si un parent est à mettre à jour
        frm = FonctionsPerso.FrameOuverte("Personnes")
        if frm != None :
            frm.listCtrl_personnes.MAJ(IDpersonne=self.IDpersonne)
            frm.panel_dossiers.tree_ctrl_problemes.MAJ_treeCtrl()
        # Fin
        self.MakeModal(False)
        self.Destroy()
    
    def Verifie_validite_donnees(self):
        # Vérifie Civilité        
        if self.notebook.pageGeneralites.combo_box_civilite.GetStringSelection() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir obligatoirement une civilité !"), "Information", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.notebook.pageGeneralites.combo_box_civilite.SetFocus()
            return False
        # Vérifie Nom        
        if self.notebook.pageGeneralites.text_nom.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir obligatoirement un nom de famille !"), "Information", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.notebook.pageGeneralites.text_nom.SetFocus()
            return False
        # Vérifie Prénom        
        if self.notebook.pageGeneralites.text_prenom.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir obligatoirement un prénom !"), "Information", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.notebook.pageGeneralites.text_prenom.SetFocus()
            return False
        return True
    










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
