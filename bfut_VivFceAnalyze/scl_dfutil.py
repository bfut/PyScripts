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
scl_dfutil.py - Python library
"""

import pathlib

import polars as pl

# util
def printdf(df: pl.DataFrame | pl.LazyFrame | pl.Series):
    if not isinstance(df, (pl.DataFrame, pl.LazyFrame, pl.Series)):
        print(df)
        return
    if isinstance(df, pl.LazyFrame):
        df = df.collect()
    print(df.to_pandas().to_string())

def writejson(df: pl.DataFrame | pl.LazyFrame, path: pathlib.Path):
    if isinstance(df, pl.LazyFrame):
        df = df.collect()
    # df.to_pandas().to_json(
    #     path,
    #     orient="records",
    #     indent=2,
    # )
    df.write_json(path)

def byteslist2hex(l: list[bytes]):
    if isinstance(l, list):
        return [b.hex() for b in l]
    return None
