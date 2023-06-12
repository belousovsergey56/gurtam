"""This module, create object and fill sensors."""

import json
import os

from dotenv import load_dotenv

import requests

load_dotenv()
URL = os.getenv('URL')

HW_ID = {
    'MT-5': 20,
    'MT-X': 20,
    'Cesar 25': 20,
    'FMB130': 19510,
    'FMB125': 96,
    'FMB920': 69,
    'FMB140': 19511,
    }

HW_TMP = {
    20: 'MT-5',
    19510: 'FMB130',
    96: 'FMB125',
    69: 'FMB920',
    19511: 'FMB140',
}


def create_object(sid: str, hardware_id: int, object_name: str):
    """Create new object.

    Args:
        sid (str): Session id
        hardware (str): hardware name
        object_name (str): this is contract name
    """
    params = {
        'svc': 'core/create_unit',
        'params': json.dumps({
            "creatorId": 117,
            "name": object_name,
            "hwTypeId": hardware_id,
            "dataFlags": 1}),
        'sid': sid
    }
    response = requests.post(URL, data=params)
    return response.json()


def create_sensors(sid: str, hardware_id: int, object_id: int):
    with open(f'data_tmp/{HW_TMP.get(hardware_id)}.json', 'r') as f:
        tmp = json.loads(f.read())
        for sensor in tmp.get('sensors'):
            param = {
                'svc': 'unit/update_sensor',
                'params': json.dumps({"itemId": object_id,
                                      "id": sensor.get("id"),
                                      "callMode": "create",
                                      "unlink": 0,
                                      "n": sensor.get('n'),
                                      "t": sensor.get('t'),
                                      "d": sensor.get('d'),
                                      "m": sensor.get('m'),
                                      "p": sensor.get('p'),
                                      "f": sensor.get('f'),
                                      "c": sensor.get('c'),
                                      "vt": sensor.get('vt'),
                                      "vs": sensor.get('vs'),
                                      "tbl": sensor.get('tbl')}),
                'sid': sid}
            requests.post(URL, data=param)
    return 0


def add_phone(sid: str, obj_id: int, phone: str):
    param = {
        'svc': 'unit/update_phone',
        'params': json.dumps({"itemId": obj_id,
                              "phoneNumber": '+{0}'.format(phone)}),
        'sid': sid}
    response = requests.post(URL, data=param)
    return response.text


def add_obj_uid(sid: str, obj_id: int, hardware_id: int, uid: str):
    param = {
        'svc': 'unit/update_device_type',
        'params': json.dumps({"itemId": obj_id,
                              "deviceTypeId": hardware_id,
                              "uniqueId": uid}),
        'sid': sid
    }
    a = requests.post(URL, data=param)
    print(a.text)


def add_param_engin_axel(sid: str, obj_id: int):
    param = {
        'svc': 'unit/update_calc_flags',
        'params': json.dumps({"itemId": obj_id,
                              "newValue": '0x310'}),
        'sid': sid
    }
    requests.post(URL, data=param)
    return 0


def update_advance_setting(sid: str, obj_id: int, hardware_id: int):
    with open(f'data_tmp/{HW_TMP.get(hardware_id)}.json', 'r') as f:
        tmp = json.loads(f.read()).get('reportProps')
        param = {
            'svc': 'unit/update_report_settings',
            'params': json.dumps(
                {"itemId": obj_id,
                 "params": {
                     "speedLimit": tmp.get('speedLimit'),
                     "maxMessagesInterval": tmp.get('maxMessagesInterval'),
                     "dailyEngineHoursRate": tmp.get('dailyEngineHoursRate'),
                     "urbanMaxSpeed": tmp.get('urbanMaxSpeed'),
                     "mileageCoefficient": tmp.get('mileageCoefficient'),
                     "speedingTolerance": tmp.get('speedingTolerance'),
                     "speedingMinDuration": tmp.get('speedingMinDuration'),
                     "speedingMode": tmp.get('speedingMode'),
                     "fuelRateCoefficient": tmp.get('fuelRateCoefficient')
                 }
                 }),
            'sid': sid
        }
    requests.post(URL, data=param)
    return 0


def update_advance_validity_filter(sid: str, obj_id: int, hardware_id: int):
    with open(f'data_tmp/{HW_TMP.get(hardware_id)}.json', 'r') as f:
        tmp = json.loads(f.read()).get('advProps').get('msgFilter')
        param = {
            'svc': 'unit/update_messages_filter',
            'params': json.dumps({"itemId": obj_id,
                                  "enabled": tmp.get('enabled'),
                                  "skipInvalid": tmp.get('skipInvalid'),
                                  "minSats": tmp.get('minSats'),
                                  "maxHdop": tmp.get('maxHdop'),
                                  "maxSpeed": tmp.get('maxSpeed'),
                                  "lbsCorrection": tmp.get('lbsCorrection')}),
            'sid': sid
        }
        requests.post(URL, data=param)
    return 0


def create_driving_param(ssid: str, obj_id: int):
    param = {
        'svc': 'unit/update_drive_rank_settings',
        'params': json.dumps({"itemId": obj_id,
                              "driveRank": {
                                  "acceleration": [
                                      {
                                          "flags": 2,
                                          "min_value": 0.4,
                                          "name": "Ускорение: опасное",
                                          "penalties": 2000
                                      },
                                      {
                                          "flags": 2,
                                          "max_value": 0.4,
                                          "min_value": 0.31,
                                          "name": "Ускорение: резкое",
                                          "penalties": 1000
                                      }
                                  ],
                                  "brake": [
                                      {
                                          "flags": 2,
                                          "min_value": 0.35,
                                          "name": "Торможение: опасное",
                                          "penalties": 2000
                                      },
                                      {
                                          "flags": 2,
                                          "max_value": 0.35,
                                          "min_value": 0.31,
                                          "name": "Торможение: резкое",
                                          "penalties": 1000
                                      }
                                  ],
                                  "turn": [
                                      {
                                          "flags": 2,
                                          "min_value": 0.4,
                                          "name": "Поворот: опасный",
                                          "penalties": 1000
                                      },
                                      {
                                          "flags": 2,
                                          "max_value": 0.4,
                                          "min_value": 0.31,
                                          "name": "Поворот: резкий",
                                          "penalties": 500
                                      }
                                  ],
                                  "speeding": [
                                      {
                                          "flags": 2,
                                          "max_duration": 30,
                                          "min_duration": 10,
                                          "min_value": 41,
                                          "name": "Превышение: опасное",
                                          "penalties": 5000
                                      },
                                      {
                                          "flags": 2,
                                          "max_value": 41,
                                          "min_duration": 10,
                                          "min_value": 21,
                                          "name": "Превышение: сильное",
                                          "penalties": 2000
                                      },
                                      {
                                          "flags": 2,
                                          "max_value": 21,
                                          "min_duration": 10,
                                          "min_value": 10,
                                          "name": "Превышение: среднее",
                                          "penalties": 100
                                      }
                                  ],
                                  "harsh": [
                                      {
                                          "flags": 2,
                                          "min_value": 0.3,
                                          "name": "Резкое вождение",
                                          "penalties": 300
                                      }
                                  ],
                                  "global": {
                                      "accel_mode": 0
                                  }
                              }
                              }),
        'sid': ssid
    }
    response = requests.post(URL, data=param)
    return 0 if len(response.json()) == 0 else -1


def create_object_with_all_params(sid: str, object_param: dict) -> None:
    hware = object_param.get('Оборудование').replace('Teltonika ', '')
    try:
        hard_id = HW_ID[hware]
    except KeyError:
        with open('logging/import_report.log', 'a') as log:
            log.write(f'Шаблон оборудования {hware} для автоматического  создания объекта на виалон не найден.\nОбъект не создан.\n')
        return -1
    # создать объект
    new_object = create_object(sid, hard_id, object_param.get('ДЛ'))
    obj_id = new_object.get('item').get('id')
    # добавить сенсоры
    sensors = create_sensors(sid, hard_id, obj_id)
    print('sensors response', sensors)
    add_obj_uid(sid, obj_id, hard_id, object_param.get('ИМЕЙ'))
    add_phone(sid, obj_id, object_param.get('ТЕЛЕФОН'))
    add_param_engin_axel(sid, obj_id)
    # обновить дополнительно
    update_advance_setting(sid, obj_id, hard_id)
    update_advance_validity_filter(sid, obj_id, hard_id)
    create_driving_param(sid, obj_id)
    return obj_id
