import requests
import json
import re
import logging
import base64
from .db import *


def sink(request):
    event = json.loads(request.body)
    logging.info(f"Received event: {event}")

    if get_env("SAVE_EVENTS").lower() == "true":
        db_add("events", {"item": event, "eventtype": event.get("event", "")})

    if "event" in event:
        event_type = event.get("event", "")
        logging.info(f"Event type is: {event_type}")

        if (
            event_type
            in [
                "participant_connected",
                "participant_disconnected",
            ]
            and event.get("data", {}).get("call_direction", None) in ["in"]
            and event.get("data", {}).get("service_type", None)
            in ["conference", "lecture", "connecting"]
        ):
            callid = event.get("data", {}).get("call_id")
            conference = event.get("data", {}).get("conference")
            if not callid:
                return

            if event_type == "participant_connected":
                logging.info(
                    f"eventsink.py: Event {callid} is type {event_type}, sending to active calls db"
                )
                db_add("activecalls", {"callid": callid, "conference": conference})

                # if conf := db_query("activeconferences",{"name": conference}):
                #     conf = conf[0]
                #     conf['participants'] += 1
                #     db_update("activeconferences", conf, {"name": conf["name"]})
                # else:
                #     db_add("activeconferences", {"name":conference, "participants": 1})

            elif event_type == "participant_disconnected":
                logging.info(
                    f"eventsink.py: Event {callid} is type {event_type}, removing from active calls db"
                )

                db_delete("activecalls", {"callid": callid})

                # conf = db_query("activeconferences",{"name": conference})
                # if conf:
                #     conf = conf[0]
                #     if conf["participants"] > 1:
                #         conf['participants'] -= 1
                #         db_update("activeconferences", conf, {"name": conf["name"]})
                #     else:
                #         db_delete("activeconferences", {"name":conference})

    return
