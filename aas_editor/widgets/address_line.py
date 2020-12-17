from typing import List

from PyQt5.QtCore import QModelIndex, Qt, QAbstractProxyModel, qDebug, \
    qCritical, pyqtSignal, QObject, QAbstractItemModel
from PyQt5.QtWidgets import QMessageBox, QCompleter, QLineEdit, QStyledItemDelegate

from aas_editor.models import StandardTable
from aas_editor.utils.util import getTreeItemPath

COMPLETION_ROLE = Qt.DisplayRole
CASE_SENSITIVITY = Qt.CaseInsensitive


class Signal(QObject):
    modelChanged = pyqtSignal(['QAbstractItemModel'])


# class AddressBar(QWidget):
#     def __init__(self, parent: 'Tab' = None) -> None:
#         super(AddressBar, self).__init__(parent=parent)
#         self.tab = parent
#         self.currItem = QModelIndex()
#         self.prevItems = []
#         self.nextItems = []
#         self.initButtons()
#         self.addressLine = AddressLine(self, tab=self.tab)
#         self.initLayout()
#
#     # noinspection PyArgumentList
#     def initButtons(self):
#         self.backBtn = QToolButton(self, icon=BACK_ICON, toolTip="Go back one item",
#                                    triggered=self.openPrevItem,
#                                    statusTip="Go back one item",
#                                    shortcut=SC_BACK,
#                                    enabled=True)
#
#         self.forwardBtn = QToolButton(self, icon=FORWARD_ICON, toolTip="Go forward one item",
#                                    triggered=self.openNextItem,
#                                    statusTip="Go forward one item",
#                                    shortcut=SC_FORWARD,
#                                    enabled=True)
#
#     def openPrevItem(self):
#         if self.prevItems:
#             prevItem = self.prevItems.pop()
#             self.nextItems.append(self.packItem)
#             self.addressLine.open(QModelIndex(prevItem))
#
#     def openNextItem(self):
#         if self.nextItems:
#             nextItem = self.nextItems.pop()
#             self.prevItems.append(self.packItem)
#             self.addressLine.open(QModelIndex(nextItem))
#
#     def open(self, index: QModelIndex):
#         model: QAbstractProxyModel = index.model()
#         if not index == QModelIndex(self.currItem) and model and index.isValid():
#             qDebug(f"Open address: {self.text()}")
#             self.nextItems.clear()
#             if self.packItem.isValid():
#                 self.prevItems.append(self.packItem)
#             index = model.mapToSource(index)
#             self.tab._openItem(index)
#             self.currItem = QPersistentModelIndex(index)
#         else:
#             qCritical(f"Index was not found for address {self.text()}")
#             QMessageBox.critical(self, "Error", f"Item not found: {self.text()}")
#
#     def text(self):
#         return self.addressLine.text()
#
#     def initLayout(self):
#         pathLayout = QHBoxLayout(self)
#         pathLayout.setContentsMargins(0, 0, 0, 0)
#         pathLayout.setSpacing(0)
#         pathLayout.addWidget(self.backBtn)
#         pathLayout.addWidget(self.forwardBtn)
#         pathLayout.addWidget(self.addressLine)


class AddressLine(QLineEdit):
    """Class for address line used in tabs"""
    signal = Signal()
    _model: StandardTable = None

    def __init__(self, parent: 'Tab') -> None:
        super(AddressLine, self).__init__(parent)
        self.tab = parent

        self.setCompleter(AddressLineCompleter(self))
        self.completer().setCompletionRole(COMPLETION_ROLE)
        self.completer().setCaseSensitivity(CASE_SENSITIVITY)
        if AddressLine._model:
            self.completer().setModel(AddressLine._model)
            self.completer().activated[QModelIndex].connect(self.onReturnPressed)
            self.returnPressed.connect(self.onReturnPressed)
        AddressLine.signal.modelChanged.connect(self.onModelChanged)

    @classmethod
    def setModel(cls, model: StandardTable):
        cls._model = model
        cls.signal.modelChanged.emit(model)
        qDebug("New model for address completer was set")

    def onModelChanged(self):
        self.completer().setModel(AddressLine._model)
        self.returnPressed.connect(self.onReturnPressed)

    def open(self, index: QModelIndex):
        model: QAbstractProxyModel = index.model()
        if model and index.isValid():
            qDebug(f"Open address: {self.text()}")
            index = model.mapToSource(index)
            self.tab.openItem(index)
        else:
            qCritical(f"Index was not found for address {self.text()}")
            QMessageBox.critical(self, "Error", f"Item not found: {self.text()}")

    def onReturnPressed(self):
        self.completer().setCompletionPrefix(self.text().rstrip("/"))
        if self.completer().currentCompletion() == self.text():
            index = self.completer().currentIndex()
            self.open(index)
        else:
            QMessageBox.critical(self, "Error", f"Item not found: {self.text()}")


class AddressLineCompleter(QCompleter):
    mCompleterItemDelegate = QStyledItemDelegate()

    def pathFromIndex(self, index: QModelIndex) -> str:
        return getTreeItemPath(index, role=self.completionRole())

    def splitPath(self, path: str) -> List[str]:
        return path.split("/")

    def setModel(self, c: QAbstractItemModel) -> None:
        super(AddressLineCompleter, self).setModel(c)
        self.popup().setItemDelegate(self.mCompleterItemDelegate)
