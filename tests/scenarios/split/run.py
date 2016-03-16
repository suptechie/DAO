import inspect
import os
import random
from datetime import datetime
currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(os.path.dirname(currentdir))
os.sys.path.insert(0, parentdir)
from utils import eval_test, arr_str, create_votes_array


def tokens_after_split(votes, original_balance, dao_balance, reward_tokens):
    """
    Create expected token and reward token results after the split scenario
        Parameters
        ----------
        votes : array of booleans
        The votes array of what each user voted

        original_balance : array of ints
        The original amount of tokens each user had before the split

        dao_balance : int
        The balance of ether left in the DAO before the scenario started

        reward_tokens : float
        Amount of reward tokens generated in the DAO before the scenario.

        Returns
        ----------
        old_dao_balance : array of ints
        The balance of tokens left in the old dao.

        new_dao_balance : array of ints
        The balance of tokens left in the new dao.

        old_reward_tokens : float
        The amount of reward tokens left in the old dao.

        new_reward_tokens : float
        The amount of reward tokens left in the new dao.
    """

    old_dao_balance = []
    new_dao_balance = []
    totalSupply = sum(original_balance)
    old_reward_tokens = reward_tokens
    new_reward_tokens = 0

    for vote, orig in zip(votes, original_balance):
        if vote:
            new_dao_balance.append(orig * dao_balance / totalSupply)
            old_dao_balance.append(0)
            rewardToMove = float(orig) * reward_tokens / float(totalSupply)
            old_reward_tokens -= float(rewardToMove)
            new_reward_tokens += float(rewardToMove)
        else:
            old_dao_balance.append(orig)
            new_dao_balance.append(0)
    return (
        old_dao_balance,
        new_dao_balance,
        old_reward_tokens,
        new_reward_tokens
    )


def prepare_test_split(framework, split_gas):
    if framework.prop_id != 2:
        # run the rewards scenario first
        framework.run_scenario('rewards')

    debate_secs = 15
    votes = create_votes_array(
        framework.token_amounts,
        not framework.args.proposal_fail
    )
    framework.create_js_file(
        'split',
        {
            "dao_abi": framework.dao_abi,
            "dao_address": framework.dao_addr,
            "debating_period": debate_secs,
            "split_gas": split_gas,
            "votes": arr_str(votes),
            "prop_id": framework.next_proposal_id()
        }
    )
    print(
        "Notice: Debate period is {} seconds so the test will wait "
        "as much".format(debate_secs)
    )
    output = framework.run_script('split.js')
    return votes, output


def run(framework):
    # Use the split_gas variable to test that splitting with insufficient gas,
    # will fail reliably and will not leave an empty contract in the state,
    # burning away user tokens in the process.
    # This should happen with the latest homestead changes:
    # https://github.com/ethereum/EIPs/blob/master/EIPS/eip-2.mediawiki#specification
    split_gas = 4000000
    votes, output = prepare_test_split(framework, split_gas)
    oldBalance, newBalance, oldDAORewards, newDAORewards = tokens_after_split(
        votes,
        framework.token_amounts,
        framework.dao_balance_after_rewards,
        framework.dao_rewardToken_after_rewards
    )
    eval_test('split', output, {
        # default deposit,a simple way to test new DAO contract got created
        "newDAOProposalDeposit": 20,
        "oldDAOBalance": oldBalance,
        "newDAOBalance": newBalance,
        "oldDaoRewardTokens": oldDAORewards,
        "newDaoRewardTokens": newDAORewards
    })
    # if gas != enough
    #     eval_test('split-insufficient-gas', output, {
    #     "newDAOProposalDeposit": 0,
    #     "oldDAOBalance": self.token_amounts,
    #     "newDAOBalance": [0] * len(self.token_amounts),
    # })
