#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" This program has the implementation of various formulations to solve the
Capacitated Vertex Separator Problem (CVSP) on a graph through unilevel and
bilevel approaches."""

from math import inf

import networkx as nx
from ortools.linear_solver import pywraplp


def cvsp_solver(graph: nx.Graph,
                k_value: int,
                b_value: int,
                formulation_index: int = 1,
                quiet: bool = False) -> (dict[str, list] | None):
    """ Function to solve the Capacitated Vertex Separator Problem on the given
    graph. """

    formulations = [
        formulation_1,
        formulation_2,
        formulation_3,
        formulation_4,
    ]
    solution = formulations[formulation_index - 1](
        graph,
        k_value,
        b_value,
        quiet,
    )

    return solution


def formulation_1(graph: nx.Graph,
                  k_value: int,
                  b_value: int,
                  quiet: bool = False) -> (dict[str, list] | None):
    """ First formulation of an unilevel approach. """

    K = range(k_value)
    V = graph.nodes()
    E = graph.edges()

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")
    assert isinstance(solver, pywraplp.Solver)

    # Create the binary variables ("1e" constraints).
    e = []
    for i in K:
        shore_i = {}
        for v in V:
            shore_i.update({v: solver.IntVar(0, 1, f"ξ_{i}_{v}")})
        e.append(shore_i)

    # Add the "1a" objective function.
    solver.Maximize(sum(e[i][v] for i in K for v in V))

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

    if not quiet:
        print("\nProblem definition:")
        print("  Number of variables =", solver.NumVariables())
        print("  Number of constraints =", solver.NumConstraints())

    # Solve the system.
    status = solver.Solve()

    if not quiet:
        print("\nAdvanced usage:")
        print(f"  Problem solved in {solver.wall_time()} milliseconds")
        print(f"  Problem solved in {solver.iterations()} iterations")
        print(f"  Problem solved in {solver.nodes()} branch-and-bound nodes")

    # Print and Parse the solution found.
    if status == pywraplp.Solver.OPTIMAL:
        solution = {'S': [], 'V': [[] for _ in K]}

        for v in V:
            n_shores = 0

            for i in K:
                int_var = e[i][v]
                assert isinstance(int_var, pywraplp.Variable)

                if int_var.solution_value() == 1:
                    solution['V'][i].append(v)
                    n_shores += 1

            if n_shores == 0:
                solution['S'].append(v)

        return solution

    if not quiet:
        print("The problem does not have an optimal solution.")

    return None


def formulation_2(graph: nx.Graph,
                  k_value: int,
                  b_value: int,
                  quiet: bool = False) -> (dict[str, list] | None):
    """ Second formulation of an unilevel approach. """

    K = range(k_value)
    V = graph.nodes()
    Q = list(nx.find_cliques(graph))

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")
    assert isinstance(solver, pywraplp.Solver)

    # Create the binary variables ("1e" constraints).
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

    # Add the "1a" objective function.
    solver.Maximize(sum(e[i][v] for i in K for v in V))

    # Add the formulation constraints.
    # "2a" constraints.
    for q in Q:
        solver.Add(sum(y[i][f"{q}"] for i in K) <= 1)

    # "2b" constraints.
    for i in K:
        for q in Q:
            for v in q:
                solver.Add(e[i][v] - y[i][f"{q}"] <= 0)

    # "1d" constraints.
    for i in K:
        solver.Add(sum(e[i][v] for v in V) <= b_value)

    if not quiet:
        print("\nProblem definition:")
        print("  Number of variables =", solver.NumVariables())
        print("  Number of constraints =", solver.NumConstraints())

    # Solve the system.
    status = solver.Solve()

    if not quiet:
        print("\nAdvanced usage:")
        print(f"  Problem solved in {solver.wall_time()} milliseconds")
        print(f"  Problem solved in {solver.iterations()} iterations")
        print(f"  Problem solved in {solver.nodes()} branch-and-bound nodes")

    # Print and Parse the solution found.
    if status == pywraplp.Solver.OPTIMAL:
        solution = {'S': [], 'V': [[] for _ in K]}

        for v in V:
            n_shores = 0

            for i in K:
                int_var = e[i][v]
                assert isinstance(int_var, pywraplp.Variable)

                if int_var.solution_value() == 1:
                    solution['V'][i].append(v)
                    n_shores += 1

            if n_shores == 0:
                solution['S'].append(v)

        return solution

    if not quiet:
        print("The problem does not have an optimal solution.")

    return None


def formulation_3(graph: nx.Graph,
                  k_value: int,
                  b_value: int,
                  quiet: bool = False) -> (list[str] | None):
    """ Third formulation for an unilevel approach. """

    V = graph.nodes()

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")
    assert isinstance(solver, pywraplp.Solver)

    # Create the binary variables ("3c" constraints).
    x = {}
    for v in V:
        x.update({v: solver.IntVar(0, 1, f"{v}")})

    # Add the "3a" objective function.
    solver.Minimize(sum(x[v] for v in V))

    # Add the "3b" constraints.
    W = subsets(list(V))
    for w in W:
        gw = graph.subgraph(w)

        if any((len(cc_nodes) > b_value)
               for cc_nodes in nx.connected_components(gw)):
            ow = inf

        else:
            ow = n_bins_to_pack(gw, b_value)

        if ow > k_value:
            solver.Add(sum(x[v] for v in w) >= 1)

    if not quiet:
        print("\nProblem definition:")
        print("  Number of variables =", solver.NumVariables())
        print("  Number of constraints =", solver.NumConstraints())

    # Solve the system.
    status = solver.Solve()

    if not quiet:
        print("\nAdvanced usage:")
        print(f"  Problem solved in {solver.wall_time()} milliseconds")
        print(f"  Problem solved in {solver.iterations()} iterations")
        print(f"  Problem solved in {solver.nodes()} branch-and-bound nodes")

    # Print and Parse the solution found.
    if status == pywraplp.Solver.OPTIMAL:
        solution = []

        for v in V:
            int_var = x[v]
            assert isinstance(int_var, pywraplp.Variable)

            if int_var.solution_value() == 1:
                solution.append(v)

        return solution

    if not quiet:
        print("The problem does not have an optimal solution.")

    return None


def formulation_4(graph: nx.Graph,
                  k_value: int,
                  b_value: int,
                  quiet: bool = False) -> (list[str] | None):
    """ Fourth formulation for an unilevel approach. """

    V = graph.nodes()

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")
    assert isinstance(solver, pywraplp.Solver)

    # Create the binary variables ("3c" constraints).
    x = {}
    for v in V:
        x.update({v: solver.IntVar(0, 1, f"{v}")})

    # Add the "3a" objective function.
    solver.Minimize(sum(x[v] for v in V))

    # Add the "4" constraints.
    W = subsets(list(V))
    for w in W:
        gw = graph.subgraph(w)

        for C in nx.connected_components(gw):
            if len(C) == b_value + 1:
                solver.Add(sum(x[v] for v in C) >= 1)

    if not quiet:
        print("\nProblem definition:")
        print("  Number of variables =", solver.NumVariables())
        print("  Number of constraints =", solver.NumConstraints())

    # Solve the system.
    status = solver.Solve()

    if not quiet:
        print("\nAdvanced usage:")
        print(f"  Problem solved in {solver.wall_time()} milliseconds")
        print(f"  Problem solved in {solver.iterations()} iterations")
        print(f"  Problem solved in {solver.nodes()} branch-and-bound nodes")

    # Print and Parse the solution found.
    if status == pywraplp.Solver.OPTIMAL:
        solution = []

        for v in V:
            int_var = x[v]
            assert isinstance(int_var, pywraplp.Variable)

            if int_var.solution_value() == 1:
                solution.append(v)

        return solution

    if not quiet:
        print("The problem does not have an optimal solution.")

    return None


def subsets(nodes: list[str]) -> list[list[str]]:
    """ Function to get all combinations with the given nodes. """

    if len(nodes) == 0:
        return [[]]

    x = subsets(nodes[1:])
    z = [[nodes[0]] + y for y in x] + x

    return z


def n_bins_to_pack(graph: nx.Graph, bin_size: int) -> int:
    """ Function to get the number of bins of size bin_size needed to pack the
    connected components of the given graph. """

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")
    assert isinstance(solver, pywraplp.Solver)

    # Variables
    # x[i, j] = 1 if item i is packed in bin j.
    x = {}
    for i in graph.nodes():
        for j in range(len(graph.nodes())):
            x[(i, j)] = solver.IntVar(0, 1, f"x_{i}_{j}")

    # y[j] = 1 if bin j is used.
    y = {}
    for j in range(len(graph.nodes())):
        y[j] = solver.IntVar(0, 1, f"y[{j}]")

    # Constraints
    # Each item must be in exactly one bin.
    for i in graph.nodes():
        solver.Add(sum(x[i, j] for j in range(len(graph.nodes()))) == 1)

    # The amount packed in each bin cannot exceed its capacity.
    for j in range(len(graph.nodes())):
        solver.Add(sum(x[(i, j)] for i in graph.nodes()) <= y[j] * bin_size)

    # Objective: minimize the number of bins used.
    solver.Minimize(solver.Sum([y[j] for j in range(len(graph.nodes()))]))

    # Solve the system.
    status = solver.Solve()

    # Print and Parse the solution found.
    if status == pywraplp.Solver.OPTIMAL:
        num_bins = 0

        for j in range(len(graph.nodes())):
            if y[j].solution_value() == 1:
                bin_items = []
                bin_weight = 0

                for i in graph.nodes():
                    if x[i, j].solution_value() > 0:
                        bin_items.append(i)
                        bin_weight += 1

                if bin_weight > 0:
                    num_bins += 1

    else:
        num_bins = inf

    return num_bins
