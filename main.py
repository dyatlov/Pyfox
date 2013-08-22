import CssParser
from CssParser import Node

import urllib2
from collections import defaultdict
import json
from json import JSONEncoder
import xml.dom
import re
import sys

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

class CssTree(defaultdict):
    def __init__(self, parent=None):
        self.parent = parent
        defaultdict.__init__(self, lambda: CssTree(self))

def add_to_tree(tree, vector, rules):
    dest = tree
    parent = dest

    for t in vector[::-1]:
        tix = t[0];
        # sort template parts for effective searching in order: id, class, tag, attr
        for el in t:
            if isinstance(el, Node) and el.get_type_int() < tix.get_type_int():
                tix = el

        if isinstance(tix, Node):
            tp = tix[0]
            tType = tix.get_type()
            if tType == 'class':
                tp = '.' + tp
        else:
            tp = tix

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
        if len(ruleset):
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
                    rules += find_rules(node.parentNode, subTree, nodeLevel+1, treeLevel+1, prevNode = node)
    return rules

def find_rules(node, tree, nodeLevel = 0, treeLevel = 0, enable_child_selector = True, enable_adjacent_selector = True, enable_general_selector = True, enable_parent_skip = True, prevNode = None):
    rules = []
    # check finished rules
    if node is None:
        return []

    clName = ''
    if node.hasAttribute('class'):
        clName = node.getAttribute('class')
    print 'node level', str(nodeLevel), 'tree level', str(treeLevel) + ': ', node.tagName, clName

    if tree is None:
        return []

    if enable_general_selector and '~' in tree:
        for idx in tree['~']['__values']:
            print '--- found general combinator (~), current node is ' + node.tagName + ', dipping inside ---'
            if prevNode is not None:
                sibling = prevNode.previousSibling
                while sibling is not None:
                    rules += find_rules(sibling, tree['~']['__values'][idx], nodeLevel, treeLevel, prevNode = prevNode)
                    sibling = sibling.previousSibling
        enable_general_selector = False

    if enable_adjacent_selector and '+' in tree:
        for idx in tree['+']['__values']:
            print '--- found adjacent combinator (+), current node is ' + node.tagName + ', dipping inside ---'
            if prevNode is not None and prevNode.previousSibling is not None:
                rules += find_rules(prevNode.previousSibling, tree['+']['__values'][idx], nodeLevel, treeLevel, prevNode = prevNode)
            enable_adjacent_selector = False

    if enable_child_selector and '>' in tree:
        print '--- found child combinator (>), current node is ' + node.tagName + ', dipping inside ---'
        for idx in tree['>']['__values']:
            rules += find_rules(node, tree['>']['__values'][idx], nodeLevel, treeLevel + 1, enable_parent_skip = False, prevNode = prevNode)
        # we can't use childs for parent nodes
        enable_child_selector = False

    #if node.hasAttribute('id'):
    #    print '--- skipping intermediate rules ---'
    #    rules += find_rules2('#' + node.getAttribute('id'), node, tree, nodeLevel, treeLevel)

    #if node.hasAttribute('class'):
    #    for cl in re.split('[ \t\r\n\f]+', node.getAttribute('class').lower()):
    #        pcl = '.' + cl
    #        rules += find_rules2(pcl, node, tree, nodeLevel, treeLevel)

    type = node.tagName.lower()
    rules += find_rules2(type, node, tree, nodeLevel, treeLevel)

    # we need this to skip intermediate nodes
    if treeLevel > 0:
        if enable_parent_skip:
            print '--- skipping intermediate rules, tree level: ' + str(treeLevel) + ' ---'
            rules += find_rules(node.parentNode, tree, nodeLevel + 1, treeLevel, enable_child_selector, enable_adjacent_selector, enable_general_selector, prevNode = prevNode)
    else:
        print '--- skipping dipping because tree level is 0 ---'

    return rules

class MyEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Node):
            if o.get_type() == 'template' or o.get_type() == 'combinator':
                return o.get_str_tpl()

        return repr(o)

#response = urllib2.urlopen('http://getbootstrap.com/dist/css/bootstrap.css')
#response = urllib2.urlopen('http://local.wutalent.co.uk/static/styles/launchpad.css')
#response = urllib2.urlopen('http://local.wutalent.co.uk/static/styles/base.css')
#data = response.read()
data = '/*p a {margin:0} b > em > a {color:#000}*/ b > em ~ u a {color: #fff}'

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
aNode.setAttribute('id', 'content')

#htmlNode.appendChild(bodyNode)
#bodyNode.appendChild(pNode)
#pNode.appendChild(bNode)
bNode.appendChild(pNode)
bNode.appendChild(emNode)
bNode.appendChild(uNode)
uNode.appendChild(a2Node)
a2Node.appendChild(aNode)

print bNode.toxml()
#print json.dumps(tree, indent = 4, cls=MyEncoder)

rules = find_rules(aNode, tree)
print rules