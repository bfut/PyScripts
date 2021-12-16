"""
    bfut_Tga2Art.py - generates ART archive from TGA files in given folder (input files sorted)
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
import argparse
import pathlib

# Parse command (or print module help)
parser = argparse.ArgumentParser()
parser.add_argument("cmd", nargs=1, help="path")
args = parser.parse_args()

script_path = pathlib.Path(__file__).parent
input_folder = pathlib.Path(args.cmd[0])


# --------------------------------------
output_path = pathlib.Path(script_path / (input_folder.name + ".art"))

i = 0
with open(output_path, mode='wb') as f:
    for x in sorted(input_folder.glob("*.[tT][gG][aA]")):
        print("File =", x)
        with open(x, mode='rb') as f2:
            buf = f2.read()

        TGA_id_length = int(buf[0])
        TGA_width = int.from_bytes(buf[12:14], "little")
        TGA_height = int.from_bytes(buf[14:16], "little")
        TGA_data_size = 4 * TGA_width * TGA_height
        hdr_len = 0x12 + TGA_id_length

        if len(buf) < TGA_data_size:
            print("TGA format error (missing alpha channel?)")
            continue

        # print("header:", buf[:hdr_len], flush=True)
        # # print(buf[hdr_len:hdr_len + TGA_data_size])
        # print("footer:", buf[hdr_len + TGA_data_size:], flush=True)
        print(TGA_id_length, TGA_width, TGA_height, TGA_data_size, len(buf), flush=True)
        # # print(TGA_width.to_bytes(4, "little"))
        # # print(TGA_height.to_bytes(4, "little"))

        f.write(TGA_width.to_bytes(4, "little"))
        f.write(TGA_height.to_bytes(4, "little"))
        f.write(buf[hdr_len:hdr_len + TGA_data_size])

        i += 1

print("wrote output file {} (contains {} TGA files)".format(output_path, i), flush=True)
if i < 1:
    print("Warning: empty ART archive")