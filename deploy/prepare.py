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
from tests.utils import determine_binary, edit_dao_source, rm_file


class TestDeployContext():
    def __init__(self, args):
        self.args = args
        self.args.solc = determine_binary(args.solc, 'solc')

    def compile_contract(self, contract_name):
        if self.args.no_limits:
            contract_path = edit_dao_source(
                self.args.contracts_dir,
                False,
                True
            )
        else:
            contract_path = os.path.join(
                self.args.contracts_dir,
                contract_name
            )
        print("    Compiling {}...".format(contract_path))
        data = subprocess.check_output([
          self.args.solc,
          contract_path,
          "--optimize",
          "--combined-json",
          "abi,bin"
        ])
        return json.loads(data)

    def cleanup(self):
        if self.args.no_limits:
            rm_file(os.path.join(self.args.contracts_dir, "DAOcopy.sol"))
            rm_file(os.path.join(self.args.contracts_dir, "TokenSaleCopy.sol"))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description='DAO deployment script')
    p.add_argument(
        '--solc',
        help='Full path to the solc binary to use'
    )
    p.add_argument(
        '--sale-duration-mins',
        type=int,
        default=60,
        help='Deployed DAO sale duration in minutes'
    )
    p.add_argument(
        '--contracts-dir',
        default="..",
        help='The directory where the contracts are located'
    )
    p.add_argument(
        '--no-limits',
        action='store_true',
        help='If given then a version of DAO.sol without limits is compiled'
    )
    p.add_argument(
        '--service-provider',
        default="0x08144824954c65b12f68b75072488e634ac4e67a",  # Griff testnet
        help='Account to set as service provider'
    )
    p.add_argument(
        '--default-proposal-deposit',
        type=int,
        default=10,
        help='The proposal deposit (in ether) for every proposal of the DAO'
    )
    args = p.parse_args()
    ctx = TestDeployContext(args)
    comp = ctx.compile_contract("DAO.sol")

    with open("prepare.js", "w") as f:
        f.write("dao_abi = {};\n".format(comp['contracts']['DAO']['abi']))
        f.write("dao_bin = '{}';\n".format(comp['contracts']['DAO']['bin']))
        f.write("creator_abi = {};\n".format(
          comp['contracts']['DAO_Creator']['abi'])
        )
        f.write("creator_bin = '{}';\n".format(
          comp['contracts']['DAO_Creator']['bin'])
        )
        f.write("seconds_from_now = {};\n".format(
          args.sale_duration_mins * 60)
        )
        f.write("service_provider = \"{}\";\n".format(args.service_provider))
        f.write("default_proposal_deposit = {};\n".format(
            args.default_proposal_deposit)
        )

    ctx.cleanup()
