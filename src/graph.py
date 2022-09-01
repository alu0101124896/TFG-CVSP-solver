#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: graph.py
Author: Sergio Tabares Hernández <alu0101124896@ull.edu.es>
Since: Summer 2022
College: University of La Laguna
Degree: Computer Science - Bachelor's Degree Final Project
Description: This program provides the implementation of the Graph class used
 to represent a loaded graph from a file containing it's definition and to
 provide an interface to solve the Capacitated Vertex Separator Problem (CVSP).
"""

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import networkx as nx

from .cvsp import cvsp_solver

EXTRACTED_NODES_COLOR = "silver"
EXTRACTED_SHORES_LINE_WIDTH = 1.0
EXTRACTED_NODES_LINE_STYLE = "dashed"

REMAINING_SHORES_COLORS = plt.rcParams['axes.prop_cycle'].by_key()['color']
REMAINING_SHORES_LINE_WIDTH = 1.5
REMAINING_NODES_LINE_STYLE = "solid"


class Graph:
    """ Class to represent a NetworkX Graph. """

    def __init__(self, input_file: str = None):
        if input_file is None:
            self.is_directed = False

            self.n_nodes = 50
            self.n_edges = 100
            self.nx_graph = nx.gnm_random_graph(self.n_nodes,
                                                self.n_edges,
                                                directed=self.is_directed)

            # self.nx_graph = nx.grid_2d_graph(20, 20)
            # self.n_nodes = self.nx_graph.number_of_nodes()
            # self.n_edges = self.nx_graph.number_of_edges()

            self.edges_data = self.nx_graph.edges()

        else:
            self.build_graph(input_file)

        self.cvsp_solution = None
        self.layout = nx.drawing.layout.kamada_kawai_layout(self.nx_graph)

    def build_graph(self, input_file: str):
        """ Function to build a graph from the given data. """

        with open(Path(input_file), 'r', encoding="utf-8-sig") as file:
            raw_data = file.read()
            self.parse_graph_data(raw_data)

            if self.is_directed:
                self.nx_graph = nx.DiGraph(self.edges_data)
            else:
                self.nx_graph = nx.Graph(self.edges_data)

            if self.nx_graph.number_of_nodes() != self.n_nodes:
                sys.exit("Error: The graph's number of nodes is not the same" +
                         " as on the data file.")

            if self.nx_graph.number_of_edges() != self.n_edges:
                sys.exit("Error: The graph's number of edges is not the same" +
                         " as on the data file.")

    def parse_graph_data(self, raw_data: str):
        """ Function to parse a file's data into a list of edges """

        main_data, *edges_raw_data = raw_data.split("\n")

        n_nodes, n_edges, is_directed = main_data.split(', ')
        self.n_nodes = int(n_nodes)
        self.n_edges = int(n_edges)
        self.is_directed = bool(int(is_directed))

        if edges_raw_data[-1] == '':
            edges_raw_data.pop()

        self.edges_data = [
            tuple(edge_raw_data.split(', '))
            for edge_raw_data in edges_raw_data
        ]

    def solve_cvsp(self, library_name: str, formulation_index: int,
                   k_value: int, b_value: int, quiet: bool):
        """ Function to solve the cvsp problem for the loaded graph. """

        self.cvsp_solution = cvsp_solver(
            self.nx_graph,
            library_name,
            formulation_index,
            k_value,
            b_value,
            quiet,
        )

    def show(self):
        """ Function to show the graph on the gui. """

        if self.cvsp_solution is None:
            nx.draw_networkx(self.nx_graph,
                             self.layout,
                             node_color=REMAINING_SHORES_COLORS[9])
            return

        if isinstance(self.cvsp_solution, list):
            nx.draw_networkx(self.nx_graph,
                             self.layout,
                             nodelist=self.cvsp_solution,
                             edgelist=self.nx_graph.edges(self.cvsp_solution),
                             node_color=EXTRACTED_NODES_COLOR,
                             width=EXTRACTED_SHORES_LINE_WIDTH,
                             style=EXTRACTED_NODES_LINE_STYLE)

            graph_copy = self.nx_graph.copy()
            for node in self.cvsp_solution:
                graph_copy.remove_node(node)

            ccc_nodes = [
                graph_copy.subgraph(cc).copy()
                for cc in nx.connected_components(graph_copy)
            ]
            ccc_edges = [graph_copy.subgraph(cc).edges() for cc in ccc_nodes]

            for cc_nodes, cc_edges, color in zip(ccc_nodes, ccc_edges,
                                                 REMAINING_SHORES_COLORS):
                nx.draw_networkx(graph_copy,
                                 self.layout,
                                 nodelist=cc_nodes,
                                 edgelist=cc_edges,
                                 node_color=color,
                                 width=REMAINING_SHORES_LINE_WIDTH,
                                 style=REMAINING_NODES_LINE_STYLE)

        else:
            sys.exit("Error: unknown solution format")

    def export_definition(self, output_file):
        """ Function to export the current graph definition to a file. """

        with open(Path(output_file), 'w', encoding="utf-8-sig") as outfile:
            print(self.n_nodes,
                  self.n_edges,
                  1 if self.is_directed else 0,
                  sep=", ",
                  file=outfile)
            for edge in self.edges_data:
                print(*edge, sep=", ", file=outfile)

    def export_solution(self, output_file):
        """ Function to export the solution to a file. """

        with open(Path(output_file), 'w', encoding="utf-8-sig") as outfile:
            print(*self.cvsp_solution, sep=", ", file=outfile)

    def load_solution(self, input_file):
        """ Function to export the solution to a file. """

        with open(Path(input_file), 'r', encoding="utf-8-sig") as infile:
            raw_data = infile.read()
            solution_nodes = raw_data.split("\n")[0].split(", ")
            self.cvsp_solution = solution_nodes

    def print_solution(self):
        """ Function to print the solution into the terminal in a more
        comprehensive way. """

        print("\nSolution:")

        if isinstance(self.cvsp_solution, dict):
            print(f"  S: {self.cvsp_solution['S']}")
            print("  V: [")
            for shore in self.cvsp_solution['V']:
                print(f"    {shore},")
            print("  ]")

        elif isinstance(self.cvsp_solution, list):
            print(f"  S: {self.cvsp_solution}")
