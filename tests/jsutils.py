#!/usr/bin/python2


def js_common_intro(accounts_num):
    """Common  functions, variables to add to all js scripts"""
    s = "console.log('unlocking accounts');\n"
    for i in range(0, accounts_num):
        s += "personal.unlockAccount(eth.accounts[{}], '123');\n".format(i)
    s += """// set the basic accounts, coinbase should be random so mining rewards don't pollute results
var curator = eth.accounts[0];
var proposalCreator = eth.accounts[1];
var etherBase = '0x9999999999999999999999999999999999999999';
web3.miner.setEtherbase(etherBase);

var testMap = {};

function checkWork() {
    miner.start(1);
    admin.sleepBlocks(3);
    miner.stop(0);
}

function bigDiff(astr, bstr) {
    return new BigNumber(astr).minus(new BigNumber(bstr));
}

function bigDiffRound(astr, bstr) {
    return Math.round(bigDiff(astr, bstr));
}

function addToTest(name, value) {
    testMap[name] = value;
    console.log("'" + name + "' = " + value);
}

function testResults() {
    console.log("Test Results: " + JSON.stringify(testMap));
}
"""
    return s
