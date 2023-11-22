from collections import defaultdict
from py4j.java_gateway import JavaGateway
from tbox_conversion import get_no_equivalence_tbox, get_tbox
from custom_graph import Node, Graph

# connect to the java gateway of dl4python
gateway = JavaGateway()

# get a parser from OWL files to DL ontologies
parser = gateway.getOWLParser()

# get a formatter to print in nice DL format
formatter = gateway.getSimpleDLFormatter()

elFactory = gateway.getELFactory()



#conceptNames = ontology.getConceptNames()

#############################################################



# applied to every new node
def apply_top_rule(node):
    new_concepts = set()
    # ⊤-rule: Add ⊤ to any individual.
    top = elFactory.getTopConcept()
    if top not in node.axioms:
        bool_concept = node.add_concept(top)
        # bool_initial_concept = node.add_initial_concept(top)
        # assert bool_concept == bool_initial_concept, "top rule: concept and initial concept should be added at the same time"
        assert bool_concept is True, "top rule: already checked if ths concept is in node.concepts and got that it is not."

        new_concepts.add(top)
        return new_concepts
    else:
        
        print(f"⊤-rule: Add ⊤ to any individual. was not applied to {node.name}")
    return new_concepts

# applied to every new concept, also the relative node is passed as argument
# ⊑-rule: If d has C assigned and C ⊑ D ∈ T , then also assign D to d 
def apply_subsumption_rule(node, concept, tbox): #if applied to top rule add new concepts as initial concepts

    assert concept in node.concepts, "apply_subsuption_rule: concept should be in node.concepts"

    new_concepts = set()
    conceptType = concept.getClass().getSimpleName()
    for axiom in tbox:
        if axiom.lhs() == concept and (axiom.rhs() not in node.concepts):

            # don't need to check if axiom.lhs() is in allConcepts, because  it's a concept in the ontology
            bool_concept = node.add_concept(axiom.rhs())

            
            # if bool_concept and (axiom.lhs() in node.initial_concepts): #if applied to top rule add new concepts as initial concepts
            #     bool_initial_concept = node.add_initial_concept(axiom.rhs())
            #     assert bool_initial_concept is True, "subsumption rule: concept and initial concept should be added at the same time"

            assert bool_concept is True, "apply_subsuption_rule: Already checked if ths concept is in node.concepts and got that it is not."
            
            new_concepts.add(axiom.rhs())
            
            
            #go to next axiom
            continue
        #test also with swapped conjuncts if it is a conjunction # TODO not necessary, but may lead to faster termination
        # if conceptType == "ConceptConjunction":
        #     conjuncts = concept.getConjuncts()
        #     left_conjunct = conjuncts[0]
        #     right_conjunct = conjuncts[1]
        #     swapped_conjunction = elFactory.getConjunction(right_conjunct, left_conjunct)
        #     if swapped_conjunction not in allConcepts:
        #         continue

        #     if axiom.lhs() ==  swapped_conjunction and (axiom.rhs() not in node.concepts):
        #         bool_concept = node.add_concept(axiom.rhs())
        #         # if bool_concept and (axiom.lhs() in node.initial_concepts):
        #         #     bool_initial_concept = node.add_initial_concept(axiom.rhs())
        #         #     assert bool_initial_concept is True, "subsumption rule: concept and initial concept should be added at the same time"

        #         assert bool_concept is True, "apply_subsuption_rule: Already checked if ths concept is in node.concepts and got that it is not."
        #         new_concepts.add(axiom.rhs())
                

    
    return new_concepts
                
# applied to every new concept, also the relative node is passed as argument
# ⊓-rule 1: If d has C ⊓ D assigned, assign also C and D to d.
def apply_conjunction_rule1(node, concept):

    assert concept in node.concepts, "apply_conjunction_rule1: concept should be in node.concepts"

    new_concepts = set()
    conceptType = concept.getClass().getSimpleName()
    
    if conceptType == "ConceptConjunction":
        conjuncts = concept.getConjuncts()

        left_conjunct = conjuncts[0]
        right_conjunct = conjuncts[1]

        if left_conjunct not in node.concepts:
            bool_left = node.add_concept(left_conjunct)
            assert bool_left is True, "apply_conjunction_rule1: Already checked if ths concept is in node.concepts and got that it is not."
            new_concepts.add(left_conjunct)
        else:
            print(f"⊓-rule 1: was not applied to {node}")
        if right_conjunct not in node.concepts:
            bool_right =node.add_concept(right_conjunct)
            assert bool_right is True, "apply_conjunction_rule1: Already checked if ths concept is in node.concepts and got that it is not."
            new_concepts.add(left_conjunct)
    else:
        print(f"⊓-rule 1: was not applied to {node}")
        print(f"concept {concept} is not a conjunction")

    return new_concepts

# applied to every new concept, also the relative node is passed as argument
# ⊓-rule 2: If d has C and D assigned, assign also C ⊓ D to d.
def apply_conjunction_rule2(node, concept, allConcepts):

    assert concept in node.concepts, "apply_conjunction_rule2: concept should be in node.concepts"

    conceptType = concept.getClass().getSimpleName()
    new_concepts = set()
    for value in node.concepts:
        # check if the new concept is a conjuction and already has value in its conjuncts
        if conceptType == "ConceptConjunction" and value in concept.getConjuncts():
            continue
        # check if value is a conjuction and already has the new concept in its conjuncts
        if value.getClass().getSimpleName() == "ConceptConjunction" and concept in value.getConjuncts():
            continue
        # check if they are they are the same concept
        if value == concept:
            continue
        

        conjunction = elFactory.getConjunction(concept, value)
        if conjunction not in node.concepts and conjunction in allConcepts:
            bool_conjunction = node.add_concept(conjunction)
            assert bool_conjunction is True, "apply_conjunction_rule2: Already checked if ths concept is in node.concepts and got that it is not."
            new_concepts.add(conjunction)
        else:
            print(f"⊓-rule 2: was not applied to {node}")
        #swapped_conjunction = elFactory.getConjunction(concept, value)
        
        # if (conjunction not in node.concepts) and (swapped_conjunction not in node.concepts):
        #     node.add_concept(conjunction)
        #     new_concepts.add(conjunction)
    return new_concepts


# applied to every new concept, also the relative node is passed as argument
#∃-rule 1: If d has ∃r.C assigned
# if there is some r-successor e of d, with initial concept C assigned, make e the r-successor of d
# Otherwise add a new r-successor e to d and assign C to e as initial concept
def apply_existential_rule1(node: Node, concept, graph: Graph):

    assert concept in node.concepts, "apply_existential_rule1: concept should be in node.concepts"

    new_edges = set()# TODO check if this being as set is needed, or if it can be just one edge
    new_nodes = set()

    conceptType = concept.getClass().getSimpleName()
    if conceptType != "ExistentialRoleRestriction":
        print(f"apply_existential_rule1: was not applied to {node}.")
        print(f"concept {concept} is not an ExistentialRoleRestriction")
        return new_nodes,new_edges
    
    role = concept.role()
    filler = concept.filler()
    if role not in node.relations.keys():
        #node.successor_relations[role] = Relation(role)
        pass
    else:
        # # check if there is already some r-successor e of d, with initial concept C assigned
        # for successor_name in node.successor_relations[role].edges:

        #     if filler == graph[successor_name].initial_concept:

        #         print(f"apply_existential_rule1: was not applied to {node}.")
        #         print("WARNING: shouldn't arrive here, because this rule should be applied only to new nodes/concepts/relations")
                
        #         return new_nodes, new_edges
        pass
    # check if there is some node e in the graph with initial concept C assigned, make e the r-successor of d
    for e_name, e_value in graph.items():
        if filler in e_value.initial_concepts:
            bool_relation = graph.add_relation(role, node.name, e_name)
            if bool_relation:
                new_edges.add((node.name, e_name))
            new_edges.add((node.name, e_name))
            return new_nodes, new_edges

    # Otherwise add a new r-successor e to d and assign C to e as initial concept
    new_node = graph.add_node(initial_concept=filler)
    new_nodes.add(new_node.name)
    
    bool_relation = graph.add_relation(role, node.name, new_node.name)
    assert bool_relation is True, "apply_existential_rule1: should be able to add a relation to a new node"
    new_edges.add((node.name, new_node.name))
    return new_nodes, new_edges


# applied to every new concept/ edge
#∃-rule 2: If d has an r-successor e with concept C assigned, assign ∃r.C to d.
def apply_existential_rule2(node: Node, concept, graph: Graph, allConcepts):

    assert concept in node.concepts, "apply_existential_rule2: concept should be in node.concepts"

    new_concepts = set()


    for relation in node.predecessor_relations:
        for predecessor_name in node.predecessor_relations[relation].edges:
            predecessor = graph[predecessor_name]
            
            # add ∃r.C to the predecessor
            role = elFactory.getRole(relation.name)
            existential = elFactory.getExistentialRoleRestriction(role, concept)

            if existential not in predecessor.concepts and existential in allConcepts:
                bool_concept = predecessor.add_concept(existential)
                assert bool_concept is True, "apply_existential_rule2: Already checked if ths concept is in node.concepts and got that it is not."
                new_concepts.add(existential)
            

    return new_concepts

            





def check_subsumed(C0, D0, tbox, allConcepts=None):

    # Every rule is applied only considering newly generated nodes/concepts/relations
    # That's why rule functions returns newly generated nodes/concepts/relations
    # On each iteration every rule is applied to them, generating new nodes/concepts/relations for the next iteration.
    # This should improve execution time because we don't apply the same rules we have already applied to old nodes/concept/relations, that would not change the graph anyway

    # initialize the graph
    graph = Graph()
    d0 = graph.add_node(initial_concept=C0)

    # initialize the sets of new nodes, new concepts and new edges
    new_nodes = set() # node_name
    new_concepts = set() # tuple of (node_name, concept)
    new_edges = set() # tuple of (node_name, node_name)

    # add the initial node to the queue
    new_nodes.add(d0.name)
    new_concepts.add((d0.name, C0))

    while new_nodes or new_concepts or new_edges:
        next_new_nodes = set()
        next_new_concepts = set()
        next_new_edges = set()




        for new_node_name in new_nodes:
            new_node = graph[new_node_name]
            # ⊤-rule: Add ⊤ to any individual.
            top_rule_results = apply_top_rule(new_node)
            for concept in top_rule_results:
                next_new_concepts.add((new_node_name, concept))
            
        for (new_node_name, concept) in new_concepts:
            new_node = graph[new_node_name]
            # ⊑-rule: If d has C assigned and C ⊑ D ∈ T , then also assign D to d 
            subsumption_rule_results = apply_subsumption_rule(new_node, concept, tbox)
            for new_concept in subsumption_rule_results:
                next_new_concepts.add((new_node_name, new_concept))
            # ⊓-rule 1: If d has C ⊓ D assigned, assign also C and D to d.
            conjunction_rule1_results = apply_conjunction_rule1(new_node, concept)
            for new_concept in conjunction_rule1_results:
                next_new_concepts.add((new_node_name, new_concept))
            # ⊓-rule 2: If d has C and D assigned, assign also C ⊓ D to d.
            conjunction_rule2_results = apply_conjunction_rule2(new_node, concept, allConcepts)
            for new_concept in conjunction_rule2_results:
                next_new_concepts.add((new_node_name, new_concept))

            # The order of the following two rules is important

            #∃-rule 2: If d has an r-successor e with concept C assigned, assign ∃r.C to d.
            existential_rule2_results = apply_existential_rule2(new_node, concept, graph, allConcepts)
            for new_concept in existential_rule2_results:
                next_new_concepts.add((new_node_name, new_concept))


            #∃-rule 1: If d has ∃r.C assigned 
            # if there is some r-successor e of d, with initial concept C assigned, make e the r-successor of d
            # Otherwise add a new r-successor e to d and assign C to e as initial concept

            existential_rule1_results = apply_existential_rule1(new_node, concept, graph)
            for new_node_name in existential_rule1_results[0]:
                next_new_nodes.add(new_node_name)
            for new_edge in existential_rule1_results[1]:
                next_new_edges.add(new_edge)

        for (from_node_name, to_node_name) in new_edges:
            to_node= graph[to_node_name]
            for concept in to_node.concepts:
                # apply ∃-rule 2
                existential_rule2_results = apply_existential_rule2(to_node, concept, graph, allConcepts)
                for new_concept in existential_rule2_results:
                    next_new_concepts.add((to_node_name, new_concept))
        
        new_nodes, new_concepts, new_edges = next_new_nodes, next_new_concepts, next_new_edges

        if D0 in graph[d0.name].concepts:
            return True
    return False



def compute_subsumers_of_class(D0, tbox, allConcepts):
    

    subsumers = []
    conceptNames = ontology.getConceptNames()

    


    # loop through all concept names to compute subsumers for every concept name
    for concept in conceptNames:
        if check_subsumed(concept, D0, tbox, allConcepts):
            subsumers.append(concept)
    return subsumers


if __name__ == "__main__":

    ontology = parser.parseFile("pizza.owl")
    allConcepts = ontology.getSubConcepts()
    
    # compute all subsumers for a given class name
    tbox = get_tbox(ontology)
    tbox = get_no_equivalence_tbox(tbox)
    #The reasoner should be able to compute all subsumers for a given class name. In particular, I should be able to call it from the command line using:

    # python PROGRAMM_NAME ONTOLOGY_FILE CLASS_NAME

    margheritaConcept = elFactory.getConceptName("Margherita")

    subsumers = compute_subsumers_of_class(margheritaConcept, tbox, allConcepts)

    print("These are the subsumers of Margherita:")
    for subsumer in subsumers:
        print(formatter.format(subsumer))




