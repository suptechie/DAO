import random
from datetime import datetime
from utils import constrained_sum_sample_pos, arr_str


def run(ctx):
    # if deployment did not already happen do it now
    if not ctx.dao_addr:
        ctx.run_scenario('deploy')
    else:
        print(
            "WARNING: Running the failed funding scenario with a pre-deployed "
            "DAO contract. Closing time is {} which is approximately {} "
            "seconds from now.".format(
                datetime.fromtimestamp(ctx.closing_time).strftime(
                    '%Y-%m-%d %H:%M:%S'
                ),
                ctx.remaining_time()
            )
        )

    accounts_num = len(ctx.accounts)
    sale_secs = ctx.remaining_time()
    ctx.total_supply = random.randint(5, ctx.args.deploy_min_value - 4)
    ctx.token_amounts = constrained_sum_sample_pos(
        accounts_num, ctx.total_supply
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
        "dao_funded": False,
        "total_supply": ctx.total_supply,
        "refund": ctx.token_amounts
    })
