"""Base func for work with Gurtam API."""
import requests
import random
import json
import os
from dotenv import load_dotenv
from requests import Response

load_dotenv()

# https://fms4.csat.ru/?login&token=3469b1a0dfc158c6d35ea9ca7475238b68DB86E7A5D10C1466D4827A7F483E85A750D6A5

URL = os.getenv('URL')
TOKEN = os.getenv('TOKEN')
CARKADE = {  # 0 - легковые, 1 - грузовые, 2 - спец.техника, 9 - рисковые
    '1': 40188,
    '0': 40187,
    '2': 53014,
}
GPBAL = {
    '1': 41343,
    '0': 41342,
    '9': 40166,
    '2': 53012,
}

EVO = {
    '1': 40577,
    '0': 40576,
    '2': 53013,
}


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
        str: eid
    """
    param = {
        "svc": "token/login",
        "params": json.dumps({"token": TOKEN})
    }
    response = requests.get(URL, params=param, headers=get_header())
    return response.json().get('eid')


def search_object(ssid: str, imei: str) -> int:
    """Find object by imei and returns object id.

    The function finds an object in the database by imei and returns id.
    If the object is not found, the function returns -1

    Args:
        ssid (str): current connection id, session number
        imei (str): unique id your equipment

    Returns:
        int: unique id avl_unit or -1
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

    response = requests.post(URL, params=param)
    if response.json().get('items'):
        return response.json().get('items')[0].get('id')
    return -1


def update_param(session_id: str, unit_id: int, new_value: dict):
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
        'params': json.dumps({
            "itemId": unit_id,
            "name": '{0}'.format(new_value.get('DL'))}),
        'sid': session_id
    }

    imei = {
        'svc': 'item/update_admin_field',
        'params': json.dumps({
            "itemId": unit_id,
            "id": 1,
            "callMode": 'update',
            "n": 'geozone_imei',
            "v": '{0}'.format(new_value.get('IMEI'))}),
        'sid': session_id
    }

    sim = {
        'svc': 'item/update_admin_field',
        'params': json.dumps({
            "itemId": unit_id,
            "id": 2,
            "callMode": 'update',
            "n": 'geozone_sim',
            "v": '{0}'.format(new_value.get('SIM'))}),
        'sid': session_id
    }

    vin = {
        'svc': 'item/update_custom_field',
        'params': json.dumps({
            'itemId': unit_id,
            'id': 1,
            'callMode': 'update',
            'n': 'Vin',
            'v': '{0}'.format(new_value.get('VIN'))}),
        'sid': session_id
    }

    info4 = {
        'svc': 'item/update_admin_field',
        'params': json.dumps({
            "itemId": unit_id,
            "id": 6,
            "callMode": 'update',
            "n": 'Инфо4',
            "v": '{0}'.format(new_value.get('INFO4'))}),
        'sid': session_id
    }

    brand = {
        'svc': 'item/update_custom_field',
        'params': json.dumps({
            'itemId': unit_id,
            'id': 2,
            'callMode': 'update',
            'n': 'Марка',
            'v': '{0}'.format(new_value.get('BRAND'))}),
        'sid': session_id
    }

    model = {
        'svc': 'item/update_custom_field',
        'params': json.dumps({
            'itemId': unit_id,
            'id': 3,
            'callMode': 'update',
            'n': 'Модель',
            'v': '{0}'.format(new_value.get('MODEL'))}),
        'sid': session_id
    }

    pin = {
        'svc': 'item/update_admin_field',
        'params': json.dumps({
            "itemId": unit_id,
            "id": 7,
            "callMode": 'update',
            "n": 'Пин',
            "v": '{0}'.format(new_value.get('PIN'))}),
        'sid': session_id
    }

    distance = {
        'svc': 'unit/update_mileage_counter',
        'params': json.dumps({'itemId': unit_id, 'newValue': 0}),
        'sid': session_id
    }

    engin_hours = {
        'svc': 'unit/update_eh_counter',
        'params': json.dumps({'itemId': unit_id, 'newValue': 0}),
        'sid': session_id
    }

    param_list = [contract_name, imei, sim, vin, info4,
                  brand, model, pin, distance, engin_hours]

    for param in param_list:
        response = requests.post(URL, params=param)
        get_log(response, param, new_value)


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
        with open('log.txt', 'a') as log:
            log.write(
                log_text.format(
                    param.get('svc'),
                    value.get('DL'),
                    response.text)
            )


def search_groups_by_name(ssid: str, group_name: str) -> dict:
    """Find groups by name.

    Args:
        ssid (str): session id
        group_name (str): the name or part of the name of the group
        we want to find

    Returns:
        dict: list of dictionaries with group names
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
    response = requests.get(URL, params=param)
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

    response = requests.get(URL, params=param)
    return response.json()


def id_group(group: dict) -> int | str:
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


def group_unit_list(group: dict) -> list | str:
    """Get group unit list.

    Args:
        group (dict): json object with metadata about group

    Returns:
        list|str: if group finded, return unit list as [123, 456, ...etc],
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
    requests.post(URL, params=param)


def remove_groups(
    ssid: str,
    leasing_id: int | str,
    leasing_unit_list: list[int],
    removed_unit: list[int]
):
    """Remove unit from a group.

    Args:
        ssid (str): session id
        leasing_id (int | str): id group
        leasing_unit_list (list[int]): list of current id group objects
        removed_unit (list[int]): list of id objects to remove
    """
    for unit in removed_unit:
        leasing_unit_list.remove(unit)
    param = {
        'svc': 'unit_group/update_units',
        'params': json.dumps({
            "itemId": leasing_id,
            "units": leasing_unit_list}),
        'sid': ssid
    }

    requests.post(URL, params=param)


if __name__ == '__main__':
    # test id object [50597, 53143, 53209]
    sid = get_ssid()
    # a = search_object(imei='401010053722801721', ssid=sid)
    # b = search_groups_by_name(sid, 'belousov')
    print()
    json_ = [{
        'DL': 'belousov_belousov',
        'IMEI': '401010053722801721',
        'SIM': '+79117084888',
        'VIN': '0DLGRT124566IO90',
        'INFO4': '',
        'BRAND': 'OMODA',
        'MODEL': '7000',
        'PIN': '213123',
        'TYPE': '0',
        'RISK': '',
        'LEASING': 'belousov_13',
        'CONFIG': 'FMB130',
    }]

    # b = update_param(sid, 50597, json_[0])
    print(search_object(sid, '401010053722801721'))
