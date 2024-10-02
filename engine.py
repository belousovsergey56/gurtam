"""Base func for work with Gurtam API."""

import json
import random

import requests

from config import fstart_stop, logger
from constant import CUSTOM_FIELDS, GROUPS
from hardware import create_object_with_all_params


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
        "Safari/537.36 OPR/26.0.1656.60",
        "(maverick) Firefox/3.6.10",
        "Chrome/39.0.2171.71 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 "
        "(KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    ]
    user_agent = random.choice(user_agent_list)
    header = {"User-Agent": user_agent}
    return header


@fstart_stop
def check_server_access(URL: str, TOKEN: str):
    """Check server accessibility

    Args:
        URL (str): server address
        TOKEN (str): server token

    Returns:
        int: status code
    """
    param = {"svc": "token/login", "params": json.dumps({"token": TOKEN})}
    response = requests.post(URL, data=param)
    return response


@fstart_stop
@logger.catch
def get_ssid(URL: str, TOKEN: str) -> str:
    """Authorize by token and getting the session number.

    The function authorizes with a token on fms4,
    receives a json file in response,
    from where it takes eid and returns it as a string,

    Args:
        URL (str): server address
        TOKEN (str): secret key

    Returns:
        str: eid - session id on vialon
    """
    param = {"svc": "token/login", "params": json.dumps({"token": TOKEN})}
    response = requests.post(URL, data=param, headers=get_header())
    logger.debug("получение id сессии")
    logger.debug(f"URL: {response.url}")
    logger.debug(f'результат id сессии: {response.json().get("eid")}')
    return response.json().get("eid")


@fstart_stop
@logger.catch
def get_object_info_by_imei(ssid: str, imei: str, URL: str) -> dict:
    """Search object by imei.

    Args:
        ssid (str): session id
        imei (str): unique id object
        URL (str): server address

    Returns:
        dict: meta data about object
    """
    param = {
        "svc": "core/search_items",
        "params": json.dumps(
            {
                "spec": {
                    "itemsType": "avl_unit",
                    "propName": "sys_unique_id",
                    "propValueMask": "*{0}*".format(imei),
                    "sortType": "sys_name",
                },
                "force": 1,
                "flags": 4611686018427387903,
                "from": 0,
                "to": 0,
            }
        ),
        "sid": ssid,
    }
    response = requests.post(URL, data=param)
    logger.debug(f'получение данных об объекте по имей: "{imei}"')
    logger.debug(f"URL: {response.url}")
    logger.debug(f"параметры URL: {param}")
    logger.debug(f"результат: {response.json()}")
    return response.json()


@fstart_stop
@logger.catch
def get_object_info_by_name(ssid: str, object_name: str, URL: str) -> dict:
    """Search object by imei.

    Args:
        ssid (str): session id
        object_name (str): partial or full object name.
        URL (str): server address

    Returns:
        dict: meta data about object
    """
    param = {
        "svc": "core/search_items",
        "params": json.dumps(
            {
                "spec": {
                    "itemsType": "avl_unit",
                    "propName": "sys_name",
                    "propValueMask": "*{0}*".format(object_name),
                    "sortType": "sys_name",
                },
                "force": 1,
                "flags": 4611686018427387903,
                "from": 0,
                "to": 0,
            }
        ),
        "sid": ssid,
    }

    response = requests.post(URL, data=param)
    logger.debug(f'получение данных об объекте по его имени: "{object_name}"')
    logger.debug(f"URL: {response.url}")
    logger.debug(f"параметры URL: {param}")
    logger.debug(f"результат: {response.json()}")
    return response.json()


@fstart_stop
@logger.catch
def get_object_id(ssid: str, imei: str, URL: str) -> int:
    """Find object by imei and returns object id.

    The function finds an object in the database by imei and returns id.
    If the object is not found, the function returns -1

    Args:
        ssid (str): current connection id, session number
        imei (str): unique id your equipment
        URL: (str): server adderss

    Returns:
        int: unique id avl_unit or -1
    """
    response = get_object_info_by_imei(ssid, imei, URL)
    logger.debug(f'получение id объекта: "{imei}"')
    logger.debug('imei отдаётся в обработку функции "get_object_info_by_imei"')
    if response.get("items"):
        logger.debug(
            f'результат id обекта: {response.get("items")[0].get("id")}')
        return response.get("items")[0].get("id")
    logger.debug('объект не существует, результат: "-1"')
    return -1


@fstart_stop
@logger.catch
def create_custom_fields(ssid: str, unit_id: int, URL: str) -> None:
    """Create of arbitrary fields in the object card on the vialon.

    The function finds the object by IMEI,
    checks the presence of the necessary fields in the "Custom fields" tab
    if the field is missing, the function creates it.

    Args:
        ssid (str): session id
        unit_id (int): object id on vialon
        URL (str): server address
    """
    logger.debug(f'параметры на входе - ssid: "{ssid}, unit_id: "{unit_id}"')
    admin_fields = (
        "geozone_imei",
        "geozone_sim",
        "Инфо1",
        "Инфо2",
        "Инфо3",
        "Инфо4",
        "Пин",
    )
    item_fields = CUSTOM_FIELDS
    id_field = {
        "geozone_imei": 1,
        "geozone_sim": 2,
        "Инфо1": 3,
        "Инфо2": 4,
        "Инфо3": 5,
        "Инфо4": 6,
        "Пин": 7,
        "Vin": 1,
        "Марка": 2,
        "Модель": 3,
    }
    logger.debug(f"шаблон админ поля: {admin_fields}")
    logger.debug(f"шаблон произвольне поля: {item_fields}")
    logger.debug(f"присвоенные id полям: {id_field}")
    for field in admin_fields:
        param = {
            "svc": "core/search_item",
            "params": json.dumps({"id": unit_id, "flags": 128}),
            "sid": ssid,
        }
        response = requests.post(URL, data=param)
        logger.debug(
            f"получение админ полей: {response.url}, параметры: {param}"
        )
        logger.debug(f"результат: {response.json()}")
        if field not in response.text:
            create_field = {
                "svc": "item/update_admin_field",
                "params": json.dumps(
                    {
                        "itemId": unit_id,
                        "id": id_field.get(field),
                        "callMode": "create",
                        "n": "{0}".format(field),
                        "v": "",
                    }
                ),
                "sid": ssid,
            }
            requests.post(URL, data=create_field)
            logger.debug(
                f'поле {field} не существует у объкта c id {unit_id}, создать поле, запрос: "requests.post(URL, data=create_field)", параметры: {create_field}'
            )
        else:
            logger.debug(f"поле {field} существует")
            continue

    for field in item_fields:
        param = {
            "svc": "core/search_item",
            "params": json.dumps({"id": unit_id, "flags": 8}),
            "sid": ssid,
        }
        response = requests.post(URL, data=param)
        logger.debug(
            f"получение произвольных полей: {response.url}, параметры: {param}"
        )
        logger.debug(f"результат: {response.json()}")
        if field not in response.text:
            create_field = {
                "svc": "item/update_custom_field",
                "params": json.dumps(
                    {
                        "itemId": unit_id,
                        "id": id_field.get(field),
                        "callMode": "create",
                        "n": "{0}".format(field),
                        "v": "",
                    }
                ),
                "sid": ssid,
            }
            requests.post(URL, data=create_field)
            logger.debug(
                f'поле {field} не существует у объкта c id {unit_id}, создать поле, запрос: "requests.post(URL, data=create_field)", параметры: {create_field}'
            )
        else:
            logger.debug(f"поле {field} существует")
            continue


@fstart_stop
@logger.catch
def update_param(
    session_id: str, unit_id: int, new_value: dict, id_field: dict, URL: str
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
        URL (str): server adderss
    """
    logger.debug("входящие параметры:")
    logger.debug(f'id сессии: "{session_id}"')
    logger.debug(f'id объекта: "{unit_id}"')
    logger.debug(f'json с данными для заполнения: "{new_value}"')
    logger.debug(f'id поля Инфо4: "{id_field}"')
    logger.debug(f'адрес сервера: "{URL}"')
    contract_name = {
        "svc": "item/update_name",
        "params": {"itemId": unit_id, "name": new_value.get("ДЛ").strip()},
        "sid": session_id,
    }

    imei = {
        "svc": "item/update_admin_field",
        "params": {
            "itemId": unit_id,
            "id": id_field.get("geozone_imei"),
            "callMode": "update",
            "n": "geozone_imei",
            "v": new_value.get("geozone_imei"),
        },
        "sid": session_id,
    }

    sim = {
        "svc": "item/update_admin_field",
        "params": {
            "itemId": unit_id,
            "id": id_field.get("geozone_sim"),
            "callMode": "update",
            "n": "geozone_sim",
            "v": new_value.get("geozone_sim"),
        },
        "sid": session_id,
    }

    vin = {
        "svc": "item/update_custom_field",
        "params": {
            "itemId": unit_id,
            "id": id_field.get("Vin"),
            "callMode": "update",
            "n": "Vin",
            "v": new_value.get("Vin"),
        },
        "sid": session_id,
    }

    info4 = {
        "svc": "item/update_admin_field",
        "params": {
            "itemId": unit_id,
            "id": id_field.get("Инфо4"),
            "callMode": "update",
            "n": "Инфо4",
            "v": new_value.get(
                "Инфо4") if new_value.get("Инфо4") is not None else "",
        },
        "sid": session_id,
    }

    brand = {
        "svc": "item/update_custom_field",
        "params": {
            "itemId": unit_id,
            "id": id_field.get("Марка"),
            "callMode": "update",
            "n": "Марка",
            "v": new_value.get("Марка"),
        },
        "sid": session_id,
    }

    model = {
        "svc": "item/update_custom_field",
        "params": {
            "itemId": unit_id,
            "id": id_field.get("Модель"),
            "callMode": "update",
            "n": "Модель",
            "v": new_value.get("Модель"),
        },
        "sid": session_id,
    }

    pin = {
        "svc": "item/update_admin_field",
        "params": {
            "itemId": unit_id,
            "id": id_field.get("Пин"),
            "callMode": "update",
            "n": "Пин",
            "v": new_value.get("Пин"),
        },
        "sid": session_id,
    }

    distance = {
        "svc": "unit/update_mileage_counter",
        "params": {"itemId": unit_id, "newValue": 0},
        "sid": session_id,
    }

    engin_hours = {
        "svc": "unit/update_eh_counter",
        "params": {"itemId": unit_id, "newValue": 0},
        "sid": session_id,
    }

    param = {
        "svc": "core/batch",
        "params": json.dumps(
            {
                "params": [
                    contract_name,
                    imei,
                    sim,
                    vin,
                    info4,
                    brand,
                    model,
                    pin,
                    distance,
                    engin_hours,
                ],
                "flags": 0,
            }
        ),
        "sid": session_id,
    }
    logger.debug(
        f"передача параметров для обновления полей карточки объект в одном запросе: {param}"
    )
    requests.post(URL, data=param)


@fstart_stop
@logger.catch
def search_groups_by_name(ssid: str, group_name: str, URL: str) -> dict:
    """Find groups by name.

    Args:
        ssid (str): session id
        group_name (str): the name or part of the name of the group
        we want to find
        URL (str): adderss server

    Returns:
        dict: dictionari with group names
        and id's that matched by name
    """
    logger.debug("вхводящие параметры: ")
    logger.debug(f'id сессии: "{ssid}"')
    logger.debug(f'маска искомой группы: "{group_name}"')
    logger.debug(f'адрес сервера: "{URL}"')
    param = {
        "svc": "core/search_items",
        "params": json.dumps(
            {
                "spec": {
                    "itemsType": "avl_unit_group",
                    "propName": "sys_name",
                    "propValueMask": "*{0}*".format(group_name),
                    "sortType": "sys_name",
                },
                "force": 1,
                "flags": 1,
                "from": 0,
                "to": 0,
            }
        ),
        "sid": ssid,
    }
    response = requests.post(URL, data=param)
    logger.debug(f"URL: {response.url}")
    logger.debug(f"параметры запроса: {param}")
    logger.debug(f"результат выполнения запроса: {response.json()}")
    return response.json()


@fstart_stop
@logger.catch
def search_group_by_id(ssid: str, group_id: int, URL: str) -> dict:
    """Find group by id.

    Args:
        ssid (str): session id
        group_id (int): group id
        URL (str): server address

    Returns:
        dict: a dictionary with the name of the group,
        the id of the group,
        the list of id objects that belong to this group, etc.
    """
    logger.debug("параметры на входе:")
    logger.debug(f"id сессии: {ssid}")
    logger.debug(f"id искомой группы: {group_id}")
    logger.debug(f"адрес сервера: {URL}")
    param = {
        "svc": "core/search_item",
        "params": json.dumps({"id": group_id, "flags": 1}),
        "sid": ssid,
    }

    response = requests.post(URL, data=param)
    logger.debug(f"URL: {response.url}")
    logger.debug(f"параметры запроса: {param}")
    logger.debug(f"результат выполнения запроса: {response.json()}")
    return response.json()


@fstart_stop
@logger.catch
def add_groups(
    ssid: str,
    leasing_id: int | str,
    leasing_unit_list: list[int],
    added_unit: list[int],
    URL: str,
) -> dict:
    """Add objects to a group.

    Args:
        ssid (str): session id
        leasing_id (int | str): id group
        leasing_unit_list (list[int]): list of current id group objects
        added_unit (int): list of id objects to add
        URL (str): server address
    Returns:
        { "u":[<long>]	/* массив ID объектов */}
    """
    logger.debug("параметры на входе:")
    logger.debug(f"id сессии: {ssid}")
    logger.debug(f"id группы: {leasing_id}")
    logger.debug(f"список текущих id объектов в группе: {leasing_unit_list}")
    logger.debug(f"список добавляемых id объектов в группу: {added_unit}")
    logger.debug(f"адрес сервера: {URL}")
    param = {
        "svc": "unit_group/update_units",
        "params": json.dumps(
            {"itemId": leasing_id, "units": leasing_unit_list + added_unit}
        ),
        "sid": ssid,
    }
    logger.debug(f"параметры запроса: {param}")
    result = requests.post(URL, data=param)
    return result.json()


@fstart_stop
@logger.catch
def create_object(sid: str, unit: dict, URL: str, fms: int) -> int:
    """Check the presence of an object on the vialon.

    Checking dictionary objects by IMEI for presence on the Vialon portal
    If the object is missing, the object is written to the log file and the
    object is created on the portal.
    An object is created based on the type of its equipment.
    To create a separate function is used.

    Args:
        unit (dict): dictionary of objects
        sid (str): session id
        URL (str): server address
        fms (int): server number

    Returns:
        obj_id: integer object id
    """
    logger.debug(f"id сесиии: {sid}")
    logger.debug(f"json с данными создаваемого объекта: {unit}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"номер сервера: {fms}")
    obj_id = create_object_with_all_params(sid, URL, unit, fms)
    create_custom_fields(sid, obj_id, URL)
    with open(f'logging/{unit.get("ЛИЗИНГ")}', "a") as log:
        data_log = """Пин {0} - Имей {1}\n"""
        logger.debug(f"объект создан: {data_log}")
        log.write(data_log.format(unit.get("Пин"), unit.get("geozone_imei")))
    logger.debug(f"результат id созданного объекта: {obj_id}")
    return obj_id


@fstart_stop
@logger.catch
def group_update(sid: str, data: dict, URL: str, fms: int) -> None:
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
        URL (str): server address
        sid (str): session id
        fms (int): server number
    """
    logger.debug(f"аргумент на входе json: {data}")
    logger.debug(f"id сессии: {sid}")
    logger.debug(f"адрес сервера: {URL}")
    truck = []
    auto = []
    special = []
    all_unit = []
    risk_auto = []

    logger.debug("распределение объектов в списки по группам")
    for unit in data:
        all_unit.append(unit.get("uid"))
        if unit.get("ТИП") == str(0):
            auto.append(unit.get("uid"))
        elif unit.get("ТИП") == str(1):
            truck.append(unit.get("uid"))
        elif unit.get("ТИП") == str(2):
            special.append(unit.get("uid"))
        if unit.get("РИСК") == str(9):
            risk_auto.append(unit.get("uid"))

    logger.debug(f"колличество грузовых: {len(truck)}")
    logger.debug(f"колличество легковых: {len(auto)}")
    logger.debug(f"колличество спецтехники: {len(special)}")
    logger.debug(f"колличество рисковых: {len(risk_auto)}")

    finded_group = search_groups_by_name(
        sid, data[0].get("ЛИЗИНГ"), URL).get("items")

    logger.debug(f'Ищем группы по маске: {data[0].get("ЛИЗИНГ")}')

    for group in finded_group:
        id_group = group.get("id")
        leasing_unit_list = group.get("u")
        if id_group in GROUPS.get(fms).get("AUTO"):
            add_groups(sid, id_group, leasing_unit_list, auto, URL)
        elif group.get("id") in GROUPS.get(fms).get("TRUCK"):
            add_groups(sid, id_group, leasing_unit_list, truck, URL)
        elif group.get("id") in GROUPS.get(fms).get("SPEC"):
            add_groups(sid, id_group, leasing_unit_list, special, URL)
        elif group.get("id") in GROUPS.get(fms).get("RISK"):
            add_groups(sid, id_group, leasing_unit_list, risk_auto, URL)
        else:
            add_groups(sid, id_group, leasing_unit_list, all_unit, URL)
    for id_group in GROUPS.get(fms).get("REQUIRED_GROUPS"):
        leasing_unit_list = search_group_by_id(
            sid, id_group, URL).get("item")["u"]
        add_groups(sid, id_group, leasing_unit_list, all_unit, URL)
    logger.debug("Объекты добавлены")


@fstart_stop
@logger.catch
def get_custom_fields(ssid: str, unit_id: int, URL: str) -> dict:
    """Get custom fields data.

    Args:
        ssid (str): sesion id
        unit_id (int): unit/object id
        URL (str): server address

    Returns:
        custom fields: custom fields data in dictionary
    """
    param = {
        "svc": "core/search_item",
        "params": json.dumps({"id": unit_id, "flags": 8}),
        "sid": ssid,
    }
    logger.debug("параметры на входе:")
    logger.debug(f"id сессии: {ssid}")
    logger.debug(f"id объекта: {unit_id}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"параметры запроса: {param}")
    response = requests.post(URL, data=param).json().get("item").get("flds")
    logger.debug(f"результат выполнения запроса: {response}")
    return response


@fstart_stop
@logger.catch
def create_custom_field(
    ssid: str, unit_id: int, info_name: str, URL: str
) -> list:
    """Create custom field.

    Args:
        ssid (str): session id
        unit_id (int): integer unit/object id
        info_name (str): field name to create
        URL (str): server address

    Returns:
        fields info: When creating or updating custom fields,
        response format will be
        [1,
        {
            "id":<long>, custom field ID
            "n":<text>, name
            "v":<text> value
        }
        ]
        where 1 it is number field
    """
    info = {
        "svc": "item/update_custom_field",
        "params": json.dumps(
            {
                "itemId": unit_id,
                "id": 0,
                "callMode": "create",
                "n": info_name,
                "v": ""
                }
        ),
        "sid": ssid,
    }
    response = requests.post(URL, data=info)
    logger.debug("параметры на входе:")
    logger.debug(f"id сессии: {ssid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"id объекта: {unit_id}")
    logger.debug(f"имя поля: {info_name}")
    logger.debug(f"параметры запроса: {info}")
    logger.debug("поле создано")
    return response.json()


@fstart_stop
@logger.catch
def get_admin_fields(ssid: str, unit_id: int, URL: str) -> dict:
    """Get admin fields data.

    Args:
        ssid: string sesion id
        URL (str): server address
        unit_id: integer unit/object id

    Returns:
        admin fields: admin fields data in dictionary
    """
    logger.debug("параметры на входе:")
    logger.debug(f"id сессии: {ssid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"id объекта: {unit_id}")
    param = {
        "svc": "core/search_item",
        "params": json.dumps({"id": unit_id, "flags": 128}),
        "sid": ssid,
    }
    logger.debug(f"параметры запроса: {param}")
    response = requests.post(URL, data=param).json().get("item").get("aflds")
    logger.debug(f"результат id поля - {response}")
    return response


@fstart_stop
@logger.catch
def create_admin_field(
    ssid: str, unit_id: int, info_name: str, URL: str
) -> list:
    """Create admin field.

    Args:
        ssid (str): session id
        unit_id (int): unit/object id
        info_name (str): field name to create
        URL (str): server address

    Returns:
        fields info: When creating or updating admin fields,
        response format will be
        [1,
        {
            "id":<long>, admin field ID
            "n":<text>, name
            "v":<text>, value
        }
        ]
        where 1 it is number field
    """
    info = {
        "svc": "item/update_admin_field",
        "params": json.dumps(
            {
                "itemId": unit_id,
                "id": 0,
                "callMode": "create",
                "n": info_name,
                "v": ""
                }
        ),
        "sid": ssid,
    }
    response = requests.post(URL, data=info)
    logger.debug("параметры на входе:")
    logger.debug(f"id сессии: {ssid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"id объекта: {unit_id}")
    logger.debug(f"имя поля: {info_name}")
    logger.debug(f"параметры запроса: {info}")
    logger.debug("поле создано")
    return response.json()


@fstart_stop
@logger.catch
def check_admin_fields(
    ssid: str, unit_id: int, info_name: str, URL: str
) -> tuple:
    """Check admin field.

        The function looks for the field id.
        If the field is not found, go to the function of creating
        the required field.
        If the field is found, the function returns a tuple
        in the form of the "field id", the "field value"

    Args:
        ssid (str): session id
        unit_id (int): unit/object id
        info_name (str): field name to check id
        URL (str): server address

    Returns:
        info data: tuple(field id(int), field value(str))
    """
    response = get_admin_fields(ssid, unit_id, URL)

    logger.debug("параметры на входе:")
    logger.debug(f"id сессии: {ssid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"id объекта: {unit_id}")
    logger.debug(f"имя поля: {info_name}")

    for info in response.items():
        logger.debug(f"обход полей объекта в цикле: {info}")
        if info_name not in info[1].get("n"):
            continue
        else:
            logger.debug("поле найдено")
            logger.debug(f'результат id поля: {info[1].get("id")}')
            logger.debug(f'результат значение поля: {info[1].get("v")}')
            return info[1].get("id"), info[1].get("v")
    logger.debug("поле не найдено")
    response = create_admin_field(ssid, unit_id, info_name, URL)
    logger.debug("поле создано")
    logger.debug(f'результат id поля: {response[1].get("id")}')
    logger.debug(f'результата значение поля: {response[1].get("v")}')
    return response[1].get("id"), response[1].get("v")


@fstart_stop
@logger.catch
def fill_info(
    ssid: str, unit_id: int, field_id_value: list[tuple], data: dict, URL: str
) -> None:
    """Update the fields for Karkade.

        Finds an object by IMEI.
        Updates fields Info1, Info4, 5, Info6, info7.
        If fields not to be filled are not found, the script creates a field
        and fills it with data.

    Args:
        ssid (str): session id
        unit_id (int): unit/object id
        field_id_value (list[tuple]): list of tupels with integer id field, str value field
        data (dict): data to fill
        URL (str): server address
    """
    logger.debug("параметры на входе")
    logger.debug(f"id сессии: {ssid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"id объекта: {unit_id}")
    logger.debug(
        f"кортеж (id поля, значение поля к заполнению): {field_id_value}")
    logger.debug(f"json с текущими значениями полей объекта: {data}")
    info1 = {
        "svc": "item/update_admin_field",
        "params": {
            "itemId": unit_id,
            "id": field_id_value[0][0],
            "callMode": "update",
            "n": "Инфо1",
            "v": data.get("РДДБ")
            if data.get("РДДБ") is not None
            else field_id_value[0][1],
        },
        "sid": ssid,
    }

    info5 = {
        "svc": "item/update_admin_field",
        "params": {
            "itemId": unit_id,
            "id": field_id_value[1][0],
            "callMode": "update",
            "n": "Инфо5",
            "v": data.get("Специалист")
            if data.get("Специалист") is not None
            else field_id_value[1][1],
        },
        "sid": ssid,
    }

    info6 = {
        "svc": "item/update_admin_field",
        "params": {
            "itemId": unit_id,
            "id": field_id_value[2][0],
            "callMode": "update",
            "n": "Инфо6",
            "v": data.get("ИНН")
            if data.get("ИНН") is not None
            else field_id_value[2][1],
        },
        "sid": ssid,
    }

    info7 = {
        "svc": "item/update_admin_field",
        "params": {
            "itemId": unit_id,
            "id": field_id_value[3][0],
            "callMode": "update",
            "n": "Инфо7",
            "v": data.get("КПП")
            if data.get("КПП") is not None
            else field_id_value[3][1],
        },
        "sid": ssid,
    }

    param = {
        "svc": "core/batch",
        "params": json.dumps(
            {"params": [info1, info5, info6, info7], "flags": 0}),
        "sid": ssid,
    }
    logger.debug(f"параметры запроса: {param}")
    requests.post(URL, data=param)


@fstart_stop
@logger.catch
def upd_inn_field(
    ssid: str, unit_id: int, field_id: int, inn_value: str, URL: str
) -> None:
    """Update the fields for GPBL.

    Finds an object by IMEI.
    Updates fields INN.
    If fields not to be filled are not found,
    the script creates a field and fills it with data.

    Args:
        ssid (str): session id
        unit_id (int): unut/object id
        field_id (int): field id
        inn_value (str): data to fill
        URL (str): server address
    """
    logger.debug("параметры на вход: ")
    logger.debug(f"id сессии: {ssid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"id объекта: {unit_id}")
    logger.debug(f"id поля ИНН: {field_id}")
    logger.debug(f"ИНН: {inn_value}")
    inn = {
        "svc": "item/update_admin_field",
        "params": json.dumps(
            {
                "itemId": unit_id,
                "id": field_id,
                "callMode": "update",
                "n": "ИНН",
                "v": inn_value,
            }
        ),
        "sid": ssid,
    }
    logger.debug(f"параметры запроса: {inn}")
    requests.post(URL, data=inn)


@fstart_stop
@logger.catch
def get_user_id(URL: str, TOKEN: str) -> int:
    """Get this user id

    Args:
        URL (str): server address
        TOKEN (str): secret key

    Returns:
        int: user wialon id for spb.csat
    """
    param = {"svc": "token/login", "params": json.dumps({"token": TOKEN})}
    response = requests.post(URL, data=param).json()
    cesar_id = response["user"]["id"]
    logger.debug(f"Результат: {cesar_id}")
    return cesar_id


@fstart_stop
@logger.catch
def __get_new_token(sid: str, URL: str, app_name="export") -> str:
    """Token creation

    Args:
        sid (str): session id
        URL (str): server address
        app_name (str, optional): Defaults to 'export'.

    Returns:
        str: token name - 72 symbols
    """
    param = {
        "svc": "token/update",
        "params": json.dumps(
            {
                "callMode": "create",
                "app": app_name,
                "at": 0,
                "dur": 300,
                "fl": -1,
                "p": "{}",
            }
        ),
        "sid": sid,
    }
    new_token = requests.post(URL, data=param).json()
    logger.debug(f'Результат: {new_token.get("h")}')
    return new_token.get("h")


@fstart_stop
@logger.catch
def update_object_name(sid: str, URL: str, unit_id: int, name: str) -> json:
    """Update contract name

    The function updates the name of the object.

    Args:
        sid (str): session id
        URL (str): server address
        unit_id (int): object id on wialon
        name (str): new name

    Returns:
        json: {"nm": new_name}
    """
    logger.debug("Параметры на входе:")
    logger.debug(f"id сессии: {sid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"id объекта: {unit_id}")
    logger.debug(f"новое имя объекта: {name}")
    param = {
        "svc": "item/update_name",
        "params": json.dumps({"itemId": unit_id, "name": name.strip()}),
        "sid": sid,
    }

    result = requests.post(URL, data=param)
    logger.debug(f"Результат {result.json()}")
    return result.json()


@fstart_stop
@logger.catch
def id_fields(sid: str, uid: int, url: str) -> dict:
    """Get id fields.

    Helper function.
    Create map id fields.
    Search field id and add to dict.
    Search custom and admin fields.
    If id field not found, go to create field and add new id to dict.
    Them return dict with field name and current id.
    Current name and id:
    geozone_sim, geozone_imei, Vin, Марка, Модель, Пин, Инфо4

    Args:
        sid (str): current session id
        uid (int): unit/object id
        url (str): server address

    Returns:
        map_id (dict): dict with current field name and field id
    """
    admin_fields = get_admin_fields(sid, uid, url)
    custom_fields = get_custom_fields(sid, uid, url)
    map_id = {
        "geozone_imei": None,
        "geozone_sim": None,
        "Vin": None,
        "Марка": None,
        "Модель": None,
        "Пин": None,
        "Инфо4": None,
    }
    logger.debug(f"получен список админ полей: {admin_fields}")
    logger.debug(f"получен список произвольных полей: {custom_fields}")
    logger.debug("старт цикла for для поиска айди админ полей")
    for field in admin_fields.items():
        name_field = field[1].get("n")
        id_field = field[1].get("id")
        logger.debug(f"имя поля: {name_field}")
        logger.debug(f"айди поля: {id_field}")
        if name_field in map_id.keys():
            map_id.update({name_field: id_field})
    logger.debug("конец цикла for для поиска айди админ полей")
    logger.debug("старт цикла for для поиска айди произвольных полей")
    for field in custom_fields.items():
        name_field = field[1].get("n")
        id_field = field[1].get("id")
        logger.debug(f"имя поля: {name_field}")
        logger.debug(f"айди поля: {id_field}")
        if name_field in map_id.keys():
            map_id.update({name_field: id_field})
    logger.debug("конец цикла for для поиска айди админ полей")
    logger.debug(
        "старт цикла for, проверка что все нужные айди собраны. Если значение поля None, тода поле создаётся и присваивается id"
    )
    for names, values in map_id.items():
        if values is None:
            if names == "Vin" or names == "Марка" or names == "Модель":
                field = create_custom_field(sid, uid, names, url)
                map_id.update({names: field[1].get("id")})
            else:
                field = create_admin_field(sid, uid, names, url)
                map_id.update({names: field[1].get("id")})
    logger.debug("конец цикла for для проверки id")
    logger.debug(f"Получен результат: {map_id}")
    return map_id


@fstart_stop
@logger.catch
def delete_object(sid: str, URL: str, obj_id: int) -> dict:
    """Delete one object.

    The function takes the id of an object, finds it and deletes it.

    Args:
        sid (str): current session id
        URL (str): server address
        obj_id (int): unit/object id

    Returns:
        dict: if object is deleted func returnet empty dict
    """
    logger.debug("Параметры на входе:")
    logger.debug(f"id сессии: {sid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"id объекта: {obj_id}")
    param = {
        "svc": "item/delete_item",
        "params": json.dumps({"itemId": obj_id}),
        "sid": sid,
    }
    result = requests.post(URL, data=param)
    logger.debug(f"результат работы функции: {result}")
    return result.json()


@fstart_stop
@logger.catch
def __change_calc_flag(sid: str, url: str, obj_id: int, flag: int) -> dict:
    """Change counter calculation parameters

     See https://sdk.wialon-online.ru/wiki/en/pro/remoteapi/apiref/unit/update_calc_flags for flag parameters

    Args:
        sid (str): current session id
        url (str): server address
        obj_id (int): object id on wialon
        flag (int): cfl: 784 - gps, cfl: 785 - одометр

    Returns:
        dict: {"cfl": flag}	/* flags applied */
    """
    logger.debug("Параметры на входе:")
    logger.debug(f"id сессии: {sid}")
    logger.debug(f"адрес сервера: {url}")
    logger.debug(f"id объекта: {obj_id}")
    logger.debug(f"Новый параметр: {flag}")
    param = {
        "svc": "unit/update_calc_flags",
        "params": json.dumps({"itemId": obj_id, "newValue": flag}),
        "sid": sid
    }
    result = requests.post(url, data=param)
    logger.debug(f"Результат: {result.json()}")
    return result.json()
