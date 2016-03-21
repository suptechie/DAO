def calculate_reward(tokens, total_tokens, total_rewards):
    result = (tokens * float(total_rewards)) / float(total_tokens)
    return result


def run(framework):
    if not framework.prop_id:
        # run the proposal scenario first
        framework.run_scenario('proposal')

    framework.create_js_file(substitutions={
            "dao_abi": framework.dao_abi,
            "dao_address": framework.dao_addr,
            "total_rewards": framework.args.rewards_total_amount,
            "proposal_deposit": framework.args.proposal_deposit,
            "transaction_bytecode": '0x0',  # fallback function
            "debating_period": framework.args.proposal_debate_seconds,
            "prop_id": framework.next_proposal_id()
        }
    )
    print(
        "Notice: Debate period is {} seconds so the test will wait "
        "as much".format(framework.args.proposal_debate_seconds)
    )

    results = framework.execute(expected={
        "provider_reward_portion": calculate_reward(
            framework.token_amounts[0],
            framework.total_supply,
            framework.args.rewards_total_amount)
    })
    framework.dao_balance_after_rewards = results['DAO_balance']
    framework.dao_rewardToken_after_rewards = results['DAO_rewardToken']
