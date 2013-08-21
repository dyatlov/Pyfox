import CssParser
from CssParser import Node

import urllib2
import collections
import json
from json import JSONEncoder
import xml.dom

class Ruleset:
    def __repr__(self):
        parts = []
        for template in self.vector:
            st = template.get_str_tpl()
            parts += [st]
        return ' '.join( parts )

    def __init__(self, vector, rules):
        self.vector = vector
        self.rules = rules

def CssTree():
    return collections.defaultdict(CssTree)

def add_to_tree(tree, vector, rules):
    dest = tree
    for t in vector[::-1]:
        tp = t[0][0]

        tdest = dest[tp]['__values']

        found = False
        for item in tdest:
            if isinstance(tdest[item]['__tpl'], Node):
                if t.get_str_tpl() == tdest[item]['__tpl'].get_str_tpl():
                    dest = tdest[item]
                    found = True
                    break

        if not found:
            dest = tdest[len(tdest)]

        dest['__tpl'] = t
    dest['__rules'] = Ruleset(vector, rules)

def build_tree(table):
    body = table[2]
    tree = CssTree()
    for ruleset in body:
        for vector in ruleset[0]:
            add_to_tree(tree, vector, ruleset[1])
    return tree

def find_rules(node, tree):
    rules = []
    # check finished rules
    if node is None:
        return []

    if tree is None:
        return []

    if '__rules' in tree:
        rules += [ tree['__rules'] ]
        return rules

    childTree = tree

    type = node.tagName
    if type in tree:
        rules += find_rules(node.parentNode, childTree[type])
    rules += find_rules(node.parentNode, childTree)

    return rules

class MyEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Node) and o.get_type() == 'template':
            return o.get_str_tpl()

        return repr(o)

#response = urllib2.urlopen('http://getbootstrap.com/dist/css/bootstrap.css')
#response = urllib2.urlopen('http://local.wutalent.co.uk/static/styles/launchpad.css')
#response = urllib2.urlopen('http://local.wutalent.co.uk/static/styles/base.css')
#data = response.read()
data = '#content {margin:0} p b a.red {color:red} b em.blue.href a {color:blue} i b a, u a {color:green}'

result = CssParser.parse(data)

tree = build_tree(result)

di = xml.dom.getDOMImplementation()
doc = di.createDocument('','root','')

htmlNode = doc.createElement('html');
bodyNode = doc.createElement('body');
pNode = doc.createElement('p');
bNode = doc.createElement('b');
uNode = doc.createElement('u');
emNode = doc.createElement('em');
aNode = doc.createElement('a');
a2Node = doc.createElement('a');

htmlNode.appendChild(bodyNode)
bodyNode.appendChild(pNode)
pNode.appendChild(bNode)
bNode.appendChild(a2Node)
bNode.appendChild(emNode)
emNode.appendChild(aNode)

print json.dumps(tree, indent = 4, cls=MyEncoder)

rules = find_rules(aNode, tree)
print rules