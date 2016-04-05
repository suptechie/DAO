

import os 
import pdb
import json
import subprocess

contracts_dir= "../"

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

comp =compile_contract("/usr/bin/solc", "../DAO.sol" )

with open("code.js", "w") as f:
  f.write("dao_abi =" + comp['contracts']['DAO']['abi'])
  f.write("dao_bin = '" + comp['contracts']['DAO']['bin']+ "'\n")
  f.write("creator_abi =" + comp['contracts']['DAO_Creator']['abi'])
  f.write("creator_bin = '" + comp['contracts']['DAO_Creator']['bin'] + "'\n")


