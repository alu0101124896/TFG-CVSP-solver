#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: graph_generator.py
Author: Sergio Tabares Hernández <alu0101124896@ull.edu.es>
Since: Summer 2022
College: University of La Laguna
Degree: Computer Science - Bachelor's Degree Final Project
Description: This program generates a random graph and exports it to a file.
"""

import matplotlib.pyplot as plt

try:
    from .src.graph import Graph
except ImportError:
    from src.graph import Graph


def main():
    """ Main function. """

    graph = Graph()
    graph.show()
    plt.show()

    file_name = input("Graph file name: ")
    graph.export_definition(file_name)


if __name__ == "__main__":
    main()
