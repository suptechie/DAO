import json
import subprocess

contracts_dir = "../"


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
    comp = compile_contract("/usr/bin/solc", "../DAO.sol")

    with open("code.js", "w") as f:
        f.write("dao_abi = {}\n".format(comp['contracts']['DAO']['abi']))
        f.write("dao_bin = '{}'\n".format(comp['contracts']['DAO']['bin']))
        f.write("creator_abi = {}\n".format(
          comp['contracts']['DAO_Creator']['abi'])
        )
        f.write("creator_bin = '{}'\n".format(
          comp['contracts']['DAO_Creator']['bin'])
        )
