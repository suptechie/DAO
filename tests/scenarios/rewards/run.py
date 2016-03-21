import inspect
import os
currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
scenario_name = os.path.basename(currentdir)


def calculate_reward(tokens, total_tokens, total_rewards):
    result = (tokens * float(total_rewards)) / float(total_tokens)
    return result


def run(framework):
    if not framework.prop_id:
        # run the proposal scenario first
        framework.run_scenario('proposal')

    framework.running_scenario = scenario_name
    debate_secs = 15
    framework.create_js_file(substitutions={
            "dao_abi": framework.dao_abi,
            "dao_address": framework.dao_addr,
            "total_rewards": framework.args.total_rewards,
            "proposal_deposit": framework.args.proposal_deposit,
            "transaction_bytecode": '0x0',  # fallback function
            "debating_period": debate_secs,
            "prop_id": framework.next_proposal_id()
        }
    )
    print(
        "Notice: Debate period is {} seconds so the test will wait "
        "as much".format(debate_secs)
    )

    results = framework.execute(expected={
        "provider_reward_portion": calculate_reward(
            framework.token_amounts[0],
            framework.total_supply,
            framework.args.total_rewards)
    })
    framework.dao_balance_after_rewards = results['DAO_balance']
    framework.dao_rewardToken_after_rewards = results['DAO_rewardToken']
