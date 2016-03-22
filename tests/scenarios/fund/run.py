import random
from datetime import datetime
from utils import constrained_sum_sample_pos, arr_str


def run(framework):
    # if deployment did not already happen do it now
    if not framework.dao_addr:
        framework.run_scenario('deploy')
    else:
        print(
            "WARNING: Running the funding scenario with a pre-deployed "
            "DAO contract. Closing time is {} which is approximately {} "
            "seconds from now.".format(
                datetime.fromtimestamp(framework.closing_time).strftime(
                    '%Y-%m-%d %H:%M:%S'
                ),
                framework.remaining_time()
            )
        )

    sale_secs = framework.remaining_time()
    framework.total_supply = framework.args.deploy_min_value + random.randint(1, 100)
    framework.token_amounts = constrained_sum_sample_pos(
        len(framework.accounts), framework.total_supply
    )
    framework.create_js_file(substitutions={
            "dao_abi": framework.dao_abi,
            "dao_address": framework.dao_addr,
            "wait_ms": (sale_secs-3)*1000,
            "amounts": arr_str(framework.token_amounts)
        }
    )
    print(
        "Notice: Funding period is {} seconds so the test will wait "
        "as much".format(sale_secs)
    )

    framework.execute(expected={
        "dao_funded": True,
        "total_supply": framework.total_supply,
        "balances": framework.token_amounts,
        "user0_after": framework.token_amounts[0],
    })
