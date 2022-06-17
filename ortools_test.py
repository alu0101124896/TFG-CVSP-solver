#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from ortools.linear_solver import pywraplp


def main():
    """ Main function. """
    # linear_programming()
    integer_programming()


def linear_programming():
    """ Linear programming sample. """

    # Instantiate a Glop solver, naming it LinearExample.
    solver = pywraplp.Solver.CreateSolver("GLOP")
    assert isinstance(solver, pywraplp.Solver)

    # Create the two variables and let them take on any non-negative value.
    x_var = solver.NumVar(0, solver.infinity(), 'x')
    y_var = solver.NumVar(0, solver.infinity(), 'y')
    assert isinstance(x_var, pywraplp.Variable)
    assert isinstance(y_var, pywraplp.Variable)

    # Constraint 0: x + 2y <= 14.
    solver.Add(x_var + 2 * y_var <= 14.0)

    # Constraint 1: 3x - y >= 0.
    solver.Add(3 * x_var - y_var >= 0.0)

    # Constraint 2: x - y <= 2.
    solver.Add(x_var - y_var <= 2.0)

    print("\nProblem definition:")
    print("  Number of variables =", solver.NumVariables())
    print("  Number of constraints =", solver.NumConstraints())

    # Objective function: Max 3x + 4y.
    solver.Maximize(3 * x_var + 4 * y_var)

    # Solve the system.
    status = solver.Solve()

    # Display the solution
    if status == pywraplp.Solver.OPTIMAL:
        objective = solver.Objective()
        assert isinstance(objective, pywraplp.Objective)
        print("\nSolution:")
        print("  Objective value =", objective.Value())
        print("  x =", x_var.solution_value())
        print("  y =", y_var.solution_value())
    else:
        print("The problem does not have an optimal solution.")

    print("\nAdvanced usage:")
    print(f"  Problem solved in {solver.wall_time()} milliseconds")
    print(f"  Problem solved in {solver.iterations()} iterations")


def integer_programming():
    """ Integer programming sample. """

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")
    assert isinstance(solver, pywraplp.Solver)

    # x and y are integer non-negative variables.
    infinity = solver.infinity()
    x_var = solver.IntVar(0, infinity, '')
    y_var = solver.IntVar(0, infinity, '')
    assert isinstance(x_var, pywraplp.Variable)
    assert isinstance(y_var, pywraplp.Variable)

    # Constraint 0: x + 7 * y <= 17.5.
    solver.Add(x_var + 7 * y_var <= 17.5)

    # Constraint 1: x <= 3.5.
    solver.Add(x_var <= 3.5)

    print("\nProblem definition:")
    print("  Number of variables =", solver.NumVariables())
    print("  Number of constraints =", solver.NumConstraints())

    # Objective function: Max x + 10 * y.
    solver.Maximize(x_var + 10 * y_var)

    # Solve the system.
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        objective = solver.Objective()
        assert isinstance(objective, pywraplp.Objective)
        print("\nSolution:")
        print("  Objective value =", objective.Value())
        print("  x =", x_var.solution_value())
        print("  y =", y_var.solution_value())
    else:
        print("The problem does not have an optimal solution.")

    print("\nAdvanced usage:")
    print(f"  Problem solved in {solver.wall_time()} milliseconds")
    print(f"  Problem solved in {solver.iterations()} iterations")
    print(f"  Problem solved in {solver.nodes()} branch-and-bound nodes")


if __name__ == "__main__":
    main()
