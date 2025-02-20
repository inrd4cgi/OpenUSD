#!/pxrpythonsubst
#
# Copyright 2017 Pixar
#
# Licensed under the terms set forth in the LICENSE.txt file available at
# https://openusd.org/license.

from pxr import Usd, UsdAbc, UsdGeom, Gf
import unittest

class TestUsdAbcConversionSubdiv(unittest.TestCase):
    def test_RoundTrip(self):
        usdFile = 'original.usda'
        abcFile = 'converted.abc'

        time = Usd.TimeCode.EarliestTime()
        
        self.assertTrue(UsdAbc._WriteAlembic(usdFile, abcFile))

        origStage = Usd.Stage.Open(usdFile)
        stage = Usd.Stage.Open(abcFile)

        testMeshPath = '/World/geom/CenterCross/UpLeft'

        origPrim = origStage.GetPrimAtPath(testMeshPath)
        prim = stage.GetPrimAtPath(testMeshPath)

        # Check subdivision scheme and interpolation options
        self.assertEqual(prim.GetAttribute('subdivisionScheme').Get(time),
                    origPrim.GetAttribute('subdivisionScheme').Get(time));

        self.assertEqual(prim.GetAttribute('interpolateBoundary').Get(time),
                    origPrim.GetAttribute('interpolateBoundary').Get(time));
        self.assertEqual(prim.GetAttribute('faceVaryingLinearInterpolation').Get(time),
                    origPrim.GetAttribute('faceVaryingLinearInterpolation').Get(time));

        # Check crease indices, lengths and sharpness
        creaseIndices = prim.GetAttribute('creaseIndices').Get(time)
        expectedCreaseIndices = [0, 1, 3, 2, 0, 4, 5, 7, 
                                 6, 4, 1, 5, 0, 4, 2, 6, 3, 7]
        for c, e in zip(creaseIndices, expectedCreaseIndices):
            self.assertTrue(Gf.IsClose(c, e, 1e-5))

        creaseLengths = prim.GetAttribute('creaseLengths').Get(time)
        expectedCreaseLengths = [5, 5, 2, 2, 2, 2]
        for c, e in zip(creaseLengths, expectedCreaseLengths):
            self.assertTrue(Gf.IsClose(c, e, 1e-5))

        creaseSharpnesses = prim.GetAttribute('creaseSharpnesses').Get(time)
        expectedCreaseSharpness = [1000, 1000, 1000, 1000, 1000, 1000]
        for c, e in zip(creaseSharpnesses, expectedCreaseSharpness):
            self.assertTrue(Gf.IsClose(c, e, 1e-5))

        # Check face vertices
        faceVertexCounts = prim.GetAttribute('faceVertexCounts').Get(time)
        expectedFaceVertexCounts = [4, 4, 4, 4, 4, 4]
        for c, e in zip(faceVertexCounts, expectedFaceVertexCounts):
            self.assertTrue(Gf.IsClose(c, e, 1e-5))

        # The writer will reverse the orientation because alembic only supports
        # left handed winding order.
        faceVertexIndices = prim.GetAttribute('faceVertexIndices').Get(time)
        expectedFaceVertexIndices = [2, 6, 4, 0, 4, 5, 1, 0, 6, 7, 5, 
                                     4, 1, 5, 7, 3, 2, 3, 7, 6, 0, 1, 3, 2]
        for c, e in zip(faceVertexIndices, expectedFaceVertexIndices):
            self.assertTrue(Gf.IsClose(c, e, 1e-5))

        # Check layer/stage metadata transfer
        self.assertEqual(origStage.GetDefaultPrim().GetPath(),
                    stage.GetDefaultPrim().GetPath())
        self.assertEqual(origStage.GetTimeCodesPerSecond(),
                    stage.GetTimeCodesPerSecond())
        self.assertEqual(origStage.GetFramesPerSecond(),
                    stage.GetFramesPerSecond())
        self.assertEqual(origStage.GetStartTimeCode(),
                    stage.GetStartTimeCode())
        self.assertEqual(origStage.GetEndTimeCode(),
                    stage.GetEndTimeCode())
        self.assertEqual(UsdGeom.GetStageUpAxis(origStage),
                    UsdGeom.GetStageUpAxis(stage))
        

if __name__ == '__main__':
    unittest.main()
