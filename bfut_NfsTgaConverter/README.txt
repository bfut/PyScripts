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
    convert TGA texture alpha channel

USAGE
    python "bfut_NfsTgaConverter (Mto3).py" [</path/to/file>|</path/to/directory>]

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

APPENDIX
    Steps to convert part.fsh and dash.fsh to TGA:
    1. Apply fshtool 1.22 or later
    2. On Linux, e.g., run the following script in a terminal to merge the resulting bitmaps
        #!/bin/sh
        OFILE="${1%%.*}"
        convert "${1}" "${2}" -alpha off -compose CopyOpacity -composite "${OFILE}.tga"

    Steps to convert TGA to part.fsh and dash.fsh:
    1. On Linux, e.g., run the following script in a terminal to split tga to bitmaps
        #!/bin/sh
        OFILE="${1%%.*}"
        convert "${1}" -alpha extract "${OFILE}-a.bmp"
    2. Apply fshtool 1.22 or later
"""