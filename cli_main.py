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

from src.cvsp import cvsp_solver

mpl_use('Qt5Agg', force=True)

DEF_INPUT_FILE = Path("./data/graph1.txt")
DEF_OUTPUT_FILE = Path("./data/graph1-solution.json")
DEF_K_VALUE = 3
DEF_B_VALUE = 3
DEF_LIBRARY = "gurobi"
DEF_FORMULATION_INDEX = 1
DEF_NO_GUI = False
DEF_QUIET = False

EXTRACTED_NODES_COLOR = "silver"
EXTRACTED_SHORES_LINE_WIDTH = 1.0
EXTRACTED_NODES_LINE_STYLE = "dashed"

REMAINING_SHORES_COLORS = plt.rcParams['axes.prop_cycle'].by_key()['color']
REMAINING_SHORES_LINE_WIDTH = 1.5
REMAINING_NODES_LINE_STYLE = "solid"


def main():
    """ Entry point for the main program. """

    args = parse_cli_args()

    solve_cvsp(
        args.input_file,
        args.output_file,
        args.k_value,
        args.b_value,
        args.library_name,
        args.formulation_index,
        args.no_gui,
        args.quiet,
    )


def parse_cli_args():
    """ Function to parse cli's argument flags and their assigned values. """

    parser = argparse.ArgumentParser(description="Test program")

    parser.add_argument("-i",
                        "--input-file",
                        help="import graph's definition from INPUT_FILE")
    parser.add_argument("-o",
                        "--output-file",
                        help="export the solution to OUTPUT_FILE")

    parser.add_argument("-l",
                        "--library_name",
                        default=None,
                        help="select an optimization library to use. " +
                        "For Google OR-Tools library: 'ortools'. " +
                        "For Gurobi Optimization library: 'gurobi'")
    parser.add_argument("-f",
                        "--formulation_index",
                        default=None,
                        help="select a problem formulation to use. " +
                        "For Google OR-Tools library: [1-4]. " +
                        "For Gurobi Optimization library: [1-6]")

    parser.add_argument("-k",
                        "--k-value",
                        default=None,
                        help="min number of remaining shores")
    parser.add_argument("-b",
                        "--b-value",
                        default=None,
                        help="max number of nodes on the remaining shores")

    parser.add_argument("--no-gui",
                        action="store_true",
                        help="do NOT output the solution graphically")
    parser.add_argument("-q",
                        "--quiet",
                        action="store_true",
                        help="suppress all normal cli output")

    args = parser.parse_args()

    if args.input_file:
        args.input_file = Path(args.input_file)
    if args.output_file:
        args.output_file = Path(args.output_file)
    if args.formulation_index:
        args.formulation_index = int(args.formulation_index)
    if args.k_value:
        args.k_value = int(args.k_value)
    if args.b_value:
        args.b_value = int(args.b_value)

    return args


def solve_cvsp(input_file: Path = None,
               output_file: Path = None,
               library_name: str = None,
               formulation_index: int = None,
               k_value: int = None,
               b_value: int = None,
               no_gui: bool = DEF_NO_GUI,
               quiet: bool = DEF_QUIET):
    """ Main function to start the execution of the program. """

    if input_file is None:
        if quiet:
            input_file = DEF_INPUT_FILE
        else:
            input_file = (
                input(f"File path (default = './{DEF_INPUT_FILE}'): ")
                or DEF_INPUT_FILE)

    if output_file is None and not quiet:
        output_file = (
            input(f"Export solution to (default = './{DEF_OUTPUT_FILE}'): ")
            or DEF_OUTPUT_FILE)

    if library_name is None:
        if quiet:
            library_name = DEF_LIBRARY
        else:
            library_name = (
                input(f"Library name (default = '{DEF_LIBRARY}'): ")
                or DEF_LIBRARY)

    if formulation_index is None:
        if quiet:
            formulation_index = DEF_FORMULATION_INDEX
        else:
            formulation_index = int(
                input("Formulation index " +
                      f"(default = '{DEF_FORMULATION_INDEX}'): ")
                or DEF_FORMULATION_INDEX)

    if k_value is None:
        if quiet:
            k_value = DEF_K_VALUE
        else:
            k_value = int(
                input(f"k value (default = '{DEF_K_VALUE}'): ") or DEF_K_VALUE)

    if b_value is None:
        if quiet:
            b_value = DEF_B_VALUE
        else:
            b_value = int(
                input(f"b value (default = '{DEF_B_VALUE}'): ") or DEF_B_VALUE)

    with open(input_file, 'r', encoding="utf-8-sig") as infile:
        raw_data = infile.read()
        n_nodes, n_edges, is_directed, edges_data = parse_data(raw_data)

        graph = build_graph(n_nodes, n_edges, is_directed, edges_data)

        solution = cvsp_solver(graph, library_name, formulation_index - 1,
                               k_value, b_value, quiet)

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
                         node_color=EXTRACTED_NODES_COLOR,
                         width=EXTRACTED_SHORES_LINE_WIDTH,
                         style=EXTRACTED_NODES_LINE_STYLE)

        v_edges = [graph.subgraph(vi).edges() for vi in solution['V']]

        for vi_nodes, vi_edges, shore_color in zip(solution['V'], v_edges,
                                                   REMAINING_SHORES_COLORS):
            nx.draw_networkx(graph,
                             n_pos_dict,
                             nodelist=vi_nodes,
                             edgelist=vi_edges,
                             node_color=shore_color,
                             width=REMAINING_SHORES_LINE_WIDTH,
                             style=REMAINING_NODES_LINE_STYLE)

    elif isinstance(solution, list):
        nx.draw_networkx(graph,
                         n_pos_dict,
                         nodelist=solution,
                         edgelist=graph.edges(solution),
                         node_color=EXTRACTED_NODES_COLOR,
                         width=EXTRACTED_SHORES_LINE_WIDTH,
                         style=EXTRACTED_NODES_LINE_STYLE)

        for node in solution:
            graph.remove_node(node)

        ccc_nodes = [
            graph.subgraph(cc).copy() for cc in nx.connected_components(graph)
        ]
        ccc_edges = [graph.subgraph(cc).edges() for cc in ccc_nodes]

        for cc_nodes, cc_edges, shore_color in zip(ccc_nodes, ccc_edges,
                                                   REMAINING_SHORES_COLORS):
            nx.draw_networkx(graph,
                             n_pos_dict,
                             nodelist=cc_nodes,
                             edgelist=cc_edges,
                             node_color=shore_color,
                             width=REMAINING_SHORES_LINE_WIDTH,
                             style=REMAINING_NODES_LINE_STYLE)

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
