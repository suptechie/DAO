import sys
import json
from utils import extract_test_dict, seconds_in_future


def calculate_closing_time(obj, script_name, substitutions):
    obj.closing_time = seconds_in_future(obj.args.closing_time)
    substitutions['closing_time'] = obj.closing_time
    return substitutions


def run(framework):
    print("Running the Deploy Test Scenario")
    framework.create_js_file(substitutions={
            "dao_abi": framework.dao_abi,
            "dao_bin": framework.dao_bin,
            "creator_abi": framework.creator_abi,
            "creator_bin": framework.creator_bin,
            "offer_abi": framework.offer_abi,
            "offer_bin": framework.offer_bin,
            "offer_onetime": framework.args.offer_onetime_costs,
            "offer_total": framework.args.offer_total_costs,
            "min_value": framework.min_value,
        },
        cb_before_creation=calculate_closing_time
    )
    output = framework.run_script('deploy.js')
    results = extract_test_dict('deploy', output)

    try:
        framework.dao_creator_addr = results['dao_creator_address']
        framework.dao_addr = results['dao_address']
        framework.offer_addr = results['offer_address']
    except:
        print(
            "ERROR: Could not find expected results in the deploy scenario"
            ". The output was:\n{}".format(output)
        )
        sys.exit(1)
    print("DAO Creator address is: {}".format(framework.dao_creator_addr))
    print("DAO address is: {}".format(framework.dao_addr))
    print("SampleOffer address is: {}".format(framework.offer_addr))
    with open(framework.save_file, "w") as f:
        f.write(json.dumps({
            "dao_creator_addr": framework.dao_creator_addr,
            "dao_addr": framework.dao_addr,
            "offer_addr": framework.offer_addr,
            "closing_time": framework.closing_time
        }))
