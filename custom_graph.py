class Relation:
    def __init__(self, name):
        self.name = name
        self.edges = set()
    def add_edge(self, to_node: str):
        if to_node in self.edges:
            print("Relation.add_edge: Edge already exists")
        self.edges.add(to_node)
        
class Node:
    def __init__(self, name):
        self.name = name
        self.concepts = set()
        self.initial_concepts = set()
        self.relations = {}
    def add_relation(self, rel_name, to_node):
        if rel_name not in self.relations.keys():
            self.relations[rel_name] = Relation(rel_name)
        self.relations[rel_name].add_edge(to_node)
        print(f"Node.add_relation: Added relation {rel_name} from {self.name} to {to_node}")
    
class Graph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, node):
        self.nodes[node.name] = node
        print(f"Graph.add_node: Added node {node.name}")

    


