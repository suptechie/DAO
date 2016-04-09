var dao = web3.eth.contract($dao_abi).at('$dao_address');

var attacker = eth.accounts[2];
addToTest('attacker_balance_before', web3.fromWei(eth.getBalance(attacker)));
addToTest('attacker_dao_balance_before', web3.fromWei(dao.balanceOf(attacker)));

// add SP to the whitelist
dao.addAllowedAddress.sendTransaction(serviceProvider, {from:serviceProvider, gas:200000});

console.log("Making the attack proposal");
var attack_proposal_id = $attack_proposal_id;
var tx_hash = null;
dao.newProposal.sendTransaction(
    serviceProvider, // only address currently in the whitelist
    web3.toWei(0, "ether"), // irrelevant
    'The colm attack proposal with a big deposit',
    '',
    $attack_debating_period,
    false,
    {
        from: attacker,
        value: web3.toWei($attack_deposit, "ether"), // big deposit
        gas: 4000000
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
console.log("After attack proposal. Proposals Number: " + dao.numberOfProposals());
console.log("Making the split proposal");
var split_proposal_id = attack_proposal_id + 1;
dao.newProposal.sendTransaction(
    attacker, // new SP
    0,
    'attacker wants to split out',
    '',
    $split_debating_period,
    true,
    {
        from: attacker,
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
console.log("After split proposal. Proposals Number: " + dao.numberOfProposals());

console.log("Vote on proposals");
// everyone votes on the attack proposal
for (i = 0; i < eth.accounts.length; i++) {
    dao.vote.sendTransaction(
        attack_proposal_id,
        true,
        {
            from: eth.accounts[i],
            gas: 1000000
        }
    );
}
// our attacker also votes on his split
dao.vote.sendTransaction(split_proposal_id, true, {from: attacker, gas: 1000000});
checkWork();


setTimeout(function() {
    miner.stop(0);
    console.log("Attack debate period over.");

    setTimeout(function() {
        miner.stop(0);

        console.log("Split debate period over. Executing the split proposal...");
        // now the attacker splits
        dao.splitDAO.sendTransaction(
            split_proposal_id,
            attacker,
            {from:attacker, gas: 4000000}
        );
        checkWork();

        console.log("Right after the split, execute the attack proposal to get the deposit back");
        dao.executeProposal.sendTransaction(attack_proposal_id, '', {from:attacker, gas:1000000});
        addToTest('attack_proposal_passed', dao.proposals(attack_proposal_id)[5]);
        checkWork();

        addToTest('split_proposal_id', split_proposal_id);
        addToTest('split_proposal_passed', dao.proposals(split_proposal_id)[5]);
        addToTest('split_dao', dao.splitProposalNewAddress(split_proposal_id, 0));
        var splitdao = web3.eth.contract($dao_abi).at(testMap['split_dao']);
        addToTest('split_dao_total_supply', web3.fromWei(eth.getBalance(splitdao.address)));
        addToTest('attacker_balance_after', web3.fromWei(eth.getBalance(attacker)));

        // now comes the check. His balance should be the same but so should be the amount
        // balance of the split DAO and the balance he owned in the previous DAO. With the
        // colm attack that would not be the case as he would also get part of his proposal
        // deposit into the new DAO and thus make profit.
        addToTest(
        'final_diff',
        bigDiffRound(testMap['attacker_balance_after'], testMap['attacker_balance_before']) +
        bigDiffRound(testMap['split_dao_total_supply'], testMap['attacker_dao_balance_before'])
    );
        testResults();
    }, ($split_debating_period - $attack_debating_period) * 1000);

    miner.start(1);
    console.log("Waiting until the split proposal debate is over");
}, $attack_debating_period * 1000);
miner.start(1);
console.log("Waiting for the split debate period.");
