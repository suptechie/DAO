var dao = web3.eth.contract($dao_abi).at('$dao_address');
dao.newProposal.sendTransaction(
    '$dao_address',
    web3.toWei(0, "ether"),
    'Changing proposal deposit',
    '$transaction_bytecode',
    $debating_period,
    false,
    {
        from: proposalCreator,
        value: web3.toWei($proposal_deposit, "ether"),
        gas: 1000000
    }
    , function (e, res) {
        if (e) {
            console.log(e + "at newProposal()!");
        } else {
            tx_hash = res;
            console.log("newProposal tx hash is: " + tx_hash);
        }
    }
);
checkWork();

var prop_id = $prop_id;

// in this scenario all users vote for the change
for (i = 0; i < eth.accounts.length; i++) {
    dao.vote.sendTransaction(
        prop_id,
        true,
        {
            from: eth.accounts[i],
            gas: 1000000
        }
    );
}
checkWork();
setTimeout(function() {
    miner.stop(0);
    console.log("Executing proposal ...");
    dao.executeProposal.sendTransaction(prop_id, '$transaction_bytecode', {from:curator, gas:1000000});
    checkWork();

    addToTest('proposal_passed', dao.proposals(prop_id)[5]);
    addToTest('deposit_after_vote', parseInt(dao.proposalDeposit()));
    testResults();
}, $debating_period * 1000);
miner.start(1);
