class Relation:
    def __init__(self, name: str):
        self.name = name
        self.edges = set()
    def add_edge(self, to_node: str):
        if to_node in self.edges:
            print("Relation.add_edge: Edge already exists")
        self.edges.add(to_node)
        
class Node:
    def __init__(self, name: str):
        self.name = name
        self.concepts = set()
        self.initial_concepts = set()
        self.relations = {}
    
    def add_relation(self, rel_name: str, to_node: str):
        if rel_name not in self.relations.keys():
            self.relations[rel_name] = Relation(rel_name)
        self.relations[rel_name].add_edge(to_node)
        print(f"Node.add_relation: Added relation {rel_name} from {self.name} to {to_node}")


# generates nodes with incremental ids and assigns initial concepts to them
class NewNodeGenerator:
    def __init__(self, suffix="d"):
        self._suffix = suffix
        self._id = 0
    def __call__(self, initial_concepts: set):
        node = Node(f"{self._suffix}{self.id}")
        node.initial_concepts.update(initial_concepts)
        self._id += 1
        return node
    
class Graph:
    def __init__(self, node_suffix="d"):
        self.nodes = {}
        self._node_generator = NewNodeGenerator(node_suffix)

    def add_node(self, initial_concepts: set):
        node = self._node_generator(initial_concepts)
        self.nodes[node.name] = node
        print(f"Graph.add_node: Added node {node.name}")
        return node



    


