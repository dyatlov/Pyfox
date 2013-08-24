import CssParser
from CssParser import Node
import CssTree

import urllib2

import json
from json import JSONEncoder
import xml.dom
import sys
import time



class MyEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Node):
            if o.get_type() == 'template' or o.get_type() == 'combinator':
                return o.get_str_tpl()

        return repr(o)

start_time = time.time()

#response = urllib2.urlopen('http://getbootstrap.com/dist/css/bootstrap.css')
#response = urllib2.urlopen('http://local.wutalent.co.uk/static/styles/launchpad.css')
#response = urllib2.urlopen('http://local.wutalent.co.uk/static/styles/base.css')
#data = response.read()
data = ':nth-child(even) {margin:0}'

print 'style fetching took', time.time() - start_time, "seconds"

start_time = time.time()

result = CssParser.parse(data)

print 'parsing took', time.time() - start_time, "seconds"

start_time = time.time()

tree = CssTree.build_tree(result)

print 'tree building took', time.time() - start_time, "seconds"

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
aNode.setAttribute('class', 'href class')
aNode.setAttribute('id', 'content')

uNode.setAttribute('class', 'open')

#htmlNode.appendChild(bodyNode)
bodyNode.appendChild(pNode)
pNode.appendChild(bNode)
bNode.appendChild(emNode)
bNode.appendChild(uNode)
uNode.appendChild(a2Node)
uNode.appendChild(aNode)

start_time = time.time()

rules = CssTree.find_rules(aNode, tree)

print 'rules search took', time.time() - start_time, "seconds"

print rules