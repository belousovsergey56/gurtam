"""There are objects with unchanged values here"""

import os

from dotenv import load_dotenv

load_dotenv()

HW_ID = {
    1: {
        "MT-5": 14296,
        "MT-X": 14296,
        "Cesar 25": 14296,
        "FMB130": 37073,
        "FMB125": 8600,
        "FMB920": 4773,
        "FMB140": 37074,
    },
    2: {
        "MT-5": 21,
        "MT-X": 21,
        "Cesar 25": 21,
        "FMB130": 40223,
        "FMB125": 79,
        "FMB920": 51,
        "FMB140": 40224,
    },
    3: {
        "MT-5": 7,
        "MT-X": 7,
        "Cesar 25": 7,
        "FMB130": 23562,
        "FMB125": 93,
        "FMB920": 67,
        "FMB140": 23563,
    },
    4: {
        "MT-5": 20,
        "MT-X": 20,
        "Cesar 25": 20,
        "FMB130": 19510,
        "FMB125": 96,
        "FMB920": 69,
        "FMB140": 19511,
    },
}

HW_TMP = {
    1: {
        14296: "MT-5",
        37073: "FMB130",
        8600: "FMB125",
        4773: "FMB920",
        37074: "FMB140",
    },
    2: {
        21: "MT-5",
        40223: "FMB130",
        79: "FMB125",
        51: "FMB920",
        40224: "FMB140",
    },
    3: {
        7: "MT-5",
        40223: "FMB130",
        79: "FMB125",
        51: "FMB920",
        40224: "FMB140",
    },
    4: {
        20: "MT-5",
        19510: "FMB130",
        96: "FMB125",
        69: "FMB920",
        19511: "FMB140",
    },
}


URL = {
    1: os.getenv("URL"),
    2: os.getenv("URL2"),
    3: os.getenv("URL3"),
    4: os.getenv("URL4"),
}

TOKEN = {
    1: os.getenv("TOKEN"),
    2: os.getenv("TOKEN2"),
    3: os.getenv("TOKEN3"),
    4: os.getenv("TOKEN4"),
}

FMS = [
    (1, "FMS 1"),
    (2, "FMS 2"),
    (3, "FMS 3"),
    (4, "FMS 4"),
]

USER_ID = {
    1: os.getenv("UID_1"),
    2: os.getenv("UID_2"),
    3: os.getenv("UID_3"),
    4: os.getenv("UID_4"),
}

lgroup = {
    "admin": ["gpbal", "carcade", "evolution", "admin", "cesar"],
    "cesar": ["cesar"],
    "gpbal": ["gpbal"],
    "carcade": ["carcade"],
    "evolution": ["evolution"],
}

AUTO = (40187, 41342, 40576, 26338)
TRUCK = (40188, 41343, 40577, 26337)
SPEC = (53014, 53012, 53013, 26339)
RISK = (40166, 59726)
REQUIRED_GROUPS = (78875,)
CUSTOM_FIELDS = ("Vin", "Марка", "Модель")
