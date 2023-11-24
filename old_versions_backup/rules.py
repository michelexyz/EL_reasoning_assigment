from resources import parser, formatter, elFactory

from custom_graph import Graph, Node, Relation

# applied to every new node
def apply_top_rule(node):
    new_concepts = set()
    # ⊤-rule: Add ⊤ to any individual.
    top = elFactory.getTop()
    if top not in node.concepts:
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
        if (conjunction not in node.concepts) and (conjunction in allConcepts):
            #bool_conjunction = node.add_concept(conjunction)
            #assert bool_conjunction is True, "apply_conjunction_rule2: Already checked if ths concept is in node.concepts and got that it is not."
            new_concepts.add(conjunction)
        # elif conjunction not in allConcepts:
        #     print(f"⊓-rule 2: was not applied to {node.name}")
        #     print(f"concept {conjunction} is not in allConcepts")
            

    for concept in new_concepts:
        node.add_concept(concept) # add concept later to avoid changing the set while iterating over it
        
        
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
    role_name = role.name()
    assert isinstance(role_name, str), "apply_existential_rule1: role name should be a string"
    # check if there is some node e in the graph with initial concept C assigned, make e the r-successor of d
    for e_name, e_value in graph.nodes.items():
        if filler == e_value.initial_concept:
            bool_relation = graph.add_relation(role_name, node.name, e_name)
            if bool_relation:
                new_edges.add((node.name, e_name))
            new_edges.add((node.name, e_name))
            return new_nodes, new_edges

    # Otherwise add a new r-successor e to d and assign C to e as initial concept
    new_node = graph.add_node(initial_concept=filler)
    new_nodes.add(new_node.name)
    
    bool_relation = graph.add_relation(role_name, node.name, new_node.name)
    assert bool_relation is True, "apply_existential_rule1: should be able to add a relation to a new node"
    new_edges.add((node.name, new_node.name))
    return new_nodes, new_edges


# applied to every new concept/ edge
#∃-rule 2: If d has an r-successor e with concept C assigned, assign ∃r.C to d.
def apply_existential_rule2(node: Node, concept, graph: Graph, allConcepts):

    assert concept in node.concepts, "apply_existential_rule2: concept should be in node.concepts"

    new_concepts = set()


    for relation in node.predecessor_relations.values():
        for predecessor_name in relation.edges:
            predecessor = graph.nodes[predecessor_name]
            
            # add ∃r.C to the predecessor
            print("Relation name:", relation.name)
            print("rel type:", type(relation.name))


            role = elFactory.getRole(relation.name)
            existential = elFactory.getExistentialRoleRestriction(role, concept)

            if existential not in predecessor.concepts and existential in allConcepts:
                bool_concept = predecessor.add_concept(existential)
                assert bool_concept is True, "apply_existential_rule2: Already checked if ths concept is in node.concepts and got that it is not."
                new_concepts.add(existential)
            

    return new_concepts