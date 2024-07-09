"""Test module hardware"""

import os
import sys


sys.path.append(os.path.join(os.getcwd(), ""))

from constant import HW_ID, TOKEN, URL
from engine import get_object_info_by_name, get_ssid
from hardware import (
    add_obj_uid,
    add_param_engin_axel,
    add_phone,
    create_driving_param,
    create_object,
    create_object_with_all_params,
    create_sensors,
    update_advance_setting,
    update_advance_validity_filter,
)
from tools import read_json


iteration = {
    0: (1, 5),
    1: (1, 2),
    2: (2, 3),
    3: (3, 4),
    4: (4, 5),
}


def test_create_object(count: int = 0):
    """Test func create object

    The count variable has values from 0 to 4. If the value 0 is selected, the function will bypass all servers from 1 to 4, and if the value 1 to 4 is selected, the function will only address a specific server.

    Args:
        count (int): default 0 (all server), max count = 4
    """
    export_object = read_json("tests/fixtures/create_object")
    for test_fms in range(*iteration[count]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        for list_id, dict_value in enumerate(export_object):
            name = f"{dict_value.get('ДЛ')}{test_fms}"
            hardware = dict_value.get("Оборудование").replace("Teltonika ", "")
            hw_id = HW_ID[test_fms][hardware]
            new_object = create_object(sid, URL[test_fms], hw_id, name, fms=test_fms)
            assert new_object.get("item").get("nm") == name
            assert new_object.get("item").get("uacl") == 880333094911


def test_create_sensors(count: int = 0):
    """Test func create sensors

    The count variable has values from 0 to 4. If the value 0 is selected, the function will bypass all servers from 1 to 4, and if the value 1 to 4 is selected, the function will only address a specific server.

    Args:
        count (int): default 0 (all server), max count = 4
    """
    export_object = read_json("tests/fixtures/create_object")
    for test_fms in range(*iteration[count]):
        url = URL[test_fms]
        sid = get_ssid(url, TOKEN[test_fms])
        for list_id, dict_value in enumerate(export_object):
            hardware = dict_value.get("Оборудование").replace("Teltonika ", "")
            name = f'{dict_value.get("ДЛ")}{test_fms}'
            hw_id = HW_ID[test_fms][hardware]
            obj_id = get_object_info_by_name(sid, name, url).get("items")[0].get("id")
            sens = create_sensors(sid, url, hw_id, obj_id, test_fms)
            assert sens == 0


def test_add_phone(count: int = 0):
    """Test func add_phone

    The count variable has values from 0 to 4. If the value 0 is selected, the function will bypass all servers from 1 to 4, and if the value 1 to 4 is selected, the function will only address a specific server.

    Args:
        count (int): default 0 (all server), max count = 4
    """
    export_object = read_json("tests/fixtures/create_object")
    for test_fms in range(*iteration[count]):
        url = URL[test_fms]
        sid = get_ssid(url, TOKEN[test_fms])
        for list_id, dict_value in enumerate(export_object):
            name = dict_value.get("ДЛ")
            phone = dict_value.get("geozone_sim")
            obj_id = get_object_info_by_name(sid, name, url).get("items")[0].get("id")
            result = add_phone(sid, url, obj_id, phone)
            assert phone in result


def test_add_obj_uid(count: int = 0):
    """Test func add object uid (imei)

    The count variable has values from 0 to 4. If the value 0 is selected, the function will bypass all servers from 1 to 4, and if the value 1 to 4 is selected, the function will only address a specific server.

    Args:
        count (int): default 0 (all server), max count = 4
    """
    export_object = read_json("tests/fixtures/create_object")
    for test_fms in range(*iteration[count]):
        url = URL[test_fms]
        sid = get_ssid(url, TOKEN[test_fms])
        for list_id, dict_value in enumerate(export_object):
            name = dict_value.get("ДЛ")
            imei = dict_value.get("geozone_imei")
            obj_id = get_object_info_by_name(sid, name, url).get("items")[0].get("id")
            hardware = dict_value.get("Оборудование").replace("Teltonika ", "")
            hw_id = HW_ID[test_fms][hardware]
            result = add_obj_uid(sid, url, obj_id, hw_id, imei)
            assert result.get("uid") == imei


def test_add_param_engin_axel(count: int = 0):
    """Test func add param engin and axel

    The count variable has values from 0 to 4. If the value 0 is selected, the function will bypass all servers from 1 to 4, and if the value 1 to 4 is selected, the function will only address a specific server.

    Args:
        count (int): default 0 (all server), max count = 4
    """
    export_object = read_json("tests/fixtures/create_object")
    for test_fms in range(*iteration[count]):
        url = URL[test_fms]
        sid = get_ssid(url, TOKEN[test_fms])
        for list_id, dict_value in enumerate(export_object):
            name = dict_value.get("ДЛ")
            obj_id = get_object_info_by_name(sid, name, url).get("items")[0].get("id")
            result = add_param_engin_axel(sid, url, obj_id)
            assert result == 0


def test_update_advance_setting(count: int = 0):
    """Test Update the settings Advanced driving.

    The count variable has values from 0 to 4. If the value 0 is selected, the function will bypass all servers from 1 to 4, and if the value 1 to 4 is selected, the function will only address a specific server.

    Args:
        count (int): default 0 (all server), max count = 4
    """
    export_object = read_json("tests/fixtures/create_object")
    for test_fms in range(*iteration[count]):
        url = URL[test_fms]
        sid = get_ssid(url, TOKEN[test_fms])
        for list_id, dict_value in enumerate(export_object):
            name = dict_value.get("ДЛ")
            obj_id = get_object_info_by_name(sid, name, url).get("items")[0].get("id")
            hardware = dict_value.get("Оборудование").replace("Teltonika ", "")
            hw_id = HW_ID[test_fms][hardware]
            result = update_advance_setting(sid, url, obj_id, hw_id, test_fms)
            assert len(result.items()) == 0


def test_update_advance_validity_filter(count: int = 0):
    """Test Update the settings used in reports. Second part.

    The count variable has values from 0 to 4. If the value 0 is selected, the function will bypass all servers from 1 to 4, and if the value 1 to 4 is selected, the function will only address a specific server.

    Args:
        count (int): default 0 (all server), max count = 4
    """
    export_object = read_json("tests/fixtures/create_object")
    for test_fms in range(*iteration[count]):
        url = URL[test_fms]
        sid = get_ssid(url, TOKEN[test_fms])
        for list_id, dict_value in enumerate(export_object):
            name = dict_value.get("ДЛ")
            obj_id = get_object_info_by_name(sid, name, url).get("items")[0].get("id")
            hardware = dict_value.get("Оборудование").replace("Teltonika ", "")
            hw_id = HW_ID[test_fms][hardware]
            result = update_advance_validity_filter(sid, url, obj_id, hw_id, test_fms)
            assert len(result.items()) == 0


def test_create_driving_param(count: int = 0):
    """Test Update the settings used in reports. Second part.

    The count variable has values from 0 to 4. If the value 0 is selected, the function will bypass all servers from 1 to 4, and if the value 1 to 4 is selected, the function will only address a specific server.

    Args:
        count (int): default 0 (all server), max count = 4
    """
    export_object = read_json("tests/fixtures/create_object")
    for test_fms in range(*iteration[count]):
        url = URL[test_fms]
        sid = get_ssid(url, TOKEN[test_fms])
        for list_id, dict_value in enumerate(export_object):
            name = dict_value.get("ДЛ")
            obj_id = get_object_info_by_name(sid, name, url).get("items")[0].get("id")
            result = create_driving_param(sid, url, obj_id)
            assert result == 0


def test_create_object_with_all_params(count: int = 0):
    """Test Create an object with sensors

    The count variable has values from 0 to 4. If the value 0 is selected, the function will bypass all servers from 1 to 4, and if the value 1 to 4 is selected, the function will only address a specific server.

    Args:
        count (int): default 0 (all server), max count = 4
    """
    export_object = read_json("tests/fixtures/create_object")
    for test_fms in range(*iteration[count]):
        url = URL[test_fms]
        sid = get_ssid(url, TOKEN[test_fms])
        for list_id, dict_value in enumerate(export_object):
            result = create_object_with_all_params(sid, url, dict_value, test_fms)
            assert result > 1
