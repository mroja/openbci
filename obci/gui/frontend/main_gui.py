#!/usr/bin/env python3
#
# Author:
#      Łukasz Polak <l.polak@gmail.com>
#
"""This is main file for whole GUI part of OpenBCI - main window of whole
application, along with loading all needed modules GUIs"""

# We are using newer version of QVariant through our GUI, so we might as well
# set it here and let all hell loose on users of older versions of PyQT :)
import sys
from PyQt4 import QtCore, QtGui
import sip
sip.setapi('QVariant', 2)


class BCIMainWindow(QtGui.QMainWindow):

    """Main window of the BCI application - shows list of available plugins and
    enables configuration of them"""

    def __init__(self, parent=None):
        super(BCIMainWindow, self).__init__(parent)
        # Holds all modules classes
        self.modules = {}
        # TODO: main gui should be made in designer, and not in code here
        self.pluginsList = QtGui.QTreeWidget()
        self.pluginsList.setMaximumWidth(200)
        self.pluginsList.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.pluginsList.setHeaderLabels(["Nazwa"])
        for i_plugin in self.modules.values():
            l_item = QtGui.QTreeWidgetItem([i_plugin.name])
            l_item.plugin = i_plugin
            self.pluginsList.addTopLevelItem(l_item)
        self.pluginsList.setCurrentItem(None)
        self.connect(self.pluginsList, QtCore.SIGNAL(
            "currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)"), self.itemChanged)

        # Dictionary for configuration widgets of modules
        self.dockWidgets = {}
        self.currentDockWidget = None
        self.setCentralWidget(self.pluginsList)

    def itemChanged(self, p_newItem):
        """Called, when selection on lists of plugins changes. Then it displays
        configuration window for newly selected plugin, and closes old one,
        unless it's floating.
        p_newItem (QTreeWidgetItem) - contains newly selected plugin
        p_oldItem (QTreeWidgetItem) - contains plugin that was selected
        before"""
        if self.currentDockWidget is not None:
            # We remove widget only if it's not floating
            if not self.currentDockWidget.isFloating():
                self.removeDockWidget(self.currentDockWidget)
            else:
                self.currentDockWidget.setAllowedAreas(QtCore.Qt.NoDockWidgetArea)
            self.currentDockWidget = None

        if p_newItem is not None:
            l_pluginName = p_newItem.plugin.name
            # If we haven't configured this plugin yet, we need to create its GUI
            if l_pluginName not in self.dockWidgets:
                self.dockWidgets[l_pluginName] = p_newItem.plugin.buildGui(self)
                self.dockWidgets[l_pluginName].setMinimumWidth(500)
                self.dockWidgets[l_pluginName].setMinimumHeight(500)
            p_pluginDock = self.dockWidgets[l_pluginName]
            # We allow docking only on right side of window
            p_pluginDock.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
            # If dock was floating and closed before, we reset him into dock
            if not p_pluginDock.isVisible() and p_pluginDock.isFloating():
                p_pluginDock.setFloating(False)

            self.restoreDockWidget(p_pluginDock)
            self.currentDockWidget = p_pluginDock
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea, p_pluginDock)

if __name__ == "__main__":
    # We simply show main window
    APPLICATION = QtGui.QApplication(sys.argv)
    WINDOW = BCIMainWindow()
    WINDOW.show()
    sys.exit(APPLICATION.exec_())
