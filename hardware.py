"""This module, create object and fill sensors."""

import json
import requests

URL = ''

HW_ID = {'MT5': 20, 'FMB130': 19510,
         'FMB125': 96, 'FMB920': 69, 'FMB140': 19511}


def create_object(sid: str, hardware: int, object_name: str):
    """Create new object.

    Args:
        sid (str): Session id
        hardware (int): id hardware
        object_name (str): this is contract name
    """
    params = {
        'svc': 'core/create_unit',
        'params': json.dumps({
            "creatorId": 117,
            "name": object_name,
            "hwTypeId": HW_ID.get(hardware),
            "dataFlags": 1}),
        'sid': sid
    }
    requests.post(URL, params=params)
