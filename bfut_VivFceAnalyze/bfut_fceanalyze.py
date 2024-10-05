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
bfut_fceanalyze.py - create a DataFrame of all FCE files from all VIV (BIGF) archives in a directory (and optionally from all FCE files in that directory)

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

import polars as pl

import scl_dfutil
import scl_libfceanalyze
import scl_libvivanalyze

CONFIG = {
    "opt_alwaysparseVIV" : 1  # if False, only parse VIV files if JSON does not exist
    , "opt_alwaysparseFCE" : 1  # if False, only parse FCE files if JSON does not exist
    , "opt_FCEondisk" : True  # if True, also parse FCE files on disk
    , "viv_archives_path" : "./viv_archives.json"
    , "fce_archives_path" : "./fce_files.json"
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

    # get FCE data
    df_fce, df_fedata = scl_libfceanalyze.fceanalyze_main(inpath, df_viv, CONFIG["fce_archives_path"], CONFIG["opt_alwaysparseFCE"], CONFIG["opt_FCEondisk"])

    # print
    # scl_dfutil.printdf(df_fce)
    print(df_fce)

    if df_fedata is not None:
        # df_fedata = df_fedata.unique()
        # df_fedata = df_fedata.sort(["version", "car_name"])
        df_fedata = df_fedata.drop(["colors"])
        print(df_fedata)
        # scl_dfutil.printdf(df_fedata)

if __name__ == "__main__":
    # print(CONFIG)
    main()
