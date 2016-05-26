var dao_abi = $dao_abi;
var dao = eth.contract(dao_abi).at('$dao_address');
var child_dao = eth.contract(dao_abi).at('$child_dao_address');
var child_curator = '$child_dao_curator';
var child_dao_members = $child_dao_members;
var offer = web3.eth.contract($offer_abi).at('$offer_address');

// The DAO will now propose for the child DAO to be the new client
var prop_id = attempt_proposal(
    dao, // DAO in question
    '$offer_address', // recipient
    curator, // proposal creator
    0, // proposal amount in ether
    'Change the client of this Sampleoffer', // description
    '$transaction_bytecode', //bytecode
    $debating_period, // debating period
    $proposal_deposit, // proposal deposit in ether
    false // whether it's a split proposal or not
);

console.log("Voting for the proposal to change client");
for (i = 0; i < eth.accounts.length; i++) {
    dao.vote.sendTransaction(
        prop_id,
        true, //omg it's unanimous!
        {
            from: eth.accounts[i],
            gas: 1000000
        }
    );
}
checkWork();

setTimeout(function() {
    miner.stop();
    console.log("After debating period. NOW is: " + Math.floor(Date.now() / 1000));
    attempt_execute_proposal(
        dao, // target DAO
        prop_id, // proposal ID
        '$transaction_bytecode', // transaction bytecode
        curator, // proposal creator
        true, // should the proposal be closed after this call?
        true // should the proposal pass?
    );

    addToTest('offer_original_client', offer.originalClient());
    addToTest('offer_client', offer.client());

    console.log("Add offer contract as allowed recipient for the Child DAO");
child_dao.changeAllowedRecipients.sendTransaction('$offer_address', true, {from: child_curator, gas: 1000000});

    // now test that the split DAO can't pay its own rewards
    // The DAO will now propose for the child DAO to be the new client
    var bad_prop_id = attempt_proposal(
        child_dao, // DAO in question
        '$offer_address', // recipient
        child_curator, // proposal creator
        2, // proposal amount in ether
        'Try to payReward() on the offer as a split DAO who is the new client', // description
        '$pay_reward_bytecode', //bytecode
        $debating_period, // debating period
        $proposal_deposit, // proposal deposit in ether
        false // whether it's a split proposal or not
    );

    console.log("Voting for the proposal to try and pay our own rewards as a split");
    for (i = 0; i < child_dao_members.length; i++) {
        dao.vote.sendTransaction(
            bad_prop_id,
            true, //omg it's unanimous!
            {
                from: child_dao_members[i],
                gas: 1000000
            }
        );
    }
    checkWork();

    setTimeout(function() {
        miner.stop();
        console.log("original DAO reward tokens: " + dao.rewardToken(dao.address));
        console.log("Split DAO reward tokens: " + dao.rewardToken(child_dao.address));
        var dao_rewardaccount_before = eth.getBalance(dao.DAOrewardAccount());
        attempt_execute_proposal(
            child_dao, // target DAO
            bad_prop_id, // proposal ID
            '$pay_reward_bytecode', // transaction bytecode
            child_curator, // proposal creator
            true, // should the proposal be closed after this call?
            false // should the proposal pass?
        );
        var dao_rewardaccount_after = eth.getBalance(dao.DAOrewardAccount());
        addToTest('dao_rewardaccount_diff', dao_rewardaccount_after.sub(dao_rewardaccount_before));

        testResults();
    }, $debating_period * 1000);
    miner.start(1);
    console.log("Wait for end of 2nd debating period");
}, $debating_period * 1000);
miner.start(1);
console.log("Wait for end of debating period");
