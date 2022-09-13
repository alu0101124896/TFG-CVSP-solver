#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: cli_main.py
Author: Sergio Tabares Hernández <alu0101124896@ull.edu.es>
Since: Summer 2022
College: University of La Laguna
Degree: Computer Science - Bachelor's Degree Final Project
Description: This program implements a Command Line Interface (CLI) to solve
 the Capacitated Vertex Separator Problem (CVSP) on a graph through various
 formulations using integer optimization approaches.
"""

import argparse
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt

try:
    from .src.graph import Graph
except ImportError:
    from src.graph import Graph

DEF_INPUT_FILE = "./data/graph1.txt"
# Output file format: "./[input_file_path]/[input_file_stem]_solution_[timestamp].txt"
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
    """ Entry point for the main cli program. """

    args = parse_cli_args()

    solve_cvsp(
        args.input_file,
        args.output_file,
        args.library_name,
        args.formulation_index,
        args.k_value,
        args.b_value,
        args.no_gui,
        args.quiet,
    )


def parse_cli_args():
    """ Function to parse cli's argument flags and their assigned values. """

    parser = argparse.ArgumentParser(
        description="This program calculates the optimal solution to the " +
        "Capacitated Vertex Separator Problem (CVSP) on a graph through " +
        "formulations using integer optimization approaches.")

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
                        "For Gurobi Optimization library: [1-8]")

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

    if args.formulation_index:
        args.formulation_index = int(args.formulation_index)
    if args.k_value:
        args.k_value = int(args.k_value)
    if args.b_value:
        args.b_value = int(args.b_value)

    return args


def solve_cvsp(input_file: str = None,
               output_file: str = None,
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
            input_file = (input(f"File path (default = '{DEF_INPUT_FILE}'): ")
                          or DEF_INPUT_FILE)

    if output_file is None:
        input_file_path = Path(input_file)
        def_output_file = ("./" + str(input_file_path.parent) + "/" +
                           input_file_path.stem + "_solution_" +
                           datetime.now().strftime("%Y-%m-%d_%H-%M-%S") +
                           ".txt")
        if quiet:
            output_file = def_output_file
        else:
            output_file = (
                input(f"Export solution to (default = '{def_output_file}'): ")
                or def_output_file)

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

    graph = Graph(input_file)

    graph.solve_cvsp(library_name, formulation_index - 1, k_value, b_value,
                     quiet)

    if graph.cvsp_solution is not None:
        if not no_gui:
            graph.show()
            plt.show()

        elif not quiet:
            graph.print_solution()

        if output_file is not None:
            graph.export_solution(output_file)

    elif not quiet:
        print("Solution not found")


if __name__ == "__main__":
    main()
