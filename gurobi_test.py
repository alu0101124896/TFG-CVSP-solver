#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" This program is used to test the functionalities of the Gurobi Optimization
library. """

import random
import sys

import gurobipy as gp
from gurobipy import GRB
import networkx


def main():
    """ Main functionto start the test/s. """

    # test_1()
    # test_2()
    test_3()


def test_1():
    """ Gurobi sample. """

    try:
        # Create a new model
        model = gp.Model("mip1")
        model.Params.OutputFlag = 0

        # Create the variables
        x = model.addVar(vtype=GRB.BINARY, name="x")
        y = model.addVar(vtype=GRB.BINARY, name="y")
        z = model.addVar(vtype=GRB.BINARY, name="z")

        # Set the objective
        model.setObjective(x + y + 2 * z, GRB.MAXIMIZE)

        # Add constraint: x + 2 y + 3 z <= 4
        model.addConstr(x + 2 * y + 3 * z <= 4, "c0")

        # Add constraint: x + y >= 1
        model.addConstr(x + y >= 1, "c1")

        # Optimize model
        model.optimize()

        # Print solution found
        print(f"\nOptimal objective value = {model.objVal}")
        for variable in model.getVars():
            print(f"  {variable.varName} = {variable.x}")

        print(f"\nSolution found in {model.Runtime} seconds")

    except gp.GurobiError as err:
        sys.exit(f"Error code {str(err.errno)}: {str(err)}")

    except AttributeError:
        sys.exit("Encountered an attribute error")


def test_2():
    """ Teacher's sample. """

    model = gp.Model("ProblemaEnteroDificil")
    model.Params.OutputFlag = 0

    x = model.addVar(vtype=GRB.INTEGER, name="x")
    y = model.addVar(vtype=GRB.INTEGER, name="y")
    z = model.addVar(vtype=GRB.INTEGER, name="z")

    model.setObjective(x, GRB.MINIMIZE)
    model.addConstr(75001 * y + 75002 * z == 75000 + 75000 * x, "c0")
    model.optimize()

    print(f"\nOptimal objective value = {model.objVal}")
    for variable in model.getVars():
        print(f"  {variable.varName} = {variable.x}")

    print(f"\nSolution found in {model.Runtime} seconds")


def test_3():
    """ Teacher's dynamic row generation sample. """

    n = 5
    todos = range(n)
    EPS = 0.001

    random.seed(12345)
    dist = {(i, j): random.randint(1, 100)
            for i in todos for j in todos if i != j}

    model = gp.Model()
    model.Params.OutputFlag = 0
    x = model.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name="a")

    def atsp_sec():
        """ Main level function for the dynamic row generation. """

        model.addConstrs(
            sum(x[i, j] for j in todos if j != i) == 1 for i in todos)
        model.addConstrs(
            sum(x[j, i] for j in todos if j != i) == 1 for i in todos)

        model.optimize()
        while sec():
            model.optimize()

    def sec():
        """ Second level function for the dynamic row generation. """

        vals = model.getAttr("x", x)

        G = networkx.Graph()
        G.add_edges_from((i, j) for i, j in vals.keys() if vals[i, j] > EPS)
        components = list(networkx.connected_components(G))

        if len(components) == 1:
            return False

        for S in components:
            model.addConstr(
                gp.quicksum(x[i, j] for i in S for j in S if j != i) < len(S))

        return True

    atsp_sec()

    print(f"\nOptimal cost = {model.objVal}")
    vals = model.getAttr("x", x)
    selected = [(i, j) for i, j in vals.keys() if vals[i, j] > EPS]
    print(f"Optimal path: {str(selected)}")

    print(f"\nSolution found in {model.Runtime} seconds")


if __name__ == "__main__":
    main()
