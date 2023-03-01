import requests
import random
import json


# https://fms4.csat.ru/?login&token=3469b1a0dfc158c6d35ea9ca7475238b68DB86E7A5D10C1466D4827A7F483E85A750D6A5

URL = 'https://fms4.csat.ru/wialon/ajax.html'
TOKEN = '3469b1a0dfc158c6d35ea9ca7475238b68DB86E7A5D10C1466D4827A7F483E85A750D6A5'
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
    """Getting the User Agent.

    The function has a list of User Agents, chooses a random 
    one from the list and returns a dictionary.

    Returns:
        dict: {User-Agent: RandomUserAgent}
    """
    user_agent_list = [
        'Safari/537.36 OPR/26.0.1656.60',
        'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 '
        '(maverick) Firefox/3.6.10',
        'Chrome/39.0.2171.71 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 '
        '(KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    ]
    UserAgent = random.choice(user_agent_list)
    header = {'User-Agent': UserAgent}
    return header


def get_ssid() -> str:
    """Authorization by token and getting the session number.

    The function authorizes with a token on fms4, receives a json file in response, 
    from where it takes eid and returns it as a string, 
    The function authorizes with a fms4 token, receives a json file in response, 
    from where it takes eid and returns it as a string

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
    """Finds object by imei and returns object id.

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
            "flags": 1,
            "from": 0,
            "to": 0
        }),
        "sid": ssid
    }

    response = requests.post(URL, params=param)
    return response.json().get('items')[0].get('id') if response.json().get('items') != [] else -1


def update_param(ssid):

    CONTRACT_NAME = {
        'svc': 'item/update_name',
        'params': json.dumps({"itemId": 53143, "name": 'belousov_t'}),
        'sid': sid
    }

    IMEI = {
        'svc': 'item/update_admin_field',
        'params': json.dumps({"itemId": 53143, "id": 1, "callMode": 'update', "n": 'geozone_imei', "v": '161100060801269'}),
        'sid': sid
    }

    SIM = {
        'svc': 'item/update_admin_field',
        'params': json.dumps({"itemId": 53143, "id": 2, "callMode": 'update', "n": 'geozone_sim', "v": '+79111234567'}),
        'sid': sid
    }

    VIN = {
        'svc': 'item/update_custom_field',
        'params': json.dumps({'itemId': 53143, 'id': 1, 'callMode': 'update', 'n': 'Vin', 'v': 'XXXXXXXXXX01'}),
        'sid': sid
    }

    INFO4 = {
        'svc': 'item/update_admin_field',
        'params': json.dumps({"itemId": 53143, "id": 6, "callMode": 'update', "n": 'Инфо4', "v": 'Да'}),
        'sid': sid
    }

    MARCK = {
        'svc': 'item/update_custom_field',
        'params': json.dumps({'itemId': 53143, 'id': 2, 'callMode': 'update', 'n': 'Марка', 'v': 'U'}),
        'sid': sid
    }

    MODEL = {
        'svc': 'item/update_custom_field',
        'params': json.dumps({'itemId': 53143, 'id': 3, 'callMode': 'update', 'n': 'Модель', 'v': 'Y'}),
        'sid': sid
    }

    PIN = {
        'svc': 'item/update_admin_field',
        'params': json.dumps({"itemId": 53143, "id": 7, "callMode": 'update', "n": 'Пин', "v": '2113564'}),
        'sid': sid
    }

    DISTANCE = {
        'svc': 'unit/update_mileage_counter',
        'params': json.dumps({'itemId': 53143, 'newValue': 0}),
        'sid': sid
    }

    ENGIN_HOURS = {
        'svc': 'unit/update_eh_counter',
        'params': json.dumps({'itemId': 53143, 'newValue': 0}),
        'sid': sid
    }


def search_groups_by_name(ssid: str, group_name: str) -> dict:
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
    """_summary_

    Args:
        ssid (str): _description_
        group_id (int): _description_

    Returns:
        dict: _description_
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
    """Getting ID group

    Args:
        group (dict): json object with meta data about group

    Returns:
        int|str: if group finded, return group id as integer, if not finded return traceback 'this is group is not finded'
    """
    try:
        return group['items'][0].get('id')
    except IndexError as e:
        return 'Группа не найдена'


def group_unit_list(group: dict) -> list | str:
    """Getting group unit list

    Args:
        group (dict): json object with meta data about group

    Returns:
        list|str: if group finded, return unit list as [123, 456, ...etc], if not finded return traceback 'this is list empty'
    """
    try:
        if 'items' in group:
            return group['items'][0].get('u')
        else:
            return group['item'].get('u')
    except IndexError as e:
        return 'Список пуст'


def add_groups(ssid: str, leasing_id: int | str, leasing_unit_list: list[int], added_unit: list[int]):
    """_summary_

    Args:
        ssid (str): _description_
        leasing_id (int | str): _description_
        leasing_unit_list (list[int]): _description_
        added_unit (int): _description_
    """
    param = {
        'svc': 'unit_group/update_units',
        'params': json.dumps({"itemId": leasing_id, "units": leasing_unit_list + added_unit}),
        'sid': ssid
    }
    requests.post(URL, params=param)


def remove_groups(ssid: str, leasing_id: int | str, leasing_unit_list: list[int], removed_unit: list[int]):
    """_summary_

    Args:
        ssid (str): _description_
        leasing_id (int | str): _description_
        leasing_unit_list (list[int]): _description_
        removed_unit (list[int]): _description_
    """
    for unit in removed_unit:
        leasing_unit_list.remove(unit)
    param = {
        'svc': 'unit_group/update_units',
        'params': json.dumps({"itemId": leasing_id, "units": leasing_unit_list}),
        'sid': ssid
    }

    requests.post(URL, params=param)


if __name__ == '__main__':

    sid = get_ssid()
