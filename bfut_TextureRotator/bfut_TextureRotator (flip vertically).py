# Copyright (C) 2023 and later Benjamin Futasz <https://github.com/bfut>
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
    bfut_TextureRotator (flip vertically).py - alt for when tools such as imagemagick are not available

USAGE
    python "bfut_TextureRotator (flip vertically).py" </path/to/file.tga> [/path/to/output.tga]
    python "bfut_TextureRotator (flip vertically).py" [</path/to/directory>]

    If input path is a directory, apply script to all contained *.tga and *.TGA files.
    If no input path is given, the script directory is used.
"""
import argparse
import pathlib
from typing import Callable

import numpy as np

CONFIG = {
    "rotate_deg" : 180,  # 180
    "flip" : "v",  # overrides "rotate_deg"; None or "horizontally"|"vertically" or 0|1 or "h"|"v"
    "overwrite" : False,  # if True, overwrites input files
}

#
def bfut_read_tga(buf: bytes, verbose=False):
    tga_ = {
        "tga_id_length_4" : int(buf[0]),
        "tga_width_2" : int.from_bytes(buf[12:14], "little"),
        "tga_height_2" : int.from_bytes(buf[14:16], "little"),
        "origin_2" : int.from_bytes(buf[0x10:0x10+2], "little"),
    }
    tga_["tga_data_size"] = tga_["tga_width_2"] * tga_["tga_height_2"] * 4
    tga_["hdr_len"] = 0x12 + tga_["tga_id_length_4"]
    if len(buf[tga_["hdr_len"]:]) < tga_["tga_data_size"]:
        if verbose:
            print("TGA format error: missing alpha channel?")
        return None, None
    pixels = buf[tga_["hdr_len"]:tga_["hdr_len"] + tga_["tga_data_size"]]
    return tga_, pixels

def bfut_write_tga(path, pixels: bytes, width: int, height: int, origin: bytes = None):
    tga_header1 = b"\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    if origin is None or not origin in [b"\x20\x08", b"\x20\x28"]:
        tga_header2 = b"\x20\x28"
    else:
        tga_header2 = origin
    tga_footer = b"\x00\x00\x00\x00\x00\x00\x00\x00TRUEVISION-XFILE.\x00"
    with open(path, mode="wb") as f:
            f.write(tga_header1)
            f.write(width.to_bytes(2, "little"))
            f.write(height.to_bytes(2, "little"))
            f.write(tga_header2)
            f.write(pixels)
            f.write(tga_footer)

def rotate_180deg(data: np.ndarray, _):
    """
        24-bit pixels [rgba]
    """
    data = np.reshape(data, newshape=(-1, 4), order="C")  # [[rgba], [rgba], ...]
    data = data[::-1]
    return data.flatten()

def flip_vertically(data: np.ndarray, width: int):
    """
        24-bit pixels [rgba]
    """
    assert width > 0
    data = np.reshape(data, newshape=(-1, 4, width), order="C")  # [ [[rgba], [rgba], ...] , [[rgba], [rgba], ...], ...]
    data = data[::-1]
    return data.flatten()


def main():
    # Parse command-line
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="*", help="path")
    args = parser.parse_args()

    # Handle paths:
    #       all files in a given directory, overwrite option set in CONFIG
    #  or
    #       mandatory inpath, optional outpath
    if args.path is None or len(args.path) < 1:
        inpath = pathlib.Path(__file__).parent.resolve()  # script path
    else:
        inpath = pathlib.Path(args.path[0])  # can be dir or file
    if inpath.is_dir():
        inpath = sorted([f for f in inpath.iterdir() if (f.suffix).lower() == ".tga"])
        if len(inpath) < 1:
            print("cannot find TGA files in given directory")
            return
    else:
        inpath = [inpath]
    if len(args.path) < 2 and not CONFIG["overwrite"]:
        outpath = [(p.parent / (p.stem + "_out" + p.suffix)).with_suffix(".tga") for p in inpath]
    else:
        outpath = inpath


    # Workload -------------------------
    assert CONFIG["rotate_deg"] == 180
    assert CONFIG["flip"] in [None, "vertically", 1, "v", "horizontally", 0, "h"]

    def texture_rotator(in_path, out_path, pixel_method: Callable):
        print(f"inpath = {in_path}")
        buf = in_path.read_bytes()
        tga_, pixels_bytes = bfut_read_tga(buf)
        pixels = np.array(list(pixels_bytes), dtype='<u1')
        pixels = pixel_method(pixels, tga_["tga_width_2"])
        bfut_write_tga(out_path, pixels.tobytes(), tga_["tga_width_2"], tga_["tga_height_2"], tga_["origin_2"])
        print(f"OUTPUT = {out_path}")


    if CONFIG["flip"] in ["vertically", 1, "v"]:
        pixel_method = flip_vertically
    else:
    # elif CONFIG["rotate_deg"] == 180:
        pixel_method = rotate_180deg

    for ip, op in zip(inpath, outpath):
        texture_rotator(ip, op, pixel_method)

if __name__ == "__main__":
    main()
