#   Copyright (c) 2016 CNRS - Centre national de la recherche scientifique.
#   All rights reserved.
#
#   Written by Telmo Menezes <telmo@telmomenezes.com>
#
#   This file is part of GraphBrain.
#
#   GraphBrain is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   GraphBrain is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with GraphBrain.  If not, see <http://www.gnu.org/licenses/>.


from gb.nlp.parser import Parser
from gb.reader.parser_output import ParserOutput
from gb.reader.semantic_tree import Position, Tree


def ignore(token):
    if (len(token.dep) == 0) or (token.dep == 'punct') or (token.word == "'"):
        return True
    return False


def nest(token, parent_elem):
    if token.dep in ['aux', 'auxpass', 'cc', 'agent', 'det', 'advmod', 'amod', 'poss', 'nummod', 'prt', 'neg']:
        return True
    if (token.dep == 'prep') and (not parent_elem.has_pos('VERB')):
        return True
    if parent_elem.has_dep('poss') and token.dep == 'case':
        return True
    return False


def add_to_first(token, parent_elem):
    if token.dep == 'pcomp':
        return True
    if token.dep == 'compound' and parent_elem.has_dep_in(['nsubj', 'pobj']):
        return True
    # if parent_elem.has_dep('poss') and token.dep == 'case':
    #     return True
    return False


class AlphaStage(object):
    def __init__(self):
        self.tree = Tree()

    def process_child_token(self, parent_elem_id, token, root_id, pos):
        # ignore
        if ignore(token):
            return

        parent_elem = self.tree.get(parent_elem_id)

        # nest
        if nest(token, parent_elem):
            child_elem_id = self.process_token(token, pos, root_id)
            self.tree.get(root_id).nest(child_elem_id)
            self.tree.get(root_id).new_layer()
            return

        child_elem_id = self.process_token(token, pos)

        # add to parent's first child
        if add_to_first(token, parent_elem):
            parent_elem.add_to_first_child(child_elem_id, pos)
            return

        # add child
        parent_elem.add_child(child_elem_id)

    def process_token(self, token, pos=None, root_id=None):
        elem = self.tree.create_leaf(token)
        elem.position = pos
        elem_id = elem.id

        if root_id is None:
            root_id = elem_id
        for child_token in token.left_children:
            self.process_child_token(elem_id, child_token, root_id, Position.LEFT)
        for child_token in token.right_children:
            self.process_child_token(elem_id, child_token, root_id, Position.RIGHT)
        self.tree.get(elem_id).apply_layers()
        return elem_id

    def process_sentence(self, sentence):
        self.tree.root_id = self.process_token(sentence.root())
        self.tree.remove_redundant_nesting()
        return ParserOutput(sentence, self.tree)


def transform(sentence):
    alpha = AlphaStage()
    return alpha.process_sentence(sentence)


if __name__ == '__main__':
    test_text = """
    Satellites from NASA and other agencies have been tracking sea ice changes since 1979.
    """

    print('Starting parser...')
    parser = Parser()
    print('Parsing...')
    result = parser.parse_text(test_text)

    print(result)

    for s in result:
        print(s)
        s.print_tree()
        t = transform(s)
        print(t)