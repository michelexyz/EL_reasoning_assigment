from collections import defaultdict
from py4j.java_gateway import JavaGateway
from tbox_conversion import get_no_equivalence_tbox
from custom_graph import Relation, Node, Graph

# connect to the java gateway of dl4python
gateway = JavaGateway()

# get a parser from OWL files to DL ontologies
parser = gateway.getOWLParser()

# get a formatter to print in nice DL format
formatter = gateway.getSimpleDLFormatter()

elFactory = gateway.getELFactory()

# load an ontology from a file
ontology = parser.parseFile("pizza.owl")



# get all concepts occurring in the ontology
allConcepts = ontology.getSubConcepts()

conceptNames = ontology.getConceptNames()

#############################################################



# applied to every new node
def apply_top_rule(node):
    # ⊤-rule: Add ⊤ to any individual.
    top = elFactory.getTopConcept()
    if top not in node.axioms:
        node.concepts.add(top)
        node.initial_concepts.add(top)
        changed = True
    else:
        changed = False
        print(f"⊤-rule: Add ⊤ to any individual. was not applied to {node}")
    return changed

# applied to every new concept/node
# ⊑-rule: If d has C assigned and C ⊑ D ∈ T , then also assign D to d 
def apply_subsumption_rule(node, concept, tbox): #if applied to top rule add new concepts as initial concepts
    new_concepts = set()
    conceptType = concept.getClass().getSimpleName()
    for axiom in tbox:
        if axiom.lhs() == concept and (axiom.rhs() not in node.concepts):
            node.concepts.add(axiom.rhs())
            new_concepts.add(axiom.rhs())
            #go to next axiom
            continue
        #test also with swapped conjuncts if it is a conjunction
        if conceptType == "ConceptConjunction":
            conjuncts = concept.getConjuncts()
            left_conjunct = conjuncts[0]
            right_conjunct = conjuncts[1]
            swapped_conjunction = elFactory.getConjunction(right_conjunct, left_conjunct)
            if axiom.lhs() ==  swapped_conjunction and (axiom.rhs() not in node.concepts):
                node.concepts.add(axiom.rhs())
                new_concepts.add(axiom.rhs())
    
    return new_concepts
                
# applied to every new concept/node
# ⊓-rule 1: If d has C ⊓ D assigned, assign also C and D to d.
def apply_conjunction_rule1(node, concept):
    new_concepts = set()
    conceptType = concept.getClass().getSimpleName()
    
    if conceptType == "ConceptConjunction":
        conjuncts = concept.getConjuncts()

        left_conjunct = conjuncts[0]
        right_conjunct = conjuncts[1]

        if left_conjunct not in node.concepts:
            node.concepts.add(left_conjunct)
            new_concepts.add(left_conjunct)
        else:
            print(f"⊓-rule 1: was not applied to {node}")
        if right_conjunct not in node.concepts:
            node.concepts.add(right_conjunct)
            new_concepts.add(left_conjunct)
    else:
        print(f"⊓-rule 1: was not applied to {node}")
        print(f"concept {concept} is not a conjunction")

    return new_concepts

# applied to every new concept/node
# ⊓-rule 2: If d has C and D assigned, assign also C ⊓ D to d.
def apply_conjunction_rule2(node, concept):
    conceptType = concept.getClass().getSimpleName()
    new_concepts = set()
    for value in node.concepts:
        # check if the new concept is a conjuction and already has value in its conjuncts
        if conceptType == "ConceptConjunction" and value in concept.getConjuncts():
            continue
        # check if value is a conjuction and already has the new concept in its conjuncts
        if value.getClass().getSimpleName() == "ConceptConjunction" and concept in value.getConjuncts():
            continue


        conjunction = elFactory.getConjunction(value, concept)
        swapped_conjunction = elFactory.getConjunction(concept, value)
        
        if (conjunction not in node.concepts) and (swapped_conjunction not in node.concepts):
            node.concepts.add(conjunction)
            new_concepts.add(conjunction)
    return new_concepts


# applied to every new concept/node
#∃-rule 1: If d has ∃r.C assigned
# if there is some r-successor e of d, with initial concept C assigned, make e the r-successor of d
# Otherwise add a new r-successor e to d and assign C to e as initial concept
def apply_existential_rule1(node, concept, graph):

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
        node.relations[role] = Relation(role)
    else:
        # check if there is already some r-successor e of d, with initial concept C assigned
        for successor_name in node.relations[role].edges:

            if filler in graph[successor_name].initial_concepts:

                print(f"apply_existential_rule1: was not applied to {node}.")
                print("WARNING: shouldn't arrive here, because this rule should be applied only to new nodes/concepts/relations")
                
                return new_nodes, new_edges
    # check if there is some node e in the graph with initial concept C assigned, make e the r-successor of d
    for e_name, node in graph.items():
        if filler in node.initial_concepts:
            node.add_relation(role, e_name)
            new_edges.add((node.name, e_name))
            return new_nodes, new_edges

    # Otherwise add a new r-successor e to d and assign C to e as initial concept
    new_node = graph.add_node(initial_concepts={filler})
    new_nodes.add(new_node.name)
    
    node.add_relation(role, new_node.name)
    new_edges.add((node.name, new_node.name))
    return new_nodes, new_edges

def apply_existential_rule2(node, concept, graph):
    #TODO
    pass

def check_subsumed(C0, D0, tbox):

    # Every rule is applied only considering newly generated nodes/concepts/relations
    # That's why rule functions returns newly generated nodes/concepts/relations
    # On each iteration every rule is applied to them, generating new nodes/concepts/relations for the next iteration.
    # This should improve execution time because we don't apply the same rules we have already applied to old nodes/concept/relations, that would not change the graph anyway
    #TODO
    pass

def compute_subsumers_of_class(D0, ontology):
    # compute all subsumers for a given class name
    tbox = ontology.tbox() # tbox = get_tbox(ontology)
    tbox = get_no_equivalence_tbox(tbox)

    subsumers = []
    conceptNames = ontology.getConceptNames()

    # loop through all concept names to compute subsumers for every concept name
    for concept in conceptNames:
        if check_subsumed(concept, D0, tbox):
            subsumers.append(concept)
    return subsumers


if __name__ == "__main__":

    #for c in allConcepts:
    #    print(formatter.format(c))

    #for c_n in conceptNames:
    #    print(formatter.format(c_n))
    
    # create a list of conjuctions for test purposes
    conjunctions = []
    conceptA = elFactory.getConceptName("A")
    conceptB = elFactory.getConceptName("B")
    conjunctions.append(elFactory.getConjunction(conceptA, conceptB))
    conceptC = elFactory.getConceptName("C")
    conceptD = elFactory.getConceptName("D")
    conjunctions.append(elFactory.getConjunction(conceptC, conceptD))

    test_conjunction1 = elFactory.getConjunction(conceptB, conceptA)
    swapped_conjunction = elFactory.getConjunction(conceptA, conceptB)

    if test_conjunction1 in conjunctions:
        print(f"test_conjunction1 {formatter.format(test_conjunction1)} is in conjunctions")
    
    if swapped_conjunction in conjunctions:
        print(f"test_conjunction2 {formatter.format(swapped_conjunction)} is in conjunctions")
