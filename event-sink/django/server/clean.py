import requests
import json
import re
import logging
import base64
from .db import *

def dbclean(request):
    body = request.GET.dict()
    logging.info(f"Request body: {body}")
    if "table" in body:
        table = body["table"]
        db_clean(table)
        return {"result": f"Table '{table}' cleaned"}
    else:
        return {"result": f"No 'table' key in request"}
