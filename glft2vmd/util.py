import json
import os
import struct
import sys


from constants import VERSION, SECTION_COUNT
from enum import Enum


def dump_json_from_file(file_name):
    """
    Dumps the given json file to dictionary.
    :param file_name: Name of json file
    :return: Dictionary representing the json
    """
    with (open(file_name)) as json_file:
        loaded_json = json.loads(json_file.read())

    return loaded_json


def write_vmd_header(file):
    """
    Writes the VMD file header to the given file.
    :param file: File to write to
    """

    file.write(b'VMD\0')
    file.write(struct.pack('>i', VERSION))
    file.write(struct.pack('>i', SECTION_COUNT))
    file.write(struct.pack('>i', 0))

    for i in range(SECTION_COUNT * 2):
        file.write(struct.pack('>i', 0))


def get_file_size(file):
    cur_offset = file.tell()

    file.seek(0, 2)
    file_size = file.tell()

    file.seek(cur_offset, 0)

    return file_size

class Vertex_Attributes(Enum):
    POSITION = 9
    NORMAL = 10
    COLOR_0 = 11
    COLOR_1 = 12
    TEXCOORD_0 = 13
    TEXCOORD_1 = 14
    TEXCOORD_2 = 15
    TEXCOORD_3 = 16
    TEXCOORD_4 = 17
    TEXCOORD_5 = 18
    TEXCOORD_6 = 19
    TEXCOORD_7 = 20
