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
    bfut_NfsTgaConverter (HStoM).py - convert NFSHS tga texture alpha channel to MCO

USAGE
    python "bfut_NfsTgaConverter (HStoM).py" [</path/to/file>|</path/to/directory>]

    If input path is a directory, apply script to all contained *.tga and *.TGA files.
    If no input path is given, current working directory is used.

DOCUMENTATION
    NFS3        = NFS:HS       = MCO      = description
    ==================================================================
    car00.tga   = car##.tga    = part.fsh =
                = dash##.tga   = dash.fsh =
    ==================================================================
      0+6  0x00 =         0x00 =     0x00 = solid
    117+-6 0x75 = 223+-6  0xDF = 200 0xC8 = primary color
    200+-6 0xC8 =  96+-6  0x60 = 180 0xB4 = secondary color
        n/a     = 163+-6  0xA3 =  80 0x50 = interior color
        n/a     =              =          = driver hair
        n/a     =     n/a      =  40 0x28 = seats interior color
        n/a     =     n/a      = 100 0x64 = dashboard interior color 1
        n/a     =     n/a      = 120 0x78 = dashboard interior color 2
    255-6  0xFF = 255     0xFF =     0xFF = transparent
    ==================================================================

TOOLS USED
    hex editor, text editor
"""
import argparse
import pathlib

import numpy as np

CONFIG = {
    "conversion" : "4M",  # "34"|"43"|"3M"|"M4"|"M3"
    "overwrite" : False,  # if True, overwrites input files
}

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
    if not CONFIG["overwrite"]:
        outpath = [(p.parent / (p.stem + "_out" + p.suffix)).with_suffix(".tga") for p in inpath]

    # Workload -------------------------
    tga_header1 = b"\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    tga_header2 = b"\x20\x28"  # Blender-friendly
    tga_footer = b"\x00\x00\x00\x00\x00\x00\x00\x00TRUEVISION-XFILE.\x00"

    def print_value_counts(arr):
        v,c = np.unique(arr, return_counts=True)
        print(np.vstack((v,c)))

    def shift_colors(in_path, out_path, conversion):
        print(f"inpath = {in_path}")
        buf = in_path.read_bytes()

        offset = 0xC
        tga_width = int.from_bytes(buf[offset:offset + 0x2], "little")
        tga_height = int.from_bytes(buf[offset + 0x2:offset + 0x4], "little")

        offset = 0x12
        data = np.array(list(buf[offset:offset + 4 * tga_height * tga_width]), dtype='<u1')

        alpha = data[3::4]
        print_value_counts(alpha)

        # Select pixels
        idx_x00 = np.argwhere(alpha <= 0x00 + 0x6)  # 3,4,M
        idx_xFF = np.argwhere(alpha >= 0xFF - 0x6)  # 3,4,M
        idx_x75 = np.argwhere(np.logical_and(alpha >= 0x75 - 0x6, alpha <= 0x75 + 0x6))  # 3
        idx_xC8 = np.argwhere(np.logical_and(alpha >= 0xC8 - 0x6, alpha <= 0xC8 + 0x6))  # 3,M
        idx_xDF = np.argwhere(np.logical_and(alpha >= 0xDF - 0x6, alpha <= 0xDF + 0x6))  # 4
        idx_x60 = np.argwhere(np.logical_and(alpha >= 0x60 - 0x6, alpha <= 0x60 + 0x6))  # 4
        idx_xA3 = np.argwhere(np.logical_and(alpha >= 0xA3 - 0x6, alpha <= 0xA3 + 0x6))  # 4
        idx_x20 = np.argwhere(np.logical_and(alpha >= 0x20 - 0x6, alpha <= 0x20 + 0x6))  # M
        idx_x28 = np.argwhere(np.logical_and(alpha >= 0x28 - 0x6, alpha <= 0x28 + 0x6))  # M
        idx_x50 = np.argwhere(np.logical_and(alpha >= 0x50 - 0x6, alpha <= 0x50 + 0x6))  # M
        # idx_x64 = np.argwhere(np.logical_and(alpha >= 0x64 - 0x6, alpha <= 0x64 + 0x6))  # M  use idx_x60
        # idx_x78 = np.argwhere(np.logical_and(alpha >= 0x78 - 0x6, alpha <= 0x78 + 0x6))  # M  use idx_x75
        idx_xB4 = np.argwhere(np.logical_and(alpha >= 0xB4 - 0x6, alpha <= 0xB4 + 0x6))  # M

        # Stats only
        tmp = 0
        for n_,a_ in zip(
        [
            0x00,
            0xFF,

            0x75,
            0xC8,

            0xDF,
            0x60,
            0xA3,

            0x20,
            0x28,
            0x50,
            # 0x64,  # redundant
            # 0x78,  # redundant
            0xB4,
        ],
        [
            idx_x00,
            idx_xFF,

            idx_x75,
            idx_xC8,

            idx_xDF,
            idx_x60,
            idx_xA3,

            idx_x20,
            idx_x28,
            idx_x50,
            # idx_x64,  # redundant
            # idx_x78,  # redundant
            idx_xB4,
        ]):
            print(f"val={n_:>3} 0x{n_:02X} count={a_.shape[0]}")
            tmp += a_.shape[0]
        print(f"selected pixels: {tmp}/{alpha.shape[0]} (ignoring {np.amax((0, alpha.shape[0]-tmp))}, redundant {np.amax((0, tmp-alpha.shape[0]))})")

        # Convert pixels
        count_changed = 0
        if conversion == "34":
            print(f"conversion mode: 3->4")
            alpha[idx_x75] = alpha[idx_x75] + 106  # primary
            alpha[idx_xC8] = alpha[idx_xC8] - 104  # secondary
            for a in [
                idx_x75,
                idx_xC8,
            ]:
                count_changed += a.shape[0]
        if conversion == "43":
            print(f"conversion mode: 4->3")
            alpha[idx_xDF] -= 106  # primary
            alpha[idx_x60] -= 104  # secondary
            # all interior colors to secondary
            alpha[idx_xA3] += 37  # interior
            for a in [
                idx_xDF,
                idx_x60,
                idx_xA3,
            ]:
                count_changed += a.shape[0]


        if conversion == "4M":
            print(f"conversion mode: 4->M")
            alpha[idx_xDF] -= 23  # primary
            alpha[idx_x60] += 84  # secondary
            alpha[idx_xA3] -= 83  # interior
            for a in [
                idx_xDF,
                idx_x60,
                idx_xA3,
            ]:
                count_changed += a.shape[0]
        if conversion == "M4":
            print(f"conversion mode: M->4")
            alpha[idx_xC8] += 23  # primary
            alpha[idx_xB4] -= 84  # secondary
            # all interior colors to interior
            alpha[idx_x50] += 83  # interior
            # alpha[idx_x20] =  # ignoring
            alpha[idx_x28] += 123
            alpha[idx_x60] += 59
            alpha[idx_x75] += 43
            for a in [
                idx_xC8,
                idx_xB4,
                idx_x50,
                # idx_x20,  # ignoring
                idx_x28,
                idx_x60,
                idx_x75,
            ]:
                count_changed += a.shape[0]


        if conversion == "3M":
            print(f"conversion mode: 3->M")
            alpha[idx_x75] += 83  # primary
            alpha[idx_xC8] -= 20  # secondary
            for a in [
                idx_x75,
                idx_xC8,
            ]:
                count_changed += a.shape[0]
        if conversion == "M3":
            print(f"conversion mode: M->3")
            alpha[idx_xC8] -= 83  # primary
            alpha[idx_xB4] += 20  # secondary
            # all interior colors to secondary
            alpha[idx_x50] += 120
            # alpha[idx_x20] =  # ignoring
            alpha[idx_x28] += 160
            alpha[idx_x60] += 100
            for a in [
                idx_xC8,
                idx_xB4,
                idx_x50,
                # idx_x20,  # ignoring
                idx_x28,
                idx_x60,
            ]:
                count_changed += a.shape[0]

        print(f"converted pixels: {count_changed}/{alpha.shape[0]}")
        print_value_counts(alpha)

        data[3::4] = alpha
        buf = data.tobytes()

        with open(out_path, mode="wb") as f:
            f.write(tga_header1)
            f.write(tga_width.to_bytes(2, "little"))
            f.write(tga_height.to_bytes(2, "little"))
            f.write(tga_header2)
            f.write(buf)
            f.write(tga_footer)
        print(f"Output = {out_path}")

    for ip, op in zip(inpath, outpath):
        shift_colors(ip, op, CONFIG["conversion"])

if __name__ == "__main__":
    main()
