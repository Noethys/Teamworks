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
import Scenario_gestion

try: import psyco; psyco.full()
except: pass


class Panel(wx.Panel):
    def __init__(self, parent, id=-1, IDpersonne=0):
        wx.Panel.__init__(self, parent, id, name="panel_pageScenarios", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDpersonne = IDpersonne

        # Widgets
        self.staticBox_staticbox = wx.StaticBox(self, -1, _(u"Scénarios"))
        self.panelScenarios = Scenario_gestion.Panel(self, IDpersonne=self.IDpersonne)
        self.panelScenarios.label_introduction.Show(False)
        
        self.__do_layout()


    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        staticBox = wx.StaticBoxSizer(self.staticBox_staticbox, wx.VERTICAL)
        staticBox.Add(self.panelScenarios, 1, wx.EXPAND|wx.ALL, 5)
        grid_sizer_base.Add(staticBox, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

