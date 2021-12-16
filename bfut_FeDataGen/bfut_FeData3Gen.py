"""
    bfut_FeData3Gen.py - generates FeData3 files in script folder
    Copyright (C) 2021 and later Benjamin Futasz <https://github.com/bfut>

    This software is provided 'as-is', without any express or implied
    warranty.  In no event will the authors be held liable for any damages
    arising from the use of this software.

    Permission is granted to anyone to use this software for any purpose,
    including commercial applications, and to alter it and redistribute it
    freely, subject to the following restrictions:

    1. The origin of this software must not be misrepresented; you must not
       claim that you wrote the original software. If you use this software
       in a product, an acknowledgment in the product documentation would be
       appreciated but is not required.
    2. Altered source versions must be plainly marked as such, and must not be
       misrepresented as being the original software.
    3. This notice may not be removed or altered from any source distribution.
"""
# format specs due to D. Auroux et al. [1998] Thanks!

import pathlib
import numpy as np
from struct import *

script_path = pathlib.Path(__file__).parent
output_folder = "./"


# --------------------------------------
data = {
           "id" : "plac",
        "class" : "A",
      "pursuit" : "No",
"serial number" : 11,

"car acceleration" : 7,
   "car top speed" : 9,
    "car handling" : 15,
     "car braking" : 18,

     "manufacturer" : "Placeholder",
            "model" : "A",
         "car name" : "Placeholder A",
            "price" : "$3,000",
           "status" : "selfmade",
"transmission type" : "manual",
    "history line1" : "Placeholder",
    "history line2" : "Placeholder",
    "history line3" : "Placeholder",
    "history line4" : "Placeholder",
    "history line5" : "Placeholder",
    "history line6" : "Placeholder",
    "history line7" : "Placeholder",
    "history line8" : "Placeholder",
           "color1" : "Red",
           "color2" : "Silver",
           "color3" : "Deepblue",
           "color4" : "Grey",
           "color5" : "Beige",
           "color6" : "Seagreen",
           "color7" : "",
#           "color8" : "",
           "color9" : None,
          "color10" : None,
}


# --------------------------------------
fname = "fedata."
fendings = ["bri", "eng", "fre", "ger", "ita", "spa", "swe"]

hdr_offset = 0xcf
# Assumes dtype == str unless mentioned otherwise
offsets = [
    "id",
    0x09,
    0x00,
    0x01,
    "class",
    0x03,
    0x00,
    "pursuit",
    0x00,
    0x00,
    0x80,
    "serial number",  # int
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,  # 0x0026

    "car acceleration",  # int  # 0x0028
    "car top speed",  # int
    "car handling",  # int
    "car braking",  # int
    0x5,

    0x28,

    "manufacturer",
    "model",
    "car name",
    "price",
    "status",
    "weight",
    "weight dist",
    "length",
    "width",
    "height",
    "engine",
    "displacement",
    "hp",
    "torque",
    "max engine speed",
    "brakes",
    "tires",
    "top speed",
    "time 0-60",
    "time 0-100",
    "transmission type",
    "num gears",
    "history line1",
    "history line2",
    "history line3",
    "history line4",
    "history line5",
    "history line6",
    "history line7",
    "history line8",
    "color1",
    "color2",
    "color3",
    "color4",
    "color5",
    "color6",
    "color7",
    "color8",
    "color9",
    "color10",
]


header = np.empty(len(offsets), dtype=int)
header = list(header)
ptr = hdr_offset
ofs = 0 + 0x2f  # debug
for i in range(len(offsets)):
    key = offsets[i]
    if i <= 24:
        if type(key) == int:
            header[i] = offsets[i]
        elif key in data:
            if key == "id":
                header[i] = data[key]
            elif key == "class":
                if data[key] == "A" or data[key] == 0x1:
                    header[i] = 0x00  # A
                elif data[key] == "B" or data[key] == 0x1:
                    header[i] = 0x1  # B
                else:
                    header[i] = 0x2  # C
            elif key == "pursuit":
                if data[key] == "Yes" or data[key] == 0x1:
                    header[i] = 0x1  # Yes
                else:
                    header[i] = 0x0  # No
            elif key in [ "serial number",
                          "car acceleration",
                          "car top speed",
                          "car handling",
                          "car braking" ]:
                header[i] = data[key]
        else:
            print("unknown error:", key)
    else:
        header[i] = ptr
        print(i, "", hex(ofs), " ", ptr, f'0x{ptr:04x}', key, key in data)
        ofs += 4  #debug

        if key in data and data[key] != None:

            if type(data[key]) == int:
                ptr += 4
            elif type(data[key]) == float:
                ptr += 4
            else:
                ptr += len(str(data[key])) + 1
        else:
            ptr += 1

print(
hdr_offset,
header[24],
"\n", header
)


for x in header:
    if type(x) == str:
        for c in x:
            print(c, bytes(c.encode('ascii', 'ignore')), ord(c), c.encode('ascii', 'ignore'))
    """
    else:
        print(
          str(hex(x)),
          bytes( str(x).encode('ascii', 'ignore'), )
        )
        print(
          f'{x:04x}',
          type( f'{x:04x}' ),
          ord(str(9)),
          chr(9),
          "foo",
          f'{x:04x}'[::-1],
          str(9),
          pack('<I', x),
          str( pack('<I', x) ),
          type( pack('<I', x) ),
        )
#    """
for fending in fendings:
    p = output_folder + fname + fending
    output_path = pathlib.Path(script_path / p)
    print(output_path)
    with open(output_path, mode='wb') as f:
        """
        file header
        """
        for i in range(len(header)):
            x = header[i]

            if type(x) == int and (i < 19 or i == 24):
                f.write(pack('<H', x))
            elif type(x) == int and i < 24:
                f.write(pack('B', x))
            #elif type(x) == float and (i in [43, 44]):
            #    f.write( pack('f', x) )
            elif type(x) == int:
                f.write(pack('<I', x))
            else:
                for c in x:
                    f.write(c.encode('ascii', 'ignore'))
        """
        file main body
        """
        for i in range(25, len(offsets)):
            key = offsets[i]
            if key in data and data[key] != None:
                for c in data[key]:
                    f.write(c.encode('ascii', 'ignore'))
            f.write(pack('<B', 0))