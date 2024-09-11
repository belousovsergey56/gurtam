import os
import sys

sys.path.append(os.path.join(os.getcwd(), ""))

from tools import (
    xls_to_json,
    is_xlsx,
    read_json,
    get_headers,
    update_bd,
    get_diff_in_upload_file
)


def test_xls_to_json():
    f = "tests/fixtures/tests.xlsx"
    to_json = xls_to_json(f).split('/')[2]
    list_dir = os.listdir("tests/fixtures/")
    assert f"{to_json}.json" in list_dir


def test_is_xlsx():
    not_xls = "tests/fixtures/fill_inn.json"
    xls = "tests/fixtures/load_rddb.xlsx"
    assert is_xlsx(not_xls) is False
    assert is_xlsx(xls) is True


def test_read_json():
    file_ = "tests/fixtures/fill_inn"
    result = read_json(file_)
    assert type(result) is dict


def test_get_headers():
    file_ = "tests/fixtures/load_rddb"
    f = read_json(file_)
    result = get_headers(f)
    assert result[2] == "ИНН"
    assert result[4] == "IMEI"
