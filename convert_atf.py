
import sys,os
import codecs
import re
import traceback
import glob
import unittest
import argparse
import json
import codecs

from lark import Lark
from lark import Tree, Transformer, Visitor
from atf_preprocessor import ATF_Preprocessor


class TestConverter(unittest.TestCase):

    # Generic Line Test case for problematic text lines
    def test_lines(self):
        atf_preprocessor = ATF_Preprocessor()

        converted_line,type=atf_preprocessor.process_line("1. [*] AN#.GE₆ GAR-ma U₄ ŠU₂{+up} * AN.GE₆ GAR-ma {d}IŠKUR KA-šu₂ ŠUB{+di} * AN.GE₆",False)
        self.assertTrue(converted_line == "1. [ DIŠ ] AN#.GE₆ GAR-ma U₄ ŠU₂{+up} DIŠ AN.GE₆ GAR-ma {d}IŠKUR KA-šu₂ ŠUB{+di} DIŠ AN.GE₆")

        converted_line,type=atf_preprocessor.process_line("8. KAR <:> e-ṭe-ri :* KAR : e-ke-mu : LUGAL ina di-bi-ri : LUGAL ina ud-da-a-ta",False)
        self.assertTrue(converted_line == "8. KAR < :> e-ṭe-ri :* KAR : e-ke-mu : LUGAL ina di-bi-ri : LUGAL ina ud-da-a-ta")

    # Test case for removal of "$" if following sign not a logogram
    def test_following_sign_not_a_logogram(self):
        atf_preprocessor = ATF_Preprocessor()

        converted_line,type = atf_preprocessor.process_line("5'.	[...] x [...] x-šu₂? : kal : nap-ha-ri : $WA-wa-ru : ia-ar₂-ru", False)
        self.assertTrue(converted_line == "5'. [...] x [...] x-šu₂? : kal : nap-ha-ri : WA-wa-ru : ia-ar₂-ru")

    # Test case for conversion of legacy grammar signs
    def test_legacy_grammar(self):
        atf_preprocessor = ATF_Preprocessor()

        converted_line,type = atf_preprocessor.process_line("57. {mulₓ(AB₂)}GU.LA KI* ŠEG₃ KI*# {kur}NIM.MA{ki} iš-kar* É.GAL : ANŠE.KUR.RA-MEŠ", False)
        self.assertTrue(converted_line == "57. {mulₓ(AB₂)}GU.LA KI* ŠEG₃ KI*# {kur}NIM.MA{ki} iš-kar* E₂.GAL : ANŠE.KUR.RA-MEŠ")

        converted_line,type = atf_preprocessor.process_line("57. {mulₓ(AB₂)}GU.LA KI* ŠEG₃ KI*# {kur}NIM.MA{ki} iš-kar* ÁM.GAL : ANŠE.KUR.RA-MEŠ", True)
        self.assertTrue(converted_line == "57. {mulₓ(AB₂)}GU.LA KI* ŠEG₃ KI*# {kur}NIM.MA{ki} iš-kar* AM₃.GAL : ANŠE.KUR.RA-MEŠ")

    # Test case to test if a lem line is parsed as type "lem_line"
    def test_lemmantization(self):
        atf_preprocessor = ATF_Preprocessor()

        converted_line,type = atf_preprocessor.process_line(
            "#lem: Sin[1]DN; ina[at]PRP; Nisannu[1]MN; ina[at]PRP; tāmartišu[appearance]N; adir[dark]AJ; ina[in]PRP; aṣîšu[going out]'N; adri[dark]AJ; uṣṣi[go out]V; šarrū[king]N; +šanānu[equal]V$iššannanū-ma",
            True)
        self.assertTrue(type == "lem_line")

        converted_line,type = atf_preprocessor.process_line("#lem: iššannanū-ma[equal]V; +šanānu[equal]V$iššannanū-ma; umma[saying]PRP; +šarru[king]N$; mala[as many]PRP; +šarru[king]N$šarri; +maṣû[correspond]V$imaṣṣû",True)
        self.assertTrue(type == "lem_line")

        converted_line,type =  atf_preprocessor.process_line("#lem: +adrūssu[darkly]AV$; īrub[enter]V; +arītu[pregnant (woman)]N$arâtu; ša[of]DET; libbašina[belly]N; ittadûni[contain]V; ina[in]PRP; +Zuqiqīpu[Scorpius]CN$",True)
        self.assertTrue(type == "lem_line")

        converted_line,type = atf_preprocessor.process_line("#lem: šatti[year]N; n; +Artaxerxes[]RN$artakšatsu; šar[king]N; pālih[reverent one]N; Nabu[1]DN; lā[not]MOD; itabbal[disappear]V; maʾdiš[greatly]N; lišāqir[value]V",True)
        self.assertTrue(type == "lem_line")

        converted_line,type = atf_preprocessor.process_line("#lem: +arāmu[cover]V$īrim-ma; ana[according to]PRP; birṣu[(a luminous phenomenon)]N; itârma[turn]V; adi[until]PRP; šāt[who(m)]DET&urri[daytime]N; illakma[flow]V",True)
        self.assertTrue(type == "lem_line")

        converted_line,type = atf_preprocessor.process_line("#lem: u; eššu[new]AJ; u +.",True)
        self.assertTrue(type == "lem_line")

        converted_line, type = atf_preprocessor.process_line(
            "#lem: u; ubû[unit]N; n; n; qû[unit]N; ubû[unit]N; +Ištar[]DN$; Ištar[1]DN +.; +saparru[cart]N$; u", True)
        self.assertTrue(type == "lem_line")

        converted_line,type = atf_preprocessor.process_line(
            "#lem: !+māru[son]N$; !+māru[son]N$māri; târu[turning back]'N; +našû[lift//carrying]V'N$ +.; u; +narkabtu[chariot]N$narkabta; īmur[see]V; marṣu[patient]N; šū[that]IP; qāt[hand]N; Ištar[1]DN; u",
            True)
        self.assertTrue(type == "lem_line")

        converted_line,type = atf_preprocessor.process_line("#lem: +burmāmu[(an animal)//porcupine?]N$; +burmāmu[(an animal)//porcupine?]N$buriyāmu; ša[whose]REL; +zumru[body]N$zumuršu; kīma[like]PRP; +ṭīmu[yarn]N$ṭime; +eṣēru[draw//mark]V$uṣṣuru +.",True)
        self.assertTrue(type == "lem_line")

        converted_line,type = atf_preprocessor.process_line("#lem: u; +appāru[reed-bed]N$",True)
        self.assertTrue(type == "lem_line")



    # Batch test case to test if lemma lines are parsed as type "lem_line"
    def test_lemmatization_batch(self):
        atf_preprocessor = ATF_Preprocessor()

        lines = atf_preprocessor.convert_lines("test-files/test_lemma.atf",False)

        for line,type in lines:
            self.assertTrue(type == "lem_line")

    # Batch test for cccp files
    def test_cccp(self):
            atf_preprocessor = ATF_Preprocessor()

            lines = atf_preprocessor.convert_lines("test-files/cccp_3_1_16_test.atf",False)
            self.assertTrue(len(lines)==259)

            lines = atf_preprocessor.convert_lines("test-files/cccp_3_1_21_test.atf",False)
            self.assertTrue(len(lines) == 90) # one invalid line removed

if __name__ == '__main__':


    atf_preprocessor = ATF_Preprocessor()

    #atf_preprocessor.process_line("#lem: X; attallû[eclipse]N; iššakkan[take place]V; šar[king]N; imâtma[die]V",True)
    #atf_preprocessor.process_line("#lem: mīlū[flood]N; ina[in]PRP; nagbi[source]N; ipparrasū[cut (off)]V; mātu[land]N; ana[according to]PRP; mātu[land]N; +hâqu[go]V$ihâq-ma; šalāmu[peace]N; šakin[displayed]AJ",True)


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

            result = dict()
            result['transliteration'] = []
            result['lemmatization'] = []

            if args.output:
                split = filepath.split("\\")
                filename = split[-1]
                filename = filename.split(".")[0]
                for c_line,c_type in converted_lines:
                    if c_type == "lem_line":
                        lemma_line = []
                        result['lemmatization'].append(lemma_line)
                        for pair in c_line:
                            lemma_line.append({"value":pair[0],"uniqueLemma":pair[1]})


                    else:
                        result['transliteration'].append(c_line)


                json_string = json.dumps(result, ensure_ascii=False).encode('utf8')

                with open(args.output + "/" + filename+".json", "w", encoding='utf8') as outputfile:
                    json.dump(result,outputfile,ensure_ascii=False)





