var dao = web3.eth.contract($dao_abi).at('$dao_address');
var offer = web3.eth.contract($offer_abi).at('$offer_address');

var dao_rewardaccount_before = eth.getBalance(dao.DAOrewardAccount());
var dao_balance_before = eth.getBalance(dao.address);

// The DAO will now make a proposal to attempt to pay its own rewards
var prop_id = attempt_proposal(
    dao, // DAO in question
    '$offer_address', // recipient
    proposalCreator, // proposal creator
    10, // proposal amount in ether
    'Attempt to pay the offer ourselves and send indirectly money to our own reward account', // description
    '$transaction_bytecode', //bytecode
    $debating_period, // debating period
    $proposal_deposit, // proposal deposit in ether
    false // whether it's a split proposal or not
);


console.log("Voting for the proposal to set the Daily withdraw limit");
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
        proposalCreator, // proposal creator
        false, // should the proposal be closed after this call?
        false // should the proposal pass?
    );

    var dao_rewardaccount_after = eth.getBalance(dao.DAOrewardAccount());
    var dao_balance_after = eth.getBalance(dao.address);

    addToTest('dao_rewardaccount_diff', dao_rewardaccount_after.sub(dao_rewardaccount_before));
    addToTest('dao_balance_diff', dao_balance_after.sub(dao_balance_before));

    testResults();
}, $debating_period * 1000);
console.log("Wait for end of debating period");
miner.start(1);
