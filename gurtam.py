"""Base func for work with Gurtam API."""
import json
import os
import random

from dotenv import load_dotenv

from hardware import create_object_with_all_params

import requests
from requests import Response


load_dotenv()

URL = os.getenv('URL')
TOKEN = os.getenv('TOKEN')

AUTO = [40187, 41342, 40576]
TRUCK = [40188, 41343, 40577]
SPEC = [53014, 53012, 53013]
RISK = [40166, 59726]


def get_header() -> dict:
    """Get the User Agent.

    The function has a list of User Agents, chooses a random
    one from the list and returns a dictionary.

    Returns:
        dict: {User-Agent: RandomUserAgent}
    """
    user_agent_list = [
        'Safari/537.36 OPR/26.0.1656.60',
        '(maverick) Firefox/3.6.10',
        'Chrome/39.0.2171.71 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 '
        '(KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    ]
    user_agent = random.choice(user_agent_list)
    header = {'User-Agent': user_agent}
    return header


def get_ssid() -> str:
    """Authorize by token and getting the session number.

    The function authorizes with a token on fms4,
    receives a json file in response,
    from where it takes eid and returns it as a string,

    Returns:
        str: eid - session id on vialon
    """
    param = {
        "svc": "token/login",
        "params": json.dumps({"token": TOKEN})
    }
    response = requests.post(URL, data=param, headers=get_header())
    return response.json().get('eid')


def get_object_info_by_imei(ssid: str, imei: str) -> dict:
    """Search object by imei.

    Args:
        ssid (str): session id
        imei (str): unique id object

    Returns:
        dict: meta data about object
    """
    param = {
        "svc": "core/search_items",
        "params": json.dumps({
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_unique_id",
                "propValueMask": "*{0}*".format(imei),
                "sortType": "sys_name"
            },
            "force": 1,
            "flags": 4611686018427387903,
            "from": 0,
            "to": 0
        }),
        "sid": ssid
    }

    response = requests.post(URL, data=param)
    return response.json()


def get_object_info_by_name(ssid: str, object_name: str) -> dict:
    """Search object by imei.

    Args:
        ssid (str): session id
        object_name (str): partial or full object name.

    Returns:
        dict: meta data about object
    """
    param = {
        "svc": "core/search_items",
        "params": json.dumps({
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_name",
                "propValueMask": "*{0}*".format(object_name),
                "sortType": "sys_name"
            },
            "force": 1,
            "flags": 4611686018427387903,
            "from": 0,
            "to": 0
        }),
        "sid": ssid
    }

    response = requests.post(URL, data=param)
    return response.json()


def get_object_id(ssid: str, imei: str) -> int:
    """Find object by imei and returns object id.

    The function finds an object in the database by imei and returns id.
    If the object is not found, the function returns -1

    Args:
        ssid (str): current connection id, session number
        imei (str): unique id your equipment

    Returns:
        int: unique id avl_unit or -1
    """
    response = get_object_info_by_imei(ssid, imei)
    if response.get('items'):
        return response.get('items')[0].get('id')
    return -1


def create_custom_fields(ssid: str, unit_id: int) -> None:
    """Create of arbitrary fields in the object card on the vialon.

    The function finds the object by IMEI,
    checks the presence of the necessary fields in the "Custom fields" tab
    if the field is missing, the function creates it.

    Args:
        ssid (str): session id
        unit_id (int): object id on vialon
    """
    admin_fields = (
        'geozone_imei',
        'geozone_sim',
        'Инфо1',
        'Инфо2',
        'Инфо3',
        'Инфо4',
        'Пин'
    )
    item_fields = ('Vin', 'Марка', 'Модель')
    id_field = {
        'geozone_imei': 1,
        'geozone_sim': 2,
        'Инфо1': 3,
        'Инфо2': 4,
        'Инфо3': 5,
        'Инфо4': 6,
        'Пин': 7,
        'Vin': 1,
        'Марка': 2,
        'Модель': 3
    }

    for field in admin_fields:
        param = {
            "svc": "core/search_item",
            "params": json.dumps({
                "id": unit_id,
                "flags": 128
            }),
            "sid": ssid
        }
        response = requests.post(URL, data=param)
        if field not in response.text:
            create_field = {
                'svc': 'item/update_admin_field',
                'params': json.dumps({
                    "itemId": unit_id,
                    "id": id_field.get(field),
                    "callMode": 'create',
                    "n": '{0}'.format(field),
                    "v": ''}),
                'sid': ssid
            }
            requests.post(URL, data=create_field)
        else:
            continue

    for field in item_fields:
        param = {
            "svc": "core/search_item",
            "params": json.dumps({
                "id": unit_id,
                "flags": 8
            }),
            "sid": ssid
        }
        response = requests.post(URL, data=param)
        if field not in response.text:
            create_field = {
                'svc': 'item/update_custom_field',
                'params': json.dumps({
                    'itemId': unit_id,
                    'id': id_field.get(field),
                    'callMode': 'create',
                    'n': '{0}'.format(field),
                    'v': ''}),
                'sid': ssid
            }
            requests.post(URL, data=create_field)
        else:
            continue


def update_param(session_id: str, unit_id: int, new_value: dict, info4id: int):
    """Fill object fields with new parameters.

    The function accepts a session ID, an object ID,
    and a dictionary with data to fill in the required fields of the object.
    The data is passed using the requests object's post method,
    the function returns nothing.

    Args:
        session_id (str): session id
        unit_id (int): gurtam object id
        new_value (dict): dictionary with new params
    """
    contract_name = {
        'svc': 'item/update_name',
        'params': {
            "itemId": unit_id,
            "name": new_value.get('ДЛ').strip()},
        'sid': session_id
    }

    imei = {
        'svc': 'item/update_admin_field',
        'params': {
            "itemId": unit_id,
            "id": 1,
            "callMode": 'update',
            "n": 'geozone_imei',
            "v": new_value.get('ИМЕЙ')},
        'sid': session_id
    }

    sim = {
        'svc': 'item/update_admin_field',
        'params': {
            "itemId": unit_id,
            "id": 2,
            "callMode": 'update',
            "n": 'geozone_sim',
            "v": new_value.get('ТЕЛЕФОН')},
        'sid': session_id
    }

    vin = {
        'svc': 'item/update_custom_field',
        'params': {
            'itemId': unit_id,
            'id': 1,
            'callMode': 'update',
            'n': 'Vin',
            'v': new_value.get('ВИН')},
        'sid': session_id
    }

    info4 = {
        'svc': 'item/update_admin_field',
        'params': {
            "itemId": unit_id,
            "id": info4id,
            "callMode": 'update',
            "n": 'Инфо4',
            "v": new_value.get(
                'ИНФО4'
                ) if new_value.get('ИНФО4') is not None else ''},
        'sid': session_id
    }

    brand = {
        'svc': 'item/update_custom_field',
        'params': {
            'itemId': unit_id,
            'id': 2,
            'callMode': 'update',
            'n': 'Марка',
            'v': new_value.get('МАРКА')},
        'sid': session_id
    }

    model = {
        'svc': 'item/update_custom_field',
        'params': {
            'itemId': unit_id,
            'id': 3,
            'callMode': 'update',
            'n': 'Модель',
            'v': new_value.get('МОДЕЛЬ')},
        'sid': session_id
    }

    pin = {
        'svc': 'item/update_admin_field',
        'params': {
            "itemId": unit_id,
            "id": 7,
            "callMode": 'update',
            "n": 'Пин',
            "v": new_value.get('ПИН')},
        'sid': session_id
    }

    distance = {
        'svc': 'unit/update_mileage_counter',
        'params': {'itemId': unit_id, 'newValue': 0},
        'sid': session_id
    }

    engin_hours = {
        'svc': 'unit/update_eh_counter',
        'params': {'itemId': unit_id, 'newValue': 0},
        'sid': session_id
    }

    param = {'svc': 'core/batch',
             'params': json.dumps({
                 "params": [contract_name,
                            imei,
                            sim,
                            vin,
                            info4,
                            brand,
                            model,
                            pin,
                            distance,
                            engin_hours
                            ],
                 "flags": 0}),
             'sid': session_id
             }
    print('start check fields')
    print(f'start update object fields {new_value.get("ПИН")}')
    requests.post(URL, data=param)


def get_log(response: Response, param: dict, value: dict):
    """Write error to a log file.

    Args:
        response (str): response object in string
        param (dict): parameter dictionary that is passed to the request
        value (dict): dictionary with data to write the object
    """
    log_text = 'Запись параметра: {0} - объекта:\
        {1} - завершена с ошибкой. Код ошибки - {2} \n'
    if response.status_code != 200:
        with open('logging/update_error.txt', 'a') as log:
            log.write(
                log_text.format(
                    param.get('svc'),
                    value.get('ДЛ'),
                    response.text)
            )


def search_groups_by_name(ssid: str, group_name: str) -> dict:
    """Find groups by name.

    Args:
        ssid (str): session id
        group_name (str): the name or part of the name of the group
        we want to find

    Returns:
        dict: dictionari with group names
        and id's that matched by name
    """
    param = {
        "svc": "core/search_items",
        "params": json.dumps({
            "spec": {
                "itemsType": "avl_unit_group",
                "propName": "sys_name",
                "propValueMask": "*{0}*".format(group_name),
                "sortType": "sys_name"
            },
            "force": 1,
            "flags": 1,
            "from": 0,
            "to": 0
        }),
        "sid": ssid
    }
    response = requests.post(URL, data=param)
    return response.json()


def search_group_by_id(ssid: str, group_id: int) -> dict:
    """Find group by id.

    Args:
        ssid (str): session id
        group_id (int): group id

    Returns:
        dict: a dictionary with the name of the group,
        the id of the group,
        the list of id objects that belong to this group, etc.
    """
    param = {
        'svc': 'core/search_item',
        'params': json.dumps({"id": group_id,
                             "flags": 1}),
        'sid': ssid
    }

    response = requests.post(URL, data=param)
    return response.json()


def get_id_group(group: dict) -> int | str:
    """Get ID group.

    Args:
        group (dict): json object with metadata about group

    Returns:
        int|str: if group finded, return group id as integer,
        if not finded return traceback 'this is group is not finded'
    """
    try:
        return group['items'][0].get('id')
    except IndexError:
        return 'Группа не найдена'


def get_group_unit_list(group: dict) -> list | str:
    """Get group unit list.

    Args:
        group (dict): json object with metadata about group

    Returns:
        list|str: if group finded, return unit list id as [123, 456, ...etc],
        if not finded return traceback 'this is list empty'
    """
    try:
        if 'items' in group:
            return group['items'][0].get('u')
        else:
            return group['item'].get('u')
    except IndexError:
        return 'Список пуст'


def add_groups(
    ssid: str,
    leasing_id: int | str,
    leasing_unit_list: list[int],
    added_unit: list[int]
):
    """Add objects to a group.

    Args:
        ssid (str): session id
        leasing_id (int | str): id group
        leasing_unit_list (list[int]): list of current id group objects
        added_unit (int): list of id objects to add
    """
    param = {
        'svc': 'unit_group/update_units',
        'params': json.dumps({
            "itemId": leasing_id,
            "units": leasing_unit_list + added_unit}),
        'sid': ssid
    }
    requests.post(URL, data=param)


def remove_groups(ssid: str, removed_unit_list: list[int]) -> None:
    """Remove unit from a group.

    Args:
        ssid (str): session id
        removed_unit_list (list[int]): list of id objects to remove
    """
    group_name = search_groups_by_name(
        ssid,
        removed_unit_list[0].get('ГРУППА')
    )
    group_id = [group.get('id') for group in group_name.get('items')]
    remove_unit_id = [
        get_object_id(ssid, unit.get('ИМЕЙ')) for unit in removed_unit_list
    ]
    for index_group, group in enumerate(group_id):
        group_data = search_group_by_id(ssid, group)
        group_list = get_group_unit_list(group_data)
        for index_unit, unit in enumerate(remove_unit_id):
            if unit in group_list:
                group_list.remove(unit)
            else:
                with open('logging/unremoved.log', 'a') as log:
                    text = 'not found {0} in {1}\n'
                    imei = removed_unit_list[index_unit].get('ИМЕЙ')
                    glog_name = group_name.get('items')[index_group].get('nm')
                    log.write(text.format(imei, glog_name))
                continue

        param = {
            'svc': 'unit_group/update_units',
            'params': json.dumps({
                "itemId": group,
                "units": group_list}),
            'sid': ssid
        }

        requests.post(URL, data=param)


def create_object(sid: str, unit_id: int, unit) -> None:
    """Check the presence of an object on the vialon.

    Checking dictionary objects by IMEI for presence on the Vialon portal
    If the object is missing, the object is written to the log file and the
    object is created on the portal.
    An object is created based on the type of its equipment.
    To create a separate function is used.

    Args:
        data (dict): dictionary of objects
    """
    obj_id = create_object_with_all_params(sid, unit)
    create_custom_fields(sid, obj_id)
    with open('logging/import_report.log', 'a') as log:
        log.write('{0} - не найден\n'.format(unit.get('ИМЕЙ')))
    return obj_id


def group_update(data: dict) -> None:
    """Update list of objects in groups.

    The function loops through the list of objects and sorts them into lists
    to add to a specific group.
    There are several specific groups: cars, trucks, special equipment, risky.
    Here is also a group where all objects are added.
    Then the function loops through all the groups that are found by the
    keyword and adds objects from the list with all objects.
    If there is a group, which is a special group, then objects from a special
    list are added to it.

    Args:
        data (dict): dictionary with data on objects
    """
    sid = get_ssid()
    truck = []
    auto = []
    special = []
    all_unit = []
    risk_auto = []

    for unit in data:
        all_unit.append(unit.get('uid'))
        if unit.get('ТИП') == str(0):
            auto.append(unit.get('uid'))
        elif unit.get('ТИП') == str(1):
            truck.append(unit.get('uid'))
        elif unit.get('ТИП') == str(2):
            special.append(unit.get('uid'))
        if unit.get('РИСК') == (9):
            risk_auto.append(unit.get('uid'))

    finded_group = search_groups_by_name(
        sid, data[0].get('ЛИЗИНГ')).get('items')
    print('start update groups')
    for group in finded_group:
        id_group = group.get('id')
        leasing_unit_list = group.get('u')
        if id_group in AUTO:
            add_groups(sid, id_group, leasing_unit_list, auto)
        elif group.get('id') in TRUCK:
            add_groups(sid, id_group, leasing_unit_list, truck)
        elif group.get('id') in SPEC:
            add_groups(sid, id_group, leasing_unit_list, special)
        elif group.get('id') in RISK:
            add_groups(sid, id_group, leasing_unit_list, risk_auto)
        else:
            add_groups(sid, id_group, leasing_unit_list, all_unit)


def update_group_by_mask(ssid: str, list_imei: list[dict]) -> int:
    """Update list objects in groups by mask.

    The function takes a list of dictionaries, in the format
    {'IMEI': 1234567890, 'Группа': 'Cardade'},
    where key IMEI - contains the value of unique block code,
    the Группа key - contains the name of the group in which you want
    to update the list of objects.
    To effectively update objects in a group, the list must contain the value
    of the Group key with the same mask to update objects in only one group at
    a time.
    For acceleration, the script will take the group of the first dictionary
    as the basis.

    Args:
        ssid (str): session id
        list_imei (list[dict]): list of objects imei

    Returns:
        If the operation of updating the list of objects in the group
        is completed successfully, the script returns 0,
        if it fails, it returns -1
    """
    upload_obj_id_list = []
    group_by_mask = search_groups_by_name(ssid, list_imei[0].get('Группа'))

    id_group = group_by_mask.get('items')[0].get('id')
    actual_object_id_list = group_by_mask.get('items')[0].get('u')
    print('group_id -', id_group)
    for object_id in list_imei:
        object_id = get_object_id(ssid, object_id.get('IMEI'))
        if object_id > 0:
            upload_obj_id_list.append(object_id)
        else:
            continue
    try:
        add_groups(ssid, id_group, actual_object_id_list, upload_obj_id_list)
    except Exception as e:
        print(e)
        return -1
    return 0


def fill_info5(ssid: str, unit_id: int, field_id: int, info_for_fill: str):
    info5 = {
        'svc': 'item/update_admin_field',
        'params': json.dumps({
            "itemId": unit_id,
            "id": field_id,
            "callMode": 'update',
            "n": 'Инфо5',
            "v": info_for_fill}),
        'sid': ssid
    }
    requests.post(URL, data=info5)


def check_create_info5(ssid: str, unit_id: int) -> int:
    param = {
        "svc": "core/search_item",
        "params": json.dumps({
            "id": unit_id,
            "flags": 128
        }),
        "sid": ssid
    }
    response = requests.post(URL, data=param).json().get('item').get('aflds')

    for info in response.items():
        if 'Инфо5' not in info[1].get('n'):
            continue
        else:
            return info[1].get('id')

    info5 = {
        'svc': 'item/update_admin_field',
        'params': json.dumps({
            "itemId": unit_id,
            "id": 0,
            "callMode": 'create',
            "n": 'Инфо5',
            "v": ''}),
        'sid': ssid
    }
    response = requests.post(URL, data=info5).json()[1].get('id')
    return response


def check_info(ssid: str, unit_id: int, info_name: str) -> int:
    param = {
        "svc": "core/search_item",
        "params": json.dumps({
            "id": unit_id,
            "flags": 128
        }),
        "sid": ssid
    }
    response = requests.post(URL, data=param).json().get('item').get('aflds')

    for info in response.items():
        if info_name not in info[1].get('n'):
            continue
        else:
            return info[1].get('id'), info[1].get('v')

    info = {
        'svc': 'item/update_admin_field',
        'params': json.dumps({
            "itemId": unit_id,
            "id": 0,
            "callMode": 'create',
            "n": info_name,
            "v": ''}),
        'sid': ssid
    }
    response = requests.post(URL, data=info)
    return response.json()[1].get('id'), response.json()[1].get('v')


def fill_info(
    ssid: str,
    unit_id: int,
    field_id_value: int,
    data: dict
):
    info1 = {
        'svc': 'item/update_admin_field',
        'params': {
            "itemId": unit_id,
            "id": field_id_value[0][0],
            "callMode": 'update',
            "n": 'Инфо1',
            "v": data.get('РДДБ') if data.get('РДДБ') is not None else field_id_value[0][1]
        },
        'sid': ssid
    }

    info5 = {
        'svc': 'item/update_admin_field',
        'params': {
            "itemId": unit_id,
            "id": field_id_value[1][0],
            "callMode": 'update',
            "n": 'Инфо5',
            "v": data.get('Специалист') if data.get('Специалист') is not None else field_id_value[1][1]},
        'sid': ssid
    }

    info6 = {
        'svc': 'item/update_admin_field',
        'params': {
            "itemId": unit_id,
            "id": field_id_value[2][0],
            "callMode": 'update',
            "n": 'Инфо6',
            "v": data.get('ИНН') if data.get('ИНН') is not None else field_id_value[2][1]},
        'sid': ssid
    }

    info7 = {
        'svc': 'item/update_admin_field',
        'params': {
            "itemId": unit_id,
            "id": field_id_value[3][0],
            "callMode": 'update',
            "n": 'Инфо7',
            "v": data.get('КПП') if data.get('КПП') is not None else field_id_value[3][1]},
        'sid': ssid
    }

    param = {'svc': 'core/batch',
             'params': json.dumps({
                 "params": [
                    info1,
                    info5,
                    info6,
                    info7
                 ],
                 "flags": 0}),
             'sid': ssid
             }
    requests.post(URL, data=param)


def upd_inn_field(ssid: str, unit_id: int, field_id: int, inn_value: str):
    inn = {
        'svc': 'item/update_admin_field',
        'params': json.dumps({
            "itemId": unit_id,
            "id": field_id,
            "callMode": 'update',
            "n": 'ИНН',
            "v": inn_value}),
        'sid': ssid
    }
    requests.post(URL, data=inn)
