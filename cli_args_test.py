#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" Program to test command line arguments' recognition. """

import argparse


def main():
    """ Entry point to the main program. """

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
                        help="select a formulation to use")

    parser.add_argument("--no-gui",
                        action="store_true",
                        help="do NOT output the solution graphically")
    parser.add_argument("-q",
                        "--quiet",
                        action="store_true",
                        help="suppress all normal output")

    # Read arguments from command line
    args = parser.parse_args()

    if args.input_file:
        print(f"Loading graph from {args.input_file} file.")
    if args.output_file:
        print(f"Exporting solution to {args.output_file} file.")

    if args.k_value:
        print(f"k={args.k_value}")
    if args.b_value:
        print(f"b={args.b_value}")
    if args.formulation:
        print(f"Formulation to be used: {args.formulation}.")

    if not args.no_gui:
        print("Show matplotlib window")
    if not args.quiet:
        print("Solution: {'S': ['v8', 'v9']}")


if __name__ == "__main__":
    main()
