import time
import re
import signal
import json

import javalang
import javalang.tree as Tree

def set_timeout(num):
    def wrap(func):
        def handle(signum, frame):  # 收到信号 SIGALRM 后的回调函数，第一个参数是信号的数字，第二个参数是the interrupted stack frame.
            raise RuntimeError
 
        def to_do(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handle)  # 设置信号和回调函数
                signal.alarm(num)  # 设置 num 秒的闹钟
                # print('start alarm signal.')
                r = func(*args, **kwargs)
                # print('close alarm signal.')
                signal.alarm(0)  # 关闭闹钟
                return r
            except RuntimeError as e:
                return [], [], [], set()
 
        return to_do
 
    return wrap

class CodeParser(object):
    def __init__(self, debug=False):
        self.debug = debug
        pass

    def preprocess(self, code:str):
        code = re.sub(r";([^\n])", r";\n\1", code)
        code = re.sub(r"\{([^\n])", r"{\n\1", code)
        code = re.sub(r"\}([^\n])", r"}\n\1", code)
        return code
    
    def split_code_into_blocks(self, code:str):
        ret = []
        bracket_st_idx = re.search(r"^.*?\{$", code, re.M)
        while (bracket_st_idx != None):
            bracket_ed_idx = bracket_st_idx.span()[1]
            bracket_st_idx = bracket_st_idx.span()[0]
            if bracket_st_idx > 0:
                ret.append(code[:bracket_st_idx])
            left_bracket_cnt = 1

            while bracket_ed_idx < len(code):
                if code[bracket_ed_idx] == "{":
                    left_bracket_cnt += 1
                elif code[bracket_ed_idx] == "}":
                    left_bracket_cnt -= 1
                bracket_ed_idx += 1
                if left_bracket_cnt == 0:
                    break
            ret.append(code[bracket_st_idx:bracket_ed_idx])
            code = code[bracket_ed_idx:]
            bracket_st_idx = re.search(r"^.*?\{$", code, re.M)
        if code and not ret:
            return [code]
        return ret
    def merge_dict(self, dst_dict, src_dict):
        for key in src_dict:
            if key not in dst_dict:
                dst_dict[key] = []
            dst_dict[key].extend(src_dict[key])
    
    @set_timeout(1)
    def parse_code(self, code):
        # code = self.preprocess(code)
        class_object_pairs, class_fields, class_method_dics = [], [], []
        try:
            class_object_pairs, class_fields, class_method_dics = self.parse_code_block_into_compilation_unit(code)
            if self.debug:
                print("Parse into compilation unit succeed!")
            return class_object_pairs, class_fields, class_method_dics, self.extract_import_sents(code)
        except javalang.parser.JavaSyntaxError as e:
            if self.debug:
                print("Trying to parse it into compilation unit failed")
            for code_block in self.split_code_into_blocks(code):
                try: 
                    tmp_pair, tmp_field, tmp_dic = self.parse_code_block_into_body_declaration(code_block)
                    if self.debug:
                        print("Parse into body_declaration succeed!")
                    class_object_pairs.append(tmp_pair)
                    class_fields.append(tmp_field)
                    class_method_dics.append(tmp_dic)
                except javalang.parser.JavaSyntaxError as e:
                    if self.debug:
                        print("Trying to parse it into body_declaration failed")
                    try:
                        tmp_pair, tmp_field, tmp_dic = self.parse_code_block_into_expression(code_block)
                        if self.debug:
                            print("Parse into expression succeed!")
                        class_object_pairs.append(tmp_pair)
                        class_fields.append(tmp_field)
                        class_method_dics.append(tmp_dic)
                    except javalang.parser.JavaSyntaxError as e:
                        if self.debug:
                            print("Trying to parse it into expression failed")
                        continue
                    except Exception as e:
                        if self.debug:
                            print("we failed")
                        continue
                except Exception as e:
                    continue
        except Exception as e:
            pass
        return class_object_pairs, class_fields, class_method_dics, self.extract_import_sents(code)
    
    
    def parse_code_block_into_body_declaration(self, code_block):
        if self.debug:
            print("parse_code_block_into_body_declaration called")
        tokens = javalang.tokenizer.tokenize(code_block)
        if self.debug:
            print("tokenizing finished")
        parser = javalang.parser.Parser(tokens)
        if self.debug:
            print("parser construction finished")
        tree = parser.parse_class_body_declaration()
        if self.debug:
            print("parse finished")
        return self.parse_tree(tree)

        for path, node in tree:
            if isinstance(node, Tree.LocalVariableDeclaration) or isinstance(node, Tree.VariableDeclaration):
                for declarator in node.declarators:
                    class_object_pair.setdefault(
                        node.type.name, []).append(declarator.name)
                class_method_dic[node.type.name] = []
            elif isinstance(node, Tree.ReferenceType):
                if node.name not in class_method_dic.keys():
                    class_method_dic[node.name] = []
            elif isinstance(node, Tree.MethodInvocation) and node.qualifier is not None:
                if len(class_object_pair) > 0:
                    for class_object_pair_value in class_object_pair.values():
                        if node.qualifier in class_object_pair_value:
                            class_method_dic.setdefault(list(class_object_pair.keys())[
                                list(class_object_pair.values()).index(
                                    class_object_pair_value)], []).append(
                                node.member)
                        else:
                            class_method_dic.setdefault(
                                node.qualifier, []).append(node.member)
                else:
                    class_method_dic.setdefault(
                        node.qualifier, []).append(node.member)
                if node.selectors is not None:
                    for selector in node.selectors:
                        class_method_dic.setdefault(node.qualifier + '.' + node.member, []).append(
                            selector.member)
    
    def parse_code_block_into_expression(self, code_block):
        if self.debug:
            print("parse_code_block_into_expression called")
        code_block = "public void main(){" + code_block + "}"
        return self.parse_code_block_into_body_declaration(code_block)
    
    def parse_code_block_into_compilation_unit(self, code_block):
        class_object_pairs = []
        class_method_dics = []
        class_fields = []

        tokens = javalang.tokenizer.tokenize(code_block)
        parser = javalang.parser.Parser(tokens)
        tree = parser.parse()
        # tree = javalang.parse.parse(code_block)
        class_trees = tree.types

        for class_tree in class_trees:
            tmp_pair, tmp_fields, tmp_dic = self.parse_tree(class_tree)
            class_object_pairs.append(tmp_pair)
            class_method_dics.append(tmp_dic)
            class_fields.append(tmp_fields)
        return class_object_pairs, class_fields, class_method_dics
    
    def parse_tree(self, tree):
        if self.debug:
            print("parse_tree called")
        class_object_pair = {}
        class_method_dic = {}
        class_extends_implements = []
        class_fields = {}

        # cnt = 0
        for path, node in tree:
            # print(cnt)
            # cnt += 1
            if isinstance(node, Tree.ClassDeclaration):
                if node.extends:
                    if isinstance(node.extends, list):
                        class_extends_implements.extend([item.name for item in node.extends])
                    else:
                        class_extends_implements.append(node.extends.name)
                if node.implements:
                    if isinstance(node.implements, list):
                        class_extends_implements.extend([item.name for item in node.implements])
                    else:
                        class_extends_implements.append(node.implements.name)
                for father in class_extends_implements:
                    class_method_dic[father] = []
            elif isinstance(node, Tree.MethodDeclaration):
                if node.annotations:
                    for annotation in node.annotations:
                        if annotation.name == 'Override':
                            for father in class_extends_implements:
                                class_method_dic[father].append(node.name)
            elif isinstance(node, Tree.SuperMethodInvocation):
                for father in class_extends_implements:
                    class_method_dic[father].append(node.member)
            elif isinstance(node, Tree.FieldDeclaration):
                for declarator in node.declarators:
                    class_fields[declarator.name] = node.type.name
            elif isinstance(node, Tree.ClassCreator):
                class_method_dic[node.type.name] = []
            elif isinstance(node, Tree.LocalVariableDeclaration) or isinstance(node, Tree.VariableDeclaration):
                for declarator in node.declarators:
                    class_object_pair.setdefault(
                        node.type.name, []).append(declarator.name)
                class_method_dic[node.type.name] = []
            elif isinstance(node, Tree.ReferenceType):
                if node.name not in class_method_dic:
                    class_method_dic[node.name] = []
            elif isinstance(node, Tree.MethodInvocation) and node.qualifier is not None:
                if len(class_object_pair) > 0:
                    for class_object_pair_value in class_object_pair.values():
                        if node.qualifier in class_object_pair_value:
                            class_method_dic.setdefault(list(class_object_pair.keys())[
                                list(class_object_pair.values()).index(
                                    class_object_pair_value)], []).append(
                                node.member)
                        else:
                            class_method_dic.setdefault(
                                node.qualifier, []).append(node.member)
                else:
                    class_method_dic.setdefault(
                        node.qualifier, []).append(node.member)
                if node.selectors:
                    # print(node, end="\n\n")
                    for selector in node.selectors:
                        # print(selector)
                        if isinstance(selector, Tree.ArraySelector):
                            continue
                        class_method_dic.setdefault(node.qualifier + '.' + node.member, []).append(
                            selector.member)
        return class_object_pair, class_fields, class_method_dic
    
    def extract_import_sents(self, code):
        imports = set()
        for match in re.finditer(r"import (.*?)[;$]", code, re.M):
            match = match.group(1)
            # imp = match[:match.rfind(".")]
            imports.add(match[:match.rfind(".")])
        return imports

class APIExtractor(object):
    def __init__(self, refer_api_doc):
        self.api_docs = dict()
        with open(refer_api_doc, "r", encoding="utf-8") as inf:
            for line in inf:
                obj = json.loads(line)
                package_name = line[1]
                ci_name = line[2]

                if ci_name not in self.api_docs:
                    self.api_docs[ci_name] = set()
                self.api_docs[ci_name].add(package_name)
        pass

    def match_api(self, class_field, class_method_dic, imports):
        apis = []
        packages = []
        for clss in class_method_dic:
            for method in class_method_dic[clss]:
                if clss.startswith("System"):
                    apis.append(f"{clss}.{method}")
                elif clss in self.api_docs:
                    if imports:
                        for pack in self.api_docs[clss].intersection(imports):
                            apis.append(f"{pack}.{clss}.{method}")
                            packages.append(pack)
                    else:
                        for pack in self.api_docs[clss]:
                            apis.append(f"{pack}.{clss}.{method}")
                            packages.append(pack)
                elif clss in class_field:
                    clss = class_field[clss]
                    if imports:
                        for pack in self.api_docs.get(clss, set()).intersection(imports):
                            apis.append(f"{pack}.{clss}.{method}")
                            packages.append(pack)
                    else:
                        for pack in self.api_docs.get(clss, []):
                            apis.append(f"{pack}.{clss}.{method}")
                            packages.append(pack)
        return apis, packages


def test_a_file(filepath):
    with open(filepath, "r", encoding="utf-8") as inf:
        code = inf.read()
    cp = CodeParser()
    cp.parse_code_block_into_compilation_unit(code)
    class_object_pairs, class_fields, class_method_dics, imports = CodeParser().parse_code(code=text)
    # tree = javalang.parse.parse(code)
    # tokens = javalang.tokenizer.tokenize(code)
    # parser = javalang.parser.Parser(tokens)
    # parser.parse_import_declaration()
    
    # print(parser.parse_import_declaration())
    # for class_tree in tree.types:
    #     for path, node in class_tree:
    #         print(node, end="\n\n")

def test(code):
    cp = CodeParser(debug=True)
    class_object_pairs, class_fields, class_method_dics, imports = cp.parse_code_block_into_expression(code)
    for pair, field, method in zip(class_object_pairs, class_fields, class_method_dics):
        print(pair, field, method, sep="\t")