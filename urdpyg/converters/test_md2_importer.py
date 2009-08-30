"""

unit tests for the md2 importer.


"""



import unittest
import md2_importer
import os
import pprint

class TestMd2Importer(unittest.TestCase):
    pass

    def testReadHeader(self):
        """
	"""
	md2_file_name = os.path.join("..", "models", "tris.md2")
	md2_texture_file_name = os.path.join("..", "models", "hobgoblin.bmp")

	md2 = md2_importer.Md2Model(md2_file_name, md2_texture_file_name)

	md2._ReadHeader()
	pprint.pprint (md2.header)

	md2.Load()






if __name__ == "__main__":
    unittest.main()


