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
scl_libfceanalyze.py - Python library

HOMEPAGE
    https://github.com/bfut/PyScripts
"""

import os
import pathlib

import fcecodec as fc
import numpy as np
import polars as pl

import scl_dfutil
import scl_libfedata
from bfut_mywrappers import *

CONFIG = {
    "dev_clean_paths" : False  # default: False
}

min_fcecodec_version = "1.11"
if fc.__version__ < min_fcecodec_version:
    print(f"Error: fcecodec version {fc.__version__} is less than {min_fcecodec_version}. Please install latest fcecodec version.")
    raise ImportError


def find_path_from_list(folder: pathlib.Path, flist: list):
    """
    Find a file in a folder from a list of files. Return the path of the first file found.

    Not case-sensitive.
    """
    inpath_ = pathlib.Path(folder)
    if inpath_.is_dir():
        for subdir, dirs, files in os.walk(inpath_):
            for file in files:
                b = str(file).isprintable()
                if not b:
                    continue
                filepath = (pathlib.Path(subdir) / file)

                if pathlib.Path(filepath.name).as_posix().lower() in flist:
                    return filepath
    return None

def find_matching_file(flist: list, searchme: list):
    """
    Find matching file from two lists of files. Return index of first file found.

    Not case-sensitive.
    """
    for i, f in enumerate(flist):
        if pathlib.Path(f).as_posix().lower() in searchme:
            return i
    return None


# util
def get_fedata_buf(path: pathlib.Path, start = -1, end = -1):
    if start < 0 or end < 0:
        fname = "fedata"
        fendings = [ ".eng", ".bri", ".fre", ".ger", ".ita", ".spa", ".swe" ]
        flist = [ fname + ext for ext in fendings ]
        path = find_path_from_list(path.parent, flist)

        # print(f"path: {path}", flush=True)
        if path is None:
            return None

        fsz = os.path.getsize(path)
        buf = GetBufAt(path, 0, fsz)
    else:
        # print(f"path: {path}", flush=True)
        buf = GetBufAt(path, start, end)

    return buf

def get_car_metadata(path: pathlib.Path, fce_version, start = -1, end = -1):
    fedata = None
    df_fedata = None

    buf = None
    if fce_version in [3, 4]:
        buf = get_fedata_buf(path, start, end)

    if buf is not None:
        if fce_version in [3, 4]:
            fedata = scl_libfedata.FEData()
            fedata.read_fedata(buf)
            df_fedata = fedata.export_polars()
            # print(fedata)
        elif fce_version == 5:
            pass
        else:
            pass
    return fedata, df_fedata





def get_mesh_from_binary(path, start, end):
    buf = GetBufAt(path, start, end)
    mesh = fc.Mesh()
    mesh = LoadFceFromBuf(mesh, buf)
    fce_version = GetFceVersionFromBuf(buf)
    return mesh, fce_version

def get_fce_info(mesh):
    MGetColors = np.array(mesh.MGetColors())
    NumColors = MGetColors.shape[0]
    MGetColors = np.array(MGetColors).flatten().tolist()

    MGetDummyNames = mesh.MGetDummyNames()
    NumDummies = len(MGetDummyNames)
    MGetDummyPos = mesh.MGetDummyPos()
    MGetDummyPos = np.array(MGetDummyPos).flatten().tolist()

    PGetName = [mesh.PGetName(i) for i in range(mesh.MNumParts)]
    PGetPos = np.array([mesh.PGetPos(i) for i in range(mesh.MNumParts)]).flatten().tolist()
    PNumTriags = [mesh.PNumTriags(i) for i in range(mesh.MNumParts)]
    PNumVerts = [mesh.PNumVerts(i) for i in range(mesh.MNumParts)]
    # mesh.PrintInfo()

    return NumColors, MGetColors, NumDummies, MGetDummyNames, MGetDummyPos, PGetName, PGetPos, PNumTriags, PNumVerts


def build_tdf(path: pathlib.Path, format: str, offset, size, name, version, mesh, fedata: dict):
    NumColors, MGetColors, NumDummies, MGetDummyNames, MGetDummyPos, PGetName, PGetPos, PNumTriags, PNumVerts = get_fce_info(mesh)

    fedata = fedata if fedata is not None else {}

    tdf = pl.DataFrame(
        {
            "car_name": [fedata.get("car_name", None)],
            "path": [path.as_posix()],
            "format": [format],
            "offset": [offset],
            "size": [size],

            "name": [name],
            "version": [version],
            "MNumParts": [mesh.MNumParts],
            "MNumTriags": [mesh.MNumTriags],
            "MNumVerts": [mesh.MNumVerts],
            "MNumArts": [mesh.MNumArts],
            "MUnknown3": [mesh.MUnknown3],

            "NumColors": [ NumColors ],
            "MGetColors": [ MGetColors ],

            "NumDummies": [ NumDummies ],
            "MGetDummyNames": [ MGetDummyNames ],
            "MGetDummyPos": [ MGetDummyPos ],

            "PGetName": [ PGetName ],
            "PGetPos": [ PGetPos ],
            "PNumTriags": [ PNumTriags ],
            "PNumVerts": [ PNumVerts ],


        }
    )
    return tdf

def fce_analyze(df_viv: pl.DataFrame, opt_FCEondisk: bool, inpath: pathlib.Path = None):
    df = pl.DataFrame(
        schema={
            "car_name": str,
            "path": str,
            "format": str,
            "offset": int,
            "size": int,

            "name": str,
            "version": int,
            "MNumParts": int,
            "MNumTriags": int,
            "MNumVerts": int,
            "MNumArts": int,
            "MUnknown3": int,

            "NumColors": int,
            "MGetColors": pl.List(int),

            "NumDummies": int,
            "MGetDummyNames": pl.List(str),
            "MGetDummyPos": pl.List(float),

            "PGetName": pl.List(str),
            "PGetPos": pl.List(float),
            "PNumTriags": pl.List(int),
            "PNumVerts": pl.List(int),
        }
    )
    print(df)

    FileNotFoundError_list = []

    df_fedata = pl.DataFrame()


    # Iterate all VIV archives, then iterate all its FCE files.
    # For each FCE file, get mesh data.
    if df_viv is not None:
        fname = "fedata"
        fendings = [ ".bri", ".eng", ".fre", ".ger", ".ita", ".spa", ".swe" ]
        fedatalist = [ fname + ext for ext in fendings ]

        for row in df_viv.iter_rows(named=True):
            # print(row)
            vivpath = pathlib.Path(row["path"])
            if not os.access(vivpath, os.R_OK):
                FileNotFoundError_list.append(vivpath)
                continue
            print(vivpath)

            for i in range(len(row["files"])):
                # get FCE file
                fce = row["files"][i]
                if str(fce).lower().find(".fce") < 0:
                    continue
                print(fce)
                start = row["files_offsets"][i]
                end = row["files_sizes"][i] + start

                # get mesh from FCE within VIV
                mesh, version = get_mesh_from_binary(vivpath, start, end)

                if version < 0:
                    FileNotFoundError_list.append(vivpath)
                    continue

                # get carname from fedata et al.
                fedata = None

                fedata_idx = find_matching_file(row["files"], fedatalist)
                # print(f"fedata_idx: {fedata_idx}")
                if fedata_idx is not None:
                    # print(f"fedata name: {row["files"][fedata_idx]}")
                    fedata_start = row["files_offsets"][fedata_idx]
                    fedata_end = row["files_sizes"][fedata_idx] + fedata_start
                    fedata, tdf_fedata = get_car_metadata(vivpath, version, fedata_start, fedata_end)
                    if fedata is not None:
                        fedata = fedata.get_data()
                    if tdf_fedata is not None:
                        try:
                            df_fedata = df_fedata.vstack(tdf_fedata)
                        except Exception as e:
                            print(e)

                # add row to DataFrame
                tdf = build_tdf(vivpath, "viv", start, end, fce, version, mesh, fedata)
                df = df.vstack(tdf)

    # Iterate over all files in a directory, skip non-FCE.
    # For each FCE file, get mesh data.
    if inpath is not None and opt_FCEondisk:
        inpath_ = pathlib.Path(inpath)

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
                    # if skip:
                    #     print(f"skip: {skip}", filepath.as_posix())
                    #     continue

                    if filepath.suffix.lower() != ".fce":
                        continue
                    print(filepath)

                    # get filepath filesize
                    fsz = os.path.getsize(filepath)

                    # get mesh from FCE
                    mesh, version = get_mesh_from_binary(filepath, 0, fsz)

                    if version < 0:
                        FileNotFoundError_list.append(filepath)
                        continue

                    # get carname from fedata et al.
                    fedata, tdf_fedata = get_car_metadata(filepath, version)
                    if fedata is not None:
                        fedata = fedata.get_data()
                    if tdf_fedata is not None:
                        try:
                            df_fedata = df_fedata.vstack(tdf_fedata)
                        except Exception as e:
                            print(e)

                    # add row to DataFrame
                    tdf = build_tdf(filepath, "fce", 0, fsz, filepath.stem, version, mesh, fedata)
                    df = df.vstack(tdf)

    return df, FileNotFoundError_list, df_fedata


# main
def fceanalyze_main(inpath: pathlib.Path, df_viv, path_json: pathlib.Path, opt_alwaysparseFCE: bool, opt_FCEondisk: bool):
    if not pathlib.Path(path_json).exists() or opt_alwaysparseFCE:
        # drop archives without any FCE files
        df_viv = df_viv.with_columns(
            has_fce=pl.col("files").list.eval(
                pl.element().str.to_lowercase().str.ends_with(".fce")
            ).list.any()
        )
        df_viv = df_viv.filter(
            (pl.col("count_dir_entries_true") > 0) &
            (pl.col("has_fce") == True)
        ).drop("has_fce")

        # analyze FCE files
        df_fce, FileNotFoundError_list, df_fedata = fce_analyze(df_viv, opt_FCEondisk, inpath)

        if CONFIG["dev_clean_paths"]:
            df_fce = df_fce.with_columns(
                pl.col("path")
                .map_elements(lambda x: ".../" + pathlib.Path(x).name, return_dtype=str)
                .alias("path"),
            )

        scl_dfutil.writejson(df_fce, path_json)
    else:
        df_fce = pl.read_json(path_json)
        df_fedata = None

    return df_fce, df_fedata