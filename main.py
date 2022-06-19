#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" This program calculates the optimal solution to the Capacitated Vertex
Separator Problem (CVSP) on a graph through unilevel and bilevel approaches."""

from pathlib import Path
import sys

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import use as mpl_use
from ortools.linear_solver import pywraplp

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
    file_path = Path("./data/graph2.txt")
    k_value = 4
    b_value = 9

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

    # solution = formulation_1(graph, k_value, b_value)
    solution = formulation_2(graph, k_value, b_value)

    return solution


def formulation_1(graph: nx.Graph, k_value: int,
                  b_value: int) -> dict[str, list]:
    """ First formulation of an unilevel approach. """

    K = range(k_value)
    V = graph.nodes()
    E = graph.edges()

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")
    assert isinstance(solver, pywraplp.Solver)

    # Create the integer binary variables ("1e" constraints).
    e = []
    for i in K:
        shore_i = {}
        for v in V:
            shore_i.update({v: solver.IntVar(0, 1, f"ξ_{i}_{v}")})
        e.append(shore_i)

    # Add the formulation constraints.
    # "1b" constraints.
    for v in V:
        solver.Add(sum(e[i][v] for i in K) <= 1)

    # "1c" constraints.
    for i in K:
        for w, v in E:
            solver.Add(e[i][w] + sum(e[j][v] for j in K if i != j) <= 1)

    # "1d" constraints.
    for i in K:
        solver.Add(sum(e[i][v] for v in V) <= b_value)

    print("\nProblem definition:")
    print("  Number of variables =", solver.NumVariables())
    print("  Number of constraints =", solver.NumConstraints())

    # Add the "1a" objective function
    solver.Maximize(sum(e[i][v] for i in K for v in V))

    # Solve the system.
    status = solver.Solve()

    print("\nAdvanced usage:")
    print(f"  Problem solved in {solver.wall_time()} milliseconds")
    print(f"  Problem solved in {solver.iterations()} iterations")
    print(f"  Problem solved in {solver.nodes()} branch-and-bound nodes")

    # Print and Parse the solution found.
    if status == pywraplp.Solver.OPTIMAL:
        solution = {"S": [], "V": [[] for _ in K]}

        for v in V:
            n_shores = 0

            for i in K:
                int_var = e[i][v]
                assert isinstance(int_var, pywraplp.Variable)

                if int_var.solution_value() == 1:
                    solution["V"][i].append(v)
                    n_shores += 1

            if n_shores == 0:
                solution["S"].append(v)

        return solution

    print("The problem does not have an optimal solution.")
    return None


def formulation_2(graph: nx.Graph, k_value: int,
                  b_value: int) -> dict[str, list]:
    """ Second formulation of an unilevel approach. """

    K = range(k_value)
    V = graph.nodes()
    Q = list(nx.find_cliques(graph))

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")
    assert isinstance(solver, pywraplp.Solver)

    # Create the integer binary variables ("1e" constraints).
    e = []
    for i in K:
        shore_i = {}
        for v in V:
            shore_i.update({v: solver.IntVar(0, 1, f"ξ_{i}_{v}")})
        e.append(shore_i)

    y = []
    for i in K:
        shore_i = {}
        for q in Q:
            shore_i.update({f"{q}": solver.IntVar(0, 1, f"ψ_{i}_{q}")})
        y.append(shore_i)

    # Add the formulation constraints.
    # "1b" constraints.
    for q in Q:
        solver.Add(sum(y[i][f"{q}"] for i in K) <= 1)

    # "1c" constraints.
    for i in K:
        for q in Q:
            for v in q:
                solver.Add(e[i][v] - y[i][f"{q}"] <= 0)

    # "1d" constraints.
    for i in K:
        solver.Add(sum(e[i][v] for v in V) <= b_value)

    print("\nProblem definition:")
    print("  Number of variables =", solver.NumVariables())
    print("  Number of constraints =", solver.NumConstraints())

    # Add the "1a" objective function
    solver.Maximize(sum(e[i][v] for i in K for v in V))

    # Solve the system.
    status = solver.Solve()

    print("\nAdvanced usage:")
    print(f"  Problem solved in {solver.wall_time()} milliseconds")
    print(f"  Problem solved in {solver.iterations()} iterations")
    print(f"  Problem solved in {solver.nodes()} branch-and-bound nodes")

    # Print and Parse the solution found.
    if status == pywraplp.Solver.OPTIMAL:
        solution = {"S": [], "V": [[] for _ in K]}

        for v in V:
            n_shores = 0

            for i in K:
                int_var = e[i][v]
                assert isinstance(int_var, pywraplp.Variable)

                if int_var.solution_value() == 1:
                    solution["V"][i].append(v)
                    n_shores += 1

            if n_shores == 0:
                solution["S"].append(v)

        return solution

    print("The problem does not have an optimal solution.")
    return None


def draw_solution(graph: nx.Graph, solution: dict[str, list]):
    """ Function to draw the graph's solution. """

    n_pos_dict = nx.drawing.layout.kamada_kawai_layout(graph)

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
