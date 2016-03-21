import random
from datetime import datetime
from utils import constrained_sum_sample_pos, arr_str


def run(framework):
    # if deployment did not already happen do it now
    if not framework.dao_addr:
        framework.run_scenario('deploy')
    else:
        print(
            "WARNING: Running the failed funding scenario with a pre-deployed "
            "DAO contract. Closing time is {} which is approximately {} "
            "seconds from now.".format(
                datetime.fromtimestamp(framework.closing_time).strftime(
                    '%Y-%m-%d %H:%M:%S'
                ),
                framework.remaining_time()
            )
        )

    accounts_num = len(framework.accounts)
    sale_secs = framework.remaining_time()
    framework.total_supply = random.randint(5, framework.min_value - 4)
    framework.token_amounts = constrained_sum_sample_pos(
        accounts_num, framework.total_supply
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
        "dao_funded": False,
        "total_supply": framework.total_supply,
        "refund": framework.token_amounts
    })
