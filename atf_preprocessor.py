
import sys
import codecs
import re
import traceback
import unittest

from lark import Lark
from lark import Tree, Transformer, Visitor



class Convert_Line_Dividers(Visitor):

  def oracc_atf_text_line__divider(self, tree):
    assert tree.data == "oracc_atf_text_line__divider"
    if tree.children[0] == "*" or tree.children[0] == "•":
        tree.children[0] = "DIŠ"

class Convert_Legacy_Grammar_Signs(Visitor):

  replacement_chars = {
      "á" : "a",
      "é" : "e",
      "í": "i",
      "ú" : "u",
      "Á" : "A",
      "É" : "E",
      "Ì" : "I",
      "Ú" : "U"
  }

  def oracc_atf_text_line__logogram_name_part(self, tree):
    assert tree.data == "oracc_atf_text_line__logogram_name_part"
    cnt = 0
    for child in tree.children:

        pattern = re.compile("[ÁÉÍÙ]")
        matches = pattern.search(child)

        if (matches != None):

            match = matches.group(0)
            try:
                next_char = tree.children[cnt + 1]
                tree.children[cnt] = self.replacement_chars[match]
                tree.children[cnt + 1] = next_char + "₃"

            except:
                tree.children[cnt] = self.replacement_chars[match] + "₂"

        cnt = cnt + 1

  def oracc_atf_text_line__value_name_part(self, tree):
    assert tree.data == "oracc_atf_text_line__value_name_part"
    cnt = 0
    for child in tree.children:

        pattern = re.compile("[áíéú]")
        matches = pattern.search(child)

        if(matches!=None):

           match = matches.group(0)
           try:
               next_char = tree.children[cnt + 1]
               tree.children[cnt] = self.replacement_chars[match]
               tree.children[cnt+1] = next_char+"₃"

           except:
               tree.children[cnt] = self.replacement_chars[match]+"₂"



        cnt = cnt + 1

class Strip_Signs(Visitor):

  def oracc_atf_text_line__uncertain_sign(self, tree):
    assert tree.data == "oracc_atf_text_line__uncertain_sign"
    if tree.children[0] == "$":
        tree.children[0] = ""

class DFS(Visitor):
    def visit_topdown(self,tree,result):

        if not hasattr(tree, 'data'):
            return result

        for child in tree.children:
            if isinstance(child, str) or isinstance(child, int):
                result +=child
            result = DFS().visit_topdown(child,result)
        return result

class Line_Serializer(Visitor):
  line = ""
  def text_line(self, tree):
    assert tree.data == "text_line"
    result = DFS().visit_topdown(tree,"")
    self.line+= " " + result
    return result

  def dollar_line(self, tree):
    assert tree.data == "dollar_line"
    result = DFS().visit_topdown(tree,"")
    self.line+= " " + result
    return result

class Get_Line_Number(Visitor):
  nr = ""
  def oracc_atf_text_line__single_line_number(self, tree):
    assert tree.data == "oracc_atf_text_line__single_line_number"
    result = DFS().visit_topdown(tree, "")
    self.nr += result

    return result

def process_line(atf,debug):

    try:
        tree = LINE_PARSER.parse(atf)
        if debug:
            print("successfully parsed: " +atf)
        return atf
    except:
        if debug:
            print("----------------------------------------------------------------------")
            print("converting line: '"+atf+"'")

        #if atf.startswith("#tr"):
         #   print("skipping translation")
        #    return

        #if atf.startswith("#lem"):
        #    print("skipping lemma line")
        #    return


        #atf = atf.replace("[*]", "[ *]") # Strip bullet line start
        #atf = atf.replace("<*>", "< *>") # Strip ?
        #atf = atf.replace("<:>", "< :>") # Strip ?
        #atf = atf.replace("[: *]", "[ : *]") # Strip ?

        atf = re.sub("([\[<])([\*:])(.*)", r"\1 \2\3", atf) # Convert [* => [  <* => < *
        atf = re.sub("(\*)([\]>])(.*)", r"\1 \2\3", atf) # Convert *] => * ]  ?

        atf = atf.replace("\t", " ") # convert tabs to spaces
        atf = ' '.join(atf.split()) # remove multiple spaces

        try:

            tree = LINE_PARSER2.parse(atf)
            #print(tree.pretty())

            Convert_Line_Dividers().visit(tree)
            Convert_Legacy_Grammar_Signs().visit(tree)

            Strip_Signs().visit(tree)



            #line_number_serializer = Get_Line_Number()
            #line_number_serializer.visit_topdown(tree)

            line_serializer = Line_Serializer()
            line_serializer.visit_topdown(tree)
            converted_line = line_serializer.line.strip(" ")


            if debug:
                print("converted line:  '"+converted_line+"'")

            try :
                tree3 = LINE_PARSER.parse(converted_line)
                if debug:
                    print("successfully parsed converted line")
                return atf

            except Exception as e:
                print("\tcould not parse converted line")
                traceback.print_exc(file=sys.stdout)

            if debug:
                print("----------------------------------------------------------------------")

        except:
            print("could not convert line")
            traceback.print_exc(file=sys.stdout)



def convert_lines(file,debug):

    print("converting: \""+file+"\"")

    with codecs.open(file, 'r', encoding='utf8') as f:
        atf_ = f.read()

    lines = atf_.split("\n")


    processed_lines = []
    for line in lines:
        # print(line)
        p_line = process_line(line,debug)
        if p_line != None:
            processed_lines.append(p_line)

    return processed_lines



class TestConverter(unittest.TestCase):

    def test_cccp(self):
        lines = convert_lines("test-files/cccp_3_1_16_test.atf",False)
        self.assertTrue(len(lines)==259)

        lines = convert_lines("test-files/cccp_3_1_21_test.atf",False)
        self.assertTrue(len(lines) == 90) # one invalid line removed


if __name__ == '__main__':


    LINE_PARSER = Lark.open("lark-ebl/ebl_atf.lark", maybe_placeholders=True, rel_to=__file__)
    LINE_PARSER2 = Lark.open("lark-oracc/oracc_atf.lark", maybe_placeholders=True, rel_to=__file__)

    #convert_lines("test-files/test_atf.atf",True)
    convert_lines("test-files/sptu_1_030.atf",True)


    unittest.main()


