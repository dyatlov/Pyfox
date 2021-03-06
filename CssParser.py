import ply.yacc as yacc
from CssLexer import tokens

class Node:
    def parts_str(self):
        st = []
        for part in self.parts:
            st.append( str( part ) )
        return "\n".join(st)

    def __repr__(self):
        return self.type + ":\n\t" + self.parts_str().replace("\n", "\n\t")

    def add_parts(self, parts):
        parts = self.normalize(parts)
        self.parts = self.parts + parts
        return self

    def __getitem__(self, n):
        return self.parts[n]

    def __len__(self):
        return len(self.parts)

    def get_type(self):
        return self.type

    def get_type_int(self):
        return self.type_int

    def get_str_tpl(self):
        st = ''
        for t in self.parts:
            if isinstance(t, Node):
                if t.get_type() == 'class':
                    st += '.'
                if t.get_type() == 'pseudo':
                    st += ':'
                st += t[0]
            else:
                st = t
        return st

    def match_node(self, node):
        '''for templates'''
        for t in self.parts:
            tp = t.get_type()
            if tp == 'type':
                if node.tagName.lower() != t[0]:
                    return False
            elif tp == 'class':
                if node.hasAttribute('class'):
                    if (' ' + node.getAttribute('class').lower() + ' ').find(' ' + t[0] + ' ') == -1:
                        return False
                else:
                    return False
            elif tp == 'id':
                if not node.hasAttribute('id') or '#'+node.getAttribute('id') != t[0]:
                    return False
            elif tp == 'attr':
                if not node.hasAttribute(t[0]):
                    return False
                if len(t) == 1:
                    return True
                destVal = node.getAttribute(t[0]).lower()
                oper = t[1]
                sourceVal = t[2]
                if oper == '=':
                    if destVal != sourceVal:
                        return False
                elif oper == '|=':
                    if destVal != sourceVal and  destVal.find(sourceVal + '-') != 0:
                        return False
                elif oper == '~=':
                    if len(sourceVal) == 0:
                        return False
                    if sourceVal.find(' ') != -1:
                        return False
                    if (' ' + destVal + ' ').find(' ' + sourceVal + ' ') == -1:
                        return False
                elif oper == '^=':
                    if len(sourceVal) == 0:
                        return False
                    if destVal.find(sourceVal) == -1:
                        return False
                elif oper == '$=':
                    if len(sourceVal) == 0:
                        return False
                    if destVal.rfind(sourceVal, -len(sourceVal)) == -1:
                        return False
                elif oper == '*=':
                    if len(sourceVal) == 0:
                        return False
                    if destVal.rfind(sourceVal) == -1:
                        return False
                else:
                    return False
            elif tp == 'universal':
                pass # it always match
            elif tp == 'pseudo':
                pseudo = t[0]
                if pseudo == 'first-child':
                    if node.previousSibling is not None:
                        return False
                elif pseudo == 'root':
                    if node.parentNode is not None:
                        return False
                elif pseudo == 'nth-child(':
                    if isinstance(t[1], Node):
                        pass
                    elif t[1] == 'even':
                        pass
                else:
                    return False
            else:
                return False
        return True

    def normalize(self, parts):
        for k,p in enumerate(parts):
            if isinstance(p, list):
                parts[k] = p.lower()
        return parts

    def __init__(self, type, parts):
        self.type = type
        parts = self.normalize(parts)
        self.parts = parts
        self.type_int = 0
        if type == 'type':
            self.type_int = -1
        elif type == 'class':
            self.type_int = -2
        elif type == 'id':
            self.type_int = -3
        elif type == 'universal':
            self.type_int = -100 # should be first
        elif type == 'pseudo':
            self.type_int = 100 # should be last

bodyNode = Node('body', [])

def p_stylesheet(p):
    '''stylesheet : charset comments importBlock body'''
    p[0] = Node('stylesheet', [ p[1], p[3], p[4] ])

def p_charset(p):
    '''charset :
               | CHARSETSYM STRING \';\''''
    if len(p) == 1:
        p[0] = Node('charset', [])
    else:
        p[0] = Node('charset', p[2])

def p_comments(p):
    '''comments :
                | comments S
                | comments CDO
                | comments CDC'''

def p_importBlock(p):
    '''importBlock :
                   | importBlock import subcomments'''
    if len(p) == 1:
        p[0] = Node('importblock', [])
    else:
        p[0] = p[1].add_parts([ p[2] ])

def p_body_other(p):
    '''body :
            | body media subcomments
            | body page subcomments'''
    if len(p) == 1:
        p[0] = bodyNode
    else:
        p[0] = bodyNode

def p_body_ruleset(p):
    '''body : body ruleset subcomments'''
    p[0] = bodyNode.add_parts([ p[2] ])

def p_subcomments(p):
    '''subcomments :
                   | subcomments CDO spaces
                   | subcomments CDC spaces'''

def p_import(p):
    '''import : IMPORTSYM spaces STRING spaces mediaList \';\' spaces
              | IMPORTSYM spaces URI spaces mediaList \';\' spaces
              | IMPORTSYM spaces STRING spaces \';\' spaces
              | IMPORTSYM spaces URI spaces \';\' spaces'''
    if len(p) == 8:
        p[0] = Node('import', [ p[3], p[5] ])
    else:
        p[0] = Node('import', [ p[3] ])

def p_media(p):
    '''media : MEDIASYM spaces mediaList \'{\' spaces rulesets \'}\' spaces'''
    p[0] = Node('media', [ p[3], p[6] ])

def p_rulesets(p):
    '''rulesets :
                | rulesets ruleset'''
    if len(p) == 1:
        p[0] = Node('rulesets', [])
    else:
        p[0] = p[1].add_parts([ p[2] ])

def p_mediaList(p):
    '''mediaList : medium
                 | mediaList \',\' spaces medium'''
    if len(p) == 2:
        p[0] = Node('medialist', [ p[1] ])
    else:
        p[0] = p[1].add_parts([ p[4] ])

def p_medium(p):
    '''medium : IDENT spaces'''
    p[0] = Node('medium', [ p[1] ])

def p_page(p):
    '''page : PAGESYM spaces pseudoPage \'{\' pageDeclarations \'}\' spaces
            | PAGESYM spaces \'{\' pageDeclarations \'}\' spaces'''
    if len(p) == 8:
        p[0] = Node('page', [ p[5], p[3] ])
    else:
        p[0] = Node('page', [ p[4] ])

def p_pageDeclarations(p):
    '''pageDeclarations : spaces
                        | spaces declaration
                        | pageDeclarations \';\' spaces
                        | pageDeclarations \';\' spaces declaration'''
    if len(p) == 2:
        p[0] = Node('pagedeclarations', [])
    else:
        if len(p) == 3:
            p[0] = Node('pagedeclarations', [ p[2] ])
        else:
            if len(p) == 4:
                p[0] = p[1]
            else:
                p[0] = p[1].add_parts([ p[4] ])

def p_pseudoPage(p):
    '''pseudoPage : \':\' IDENT spaces'''
    p[0] = Node('pseudopage', [ p[2] ])

def p_operator(p):
    '''operator : \'/\' spaces
                | \',\' spaces'''
    p[0] = Node('operator', p[1])

def p_combinator(p):
    '''combinator : \'+\' spaces
                  | \'~\' spaces
                  | \'>\' spaces'''
    p[0] = Node('combinator', p[1])

def p_unaryOperator(p):
    '''unaryOperator : \'-\'
                     | \'+\''''
    p[0] = Node('unary', p[1])

def p_property(p):
    '''property : IDENT spaces'''
    p[0] = Node('property', [ p[1] ])

def p_ruleset(p):
    '''ruleset : selectorList \'{\' spaces declarations \'}\' spaces
               | selectorList \'{\' spaces \'}\' spaces'''
    if len(p) > 6:
        p[0] = Node('ruleset', [ p[1], p[4] ])
    else:
        p[0] = Node('ruleset', [])

def p_selectorList(p):
    '''selectorList : complexSelector
                    | universalSelector
                    | selectorList \',\' spaces complexSelector
                    | selectorList \',\' spaces universalSelector'''
    if len(p) == 2:
        p[0] = Node('selectors', [ p[1] ])
    else:
        p[0] = p[1].add_parts([ p[4] ])

def p_complexSelector_v1(p):
    '''complexSelector : compoundSelector
                       | complexSelector combinator compoundSelector'''
    if len(p) == 2:
        if len(p[1]) == 1:
            if p[1][0].get_type() == 'pseudo':
                p[1].add_parts([ Node('universal', ['*']) ])
        p[0] = Node('vector', [ p[1] ])
    else:
        if len(p[3]) == 1:
            if p[3][0].get_type() == 'pseudo':
                p[3].add_parts([ Node('universal', ['*']) ])
        p[0] = p[1].add_parts([ p[2], p[3] ])

def p_complexSelector_v2(p):
    '''complexSelector : complexSelector S compoundSelector
                       | complexSelector S'''
    if len(p) == 3:
        p[0] = p[1]
    else:
        p[0] = p[1].add_parts([ p[3] ])

def p_universalSelector(p):
    '''universalSelector :
                         | \'*\''''
    if len(p) == 1:
        p[0] = Node('universal', [])
    else:
        p[0] = Node('universal', [ p[1] ])

def p_compoundSelector_star(p):
    '''compoundSelector : \'*\' typeSelector
                        | \'*\' simpleSelector'''
    p[0] = Node('template', [ Node('universal', [ p[1] ]), p[2] ])

def p_compoundSelector_default(p):
    '''compoundSelector : typeSelector
                        | simpleSelector
                        | compoundSelector simpleSelector'''
    if len(p) == 2:
        p[0] = Node('template', [ p[1] ])
    else:
        p[0] = p[1].add_parts( [ p[2] ] )

def p_simpleSelector(p):
    '''simpleSelector : attributeSelector
                      | classSelector
                      | idSelector
                      | pseudoClassSelector'''
    p[0] = p[1]

def p_idSelector(p):
    '''idSelector : HASH'''
    p[0] = Node('id', [ p[1] ])

def p_classSelector(p):
    '''classSelector : \'.\' IDENT'''
    p[0] = Node('class', [ p[2] ])

def p_typeSelector(p):
    '''typeSelector : IDENT
                    | \'@\' IDENT'''
    if len(p) == 2:
        p[0] = Node('type', [ p[1] ])
    else:
        p[0] = Node('type', [ p[2], '@' ])

def p_attributeSelector(p):
    '''attributeSelector : \'[\' spaces IDENT spaces \']\'
                         | \'[\' spaces IDENT spaces attribEq spaces attribValue spaces \']\''''
    if len(p) < 7:
        p[0] = Node('attr', [ p[3] ])
    else:
        p[0] = Node('attr', [ p[3], p[5], p[7] ])

def p_attribEq(p):
    '''attribEq : \'=\'
                | INCLUDES
                | EXCLUDES
                | ENDMATCH
                | ANYMATCH
                | DASHMATCH'''
    p[0] = p[1]

def p_attribValue(p):
    '''attribValue : IDENT
                   | STRING'''
    p[0] = p[1]

def p_pseudoClassSelector(p):
    '''pseudoClassSelector : \':\' pseudoBlock'''
    p[0] = p[2]

def p_pseudoBlock(p):
    '''pseudoBlock : IDENT
                   | FUNCTION spaces pseudoBlockFunctionIdent \')\''''
    if len(p) == 2:
        p[0] = Node('pseudo', [ p[1] ])
    else:
        p[0] = Node('pseudo', [ p[1], p[3] ])

def p_pseudoBlockFunctionIdent_num(p):
    '''pseudoBlockFunctionIdent :
                                | selPNum spaces'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = None

def p_pseudoBlockFunctionIdent_gen(p):
    '''pseudoBlockFunctionIdent : IDENT spaces
                                | selPNum IDENT spaces
                                | selPNum IDENT spaces \'-\' spaces NUMBER spaces
                                | selPNum IDENT spaces \'+\' spaces NUMBER spaces'''
    if len(p) == 3:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = Node('pseudo_math', [p[1], 0])
    elif p[4] == '-':
        p[0] = Node('pseudo_math', [p[1], -int(p[6])])
    else:
        p[0] = Node('pseudo_math', [p[1], p[6]])


def p_selPNum(p):
    '''selPNum : NUMBER
               | \'-\' NUMBER
               | \'+\' NUMBER'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[1] == '-':
            p[0] = 0 - int(p[2])
        else:
            p[0] = p[2]

def p_declarations(p):
    '''declarations : declaration
                    | declarations \';\' spaces declaration
                    | declarations \';\' spaces'''
    if len(p) == 2:
        p[0] = Node('declarations', [ p[1] ])
    else:
        if len(p) > 4:
            p[0] = p[1].add_parts( [ p[4] ] )
        else:
            p[0] = p[1]

def p_declaration(p):
    '''declaration : property \':\' spaces expr prio
                   | property \':\' spaces expr'''
    if len(p) > 5:
        p[0] = Node('declaration', [ p[1], p[4], p[5] ])
    else:
        p[0] = Node('declaration', [ p[1], p[4] ])

def p_prio(p):
    '''prio : IMPORTANTSYM spaces'''
    p[0] = Node('prio', [ p[1] ])

def p_expr(p):
    '''expr : term
            | expr operator term
            | expr term'''
    if len(p) > 3:
        p[0] = p[1].add_parts([ p[2], p[3] ])
    else:
        if len(p) > 2:
            p[0] = p[1].add_parts([ p[2] ])
        else:
            p[0] = Node('expression', [ p[1] ])

def p_term_default(p):
    '''term : termNumeral spaces
            | hexcolor
            | function'''
    p[0] = Node('term', [ p[1] ])

def p_term_str(p):
    '''term : STRING spaces'''
    p[0] = Node('term', [ Node('string', [p[1]]) ])

def p_term_ident(p):
    '''term : IDENT spaces'''
    p[0] = Node('term', [ Node('identifier', [p[1]]) ])

def p_term_uri(p):
    '''term : URI spaces'''
    p[0] = Node('term', [ Node('uri', [p[1]]) ])

def p_term_unary(p):
    '''term : unaryOperator termNumeral spaces'''
    p[0] = Node('term', [ p[2], p[1] ])


def p_termNumeral(p):
    '''termNumeral : NUMBER
                   | PERCENTAGE
                   | LENGTH
                   | EMS
                   | EXS
                   | ANGLE
                   | TIME
                   | FREQ'''
    p[0] = Node('numeral', [ p[1] ])

def p_function(p):
    '''function : FUNCTION spaces expr \')\' spaces'''
    p[0] = Node('function', [ p[1], p[3] ])

def p_hexcolor(p):
    '''hexcolor : HASH spaces'''
    p[0] = Node('hexcolor', [ p[1] ])

def p_spaces(p):
    '''spaces :
              | spaces S'''

def p_error(p):
    print 'Syntax error in input!'
    print p

def parse(data):
    return parser.parse(data)

parser = yacc.yacc()