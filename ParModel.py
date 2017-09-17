from PyQt5 import QtCore

class ParModel(QtCore.QAbstractTableModel):
    """
    Table model for broadcasted parameters.
    """
    def __init__(self, parent=None):
        """
        Args:
            parent (QtGui.QWidget): parent widget
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.parent = parent
        self.parList = []
        self.valList = []
        self.checkList = []
        self.settingsRead = False

        
    def rowCount(self, parent=QtCore.QModelIndex()):
        """"See QtCore.QAbstractItemModel."""
        return len(self.parList)

        
    def columnCount(self, parent=QtCore.QModelIndex()):
        """"See QtCore.QAbstractItemModel."""
        return 2

        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        """"See QtCore.QAbstractItemModel."""
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                if index.column() == 0:
                    return self.parList[index.row()]
                elif index.column() == 1:
                    return self.valList[index.row()]
            if role == QtCore.Qt.CheckStateRole:
                if index.column() == 0:
                    return self.checkList[index.row()]

                    
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """"See QtCore.QAbstractItemModel."""
        if index.isValid():
            if role == QtCore.Qt.CheckStateRole:
                self.checkList[index.row()] = value
                self.writeSettings()
                return True
        return False

                    
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """"See QtCore.QAbstractItemModel."""
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section == 0:
                    return 'parameter'
                elif section == 1:
                    return 'value'
            else:
                return section

                
    def flags(self, index):
        """"See QtCore.QAbstractItemModel."""
        if index.column() == 0:
            return QtCore.Qt.ItemFlags(QtCore.Qt.ItemIsEnabled |
                                       QtCore.Qt.ItemIsUserCheckable)
        else:
            return QtCore.Qt.ItemFlags(QtCore.Qt.ItemIsEnabled)

            
    def writeSettings(self):
        """Save frame configuration."""
        settings = self.parent.settings
        settings.beginGroup('FRAME_CONFIG')
        for i, par in enumerate(self.parList):
            settings.setValue(par, self.checkList[i]/2)
        settings.endGroup()

        
    def readSettings(self):
        """Read frame configuration."""
        settings = self.parent.settings
        settings.beginGroup('FRAME_CONFIG')
        for i, par in enumerate(self.parList):
            self.checkList[i] = 2*int(settings.value(par, 0))
        settings.endGroup()

            
    def updateData(self, parList, valList):
        """Update table model data."""
        self.parList = parList
        self.valList = valList
        while len(self.checkList) < len(self.parList):
            self.checkList.append(0)
        if not self.settingsRead:
            self.settingsRead = True
            self.readSettings()
        self.modelReset.emit()
