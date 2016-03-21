import inspect
import os
import sys
import random
from datetime import datetime
currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(os.path.dirname(currentdir))
os.sys.path.insert(0, parentdir)
from utils import constrained_sum_sample_pos, arr_str, ts_now


def run(framework):
    # if deployment did not already happen do it now
    if not framework.dao_addr:
        framework.run_scenario('deploy')
    else:
        print(
            "WARNING: Running the failed funding 2 scenario with a "
            "pre-deployed DAO contract. Closing time is {} which is "
            "approximately {} seconds from now.".format(
                datetime.fromtimestamp(framework.closing_time).strftime(
                    '%Y-%m-%d %H:%M:%S'
                ),
                framework.closing_time - ts_now()
            )
        )

    accounts_num = len(framework.accounts)
    if accounts_num * 2 >= framework.min_value - 4:
        print("Please increase the minimum funding goal for the scenario.")
        sys.exit(1)

    sale_secs = framework.closing_time - ts_now()
    # total_supply = random.randint(accounts_num*2, framework.min_value - 4)
    total_supply = framework.min_value - 4
    proxy_amounts = constrained_sum_sample_pos(
        accounts_num, total_supply / 2
    )
    normal_amounts = constrained_sum_sample_pos(
        accounts_num, total_supply / 2
    )
    framework.token_amounts = [
        sum(x) for x in zip(proxy_amounts[::-1], normal_amounts)
    ]
    framework.total_supply = sum(framework.token_amounts)
    framework.create_js_file(
        'fund_fail2',
        {
            "dao_abi": framework.dao_abi,
            "dao_address": framework.dao_addr,
            "wait_ms": (sale_secs-3)*1000,
            "proxy_amounts": arr_str(proxy_amounts),
            "normal_amounts": arr_str(normal_amounts)
        }
    )
    print(
        "Notice: Funding period is {} seconds so the test will wait "
        "as much".format(sale_secs)
    )
    framework.execute('fund_fail2', {
        "dao_funded": False,
        "total_supply": framework.total_supply,
        "refund": framework.token_amounts
    })
