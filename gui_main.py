#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: gui_main.py
Author: Sergio Tabares Hernández <alu0101124896@ull.edu.es>
Since: Summer 2022
College: University of La Laguna
Degree: Computer Science - Bachelor's Degree Final Project
Description: This program implements a Graphical User Interface (GUI) to solve
 the Capacitated Vertex Separator Problem (CVSP) on a graph through various
 formulations using integer optimization approaches.
"""

import sys

from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as
                                                FigureCanvas,
                                                NavigationToolbar2QT as
                                                NavToolbar)
import matplotlib.pyplot as plt
import networkx as nx
from PyQt5 import QtCore, QtWidgets

try:
    from .src.graph import Graph
except ImportError:
    from src.graph import Graph

QUIET = False

WIN_WIDTH = 650
WIN_HEIGHT = 630

FORMULATIONS = {
    "ortools": [
        "1",
        "2",
        "3",
        "4",
    ],
    "gurobi": [
        "1",
        "1 alt b",
        "1 alt c",
        "2",
        "3",
        "3 lazy",
        "4",
        "4 lazy",
    ],
}

GRAPH_FILENAME_LEN_THRESHOLD = 70
SOLUTION_FILENAME_LEN_THRESHOLD = 64


def main():
    """ Entry point for the main gui program. """

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
        self.selected_graph_file_label = None

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

        self.horizontal_layout_2 = None
        self.save_solution_button = None
        self.load_solution_button = None
        self.selected_solution_file_label = None

        self.figure = None
        self.canvas = None

        self.horizontal_layout_3 = None
        self.status_label = None
        self.tool_bar = None

        self.line_1 = None
        self.line_2 = None

        self.spacer_item_1 = None
        self.spacer_item_2 = None
        self.spacer_item_3 = None
        self.spacer_item_4 = None

        self.graph_file = None
        self.graph = None

        self.solution_file = None

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

        self.selected_graph_file_label = QtWidgets.QLabel(self.central_widget)
        self.selected_graph_file_label.setObjectName(
            "selected_graph_file_label")
        self.selected_graph_file_label.setText("No file selected")
        self.horizontal_layout_0.addWidget(self.selected_graph_file_label)

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
        self.k_value.setRange(2, 999)
        self.k_value.setValue(3)
        self.horizontal_layout_1.addWidget(self.k_value)

        self.b_label = QtWidgets.QLabel(self.central_widget)
        self.b_label.setObjectName("b_label")
        self.b_label.setText("b value:")
        self.horizontal_layout_1.addWidget(self.b_label)

        self.b_value = QtWidgets.QSpinBox(self.central_widget)
        self.b_value.setObjectName("b_value")
        self.b_value.setRange(1, 999)
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

        self.spacer_item_2 = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum,
        )
        self.horizontal_layout_1.addItem(self.spacer_item_2)

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

        self.horizontal_layout_2 = QtWidgets.QHBoxLayout()
        self.horizontal_layout_2.setObjectName("horizontal_layout_2")
        self.grid_layout.addLayout(self.horizontal_layout_2, 4, 0)

        self.save_solution_button = QtWidgets.QPushButton(self.central_widget)
        self.save_solution_button.setObjectName("save_solution_button")
        self.save_solution_button.setText("Save solution")
        self.horizontal_layout_2.addWidget(self.save_solution_button)

        self.load_solution_button = QtWidgets.QPushButton(self.central_widget)
        self.load_solution_button.setObjectName("load_solution_button")
        self.load_solution_button.setText("Load solution")
        self.horizontal_layout_2.addWidget(self.load_solution_button)

        self.selected_solution_file_label = QtWidgets.QLabel(
            self.central_widget)
        self.selected_solution_file_label.setObjectName(
            "selected_solution_file_label")
        self.selected_solution_file_label.setText("No file selected")
        self.horizontal_layout_2.addWidget(self.selected_solution_file_label)

        self.spacer_item_3 = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum,
        )
        self.horizontal_layout_2.addItem(self.spacer_item_3)

        # ---------------------------------------------------------------------

        self.line_2 = QtWidgets.QFrame(self.central_widget)
        self.line_2.setObjectName("line_2")
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.grid_layout.addWidget(self.line_2, 5, 0)

        # ---------------------------------------------------------------------

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.grid_layout.addWidget(self.canvas, 6, 0)

        # ---------------------------------------------------------------------

        self.horizontal_layout_3 = QtWidgets.QHBoxLayout()
        self.horizontal_layout_3.setObjectName("horizontal_layout_3")
        self.grid_layout.addLayout(self.horizontal_layout_3, 7, 0)

        self.status_label = QtWidgets.QLabel(self.central_widget)
        self.status_label.setObjectName("status_label")
        self.status_label.setText("")
        self.horizontal_layout_3.addWidget(self.status_label)

        self.spacer_item_4 = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum,
        )
        self.horizontal_layout_3.addItem(self.spacer_item_4)

        self.tool_bar = NavToolbar(self.canvas,
                                   self.central_widget,
                                   coordinates=False)
        self.tool_bar.setFixedWidth(300)
        self.horizontal_layout_3.addWidget(self.tool_bar)

        # ---------------------------------------------------------------------

        self.load_graph_button.clicked.connect(self.load_graph)
        self.get_solution_button.clicked.connect(self.get_solution)
        self.save_solution_button.clicked.connect(self.save_solution)
        self.load_solution_button.clicked.connect(self.load_solution)

        self.library_selector.currentIndexChanged["QString"].connect(
            self.update_formulation_selector)

        QtCore.QMetaObject.connectSlotsByName(main_window)

    def load_graph(self):
        """ Function to show a file selection window. """

        self.status_label.setText("Loading graph...")

        graph_file, check = QtWidgets.QFileDialog.getOpenFileName(
            None, "Select a graph file", "", "All Files (*)")

        if not check:
            self.status_label.setText("Graph not loaded.")

        else:
            try:
                self.set_graph_file(graph_file)
                self.graph = Graph(self.graph_file)
                self.show_graph()

                self.status_label.setText("Done.")

            except ValueError:
                self.status_label.setText(
                    "Error: The graph file is not valid."
                )

    def set_graph_file(self, graph_file: str):
        """ Function to set a new graph file path. """

        self.graph_file = graph_file

        if len(graph_file) > GRAPH_FILENAME_LEN_THRESHOLD:
            file_str = "..." + graph_file[-GRAPH_FILENAME_LEN_THRESHOLD:]
        else:
            file_str = graph_file

        self.selected_graph_file_label.setText(file_str)

    def update_formulation_selector(self, library_name: str):
        """ Function to update the available formulations for the selected
        library. """

        self.formulation_selector.clear()
        self.formulation_selector.addItems(
            self.available_formulations[library_name])

    def get_solution(self):
        """ Function to get the solution to the CVSP problem. """

        self.graph.cvsp_solution = None
        self.solution_file = None
        self.selected_solution_file_label.setText("No file selected")

        if self.graph is None:
            self.status_label.setText("Please, load a graph first.")

        else:
            self.status_label.setText("Loading solution...")
            self.status_label.resize(200, 40)
            self.status_label.repaint()

            self.graph.solve_cvsp(
                self.library_selector.currentText(),
                self.formulation_selector.currentIndex(),
                self.k_value.value(),
                self.b_value.value(),
                QUIET,
            )

            self.show_graph()

            if self.graph.cvsp_solution is None:
                self.status_label.setText("Solution not found.")
            else:
                self.status_label.setText("Done.")

    def save_solution(self):
        """ Function to save the current solution to a file. """

        if self.graph is None:
            self.status_label.setText(
                "Please, load a graph and get a solution first.")

        elif self.graph.cvsp_solution is None:
            self.status_label.setText("Please, get a solution first.")

        else:
            self.status_label.setText("Saving solution...")

            solution_file, check = QtWidgets.QFileDialog.getSaveFileName(
                None, "Select a destination file", "", "All Files (*)")

            if not check:
                self.status_label.setText("Solution file not saved.")

            else:
                self.set_solution_file(solution_file)
                self.graph.export_solution(self.solution_file)

                self.status_label.setText("Done.")

    def load_solution(self):
        """ Function to load a saved solution from a file. """

        if self.graph is None:
            self.status_label.setText("Please, load a graph first.")

        else:
            self.status_label.setText("Loading solution...")

            solution_file, check = QtWidgets.QFileDialog.getOpenFileName(
                None, "Select a solution file", "", "All Files (*)")

            if not check:
                self.status_label.setText("Solution file not loaded.")

            else:
                try:
                    self.set_solution_file(solution_file)
                    self.graph.load_solution(self.solution_file)
                    self.show_graph()

                    self.status_label.setText("Done.")

                except nx.exception.NetworkXError:
                    self.status_label.setText(
                        "Error: The solution file is not valid for this graph."
                    )

    def set_solution_file(self, solution_file: str):
        """ Function to set a new input file path. """

        self.solution_file = solution_file

        if len(solution_file) > SOLUTION_FILENAME_LEN_THRESHOLD:
            file_str = "..." + solution_file[-SOLUTION_FILENAME_LEN_THRESHOLD:]
        else:
            file_str = solution_file

        self.selected_solution_file_label.setText(file_str)

    def show_graph(self):
        """ Function to show the loaded graph. """

        if self.graph is not None:
            self.figure.clf()
            self.graph.show()
            self.canvas.draw_idle()


if __name__ == "__main__":
    main()
