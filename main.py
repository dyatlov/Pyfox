import CssParser
from CssParser import Node

import urllib2

#response = urllib2.urlopen('http://getbootstrap.com/dist/css/bootstrap.css')
#response = urllib2.urlopen('http://local.wutalent.co.uk/static/styles/launchpad.css')
#response = urllib2.urlopen('http://local.wutalent.co.uk/static/styles/base.css')
#data = response.read()
data = 'p span a#id1 {} div span#sp2 a {}'

class ReverseCssItem:
    def add_parent(self, item):
        self.parent = item

    def has_parent(self):
        return self.parent is not None

    def get_parent(self):
        return self.parent

    def count_parents(self):
        if self.parent is not None:
            return 1 + self.parent.count_parents()
        return 1

    def repr_attributes(self):
        data = []
        for attr in self.attributes:
            if len(attr) == 1:
                data = data + [attr[0]]
            else:
                data = data + [attr[0] + '=' + attr[1]]
        return '[' + ']['.join(sorted(data)) + ']'

    def repr_pseudos(self):
        data = []
        for pseudo in self.pseudos:
            if len(pseudo) == 1:
                data = data + [pseudo[0]]
            else:
                data = data + [pseudo[0] + pseudo[1] + ')']
        return ':' + ':'.join(sorted(data))

    def repr_classes(self):
        return '.' + '.'.join(sorted(self.classes))

    def repr_item(self):
        st = self.combinator
        if self.type is not None:
            st = st + self.type
        if self.id is not None:
            st = st + self.id
        if len(self.classes) > 0:
            st = st + self.repr_classes()
        if len(self.attributes) > 0:
            st = st + self.repr_attributes()
        if len(self.pseudos) > 0:
            st = st + self.repr_pseudos()
        return st

    def __repr__(self):
        if self.parent is None:
            return self.repr_item()
        else:
            return self.repr_item() + ' ' + str(self.parent)

    def __init__(self, type, id, classes, attributes, pseudos, combinator):
        self.parent = None
        self.type = type
        self.id = id
        self.classes = classes
        self.attributes = attributes
        self.pseudos = pseudos
        self.combinator = combinator

class CssTraverser:
    def next(self):
        return CssTraverser(self.nextList)

    def filter_by_id(self, id):
        if self.itemList is None or id not in self.itemList['id']:
            self.items = []
            return self
        self.nextList = self.itemList['id'][id]['_parent']
        self.items = self.itemList['id'][id]['values']
        return self

    def filter_by_type(self, type):
        if self.itemList is None or type not in self.itemList['type']:
            self.items = []
            return self
        self.nextList = self.itemList['type'][type]['_parent']
        self.items = self.itemList['type'][type]['values']
        return self

    def filter_by_class(self, cl):
        if self.itemList is None or cl not in self.itemList['class']:
            return CssTraverser([])
        return CssTraverser(self.itemList['class'][cl])

    def filter_by_attr(self, attr):
        if self.itemList is None or attr not in self.itemList['attr']:
            return CssTraverser([])
        return CssTraverser(self.itemList['attr'][attr])

    def get_items(self):
        return self.items

    def __init__(self, itemList):
        self.items = []
        self.itemList = itemList

class ReverseCss:
    def add_item_to_tree(self, item, parentTree):
        if item is None:
            return None

        if item.id is not None:
            if item.id not in parentTree['id']:
                parentTree['id'][item.id] = {'values':[], '_parent': self.init_dict()}
            self.add_item_to_tree(item.get_parent(), parentTree['id'][item.id]['_parent'])
            parentTree['id'][item.id]['values'] += [item]
        if item.type is not None:
            if item.type not in parentTree['type']:
                parentTree['type'][item.type] = {'values':[], '_parent': self.init_dict()}
            self.add_item_to_tree(item.get_parent(), parentTree['type'][item.type]['_parent'])
            parentTree['type'][item.type]['values'] += [item]
        if len(item.classes) > 0:
            for cl in item.classes:
                if cl in md['class']:
                    mtype = md['class'][cl]
                else:
                    mtype = [None, self.init_dict()]
                md['class'][cl] = [items, self.add_item_to_tree(item.get_parent(), mtype)]
        if len(item.attributes) > 0:
            for at in item.attributes:
                if at in md['attr']:
                    mtype = md['attr'][at]
                else:
                    mtype = [None, self.init_dict()]
                md['attr'][at] = [items, self.add_item_to_tree(item.get_parent(), mtype)]

    def add_vector(self, vector_rule, declarations):
        item = None
        for template in vector_rule:
            id = None
            type = None
            classes = []
            attributes = []
            pseudos = []
            for elem in template:
                combinator = ''
                if isinstance(elem, Node):
                    elType = elem.get_type()
                    if elType == 'type':
                        type = elem[0]
                    elif elType == 'class':
                        classes = classes + [elem[0]]
                    elif elType == 'id':
                        id = elem[0]
                    elif elType == 'attr':
                        attributes = attributes + [elem]
                    elif elType == 'pseudo':
                        pseudos = pseudos + [elem]
                else:
                    combinator = elem
            newItem = ReverseCssItem(type, id, classes, attributes, pseudos, combinator)
            if item is not None:
                newItem.add_parent( item )
            item = newItem

        self.add_item_to_tree(item, self.cssDict)
        #print self.cssDict
        #print

    def init_dict(self):
        #d = {'id': {}, 'type': {}, 'class': {}, 'attr': {}}
        d = {'id': {}, 'type': {}}
        return d

    def get_traverser(self):
        return CssTraverser(self.cssDict)

    def __init__(self):
        self.cssDict = self.init_dict()
        pass

result = CssParser.parse(data)
reverseCss = ReverseCss()

for ruleset in result[2]:
    selectors = ruleset[0]
    declarations = ruleset[1]
    for vector in selectors:
        reverseCss.add_vector(vector, declarations)

traverser = reverseCss.get_traverser().filter_by_type('a')
print traverser.get_items()
