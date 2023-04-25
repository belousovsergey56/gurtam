"""
Module for convert and read files.

Module have a func for convert xls to json,
and read json for returns dictionary.
"""

import json

import pandas as pd


def xls_to_json(xls_file):
    """Convert Excel file to json.

    Args:
        xls_file (file.xlsx): Excel file to be converted to json
    """
    xls = pd.read_excel(xls_file)
    xls.to_json('upload/work_file.json', orient='records')


def read_json() -> dict:
    """Read a file.

    The function reads a json file saved in upload/ directory
    and returns a dictionary.

    Returns:
        dict: dictionary ready to use
    """
    with open('upload/work_file.json', 'r', encoding='UTF-8') as f:
        a = json.loads(f.read())
        return a
