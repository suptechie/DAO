from utils import calculate_bytecode, to_wei

scenario_description = (
    "Test that the DAO can't call `payReward()` or "
    "`payOneTimeReward()` after the offer is deployed, in essence "
    "generating infinite reward tokens"
)


def run(ctx):
    ctx.assert_scenario_ran('proposal')
    bytecode = calculate_bytecode('payOneTimeReward')
    ctx.create_js_file(substitutions={
        "dao_abi": ctx.dao_abi,
        "dao_address": ctx.dao_addr,
        "offer_abi": ctx.offer_abi,
        "offer_address": ctx.offer_addr,
        "proposal_deposit": ctx.args.proposal_deposit,
        "transaction_bytecode": bytecode,
        "debating_period": ctx.args.proposal_debate_seconds,
    })
    print(
        "Notice: Debate period is {} seconds so the test will wait "
        "as much".format(ctx.args.proposal_debate_seconds)
    )

    ctx.execute(expected={
        # Nothing should make it to the reward account
        "dao_rewardaccount_diff": 0,
        # The DAO keeps the proposal deposit
        "dao_balance_diff": to_wei(ctx.args.proposal_deposit)
    })
