import random
from datetime import datetime
from utils import constrained_sum_sample_pos, arr_str


def run(ctx):
    # if deployment did not already happen do it now
    if not ctx.dao_addr:
        ctx.run_scenario('deploy')
    else:
        print(
            "WARNING: Running the funding scenario with a pre-deployed "
            "DAO contract. Closing time is {} which is approximately {} "
            "seconds from now.".format(
                datetime.fromtimestamp(ctx.closing_time).strftime(
                    '%Y-%m-%d %H:%M:%S'
                ),
                ctx.remaining_time()
            )
        )

    sale_secs = ctx.remaining_time()
    ctx.total_supply = ctx.args.deploy_min_value + random.randint(1, 100)
    ctx.token_amounts = constrained_sum_sample_pos(
        len(ctx.accounts), ctx.total_supply
    )
    ctx.create_js_file(substitutions={
            "dao_abi": ctx.dao_abi,
            "dao_address": ctx.dao_addr,
            "wait_ms": (sale_secs-3)*1000,
            "amounts": arr_str(ctx.token_amounts)
        }
    )
    print(
        "Notice: Funding period is {} seconds so the test will wait "
        "as much".format(sale_secs)
    )

    ctx.execute(expected={
        "dao_funded": True,
        "total_supply": ctx.total_supply,
        "balances": ctx.token_amounts,
        "user0_after": ctx.token_amounts[0],
    })
