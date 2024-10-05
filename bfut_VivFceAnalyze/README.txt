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
