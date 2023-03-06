"""
Module for convert and read files.

Module have a func for convert xls to json,
and read json for returns ditionary.
"""

import pandas as pd
import json


def xls_to_json(xls_file):
    """Convert excel file to json.

    Args:
        xls_file (file.xlsx): excel file to be converted to json
    """
    xls = pd.read_excel(xls_file)
    xls.to_json('work_file.json', orient='records')


def read_json() -> dict:
    """Read a file.

    The function reads a json file and returns a dictionary.

    Returns:
        dict: dictionary ready to use
    """
    with open('work_file.json', 'r') as f:
        a = json.loads(f.read())
        return a
