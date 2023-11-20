#OUTDATED


class Relation:
    def __init__(self, name):
        self.name = name
        self.edges = set()
    def add_edge(self, from_node, to_node):
        self.edges.add((from_node, to_node))
        
class Node:
    def __init__(self, name, axioms):
        self.name = name
        self.axioms = axioms
    
class Graph:
    def __init__(self):
        self.nodes = {}
        self.relations = {}

    def add_node(self, node):
        self.nodes[node.name] = node

    def add_relation(self, relation_name, from_node, to_node):
        if relation_name not in self.relations.keys():
            self.relations[relation_name].add_edge(from_node,to_node)
        else:
            relation = Relation(relation_name)
            relation.add_edge(from_node,to_node)
            self.relations[relation_name] = relation


