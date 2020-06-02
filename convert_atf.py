
import sys,os
import codecs
import re
import traceback
import glob
import unittest
import argparse
import json
import codecs
from pymongo import MongoClient
from lark import Lark
from lark import Tree, Transformer, Visitor
from atf_preprocessor import ATF_Preprocessor
from dotenv import load_dotenv

class LemmatizationError(Exception):
   pass

POS_TAGS  = ["REL" , "DET" , "CNJ" , "MOD" , "PRP" , "SBJ" , "AJ", "AV" , "NU" , "DP" , "IP" , "PP" , "RP" , "XP" , "QP" ,"DN" , "AN" , "CN" , "EN" , "FN" , "GN" , "LN", "MN" , "ON" , "PN" , "QN" , "RN" , "SN" , "TN" , "WN" ,"YN" , "N" , "V" , "J"]

not_lemmatized = {}

class TestConverter(unittest.TestCase):

    # Generic Line Test case for problematic text lines
    def test_lines(self):
        atf_preprocessor = ATF_Preprocessor()

        converted_line,c_array,type=atf_preprocessor.process_line("1. [*] AN#.GE₆ GAR-ma U₄ ŠU₂{+up} * AN.GE₆ GAR-ma {d}IŠKUR KA-šu₂ ŠUB{+di} * AN.GE₆",False)
        self.assertTrue(converted_line == "1. [ DIŠ ] AN#.GE₆ GAR-ma U₄ ŠU₂{+up} DIŠ AN.GE₆ GAR-ma {d}IŠKUR KA-šu₂ ŠUB{+di} DIŠ AN.GE₆")

        converted_line,c_array,type=atf_preprocessor.process_line("8. KAR <:> e-ṭe-ri :* KAR : e-ke-mu : LUGAL ina di-bi-ri : LUGAL ina ud-da-a-ta",False)
        self.assertTrue(converted_line == "8. KAR < :> e-ṭe-ri :* KAR : e-ke-mu : LUGAL ina di-bi-ri : LUGAL ina ud-da-a-ta")

    # Test case for removal of "$" if following sign not a logogram
    def test_following_sign_not_a_logogram(self):
        atf_preprocessor = ATF_Preprocessor()

        converted_line,c_array,type = atf_preprocessor.process_line("5'.	[...] x [...] x-šu₂? : kal : nap-ha-ri : $WA-wa-ru : ia-ar₂-ru", False)
        self.assertTrue(converted_line == "5'. [...] x [...] x-šu₂? : kal : nap-ha-ri : WA-wa-ru : ia-ar₂-ru")

    # Test case for conversion of legacy grammar signs
    def test_legacy_grammar(self):
        atf_preprocessor = ATF_Preprocessor()

        converted_line,c_array,type = atf_preprocessor.process_line("57. {mulₓ(AB₂)}GU.LA KI* ŠEG₃ KI*# {kur}NIM.MA{ki} iš-kar* É.GAL : ANŠE.KUR.RA-MEŠ", False)
        self.assertTrue(converted_line == "57. {mulₓ(AB₂)}GU.LA KI* ŠEG₃ KI*# {kur}NIM.MA{ki} iš-kar* E₂.GAL : ANŠE.KUR.RA-MEŠ")

        converted_line,c_array,type = atf_preprocessor.process_line("57. {mulₓ(AB₂)}GU.LA KI* ŠEG₃ KI*# {kur}NIM.MA{ki} iš-kar* ÁM.GAL : ANŠE.KUR.RA-MEŠ", True)
        self.assertTrue(converted_line == "57. {mulₓ(AB₂)}GU.LA KI* ŠEG₃ KI*# {kur}NIM.MA{ki} iš-kar* AM₃.GAL : ANŠE.KUR.RA-MEŠ")

    # Test case to test if a lem line is parsed as type "lem_line"
    def test_lemmantization(self):
        atf_preprocessor = ATF_Preprocessor()

        converted_line,c_array,type = atf_preprocessor.process_line(
            "#lem: Sin[1]DN; ina[at]PRP; Nisannu[1]MN; ina[at]PRP; tāmartišu[appearance]N; adir[dark]AJ; ina[in]PRP; aṣîšu[going out]'N; adri[dark]AJ; uṣṣi[go out]V; šarrū[king]N; +šanānu[equal]V$iššannanū-ma",
            True)
        self.assertTrue(type == "lem_line")

        converted_line,c_array,type = atf_preprocessor.process_line("#lem: iššannanū-ma[equal]V; +šanānu[equal]V$iššannanū-ma; umma[saying]PRP; +šarru[king]N$; mala[as many]PRP; +šarru[king]N$šarri; +maṣû[correspond]V$imaṣṣû",True)
        self.assertTrue(type == "lem_line")

        converted_line,c_array,type =  atf_preprocessor.process_line("#lem: +adrūssu[darkly]AV$; īrub[enter]V; +arītu[pregnant (woman)]N$arâtu; ša[of]DET; libbašina[belly]N; ittadûni[contain]V; ina[in]PRP; +Zuqiqīpu[Scorpius]CN$",True)
        self.assertTrue(type == "lem_line")

        converted_line,c_array,type = atf_preprocessor.process_line("#lem: šatti[year]N; n; +Artaxerxes[]RN$artakšatsu; šar[king]N; pālih[reverent one]N; Nabu[1]DN; lā[not]MOD; itabbal[disappear]V; maʾdiš[greatly]N; lišāqir[value]V",True)
        self.assertTrue(type == "lem_line")

        converted_line,c_array,type = atf_preprocessor.process_line("#lem: +arāmu[cover]V$īrim-ma; ana[according to]PRP; birṣu[(a luminous phenomenon)]N; itârma[turn]V; adi[until]PRP; šāt[who(m)]DET&urri[daytime]N; illakma[flow]V",True)
        self.assertTrue(type == "lem_line")

        converted_line,c_array,type = atf_preprocessor.process_line("#lem: u; eššu[new]AJ; u +.",True)
        self.assertTrue(type == "lem_line")

        converted_line,c_array, type = atf_preprocessor.process_line(
            "#lem: u; ubû[unit]N; n; n; qû[unit]N; ubû[unit]N; +Ištar[]DN$; Ištar[1]DN +.; +saparru[cart]N$; u", True)
        self.assertTrue(type == "lem_line")

        converted_line,c_array,type = atf_preprocessor.process_line(
            "#lem: !+māru[son]N$; !+māru[son]N$māri; târu[turning back]'N; +našû[lift//carrying]V'N$ +.; u; +narkabtu[chariot]N$narkabta; īmur[see]V; marṣu[patient]N; šū[that]IP; qāt[hand]N; Ištar[1]DN; u",
            True)
        self.assertTrue(type == "lem_line")

        converted_line,c_array,type = atf_preprocessor.process_line("#lem: +burmāmu[(an animal)//porcupine?]N$; +burmāmu[(an animal)//porcupine?]N$buriyāmu; ša[whose]REL; +zumru[body]N$zumuršu; kīma[like]PRP; +ṭīmu[yarn]N$ṭime; +eṣēru[draw//mark]V$uṣṣuru +.",True)
        self.assertTrue(type == "lem_line")

        converted_line,c_array,type = atf_preprocessor.process_line("#lem: u; +appāru[reed-bed]N$",True)
        self.assertTrue(type == "lem_line")



    # Batch test case to test if lemma lines are parsed as type "lem_line"
    def test_lemmatization_batch(self):
        atf_preprocessor = ATF_Preprocessor()

        lines = atf_preprocessor.convert_lines("test-files/test_lemma.atf",False)

        for line in lines:
            self.assertTrue(line['c_type'] == "lem_line")

    # Batch test for cccp files
    def test_cccp(self):
            atf_preprocessor = ATF_Preprocessor()

            lines = atf_preprocessor.convert_lines("test-files/cccp_3_1_16_test.atf",False)
            self.assertTrue(len(lines)==259)

            lines = atf_preprocessor.convert_lines("test-files/cccp_3_1_21_test.atf",False)
            self.assertTrue(len(lines) == 90) # one invalid line removed

if __name__ == '__main__':

    load_dotenv()
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client.get_database(os.getenv("MONGODB_DB"))


    atf_preprocessor = ATF_Preprocessor()

    #atf_preprocessor.process_line("#lem: X; attallû[eclipse]N; iššakkan[take place]V; šar[king]N; imâtma[die]V",True)
    #atf_preprocessor.process_line("#lem: mīlū[flood]N; ina[in]PRP; nagbi[source]N; ipparrasū[cut (off)]V; mātu[land]N; ana[according to]PRP; mātu[land]N; +hâqu[go]V$ihâq-ma; šalāmu[peace]N; šakin[displayed]AJ",True)
    atf_preprocessor.process_line("1. [*] AN#.GE₆ GAR-ma U₄ ŠU₂{+up} * AN.GE₆ GAR-ma {d}IŠKUR KA-šu₂ ŠUB{+di} * AN.GE₆",True)


    parser = argparse.ArgumentParser(description='Converts ATF-files to eBL-ATF standard.')
    parser.add_argument('-i', "--input", required=True,
                        help='path of the input directory')
    parser.add_argument('-o', "--output", required=False,
                        help='path of the output directory')
    parser.add_argument('-g', "--glossary", required=True,
                        help='path to the glossary file')
    parser.add_argument('-t', "--test", required=False, default=False, action='store_true',
                        help='runs all unit-tests')
    parser.add_argument('-v', "--verbose", required=False, default=False, action='store_true',
                        help='display status messages')

    args = parser.parse_args()

    debug = args.verbose

    lemmas_cfforms = dict()
    cfforms_senses = dict()
    cfform_guideword = dict()

    # read glossary
    with open(args.glossary, "r", encoding='utf8') as f:
        for line in f.readlines():

            if line.startswith("@entry"):
                split = line.split(" ")
                cfform = split[1]
                guidword = split[2].rstrip("]").lstrip("[")
                cfform_guideword[cfform] = guidword

            if line.startswith("@form"):
                split = line.split(" ")
                lemma = split[2].lstrip("$").rstrip("\n")
                lemmas_cfforms[lemma] = cfform.strip()

            if line.startswith("@sense"):
                split = line.split(" ")

                for s in split:
                    if s in POS_TAGS:
                        pos_tag = s

                split2 = line.split(pos_tag)
                sense = split2[1].rstrip("\n")
                if not cfform in cfforms_senses:
                    cfforms_senses[cfform] = [sense.strip()]
                else:
                    cfforms_senses[cfform].append(sense.strip())



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


                for line in converted_lines:
                    print(line['c_type'])
                    if line['c_type'] == "lem_line":


                        wrong_lemmatization = False
                        lemma_line = []

                        print(len(last_transliteration))
                        print(last_transliteration)
                        print(len(line['c_array']))
                        print(line['c_array'])

                        for pair in line['c_array'] :

                            oracc_lemma = pair[0]
                            oracc_guideword = pair[1]

                            if "//" in oracc_guideword:
                                oracc_guideword = oracc_guideword.split("//")[0]

                            try:

                                if oracc_guideword == "":
                                    wrong_lemmatization = True
                                    not_lemmatized[oracc_lemma] = True
                                    raise LemmatizationError("Incompatible lemmatization: No guide word to oracc lemma '"+oracc_lemma+"' present")

                                unique_lemmas = []
                                for entry in db.get_collection('words').find({"oraccWords.guideWord": oracc_guideword},{"_id"}):
                                    unique_lemmas.append(entry['_id'])

                                for entry in db.get_collection('words').find({"oraccWords.lemma": oracc_lemma},{"_id"}):
                                    if entry['_id'] not in unique_lemmas:
                                        unique_lemmas.append(entry['_id'])

                                if len(unique_lemmas) == 0:
                                    try:
                                        citation_form = lemmas_cfforms[oracc_lemma]
                                        guideword = cfform_guideword[citation_form]
                                        if "//" in guideword:
                                            guideword = guideword.split("//")[0]
                                        senses = cfforms_senses[citation_form]

                                        if senses != None and oracc_guideword in senses:

                                            for entry in db.get_collection('words').find({"oraccWords.guideWord": guideword}, {"_id"}):
                                                unique_lemmas.append(entry['_id'])

                                            for entry in db.get_collection('words').find({"oraccWords.lemma": citation_form}, {"_id"}):
                                                if entry['_id'] not in unique_lemmas:
                                                    unique_lemmas.append(entry['_id'])

                                            for entry in db.get_collection('words').find({"oraccWords.lemma": oracc_lemma}, {"_id"}):
                                                if entry['_id'] not in unique_lemmas:
                                                    unique_lemmas.append(entry['_id'])

                                    except:
                                        not_lemmatized[oracc_lemma] = True
                                        print("Incompatible lemmatization: No citation form found in the glossary for '"+oracc_lemma+"'")


                                if len(unique_lemmas) == 0:
                                    wrong_lemmatization = True
                                    not_lemmatized[oracc_lemma] = True
                                    raise LemmatizationError("Incompatible lemmatization: No eBL word found to oracc lemma or guide word ("+oracc_lemma+" : "+oracc_guideword+")")

                                else:
                                    lemma_line.append({"value":pair[0],"uniqueLemma":unique_lemmas})
                            except Exception as e:
                                print(e)


                        result['lemmatization'].append(lemma_line)

                    else:
                        last_transliteration = line['c_array']
                        result['transliteration'].append(line['c_line'])


                json_string = json.dumps(result, ensure_ascii=False).encode('utf8')

                with open(args.output + "/" + filename+".json", "w", encoding='utf8') as outputfile:
                    json.dump(result,outputfile,ensure_ascii=False)

                with open(args.output + "/not_lemmatized_" + filename+".txt", "w", encoding='utf8') as outputfile:
                    for key in not_lemmatized:
                        outputfile.write(key+"\n")



