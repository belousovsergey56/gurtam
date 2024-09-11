import os
import sys

sys.path.append(os.path.join(os.getcwd(), ""))

from constant import GROUPS, TOKEN, URL, USER_ID
from engine import (
    __get_new_token,
    add_groups,
    check_admin_fields,
    create_admin_field,
    create_custom_field,
    create_custom_fields,
    create_object,
    delete_object,
    fill_info,
    get_admin_fields,
    get_custom_fields,
    get_header,
    get_object_id,
    get_object_info_by_imei,
    get_object_info_by_name,
    get_ssid,
    get_user_id,
    group_update,
    id_fields,
    search_group_by_id,
    search_groups_by_name,
    upd_inn_field,
    update_name,
    update_param,
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
    assert "1Эволюция спецтехника" == get_group.get("item").get("nm")


def test_create_object():
    export_object = read_json("tests/fixtures/tst_engn_create_obj")
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        imei = export_object.get("geozone_imei")
        create_object(sid, export_object, URL[test_fms], test_fms)
        new_object = get_object_info_by_imei(sid, imei, URL[test_fms])
        assert export_object.get("ДЛ") == new_object.get("items")[0].get("nm")


def test_add_groups():
    export_object = read_json("tests/fixtures/one_object")
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        group = search_groups_by_name(sid, "belousov", URL[test_fms])
        unit_list = group.get("items")[0].get("u")
        id_group = group.get("items")[0].get("id")
        obj_id = get_object_id(
            sid, export_object.get("geozone_imei"), URL[test_fms])
        new_group_list = add_groups(
            sid, id_group, unit_list, [obj_id], URL[test_fms])
        print(new_group_list)
        assert obj_id in new_group_list.get("u")


def test_group_update():
    export_object = read_json("tests/fixtures/create_object")
    for test_fms in range(3, 5):
        auto = int()
        truck = int()
        spec = int()
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        for obj in export_object:
            uid = get_object_id(sid, obj.get("geozone_imei"), URL[test_fms])
            obj.update({"uid": uid})
            if obj.get("geozone_imei") == "150317175645805":
                auto += obj.get("uid")
            elif obj.get("geozone_imei") == "150457175415805":
                truck += obj.get("uid")
            elif obj.get("geozone_imei") == "150317175415899":
                spec += obj.get("uid")
        group_update(sid, export_object, URL[test_fms])
        if test_fms == 3:
            AUTO = (
                search_group_by_id(
                    sid, GROUPS[test_fms]["AUTO"][0], URL[test_fms])
                .get("item")
                .get("u")
            )
            TRUCK = (
                search_group_by_id(
                    sid, GROUPS[test_fms]["TRUCK"][0], URL[test_fms])
                .get("item")
                .get("u")
            )
            SPEC = (
                search_group_by_id(
                    sid, GROUPS[test_fms]["SPEC"][0], URL[test_fms])
                .get("item")
                .get("u")
            )
            assert auto in AUTO
            assert truck in TRUCK
            assert spec in SPEC
        else:
            AUTO = (
                search_group_by_id(
                    sid, GROUPS[test_fms]["AUTO"][2], URL[test_fms])
                .get("item")
                .get("u")
            )
            TRUCK = (
                search_group_by_id(
                    sid, GROUPS[test_fms]["TRUCK"][2], URL[test_fms])
                .get("item")
                .get("u")
            )
            SPEC = (
                search_group_by_id(
                    sid, GROUPS[test_fms]["SPEC"][2], URL[test_fms])
                .get("item")
                .get("u")
            )
            assert auto in AUTO
            assert truck in TRUCK
            assert spec in SPEC


def test_get_custom_fields():
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        uid = get_object_id(sid, "220557175415805", URL[test_fms])
        result = get_custom_fields(sid, uid, URL[test_fms])
        assert len(result) > 0


def test_create_custom_field():
    imei = "440317175415805"
    field = "belousov_info"
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        uid = get_object_id(sid, imei, URL[test_fms])
        upd_fld = create_custom_field(sid, uid, field, URL[test_fms])
        assert upd_fld[1].get("n") == field


def test_get_admin_fields():
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        uid = get_object_id(sid, "220557175415805", URL[test_fms])
        result = get_admin_fields(sid, uid, URL[test_fms])
        assert len(result) > 0


def test_create_admin_field():
    imei = "440317175415805"
    field = "belousov_admin"
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        uid = get_object_id(sid, imei, URL[test_fms])
        upd_fld = create_admin_field(sid, uid, field, URL[test_fms])
        assert upd_fld[1].get("n") == field


def test_check_admin_fields():
    imei = "440317175415805"
    field = "belousov_admin"
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        uid = get_object_id(sid, imei, URL[test_fms])
        responce = check_admin_fields(sid, uid, field, URL[test_fms])
        assert 1 == responce[0]


def test_fill_info():
    data = read_json("tests/fixtures/load_rddb")[0]
    imei = data.get("IMEI")
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        uid = get_object_id(sid, imei, URL[test_fms])

        create_admin_field(sid, uid, "Инфо1", URL[test_fms])
        create_admin_field(sid, uid, "Инфо5", URL[test_fms])
        create_admin_field(sid, uid, "Инфо6", URL[test_fms])
        create_admin_field(sid, uid, "Инфо7", URL[test_fms])

        id_info1 = check_admin_fields(sid, uid, "Инфо1", URL[test_fms])
        id_info5 = check_admin_fields(sid, uid, "Инфо5", URL[test_fms])
        id_info6 = check_admin_fields(sid, uid, "Инфо6", URL[test_fms])
        id_info7 = check_admin_fields(sid, uid, "Инфо7", URL[test_fms])
        id_value_list = [id_info1, id_info5, id_info6, id_info7]
        fill_info(sid, uid, id_value_list, data, URL[test_fms])
        assert check_admin_fields(
            sid, uid, "Инфо1", URL[test_fms])[1] == data.get(
            "РДДБ"
        )
        assert check_admin_fields(
            sid, uid, "Инфо5", URL[test_fms])[1] == data.get(
            "Специалист"
        )
        assert check_admin_fields(
            sid, uid, "Инфо6", URL[test_fms])[1] == data.get(
            "ИНН"
        )
        assert check_admin_fields(
            sid, uid, "Инфо7", URL[test_fms])[1] == data.get(
            "КПП"
        )


def test_upd_inn_field():
    data = read_json("tests/fixtures/fill_inn")
    imei = data.get("IMEI")
    inn = data.get("ИНН")
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        uid = get_object_id(sid, imei, URL[test_fms])
        id_field = check_admin_fields(sid, uid, "ИНН", URL[test_fms])[0]
        upd_inn_field(sid, uid, id_field, inn, URL[test_fms])
        value_field = check_admin_fields(sid, uid, "ИНН", URL[test_fms])[1]
        assert inn == value_field


def test_get_user_id():
    for test_fms in range(*iteration[fms]):
        url = URL[test_fms]
        token = TOKEN[test_fms]
        uid = get_user_id(url, token)
        assert USER_ID[test_fms] == str(uid)


def test_get_new_token():
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        app_name = f"test FMS {test_fms}"
        new_token = __get_new_token(sid, URL[test_fms], app_name)
        assert len(new_token) == 72


def test_update_name():
    old_name = read_json("tests/fixtures/one_object")
    imei = old_name.get("geozone_imei")
    nname = "belousov_new"
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        uid = get_object_id(sid, imei, URL[test_fms])
        new_name = update_name(sid, URL[test_fms], uid, nname)
        check_name = (
            get_object_info_by_imei(
                sid, imei, URL[test_fms]).get("items")[0].get("nm")
        )
        assert check_name == new_name.get("nm")


def test_id_fields():
    obj = read_json("tests/fixtures/one_object")
    imei = obj.get("geozone_imei")
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        uid = get_object_id(sid, imei, URL[test_fms])
        res = id_fields(sid, uid, URL[test_fms])
        assert len(res) == 7
        assert None not in res.values()


def test_delete_object():
    mask = "belousov"
    for test_fms in range(*iteration[fms]):
        sid = get_ssid(URL[test_fms], TOKEN[test_fms])
        obj = get_object_info_by_name(sid, mask, URL[test_fms])
        for uid in obj.get("items"):
            result = delete_object(sid, URL[test_fms], uid.get("id"))
            assert len(result) == 0
