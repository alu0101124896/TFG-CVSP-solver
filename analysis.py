#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: analysis.py
Author: Sergio Tabares Hernández <alu0101124896@ull.edu.es>
Since: Summer 2022
College: University of La Laguna
Degree: Computer Science - Bachelor's Degree Final Project
Description: This program solves the Capacitated Vertex Separator Problem
 (CVSP) for a wide variety of graphs and with diferent formulations and
 parameters to make a comparative analysis.
"""

from datetime import datetime
from math import floor

try:
    from .src.graph import Graph
except ImportError:
    from src.graph import Graph


def main():
    """ Main function. """

    counter = 1
    graph_paths = [
        "./data/graph1.txt",
        "./data/random_small_size_low_density_graph.txt",
        "./data/random_small_size_high_density_graph.txt",
        "./data/grid_5x5_graph.txt",
        "./data/graph2.txt",
        "./data/random_medium_size_low_density_graph.txt",
        "./data/grid_10x10_graph.txt",
        "./data/random_medium_size_high_density_graph.txt",
        "./data/random_big_size_low_density_graph.txt",
        "./data/grid_20x20_graph.txt",
        "./data/random_big_size_high_density_graph.txt",
    ]

    for graph_path in graph_paths:
        graph = Graph(graph_path)

        for k_value in range(2, floor(graph.n_nodes / 2)):
            val = floor(graph.n_nodes / k_value)

            for b_value in (val - 1, val, val + 1):
                for library_name, formulation_range in (("ortools", range(4)),
                                                        ("gurobi", range(8))):
                    for formulation_index in formulation_range:
                        print(
                            f"\n\nExecution {counter}:",
                            f"  Graph: {graph_path}",
                            f"  Library name: {library_name}",
                            f"  Formulation index: {formulation_index + 1}",
                            f"  K value: {k_value}",
                            f"  B value: {b_value}",
                            sep="\n",
                            flush=True,
                        )

                        graph.solve_cvsp(
                            library_name,
                            formulation_index,
                            k_value,
                            b_value,
                            quiet=False,
                        )

                        print("\nSolution:", graph.cvsp_solution)

                        print("\n\nTimestamp:", datetime.now())

                        counter += 1


if __name__ == "__main__":
    main()
