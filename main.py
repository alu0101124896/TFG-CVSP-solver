#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" This program calculates the optimal solution to the Capacitated Vertex
Separator Problem (CVSP) on a graph through unilevel and bilevel approaches."""

import argparse
import json
from pathlib import Path
import sys

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import use as mpl_use

from cvsp import cvsp_solver

mpl_use('TkAgg', force=True)

COLORS = [
    "lightcoral",
    "lightgreen",
    "lightblue",
    "yellow",
    "lightsalmon",
]


def main():
    """ Entry point to parse the cli arguments for the main program. """

    # Initialize parser
    parser = argparse.ArgumentParser(description="Test program")

    # Adding optional argument
    parser.add_argument("-i",
                        "--input-file",
                        help="import graph's definition from INPUT_FILE")
    parser.add_argument("-o",
                        "--output-file",
                        help="export the solution to OUTPUT_FILE")

    parser.add_argument("-k",
                        "--k-value",
                        default=None,
                        help="min number of remaining shores")
    parser.add_argument("-b",
                        "--b-value",
                        default=None,
                        help="max number of nodes on the remaining shores")
    parser.add_argument("-f",
                        "--formulation",
                        default=None,
                        help="select a formulation to use [1-4]")

    parser.add_argument("--no-gui",
                        action="store_true",
                        help="do NOT output the solution graphically")
    parser.add_argument("-q",
                        "--quiet",
                        action="store_true",
                        help="suppress all normal cli output")

    # Read arguments from command line
    args = parser.parse_args()

    if args.input_file:
        args.input_file = Path(args.input_file)
    if args.output_file:
        args.output_file = Path(args.output_file)
    if args.k_value:
        args.k_value = int(args.k_value)
    if args.b_value:
        args.b_value = int(args.b_value)
    if args.formulation:
        args.formulation = int(args.formulation)

    cvsp(
        args.input_file,
        args.output_file,
        args.k_value,
        args.b_value,
        args.formulation,
        args.no_gui,
        args.quiet,
    )


def cvsp(input_file: Path = None,
         output_file: Path = None,
         k_value: int = None,
         b_value: int = None,
         formulation_index: int = None,
         no_gui: bool = False,
         quiet: bool = False):
    """ Main function to start the execution of the program. """

    if input_file is None:
        if quiet:
            input_file = Path("./data/graph1.txt")
        else:
            input_file = (input("File path (default = './data/graph1.txt'): ")
                          or Path("./data/graph1.txt"))

    if k_value is None:
        if quiet:
            k_value = 3
        else:
            k_value = int(input("k value (default = '3'): ") or 3)

    if b_value is None:
        if quiet:
            b_value = 3
        else:
            b_value = int(input("b value (default = '3'): ") or 3)

    if formulation_index is None:
        if quiet:
            formulation_index = 1
        else:
            formulation_index = int(input("Formulation index (default = '1'): ") or 1)

    with open(input_file, 'r', encoding="utf-8-sig") as infile:
        raw_data = infile.read()
        n_nodes, n_edges, is_directed, edges_data = parse_data(raw_data)

        graph = build_graph(n_nodes, n_edges, is_directed, edges_data)

        solution = cvsp_solver(graph, k_value, b_value, formulation_index,
                               quiet)

        if solution is not None:
            if not no_gui:
                draw_solution(graph, solution)
            elif not quiet:
                print_solution(solution)

            if output_file is not None:
                with open(output_file, 'w', encoding="utf-8-sig") as outfile:
                    print(json.dumps(solution), file=outfile)

        elif not quiet:
            print("Solution not found")


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


def draw_solution(graph: nx.Graph, solution: dict[str, list]):
    """ Function to draw the graph's solution. """

    n_pos_dict = nx.drawing.layout.kamada_kawai_layout(graph)

    if isinstance(solution, dict):
        nx.draw_networkx(graph,
                         n_pos_dict,
                         nodelist=solution['S'],
                         edgelist=graph.edges(solution['S']),
                         node_color="silver",
                         style="dashed")

        v_edges = [graph.subgraph(vi).edges() for vi in solution['V']]

        for vi_nodes, vi_edges, color in zip(solution['V'], v_edges, COLORS):
            nx.draw_networkx(graph,
                             n_pos_dict,
                             nodelist=vi_nodes,
                             edgelist=vi_edges,
                             node_color=color,
                             width=1.5)

    elif isinstance(solution, list):
        nx.draw_networkx(graph,
                         n_pos_dict,
                         nodelist=solution,
                         edgelist=graph.edges(solution),
                         node_color="silver",
                         style="dashed")

        for node in solution:
            graph.remove_node(node)

        ccc_nodes = [
            graph.subgraph(cc).copy() for cc in nx.connected_components(graph)
        ]
        ccc_edges = [graph.subgraph(cc).edges() for cc in ccc_nodes]

        for cc_nodes, cc_edges, color in zip(ccc_nodes, ccc_edges, COLORS):
            nx.draw_networkx(graph,
                             n_pos_dict,
                             nodelist=cc_nodes,
                             edgelist=cc_edges,
                             node_color=color,
                             width=1.5)

    else:
        sys.exit("Error: unknown solution format")

    plt.show()


def print_solution(solution):
    """ Function to print the solution into the terminal in a more
    comprehensive way. """

    print("\nSolution:")

    if isinstance(solution, dict):
        print(f"  S: {solution['S']}")
        print("  V: [")
        for shore in solution['V']:
            print(f"    {shore},")
        print("  ]")

    elif isinstance(solution, list):
        print(f"  S: {solution}")


if __name__ == "__main__":
    main()
