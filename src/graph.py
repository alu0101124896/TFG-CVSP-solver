#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import sys

import matplotlib.pyplot as plt
from matplotlib import use as mpl_use
import networkx as nx

from src.cvsp import cvsp_solver

mpl_use('TkAgg', force=True)

QUIET = False

EXTRACTED_NODES_COLOR = "silver"
EXTRACTED_SHORES_LINE_WIDTH = 1.0
EXTRACTED_NODES_LINE_STYLE = "dashed"

REMAINING_SHORES_COLORS = plt.rcParams['axes.prop_cycle'].by_key()['color']
REMAINING_SHORES_LINE_WIDTH = 1.5
REMAINING_NODES_LINE_STYLE = "solid"


class Graph:
    """ Class to represent a NetworkX Graph. """
    def __init__(self, input_file: Path):

        self.nx_graph = None
        self.cvsp_solution = None

        self.n_nodes = None
        self.n_edges = None
        self.is_directed = None
        self.edges_data = None

        self.definition_file = input_file
        self.build_graph()

        self.layout = nx.drawing.layout.kamada_kawai_layout(self.nx_graph)

    def build_graph(self):
        """ Function to build a graph from the given data. """

        with open(self.definition_file, 'r', encoding="utf-8-sig") as file:
            raw_data = file.read()
            self.parse_data(raw_data)

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

    def parse_data(self, raw_data: str):
        """ Function to parse a file's data into a list of edges """

        main_data, *edges_raw_data = raw_data.split("\n")

        n_nodes, n_edges, is_directed = main_data.split(', ')
        self.n_nodes = int(n_nodes)
        self.n_edges = int(n_edges)
        self.is_directed = bool(int(is_directed))

        if edges_raw_data[-1] == '':
            edges_raw_data.pop()

        self.edges_data = [
            edge_raw_data.split(', ') for edge_raw_data in edges_raw_data
        ]

    def solve_cvsp(self, library_name: str, formulation_index: int,
                   k_value: int, b_value: int):
        """ Function to solve the cvsp problem for the loaded graph. """

        self.cvsp_solution = cvsp_solver(
            self.nx_graph,
            library_name,
            formulation_index,
            k_value,
            b_value,
            QUIET,
        )

    def show(self):
        """ Function to show the graph on the gui. """

        if self.cvsp_solution is None:
            nx.draw_networkx(self.nx_graph, self.layout)

        else:
            if isinstance(self.cvsp_solution, dict):
                nx.draw_networkx(self.nx_graph,
                                 self.layout,
                                 nodelist=self.cvsp_solution['S'],
                                 edgelist=self.nx_graph.edges(
                                     self.cvsp_solution['S']),
                                 node_color=EXTRACTED_NODES_COLOR,
                                 width=EXTRACTED_SHORES_LINE_WIDTH,
                                 style=EXTRACTED_NODES_LINE_STYLE)

                v_edges = [
                    self.nx_graph.subgraph(vi).edges()
                    for vi in self.cvsp_solution['V']
                ]

                for vi_nodes, vi_edges, color in zip(self.cvsp_solution['V'],
                                                     v_edges,
                                                     REMAINING_SHORES_COLORS):
                    nx.draw_networkx(self.nx_graph,
                                     self.layout,
                                     nodelist=vi_nodes,
                                     edgelist=vi_edges,
                                     node_color=color,
                                     width=REMAINING_SHORES_LINE_WIDTH,
                                     style=REMAINING_NODES_LINE_STYLE)

            elif isinstance(self.cvsp_solution, list):
                nx.draw_networkx(self.nx_graph,
                                 self.layout,
                                 nodelist=self.cvsp_solution,
                                 edgelist=self.nx_graph.edges(
                                     self.cvsp_solution),
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
                ccc_edges = [
                    graph_copy.subgraph(cc).edges() for cc in ccc_nodes
                ]

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
