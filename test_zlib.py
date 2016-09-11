#!/usr/bin/env python3

import zlib
import os
from PIL import Image
from io import BytesIO

zlib_dir = "laws_zlib"

bytesToInt = lambda x: int.from_bytes(x, "little")

def testPicture(picture):
    print("    Test Picture Size", len(picture))
    picBuf = BytesIO()
    picBuf.write(picture)
    picBuf.seek(0)
    img = Image.open(picBuf)
    print("    Icon Picture OK!")
    
    

def testFile(filePath):
    print(filePath)
    file = open(filePath, "rb")
    offset = bytesToInt(file.read(4))
    date = bytesToInt(file.read(8))
    picSize = bytesToInt(file.read(4))
    if picSize != 0:
        picture = file.read(picSize)
        testPicture(picture)
    else:
        print("    --> No Icon")
        
    file.seek(0)

    file.seek(offset)
    origSize = bytesToInt(file.read(4))
    zlibbed = file.read()

    origFile = zlib.decompress(zlibbed)
    if origSize != len(origFile):
        print("!!!!Orig size not equalent!")
    else:
        print("    Zlib Test OK!")



  
if __name__ == "__main__":
    for root, dirs, files in os.walk(zlib_dir):
        for file in files:
            testFile(zlib_dir+"/"+file)



