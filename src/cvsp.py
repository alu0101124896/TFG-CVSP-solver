#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: cvsp.py
Author: Sergio Tabares Hernández <alu0101124896@ull.edu.es>
Since: Summer 2022
College: University of La Laguna
Degree: Computer Science - Bachelor's Degree Final Project
Description: This program calculates the optimal solution to the Capacitated
 Vertex Separator Problem (CVSP) on a graph through various formulations using
 integer optimization approaches.
"""

from itertools import combinations
from math import inf

from gurobipy import GRB, Model, StatusConstClass
import networkx as nx
from ortools.linear_solver import pywraplp

STATUS_DICT = {
    StatusConstClass.__dict__[k]: k
    for k in StatusConstClass.__dict__.keys() if k[0] >= 'A' and k[0] <= 'Z'
}


def cvsp_solver(graph: nx.Graph,
                library_name: str = "gurobi",
                formulation_index: int = 0,
                k_value: int = 3,
                b_value: int = 3,
                quiet: bool = False) -> (dict[str, list] | list[str] | None):
    """ Function to solve the Capacitated Vertex Separator Problem on the given
    graph. """

    formulations = {
        "ortools": [
            formulation_1_ortools,
            formulation_2_ortools,
            formulation_3_ortools,
            formulation_4_ortools,
        ],
        "gurobi": [
            formulation_1_gurobi,
            formulation_1_alt_b_gurobi,
            formulation_1_alt_c_gurobi,
            formulation_2_gurobi,
            formulation_3_gurobi,
            formulation_3_lazy_gurobi,
            formulation_4_gurobi,
            formulation_4_lazy_gurobi,
        ],
    }
    solution = formulations.get(library_name)[formulation_index](
        graph,
        k_value,
        b_value,
        quiet,
    )

    return solution


def formulation_1_ortools(graph: nx.Graph,
                          k_value: int,
                          b_value: int,
                          quiet: bool = False) -> (dict[str, list] | None):
    """ First formulation using the OR-Tools library. """

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
                variable = e[i][v]
                assert isinstance(variable, pywraplp.Variable)

                if variable.solution_value() == 1:
                    solution['V'][i].append(v)
                    n_shores += 1

            if n_shores == 0:
                solution['S'].append(v)

        return solution

    if not quiet:
        print("The problem does not have an optimal solution.")

    return None


def formulation_2_ortools(graph: nx.Graph,
                          k_value: int,
                          b_value: int,
                          quiet: bool = False) -> (dict[str, list] | None):
    """ Second formulation using the OR-Tools library. """

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
                variable = e[i][v]
                assert isinstance(variable, pywraplp.Variable)

                if variable.solution_value() == 1:
                    solution['V'][i].append(v)
                    n_shores += 1

            if n_shores == 0:
                solution['S'].append(v)

        return solution

    if not quiet:
        print("The problem does not have an optimal solution.")

    return None


def formulation_3_ortools(graph: nx.Graph,
                          k_value: int,
                          b_value: int,
                          quiet: bool = False) -> (list[str] | None):
    """ Third formulation using the OR-Tools library. """

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
    W = []
    for subset_size in range(1, len(V)):
        W.extend(combinations(V, subset_size))

    for w in W:
        gw = graph.subgraph(w)

        if any((len(cc_nodes) > b_value)
               for cc_nodes in nx.connected_components(gw)):
            ow = inf

        else:
            ow = n_bins_to_pack_ortools(gw, b_value)

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
            variable = x[v]
            assert isinstance(variable, pywraplp.Variable)

            if variable.solution_value() == 1:
                solution.append(v)

        return solution

    if not quiet:
        print("The problem does not have an optimal solution.")

    return None


def formulation_4_ortools(graph: nx.Graph,
                          _,
                          b_value: int,
                          quiet: bool = False) -> (list[str] | None):
    """ Fourth formulation using the OR-Tools library. """

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
    W = []
    for subset_size in range(1, len(V)):
        W.extend(combinations(V, subset_size))

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
            variable = x[v]
            assert isinstance(variable, pywraplp.Variable)

            if variable.solution_value() == 1:
                solution.append(v)

        return solution

    if not quiet:
        print("The problem does not have an optimal solution.")

    return None


def formulation_1_gurobi(graph: nx.Graph,
                         k_value: int,
                         b_value: int,
                         quiet: bool = False) -> (dict[str, list] | None):
    """ First formulation using the Gurobi library. """

    K = range(k_value)
    V = graph.nodes()
    E = graph.edges()

    # Create a new model.
    model = Model()
    model.Params.OutputFlag = 0

    # Create the binary variables ("1e" constraints)
    e = []
    for i in K:
        shore_i = {}
        for v in V:
            shore_i.update(
                {v: model.addVar(vtype=GRB.BINARY, name=f"ξ_{i}_{v}")})
        e.append(shore_i)

    # Add the "1a" objective function.
    model.setObjective(sum(e[i][v] for i in K for v in V), GRB.MAXIMIZE)

    # Add the formulation constraints.
    # "1b" constraints.
    for v in V:
        model.addConstr(sum(e[i][v] for i in K) <= 1)

    # "1c" constraints.
    for i in K:
        for w, v in E:
            model.addConstr(e[i][w] + sum(e[j][v] for j in K if i != j) <= 1)

    # "1d" constraints.
    for i in K:
        model.addConstr(sum(e[i][v] for v in V) <= b_value)

    # Solve the system.
    model.optimize()

    if not quiet:
        print(f"\nSolution found in {model.Runtime} seconds")

    # Print and Parse the solution found.
    if STATUS_DICT[model.status] == "OPTIMAL":
        solution = {'S': [], 'V': [[] for _ in K]}

        for v in V:
            n_shores = 0

            for i in K:
                variable = e[i][v]

                if variable.x == 1:
                    solution['V'][i].append(v)
                    n_shores += 1

            if n_shores == 0:
                solution['S'].append(v)

        return solution

    if not quiet:
        print("The problem does not have an optimal solution.")

    return None


def formulation_1_alt_b_gurobi(
        graph: nx.Graph,
        k_value: int,
        b_value: int,
        quiet: bool = False) -> (dict[str, list] | None):
    """ Teacher's alternative "b" formulation. """

    K = range(k_value)
    V = graph.nodes()
    E = graph.edges()

    # Create a new model.
    model = Model()
    model.Params.OutputFlag = 0

    # Create the binary variables ("1e" constraints)
    e = []
    for i in K:
        shore_i = {}
        for v in V:
            shore_i.update(
                {v: model.addVar(vtype=GRB.BINARY, name=f"ξ_{i}_{v}")})
        e.append(shore_i)

    # Add the "1a" objective function.
    model.setObjective(sum(e[i][v] for i in K for v in V), GRB.MAXIMIZE)

    # Add the formulation constraints.
    # "1b" constraints.
    for v in V:
        model.addConstr(sum(e[i][v] for i in K) <= 1)

    # alternative version "b" of "1c" constraints.
    for i in K:
        for j in K:
            if i != j:
                for w, v in E:
                    model.addConstr(e[i][w] + e[j][v] <= 1)

    # "1d" constraints.
    for i in K:
        model.addConstr(sum(e[i][v] for v in V) <= b_value)

    # Solve the system.
    model.optimize()

    if not quiet:
        print(f"\nSolution found in {model.Runtime} seconds")

    # Print and Parse the solution found.
    if STATUS_DICT[model.status] == "OPTIMAL":
        solution = {'S': [], 'V': [[] for _ in K]}

        for v in V:
            n_shores = 0

            for i in K:
                variable = e[i][v]

                if variable.x == 1:
                    solution['V'][i].append(v)
                    n_shores += 1

            if n_shores == 0:
                solution['S'].append(v)

        return solution

    if not quiet:
        print("The problem does not have an optimal solution.")

    return None


def formulation_1_alt_c_gurobi(
        graph: nx.Graph,
        k_value: int,
        b_value: int,
        quiet: bool = False) -> (dict[str, list] | None):
    """ Teacher's alternative "c" formulation. """

    K = range(k_value)
    V = graph.nodes()
    E = graph.edges()

    # Create a new model.
    model = Model()
    model.Params.OutputFlag = 0

    # Create the binary variables ("1e" constraints)
    e = []
    for i in K:
        shore_i = {}
        for v in V:
            shore_i.update(
                {v: model.addVar(vtype=GRB.BINARY, name=f"ξ_{i}_{v}")})
        e.append(shore_i)

    # Add the "1a" objective function.
    model.setObjective(sum(e[i][v] for i in K for v in V), GRB.MAXIMIZE)

    # Add the formulation constraints.
    # "1b" constraints.
    for v in V:
        model.addConstr(sum(e[i][v] for i in K) <= 1)

    # alternative version "c" of "1c" constraints.
    max_subset_size = k_value
    # max_subset_size = 2  # Do not generate all subsets

    for subset_size in range(1, max_subset_size + 1):
        L = combinations(K, subset_size)

        for l in L:
            for w, v in E:
                model.addConstr(
                    sum(e[k1][w]
                        for k1 in l) + sum(e[k2][v]
                                           for k2 in (set(K) - set(l))) <= 1)

    # "1d" constraints.
    for i in K:
        model.addConstr(sum(e[i][v] for v in V) <= b_value)

    # Solve the system.
    model.optimize()

    if not quiet:
        print(f"\nSolution found in {model.Runtime} seconds")

    # Print and Parse the solution found.
    if STATUS_DICT[model.status] == "OPTIMAL":
        solution = {'S': [], 'V': [[] for _ in K]}

        for v in V:
            n_shores = 0

            for i in K:
                variable = e[i][v]

                if variable.x == 1:
                    solution['V'][i].append(v)
                    n_shores += 1

            if n_shores == 0:
                solution['S'].append(v)

        return solution

    if not quiet:
        print("The problem does not have an optimal solution.")

    return None


def formulation_2_gurobi(graph: nx.Graph,
                         k_value: int,
                         b_value: int,
                         quiet: bool = False) -> (dict[str, list] | None):
    """ Second formulation using the Gurobi library. """

    K = range(k_value)
    V = graph.nodes()
    Q = list(nx.find_cliques(graph))

    # Create a new model.
    model = Model()
    model.Params.OutputFlag = 0

    # Create the binary variables ("1e" constraints).
    e = []
    for i in K:
        shore_i = {}
        for v in V:
            shore_i.update(
                {v: model.addVar(vtype=GRB.BINARY, name=f"ξ_{i}_{v}")})
        e.append(shore_i)

    y = []
    for i in K:
        shore_i = {}
        for q in Q:
            shore_i.update(
                {f"{q}": model.addVar(vtype=GRB.BINARY, name=f"ψ_{i}_{q}")})
        y.append(shore_i)

    # Add the "1a" objective function.
    model.setObjective(sum(e[i][v] for i in K for v in V), GRB.MAXIMIZE)

    # Add the formulation constraints.
    # "2a" constraints.
    for q in Q:
        model.addConstr(sum(y[i][f"{q}"] for i in K) <= 1)

    # "2b" constraints.
    for i in K:
        for q in Q:
            for v in q:
                model.addConstr(e[i][v] - y[i][f"{q}"] <= 0)

    # "1d" constraints.
    for i in K:
        model.addConstr(sum(e[i][v] for v in V) <= b_value)

    # Solve the system.
    model.optimize()

    if not quiet:
        print(f"\nSolution found in {model.Runtime} seconds")

    # Print and Parse the solution found.
    if STATUS_DICT[model.status] == "OPTIMAL":
        solution = {'S': [], 'V': [[] for _ in K]}

        for v in V:
            n_shores = 0

            for i in K:
                variable = e[i][v]

                if variable.x == 1:
                    solution['V'][i].append(v)
                    n_shores += 1

            if n_shores == 0:
                solution['S'].append(v)

        return solution

    if not quiet:
        print("The problem does not have an optimal solution.")

    return None


def formulation_3_gurobi(graph: nx.Graph,
                         k_value: int,
                         b_value: int,
                         quiet: bool = False) -> (list[str] | None):
    """ Third formulation using the Gurobi library. """

    V = graph.nodes()

    # Create a new model.
    model = Model()
    model.Params.OutputFlag = 0

    # Create the binary variables ("3c" constraints).
    x = {}
    for v in V:
        x.update({v: model.addVar(vtype=GRB.BINARY, name=f"{v}")})

    # Add the "3a" objective function.
    model.setObjective(sum(x[v] for v in V), GRB.MINIMIZE)

    # Add the "3b" constraints.
    W = []
    for subset_size in range(1, len(V)):
        W.extend(combinations(V, subset_size))

    for w in W:
        gw = graph.subgraph(w)

        if any((len(cc_nodes) > b_value)
               for cc_nodes in nx.connected_components(gw)):
            ow = inf

        else:
            ow = n_bins_to_pack_gurobi(gw, b_value)

        if ow > k_value:
            model.addConstr(sum(x[v] for v in w) >= 1)

    # Solve the system.
    model.optimize()

    if not quiet:
        print(f"\nSolution found in {model.Runtime} seconds")

    # Print and Parse the solution found.
    if STATUS_DICT[model.status] == "OPTIMAL":
        solution = []

        for v in V:
            variable = x[v]

            if variable.x == 1:
                solution.append(v)

        return solution

    if not quiet:
        print("The problem does not have an optimal solution.")

    return None


def formulation_3_lazy_gurobi(graph: nx.Graph,
                              k_value: int,
                              b_value: int,
                              quiet: bool = False) -> (list[str] | None):
    """ Third formulation using the Gurobi library and the dynamic row
    generation method. """

    V = graph.nodes()

    # Create a new model.
    model = Model()
    model.Params.OutputFlag = 0
    model.Params.lazyConstraints = 1

    # Create the binary variables ("3c" constraints).
    x = {}
    for v in V:
        x.update({v: model.addVar(vtype=GRB.BINARY, name=f"{v}")})

    # Add the "3a" objective function.
    model.setObjective(sum(x[v] for v in V), GRB.MINIMIZE)

    # Add the "3b" constraints by the dynamic row generation method.
    def sec_lazy(model, where):
        if where == GRB.Callback.MIPSOL:
            values = model.cbGetSolution(x)
            w = list(node for node, value in values.items() if value < 0.1)
            gw = graph.subgraph(w)

            if any((len(cc_nodes) > b_value)
                   for cc_nodes in nx.connected_components(gw)):
                ow = inf

            else:
                ow = n_bins_to_pack_gurobi(gw, b_value)

            constraint_added = False
            if ow > k_value:
                model.cbLazy(sum(x[v] for v in w) >= 1)
                constraint_added = True

            return constraint_added

        return True

    # Solve the system.
    model.optimize(sec_lazy)

    if not quiet:
        print(f"\nSolution found in {model.Runtime} seconds")

    # Print and Parse the solution found.
    if STATUS_DICT[model.status] == "OPTIMAL":
        solution = []

        for v in V:
            variable = x[v]

            if variable.x == 1:
                solution.append(v)

        return solution

    if not quiet:
        print("The problem does not have an optimal solution.")

    return None


def formulation_4_gurobi(graph: nx.Graph,
                         _,
                         b_value: int,
                         quiet: bool = False) -> (list[str] | None):
    """ Fourth formulation using the Gurobi library. """

    V = graph.nodes()

    # Create a new model.
    model = Model()
    model.Params.OutputFlag = 0

    # Create the binary variables ("3c" constraints).
    x = {}
    for v in V:
        x.update({v: model.addVar(vtype=GRB.BINARY, name=f"{v}")})

    # Add the "3a" objective function.
    model.setObjective(sum(x[v] for v in V), GRB.MINIMIZE)

    # Add the "4" constraints.
    W = []
    for subset_size in range(1, len(V)):
        W.extend(combinations(V, subset_size))

    for w in W:
        gw = graph.subgraph(w)

        for C in nx.connected_components(gw):
            if len(C) == b_value + 1:
                model.addConstr(sum(x[v] for v in C) >= 1)

    # Solve the system.
    model.optimize()

    if not quiet:
        print(f"\nSolution found in {model.Runtime} seconds")

    # Print and Parse the solution found.
    if STATUS_DICT[model.status] == "OPTIMAL":
        solution = []

        for v in V:
            variable = x[v]

            if variable.x == 1:
                solution.append(v)

        return solution

    if not quiet:
        print("The problem does not have an optimal solution.")

    return None


def formulation_4_lazy_gurobi(graph: nx.Graph,
                              _,
                              b_value: int,
                              quiet: bool = False) -> (list[str] | None):
    """ Fourth formulation using the Gurobi library and the dynamic row
    generation method. """

    V = graph.nodes()

    # Create a new model.
    model = Model()
    model.Params.OutputFlag = 0
    model.Params.lazyConstraints = 1

    # Create the binary variables ("3c" constraints).
    x = {}
    for v in V:
        x.update({v: model.addVar(vtype=GRB.BINARY, name=f"{v}")})

    # Add the "3a" objective function.
    model.setObjective(sum(x[v] for v in V), GRB.MINIMIZE)

    # Add the "4" constraints.
    def sec_lazy(model, where):
        if where == GRB.Callback.MIPSOL:
            values = model.cbGetSolution(x)
            w = list(node for node, value in values.items() if value < 0.1)
            gw = graph.subgraph(w)

            constraints_added = False
            for C in nx.connected_components(gw):
                if len(C) > b_value:
                    model.cbLazy(sum(x[v] for v in C) >= 1)
                    constraints_added = True

            return constraints_added

        return True

    # Solve the system.
    model.optimize(sec_lazy)

    if not quiet:
        print(f"\nSolution found in {model.Runtime} seconds")

    # Print and Parse the solution found.
    if STATUS_DICT[model.status] == "OPTIMAL":
        solution = []

        for v in V:
            variable = x[v]

            if variable.x == 1:
                solution.append(v)

        return solution

    if not quiet:
        print("The problem does not have an optimal solution.")

    return None


def n_bins_to_pack_ortools(graph: nx.Graph, bin_size: int) -> int:
    """ Auxiliary function to get the number of bins of size bin_size needed to
    pack the connected components of the given graph using the OR-Tools
    library. """

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
    solver.Minimize(sum([y[j] for j in range(len(graph.nodes()))]))

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


def n_bins_to_pack_gurobi(graph: nx.Graph, bin_size: int) -> int:
    """ Auxiliary function to get the number of bins of size bin_size needed to
    pack the connected components of the given graph using the Gurobi
    library. """

    # Create a new model.
    model = Model()
    model.Params.OutputFlag = 0

    # Variables
    # x[i, j] = 1 if item i is packed in bin j.
    x = {}
    for i in graph.nodes():
        for j in range(len(graph.nodes())):
            x[(i, j)] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")

    # y[j] = 1 if bin j is used.
    y = {}
    for j in range(len(graph.nodes())):
        y[j] = model.addVar(vtype=GRB.BINARY, name=f"y[{j}]")

    # Constraints
    # Each item must be in exactly one bin.
    for i in graph.nodes():
        model.addConstr(sum(x[i, j] for j in range(len(graph.nodes()))) == 1)

    # The amount packed in each bin cannot exceed its capacity.
    for j in range(len(graph.nodes())):
        model.addConstr(
            sum(x[(i, j)] for i in graph.nodes()) <= y[j] * bin_size)

    # Objective: minimize the number of bins used.
    model.setObjective(sum([y[j] for j in range(len(graph.nodes()))]),
                       GRB.MINIMIZE)

    # Solve the system.
    model.optimize()

    # Print and Parse the solution found.
    if STATUS_DICT[model.status] == "OPTIMAL":
        num_bins = 0

        for j in range(len(graph.nodes())):
            if y[j].x == 1:
                bin_items = []
                bin_weight = 0

                for i in graph.nodes():
                    if x[i, j].x > 0:
                        bin_items.append(i)
                        bin_weight += 1

                if bin_weight > 0:
                    num_bins += 1

    else:
        num_bins = inf

    return num_bins
