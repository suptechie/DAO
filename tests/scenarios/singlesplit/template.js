var dao = web3.eth.contract($dao_abi).at('$dao_address');
var newServiceProvider = eth.accounts[1];


console.log("Our disgruntled user is creating proposal to change SP to itself...");
var tx_hash = null;
dao.newProposal.sendTransaction(
    newServiceProvider, // new SP
    0,
    'eth.accounts[1] wants to split out',
    '',
    $debating_period,
    true,
    {
        from: newServiceProvider,
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
console.log("Voting for split proposal '" + prop_id + "' ...");
for (i = 0; i < eth.accounts.length; i++) {
    dao.vote.sendTransaction(
        prop_id,
        i == 1 ? true : false,
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
    // now our disgruntled user is the only one to execute the splitDAO function
    dao.splitDAO.sendTransaction(
        prop_id,
        newServiceProvider,
        {from:newServiceProvider, gas: $split_gas}
    );
    checkWork();
    console.log("After split execution");
    addToTest('proposal_passed', dao.proposals(prop_id)[5]);
    addToTest('proposal_newdao', dao.splitProposalNewAddress(prop_id, 0));

    var newdao = web3.eth.contract($dao_abi).at(testMap['proposal_newdao']);
    // check token balance of each user in both DAOs
    oldDAOBalance = [];
    newDAOBalance = [];
    for (i = 0; i < eth.accounts.length; i++) {
        oldDAOBalance.push(parseInt(web3.fromWei(dao.balanceOf(eth.accounts[i]))));
        newDAOBalance.push(parseInt(web3.fromWei(newdao.balanceOf(eth.accounts[i]))));
    }
    addToTest('oldDAOBalance', oldDAOBalance);
    addToTest('newDAOBalance', newDAOBalance);
    addToTest('newDAOTotalSupply', parseInt(web3.fromWei(newdao.totalSupply())));

    setTimeout(function() {
        // now our disgruntled user has his own DAO and is the SP of that DAO so ...
        console.log("Angry user proposes to his own DAO to send all funds to himself...");
        newdao.newProposal.sendTransaction(
            newServiceProvider,
            newdao.totalSupply(),
            'Send all money to myself!! Screw you guys ... I am going home!',
            '0x0', // bytecode, not needed here, calling the fallback function
            $debating_period,
            false,
            {
                from: newServiceProvider,
                value: web3.toWei($proposal_deposit, "ether"),
                gas: 1000000
            }
            , function (e, res) {
                if (e) {
                    console.log(e + "at newProposal()!");
                } else {
                    tx_hash = res;
                    console.log("SOLO MOVE proposal tx hash is: " + tx_hash);
                }
            }
        );
        checkWork();
        console.log("Angry user votes in his own DAO...");
        newdao.vote.sendTransaction(
            1,
            true,
            {
                from: newServiceProvider,
                gas: 1000000
            }
        );
        checkWork();
        addToTest('newdao_proposals_num', newdao.numberOfProposals());
        addToTest('angry_user_before', web3.fromWei(eth.getBalance(newServiceProvider)));
        setTimeout(function() {
            addToTest('newdao_proposal_passed', newdao.proposals(1)[5]);
            // now execute the proposal
            newdao.executeProposal.sendTransaction(1, '0x0', {from:newServiceProvider, gas:1000000});
            checkWork();
            addToTest('angry_user_after', web3.fromWei(eth.getBalance(newServiceProvider)));
            addToTest(
                'angry_user_profit',
                bigDiffRound(testMap['angry_user_after'], testMap['angry_user_before'])
            );
            testResults();
        }, $debating_period * 1000);
        console.log("Wait for end of second debating period");
    }, 20 * 1000);
    console.log("Wait for new DAO funding period to end");
}, $debating_period * 1000);
console.log("Wait for end of first debating period");
