import ply.lex as lex
from ply.lex import TOKEN

import re

tokens = (
    'S',
    'COMMENT',
    'BADCOMMENT',
    'CDO',
    'CDC',
    'INCLUDES',
    'DASHMATCH',
    'STRING',
    'BADSTRING',
    'IDENT',
    'HASH',
    'IMPORTSYM',
    'PAGESYM',
    'MEDIASYM',
    'CHARSETSYM',
    'IMPORTANTSYM',
    'EMS',
    'EXS',
    'LENGTH',
    'ANGLE',
    'TIME',
    'FREQ',
    'PERCENTAGE',
    'NUMBER',
    'URI',
    'BADURI',
    'FUNCTION',
    'EXCLUDES'
)

literals = ';:{}/,-+~[].<>*@)=!'

nl = r'(\n|\r\n|\r|\f)'
th = r'[0-9a-f]'
s = r'([ \t\r\n\f]+)'
w = r'('+s+r'?)'
tnonascii = r'([\240-\377])'
tunicode = r'(\\' + th + r'{1,6}(\r\n|[ \t\r\n\f])?)'
tescape = r'(' + tunicode + r'(|\\[^\r\n\f0-9a-f])' + r')'
nmstart	= r'([_a-z]|'+tnonascii+r'|'+tescape+r')'
nmchar = r'([_a-z0-9-]|'+tnonascii+r'|'+tescape+r')'
string1 = r'(\"([^\n\r\f\\"]|\\'+nl+r'|'+tescape+r')*\")'
string2 = r'(\'([^\n\r\f\\\']|\\'+nl+r'|'+tescape+r')*\')'
string = r'('+string1+r'|'+string2+r')'
badstring1 = r'(\"([^\n\r\f\\"]|\\'+nl+r'|'+tescape+r')*\\?$)'
badstring2 = r'(\'([^\n\r\f\\\']|\\'+nl+r'|'+tescape+r')*\\?$)'
badstring = r'('+badstring1+r'|'+badstring2+r')'
badcomment1 = r'(/\*[^*]*\*+([^/*][^*]*\*+)*$)'
badcomment2 = r'(/\*[^*]*(\*+[^/*][^*]*)*$)'
badcomment = r'('+badcomment1+r'|'+badcomment2+r')'
url = r'(([!#$%&*-~]|'+tnonascii+r'|'+tescape+r')*)'
baduri1 = r'(url\('+w+r'([!#$%&*-\[\]-~]|'+tnonascii+r'|'+tescape+r')*{w})'
baduri2 = r'(url\('+w+string+w+r'$)'
baduri3 = r'(url\('+w+badstring+r')'
baduri = r'('+baduri1+r'|'+baduri2+r'|'+baduri3+r')'
comment = r'(/\*[^*]*\*+([^/*][^*]*\*+)*/)'
ident = r'(-?'+nmstart+nmchar+r'*)'
name = r'('+nmchar+r'+)'
num = r'([0-9]*\.?[0-9]+)'

A = r'(a|\\0{0,4}(41|61)(\r\n|[ \t\r\n\f])?)'
C = r'(c|\\0{0,4}(43|63)(\r\n|[ \t\r\n\f])?)'
D = r'(d|\\0{0,4}(44|64)(\r\n|[ \t\r\n\f])?)'
E = r'(e|\\0{0,4}(45|65)(\r\n|[ \t\r\n\f])?)'
G = r'(g|\\0{0,4}(47|67)(\r\n|[ \t\r\n\f])?|\\g)'
H = r'(h|\\0{0,4}(48|68)(\r\n|[ \t\r\n\f])?|\\h)'
I = r'(i|\\0{0,4}(49|69)(\r\n|[ \t\r\n\f])?|\\i)'
K = r'(k|\\0{0,4}(4b|6b)(\r\n|[ \t\r\n\f])?|\\k)'
L = r'(l|\\0{0,4}(4c|6c)(\r\n|[ \t\r\n\f])?|\\l)'
M = r'(m|\\0{0,4}(4d|6d)(\r\n|[ \t\r\n\f])?|\\m)'
N = r'(n|\\0{0,4}(4e|6e)(\r\n|[ \t\r\n\f])?|\\n)'
O = r'(o|\\0{0,4}(4f|6f)(\r\n|[ \t\r\n\f])?|\\o)'
P = r'(p|\\0{0,4}(50|70)(\r\n|[ \t\r\n\f])?|\\p)'
R = r'(r|\\0{0,4}(52|72)(\r\n|[ \t\r\n\f])?|\\r)'
S = r'(s|\\0{0,4}(53|73)(\r\n|[ \t\r\n\f])?|\\s)'
T = r'(t|\\0{0,4}(54|74)(\r\n|[ \t\r\n\f])?|\\t)'
U = r'(u|\\0{0,4}(55|75)(\r\n|[ \t\r\n\f])?|\\u)'
X = r'(x|\\0{0,4}(58|78)(\r\n|[ \t\r\n\f])?|\\x)'
Z = r'(z|\\0{0,4}(5a|7a)(\r\n|[ \t\r\n\f])?|\\z)'

@TOKEN(comment)
def t_COMMENT(t):
    t.lexer.lineno += t.value.count('\n')
    pass

t_BADCOMMENT = badcomment

t_CDO = r'<\!--'
t_CDC = r'-->'
t_INCLUDES = r'~='
t_EXCLUDES = r'\^='
t_DASHMATCH = r'\|='

t_STRING = string
t_BADSTRING = badstring

t_IDENT = ident
t_HASH = '\#' + name

t_IMPORTSYM = '@'+I+M+P+O+R+T
t_PAGESYM = '@'+P+A+G+E
t_MEDIASYM = '@'+M+E+D+I+A
t_CHARSETSYM = '@charset '
t_IMPORTANTSYM = '!'+r'('+w+'r|'+comment+r')*'+I+M+P+O+R+T+A+N+T

#t_DIMENSION = num+ident

t_EMS = num+E+M
t_EXS = num+E+X

t_LENGTH = r'('+num+P+X+r'|'+num+C+M+r'|'+num+M+M+r'|'+num+I+N+r'|'+num+P+T+r'|'+num+P+C+r')'

t_ANGLE = r'('+num+D+E+G+r'|'+num+R+A+D+r'|'+num+G+R+A+D+r')'

t_TIME = r'('+num+M+S+r'|'+num+S+r')'

t_FREQ = r'('+num+H+Z+r'|'+num+K+H+Z+r')'

t_PERCENTAGE = num+'%'

t_NUMBER = num

t_URI = r'(url\('+w+string+w+r'\)|url\('+w+url+w+r'\))'
t_BADURI = baduri

t_FUNCTION = ident + r'\('

def t_S(t):
    r'([ \t\r\n\f])'
    if t.value == '\n':
        t.lexer.lineno += 1
    return t

def t_error(t):
    print "Illegal character '%s', line: %s" % (t.value[0], t.lexer.lineno)
    t.lexer.skip(1)

lex.lex(reflags=re.IGNORECASE)
