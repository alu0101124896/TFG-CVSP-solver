#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import sys

from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as
                                                FigureCanvas,
                                                NavigationToolbar2QT as
                                                NavToolbar)
import matplotlib.pyplot as plt
from matplotlib import use as mpl_use
from PyQt5 import QtCore, QtWidgets

from src.graph import Graph

mpl_use('Qt5Agg', force=True)

WIN_WIDTH = 650
WIN_HEIGHT = 630

FORMULATIONS = {
    "ortools": ["1", "2", "3", "4"],
    "gurobi": ["1", "2", "3", "3 lazy", "4", "4 lazy"],
}

FILENAME_LEN_THRESHOLD = 70


def main():
    """ Main window. """

    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = UiMainWindow()
    ui.setup_ui(main_window)

    main_window.show()
    sys.exit(app.exec_())


class UiMainWindow(object):
    """ Main app window class. """

    def __init__(self):
        self.central_widget = None
        self.grid_layout = None

        self.horizontal_layout_0 = None
        self.graph_file_label = None
        self.load_graph_button = None
        self.selected_file_label = None

        self.horizontal_layout_1 = None
        self.k_label = None
        self.k_value = None
        self.b_label = None
        self.b_value = None
        self.library_label = None
        self.library_selector = None
        self.formulation_label = None
        self.formulation_selector = None
        self.get_solution_button = None

        self.figure = None
        self.canvas = None
        self.tool_bar = None

        self.line_1 = None
        self.line_2 = None

        self.spacer_item_1 = None
        self.spacer_item_2 = None
        self.spacer_item_3 = None
        self.spacer_item_4 = None
        self.spacer_item_5 = None

        self.input_file = None
        self.graph = None

        self.available_formulations = FORMULATIONS
        self.available_libraries = FORMULATIONS.keys()

    def setup_ui(self, main_window):
        """ Function to initialize the window layout. """

        main_window.setObjectName("main_window")
        main_window.setWindowTitle("CVSP Solver")
        main_window.setFixedSize(WIN_WIDTH, WIN_HEIGHT)

        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        main_window.setCentralWidget(self.central_widget)

        self.grid_layout = QtWidgets.QGridLayout(self.central_widget)
        self.grid_layout.setObjectName("grid_layout")

        # ---------------------------------------------------------------------

        self.horizontal_layout_0 = QtWidgets.QHBoxLayout()
        self.horizontal_layout_0.setObjectName("horizontal_layout_0")
        self.grid_layout.addLayout(self.horizontal_layout_0, 0, 0)

        self.graph_file_label = QtWidgets.QLabel(self.central_widget)
        self.graph_file_label.setObjectName("graph_file_label")
        self.graph_file_label.setText("Graph file:")
        self.horizontal_layout_0.addWidget(self.graph_file_label)

        self.load_graph_button = QtWidgets.QPushButton(self.central_widget)
        self.load_graph_button.setObjectName("load_graph_button")
        self.load_graph_button.setText("Select file")
        self.horizontal_layout_0.addWidget(self.load_graph_button)

        self.selected_file_label = QtWidgets.QLabel(self.central_widget)
        self.selected_file_label.setObjectName("selected_file_label")
        self.selected_file_label.setText("No file selected")
        self.horizontal_layout_0.addWidget(self.selected_file_label)

        self.spacer_item_1 = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum,
        )
        self.horizontal_layout_0.addItem(self.spacer_item_1)

        # ---------------------------------------------------------------------

        self.line_1 = QtWidgets.QFrame(self.central_widget)
        self.line_1.setObjectName("line_1")
        self.line_1.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.grid_layout.addWidget(self.line_1, 1, 0)

        # ---------------------------------------------------------------------

        self.horizontal_layout_1 = QtWidgets.QHBoxLayout()
        self.horizontal_layout_1.setObjectName("horizontal_layout_1")
        self.grid_layout.addLayout(self.horizontal_layout_1, 2, 0)

        self.k_label = QtWidgets.QLabel(self.central_widget)
        self.k_label.setObjectName("k_label")
        self.k_label.setText("k value:")
        self.horizontal_layout_1.addWidget(self.k_label)

        self.k_value = QtWidgets.QSpinBox(self.central_widget)
        self.k_value.setObjectName("k_value")
        self.k_value.setValue(3)
        self.horizontal_layout_1.addWidget(self.k_value)

        self.b_label = QtWidgets.QLabel(self.central_widget)
        self.b_label.setObjectName("b_label")
        self.b_label.setText("b value:")
        self.horizontal_layout_1.addWidget(self.b_label)

        self.b_value = QtWidgets.QSpinBox(self.central_widget)
        self.b_value.setObjectName("b_value")
        self.b_value.setValue(3)
        self.horizontal_layout_1.addWidget(self.b_value)

        self.library_label = QtWidgets.QLabel(self.central_widget)
        self.library_label.setObjectName("library_label")
        self.library_label.setText("Library:")
        self.horizontal_layout_1.addWidget(self.library_label)

        self.library_selector = QtWidgets.QComboBox(self.central_widget)
        self.library_selector.setObjectName("library_selector")
        self.library_selector.addItems(self.available_libraries)
        self.horizontal_layout_1.addWidget(self.library_selector)

        self.formulation_label = QtWidgets.QLabel(self.central_widget)
        self.formulation_label.setObjectName("formulation_label")
        self.formulation_label.setText("Formulation:")
        self.horizontal_layout_1.addWidget(self.formulation_label)

        self.formulation_selector = QtWidgets.QComboBox(self.central_widget)
        self.formulation_selector.setObjectName("formulation_selector")
        self.formulation_selector.addItems(
            list(self.available_formulations.values())[0])
        self.formulation_selector.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToContents)
        self.horizontal_layout_1.addWidget(self.formulation_selector)

        self.spacer_item_5 = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum,
        )
        self.horizontal_layout_1.addItem(self.spacer_item_5)

        self.get_solution_button = QtWidgets.QPushButton(self.central_widget)
        self.get_solution_button.setObjectName("get_solution_button")
        self.get_solution_button.setText("Get Solution")
        self.horizontal_layout_1.addWidget(self.get_solution_button)

        # ---------------------------------------------------------------------

        self.line_2 = QtWidgets.QFrame(self.central_widget)
        self.line_2.setObjectName("line_2")
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.grid_layout.addWidget(self.line_2, 3, 0)

        # ---------------------------------------------------------------------

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.grid_layout.addWidget(self.canvas, 4, 0)

        self.tool_bar = NavToolbar(self.canvas, self.central_widget)
        self.grid_layout.addWidget(self.tool_bar, 5, 0)

        # ---------------------------------------------------------------------

        self.load_graph_button.clicked.connect(self.load_graph)
        self.get_solution_button.clicked.connect(self.get_solution)
        self.library_selector.currentIndexChanged["QString"].connect(
            self.update_formulation_selector)

        QtCore.QMetaObject.connectSlotsByName(main_window)

    def load_graph(self):
        """ Function to show a file selection window. """

        input_file, check = QtWidgets.QFileDialog.getOpenFileName(
            None, "Select graph file", "", "All Files (*)")

        if check:
            self.set_input_file(input_file)
            self.graph = Graph(self.input_file)
            self.show_graph()

    def set_input_file(self, input_file: str):
        """ Function to set a new input file path. """

        self.input_file = Path(input_file)

        if len(input_file) > FILENAME_LEN_THRESHOLD:
            ipf_str = "..." + input_file[-FILENAME_LEN_THRESHOLD:]
        else:
            ipf_str = input_file

        self.selected_file_label.setText(ipf_str)

    def update_formulation_selector(self, library_name: str):
        """ Function to update the available formulations for the selected
        library. """

        self.formulation_selector.clear()
        self.formulation_selector.addItems(
            self.available_formulations[library_name])

    def get_solution(self):
        """ Function to get the solution to the CVSP problem. """

        if self.graph is not None:
            self.graph.solve_cvsp(
                self.library_selector.currentText(),
                self.formulation_selector.currentIndex(),
                self.k_value.value(),
                self.b_value.value(),
            )

            self.show_graph()

    def show_graph(self):
        """ Function to show the loaded graph. """

        if self.graph is not None:
            self.figure.clf()
            self.graph.show()
            self.canvas.draw_idle()


if __name__ == "__main__":
    main()
