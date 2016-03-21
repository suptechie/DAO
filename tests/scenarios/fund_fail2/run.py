import sys
from datetime import datetime
from utils import constrained_sum_sample_pos, arr_str


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
                framework.remaining_time()
            )
        )

    accounts_num = len(framework.accounts)
    if accounts_num * 2 >= framework.args.deploy_min_value - 4:
        print("Please increase the minimum funding goal for the scenario.")
        sys.exit(1)

    sale_secs = framework.remaining_time()
    total_supply = framework.args.deploy_min_value - 4
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
        substitutions={
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
    framework.execute(expected={
        "dao_funded": False,
        "total_supply": framework.total_supply,
        "refund": framework.token_amounts
    })
