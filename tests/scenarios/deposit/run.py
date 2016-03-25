scenario_description = (
    "Make a proposal to change the default proposal deposit, vote for it and "
    "then assure that the DAO's proposal deposit did indeed change"
)


def calculate_bytecode(new_deposit):
    """
    Create the bytecode for calling dao.changeProposalDeposit() as defined
    here:
    https://github.com/ethereum/wiki/wiki/Ethereum-Contract-ABI#examples
    """
    return "{0}{1:0{2}x}".format('0xe33734fd', new_deposit, 64)


def run(ctx):
    ctx.assert_scenario_ran('fund')

    bytecode = calculate_bytecode(ctx.args.deposit_new_value)
    ctx.create_js_file(substitutions={
            "dao_abi": ctx.dao_abi,
            "dao_address": ctx.dao_addr,
            "proposal_deposit": ctx.args.proposal_deposit,
            "transaction_bytecode": bytecode,
            "debating_period": ctx.args.deposit_debate_seconds,
            "prop_id": ctx.next_proposal_id()
        }
    )
    print(
        "Notice: Debate period is {} seconds so the test will wait "
        "as much".format(ctx.args.proposal_debate_seconds)
    )

    ctx.execute(expected={
        "proposal_passed": True,
        "deposit_after_vote": ctx.args.deposit_new_value
    })
