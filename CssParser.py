import ply.yacc as yacc
from CssLexer import tokens

def p_stylesheet(p):
    '''stylesheet : charset comments importBLock body'''

def p_charset(p):
    '''charset :
               | CHARSETSYM STRING \';\''''

def p_comments(p):
    '''comments :
                | comments S
                | comments CDO
                | comments CDC'''

def p_importBLock(p):
    '''importBLock :
                   | import subcomments'''

def p_body(p):
    '''body :
            | body ruleset subcomments
            | body media subcomments
            | body page subcomments'''

def p_subcomments(p):
    '''subcomments :
                   | subcomments CDO spaces
                   | subcomments CDC spaces'''

def p_import(p):
    '''import : IMPORTSYM spaces STRING spaces mediaList \';\' spaces
              | IMPORTSYM spaces URI spaces mediaList \';\' spaces
              | IMPORTSYM spaces STRING spaces \';\' spaces
              | IMPORTSYM spaces URI spaces \';\' spaces'''

def p_media(p):
    '''media : MEDIASYM spaces mediaList \'{\' spaces rulesets \'}\' spaces'''

def p_rulesets(p):
    '''rulesets :
                | rulesets ruleset'''

def p_mediaList(p):
    '''mediaList : medium
                 | mediaList \',\' spaces medium'''

def p_medium(p):
    '''medium : IDENT spaces'''

def p_page(p):
    '''page : PAGESYM spaces pseudoPage \'{\' pageDeclarations \'}\' spaces
            | PAGESYM spaces \'{\' pageDeclarations \'}\' spaces'''

def p_pageDeclarations(p):
    '''pageDeclarations : spaces declaration
                        | spaces
                        | pageDeclarations \';\' spaces declaration
                        | pageDeclarations \';\' spaces'''

def p_pseudoPage(p):
    '''pseudoPage : \':\' IDENT spaces'''

def p_operator(p):
    '''operator : \'/\' spaces
                | \',\' spaces'''

def p_combinator(p):
    '''combinator : \'+\' spaces
                  | \'>\' spaces'''

def p_unaryOperator(p):
    '''unaryOperator : \'-\'
                     | \'+\''''

def p_property(p):
    '''property : IDENT spaces'''

def p_ruleset(p):
    '''ruleset : selectorList \'{\' spaces declarations \'}\' spaces
               | selectorList \'{\' spaces \'}\' spaces'''

def p_selectorList(p):
    '''selectorList : complexSelector
                    | universalSelector
                    | selectorList \',\' spaces complexSelector
                    | selectorList \',\' spaces universalSelector'''

def p_complexSelector(p):
    '''complexSelector : compoundSelector
                       | complexSelector combinator compoundSelector
                       | complexSelector S compoundSelector
                       | complexSelector S'''

def p_universalSelector(p):
    '''universalSelector :
                         | \'*\''''

def p_compoundSelector(p):
    '''compoundSelector : \'*\' typeSelector
                        | typeSelector
                        | \'*\' simpleSelector
                        | simpleSelector
                        | compoundSelector simpleSelector'''

def p_simpleSelector(p):
    '''simpleSelector : attributeSelector
                      | classSelector
                      | idSelector
                      | pseudoClassSelector'''

def p_idSelector(p):
    '''idSelector : HASH'''

def p_classSelector(p):
    '''classSelector : \'.\' IDENT'''

def p_typeSelector(p):
    '''typeSelector : IDENT
                    | \'@\' IDENT'''

def p_attributeSelector(p):
    '''attributeSelector : \'[\' spaces IDENT spaces \']\'
                         | \'[\' spaces IDENT spaces attribEq spaces attribValue spaces \']\''''

def p_attribEq(p):
    '''attribEq : \'=\'
                | INCLUDES
                | DASHMATCH'''

def p_attribValue(p):
    '''attribValue : IDENT
                   | STRING'''

def p_pseudoClassSelector(p):
    '''pseudoClassSelector : \':\' pseudoBlock'''

def p_pseudoBlock(p):
    '''pseudoBlock : IDENT
                   | FUNCTION spaces pseudoBlockFunctionIdent \')\''''

def p_pseudoBlockFunctionIdent(p):
    '''pseudoBlockFunctionIdent :
                                | IDENT spaces
                                | STRING spaces
                                | NUMBER spaces'''

def p_declarations(p):
    '''declarations : declaration
                    | declarations \';\' spaces declaration
                    | declarations \';\' spaces'''

def p_declaration(p):
    '''declaration : property \':\' spaces expr prio
                   | property \':\' spaces expr'''

def p_prio(p):
    '''prio : IMPORTANTSYM spaces'''

def p_expr(p):
    '''expr : term
            | expr operator term
            | expr term'''

def p_term(p):
    '''term : unaryOperator termNumeral spaces
            | termNumeral spaces
            | STRING spaces
            | IDENT spaces
            | URI spaces
            | hexcolor
            | function'''

def p_termNumeral(p):
    '''termNumeral : NUMBER
                   | PERCENTAGE
                   | LENGTH
                   | EMS
                   | EXS
                   | ANGLE
                   | TIME
                   | FREQ'''

def p_function(p):
    '''function : FUNCTION spaces expr \')\' spaces'''

def p_hexcolor(p):
    '''hexcolor : HASH spaces'''

def p_spaces(p):
    '''spaces :
              | spaces S'''

def p_error(p):
    print 'Syntax error in input!'
    print p

def parse(data):
    parser.parse(data)

parser = yacc.yacc()