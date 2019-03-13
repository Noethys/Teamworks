#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import sys
from importlib import import_module


def Import(nom_module=""):
    # Essaye d'importer
    try :
        module = import_module(nom_module)
        return module
    except ImportError:
        pass

    # Recherche si le module est d�j� charg�
    if nom_module in sys.modules:
        module = sys.modules[nom_module]
        return module

    # Essaye d'importer sans le module_path
    module_path, class_name = nom_module.rsplit('.', 1)
    try :
        module = import_module(class_name)
        return module
    except ImportError:
        pass

    return None



class Menu(wx.Menu):
    def __init__(self, *args, **kwds):
        wx.Menu.__init__(self, *args, **kwds)

    def AppendItem(self, item):
        if 'phoenix' in wx.PlatformInfo:
            super(Menu, self).Append(item)
        else :
            super(Menu, self).AppendItem(item)

    def AppendMenu(self, *args, **kwds):
        if 'phoenix' in wx.PlatformInfo:
            super(Menu, self).Append(*args, **kwds)
        else :
            super(Menu, self).AppendMenu(*args, **kwds)


class ToolBar(wx.ToolBar):
    def __init__(self, *args, **kwds):
        wx.ToolBar.__init__(self, *args, **kwds)

    def AddLabelTool(self, *args, **kw):
        if 'phoenix' in wx.PlatformInfo:
            if "longHelp" in kw:
                kw.pop("longHelp")
            super(ToolBar, self).AddTool(*args, **kw)
        else :
            super(ToolBar, self).AddLabelTool(*args, **kw)

    def AddSimpleTool(self, *args, **kw):
        if 'phoenix' in wx.PlatformInfo:
            if "longHelp" in kw:
                kw.pop("longHelp")
            super(ToolBar, self).AddTool(*args, **kw)
        else :
            super(ToolBar, self).AddSimpleTool(*args, **kw)

    def AddTool(self, *args, **kw):
        if 'phoenix' in wx.PlatformInfo:
            if "shortHelpString" in kw:
                shortHelp = kw.pop("shortHelpString")
            else:
                shortHelp = ""
            toolId = args[0]
            bitmap = args[1]
            super(ToolBar, self).AddTool(toolId=toolId, label="", bitmap=bitmap, shortHelp=shortHelp)
        else :
            super(ToolBar, self).AddTool(*args, **kw)


if __name__ == "__main__":
    pass