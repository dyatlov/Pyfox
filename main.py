import CssParser
from CssParser import Node

import urllib2
import collections
import json
from json import JSONEncoder
import xml.dom
import re

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

        tType = t[0].get_type()
        if tType == 'class':
            tp = '.' + tp

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

def find_rules2(type, node, tree, nodeLevel, treeLevel):
    rules = []
    if type in tree:
        for idx in tree[type]['__values']:
            subTree = tree[type]['__values'][idx]
            if subTree['__tpl'].match_node(node):
                if '__rules' in subTree:
                    print '!-- found rule: ', subTree['__rules'], ' ---'
                    rules += [ subTree['__rules'] ]
                else:
                    print '--- going deeper.. ---'
                    rules += find_rules(node.parentNode, subTree, nodeLevel+1, treeLevel+1)
    return rules

def find_rules(node, tree, nodeLevel = 0, treeLevel = 0):
    rules = []
    # check finished rules
    if node is None:
        return []

    clName = ''
    if node.hasAttribute('class'):
        clName = node.getAttribute('class')
    print node.tagName, clName

    if tree is None:
        return []

    if node.hasAttribute('id'):
        print '--- skipping intermediate rules ---'
        rules += find_rules2(type, node, tree, nodeLevel, treeLevel)

    if node.hasAttribute('class'):
        for cl in re.split('[ \t\r\n\f]+', node.getAttribute('class').lower()):
            pcl = '.' + cl
            rules += find_rules2(pcl, node, tree, nodeLevel, treeLevel)

    type = node.tagName.lower()
    rules += find_rules2(type, node, tree, nodeLevel, treeLevel)

    # we need this to skip intermediate nodes
    if treeLevel > 0:
        print '--- skipping intermediate rules ---'
        rules += find_rules(node.parentNode, tree, nodeLevel + 1, treeLevel)
    else:
        print '--- skipping dipping because tree level is 0 ---'

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
data = 'p .href {border:1px solid red} #content {margin:0} p b a.red {color:red} b em.Blue.href2 a {color:blue} i b a, u a {color:green}'

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
aNode = doc.createElement('A');
a2Node = doc.createElement('a');

emNode.setAttribute('class', 'Blue hRef')
aNode.setAttribute('class', 'href')

htmlNode.appendChild(bodyNode)
bodyNode.appendChild(pNode)
pNode.appendChild(bNode)
bNode.appendChild(a2Node)
bNode.appendChild(emNode)
emNode.appendChild(aNode)

#print json.dumps(tree, indent = 4, cls=MyEncoder)

rules = find_rules(aNode, tree)
print rules