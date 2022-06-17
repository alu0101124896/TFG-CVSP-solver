#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" This program calculates the optimal solution to the Capacitated Vertex
Separator Problem (CVSP) on a graph through unilevel and bilevel aproaches. """

from pathlib import Path
import sys

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import use as mpl_use

mpl_use('TkAgg', force=True)

COLORS = [
    "lightcoral",
    "lightgreen",
    "lightblue",
    "yellow",
    "lightsalmon",
]


def main():
    """ Main function to start the execution of the program. """

    # file_path = (input("File path (default = './data/graph1.txt'): ")
    #              or Path("./data/graph1.txt"))
    # k_value = (input("k value (default = '3'): ") or 3)
    # b_value = (input("b value (default = '3'): ") or 3)

    # Temporal non-interactive version
    file_path = Path("./data/graph1.txt")
    k_value = 3
    b_value = 3

    with open(file_path, "r", encoding="utf-8-sig") as file:
        raw_data = file.read()
        n_nodes, n_edges, is_directed, edges_data = parse_data(raw_data)

        graph = build_graph(n_nodes, n_edges, is_directed, edges_data)

        solution = cvsp(graph, k_value, b_value)

        draw_solution(graph, solution)


def parse_data(raw_data: str) -> tuple[int, int, bool, list[list[str]]]:
    """ Function to parse a file's data into a list of edges """

    main_data, *edges_raw_data = raw_data.split("\n")

    n_nodes, n_edges, is_directed = main_data.split(', ')

    if edges_raw_data[-1] == '':
        edges_raw_data.pop()

    edges_data = [
        edge_raw_data.split(', ') for edge_raw_data in edges_raw_data
    ]

    return int(n_nodes), int(n_edges), bool(int(is_directed)), edges_data


def build_graph(n_nodes: int, n_edges: int, is_directed: bool,
                edges_data: list[list[str]]) -> nx.Graph:
    """ Function to build a graph from the given data. """

    if is_directed:
        graph = nx.DiGraph(edges_data)
    else:
        graph = nx.Graph(edges_data)

    if graph.number_of_nodes() != n_nodes:
        sys.exit("Error: The graph's number of nodes is not the same as" +
                 " on the data file.")

    if graph.number_of_edges() != n_edges:
        sys.exit("Error: The graph's number of edges is not the same as" +
                 " on the data file.")

    return graph


def cvsp(graph: nx.Graph, k_value: int, b_value: int) -> dict[str, list]:
    """ Function to solve the Capacitated Vertex Separator Problem on the given
    graph. """

    # Solution to graph 1
    solution = {
        "S": ["v8", "v9"],
        "V": [
            ["v1", "v2", "v7"],
            ["v5", "v6", "v10"],
            ["v3", "v4"],
        ]
    }

    return solution


def draw_solution(graph: nx.Graph, solution: dict[str, list]):
    """ Function to draw the graph's solution. """

    # Graph1's positions
    n_pos_dict = {
        "v1": (10, 15),
        "v2": (15, 15),
        "v3": (20, 15),
        "v4": (25, 15),
        "v5": (30, 15),
        "v6": (35, 15),
        "v7": (15, 10),
        "v8": (20, 10),
        "v9": (25, 10),
        "v10": (30, 10),
    }

    nx.draw_networkx(graph,
                     n_pos_dict,
                     nodelist=solution["S"],
                     edgelist=graph.edges(solution["S"]),
                     node_color="silver",
                     style="dashed")

    v_edges = [graph.subgraph(vi).edges() for vi in solution["V"]]

    for vi_nodes, vi_edges, color in zip(solution["V"], v_edges, COLORS):
        nx.draw_networkx(graph,
                         n_pos_dict,
                         nodelist=vi_nodes,
                         edgelist=vi_edges,
                         node_color=color,
                         width=1.5)

    plt.show()


if __name__ == "__main__":
    main()
