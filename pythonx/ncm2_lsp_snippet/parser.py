import re
import os.path

tabstop_pat1 = re.compile(r'^\$(\d+)')
tabstop_pat2 = re.compile(r'^\$\{(\d+)\}')

placeholder_pat = re.compile(r'^\$\{(\d+):(.*?)\}')

var_pat1 = re.compile(r'^\$([_a-zA-Z][_a-zA-Z0-9]*)')
var_pat2 = re.compile(r'^\$\{([_a-zA-Z][_a-zA-Z0-9]*)\}')

choice_pat = re.compile(r'^\$\{(\d+)\|(.*?[^\\])?\|\}')


class Parser:

    def get_elements(self, s, pos, escs=['$', '\\'], loose_escs=['}']):
        elements = []
        while True:
            if len(s) == pos:
                break
            ele, end = self.get_tabstop(s, pos)
            if ele is not None:
                elements.append(['tabstop', ele])
                pos = end
                continue
            ele, end = self.get_placeholder(s, pos)
            if ele is not None:
                elements.append(['placeholder', ele])
                pos = end
                continue
            ele, end = self.get_choice(s, pos)
            if ele is not None:
                elements.append(['choice', ele])
                pos = end
                continue
            ele, end = self.get_variable(s, pos)
            if ele is not None:
                elements += ele
                pos = end
                continue
            ele, end = self.get_text(s, pos, escs, loose_escs)
            if ele is None:
                pos = end
                break
            pos = end
            elements.append(['text', ele])
        if elements == []:
            return None, pos
        return elements, pos

    def get_text(self, s, pos, escs, loose_escs = []):
        s = s[pos:]
        ele = ''
        end = pos
        while len(s):
            esc = s[:2]
            if esc in ['\\'+e for e in escs + loose_escs]:
                ele += s[1]
                end += 2
                s = s[2:]
                continue
             # unexpected unescaped character
            if s[0] in escs:
                break
            end += 1
            ele += s[0]
            s = s[1:]
        if len(ele) == 0:
            return None, pos
        return ele, end

    def get_tabstop(self, s, pos):
        m = tabstop_pat1.search(s[pos:])
        if m:
            return int(m.group(1)), pos + m.end()
        m = tabstop_pat2.search(s[pos:])
        if m:
            return int(m.group(1)), pos + m.end()
        return None, pos

    def get_placeholder(self, s, pos):
        m = placeholder_pat.search(s[pos:])
        if not m:
            return None, pos
        tab = int(m.group(1))
        # NOTE specialcase, placeholder with empty text, not sure whether it is
        # valid placeholder
        if m.group(2) == '':
            return [tab, ["text", ""]], pos + m.end()
        subeles, pos = self.get_elements(s, pos + m.start(2), escs=['$', '}', '\\'], loose_escs = [])
        if pos == len(s) or s[pos] != '}':
            self.invalid_near(s, pos, "expecting '}' character")
        return [tab, subeles], pos + 1

    def get_choice(self, s, pos=0):
        m = choice_pat.search(s[pos:])
        if not m:
            return None, pos
        tab = int(m.group(1))
        # there's no nested opts
        end = pos + m.end()
        opts = []
        # parse opts  "one,two,three"
        opts_txt = m.group(2) or ""
        c_pos = 0
        while True:
            if c_pos == len(opts_txt):
                break
            cho, c_end = self.get_text(opts_txt, c_pos, ['$', '}', '\\', ',', '|'])
            if cho is None:
                self.invalid_near(s, pos + m.start(2) + c_pos,
                                  "get_text failed for choices")
            opts.append(cho)
            c_pos = c_end
            if c_pos == len(opts_txt):
                break
            if opts_txt[c_pos] != ',':
                self.invalid_near(s, pos + m.start(2) +
                                  c_pos, "expecting comma")
            c_pos += 1
            if c_pos == len(opts_txt):
                # FIXME empty choice ?
                opts.append('')
                break
        return opts, end

    def invalid_near(self, s, pos, reason):
        if pos < len(s):
            s = s[:pos] + '>>' + s[pos] + '<<' + s[pos+1:]
        raise Exception("encounter invalid syntax: [%s] %s" % (s, reason))

    def get_variable(self, s, pos):
        # variable: '$' var | '${' var }'
        # FIXME These two format is tooo-complicated and not supported
        # | '${' var ':' any '}'
        # | '${' var '/' regex '/' (format | text)+ '/' options '}'
        m = var_pat1.search(s[pos:])
        if m:
            return [["text", os.path.expandvars(m.group())]], pos + m.end()
        m = var_pat2.search(s[pos:])
        if m:
            return [["text", os.path.expandvars(m.group())]], pos + m.end()
        return None, pos

    def get_ast(self, snippet):
        eles, pos = self.get_elements(snippet, 0)
        if pos != len(snippet):
            self.invalid_near(snippet, pos, "encounter invalid character")
        return eles



# snippet = "hello $123 $HOME fooba"
# snippet = """unshift(${1:newelt})${0}"""
# ast = Parser().get_ast(snippet)
# print(ast)
# 
# 
# def snipmate_escape(txt):
#     txt = txt.replace('$', r'\$')
#     txt = txt.replace('{', r'\{')
#     txt = txt.replace('}', r'\}')
#     txt = txt.replace(':', r'\:')
#     return txt
# 
# def to_snipmate(ast):
#     txt = ''
#     for t, ele in ast:
#         if t == 'text':
#             txt += snipmate_escape(ele)
#         elif t == 'tabstop':
#             txt += "${%s}" % ele
#         elif t == 'placeholder':
#             tab, ph = ele
#             txt += "${%s:%s}" % (tab, to_snipmate(ph))
#     return txt
# 
# print(to_snipmate(ast))
