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

def main():
    # Parse command-line
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs=1, help="folder path")
    args = parser.parse_args()

    script_path = pathlib.Path(__file__).parent
    input_folder = pathlib.Path(args.path[0])

    # --------------------------------------
    if not input_folder.is_dir():
        raise NotADirectoryError("input_folder does not exist "
                                 f"or is not a directory ('{input_folder}')")
    output_path = (script_path / input_folder.name).with_suffix(".art")

    i = 0
    with open(output_path, mode="wb") as f:
        for x in sorted(input_folder.glob("*.[tT][gG][aA]")):
            print(f"File = {x}")
            buf = x.read_bytes()

            tga_id_length = int(buf[0])
            tga_width = int.from_bytes(buf[12:14], "little")
            tga_height = int.from_bytes(buf[14:16], "little")
            tga_data_size = 4 * tga_width * tga_height
            hdr_len = 0x12 + tga_id_length

            if len(buf) < tga_data_size:
                print("Skipping... TGA format error (missing alpha channel?)")
                continue

            # print("header:", buf[:hdr_len])
            # print(buf[hdr_len:hdr_len + tga_data_size])
            # print("footer:", buf[hdr_len + tga_data_size:])
            print(f"id_len={tga_id_length} w={tga_width} h={tga_height} "
                  f"in_size={tga_data_size} out_size={len(buf)}")
            # print(tga_width.to_bytes(4, "little"))
            # print(tga_height.to_bytes(4, "little"))

            f.write(tga_width.to_bytes(4, "little"))
            f.write(tga_height.to_bytes(4, "little"))
            f.write(buf[hdr_len:hdr_len + tga_data_size])

            i += 1

    print(f"created file {output_path} (contains {i} TGA files)")
    if i < 1:
        raise Warning("empty ART archive")

if __name__ == "__main__":
    main()
