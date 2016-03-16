import inspect
import os
import random
currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(os.path.dirname(currentdir))
os.sys.path.insert(0, parentdir)
from utils import eval_test, arr_str, create_votes_array


def count_token_votes(amounts, votes):
    """Returns how many tokens votes yay and how many voted nay"""
    yay = 0
    nay = 0
    for idx, amount in enumerate(amounts):
        if votes[idx]:
            yay += amount
        else:
            nay += amount
    return yay, nay


def run(framework):
    if not framework.token_amounts:
        # run the funding scenario first
        framework.run_scenario('fund')

    debate_secs = 20
    minamount = 2  # is determined by the total costs + one time costs
    amount = random.randint(minamount, sum(framework.token_amounts))
    votes = create_votes_array(
        framework.token_amounts,
        not framework.args.proposal_fail
    )
    yay, nay = count_token_votes(framework.token_amounts, votes)
    framework.create_js_file(
        'proposal',
        {
            "dao_abi": framework.dao_abi,
            "dao_address": framework.dao_addr,
            "offer_abi": framework.offer_abi,
            "offer_address": framework.offer_addr,
            "offer_amount": amount,
            "offer_desc": 'Test Proposal',
            "proposal_deposit": framework.args.proposal_deposit,
            "transaction_bytecode": '0x2ca15122',  # solc --hashes SampleOffer.sol
            "debating_period": debate_secs,
            "votes": arr_str(votes)
        }
    )
    print(
        "Notice: Debate period is {} seconds so the test will wait "
        "as much".format(debate_secs)
    )
    output = framework.run_script('proposal.js')
    eval_test('proposal', output, {
        "dao_proposals_number": "1",
        "proposal_passed": True,
        "proposal_yay": yay,
        "proposal_nay": nay,
        "calculated_deposit": framework.args.proposal_deposit,
        "onetime_costs": framework.args.offer_onetime_costs,
        "deposit_returned": True,
        "offer_promise_valid": True
    })
    framework.prop_id = 1
