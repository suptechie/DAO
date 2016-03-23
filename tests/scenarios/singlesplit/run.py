def run(framework):
    if not framework.token_amounts:
        # run the funding scenario first
        framework.run_scenario('fund')

    framework.create_js_file(substitutions={
        "dao_abi": framework.dao_abi,
        "dao_address": framework.dao_addr,
        "proposal_deposit": framework.args.proposal_deposit,
        "split_gas": 4000000,
        "debating_period": framework.args.proposal_debate_seconds,
        "prop_id": framework.next_proposal_id()
    })
    print(
        "Notice: Debate period is {} seconds so the test will wait "
        "as much".format(framework.args.proposal_debate_seconds)
    )

    framework.execute(expected={
        "newdao_proposals_num": 1,
        "angry_user_profit": framework.token_amounts[1] + framework.args.proposal_deposit
    })
