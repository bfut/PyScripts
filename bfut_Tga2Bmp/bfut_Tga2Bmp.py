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
    bfut_Tga2Bmp - extract TGA (rgb+alpha) to fshtool-compatible BMP files, and create index.fsh

    For given path/to/example.tga, creates subfolder with 0000.BMP, 0000-a.BMP, and index.fsh
    This can be compiled to an FSH immediately using fshtool v1.22

USAGE
    python bfut_Tga2Bmp.py [</path/to/file>|</path/to/directory>]

    If input path is a directory, apply script to all contained *.tga and *.TGA files.
    If no input path is given, the script directory is used.

DESCRIPTION
    fshtool 1.22 encodes an FSH file with transparency from a RGB 24-bit bitmap
    and an Alpha 8-bit bitmap.

    The alpha channel bitmap is expected as 8-bit BMP3 bitmap (alpha) with a
    256c colormap in its header.
    Tools that match this specific BMP3 format are not readily available.

    For instance, widely-used imagemagick's convert supports BMP3,
    but may write a 4-bit BMP3 with 16c colormap when 16 or less colors occur.

APPENDIX
    Convert file.fsh to file.tga on Linux:
    1. Apply fshtool
        fshtool path/to/file.fsh
    2. Run the following script in a terminal to merge the resulting bitmaps to TGA
        #!/bin/sh
        OFILE="${1%%.*}"
        convert "${1}" "${2}" -auto-orient -alpha off -compose CopyOpacity -composite "${OFILE}.tga"

    Convert file.tga to file.fsh on Linux:
    1. Run the following script in a terminal to extract TGA to rgb and alpha channel bitmaps to path/to/file_FSH/
        python bfut_Tga2Bmp.py path/to/file.tga
    2. Apply fshtool
        fshtool path/to/file_FSH/index.fsh

    Note: imagemagick also extracts rgb and alpha channels, respectively. However, the result may not be fshtool-compatible.
        #!/bin/sh
        OFILE="${1%%.*}"
        convert "${1}" -alpha off "${OFILE}.BMP"
        convert "${1}" -alpha extract "${OFILE}-a.BMP"

    Required tools:
        fshtool v1.22
        imagemagick
        bfut_Tga2Bmp.py <https://github.com/bfut/PyScripts>
"""
import argparse
# import contextlib
import os
import pathlib

import numpy as np

CONFIG = {
    "verbose" : True,
}

# def bfut_get_index_for_dashfsh(idxpath: pathlib.Path, width: int, height: int):
#     """
#         Return fshtool v1.22 compatible index file as string.

#         compare format and BUFSZ to fshtool.c -> void fsh_to_bmp(char *fshname)
#     """
#     bufsz = width * height * 4 + 44  # 24-bit TGA
#     bufsz += 500000

#     print("Warning: \"index.fsh\" is generated for dash.fsh "
#           "More than likely this index will have to be replaced for other FSH-targets.")

#     return \
# f"""FSHTool generated file -- be very careful when editing
# {idxpath.with_suffix(".fsh")}
# FSH
# SHPI 1 objects, tag GIMX
# BUFSZ {bufsz}
# NOGLOBPAL
# ds00 0000.BMP
# BMP FD +0 {width} {height} {{0 0 0 0}}
# alpha 0000-a.BMP
# #END
# """

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


def bfut_set_bmp3_header(width: int, height: int, depth: int):
    """
        Returns fshtool-compatible BMP3 bitmap header as dict, and for 8-bit a colorspace bytes-array.

        16-bit, no colorspace, headersize=1078 (0x436) = 0xE + 0x28 + 4 * 256

        8-bit, 256c colorspace, headersize=54 (0x36) = 0xE + 0x28
    """
    if not depth in [8, 24]:
        return None, None, None

    hdrsize = 0xE + 0x28  # headers
    if depth == 8:
        hdrsize += 4 * 256  # colorspace
        num_colors = 1
    else:
        num_colors = 3

    bmp3_ = {
        # Bitmap file header (0xE  14 bytes)
        "bmp3_id_2" : b"\x42\x4D",
        "bmp3_fsize_4" : int(hdrsize + width * height * num_colors).to_bytes(4, "little"),
        "bmp3_reserved_4" : b"\x00\x00\x00\x00",
        "bmp3_pixeloffset_4" : hdrsize.to_bytes(4, "little"),

        # BITMAPINFOHEADER (0x28  40 bytes)
        "dib_hdrsize_4" : b"\x28\x00\x00\x00",
        "dib_width_4" : width.to_bytes(4, "little"),
        "dib_height_4" : height.to_bytes(4, "little"),
        "dib_cplanes_2" : b"\x01\x00",
        "dib_depth_2" : depth.to_bytes(2, "little"),
        "dib_compression_4" : b"\x00\x00\x00\x00",
        "dib_imagesize_4" : int(width * height * num_colors).to_bytes(4, "little"),
        "dib_filler_16" : b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    }

    colorspace256 = np.zeros(4*256, dtype=np.int8)
    for i in range(256):
        colorspace256[i*4:i*4+4] = i
    colorspace256 = colorspace256.tobytes("C")

    return bmp3_, colorspace256


def bfut_tga2bmp(buf: bytes, channel="alpha", verbose_=False):
    tga_, pixels = bfut_read_tga(buf, verbose_)

    if tga_ is None:
        return None, None, None, None

    if tga_["origin_2"].to_bytes(2, "little") == b"\x20\x28":  # flip vertically
        # print(pixels[:4])  # pixel (0,0)
        # print(pixels[-4:])  # pixel (0,-1)
        pixels = np.array(bytearray(pixels), ndmin=1)
        # pixels = np.reshape(pixels, newshape=(-1,tga_["tga_height_2"], 4), order='C')
        pixels = np.reshape(pixels, newshape=(-1, tga_["tga_width_2"], 4), order='C')
        # print(pixels[0,:4])  # pixel (0,0)
        # print(pixels[-1,:4])  # pixel (0,-1)
        print(pixels.shape)
        pixels = np.flip(pixels, axis=0)
        pixels = pixels.flatten(order="C")
        pixels = pixels.tobytes("C")

    if channel.lower() == "alpha":
        bmp3_, colorspace256 = bfut_set_bmp3_header(
            tga_["tga_width_2"],
            tga_["tga_height_2"],
            depth=8)
        return pixels[3::4], bmp3_, colorspace256
    else:  # rgb
        bmp3_, colorspace256 = bfut_set_bmp3_header(
            tga_["tga_width_2"],
            tga_["tga_height_2"],
            depth=24)
        pixels = bytearray(pixels)
        del pixels[3::4]
        return bytes(pixels), bmp3_, None


def main():
    # Parse command-line
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="*", help="path")
    args = parser.parse_args()

    if args.path and len(args.path) > 0:
        inpath = pathlib.Path(args.path[0])
    else:
        inpath = pathlib.Path(__file__).parent.resolve()  # script path

    # Handle paths
    if inpath.is_dir():
        inpath = sorted([f for f in inpath.iterdir() if (f.suffix).lower() == ".tga"])
        if len(inpath) < 1:
            print("cannot find TGA files in given directory")
            return
    else:
        inpath = [inpath]

    outpath = [p.parent / (p.stem + "_FSH") for p in inpath]


    # Workload -------------------------
    def tga2bmp_(inpath: pathlib.Path, outpath: pathlib.Path):
        print(f"inpath = {inpath}")
        buf = inpath.read_bytes()

        pixels, bmp3, _ = bfut_tga2bmp(buf, "rgb", CONFIG["verbose"])
        pixels_a, bmp3_a, colorspace256 = bfut_tga2bmp(buf, "alpha", CONFIG["verbose"])

        if not pixels is None and not pixels_a is None:
            if not outpath.exists():
                os.mkdir(outpath)

            with open((outpath / "0000").with_suffix(".BMP"), mode="wb") as f:
                for d in [
                    bmp3["bmp3_id_2"],
                    bmp3["bmp3_fsize_4"],
                    bmp3["bmp3_reserved_4"],
                    bmp3["bmp3_pixeloffset_4"],
                    bmp3["dib_hdrsize_4"],
                    bmp3["dib_width_4"],
                    bmp3["dib_height_4"],
                    bmp3["dib_cplanes_2"],
                    bmp3["dib_depth_2"],
                    bmp3["dib_compression_4"],
                    bmp3["dib_imagesize_4"],
                    bmp3["dib_filler_16"],
                    pixels,
                ]:
                    f.write(d)
            if CONFIG["verbose"]:
                print(f"""rgb = {(outpath / "0000").with_suffix(".BMP")}""")

            with open((outpath / "0000-a").with_suffix(".BMP"), mode="wb") as f:
                for d in [
                    bmp3_a["bmp3_id_2"],
                    bmp3_a["bmp3_fsize_4"],
                    bmp3_a["bmp3_reserved_4"],
                    bmp3_a["bmp3_pixeloffset_4"],
                    bmp3_a["dib_hdrsize_4"],
                    bmp3_a["dib_width_4"],
                    bmp3_a["dib_height_4"],
                    bmp3_a["dib_cplanes_2"],
                    bmp3_a["dib_depth_2"],
                    bmp3_a["dib_compression_4"],
                    bmp3_a["dib_imagesize_4"],
                    bmp3_a["dib_filler_16"],
                    colorspace256,
                    pixels_a,
                ]:
                    f.write(d)
            if CONFIG["verbose"]:
                print(f"""alpha = {(outpath / "0000-a").with_suffix(".BMP")}""")

            # with open((outpath / "index").with_suffix(".fsh"), "w") as f:
            #     with contextlib.redirect_stdout(f):
            #         print(bfut_get_index_for_dashfsh(inpath,
            #             int.from_bytes(bmp3["dib_height_4"], "little"),
            #             int.from_bytes(bmp3["dib_width_4"], "little")),
            #             CONFIG["fsh_target"]
            #         )
            if CONFIG["verbose"]:
                print(f"""index = {(outpath / "index").with_suffix(".fsh")}""")


    for ip, op in zip(inpath, outpath):
        tga2bmp_(ip, op)

if __name__ == "__main__":
    main()
