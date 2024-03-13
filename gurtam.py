"""Base func for work with Gurtam API."""
import json
import os
import random

from config import logger, fstart_stop

from collections import defaultdict

from dotenv import load_dotenv

from hardware import create_object_with_all_params

import requests


load_dotenv()

URL = os.getenv('URL')
TOKEN = os.getenv('TOKEN')

AUTO = (40187, 41342, 40576)
TRUCK = (40188, 41343, 40577)
SPEC = (53014, 53012, 53013)
RISK = (40166, 59726)
REQUIRED_GROUPS = (78875,)
CUSTOM_FIELDS = ('Vin', 'Марка', 'Модель')


@fstart_stop
@logger.catch
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


@fstart_stop
@logger.catch
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
    logger.debug('получение id сессии')
    logger.debug(f'URL: {response.url}')
    logger.debug(f'результат id сессии: {response.json().get("eid")}')
    return response.json().get('eid')


@fstart_stop
@logger.catch
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
    logger.debug(f'получение данных об объекте по имей: "{imei}"')
    logger.debug(f'URL: {response.url}')
    logger.debug(f'параметры URL: {param}')
    logger.debug(f'результат: {response.json()}')
    return response.json()


@fstart_stop
@logger.catch
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
    logger.debug(f'получение данных об объекте по его имени: "{object_name}"')
    logger.debug(f'URL: {response.url}')
    logger.debug(f'параметры URL: {param}')
    logger.debug(f'результат: {response.json()}')
    return response.json()


@fstart_stop
@logger.catch
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
    logger.debug(f'получение id объекта: "{imei}"')
    logger.debug('imei отдаётся в обработку функции "get_object_info_by_imei"')
    if response.get('items'):
        logger.debug(f'результат id обекта: {response.get("items")[0].get("id")}')
        return response.get('items')[0].get('id')
    logger.debug('объект не существует, результат: "-1"')
    return -1


@fstart_stop
@logger.catch
def create_custom_fields(ssid: str, unit_id: int) -> None:
    """Create of arbitrary fields in the object card on the vialon.

    The function finds the object by IMEI,
    checks the presence of the necessary fields in the "Custom fields" tab
    if the field is missing, the function creates it.

    Args:
        ssid (str): session id
        unit_id (int): object id on vialon
    """
    logger.debug(f'параметры на входе - ssid: "{ssid}, unit_id: "{unit_id}"')
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
    logger.debug(f'шаблон админ поля: {admin_fields}')
    logger.debug(f'шаблон произвольне поля: {item_fields}')
    logger.debug(f'присвоенные id полям: {id_field}')
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
        logger.debug(f'получени дынных об админ полях: {response.url}, параметры: {param}')
        logger.debug(f'результат: {response.json()}')
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
            logger.debug(f'поле {field} не существует у объкта c id {unit_id}, создать поле, запрос: "requests.post(URL, data=create_field)", параметры: {create_field}')
        else:
            logger.debug(f'поле {field} существует')
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
        logger.debug(f'получение данных о произвольных полях: {response.url}, параметры: {param}')
        logger.debug(f'результат: {response.json()}')
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
            logger.debug(f'поле {field} не существует у объкта c id {unit_id}, создать поле, запрос: "requests.post(URL, data=create_field)", параметры: {create_field}')
        else:
            logger.debug(f'поле {field} существует')
            continue


@fstart_stop
@logger.catch
def update_param(
    session_id: str,
    unit_id: int,
    new_value: dict,
    id_field: dict
) -> None:
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
    logger.debug('входящие параметры:')
    logger.debug(f'id сессии: "{session_id}"')
    logger.debug(f'id объекта: "{unit_id}"')
    logger.debug(f'json с данными для заполнения: "{new_value}"')
    logger.debug(f'id поля Инфо4: "{id_field}"')
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
            "id": id_field.get('geozone_imei'),
            "callMode": 'update',
            "n": 'geozone_imei',
            "v": new_value.get('geozone_imei')},
        'sid': session_id
    }

    sim = {
        'svc': 'item/update_admin_field',
        'params': {
            "itemId": unit_id,
            "id": id_field.get('geozone_sim'),
            "callMode": 'update',
            "n": 'geozone_sim',
            "v": new_value.get('geozone_sim')},
        'sid': session_id
    }

    vin = {
        'svc': 'item/update_custom_field',
        'params': {
            'itemId': unit_id,
            'id': id_field.get('Vin'),
            'callMode': 'update',
            'n': 'Vin',
            'v': new_value.get('Vin')},
        'sid': session_id
    }

    info4 = {
        'svc': 'item/update_admin_field',
        'params': {
            "itemId": unit_id,
            "id": id_field.get('Инфо4'),
            "callMode": 'update',
            "n": 'Инфо4',
            "v": new_value.get(
                'Инфо4'
            ) if new_value.get('Инфо4') is not None else ''},
        'sid': session_id
    }

    brand = {
        'svc': 'item/update_custom_field',
        'params': {
            'itemId': unit_id,
            'id': id_field.get('Марка'),
            'callMode': 'update',
            'n': 'Марка',
            'v': new_value.get('Марка')},
        'sid': session_id
    }

    model = {
        'svc': 'item/update_custom_field',
        'params': {
            'itemId': unit_id,
            'id': id_field.get('Модель'),
            'callMode': 'update',
            'n': 'Модель',
            'v': new_value.get('Модель')},
        'sid': session_id
    }

    pin = {
        'svc': 'item/update_admin_field',
        'params': {
            "itemId": unit_id,
            "id": id_field.get('Пин'),
            "callMode": 'update',
            "n": 'Пин',
            "v": new_value.get('Пин')},
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
    logger.debug(f'передача параметров для обновления полей карточки объект в одном запросе: {param}')
    requests.post(URL, data=param)


@fstart_stop
@logger.catch
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
    logger.debug('вхводящие параметры: ')
    logger.debug(f'id сессии: "{ssid}"')
    logger.debug(f'маска искомой группы: "{group_name}"')
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
    logger.debug(f'URL: {response.url}')
    logger.debug(f'параметры запроса: {param}')
    logger.debug(f'результат выполнения запроса: {response.json()}')
    return response.json()


@fstart_stop
@logger.catch
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
    logger.debug('параметры на входе:')
    logger.debug(f'id сессии: {ssid}')
    logger.debug(f'id искомой группы: {group_id}')
    param = {
        'svc': 'core/search_item',
        'params': json.dumps({"id": group_id,
                             "flags": 1}),
        'sid': ssid
    }

    response = requests.post(URL, data=param)
    logger.debug(f'URL: {response.url}')
    logger.debug(f'параметры запроса: {param}')
    logger.debug(f'результат выполнения запроса: {response.json()}')
    return response.json()


@fstart_stop
@logger.catch
def get_id_group(group: dict) -> int | str:
    """Get ID group.

    Args:
        group (dict): json object with metadata about group

    Returns:
        int|str: if group finded, return group id as integer,
        if not finded return traceback 'this is group is not finded'
    """
    logger.debug(f'параметр на входе: {group}')
    try:
        logger.debug(f'полученный id группы: {group["items"][0].get("id")}')
        return group['items'][0].get('id')
    except IndexError:
        logger.debug('Группа не найдена')
        return 'Группа не найдена'


@fstart_stop
@logger.catch
def get_group_unit_list(group: dict) -> list | str:
    """Get group unit list.

    Args:
        group (dict): json object with metadata about group

    Returns:
        list|str: if group finded, return unit list id as [123, 456, ...etc],
        if not finded return traceback 'this is list empty'
    """
    logger.debug(f'параметр на входе: {group}')
    try:
        if 'items' in group:
            logger.debug(f'результат, список id объектов в группе: {group["items"][0].get("u")}')
            return group['items'][0].get('u')
        else:
            logger.debug(f'результат, список id объектов в группе: {group["item"].get("u")}')
            return group['item'].get('u')
    except IndexError as e:
        logger.debug(f'{e}')
        return 'Список пуст'


@fstart_stop
@logger.catch
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
    logger.debug('параметры на входе:')
    logger.debug(f'id сессии: {ssid}')
    logger.debug(f'id группы: {leasing_id}')
    logger.debug(f'список текущих id объектов в группе: {leasing_unit_list}')
    logger.debug(f'список добавляемых id объектов в группу: {added_unit}')
    param = {
        'svc': 'unit_group/update_units',
        'params': json.dumps({
            "itemId": leasing_id,
            "units": leasing_unit_list + added_unit}),
        'sid': ssid
    }
    logger.debug(f'параметры запроса: {param}')
    requests.post(URL, data=param)


@fstart_stop
@logger.catch
def remove_groups(ssid: str, removed_unit_list: list[int]) -> None:
    """Remove unit from a group.

    Args:
        ssid (str): session id
        removed_unit_list (list[int]): list of id objects to remove
    """
    logger.debug('парметры на входе')
    logger.debug(f'id сессии: {ssid}')
    logger.debug(f'список IMEI объектов на удаление: {removed_unit_list}')
    group_name = search_groups_by_name(
        ssid,
        removed_unit_list[0].get('ГРУППА')
    )
    group_id = [group.get('id') for group in group_name.get('items')]
    remove_unit_id = [
        get_object_id(ssid, unit.get('ИМЕЙ')) for unit in removed_unit_list
    ]
    logger.debug(f'получение json группы: {group_name}')
    logger.debug(f'получение списка id групп по маске: {group_id}')
    logger.debug(f'получение списка id объектов из списка: {remove_unit_id}')
    for index_group, group in enumerate(group_id):
        group_data = search_group_by_id(ssid, group)
        group_list = get_group_unit_list(group_data)
        for index_unit, unit in enumerate(remove_unit_id):
            if unit in group_list:
                group_list.remove(unit)
                logger.debug('если объект есть в группе, удалить из списка объектов')
            else:
                with open('logging/unremoved.log', 'a') as log:
                    text = 'not found {0} in {1}\n'
                    imei = removed_unit_list[index_unit].get('ИМЕЙ')
                    glog_name = group_name.get('items')[index_group].get('nm')
                    log.write(text.format(imei, glog_name))
                    logger.debug(f'объект по IMEI не найден: {imei}')
                continue

        param = {
            'svc': 'unit_group/update_units',
            'params': json.dumps({
                "itemId": group,
                "units": group_list}),
            'sid': ssid
        }
        logger.debug(f'параметры запроса: {param}')
        requests.post(URL, data=param)


@fstart_stop
@logger.catch
def create_object(sid: str, unit_id: int, unit: dict) -> int:
    """Check the presence of an object on the vialon.

    Checking dictionary objects by IMEI for presence on the Vialon portal
    If the object is missing, the object is written to the log file and the
    object is created on the portal.
    An object is created based on the type of its equipment.
    To create a separate function is used.

    Args:
        unit (dict): dictionary of objects

    Returns:
        obj_id: integer object id
    """
    logger.debug(f'id сесиии: {sid}')
    logger.debug(f'id объектка: {unit_id}')
    logger.debug(f'json с данными создаваемого объекта: {unit}')
    obj_id = create_object_with_all_params(sid, unit)
    create_custom_fields(sid, obj_id)
    with open(f'logging/{unit.get("ЛИЗИНГ")}', 'a') as log:
        data_log = """Пин {0} - Имей {1}\n"""
        logger.debug(f'объект создан: {data_log}')
        log.write(data_log.format(unit.get('Пин'), unit.get('geozone_imei')))
    logger.debug(f'результат id созданного объекта: {obj_id}')
    return obj_id


@fstart_stop
@logger.catch
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
    logger.debug(f'аргумент на входе json: {data}')
    sid = get_ssid()
    truck = []
    auto = []
    special = []
    all_unit = []
    risk_auto = []

    logger.debug('распределение объектов в списки по группам')
    for unit in data:
        all_unit.append(unit.get('uid'))
        if unit.get('ТИП') == str(0):
            auto.append(unit.get('uid'))
        elif unit.get('ТИП') == str(1):
            truck.append(unit.get('uid'))
        elif unit.get('ТИП') == str(2):
            special.append(unit.get('uid'))
        if unit.get('РИСК') == str(9):
            risk_auto.append(unit.get('uid'))

    logger.debug(f'колличество грузовых: {len(truck)}')
    logger.debug(f'колличество легковых: {len(auto)}')
    logger.debug(f'колличество спецтехники: {len(special)}')
    logger.debug(f'колличество рисковых: {len(risk_auto)}')

    finded_group = search_groups_by_name(
        sid, data[0].get('ЛИЗИНГ')).get('items')

    logger.debug(f'Ищем группы по маске: {data[0].get("ЛИЗИНГ")}')

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
    for id_group in REQUIRED_GROUPS:
        leasing_unit_list = search_group_by_id(sid, id_group).get('item')['u']
        add_groups(sid, id_group, leasing_unit_list, all_unit)
    logger.debug('Объекты добавлены')


@fstart_stop
@logger.catch
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
    logger.debug('Аргументы на входе:')
    logger.debug(f'id сессии: {ssid}')
    logger.debug(f'список json объектов ИМЕЙ, Группа: {list_imei}')
    upload_obj_id_list = []
    group_by_mask = search_groups_by_name(ssid, list_imei[0].get('Группа'))

    id_group = group_by_mask.get('items')[0].get('id')
    actual_object_id_list = group_by_mask.get('items')[0].get('u')
    for object_id in list_imei:
        object_id = get_object_id(ssid, object_id.get('IMEI'))
        if object_id > 0:
            upload_obj_id_list.append(object_id)
        else:
            continue
    try:
        logger.debug('добавление объектов')
        add_groups(ssid, id_group, actual_object_id_list, upload_obj_id_list)
    except Exception as e:
        logger.debug(e)
        return -1
    return 0


@fstart_stop
@logger.catch
def get_custom_fields(ssid: str, unit_id: int) -> dict:
    """Get custom fields data.

    Args:
        ssid: string sesion id
        unit_id: integer unit/object id

    Returns:
        custom fields: custom fields data in dictionary
    """
    param = {
        "svc": "core/search_item",
        "params": json.dumps({
            "id": unit_id,
            "flags": 8
        }),
        "sid": ssid
    }
    logger.debug('параметры на входе:')
    logger.debug(f'id сессии: {ssid}')
    logger.debug(f'id объекта: {unit_id}')
    logger.debug(f'параметры запроса: {param}')
    response = requests.post(URL, data=param).json().get('item').get('flds')
    logger.debug(f'результат выполнения запроса: {response}')
    return response


@fstart_stop
@logger.catch
def create_custom_field(ssid: str, unit_id: int, info_name: str) -> dict:
    """Create custom field.

    Args:
        ssid: string session id
        unit_id: integer unit/object id
        info_name: field name to create

    Returns:
        fields info: When creating or updating custom fields,
        response format will be ditionary
        {
            "id":<long>, custom field ID
            "n":<text>, name
            "v":<text> value
        }
    """
    info = {
        'svc': 'item/update_custom_field',
        'params': json.dumps({
            "itemId": unit_id,
            "id": 0,
            "callMode": 'create',
            "n": info_name,
            "v": ''}),
        'sid': ssid
    }
    response = requests.post(URL, data=info)
    logger.debug('параметры на входе:')
    logger.debug(f'id сессии: {ssid}')
    logger.debug(f'id объекта: {unit_id}')
    logger.debug(f'имя поля: {info_name}')
    logger.debug(f'параметры запроса: {info}')
    logger.debug('поле создано')
    return response.json()


@fstart_stop
@logger.catch
def check_custom_fields(ssid: str, unit_id: int, info_name: str) -> tuple:
    """Check custom field.

        The function looks for the field id.
        If the field is not found, go to the function of creating
        the required field.
        If the field is found, the function returns a tuple
        in the form of the "field id", the "field value"

    Args:
        ssid: string session id
        unit_id: integer unit/object id
        info_name: field name to check id

    Returns:
        info data: tuple(field id(int), field value(str))
    """
    response = get_custom_fields(ssid, unit_id)

    logger.debug('параметры на входе:')
    logger.debug(f'id сессии: {ssid}')
    logger.debug(f'id объекта: {unit_id}')
    logger.debug(f'имя поля: {info_name}')

    for info in response.items():
        logger.debug(f'обход полей в цикле: {info}')
        if info_name not in info[1].get('n'):
            continue
        else:
            logger.debug('поле найдено')
            logger.debug(f'результат - id поля: {info[1].get("id")}')
            logger.debug(f'результат - значение поля: {info[1].get("v")}')
            return info[1].get('id'), info[1].get('v')
    logger.debug('поле не найдено')
    response = create_custom_field(ssid, unit_id, info_name)
    logger.debug('поле создано')
    logger.debug(f'результат - id поля: {response[1].get("id")}')
    logger.debug(f'результат - значение поля: {response[1].get("v")}')
    return response[1].get('id'), response[1].get('v')


@fstart_stop
@logger.catch
def get_admin_fields(ssid: str, unit_id: int) -> dict:
    """Get admin fields data.

    Args:
        ssid: string sesion id
        unit_id: integer unit/object id

    Returns:
        admin fields: admin fields data in dictionary
    """
    logger.debug('параметры на входе:')
    logger.debug(f'id сессии: {ssid}')
    logger.debug(f'id объекта: {unit_id}')
    param = {
        "svc": "core/search_item",
        "params": json.dumps({
            "id": unit_id,
            "flags": 128
        }),
        "sid": ssid
    }
    logger.debug(f'параметры запроса: {param}')
    response = requests.post(URL, data=param).json().get('item').get('aflds')
    logger.debug(f'результат id поля - {response}')
    return response


@fstart_stop
@logger.catch
def create_admin_field(ssid: str, unit_id: int, info_name: str) -> dict:
    """Create admin field.

    Args:
        ssid: string session id
        unit_id: integer unit/object id
        info_name: field name to create

    Returns:
        fields info: When creating or updating admin fields,
        response format will be ditionary
        {
            "id":<long>, admin field ID
            "n":<text>, name
            "v":<text>, value
        }
    """
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
    logger.debug('параметры на входе:')
    logger.debug(f'id сессии: {ssid}')
    logger.debug(f'id объекта: {unit_id}')
    logger.debug(f'имя поля: {info_name}')
    logger.debug(f'параметры запроса: {info}')
    logger.debug('поле создано')
    return response.json()


@fstart_stop
@logger.catch
def check_admin_fields(ssid: str, unit_id: int, info_name: str) -> tuple:
    """Check admin field.

        The function looks for the field id.
        If the field is not found, go to the function of creating
        the required field.
        If the field is found, the function returns a tuple
        in the form of the "field id", the "field value"

    Args:
        ssid: string session id
        unit_id: integer unit/object id
        info_name: field name to check id

    Returns:
        info data: tuple(field id(int), field value(str))
    """
    response = get_admin_fields(ssid, unit_id)

    logger.debug('параметры на входе:')
    logger.debug(f'id сессии: {ssid}')
    logger.debug(f'id объекта: {unit_id}')
    logger.debug(f'имя поля: {info_name}')

    for info in response.items():
        logger.debug(f'обход полей объекта в цикле: {info}')
        if info_name not in info[1].get('n'):
            continue
        else:
            logger.debug('поле найдено')
            logger.debug(f'результат id поля: {info[1].get("id")}')
            logger.debug(f'результат значение поля: {info[1].get("v")}')
            return info[1].get('id'), info[1].get('v')
    logger.debug('поле не найдено')
    response = create_admin_field(ssid, unit_id, info_name)
    logger.debug('поле создано')
    logger.debug(f'результат id поля: {response[1].get("id")}')
    logger.debug(f'результата значение поля: {response[1].get("v")}')
    return response[1].get('id'), response[1].get('v')


@fstart_stop
@logger.catch
def fill_info(
    ssid: str,
    unit_id: int,
    field_id_value: list[tuple],
    data: dict
) -> None:
    """Update the fields for Karkade.

        Finds an object by IMEI.
        Updates fields Info1, Info4, 5, Info6, info7.
        If fields not to be filled are not found, the script creates a field
        and fills it with data.

    Args:
        ssid: string session id
        unit_id: integer unit/object id
        field_id_value: list of tupels with integer id field, str value field
        data: data to fill
    """
    logger.debug('параметры на входе')
    logger.debug(f'id сессии: {ssid}')
    logger.debug(f'id объекта: {unit_id}')
    logger.debug(f'кортеж (id поля, значение поля к заполнению): {field_id_value}')
    logger.debug(f'json с текущими значениями полей объекта: {data}')
    info1 = {
        'svc': 'item/update_admin_field',
        'params': {
            "itemId": unit_id,
            "id": field_id_value[0][0],
            "callMode": 'update',
            "n": 'Инфо1',
            "v": data.get('РДДБ') if data.get(
                'РДДБ') is not None else field_id_value[0][1]
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
            "v": data.get('Специалист') if data.get(
                'Специалист') is not None else field_id_value[1][1]},
        'sid': ssid
    }

    info6 = {
        'svc': 'item/update_admin_field',
        'params': {
            "itemId": unit_id,
            "id": field_id_value[2][0],
            "callMode": 'update',
            "n": 'Инфо6',
            "v": data.get('ИНН') if data.get(
                'ИНН') is not None else field_id_value[2][1]},
        'sid': ssid
    }

    info7 = {
        'svc': 'item/update_admin_field',
        'params': {
            "itemId": unit_id,
            "id": field_id_value[3][0],
            "callMode": 'update',
            "n": 'Инфо7',
            "v": data.get('КПП') if data.get(
                'КПП') is not None else field_id_value[3][1]},
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
    logger.debug(f'параметры запроса: {param}')
    requests.post(URL, data=param)


@fstart_stop
@logger.catch
def upd_inn_field(
    ssid: str, unit_id: int, field_id: int, inn_value: str
) -> None:
    """Update the fields for GPBL.

    Finds an object by IMEI.
    Updates fields INN.
    If fields not to be filled are not found,
    the script creates a field and fills it with data.

    Args:
        ssid: string session id
        unit_id: integer unut/object id
        field_id: integer field id
        inn_value: data to fill
    """
    logger.debug('параметры на вход: ')
    logger.debug(f'id сессии: {ssid}')
    logger.debug(f'id объекта: {unit_id}')
    logger.debug(f'id поля ИНН: {field_id}')
    logger.debug(f'ИНН: {inn_value}')
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
    logger.debug(f'параметры запроса: {inn}')
    requests.post(URL, data=inn)


@fstart_stop
@logger.catch
def get_group_to_list(data: list[dict]) -> list:
    """Group items in a list.
    
    Collecting unique groups from the dictionary into a list

    Args:
        data (list): [{ID: 345646, 'Группы': 'group1, group2, group3'}]

    Returns:
        list: [group1, group2, group3]
    """
    logger.debug('параметры на вход: ')
    logger.debug(f'Список словарей: {data}')
    set_groups = set()
    logger.debug('старт цикла for')
    for i in data:
        tmp = i.get('Группы').split(',')
        for j in tmp:
            set_groups.add(j.strip())
    logger.debug(f'результат: {set_groups}')
    logger.debug('функция вернёт в формате списка list(set_groups)')
    return list(set_groups)


@fstart_stop
@logger.catch
def get_group_id(ssid: str, data: list) -> dict:
    """Search group id
    
    The function collects groups into a dictionary in the format
    {group: id_group, group2: id_group}

    Args:
        ssid (str): session id
        data (list): [group1, group2, group3]

    Returns:
        dict: {group1: id, group2: id, group3: id}
    """
    logger.debug('Параметры на входе:')
    logger.debug(f'id сессии: {ssid}')
    logger.debug(f'список групп: {data}')
    id_group = dict()
    for group in data:
        try:
            get_id_group = search_groups_by_name(ssid, group)
            id_group.update({group: get_id_group.get('items')[0].get('id')})
        except IndexError:
            logger.debug(f'группа {group} не найдена')
            id_group.update({group: -1})
            continue
    logger.debug(f'Результат: {id_group}')
    return id_group


@fstart_stop
@logger.catch
def add_obj_in_group_dict(
    ssid: str,
    group_list: list,
    input_file: list
    ) -> dict:
    """Distribution of objects by groups
    
    The script runs a loop in a loop, if there is a group in a row, we find
    the object ID of that row and add it to the list of the current group.

    Args:
        ssid (str): session id
        group_list (list): [group1, group2, group3]
        input_file (list): [{ID: 345646, 'Группы': 'group1, group2, group3'}]

    Returns:
        dict: {group1: [obj_id1, obj_id2, obj_id3 etc]}
    """
    logger.debug('Параметры на входе:')
    logger.debug(f'id сессии: {ssid}')
    logger.debug(f'Список из групп: {group_list}')
    logger.debug(f'Входящий файл: {input_file}')
    group_dict = defaultdict()
    for dictionary in input_file:
        for group in group_list:
            if group in dictionary.get('Группы'):
                obj_id = get_object_id(ssid, dictionary.get('ID'))
                group_dict.setdefault(group, []).append(obj_id)
    logger.debug(f'Результат: {group_dict}')
    return group_dict


@fstart_stop
@logger.catch
def get_user_id() -> int:
    """Get spb.csat id

    Returns:
        int: user wialon id for spb.csat 
    """
    param = {
        'svc': 'token/login',
        'params':json.dumps({"token":TOKEN})
        }
    response = requests.post(URL, data=param).json()
    cesar_id = response['user']['id']
    logger.debug(f'Результат: {cesar_id}')
    return cesar_id


@fstart_stop
@logger.catch
def get_new_token(app_name='export') -> str:
    """Token creation

    Args:
        app_name (str, optional): Defaults to 'export'.

    Returns:
        str: token name - 72 symbols
    """
    param = {
        'svc': 'token/update',
        'params': json.dumps({
            "callMode": "create",
			 "app": app_name,
			 "at": 0,
			 "dur": 300,
			 "fl": -1,
			 "p": '{}',
			 }),
        'sid': sid}
    new_token = requests.post(URL, data=param).json()
    logger.debug(f'Результат: {new_token.get("h")}')
    return new_token.get('h')
