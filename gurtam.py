import requests
import random
import json


# https://fms4.csat.ru/?login&token=3469b1a0dfc158c6d35ea9ca7475238b68DB86E7A5D10C1466D4827A7F483E85A750D6A5

URL = 'https://fms4.csat.ru/wialon/ajax.html'
TOKEN = '3469b1a0dfc158c6d35ea9ca7475238b68DB86E7A5D10C1466D4827A7F483E85A750D6A5'
CARKADE = {
    '1Каркаде': 157,
    '1Каркаде Абхазия': 42928,
    '1Каркаде актив': 38071,
    '1Каркаде Беларусь': 42932,
    '1Каркаде Грузия': 42929,
    '1Каркаде грузовые': 40188,
    '1Каркаде Казахстан': 42930,
    '1Каркаде легковые': 40187,
    '1Каркаде разбивка 16': 47114,
    '1Каркаде спецтехника': 53014,
    '1Каркаде Украина': 42931,
}
GPBAL = {
    '1ГПБАЛ': 28044,
    '1ГПБАЛ Въезд в Азербайджан': 44412,
    '1ГПБАЛ Въезд в Беларусь': 44405,
    '1ГПБАЛ Въезд в Грузию': 44411,
    '1ГПБАЛ Въезд в Казахстан': 44406,
    '1ГПБАЛ Въезд в Китай': 44407,
    '1ГПБАЛ Въезд в Монголию': 44408,
    '1ГПБАЛ Въезд в Прибалтику': 44409,
    '1ГПБАЛ Въезд в Украину': 44404,
    '1ГПБАЛ Въезд в Финляндию': 44410,
    '1ГПБАЛ Выезд за пределы РФ': 44413,
    '1ГПБАЛ грузовые': 41343,
    '1ГПБАЛ звонки': 35754,
    '1ГПБАЛ легковые': 41342,
    '1ГПБАЛ Риск': 40166,
    '1ГПБАЛ спецтехника': 53012,
}

EVO = {
    '1Эволюция': 28040,
    '1Эволюция Армения': 49371,
    '1Эволюция в движение зажигание': 28248,
    '1Эволюция Грузия': 47767,
    '1Эволюция грузовые': 40577,
    '1Эволюция Казахстан': 47768,
    '1Эволюция Киргизия': 47769,
    '1Эволюция Латвия': 47770,
    '1Эволюция легковая': 40576,
    '1Эволюция Литва': 47771,
    '1Эволюция Польша': 47772,
    '1Эволюция Приближение к Казахстану': 48072,
    '1Эволюция спецтехника': 53013,
    '1Эволюция Таджикистан': 47773,
    '1Эволюция Туркменистан': 47774,
    '1Эволюция уведомления': 28771,
    '1Эволюция Узбекистан': 47775,
    '1Эволюция Украина': 47776,
    '1Эволюция Финляндия': 47777,
    '1Эволюция Эстония': 47779,
    '1Эволюция Южная Осетия': 47780,
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
    """Finds object and returns id.

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


def search_groups(ssid: str, group_name: str) -> dict:
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
        return group['items'][0].get('u')
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

    a = search_groups(ssid=sid, group_name='belousov_12')
   