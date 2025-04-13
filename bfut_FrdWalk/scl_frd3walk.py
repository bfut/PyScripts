# Copyright (C) 2025 and later Benjamin Futasz <https://github.com/bfut>
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
scl_frd3walk.py - tree-walk for FRD3 file

HOW TO USE
    from scl_frd3walk import *
    frd = FRD3Walk(buf)
    frd.walk()
    frd.print()
"""
import struct


class Item:
    def __init__(self, ofs, lvl, name = ""):
        self.ofs = ofs
        self.lvl = lvl
        self.name = name


class FRD3Walk:
    def __init__(self, buf: bytes):
        self.tree = []
        self.ofs = 0
        self.lvl = 0

        self.buf = buf

    def print(self):
        for item in self.tree:
            print(f"{'.' * item.lvl} 0x{item.ofs:08x} {item.name} {item.ofs:02} (0x{item.ofs:0X})")
        print(f"self.ofs: 0x{self.ofs:08x} {self.ofs}")
        print(f"bufsz: 0x{len(self.buf):08x} {len(self.buf)} bytes")


    def walk(self):
        self._FRDFILE3()


    def _FRDFILE3(self):
        node = Item(self.ofs, self.lvl, "FRDFILE3")
        self.tree.append(node)

        self.lvl += 1
        self.ofs += 28
        nBlocks = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        for i in range(nBlocks+1):
            self._TRKBLOCK3()
        for i in range(nBlocks+1):
            self._POLYGONBLOCK3()
        for i in range(4*(nBlocks+1)+1):
            self._XOBJBLOCK3()
        nTextures = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        for i in range(nTextures):
            self._TEXTUREBLOCK3()
        if len(self.buf) != self.ofs:
            raise ValueError(f"FRDFILE3: {len(self.buf)} != {self.ofs} (expected)")
        self.lvl -= 1


    def _TRKBLOCK3(self):
        node = Item(self.ofs, self.lvl, "TRKBLOCK3")
        self.tree.append(node)

        self.lvl += 1
        self.ofs += 12
        self.ofs += 12*4
        nVertices = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        self.ofs += 5*4
        self.ofs += 12*nVertices
        self.ofs += 4*nVertices
        self.ofs += 4*300
        self.ofs += 4
        nPositions = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        nPolygons = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        nVroad = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        nXobj = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        nPolyobj = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        nSoundsrc = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        nLightsrc = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        self.ofs += 8*nPositions
        self.ofs += 8*nPolygons
        self.ofs += 12*nVroad
        self.ofs += 20*nXobj
        self.ofs += 20*nPolyobj
        self.ofs += 16*nSoundsrc
        self.ofs += 16*nLightsrc
        self.lvl -= 1


    def _POLYGONBLOCK3(self):
        node = Item(self.ofs, self.lvl, "POLYGONBLOCK3")
        self.tree.append(node)

        self.lvl += 1
        for i in range(7):
            self._POLYGONCHUNK3()
        for i in range(4):
            self._OBJPOLYBLOCK3()
        self.lvl -= 1


    def _POLYGONCHUNK3(self):
        nPolygons = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        if nPolygons == 0:
            pass
        elif nPolygons > 0:
            self.ofs += 4
            self.ofs += 14*nPolygons
        else:
            raise ValueError(f"POLYGONCHUNK3 nPolygons: {nPolygons} (expected >= 0)")


    def _OBJPOLYBLOCK3(self):
        node = Item(self.ofs, self.lvl, "OBJPOLYBLOCK3")
        self.tree.append(node)

        self.lvl += 1
        nPolygons = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        if nPolygons == 0:
            pass
        elif nPolygons != 0:
            nObjects = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
            self.ofs += 4
            for k in range(nObjects):
                self._POLYOBJDATA3()
        else:
            raise ValueError(f"OBJPOLYBLOCK3 nPolygons: {nPolygons} (expected >= 0)")
        self.lvl -= 1


    def _POLYOBJDATA3(self):
        _type = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        if _type in [3, 4]:
            pass
        elif _type in [1]:
            _nPolygons = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
            self.ofs += 4
            self.ofs += 14*_nPolygons
        else:
            raise ValueError(f"POLYOBJDATA3 type: {_type} (expected in [1, 3, 4])")


    def _XOBJBLOCK3(self):
        node = Item(self.ofs, self.lvl, "XOBJBLOCK3")
        self.tree.append(node)

        self.lvl += 1
        nObjects = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        for i in range(nObjects):
            self._XOBJDATA3()
        self.lvl -= 1


    def _XOBJDATA3(self):
        node = Item(self.ofs, self.lvl, "XOBJDATA3")
        self.tree.append(node)

        self.lvl += 1
        _type = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        self.ofs += 4
        self.ofs += 4
        if _type == 4:  # static extra-object
            self.ofs += 12
            self.ofs += 4
        elif _type == 3:  # animated extra-object
            self.ofs += 9*2
            self.ofs += 1
            self.ofs += 1
            nAnimLength = struct.unpack("h", self.buf[self.ofs:self.ofs+2])[0]
            self.ofs += 2
            self.ofs += 2
            self.ofs += 20*nAnimLength
        else:
            raise ValueError(f"XOBJDATA3 type: {_type} (expected in [3, 4])")

        nVertices = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        self.ofs += 12*nVertices
        self.ofs += 4*nVertices
        nPolygons = struct.unpack("i", self.buf[self.ofs:self.ofs+4])[0]
        self.ofs += 4
        self.ofs += 14*nPolygons
        self.lvl -= 1


    def _TEXTUREBLOCK3(self):
        node = Item(self.ofs, self.lvl, "TEXTUREBLOCK3")
        self.tree.append(node)

        self.ofs += 47
