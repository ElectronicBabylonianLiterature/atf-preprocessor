
import sys,os
import codecs
import re
import traceback
import glob
import unittest

from lark import Lark
from lark import Tree, Transformer, Visitor
from atf_preprocessor import ATF_Preprocessor


class TestConverter(unittest.TestCase):

    def test_lines(self):
        atf_preprocessor = ATF_Preprocessor()

        converted_line=atf_preprocessor.process_line("1. [*] AN#.GE₆ GAR-ma U₄ ŠU₂{+up} * AN.GE₆ GAR-ma {d}IŠKUR KA-šu₂ ŠUB{+di} * AN.GE₆",False)
        self.assertTrue(converted_line == "1. [ DIŠ ] AN#.GE₆ GAR-ma U₄ ŠU₂{+up} DIŠ AN.GE₆ GAR-ma {d}IŠKUR KA-šu₂ ŠUB{+di} DIŠ AN.GE₆")

        converted_line=atf_preprocessor.process_line("5'.	[...] x [...] x-šu₂? : kal : nap-ha-ri : $WA-wa-ru : ia-ar₂-ru",False)
        self.assertTrue(converted_line == "5'. [...] x [...] x-šu₂? : kal : nap-ha-ri : WA-wa-ru : ia-ar₂-ru")

        converted_line=atf_preprocessor.process_line("8. KAR <:> e-ṭe-ri :* KAR : e-ke-mu : LUGAL ina di-bi-ri : LUGAL ina ud-da-a-ta",True)
        self.assertTrue(converted_line == "8. KAR < :> e-ṭe-ri :* KAR : e-ke-mu : LUGAL ina di-bi-ri : LUGAL ina ud-da-a-ta")


    def test_cccp(self):
        atf_preprocessor = ATF_Preprocessor()

        lines = atf_preprocessor.convert_lines("test-files/cccp_3_1_16_test.atf",False)
        self.assertTrue(len(lines)==259)

        lines = atf_preprocessor.convert_lines("test-files/cccp_3_1_21_test.atf",False)
        self.assertTrue(len(lines) == 90) # one invalid line removed


if __name__ == '__main__':

    LINE_PARSER = Lark.open("lark-ebl/ebl_atf.lark", maybe_placeholders=True, rel_to=__file__)
    LINE_PARSER2 = Lark.open("lark-oracc/oracc_atf.lark", maybe_placeholders=True, rel_to=__file__)
    atf_preprocessor = ATF_Preprocessor()

    path = 'convert/'
    for filename in glob.glob(os.path.join(path, '*.atf')):
        with open(filename, 'r') as f:
            atf_preprocessor.convert_lines(filename, True)




    unittest.main()


