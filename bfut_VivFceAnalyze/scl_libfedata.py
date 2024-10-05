# Copyright (C) 2024 and later Benjamin Futasz <https://github.com/bfut>
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
"""
scl_libfedata.py - Python library

HOMEPAGE
    https://github.com/bfut/PyScripts
"""

def read_fedata3(self, buf: bytes):
    """
    References:
        [1] unofficial_nfs3_file_specs_10.txt (D. Auroux et al.)
    """
    self.data["version"] = 3

    ofs = 0
    self.data["id"] = buf[ofs:ofs+4].decode("ascii")

    ofs = 0x10
    pursuit = buf[ofs:ofs+2]
    if pursuit == b"\x00\x00":
        self.data["pursuit"] = "N"
    elif pursuit == b"\x01\x00":
        self.data["pursuit"] = "Y"
    else:
        self.data["pursuit"] = pursuit

    ofs = 0xA
    car_class = buf[ofs:ofs+2]
    if car_class == b"\x00\x00":
        self.data["class"] = "A"
    elif car_class == b"\x01\x00":
        self.data["class"] = "B"
    elif car_class == b"\x02\x00":
        self.data["class"] = "C"
    elif car_class == b"\xff\x00":
        self.data["class"] = "knockout"
    else:
        self.data["class"] = car_class.decode("utf-8", "backslashreplace")

    ofs = 0x18
    self.data["serial"] = int.from_bytes(buf[ofs:ofs+2], "little")

    # manufacturer
    ofs = 0x2F
    fpos = int.from_bytes(buf[ofs:ofs+4], "little")
    if fpos > 0:
        self.data["manufacturer"] = buf[fpos:buf.index(b"\x00", fpos)].decode("windows-1252")

    # model
    ofs = 0x33
    fpos = int.from_bytes(buf[ofs:ofs+4], "little")
    if fpos > 0:
        self.data["model"] = buf[fpos:buf.index(b"\x00", fpos)].decode("windows-1252")

    # car_name
    ofs = 0x37
    fpos = int.from_bytes(buf[ofs:ofs+4], "little")
    if fpos > 0:
        self.data["car_name"] = buf[fpos:buf.index(b"\x00", fpos)].decode("windows-1252")

    # 10 colors
    ofs_list = [0xA7, 0xAB, 0xAF, 0xB3, 0xB7, 0xBB, 0xBF, 0xC3, 0xC7, 0xCB]
    i = 0
    for ofs in ofs_list:
        fpos = int.from_bytes(buf[ofs:ofs+4], "little")
        if fpos > 0:
            self.data[f"color{i:02}"] = buf[fpos:buf.index(b"\x00", fpos)].decode("windows-1252")
        i += 1

    # n/a in this version
    self.data["bonus"] = None
    self.data["convertible"] = None
    self.data["upgrades"] = None
    self.data["car_info"] = None



def read_fedata4(self, buf: bytes):
    """
    References:
        [1] NFS4HS_Fedata_desc_by_Addict.txt (Addict)
    """
    self.data["version"] = 4

    ofs = 0x0112
    self.data["id"] = buf[ofs:ofs+4].decode("ascii")

    ofs = 0x031E
    self.data["serial"] = int.from_bytes(buf[ofs:ofs+4], "little")

    ofs = 0x0382
    car_class = buf[ofs:ofs+4]
    # print(f"car_class: {car_class}")
    if car_class == b"\x00\x00\x00\x00":
        self.data["class"] = "AAA"
    elif car_class == b"\x01\x00\x00\x00":
        self.data["class"] = "AA"
    elif car_class == b"\x02\x00\x00\x00":
        self.data["class"] = "A"
    elif car_class == b"\x03\x00\x00\x00":
        self.data["class"] = "B"
    elif car_class == b"\xff\x00\x00\x00":
        self.data["class"] = "knockout"
    else:
        self.data["class"] = car_class.decode("utf-8", "backslashreplace")

    ofs = 0x037A
    car_info = int.from_bytes(buf[ofs:ofs+2], "little")
    # print(f"car_info:: {hex(car_info)} {buf[ofs:ofs+2]}")
    # print(f"car_info: {car_info & 0xF}")
    # print(f"car_info: {(car_info >> 4) & 0xF}")
    # print(f"car_info: {(car_info >> 8) & 0xF}")
    # print(f"car_info: {(car_info >> 12) & 0x0F}")

    self.data["car_info"] = hex(car_info)

    match car_info & 0xF:
        case 0:
            self.data["bonus"] = "knockout"
        case 1:
            self.data["bonus"] = "LaNina"
        case 2:
            self.data["bonus"] = "N"
        case 3:
            self.data["bonus"] = "Y"
        case _:
            self.data["bonus"] = str(car_info & 0xF)

    match (car_info >> 4) & 0xF:
        case 0:
            self.data["pursuit"] = "N"
        case 1:
            self.data["pursuit"] = "Y"
        case 2:
            self.data["pursuit"] = "M"  # manufacturer n/a in pursuit
        case 0xA:
            self.data["pursuit"] = "F"  # manufacturer n/a in pursuit
        case _:
            self.data["pursuit"] = str((car_info >> 4) & 0xF)

    match (car_info >> 8) & 0xF:
        case 0:
            self.data["convertible"] = "N"
        case 1:
            self.data["convertible"] = "Y"
        case _:
            self.data["convertible"] = str((car_info >> 8) & 0xF)

    match (car_info >> 12) & 0xF:
        case 0:
            self.data["upgrades"] = "Y"
        case 4:
            self.data["upgrades"] = "N"
        case _:
            self.data["upgrades"] = str((car_info >> 12) & 0xF)

    # manufacturer
    ofs = 0x03C0
    fpos = int.from_bytes(buf[ofs:ofs+4], "little")
    if fpos > 0:
        self.data["manufacturer"] = buf[fpos:buf.index(b"\x00", fpos)].decode("windows-1252")

    # model
    ofs = 0x03C4
    fpos = int.from_bytes(buf[ofs:ofs+4], "little")
    if fpos > 0:
        self.data["model"] = buf[fpos:buf.index(b"\x00", fpos)].decode("windows-1252")

    # car_name
    ofs = 0x03C8
    fpos = int.from_bytes(buf[ofs:ofs+4], "little")
    if fpos > 0:
        self.data["car_name"] = buf[fpos:buf.index(b"\x00", fpos)].decode("windows-1252")

    # 10 colors
    ofs_list = [0x043C, 0x0440, 0x0444, 0x0448, 0x044C, 0x0450, 0x0454, 0x0458, 0x045C, 0x0460]
    i = 0
    for ofs in ofs_list:
        fpos = int.from_bytes(buf[ofs:ofs+4], "little")
        if fpos > 0:
            self.data[f"color{i:02}"] = buf[fpos:buf.index(b"\x00", fpos)].decode("windows-1252")
        i += 1


def export_polars(self):
    try:
        import polars as pl
    except ImportError:
        print("Error: polars not installed")
        return None
    clrs_ = [self.data[f"color{i:02}"] for i in range(10)]
    # print(self.data)
    df = pl.DataFrame(
        {
            # metadata
            "version": [ self.data["version"] ],

            #fedata3 and fedata4
            "id": [ self.data.get("id") ],
            "serial": [ self.data.get("serial") ],
            "class": [ self.data.get("class") ],
            # "class": [ None ],
            "pursuit": [ self.data.get("pursuit") ],
            "manufacturer": [ self.data.get("manufacturer") ],
            "model": [ self.data.get("model") ],
            "car_name": [ self.data.get("car_name") ],
            "colors": [ clrs_ ],

            # fedata4
            "bonus": [ self.data.get("bonus", None) ],
            "convertible": [ self.data.get("convertible", None) ],
            "upgrades": [ self.data.get("upgrades", None) ],
            "car_info": [ self.data.get("car_info", None) ],
        },
        {
            "version": pl.Int32,

            "id": str,
            "serial": pl.Int32,
            "class": str,
            "pursuit": str,
            "manufacturer": str,
            "model": str,
            "car_name": str,
            "colors": pl.List(str),

            "bonus": str,
            "convertible": str,
            "upgrades": str,
            "car_info": str
        }
    )
    return df



class FEData:
    def __init__(self):
        self.data = {}

    def get_version(self, buf):
        """ heuristic """
        if buf is None:
            return -1
        if len(buf) >= 0x464 and buf[:0x2] == b"\x04\x00":
            return 4
        if len(buf) >= 0xCB and buf[0x4:0x6] == b"\x09\x00":
            return 3
        return -1

    read_fedata3 = read_fedata3
    read_fedata4 = read_fedata4
    def read_fedata(self, buf: bytes):
        version = self.get_version(buf)
        if version == 3:
            self.read_fedata3(buf)
        elif version == 4:
            self.read_fedata4(buf)
        else:
            raise ValueError("Unknown version")

    def get_data(self):
        return self.data

    export_polars = export_polars

# def get_fedata(buf):
#     fedata = FEData()
#     fedata.read_fedata(buf)
#     data = fedata.get_data()
#     return data
