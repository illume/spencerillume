"""

unit tests for the cal3d exporter.


"""



import unittest

import cal3d_exporter

class Cal3dExporter(unittest.TestCase):
    pass
    
    def test_Cal3dBone__to_xml(self):
        """ does converting a Cal3dBone to xml work?
        """
        
        b = cal3d_exporter.Cal3dBone()
        print b.to_xml()
        
    
    def test_Cal3dSkeleton__to_xml(self):
        """ does converting a Cal3dSkeleton to xml work?
        """
        
        s = cal3d_exporter.Cal3dSkeleton()
        s.bones.append(cal3d_exporter.Cal3dBone())
        s.bones.append(cal3d_exporter.Cal3dBone())
        s.bones.append(cal3d_exporter.Cal3dBone())
        s.bones.append(cal3d_exporter.Cal3dBone())

        print s.to_xml()
    
    



if __name__ == "__main__":
    unittest.main()


