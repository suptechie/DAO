def calculate_bytecode(new_deposit):
    """
    Create the bytecode for calling dao.changeProposalDeposit() as defined
    here:
    https://github.com/ethereum/wiki/wiki/Ethereum-Contract-ABI#examples
    """
    return "{0}{1:0{2}x}".format('0xe33734fd', new_deposit, 64)


def run(framework):
    if not framework.token_amounts:
        # run the funding scenario first
        framework.run_scenario('fund')

    bytecode = calculate_bytecode(framework.args.deposit_new_value)
    framework.create_js_file(substitutions={
            "dao_abi": framework.dao_abi,
            "dao_address": framework.dao_addr,
            "proposal_deposit": framework.args.proposal_deposit,
            "transaction_bytecode": bytecode,
            "debating_period": framework.args.deposit_debate_seconds,
            "prop_id": framework.next_proposal_id()
        }
    )
    print(
        "Notice: Debate period is {} seconds so the test will wait "
        "as much".format(framework.args.proposal_debate_seconds)
    )

    framework.execute(expected={
        "proposal_passed": True,
        "deposit_after_vote": framework.args.deposit_new_value
    })
