var dao = web3.eth.contract($dao_abi).at('$dao_address');

addToTest('dao_total_balance_before', web3.fromWei(eth.getBalance(dao.address)));

var prop_id = attempt_proposal(
    dao, // DAO in question
    curator, // recipient
    proposalCreator, // proposal creator
    web3.fromWei(dao.totalSupply())-10, // proposal amount in ether
    'Spend almost all of the DAOs money', // description
    '', //bytecode
    $debating_period, // debating period
    $proposal_deposit, // proposal deposit in ether
    false // whether it's a split proposal or not
);


console.log("Deadline is: " + dao.proposals(prop_id)[3] + " Voting ... ");
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
    console.log("After spending debating period. NOW is: " + Math.floor(Date.now() / 1000));
    attempt_execute_proposal(
        dao, // target DAO
        prop_id, // proposal ID
        '', // transaction bytecode
        proposalCreator, // proposal creator
        true // should the proposal pass?
    );

    addToTest('dao_total_balance_after_spend', web3.fromWei(dao.actualBalance()));

    var extraBalance = dao.extraBalance();
    var claim_prop_id = attempt_proposal(
        dao, // DAO in question
        extraBalance, // recipient
        proposalCreator, // proposal creator
        0, // proposal amount in ether
        'Ask the extraBalance account to pay out to the DAO', // description
        '$transaction_bytecode', // transaction bytecode
        $debating_period, // debating period
        $proposal_deposit, // proposal deposit in ether
        false // whether it's a split proposal or not
    );
    console.log("Voting on the extra balance payout proposal");
    for (i = 0; i < eth.accounts.length; i++) {
        dao.vote.sendTransaction(
            claim_prop_id,
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
        console.log("After extra balance payout debating period. NOW is: " + Math.floor(Date.now() / 1000));
        attempt_execute_proposal(
            dao, // target DAO
            claim_prop_id, // proposal ID
            '$transaction_bytecode', // transaction bytecode
            proposalCreator, // proposal creator
            true // should the proposal pass?
        );

        addToTest('dao_total_balance_after_claim', web3.fromWei(dao.actualBalance()));
        addToTest('dao_balance_diff_after_claim',
                  testMap['dao_total_balance_after_claim'].sub(
                      testMap['dao_total_balance_after_spend']
                  ).round());

        testResults();
    }, ($debating_period + 1) * 1000);
    console.log("Wait for end of debating period for claiming extraBalance payout");
    miner.start(1);
}, ($debating_period + 1) * 1000);
console.log("Wait for end of debating period for spending all of the DAO's money");
miner.start(1);
