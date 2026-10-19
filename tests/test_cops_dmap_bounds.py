import tempfile
import unittest
from pathlib import Path
from tools.patch_cops_dmap_bounds import patch

UPSTREAM = """#include <stdlib.h>
        if (width < UINT16_MAX && height < UINT16_MAX)
        {
            mWidth = (uint16_t)width;
            mHeight = (uint16_t)height;
        }
    mCells = new Cell[mWidth * mHeight];
    for (uint16_t y = 0; ERROR_SUCCESS == err && y < mHeight; ++y)
    DOIF(err, aReader.readInt32(count));
    mPassages.reserve(count);
            if (posX < UINT16_MAX && posX < UINT16_MAX)
            {
                passage->PosX = (uint16_t)posX;
    LOG(INFO, "Found %d layers for the map.", count);

    for (int32_t i = 0; ERROR_SUCCESS == err && i < count; ++i)
                size_t posX = ((startX + sceneOffsetX) + x) - width;
                                size_t posY = ((startY + sceneOffsetY) + y) - height;
                                if (posX < UINT16_MAX && posX < UINT16_MAX)
                DOIF(err, aReader.read(fileName, sizeof(fileName)));
"""

class DMapBoundsPatchTests(unittest.TestCase):
    def test_guards_all_dangerous_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/"src/Map/mapdata.cpp"
            target.parent.mkdir(parents=True)
            target.write_text(UPSTREAM)
            patch(Path(d))
            result=target.read_text()
            for expected in ("16000000ULL","count < 0","posY < mHeight",
                             "posX >= 0 && posY >= 0","memchr(fileName",
                             "new Cell[size_t(mWidth) * size_t(mHeight)]"):
                self.assertIn(expected,result)
            self.assertIn("#include <stdint.h>",result)
            self.assertIn("for (uint16_t y = 0; ERROR_SUCCESS == err && y < mHeight; ++y)",result)
            self.assertIn("passage->PosX = (uint16_t)posX;",result)
    def test_upstream_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/"src/Map/mapdata.cpp"
            target.parent.mkdir(parents=True)
            target.write_text("#include <stdlib.h>\n")
            with self.assertRaises(RuntimeError): patch(Path(d))

if __name__=="__main__": unittest.main()
