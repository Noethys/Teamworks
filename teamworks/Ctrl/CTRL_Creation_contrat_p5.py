#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Auteur:        Ivan LUCAS
# Copyright:    (c) 2008-09 Ivan LUCAS
# Licence:      Licence GNU GPL
#-----------------------------------------------------------

from Utils.UTILS_Traduction import _
import wx
import six
import  wx.lib.scrolledpanel as scrolled


class PanelDefilant(scrolled.ScrolledPanel):
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent, -1)
        
        self.Creation_champs()
    
    def Creation_champs(self):       
        # Récupération des données
        self.dicoChampsTous = self.GetGrandParent().GetParent().page4.listCtrl_champs.dictChamps
        self.selections = self.GetGrandParent().GetParent().page4.listCtrl_champs.selections
        self.dicoChamps = {}
        for ID, valeurs in self.dicoChampsTous.items() :
            if ID in self.selections :
                self.dicoChamps[ID] = valeurs
                
        # Modification du texte d'intro du panel
        if len(self.dicoChamps) == 0 :
            self.GetParent().label_intro.SetLabel(_(u"Vous n'avez aucun champ à remplir. Cliquez sur 'Suite'..."))
        else:
            self.GetParent().label_intro.SetLabel(_(u"Vous pouvez maintenant remplir vos champs personnalisés :"))
        
        # Création des champs dans l'interface
        grid_sizer = wx.FlexGridSizer(rows=len(self.dicoChamps)+1, cols=1, vgap=10, hgap=10)
        
        for ID, valeurs in self.dicoChamps.items() : 
            nom = "champ" + str(ID)
            label = valeurs[1]
            infoBulle = valeurs[2]
            motCle = valeurs[3]
            valeur = valeurs[4]
            exemple = valeurs[5]
            
            # Importation de la valeur si le contrat est en modification
            d = self.GetGrandParent().GetParent().dictChamps
            if ID in list(d.keys()) : valeur = d[ID]
            
            # TextCtrl pour réponse
            self.sizer_champs = wx.StaticBox(self, -1, label)
            sizer_champ = wx.StaticBoxSizer(self.sizer_champs, wx.VERTICAL)
            setattr(self, "text_%s" % nom, wx.TextCtrl(self, -1, six.text_type(valeur)))
            getattr(self, "text_%s" % nom).SetToolTip(wx.ToolTip(infoBulle))
            sizer_champ.Add(getattr(self, "text_%s" % nom), 0, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 0)

            # Exemple :
            if exemple != "" :
                txtExemple = "Ex. : " + exemple[:60]
                setattr(self, "label_%sEX" % nom, wx.StaticText(self, -1, txtExemple))
                getattr(self, "label_%sEX" % nom).SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ''))
                getattr(self, "label_%sEX" % nom).SetForegroundColour((120, 120, 120))
                sizer_champ.Add(getattr(self, "label_%sEX" % nom), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

            grid_sizer.Add(sizer_champ, 1, wx.RIGHT|wx.EXPAND, 10)

        grid_sizer.AddGrowableCol(0)
        self.SetSizer(grid_sizer)
        
        # Initialisation des barres de défilement
        self.SetupScrolling()
        
        
class Page(wx.Panel):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.label_titre = wx.StaticText(self, -1, _(u"4. Remplissage des champs personnalisés"))
        self.label_intro = wx.StaticText(self, -1, _(u"Vous pouvez maintenant remplir vos champs personnalisés :"))
        self.panelDefilant = wx.Panel(self, -1)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.label_titre.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_titre, 0, 0, 0)
        grid_sizer_base.Add(self.label_intro, 0, wx.LEFT, 20)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        sizer_pages.Add(self.panelDefilant, 1, wx.LEFT|wx.EXPAND, 20)
        grid_sizer_base.Add(sizer_pages, 1, wx.LEFT|wx.EXPAND, 20)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.sizer_pages = sizer_pages

    def MAJ_panelDefilant(self):
        # Destruction du panel actuel
        self.panelDefilant.Destroy()
        # Recontruction avec les nouveaux contrôles
        self.panelDefilant = PanelDefilant(self)
        self.sizer_pages.Add(self.panelDefilant, 1, wx.LEFT|wx.EXPAND, 20)
        self.sizer_pages.Layout()


    def Validation(self):
        
        # Vérifie que les champs ont été remplis
        listeInvalides = []
        dictChamps = {}
        for ID, valeurs in self.panelDefilant.dicoChamps.items() : 
            nom = "champ" + str(ID)
            label = valeurs[1]
            texte = getattr(self.panelDefilant, "text_%s" % nom).GetValue()
                        
            # Critères de validation
            if texte == "" :
                listeInvalides.append(label)
            else:
                # Mémorisation pour enr. base de données (cf plus bas)
                dictChamps[ID] = texte

        if len(listeInvalides) == 1 :
            txtMessage = _(u"Vous n'avez pas rempli le champ suivant : '") + listeInvalides[0]
            txtMessage += _(u"'\n\nSouhaitez-vous continuer quand même ?")
            dlg = wx.MessageDialog(self, txtMessage, _(u"Demande de confirmation"), wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_NO :
                dlg.Destroy() 
                return False
                    
        if len(listeInvalides) > 1 :
            txtMessage = _(u"Vous n'avez pas rempli les champs suivants : \n\n")
            for item in listeInvalides :
                txtMessage += "      - " + item + "\n"
            txtMessage += _(u"\nSouhaitez-vous continuer quand même ?")
            dlg = wx.MessageDialog(self, txtMessage, _(u"Demande de confirmation"), wx.ICON_QUESTION | wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_NO :
                dlg.Destroy() 
                return False
        
        # Mémorisation des données pour l'enregistrement dans la base de données
        self.GetGrandParent().dictChamps = dictChamps
            
        return True