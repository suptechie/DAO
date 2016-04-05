#!/usr/bin/python2

import json
import subprocess
import argparse
import os
import inspect

contracts_dir = "../"
currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
os.sys.path.insert(0, os.path.dirname(currentdir))
from tests.utils import determine_binary


def compile_contract(solc, contract_path):
    print("    Compiling {}...".format(contract_path))
    data = subprocess.check_output([
      solc,
      contract_path,
      "--optimize",
      "--combined-json",
      "abi,bin"
    ])
    return json.loads(data)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description='DAO deployment script')
    p.add_argument(
        '--solc',
        help='Full path to the solc binary to use'
    )
    args = p.parse_args()
    solc = determine_binary(args.solc, 'solc')
    comp = compile_contract(solc, "../DAO.sol")

    with open("code.js", "w") as f:
        f.write("dao_abi = {};\n".format(comp['contracts']['DAO']['abi']))
        f.write("dao_bin = '{}';\n".format(comp['contracts']['DAO']['bin']))
        f.write("creator_abi = {};\n".format(
          comp['contracts']['DAO_Creator']['abi'])
        )
        f.write("creator_bin = '{}';\n".format(
          comp['contracts']['DAO_Creator']['bin'])
        )
