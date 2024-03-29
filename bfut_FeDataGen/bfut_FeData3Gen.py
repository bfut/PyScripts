# Copyright (C) 2021 and later Benjamin Futasz <https://github.com/bfut>
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
bfut_FeData3Gen.py - generates a full set of FeData3 files in script folder

USAGE
    python bfut_FeData3Gen.py
"""
import pathlib
import struct

def main():
    script_path = pathlib.Path(__file__).parent
    output_folder = "./"

    # ---------------------------------- Set properties here

    # All named values from the offsets table in the next section can be set here.
    # Values usually are expected to be strings unless documented otherwise.
    # Certain values are mandatory, others can be omitted.
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
            #    "color8" : "",
               "color9" : None,
              "color10" : None,
    }

    # ---------------------------------- Do not change anything below
    fname = "fedata."
    fendings = [ "bri", "eng", "fre", "ger", "ita", "spa", "swe" ]

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

    # Create Fedata3
    assert len(offsets) == 65
    header = [0] * len(offsets)
    ptr = hdr_offset
    ofs = 0 + 0x2f  # debug
    for i in range(len(offsets)):
        key = offsets[i]
        if i <= 24:
            if isinstance(key, int):
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
            print(i, "", hex(ofs), " ", ptr, f"0x{ptr:04x}", key, key in data)
            ofs += 4  # debug

            if key in data and data[key] is not None:
                if isinstance(data[key], int):
                    ptr += 4
                elif isinstance(data[key], float):
                    ptr += 4
                else:
                    ptr += len(str(data[key])) + 1
            else:
                ptr += 1

    print(hdr_offset)
    print(header[24])
    print(header)

    # verbose: print encoded header items
    for item in header:
        if isinstance(item, str):
            for c in item:
                print(c, bytes(c.encode("ascii", "ignore")), ord(c),
                      c.encode("ascii", "ignore"))
        """
        else:
            print(
            str(hex(item)),
            bytes( str(item).encode("ascii", "ignore"), )
            )
            print(
            f"{item:04x}",
            type(f"{item:04x}"),
            ord(str(9)),
            chr(9),
            "foo",
            f"{item:04x}"[::-1],
            str(9),
            struct.pack("<I", item),
            str(struct.pack("<I", item)),
            type(struct.pack("<I", item)),
            )
    #    """

    # Write output
    for fending in fendings:
        output_path = script_path / (output_folder + fname + fending)
        print(output_path)
        with open(output_path, mode="wb") as f:
            # file header
            for i in range(len(header)):
                item = header[i]

                if isinstance(item, int) and (i < 19 or i == 24):
                    f.write(struct.pack("<H", item))
                elif isinstance(item, int) and i < 24:
                    f.write(struct.pack("B", item))
                #elif type(x) == float and (i in [43, 44]):
                #    f.write( pack("f", x) )
                elif isinstance(item, int):
                    f.write(struct.pack("<I", item))
                else:
                    for c in item:
                        f.write(c.encode("ascii", "ignore"))
            # file main body
            for i in range(25, len(offsets)):
                key = offsets[i]
                if key in data and data[key] is not None:
                    for c in data[key]:
                        f.write(c.encode("ascii", "ignore"))
                f.write(struct.pack("<B", 0))

if __name__ == "__main__":
    main()
