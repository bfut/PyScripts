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
scl_libvivanalyze.py - Python library

HOMEPAGE
    https://github.com/bfut/PyScripts
"""

import os
import pathlib

import polars as pl
import unvivtool as uvt

import scl_dfutil

CONFIG = {
    "dev_clean_paths" : False  # default: False
}

min_unvivtool_version = "3.1"
if uvt.__version__ < min_unvivtool_version:
    print(f"Error: unvivtool version {uvt.__version__} is less than {min_unvivtool_version}. Please install latest unvivtool version.")
    raise ImportError

def get_viv_info(path: pathlib.Path, verbose=False):
    ret = None
    retx = None
    retLEN = None
    retINV = None

    FileNotFoundError_ = None

    # if True:
    if os.access(path, os.R_OK): # and path.is_file():# and not path.is_reserved():
        pass
        # print(f"{path} st_mode: {path.stat().st_mode} R_OK: {os.access(path, os.R_OK)}")

        try:
            ret = uvt.get_info(path)
            ret = uvt.get_info(path, verbose=True)
            retx = uvt.get_info(path, fnhex=True)
            retx = uvt.get_info(path, fnhex=True, verbose=True)
            retLEN = uvt.get_info(path, direnlen=80)
            retLEN = uvt.get_info(path, direnlen=80, verbose=True)
            retINV = uvt.get_info(path, invalid=True)
            retINV = uvt.get_info(path, invalid=True, verbose=True)

        # except FileNotFoundError as e:
        except Exception:
            FileNotFoundError_ = str(path)
            # print(f"FileNotFoundError: {path}: {ret} {retx} {retLEN}")
            # raise e

        if retx is not None:
            files_bytes = retx.get("files", [])
            files_bytes = scl_dfutil.byteslist2hex(files_bytes)
            retx.update({"files": files_bytes})
        if retLEN is not None:
            files_bytes = retLEN.get("files", [])
            files_bytes = scl_dfutil.byteslist2hex(files_bytes)
            retLEN.update({"files": files_bytes})

    if verbose:
        print("ret", "retx", "retLEN")
        print(ret)
        print(retx)
        print(retLEN)
        print("ret", "retx", "retLEN")
        if ret is not None: print(len(ret.get("files", [])))
        if retx is not None: print(len(retx.get("files", [])))
        if retLEN is not None: print(len(retLEN.get("files", [])))
        print("ret", "retx", "retLEN")
        if ret is not None: print(ret["format"])
        if retx is not None: print(retx["format"])
        if retLEN is not None: print(retLEN["format"])



    return FileNotFoundError_, ret, retx, retLEN, retINV

def build_tdf(filepath: pathlib.Path, ret):
    tdf = pl.DataFrame(
        {
            "path": [filepath.as_posix()],
            "format": [ret.get("format", None)],
            "__state": [ret.get("__state", None)],
            "size": [ret.get("size", None)],
            "size_true": [filepath.stat().st_size],
            "count_dir_entries": [ret.get("count_dir_entries", None)],
            "count_dir_entries_true": [ret.get("count_dir_entries_true", None)],
            "header_size": [ret.get("header_size", None)],
            "header_size_true": [ret.get("header_size_true", None)],
            "files": [ ret.get("files") ],
            # "files": [ ret.get("files", None) ],  # this works
            "files_offsets": [ ret.get("files_offsets", None) ],
            "files_sizes": [ ret.get("files_sizes", None) ],
            "files_fn_lens": [ ret.get("files_fn_lens", None) ],
            "files_fn_ofs": [ ret.get("files_fn_ofs", None) ],
            "validity_bitmap": [ ret.get("validity_bitmap", None) ],
        }
    )
    return tdf

def viv_analyze(inpath: pathlib.Path):
    df = pl.DataFrame(
        schema={
            "path": str,
            "format": str,
            "__state": int,
            "size": int,
            "size_true": int,
            "count_dir_entries": int,
            "count_dir_entries_true": int,
            "header_size": int,
            "header_size_true": int,
            # "files": pl.List(pl.Binary),
            "files": pl.List(str),
            "files_offsets": pl.List(int),
            "files_sizes": pl.List(int),
            "files_fn_lens": pl.List(int),
            "files_fn_ofs": pl.List(int),
            "validity_bitmap": pl.List(int),
        }
    )
    print(df)

    inpath_ = pathlib.Path(inpath)

    FileNotFoundError_list = []
    counter = 0
    if inpath_.is_file():
        # print(inpath_)
        e_, ret, retx, retLEN = None, None, None, None
        e_, ret, retx, retLEN = get_viv_info(inpath_)
        if e_ is not None: FileNotFoundError_list.append(e_)
        if ret is None: ret = retx
        if ret is None: ret = retLEN
        # print(ret)
        if ret.get("format") in ["BIGF", "BIGH", "BIG4", "REFPACK_BIGF", "REFPACK_BIGH", "REFPACK_BIG4"]:
            pass
        #     tdf = build_tdf(pathlib.Path(inpath_).resolve(), ret)
        #     print(tdf)
        #     df = df.vstack(tdf)

    if inpath_.is_dir():
        for subdir, dirs, files in os.walk(inpath_):
            for file in files:
                b = str(file).isprintable()
                if not b:
                    continue
                filepath = (pathlib.Path(subdir) / file)

                # # Skip if filepath is in list
                # skip = filepath.as_posix() in [
                #     # uvt.get_info(path)
                #     # 'path/to/file',
                #     ]
                # print(f"skip: {skip}", filepath.as_posix())
                # if skip:
                #     continue
                print(filepath)

                e_, ret, retx, retLEN, retINV = get_viv_info(filepath)
                if e_ is not None: FileNotFoundError_list.append(e_)
                if ret is None: ret = retx
                if ret is None: ret = retLEN
                # continue
                if ret is None:
                    continue
                # if retx is None:
                #     continue
                print(ret)
                if ret.get("format") not in ["BIGF", "BIGH", "BIG4", "REFPACK_BIGF", "REFPACK_BIGH", "REFPACK_BIG4"]:
                    continue
                counter += 1

                tdf = None
                tdfx = None
                tdfLEN = None
                if ret is not None: tdf = build_tdf(filepath, ret)
                if retx is not None: tdfx = build_tdf(filepath, retx)
                if retLEN is not None: tdfLEN = build_tdf(filepath, retLEN)
                if tdf is not None: print(tdf)

                if tdfLEN is not None and tdfLEN.item(0, "count_dir_entries_true") > 0 and tdfLEN.item(0, "count_dir_entries") <= tdfLEN.item(0, "count_dir_entries_true"):
                    df = df.vstack(tdfLEN)
                    continue
                df = df.vstack(tdf)

    return df, FileNotFoundError_list, counter


# main
def vivanalyze_main(path_json: pathlib.Path, inpath: pathlib.Path, opt_alwaysparseVIV: bool):
    if not pathlib.Path(path_json).exists() or opt_alwaysparseVIV:
        df_viv, FileNotFoundError_list, counter = viv_analyze(inpath)

        if CONFIG["dev_clean_paths"]:
            df_viv = df_viv.with_columns(
                pl.col("path")
                .map_elements(lambda x: ".../" + pathlib.Path(x).name, return_dtype=str)
                .alias("path"),
            )

        scl_dfutil.writejson(df_viv, path_json)
    else:
        df_viv = pl.read_json(path_json)
        FileNotFoundError_list = []
        counter = df_viv.shape[0]

    return df_viv, FileNotFoundError_list, counter
