# Scripts for DAO deployment using geth

## Introduction

`prepare.py` compiles `DAO.sol` and populates some helper variables inside `prepare.js`

1. `loadScript("prepare.js")` loads these variables into geth.
2. `loadScript("deploy.js")` deploys them.

## Example usage

At the moment of writting of this README the usage of the prepare script is:

```
usage: prepare.py [-h] [--solc SOLC] [--sale-duration-mins SALE_DURATION_MINS]

DAO deployment script

optional arguments:
  -h, --help            show this help message and exit
  --solc SOLC           Full path to the solc binary to use
  --sale-duration-mins SALE_DURATION_MINS
                        Deployed DAO sale duration in minutes
```

You can for example call the script with a specifically compiled solc and set
the sale to end in 15 mins by doing:

```
./prepare.py --solc ~/ew/solidity/build/solc/solc --sale-duration-mins 15
```
