
class Relation:
    def __init__(self, name: str):
        assert isinstance(name, str), "Relation.__init__: name should be a string"
        self.name = name
        self.edges = set()

    def add_edge(self, node_name: str):
        if node_name not in self.edges:
            self.edges.add(node_name)
            return True
        else:
            return False


class Node:
    def __init__(self, name: str, initial_concept):
        self.name = name
        self.concepts = set()
        self.concepts.add(initial_concept)
        self.initial_concept = initial_concept
        self.successor_relations = {}
        self.predecessor_relations = {}

    def add_concept(self, concept):
        if concept not in self.concepts:
            self.concepts.add(concept)
            #print(f"Node.add_concept: Added concept {concept} to node {self.name}")
            return True
        else:
            #print(f"Node.add_concept: Concept {concept} already in node {self.name}")
            return False


class NewNodeGenerator:
    def __init__(self, suffix="d"):
        """
        Initialize a NewNodeGenerator object.

        Args:
            suffix (str): The suffix to be appended to the node names.
        """
        self._suffix = suffix
        self._id = 0

    def __call__(self, initial_concept):
        """
        Generate a new node with an incremental id and assign initial concepts to it.

        Args:
            initial_concepts (set): The set of initial concepts for the node.

        Returns:
            Node: The newly generated node.
        """
        node = Node(f"{self._suffix}_{self._id}", initial_concept)
        self._id += 1
        return node


class Graph:
    def __init__(self, node_suffix="d"):
        """
        Initialize a Graph object.

        Args:
            node_suffix (str): The suffix to be appended to the node names.
        """
        self.nodes = {}
        self._node_generator = NewNodeGenerator(node_suffix)

    def add_node(self, initial_concept):
        """
        Add a new node to the graph.

        Args:
            initial_concepts (set): The set of initial concepts for the node.

        Returns:
            Node: The newly added node.
        """
        node = self._node_generator(initial_concept)
        assert node.name not in self.nodes.keys(), "Graph.add_node: node name should be unique"
        self.nodes[node.name] = node
        #print(f"Graph.add_node: Added node {node.name}")
        return node

    def add_relation(self, rel_name: str, from_node_name: str, to_node_name: str):
        """
        Add a two-way relation between two nodes in the graph.

        Args:
            rel_name (str): The name of the relation.
            from_node (str): The name of the node the relation starts from.
            to_node (str): The name of the node the relation points to.
        """
        assert from_node_name in self.nodes.keys(), "Graph.add_relation: from_node should be in self.nodes.keys()"
        assert to_node_name in self.nodes.keys(), "Graph.add_relation: to_node should be in self.nodes.keys()"

        from_node = self.nodes[from_node_name]
        to_node = self.nodes[to_node_name]

        if rel_name not in from_node.successor_relations.keys():
            from_node.successor_relations[rel_name] = Relation(rel_name)
        if rel_name not in to_node.predecessor_relations.keys():
            to_node.predecessor_relations[rel_name] = Relation(rel_name)

        bool_successor = from_node.successor_relations[rel_name].add_edge(to_node_name)
        bool_predecessor = to_node.predecessor_relations[rel_name].add_edge(from_node_name)
        assert bool_successor == bool_predecessor, "Graph.add_relation: successor and predecessor relations should be added in pairs"

        if bool_successor:
            pass
            #print(f"Graph.add_relation: Added relation {rel_name} from node {from_node_name} to node {to_node_name}")

        return bool_successor




    


