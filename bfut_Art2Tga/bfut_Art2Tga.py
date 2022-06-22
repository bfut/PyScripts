"""
    bfut_Art2Tga.py - from given ART archive unpack TGA data to subfolder
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
import os
import pathlib

def main():
    # Parse command (or print module help)
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", nargs=1, help="path")
    args = parser.parse_args()

    input_file = pathlib.Path(args.cmd[0])
    output_path = pathlib.Path(input_file.parent / input_file.stem)


    # --------------------------------------
    try:
        os.mkdir(output_path)
    except FileExistsError:
        if not output_path.is_dir():
            raise FileExistsError(
                f"output_path exists and is not a directory ({output_path})")

    tga_header1 = b"\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    tga_header2 = b"\x20\x28"
    tga_footer = b"\x00\x00\x00\x00\x00\x00\x00\x00TRUEVISION-XFILE.\x00"

    print(f"File = {input_file}", flush=True)
    with open(input_file, mode="rb") as f:
        buf = f.read()
    # print(len(buf), flush=True)

    offset = 0
    i = 0
    while offset < len(buf):
        tga_width = int.from_bytes(buf[offset:offset + 0x4], "little")
        tga_height = int.from_bytes(buf[offset + 0x4:offset + 0x8], "little")
        tga_data_size = 4 * tga_width * tga_height
        print(tga_width, tga_height)

        # print(tga_width, tga_height, tga_data_size, output_path, offset, flush=True)
        with open(pathlib.Path(
            output_path / (format(i, "04d") + ".tga")), mode="wb") as f:
            f.write(tga_header1)
            f.write(tga_width.to_bytes(2, "little"))
            f.write(tga_height.to_bytes(2, "little"))
            f.write(tga_header2)
            f.write(buf[offset + 0x8:offset + 0x8 + tga_data_size])
            f.write(tga_footer)
        print(f"wrote file {pathlib.Path(output_path / format(i, '04d')).with_suffix('.tga')}", flush=True)

        offset += 0x8 + tga_data_size
        i += 1
    print(f"extracted {i} TGA files", flush=True)

if __name__ == "__main__":
    main()
