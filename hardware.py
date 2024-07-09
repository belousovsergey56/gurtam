"""This module, create object and fill sensors."""

import json

import requests

from config import fstart_stop, logger
from constant import HW_ID, HW_TMP, USER_ID


@fstart_stop
@logger.catch
def create_object(
    sid: str, URL: str, hardware_id: int, object_name: str, fms: int
) -> dict:
    """Create new object.

    Args:
        sid (str): Session id
        URL (str): server address
        hardware (str): hardware id
        object_name (str): this is contract name
        fms (int): server number
    Returns:
        dict: {'item': {'nm': 'object name', 'cls': 2, 'id': 26370, 'mu': 0, 'uacl': 880333094911}, 'flags': 1}
    """
    logger.debug("Параметры на входе:")
    logger.debug(f"id сессии: {sid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"id оборудования: {hardware_id}")
    logger.debug(f"имя ДЛ: {object_name}")
    logger.debug(f"номер сервера: {fms}")
    uid = USER_ID[fms]
    params = {
        "svc": "core/create_unit",
        "params": json.dumps(
            {
                "creatorId": uid,
                "name": object_name,
                "hwTypeId": hardware_id,
                "dataFlags": 1,
            }
        ),
        "sid": sid,
    }
    logger.debug(f"параметры запроса: {params}")
    response = requests.post(URL, data=params)
    logger.info(f"Объект создан, результат запроса: {response.json()}")
    return response.json()


@fstart_stop
@logger.catch
def create_sensors(
    sid: str, URL: str, hardware_id: int, object_id: int, fms: int
) -> int:
    """Creation of sensors.

    The function reads the equipment field from the input,
    reads the template with sensors and fills in the required fields
    to send a request to create sensors to a specific object.

    Args:
        sid (str): session id
        URL (str): server address
        hardware_id (int): hardware id
        object_id (int): unit/object id
        fms (int): server number

    Returns:
        data: integer 0
    """
    logger.debug("параметры на входе")
    logger.debug(f"id сессии: {sid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"id оборуддования: {hardware_id}")
    logger.debug(f"id объекта: {object_id}")
    logger.debug(f"номер сервера: {fms}")
    sensor_template = HW_TMP[fms].get(hardware_id)
    with open(f"data_tmp/{sensor_template}.json", "r") as f:
        tmp = json.loads(f.read())
        for sensor in tmp.get("sensors"):
            param = {
                "svc": "unit/update_sensor",
                "params": json.dumps(
                    {
                        "itemId": object_id,
                        "id": sensor.get("id"),
                        "callMode": "create",
                        "unlink": 0,
                        "n": sensor.get("n"),
                        "t": sensor.get("t"),
                        "d": sensor.get("d"),
                        "m": sensor.get("m"),
                        "p": sensor.get("p"),
                        "f": sensor.get("f"),
                        "c": sensor.get("c"),
                        "vt": sensor.get("vt"),
                        "vs": sensor.get("vs"),
                        "tbl": sensor.get("tbl"),
                    }
                ),
                "sid": sid,
            }
            requests.post(URL, data=param)
            logger.debug(f"параметры запроса: {param}")
        logger.info("датчики созданы")
    return 0


@fstart_stop
@logger.catch
def add_phone(sid: str, URL: str, obj_id: int, phone: str) -> str:
    """Add phone.

    The function updates the phone field in the Main tab
    to the wialon in the object card.

    Args:
        sid (str): session id
        URL (str): server address
        obj_id (int): unit/object id
        phone (str): new phone number

    Returns:
        phone: string new phone number
    """
    logger.debug("параметры на входе:")
    logger.debug(f"id сессии: {sid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"id объекта: {obj_id}")
    logger.debug(f"телефон: {phone}")
    param = {
        "svc": "unit/update_phone",
        "params": json.dumps({"itemId": obj_id, "phoneNumber": phone}),
        "sid": sid,
    }
    logger.debug(f"параметры запроса: {param}")
    response = requests.post(URL, data=param)
    logger.info(f"телефон внесён, результат запроса: {response.text}")
    return response.text


@fstart_stop
@logger.catch
def add_obj_uid(sid: str, URL: str, obj_id: int, hardware_id: int, uid: str):
    """Update geozone imei.

    The function updates the geozone imei field in the Main tab
    to the wialon in the object card.

    Args:
        sid (str): session id
        URL (str): server address
        obj_id (int): unit/object id
        hardware_id (int): harware id
        uid (int): new unit/object id
    Returns:
        dict: {
        "uid":<text>, /* уникальный ID */
        "hw":<long>	/* тип оборудования */
                }
    """
    logger.debug("параметры на входе:")
    logger.debug(f"id сессии: {sid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"id объекта: {obj_id}")
    logger.debug(f"id оборудования: {hardware_id}")
    logger.debug(f"новый id: {uid}")
    param = {
        "svc": "unit/update_device_type",
        "params": json.dumps(
            {"itemId": obj_id, "deviceTypeId": hardware_id, "uniqueId": uid}
        ),
        "sid": sid,
    }
    a = requests.post(URL, data=param)
    logger.debug(f"параметры запроса: {param}")
    logger.info(f"имей добавлен, результат запроса: {a.text}")
    return a.json()


@fstart_stop
@logger.catch
def add_param_engin_axel(sid: str, URL: str, obj_id: int) -> int:
    """Update counter settings.

    Resets the odometer and engine hours counter to zero.

    Args:
        sid (str): session id
        URL (str): server address
        obj_id (int): unit/object id

    Returns:
        data (int): 0
    """
    logger.debug("Параметры на входе:")
    logger.debug(f"id сессии: {sid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"id объекта: {obj_id}")
    param = {
        "svc": "unit/update_calc_flags",
        "params": json.dumps({"itemId": obj_id, "newValue": "0x310"}),
        "sid": sid,
    }
    requests.post(URL, data=param)
    logger.debug(f"параметры запроса: {param}")
    logger.info("Одометр и моточасы сброшены до нуля")
    return 0


@fstart_stop
@logger.catch
def update_advance_setting(
    sid: str, URL: str, obj_id: int, hardware_id: int, fms: int
) -> dict:
    """Update the settings Advanced driving.

    Updates the settings in the Advanced tab.
    First part.
    For specific equipment.

    Args:
        sid (str): session id
        URL (str): server address
        obj_id (int): unit/ogject id
        hardware_id (int): hargware id
        fms (int): server number
    Returns:
        data (json): {}	/* пустой объект при удачном выполнении, при неудачном - код ошибки */
    """
    logger.debug("параметры на входе:")
    logger.debug(f"id сессии: {sid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"id объекта: {obj_id}")
    logger.debug(f"id железки (тип устройства): {hardware_id}")
    logger.debug(f"номер сервера: {fms}")
    with open(f"data_tmp/{HW_TMP[fms].get(hardware_id)}.json", "r") as f:
        tmp = json.loads(f.read()).get("reportProps")
        param = {
            "svc": "unit/update_report_settings",
            "params": json.dumps(
                {
                    "itemId": obj_id,
                    "params": {
                        "speedLimit": tmp.get("speedLimit"),
                        "maxMessagesInterval": tmp.get("maxMessagesInterval"),
                        "dailyEngineHoursRate": tmp.get("dailyEngineHoursRate"),
                        "urbanMaxSpeed": tmp.get("urbanMaxSpeed"),
                        "mileageCoefficient": tmp.get("mileageCoefficient"),
                        "speedingTolerance": tmp.get("speedingTolerance"),
                        "speedingMinDuration": tmp.get("speedingMinDuration"),
                        "speedingMode": tmp.get("speedingMode"),
                        "fuelRateCoefficient": tmp.get("fuelRateCoefficient"),
                    },
                }
            ),
            "sid": sid,
        }
        logger.debug(f"параметры запроса: {param}")
        logger.info("Параметры, используемые в отчётах - обновлены")
    response = requests.post(URL, data=param)
    return response.json()


@fstart_stop
@logger.catch
def update_advance_validity_filter(
    sid: str, URL: str, obj_id: int, hardware_id: int, fms: int
) -> dict:
    """Update the settings used in reports.

    Updates the settings in the Advanced tab.
    Second part.
    For specific equipment.

    Args:
        sid (str): session id
        URL (str): server address
        obj_id (int): unit/ogject id
        hardware_id (int): hargware id
        fms (int): server number
    Returns:
        data (json): {}	/* пустой объект при удачном выполнении, при неудачном - код ошибки */
    """
    logger.debug("Параметры на входе:")
    logger.debug(f"id сессии: {sid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"id объекта: {obj_id}")
    logger.debug(f"id железки (тип устройства): {hardware_id}")
    logger.debug(f"номер сервера: {fms}")
    with open(f"data_tmp/{HW_TMP[fms].get(hardware_id)}.json", "r") as f:
        tmp = json.loads(f.read()).get("advProps").get("msgFilter")
        param = {
            "svc": "unit/update_messages_filter",
            "params": json.dumps(
                {
                    "itemId": obj_id,
                    "enabled": tmp.get("enabled"),
                    "skipInvalid": tmp.get("skipInvalid"),
                    "minSats": tmp.get("minSats"),
                    "maxHdop": tmp.get("maxHdop"),
                    "maxSpeed": tmp.get("maxSpeed"),
                    "lbsCorrection": tmp.get("lbsCorrection"),
                }
            ),
            "sid": sid,
        }
        response = requests.post(URL, data=param)
        logger.debug(f"параметры запроса: {param}")
        logger.debug(f"Результат запроса: {response.json()}")
        logger.info("Фильтрация валидности сообщений - обновлены")
    return response.json()


@fstart_stop
@logger.catch
def create_driving_param(ssid: str, URL: str, obj_id: int) -> int:
    """Driving Quality Tab. Add param.

    Eco Driving tab.
    Create and update params.

    Args:
        sid (str): session id
        URL (str): server address
        obj_id (int): unit/ogject id

    Returns:
        integer: if param updated, return 0, else -1
    """
    logger.debug("параметры на входе:")
    logger.debug(f"id сессии: {ssid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"id объекта: {obj_id}")
    param = {
        "svc": "unit/update_drive_rank_settings",
        "params": json.dumps(
            {
                "itemId": obj_id,
                "driveRank": {
                    "acceleration": [
                        {
                            "flags": 2,
                            "min_value": 0.4,
                            "name": "Ускорение: опасное",
                            "penalties": 2000,
                        },
                        {
                            "flags": 2,
                            "max_value": 0.4,
                            "min_value": 0.31,
                            "name": "Ускорение: резкое",
                            "penalties": 1000,
                        },
                    ],
                    "brake": [
                        {
                            "flags": 2,
                            "min_value": 0.35,
                            "name": "Торможение: опасное",
                            "penalties": 2000,
                        },
                        {
                            "flags": 2,
                            "max_value": 0.35,
                            "min_value": 0.31,
                            "name": "Торможение: резкое",
                            "penalties": 1000,
                        },
                    ],
                    "turn": [
                        {
                            "flags": 2,
                            "min_value": 0.4,
                            "name": "Поворот: опасный",
                            "penalties": 1000,
                        },
                        {
                            "flags": 2,
                            "max_value": 0.4,
                            "min_value": 0.31,
                            "name": "Поворот: резкий",
                            "penalties": 500,
                        },
                    ],
                    "speeding": [
                        {
                            "flags": 2,
                            "max_duration": 30,
                            "min_duration": 10,
                            "min_value": 41,
                            "name": "Превышение: опасное",
                            "penalties": 5000,
                        },
                        {
                            "flags": 2,
                            "max_value": 41,
                            "min_duration": 10,
                            "min_value": 21,
                            "name": "Превышение: сильное",
                            "penalties": 2000,
                        },
                        {
                            "flags": 2,
                            "max_value": 21,
                            "min_duration": 10,
                            "min_value": 10,
                            "name": "Превышение: среднее",
                            "penalties": 100,
                        },
                    ],
                    "harsh": [
                        {
                            "flags": 2,
                            "min_value": 0.3,
                            "name": "Резкое вождение",
                            "penalties": 300,
                        }
                    ],
                    "global": {"accel_mode": 0},
                },
            }
        ),
        "sid": ssid,
    }
    response = requests.post(URL, data=param)
    logger.debug(f"параметры запроса: {param}")
    logger.info("Качество вождения - данные обновлены")
    return 0 if len(response.json()) == 0 else -1


@fstart_stop
@logger.catch
def create_object_with_all_params(
    sid: str, URL: str, object_param: dict, fms: int
) -> int:
    """Create an object with sensors.

    The function creates an object on wialon,
    fills it with data based on the template,
    and returns the id of the new object.

    Args:
        sid (str): session id
        URL (str): server address
        object_param (dict): dict with object data
        fms (int): server number

    Returns:
        object_id (int): object id
    """
    logger.debug("Параметры на вход:")
    logger.debug(f"id сессии: {sid}")
    logger.debug(f"адрес сервера: {URL}")
    logger.debug(f"json с параметрами объекта: {object_param}")
    logger.debug(f"номер сервера: {fms}")
    hware = object_param.get("Оборудование").replace("Teltonika ", "")
    try:
        hard_id = HW_ID[fms][hware]
    except KeyError as e:
        logger.error(f"Шаблон {hware} не найден, объект не создан, ошибка {e}")
        with open("logging/import_report.log", "a") as log:
            log.write(f"""Шаблон оборудования {hware} для автоматического
              создания объекта на виалон не найден.\nОбъект не создан.\n""")
        return -1

    new_object = create_object(sid, URL, hard_id, object_param.get("ДЛ"), fms)
    obj_id = new_object.get("item").get("id")

    create_sensors(sid, URL, hard_id, obj_id, fms)

    add_obj_uid(sid, URL, obj_id, hard_id, object_param.get("geozone_imei"))
    add_phone(sid, URL, obj_id, object_param.get("geozone_sim"))
    add_param_engin_axel(sid, URL, obj_id)

    update_advance_setting(sid, URL, obj_id, hard_id, fms)
    update_advance_validity_filter(sid, URL, obj_id, hard_id, fms)
    create_driving_param(sid, URL, obj_id)
    logger.debug("Объект со всеми параметрами, создан")
    return obj_id
