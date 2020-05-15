
import sys
import codecs
import re
import traceback
import unittest

from lark import Lark
from lark import Tree, Transformer, Visitor


class ConversionError(Exception):
   pass

class ParseError(Exception):
   pass


class Convert_Line_Dividers(Visitor):

  def oracc_atf_text_line__divider(self, tree):
    assert tree.data == "oracc_atf_text_line__divider"
    if tree.children[0] == "*":
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

class ATF_Preprocessor:

    def __init__(self):
        pass
        self.LINE_PARSER = Lark.open("lark-ebl/ebl_atf.lark", maybe_placeholders=True, rel_to=__file__)
        self.LINE_PARSER2 = Lark.open("lark-oracc/oracc_atf.lark", maybe_placeholders=True, rel_to=__file__)

    def process_line(self,atf,debug):

        try:

            if atf.startswith("#lem"):
                raise Exception

            tree = self.LINE_PARSER.parse(atf)
            if debug:
                print("successfully parsed: " +atf)
                print("----------------------------------------------------------------------")
            return atf

        except Exception :
            if debug:
                print("converting line: '"+atf+"'")

            atf = re.sub("([\[<])([\*:])(.*)", r"\1 \2\3", atf) # Convert [* => [  <* => < *
            atf = re.sub("(\*)([\]>])(.*)", r"\1 \2\3", atf) # Convert *] => * ]  ?

            atf = atf.replace("\t", " ") # convert tabs to spaces
            atf = ' '.join(atf.split()) # remove multiple spaces

            try:
                tree = self.LINE_PARSER2.parse(atf)

                #print(tree.pretty())


                Convert_Line_Dividers().visit(tree)
                Convert_Legacy_Grammar_Signs().visit(tree)

                Strip_Signs().visit(tree)

                line_serializer = Line_Serializer()
                line_serializer.visit_topdown(tree)
                converted_line = line_serializer.line.strip(" ")

                if debug:
                    print("converted line as "+tree.data+" --> '" + converted_line + "'")

                try:
                    tree3 = self.LINE_PARSER.parse(converted_line)
                    if debug:
                        print("successfully parsed converted line")
                    print(converted_line)
                    if debug:
                        print("----------------------------------------------------------------------")

                    return converted_line

                except Exception as e:
                    print("\tcould not parse converted line")
                    if debug:
                        traceback.print_exc(file=sys.stdout)



            except:
                error = "could not convert this line"
                print(error+": "+atf)
                traceback.print_exc(file=sys.stdout)

                return(error+": "+atf)




    def convert_lines(self,file,debug):

        print("converting: \""+file+"\"")

        with codecs.open(file, 'r', encoding='utf8') as f:
            atf_ = f.read()

        lines = atf_.split("\n")


        processed_lines = []
        for line in lines:
            # print(line)
            p_line = self.process_line(line,debug)
            if p_line != None:
                processed_lines.append(p_line)

        return processed_lines


