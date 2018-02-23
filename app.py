#! /usr/bin/python3
# coding: utf-8


"""GUI for Finite Elements Method."""


__author__ = "Ewen BRUN, Pierre HAON"
__email__ = "ewen.brun@ecam.fr"


import ast
import models
import xlsxwriter
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QProgressDialog, QFileDialog, QMessageBox
from sqlalchemy import text
from db.fem import Materials, Sections
from matplotlib import pyplot as plt


def listModels(models=models):
    """List models."""
    with open(models.__file__, 'r') as source:
        p = ast.parse(source.read())
    return [node.name for node in ast.walk(p) if isinstance(node, ast.ClassDef) and node.name != "Model"]


qtCreatorFile = "ui/mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class App(QMainWindow, Ui_MainWindow):
    """Mainwindow."""

    def __init__(self):
        """Init."""
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.horizontalSliderElements.setVisible(False)
        self.lineEditElements.setVisible(False)
        self.lineEditElements.setText("128")
        self.listWidget.addItems(listModels())
        self.model = models.Model()
        self.loadMaterials()
        self.loadSections()
        self.loadSectionImage()

        self.dockWidget.topLevelChanged.connect(self.updateWindowSize)
        self.listWidget.currentTextChanged.connect(self.modelChanged)
        self.tabwidget.Tabs.currentChanged.connect(self.typeChanged)
        self.comboBoxMaterials.currentTextChanged.connect(self.materialChanged)
        self.comboBoxSections.currentTextChanged.connect(self.sectionChanged)
        self.horizontalSliderElements.valueChanged.connect(self.elementsNumberChanged)
        self.pushButtonStartComputation.clicked.connect(self.compute)
        self.pushButtonSave.clicked.connect(self.saveFigure)
        self.pushButtonExcel.clicked.connect(self.saveExcel)
        self.pushButtonPlotMatrix.clicked.connect(self.plotMatrix)

    def updateWindowSize(self, onTop):
        """Update window size if dockWidget is on Top."""
        if onTop:
            self.resize(self.minimumSize())
        else:
            self.resize(self.maximumSize())

    def modelChanged(self):
        """Change model on selection."""
        self.labelSelectModel.setHidden(True)
        self.pushButtonPlotMatrix.setEnabled(True)
        self.groupBoxConditions.setEnabled(True)
        self.groupBoxElements.setEnabled(True)
        self.groupBoxComputation.setEnabled(True)
        self.labelStatus1.setText("✅")
        self.model = eval(
            "models." + self.listWidget.currentItem().text() + '()')
        self.tabwidget.addTabFromList(self.model.types)

    def materialChanged(self):
        """Change material on selection."""
        self.model.material = self.model.session.query(Materials).filter(
            Materials.Name == self.comboBoxMaterials.currentText()).first()

    def sectionChanged(self):
        """Change section on selection."""
        self.model.section = self.model.session.query(Sections).filter(
            Sections.Name == self.comboBoxSections.currentText()).first()
        self.loadSectionImage()

    def loadMaterials(self):
        """Load materials from db."""
        self.comboBoxMaterials.addItems(
            [i[0] for i in self.model.session.execute(text('select Name from Materials'))])

    def loadSections(self):
        """Load scetion names from db."""
        self.comboBoxSections.addItems(
            [i[0] for i in self.model.session.execute(text('select Name from Sections'))])

    def loadSectionImage(self):
        """Load image corresponding to section from db."""
        p = QPixmap()
        p.loadFromData(self.model.section.raw_Image)
        p = p.scaled(32, 32)
        self.labelSectionImage.setPixmap(p)
        self.labelSectionImage.resize(p.width(), p.height())
        self.labelSectionImage.show()

    def plotMatrix(self):
        """Plot rigidity matrix."""
        plt.matshow(self.model.K())
        plt.show()

    def typeChanged(self):
        """Change type of study."""
        if self.tabwidget.Tabs.currentIndex() != -1:
            self.model.elems(int(self.lineEditElements.text()))
            self.model.solve(self.tabwidget.Tabs.currentIndex())
            self.mpl.canvas.graph(self.model)

    def elementsNumberChanged(self):
        """Change in number of elements."""
        self.lineEditElements.setText(
            str(int(2**(self.horizontalSliderElements.value()))))
        print(self.lineEditElements.text())

    def saveFigure(self):
        """Save figure."""
        try:
            name = QFileDialog.getSaveFileName(self, 'Save File')
            if name[0] != "":
                self.mpl.canvas.fig.savefig(name[0], dpi=300)
        except BaseException:
            QMessageBox.warning(self, 'Avertissement',
                                'Le fichier n\'as pas pu etre enregistré')

    def saveExcel(self):
        """Save data under excel file."""
        try:
            name = QFileDialog.getSaveFileName(self, 'Save File')[0]
            if name != "":
                if '.xlsx' not in name:
                    name += '.xlsx'
                wk = xlsxwriter.Workbook(name)
                ws = wk.add_worksheet()
                wk.close()
        except BaseException:
            QMessageBox.warning(self, 'Avertissement',
                                'Le fichier n\'as pas pu etre enregistré')

    def compute(self):
        """Compute."""
        diag = QProgressDialog(self)
        diag.setRange(0, 0)
        diag.setValue(0)
        diag.setModal(True)
        diag.setWindowTitle("Calcul en cours")
        diag.setLabelText("Resolution en cours...")
        diag.show()
        self.model.elems(self.horizontalSliderElements.value())
        diag.show()
        QApplication.processEvents()
        self.model.solve()
        diag.reset()
        self.typeChanged()
