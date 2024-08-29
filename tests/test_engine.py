import os
import sys

sys.path.append(os.path.join(os.getcwd(), ""))

from constant import TOKEN, URL
from engine import (
    create_custom_fields,
    create_object,
    get_admin_fields,
    get_header,
    get_object_id,
    get_object_info_by_imei,
    get_object_info_by_name,
    get_ssid,
    id_fields,
    search_group_by_id,
    search_groups_by_name,
    update_param,
    group_update
)
from hardware import create_object_with_all_params
from tools import read_json

iteration = {
    0: (1, 5),
    1: (1, 2),
    2: (2, 3),
    3: (3, 4),
    4: (4, 5),
}

fms = 0  # if 0 run tests iteration for all fms or only 1 or only 2 etc


def test_get_haeder():
    user_agent_list = [
        "Safari/537.36 OPR/26.0.1656.60",
        "(maverick) Firefox/3.6.10",
        "Chrome/39.0.2171.71 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 "
        "(KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    ]
    assert get_header().get("User-Agent") in user_agent_list


def test_get_ssid():
    for test_fms in range(*iteration[fms]):
        ssid = get_ssid(URL[test_fms], TOKEN[test_fms])
        assert len(ssid) == 32


def test_get_object_info_by_imei():
    export_object = read_json("tests/fixtures/create_object")
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        for list_id, dict_value in enumerate(export_object):
            imei = dict_value.get("geozone_imei")
            object_info = get_object_info_by_imei(sid, imei, URL[test_fms])
            assert imei == object_info.get("items")[0].get("uid")


def test_get_object_info_by_name():
    export_object = read_json("tests/fixtures/create_object")
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        for list_id, dict_value in enumerate(export_object):
            imei = dict_value.get("geozone_imei")
            name = dict_value.get("ДЛ")
            object_info = get_object_info_by_name(sid, name, URL[test_fms])
            assert imei == object_info.get("items")[0].get("uid")


def test_get_object_id():
    export_object = read_json("tests/fixtures/create_object")
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        for list_id, dict_value in enumerate(export_object):
            imei = dict_value.get("geozone_imei")
            object_id = get_object_id(sid, imei, URL[test_fms])
            assert object_id > 0
        error_imei = "122334455668877"
        assert get_object_id(sid, error_imei, URL[test_fms]) == -1


def test_create_custom_fields():
    export_object = read_json("tests/fixtures/one_object")
    for test_fms in range(*iteration[fms]):
        imei = export_object.get("geozone_imei")
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        new_object = create_object_with_all_params(
            sid, URL[test_fms], export_object, test_fms
        )
        create_custom_fields(sid, new_object, URL[test_fms])
        check_object = get_object_info_by_imei(sid, imei, URL[test_fms])
        assert len(check_object.get("items")[0].get("aflds")) > 0
        assert len(check_object.get("items")[0].get("flds")) > 0


def test_update_param():
    export_object = read_json("tests/fixtures/one_object")
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        imei = export_object.get("geozone_imei")
        pin = export_object.get("Пин")
        uid = get_object_id(sid, imei, URL[test_fms])
        id_field = id_fields(sid, uid, URL[test_fms])
        update_param(sid, uid, export_object, id_field, URL[test_fms])
        fields = get_admin_fields(sid, uid, URL[test_fms])
        assert fields.get("1").get("v") == imei
        assert fields.get("7").get("v") == pin


def test_search_groups_by_name():
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        groups = {
            1: ["belousov"],
            2: ["belousov"],
            3: ["belousov", "1Т-Лизинг", "1Эволюция"],
            4: ["belousov", "1ГПБАЛ", "1Эволюция", "1Каркаде"],
        }
        for group in groups[test_fms]:
            finded = search_groups_by_name(sid, group, URL[test_fms])
            assert group in finded.get("items")[0].get("nm")


def test_admin_fields():
    export_object = read_json("tests/fixtures/one_object")
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        imei = export_object.get("geozone_imei")
        uid = get_object_id(sid, imei, URL[test_fms])
        afields = get_admin_fields(sid, uid, URL[test_fms])
        assert len(afields) > 0
        empty_id = get_object_id(sid, 150457175415805, URL[test_fms])
        empty_object = get_admin_fields(sid, empty_id, URL[test_fms])
        assert len(empty_object) == 0


def test_search_group_by_id():
    evo_spec = 26339
    sid = get_ssid(URL[3], TOKEN[3])
    get_group = search_group_by_id(sid, evo_spec, URL[3])
    assert '1Эволюция спецтехника' == get_group.get('item').get('nm')


def test_create_object():
    export_object = read_json("tests/fixtures/tst_engn_create_obj")
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        imei = export_object.get("geozone_imei")
        create_object(sid, export_object, URL[test_fms], test_fms)
        new_object = get_object_info_by_imei(sid, imei, URL[test_fms])
        assert export_object.get("ДЛ") == new_object.get('items')[0].get('nm')


def test_group_update():
    export_object = read_json("tests/fixtures/create_object")
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        group_update(sid, export_object, URL[test_fms])


if __name__ == '__main__':
    sid = get_ssid(URL[1], TOKEN[1])
    export_object = read_json("tests/fixtures/tst_engn_create_obj")
    create_object(sid, export_object, URL[1], 1)
    imei = export_object.get("geozone_imei")
    a = get_object_info_by_imei(sid, imei, URL[1])
    from pprint import pprint
    pprint(a)
    print(a.get('items')[0].get('nm'))
