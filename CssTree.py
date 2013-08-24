from collections import defaultdict
from CssParser import Node
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
        return defaultdict(CssTree)

def add_to_tree(tree, vector, rules):
    dest = tree
    parent = dest

    for t in vector[::-1]:
        tix = t[0];
        # sort template parts for effective searching in order: id, class, tag, attr
        for el in t:
            if isinstance(el, Node):
                if el.get_type_int() < tix.get_type_int():
                    tix = el

        if isinstance(tix, Node):
            tp = tix[0]
            tType = tix.get_type()
            if tType == 'class':
                tp = '.' + tp
            elif tType == 'attr':
                tp = '[' + tp + ']'
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
            if isinstance(subTree['__tpl'], Node) and subTree['__tpl'].match_node(node):
                if '__rules' in subTree:
                    rules += [ subTree['__rules'] ]
                rules += find_rules(node.parentNode, subTree, nodeLevel+1, treeLevel+1, prevNode = node)
    return rules

def find_rules(node, tree, nodeLevel = 0, treeLevel = 0,
               enable_child_selector = True, enable_adjacent_selector = True,
               enable_general_selector = True, enable_parent_skip = True, prevNode = None):
    rules = []
    # check finished rules
    if node is None:
        return []

    clName = ''
    if node.hasAttribute('class'):
        clName = node.getAttribute('class')

    if enable_general_selector and '~' in tree:
        for idx in tree['~']['__values']:
            if prevNode is not None:
                sibling = prevNode.previousSibling
                while sibling is not None:
                    rules += find_rules(sibling, tree['~']['__values'][idx], nodeLevel, treeLevel - 1, prevNode = prevNode)
                    sibling = sibling.previousSibling
        enable_general_selector = False

    if enable_adjacent_selector and '+' in tree:
        for idx in tree['+']['__values']:
            if prevNode is not None and prevNode.previousSibling is not None:
                rules += find_rules(prevNode.previousSibling, tree['+']['__values'][idx], nodeLevel, treeLevel - 1, prevNode = prevNode)
            enable_adjacent_selector = False

    if enable_child_selector and '>' in tree:
        for idx in tree['>']['__values']:
            rules += find_rules(node, tree['>']['__values'][idx], nodeLevel, treeLevel + 1, enable_parent_skip = False, prevNode = prevNode)
        # we can't use childs for parent nodes
        enable_child_selector = False

    if node.hasAttribute('id'):
        rules += find_rules2('#' + node.getAttribute('id'), node, tree, nodeLevel, treeLevel)

    if node.hasAttribute('class'):
        for cl in re.split('[ \t\r\n\f]+', node.getAttribute('class').lower()):
            pcl = '.' + cl
            rules += find_rules2(pcl, node, tree, nodeLevel, treeLevel)

    type = node.tagName.lower()
    rules += find_rules2(type, node, tree, nodeLevel, treeLevel)

    rules += find_rules2('*', node, tree, nodeLevel, treeLevel)

    if node.attributes.length:
        for atName, atValue in node.attributes.items():
            at = '[' + atName + ']'
            rules += find_rules2(at, node, tree, nodeLevel, treeLevel)

    # we need this to skip intermediate nodes
    if treeLevel > 0:
        if enable_parent_skip:
            rules += find_rules(node.parentNode, tree, nodeLevel + 1, treeLevel, enable_child_selector, enable_adjacent_selector, enable_general_selector, prevNode = prevNode)

    return rules