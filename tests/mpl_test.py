#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg,
                                                NavigationToolbar2QT as Navi)
from matplotlib.figure import Figure
import pandas as pd
import sip  # can be installed : pip install sip


def main():
    """ Main window. """

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UiMainWindow()
    ui.setup_ui(MainWindow)

    MainWindow.show()
    sys.exit(app.exec_())


class MatplotlibCanvas(FigureCanvasQTAgg):
    """ Matplotlib canvas class. """
    def __init__(self, parent=None, dpi=120):
        fig = Figure(dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MatplotlibCanvas, self).__init__(fig)
        fig.tight_layout()


class UiMainWindow(object):
    """ Main app window class. """
    def __init__(self):
        pass

    def setup_ui(self, main_window):
        """ Function to initialize the window layout. """

        main_window.setObjectName("MainWindow")
        main_window.resize(800, 800)

        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        main_window.setCentralWidget(self.central_widget)

        self.grid_layout = QtWidgets.QGridLayout(self.central_widget)
        self.grid_layout.setObjectName("gridLayout")

        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.horizontal_layout.setObjectName("horizontalLayout")
        self.grid_layout.addLayout(self.horizontal_layout, 0, 0, 1, 1)

        self.label = QtWidgets.QLabel(self.central_widget)
        self.label.setObjectName("label")
        self.horizontal_layout.addWidget(self.label)

        self.combo_box = QtWidgets.QComboBox(self.central_widget)
        self.combo_box.setObjectName("comboBox")
        self.horizontal_layout.addWidget(self.combo_box)

        self.push_button = QtWidgets.QPushButton(self.central_widget)
        self.push_button.setObjectName("pushButton")
        self.horizontal_layout.addWidget(self.push_button)

        self.spacer_item_1 = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum,
        )
        self.horizontal_layout.addItem(self.spacer_item_1)

        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.vertical_layout.setObjectName("verticalLayout")
        self.grid_layout.addLayout(self.vertical_layout, 1, 0, 1, 1)

        self.spacer_item_2 = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding,
        )
        self.vertical_layout.addItem(self.spacer_item_2)

        self.menu_bar = QtWidgets.QMenuBar(main_window)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menu_bar.setObjectName("menubar")
        main_window.setMenuBar(self.menu_bar)

        self.menu_file = QtWidgets.QMenu(self.menu_bar)
        self.menu_file.setObjectName("menuFile")

        self.status_bar = QtWidgets.QStatusBar(main_window)
        self.status_bar.setObjectName("statusbar")
        main_window.setStatusBar(self.status_bar)

        self.actionOpen_csv_file = QtWidgets.QAction(main_window)
        self.actionOpen_csv_file.setObjectName("actionOpen_csv_file")
        self.actionExit = QtWidgets.QAction(main_window)
        self.actionExit.setObjectName("actionExit")

        self.menu_file.addAction(self.actionOpen_csv_file)
        self.menu_file.addAction(self.actionExit)
        self.menu_bar.addAction(self.menu_file.menuAction())

        self.retranslate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

        self.filename = ''
        self.canv = MatplotlibCanvas(self)
        self.df = []

        self.toolbar = Navi(self.canv, self.central_widget)
        self.horizontal_layout.addWidget(self.toolbar)

        self.themes = [
            'bmh', 'classic', 'dark_background', 'fast', 'fivethirtyeight',
            'ggplot', 'grayscale', 'seaborn-bright', 'seaborn-colorblind',
            'seaborn-dark-palette', 'seaborn-dark', 'seaborn-darkgrid',
            'seaborn-deep', 'seaborn-muted', 'seaborn-notebook',
            'seaborn-paper', 'seaborn-pastel', 'seaborn-poster',
            'seaborn-talk', 'seaborn-ticks', 'seaborn-white',
            'seaborn-whitegrid', 'seaborn', 'Solarize_Light2',
            'tableau-colorblind10'
        ]
        self.combo_box.addItems(self.themes)

        self.push_button.clicked.connect(self.get_file)
        self.combo_box.currentIndexChanged['QString'].connect(self.update)
        self.actionExit.triggered.connect(main_window.close)
        self.actionOpen_csv_file.triggered.connect(self.get_file)

    def update(self, value):
        """update"""
        print("Value from Combo Box:", value)
        plt.clf()
        plt.style.use(value)

        try:
            self.horizontal_layout.removeWidget(self.toolbar)
            self.vertical_layout.removeWidget(self.canv)

            sip.delete(self.toolbar)
            sip.delete(self.canv)
            self.toolbar = None
            self.canv = None

            self.vertical_layout.removeItem(self.spacer_item_2)

        except Exception as err:
            print(err)
            pass

        self.canv = MatplotlibCanvas(self)
        self.toolbar = Navi(self.canv, self.central_widget)

        self.horizontal_layout.addWidget(self.toolbar)
        self.vertical_layout.addWidget(self.canv)

        self.canv.axes.cla()
        ax = self.canv.axes
        self.df.plot(ax=self.canv.axes)
        legend = ax.legend()
        legend.set_draggable(True)

        ax.set_xlabel('X axis')
        ax.set_ylabel('Y axis')
        ax.set_title(self.Title)

        self.canv.draw()

    def get_file(self):
        """ This function will get the address of the csv file location
			also calls a readData function
		"""
        self.filename = QtWidgets.QFileDialog.getOpenFileName(
            filter="csv (*.csv)")[0]
        print("File :", self.filename)
        self.read_data()

    def read_data(self):
        """ This function will read the data using pandas and call the update
			function to plot
		"""
        import os
        base_name = os.path.basename(self.filename)
        self.Title = os.path.splitext(base_name)[0]
        print('FILE', self.Title)
        self.df = pd.read_csv(self.filename, encoding='utf-8').fillna(0)
        self.update(self.themes[0])  # lets 0th theme be the default : bmh

    def retranslate_ui(self, MainWindow):
        """translate"""
        _translate = QtCore.QCoreApplication.translate

        MainWindow.setWindowTitle(
            _translate("MainWindow", "PyShine simple plot"))
        self.label.setText(_translate("MainWindow", "Select Theme"))
        self.push_button.setText(_translate("MainWindow", "Open"))
        self.menu_file.setTitle(_translate("MainWindow", "File"))
        self.actionOpen_csv_file.setText(
            _translate("MainWindow", "Open csv file"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))


# Subscribe to PyShine Youtube channel for more detail!

# WEBSITE: www.pyshine.com

if __name__ == "__main__":
    main()
