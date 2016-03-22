#!/usr/bin/python2
import argparse
import sys
import os
import json


def available_scenarios():
    dir = "scenarios"
    return [name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name))]


def read_scenario_options(args):
    """ Iterate scenarios and load all argument options """
    dir = "scenarios"
    for name in os.listdir(dir):
        argfile = os.path.join(dir, name, "arguments.json")
        if os.path.isfile(argfile):
            with open(argfile, 'r') as f:
                data = json.loads(f.read())

            for arg in data:
                args.add_argument(
                    "--{}-{}".format(name, arg['name']).replace("_", "-"),
                    help=arg['description'],
                    default=arg['default']
                )


def test_args():
    """ Parse the test arguments and create and return the arguments object"""
    p = argparse.ArgumentParser(description='DAO contracts test framework')
    read_scenario_options(p)

    p.add_argument(
        '--solc',
        help='Full path to the solc binary to use'
    )
    p.add_argument(
        '--geth',
        help='Full path to the geth binary to use'
    )
    p.add_argument(
        '--keep-limits',
        action='store_true',
        help=(
            'If given then the debate limits of the original '
            'contracts will not be removed'
        )
    )
    p.add_argument(
        '--clean-chain',
        action='store_true',
        help=(
            'If given then the blockchain is deleted before any '
            'test scenario is executed'
        )
    )
    p.add_argument(
        '--verbose',
        action='store_true',
        help='If given then all test checks are printed in the console'
    )
    p.add_argument(
        '--proposal-fail',
        action='store_true',
        help='If given, then in the proposal scenario the voting will fail'
    )
    p.add_argument(
        '--users-num',
        type=int,
        help='The number of user accounts to create for the scenarios.'
        'Should be at least 3',
        default=5
    )
    p.add_argument(
        '--scenario',
        choices=['none'] + available_scenarios(),
        default='none',
        help='Test scenario to play out'
    )
    args = p.parse_args()

    # Argument verification
    if args.users_num < 3:
        print("ERROR: Tests need 3 or more users")
        sys.exit(1)

    return args
