var dao = web3.eth.contract($dao_abi).at('$dao_address');

// No need to have an actual contract for the purpose of the test
var newContract = '$new_contract_address';
addToTest('new_contract_balance_before', web3.fromWei(eth.getBalance(newContract)));
addToTest('dao_balance_before', web3.fromWei(eth.getBalance(dao.address)));
addToTest('dao_reward_token_before', web3.fromWei(dao.rewardToken(dao.address)));
addToTest('new_contract_reward_token_before', web3.fromWei(dao.rewardToken(newContract)));
console.log("Add new contract as allowed recipient");
dao.changeAllowedRecipients.sendTransaction(newContract, true, {from: curator, gas: 1000000});
checkWork();

console.log("Create the proposal to update");
dao.newProposal.sendTransaction(
    dao.address,
    web3.toWei(0, "ether"),
    'Move all funds to a new contract',
    '$transaction_bytecode',
    $debating_period,
    false,
    {
        from: proposalCreator,
        value: web3.toWei($proposal_deposit, "ether"),
        gas: 1000000
    }
);
checkWork();

console.log("Vote on the proposal to update");
var prop_id = $prop_id;
for (i = 0; i < eth.accounts.length; i++) {
    dao.vote.sendTransaction(
        prop_id,
        true,
        {
            from: eth.accounts[i],
            gas: 4000000
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

    addToTest('new_contract_balance_after', web3.fromWei(eth.getBalance(newContract)));
    addToTest('dao_balance_after', web3.fromWei(eth.getBalance(dao.address)));
    addToTest('dao_reward_token_after', web3.fromWei(dao.rewardToken(dao.address)));
    addToTest('new_contract_reward_token_after', web3.fromWei(dao.rewardToken(newContract)));

    addToTest('new_contract_balance', bigDiff(
        testMap['new_contract_balance_after'],
        testMap['new_contract_balance_before']
    ));
    addToTest(
        'money_transferred',
        testMap['new_contract_balance'].ceil().equals(testMap['dao_balance_before'].ceil())
    );
    addToTest(
        'reward_tokens_transferred',
        testMap['new_contract_reward_token_after'].ceil().equals(testMap['dao_reward_token_before'].ceil())
    );


    testResults();
}, $debating_period * 1000);
console.log("Wait for end of debating period");
miner.start(1);
