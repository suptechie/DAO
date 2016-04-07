var dao = web3.eth.contract($dao_abi).at('$dao_address');

// some kind soul makes a donation to the DAO, so rewards get populated
console.log("Donating to DAO...");
eth.sendTransaction({
    from:eth.accounts[1],
    to: dao.DAOrewardAccount(),
    gas: 210000,
    value: web3.toWei($total_rewards, "ether")
});
checkWork();

// create a new proposal for sending this whole donation to the rewardAccount
console.log("Creating proposal to send to rewardAccount...");
var tx_hash = null;
dao.newProposal.sendTransaction(
    '$dao_address',
    0,
    'Ask the DAO to retrieveDAOReward()',
    '$transaction_bytecode',
    $debating_period,
    false,
    {
        from: proposalCreator,
        value: web3.toWei($proposal_deposit + 1, "ether"),
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
console.log("Voting for proposal '" + prop_id + "' ...");
// in this scenario let's just say everyone votes 100% in favour
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
    console.log("Executing the proposal...");
    // now execute the proposal
    dao.executeProposal.sendTransaction(prop_id, '$transaction_bytecode', {from:serviceProvider, gas:1000000});
    checkWork();
    addToTest('provider_balance_before_claim', eth.getBalance(serviceProvider));
    console.log("Claiming the reward...");
    dao.getMyReward.sendTransaction({from: serviceProvider, gas: 1000000});
    checkWork();
    addToTest('provider_balance_after_claim', eth.getBalance(serviceProvider));
    addToTest(
        'provider_reward_portion',
        parseFloat(web3.fromWei(bigDiff(
            testMap['provider_balance_after_claim'], testMap['provider_balance_before_claim']
        )))
    );
    addToTest('DAO_balance', parseFloat(web3.fromWei(eth.getBalance('$dao_address'))));
    addToTest('DAO_rewardToken', parseFloat(web3.fromWei(dao.rewardToken('$dao_address'))));
    testResults();
}, $debating_period * 1000);
console.log("Wait for end of debating period");
