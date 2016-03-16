import inspect
import os
import random
from datetime import datetime
currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(os.path.dirname(currentdir))
os.sys.path.insert(0, parentdir)
from utils import eval_test, constrained_sum_sample_pos, arr_str, ts_now


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
                framework.closing_time - ts_now()
            )
        )

    accounts_num = len(framework.accounts)
    sale_secs = framework.closing_time - ts_now()
    framework.total_supply = random.randint(5, framework.min_value - 2)
    framework.token_amounts = constrained_sum_sample_pos(
        accounts_num, framework.total_supply
    )
    framework.create_js_file(
        'fund_fail',
        {
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
    framework.execute('fund_fail', {
        "dao_funded": False,
        "total_supply": framework.total_supply,
        "balances": [0] * accounts_num,
        "refund": framework.token_amounts[0:1]
    })
