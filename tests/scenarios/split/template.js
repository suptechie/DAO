var dao_abi = $dao_abi;
var dao = web3.eth.contract(dao_abi).at('$dao_address');
var newCurator = eth.accounts[1];

var prop_id = attempt_proposal(
    dao, // DAO in question
    newCurator, // recipient
    proposalCreator, // proposal creator
    0, // proposal amount in ether
    'Voting to split and change Curator', // description
    '', //bytecode
    $debating_period, // debating period
    0, // proposal deposit in ether
    true // whether it's a split proposal or not
);

var votes = $votes;
console.log("Voting for split proposal '" + prop_id + "' ...");
for (i = 0; i < votes.length; i++) {
    dao.vote.sendTransaction(
        prop_id,
        votes[i],
        {
            from: eth.accounts[i],
            gas: 1000000
        }
    );
}
checkWork();
addToTest('proposal_yay', parseInt(web3.fromWei(dao.proposals(prop_id)[9])));
addToTest('proposal_nay', parseInt(web3.fromWei(dao.proposals(prop_id)[10])));

setTimeout(function() {
    miner.stop(0);
    console.log("Executing the split proposal...");
    // now each user who voted for the split should call splitDAO to execute the proposal
    for (i = 0; i < votes.length; i++) {
        if (votes[i]) {
            dao.splitDAO.sendTransaction(
                prop_id,
                newCurator,
                {from:eth.accounts[i], gas: $split_gas}
            );
        }
    }
    checkWork();
    console.log("After split execution");
    addToTest('proposal_passed', dao.proposals(prop_id)[5]);
    addToTest('proposal_newdao', dao.splitProposalNewAddress(prop_id, 0));

    var newdao = web3.eth.contract(dao_abi).at(testMap['proposal_newdao']);
    // check token balance of each user in both DAOs
    oldDAOBalance = [];
    newDAOBalance = [];
    for (i = 0; i < eth.accounts.length; i++) {
        oldDAOBalance.push(parseInt(web3.fromWei(dao.balanceOf(eth.accounts[i]))));
        newDAOBalance.push(parseInt(web3.fromWei(newdao.balanceOf(eth.accounts[i]))));
    }
    addToTest('oldDAOBalance', oldDAOBalance);
    addToTest('newDAOBalance', newDAOBalance);
    addToTest('oldDaoRewardTokens', parseFloat(web3.fromWei(dao.rewardToken('$dao_address'))));
    addToTest('newDaoRewardTokens', parseFloat(web3.fromWei(dao.rewardToken(testMap['proposal_newdao']))));

    addToTest('newDAOTotalSupply', parseInt(web3.fromWei(newdao.totalSupply())));
    addToTest('newDAOProposalDeposit', parseInt(web3.fromWei(newdao.proposalDeposit())));

    testResults();
}, $debating_period * 1000);
console.log("Wait for end of debating period");
