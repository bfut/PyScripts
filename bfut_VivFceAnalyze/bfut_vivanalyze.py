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
bfut_vivanalyze.py - create a DataFrame from all BIGF/BIGH/BIG4 archives in a directory

USAGE
    1. Write JSON to disk of every BIGF/BIGH/BIG4 file in /path/to/directory:
        python "bfut_vivanalyze.py" /path/to/directory

    2. Write JSON to disk of every FCE file from every VIV archive in /path/to/directory (and optionally from all FCE files in that directory):
        python "bfut_fceanalyze.py" /path/to/directory

INSTALLATION
    Requires Python 3.10 or later.

    python -m pip install -U fcecodec unvivtool polars

HOMEPAGE
    https://github.com/bfut/PyScripts
"""

import argparse
import pathlib

import scl_dfutil
import scl_libvivanalyze

CONFIG = {
    "opt_alwaysparseVIV" : 1  # if False, only parse VIV files if JSON does not exist
    , "viv_archives_path" : "./viv_archives.json"
}

# Parse command (or print module help)
parser = argparse.ArgumentParser()
parser.add_argument("path", nargs="+", help="<path/to/folder>")
args = parser.parse_args()
inpath = pathlib.Path(args.path[0])

print(f"inpath: '{inpath}'")

def main():
    # get BIGF/BIGH/BIG4 data
    df_viv, FileNotFoundError_list, counter = scl_libvivanalyze.vivanalyze_main(CONFIG["viv_archives_path"], inpath, CONFIG["opt_alwaysparseVIV"])

    # print
    # df_viv = df_viv.select(
    #     ['path', 'format', 'size_true', 'files', 'files_offsets', 'files_sizes', 'files_fn_lens', 'files_fn_ofs']
    # )
    # scl_dfutil.printdf(df_viv)
    print(df_viv)
    print(f"df_viv.columns: {df_viv.columns}")
    print(f"FileNotFoundError_list: {FileNotFoundError_list}")
    print(f"counter: {counter}")

if __name__ == "__main__":
    # print(CONFIG)
    main()
