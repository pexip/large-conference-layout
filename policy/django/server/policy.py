import requests
import json
import re
import logging
import base64
from .db import *
from django.conf import settings
import threading


def dialout(fqdn, dial, pin_header):
    req_token = f"{fqdn}/request_token"
    dial_api = f"{fqdn}/dial"
    rel_token = f"{fqdn}/release_token"

    token_response = requests.post(req_token, headers=pin_header)
    token = json.loads(token_response.text)["result"]["token"]

    token_header = {"token": token}
    requests.post(dial_api, headers=token_header, json=dial)

    requests.post(rel_token, headers=token_header)


def dial_trigger(fqdn, dial, pin_header):
    threading.Thread(target=dialout, args=(fqdn, dial, pin_header)).start()


def service_config(request):
    call_info = request.GET.dict()

    # config = json.loads(get_env("CONFIG"))["configs"]
    config = settings.CONFERENCE_CONFIG["configs"]

    policy_response = None

    # response to reject call
    policy_reponse_reject = {"status": "success", "action": "reject"}

    # response to pass back to Pexip to check internally
    policy_response_continue = {"status": "success", "action": "continue"}

    # if call_info["call_direction"] == "dial_out":
    #     return policy_response_continue

    logging.info(
        f"PolicyServer: /service/configuration http trigger function processed a request."
    )
    logging.info(f"PolicyServer: {call_info}")

    # Get local alias from passed-in parameters
    local_alias = call_info["local_alias"]

    # If local_alias is missing, reject the call
    if not local_alias:
        return policy_reponse_reject

    else:
        for conf in config:
            alias_regex = conf.get("alias", r"(?!x)x")
            domain = conf.get("domain", None)

            # Replace "<domain>"" with actual domain in regex if necessary
            if alias_regex and domain and "<domain>" in alias_regex:
                alias_regex = alias_regex.replace("<domain>", domain)

            # Check if the alias matches the regex
            match = re.match(alias_regex, local_alias)

            # If alias matches regex then calculate response
            if match:
                policy_response = conf.get("response", None)

                # If there is a valid response field in the database use that.  Else send "continue"
                if (
                    policy_response
                    and "basename" in conf
                    and conf.get("basename", None)
                    and len(list(match.groups())) > 0
                ):
                    try:
                        vmr_id = match.group(2)
                    except:
                        vmr_id = None

                    if vmr_id:
                        specific_vmr_dialed = True
                    else:
                        specific_vmr_dialed = False

                    # Conference ID is the regex match group
                    conf_id = match.group(1)

                    # Calculate name of conference by combining basename and conference ID

                    # Check if this is a partitioned VMR
                    part_per_vmr = conf.get("participants_per_vmr", None)

                    # Default vmr_id is 1, which will create this if there are none
                    part_vmrs = []

                    if (
                        not vmr_id
                        and part_per_vmr
                        and call_info.get("call_direction", "") == "dial_in"
                    ):
                        # Filter to only ones that match partitioned VMR alias
                        conf_regex = f"{conf['basename']}{conf_id}_vmr(\d+)"

                        # Search database for conferences matching regex
                        active_conferences = active_conferences = [
                            dict(c)
                            for c in db_count(
                                "ActiveCalls",
                                {"conference": conf_regex},
                                "conference",
                                regex=True,
                            )
                        ]

                        # Split results into partially full and full VMRs
                        part_vmrs = [
                            c["conference"]
                            for c in active_conferences
                            if c["count"] < part_per_vmr
                        ]
                        full_vmrs = [
                            c["conference"]
                            for c in active_conferences
                            if c["count"] >= part_per_vmr
                        ]

                        # Pull out just the numeric VMR ids
                        part_vmrs = [
                            int(re.search(conf_regex, r).group(1)) for r in part_vmrs
                        ]
                        full_vmrs = [
                            int(re.search(conf_regex, r).group(1)) for r in full_vmrs
                        ]

                        vmr_id = 1

                        # If there are partially full VMRs fill the lowest numbered one first
                        if part_vmrs:
                            vmr_id = min(part_vmrs)
                        # If there are only full VMRs then find the lowest numbered one that is not full
                        else:
                            while vmr_id in full_vmrs:
                                vmr_id += 1

                        # Create VMR name with calculated vmr_id
                        policy_response["result"][
                            "name"
                        ] = f"{conf.get('basename')}{conf_id}_vmr{vmr_id}"
                    elif vmr_id:
                        policy_response["result"][
                            "name"
                        ] = f"{conf.get('basename')}{conf_id}_vmr{vmr_id}"
                    else:
                        policy_response["result"][
                            "name"
                        ] = f"{conf.get('basename')}{conf_id}"

                    # If this conference is supposed to dialout to another, dial with client API
                    if (
                        conf.get("dialout", False)
                        and conf.get("dialout_basename", False)
                        and conf.get("dialout_location", False)
                        and vmr_id not in part_vmrs
                        and call_info.get("call_direction", "") == "dial_in"
                        and not specific_vmr_dialed
                    ):
                        fqdn = f"https://{domain}/api/client/v2/conferences/{policy_response['result']['name']}"
                        dial = {
                            "role": "HOST",
                            "destination": f"{conf['dialout_basename']}_{conf_id}@{domain}",
                            "protocol": "auto",
                            "source_display_name": f"VMR{vmr_id}",
                            "remote_display_name": f"{conf.get('dialout_remote_display_name', 'Main')}",
                            "keep_conference_alive": "keep_conference_alive_never",
                        }
                        pin_header = {"pin": f"{policy_response['result']['host_pin']}"}

                        dial_trigger(fqdn, dial, pin_header)

                    return policy_response
                else:
                    return policy_response_continue

    # For anything else pass back to Pexip
    return policy_response_continue


def location(request):
    call_info = request.GET.dict()
    logging.info(call_info)

    policy_response = {
        "status": "success",
        "result": {
            "location": "non_existent_location_to_force_fallback",
        },
        "type": "media_location",
    }

    logging.info(policy_response)

    return policy_response


def avatar(request, alias):
    call_info = request.GET.dict()
    logging.info(call_info)

    with open("/app/server/pexip.jpg", "rb") as f:
        policy_response = base64.b64encode(f.read()).decode()

    logging.info(policy_response)

    return policy_response


def directory(request):
    call_info = request.GET.dict()
    logging.info(call_info)

    policy_response = {
        "status": "success",
        "result": [],
        "type": "directory",
    }

    logging.info(policy_response)

    return policy_response


def registration(request, alias):
    call_info = request.GET.dict()
    logging.info(call_info)

    policy_response = {
        "status": "success",
        "action": "continue",
        "result": {},
        "type": "registration",
    }

    logging.info(policy_response)

    return policy_response
