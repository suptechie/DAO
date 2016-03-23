def calculate_reward(tokens, total_tokens, total_rewards):
    result = (tokens * float(total_rewards)) / float(total_tokens)
    return result


def run(ctx):
    if not ctx.prop_id:
        # run the proposal scenario first
        ctx.run_scenario('proposal')

    ctx.create_js_file(substitutions={
            "dao_abi": ctx.dao_abi,
            "dao_address": ctx.dao_addr,
            "total_rewards": ctx.args.rewards_total_amount,
            "proposal_deposit": ctx.args.proposal_deposit,
            "transaction_bytecode": '0x0',  # fallback function
            "debating_period": ctx.args.proposal_debate_seconds,
            "prop_id": ctx.next_proposal_id()
        }
    )
    print(
        "Notice: Debate period is {} seconds so the test will wait "
        "as much".format(ctx.args.proposal_debate_seconds)
    )

    results = ctx.execute(expected={
        "provider_reward_portion": calculate_reward(
            ctx.token_amounts[0],
            ctx.total_supply,
            ctx.args.rewards_total_amount)
    })
    ctx.dao_balance_after_rewards = results['DAO_balance']
    ctx.dao_rewardToken_after_rewards = results['DAO_rewardToken']
