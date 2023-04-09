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
    If no input path is given, the script directory is used.

DOCUMENTATION
    NFS3        = NFS:HS       = MCO      = description
    ==================================================================
    car00.tga   = car#00.tga   = part.fsh =
                = dash00.tga   = dash.fsh =
    ==================================================================
      0+6  0x00 =   0+6   0x00 =   0 0x00 = solid
    117+-6 0x75 = 223+-6  0xDF = 200 0xC8 = primary color
    200+-6 0xC8 =  96+-6  0x60 = 180 0xB4 = secondary color
     n/a        = 163+-6  0xA3 =  80 0x50 = interior color
     n/a        =              =  n/a     = driver hair color
     n/a        =  n/a         =  40 0x28 = seats interior color
     n/a        =  n/a         = 100 0x64 = dashboard interior color 1
     n/a        =  n/a         = 120 0x78 = dashboard interior color 2
    255-6  0xFF = 255-6   0xFF = 255 0xFF = transparent
    ==================================================================

TOOLS USED
    hex editor, text editor

APPENDIX
    Convert file.fsh to file.tga on Linux:
    1. Apply fshtool
        fshtool path/to/file.fsh
    2. Run the following script in a terminal to merge the resulting bitmaps to TGA
        #!/bin/sh
        OFILE="${1%%.*}"
        convert "${1}" "${2}" -auto-orient -alpha off -compose CopyOpacity -composite "${OFILE}.tga"

    Convert file.tga to file.fsh on Linux:
    1. Run the following script in a terminal to extract TGA to rgb and alpha channel bitmaps
        python bfut_Tga2Bmp.py path/to/file.tga
    2. Apply fshtool
        fshtool path/to/file_FSH/index.fsh

    Note: imagemagick also extracts rgb and alpha channels, respectively. However, the result may not be fshtool-compatible.
        #!/bin/sh
        OFILE="${1%%.*}"
        convert "${1}" -alpha off "${OFILE}.BMP"
        convert "${1}" -alpha extract "${OFILE}-a.BMP"

    Tools mentioned:
        fshtool v1.22
        imagemagick
        bfut_Tga2Bmp.py <https://github.com/bfut/PyScripts>
"""
