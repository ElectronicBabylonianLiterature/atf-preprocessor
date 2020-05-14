
import sys,os
import codecs
import re
import traceback
import glob
import unittest
import argparse

from lark import Lark
from lark import Tree, Transformer, Visitor
from atf_preprocessor import ATF_Preprocessor


class TestConverter(unittest.TestCase):

    def test_lines(self):
        atf_preprocessor = ATF_Preprocessor()

        converted_line=atf_preprocessor.process_line("1. [*] AN#.GE₆ GAR-ma U₄ ŠU₂{+up} * AN.GE₆ GAR-ma {d}IŠKUR KA-šu₂ ŠUB{+di} * AN.GE₆",False)
        self.assertTrue(converted_line == "1. [ DIŠ ] AN#.GE₆ GAR-ma U₄ ŠU₂{+up} DIŠ AN.GE₆ GAR-ma {d}IŠKUR KA-šu₂ ŠUB{+di} DIŠ AN.GE₆")

        converted_line=atf_preprocessor.process_line("8. KAR <:> e-ṭe-ri :* KAR : e-ke-mu : LUGAL ina di-bi-ri : LUGAL ina ud-da-a-ta",False)
        self.assertTrue(converted_line == "8. KAR < :> e-ṭe-ri :* KAR : e-ke-mu : LUGAL ina di-bi-ri : LUGAL ina ud-da-a-ta")


    def test_following_sign_not_a_logogram(self):
        atf_preprocessor = ATF_Preprocessor()

        converted_line = atf_preprocessor.process_line("5'.	[...] x [...] x-šu₂? : kal : nap-ha-ri : $WA-wa-ru : ia-ar₂-ru", False)
        self.assertTrue(converted_line == "5'. [...] x [...] x-šu₂? : kal : nap-ha-ri : WA-wa-ru : ia-ar₂-ru")

    def test_legacy_grammar(self):
        atf_preprocessor = ATF_Preprocessor()

        converted_line = atf_preprocessor.process_line("57. {mulₓ(AB₂)}GU.LA KI* ŠEG₃ KI*# {kur}NIM.MA{ki} iš-kar* É.GAL : ANŠE.KUR.RA-MEŠ", False)
        self.assertTrue(converted_line == "57. {mulₓ(AB₂)}GU.LA KI* ŠEG₃ KI*# {kur}NIM.MA{ki} iš-kar* E₂.GAL : ANŠE.KUR.RA-MEŠ")

        converted_line = atf_preprocessor.process_line("57. {mulₓ(AB₂)}GU.LA KI* ŠEG₃ KI*# {kur}NIM.MA{ki} iš-kar* ÁM.GAL : ANŠE.KUR.RA-MEŠ", True)
        self.assertTrue(converted_line == "57. {mulₓ(AB₂)}GU.LA KI* ŠEG₃ KI*# {kur}NIM.MA{ki} iš-kar* AM₃.GAL : ANŠE.KUR.RA-MEŠ")



    def test_cccp(self):
        atf_preprocessor = ATF_Preprocessor()

        lines = atf_preprocessor.convert_lines("test-files/cccp_3_1_16_test.atf",False)
        self.assertTrue(len(lines)==259)

        lines = atf_preprocessor.convert_lines("test-files/cccp_3_1_21_test.atf",False)
        self.assertTrue(len(lines) == 90) # one invalid line removed


if __name__ == '__main__':


    atf_preprocessor = ATF_Preprocessor()

    atf_preprocessor.process_line("#lem: attallû[eclipse]N; iššakinma[take place]V; enūma[when]SBJ; īrup[cloud over]V; attallû[eclipse]N; iššakinma[take place]V; Adad[1]DN; +rigmu[voice]N$rigimšu;",True)

    #atf_preprocessor.process_line("#lem: attallû[eclipse]N; iššakinma[take place]V; enūma[when]SBJ; īrup[cloud over]V; attallû[eclipse]N; iššakinma[take place]V; Adad[1]DN; +rigmu[voice]N$rigimšu; iddi[utter]V; attallû[eclipse]N",True)
    #atf_preprocessor.process_line("@translation parallel en project",True)



    parser = argparse.ArgumentParser(description='Converts ATF-files to eBL-ATF standard.')
    parser.add_argument('-i', "--input", required=True,
                        help='path of the input directory')
    parser.add_argument('-o', "--output", required=False,
                        help='path of the output directory')
    parser.add_argument('-t', "--test", required=False, default=False, action='store_true',
                        help='runs all unit-tests')
    parser.add_argument('-v', "--verbose", required=False, default=False, action='store_true',
                        help='display status messages')

    args = parser.parse_args()

    debug = args.verbose



    for filepath in glob.glob(os.path.join(args.input, '*.atf')):
        with open(filepath, 'r') as f:

            converted_lines = atf_preprocessor.convert_lines(filepath, debug)

            if args.output:
                split = filepath.split("\\")
                filename = split[-1]

                f = open(args.output + "/" + filename, "wb")
                for c_line in converted_lines:
                    c_line=c_line+"\n"
                    f.write(c_line.encode('utf-8'))
                f.close()





