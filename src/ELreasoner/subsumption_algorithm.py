from ELreasoner.custom_graph import Node, Graph
from ELreasoner.rules import (apply_top_rule, apply_subsumption_rule, 
                   apply_conjunction_rule1, apply_conjunction_rule2, 
                   apply_existential_rule1, apply_existential_rule2)
from ELreasoner.resources import formatter, elFactory


def check_subsumed(C0, D0s, tbox, allConcepts=None):

    # if C0 in DO:
    #     return True

    # Every rule is applied only considering newly generated nodes/concepts/relations
    # That's why rule functions returns newly generated nodes/concepts/relations
    # On each iteration every rule is applied to them, generating new nodes/concepts/relations for the next iteration.
    # This should improve execution time because we don't apply the same rules we have already applied to old nodes/concept/relations, that would not change the graph anyway

    # initialize the graph
    graph = Graph()
    d0 = graph.add_node(initial_concept=C0)

    # initialize the sets of new nodes, new concepts and new edges
    new_nodes = set() # node_name
    new_concepts = set() # tuple of (node_name, concept) the new concept with its associated node
    new_edges = set() # tuple of (node_name, node_name)

    # add the initial node to the queue
    new_nodes.add(d0.name)
    new_concepts.add((d0.name, C0))
    
    while new_nodes or new_concepts or new_edges:
        next_new_nodes = set()
        next_new_concepts = set()
        next_new_edges = set()

        # for every new node we just need to apply the ⊤-rule
        for node_name in new_nodes:
            new_node = graph.nodes[node_name]
            # ⊤-rule: Add ⊤ to any individual.
            top_rule_results = apply_top_rule(new_node)
            for concept in top_rule_results:
                next_new_concepts.add((node_name, concept))
        
        # for every new concept we need to apply all the rules except the ⊤-rule
        for (node_name, concept) in new_concepts:
            new_node = graph.nodes[node_name]
            # ⊑-rule: If d has C assigned and C ⊑ D ∈ T , then also assign D to d 
            subsumption_rule_results = apply_subsumption_rule(new_node, concept, tbox)
            for new_concept in subsumption_rule_results:
                next_new_concepts.add((node_name, new_concept))
            # ⊓-rule 1: If d has C ⊓ D assigned, assign also C and D to d.
            conjunction_rule1_results = apply_conjunction_rule1(new_node, concept)
            for new_concept in conjunction_rule1_results:
                next_new_concepts.add((node_name, new_concept))
            # ⊓-rule 2: If d has C and D assigned, assign also C ⊓ D to d.
            conjunction_rule2_results = apply_conjunction_rule2(new_node, concept, allConcepts)
            for new_concept in conjunction_rule2_results:
                next_new_concepts.add((node_name, new_concept))

            # The order of the following two rules is important

            #∃-rule 2: If d has an r-successor e with concept C assigned, assign ∃r.C to d.
            existential_rule2_results = apply_existential_rule2(new_node, concept, graph, allConcepts)
            for associated_node_name, new_concept in existential_rule2_results:
                    next_new_concepts.add((associated_node_name, new_concept))


            #∃-rule 1: If d has ∃r.C assigned 
            # if there is some r-successor e of d, with initial concept C assigned, make e the r-successor of d
            # Otherwise add a new r-successor e to d and assign C to e as initial concept
            erule_new_node, erule_new_edge, erule_new_concept = apply_existential_rule1(new_node, concept, graph)
            if erule_new_node is not None:
                assert erule_new_concept is not None, "check_subsumed: new concept should be generated if a new node is generated"
                next_new_nodes.add(erule_new_node)
            if erule_new_edge is not None:
                next_new_edges.add(erule_new_edge)
            if erule_new_concept is not None:
                assert erule_new_node is not None, "check_subsumed: new node should be generated if a new concept is generated"
                next_new_concepts.add((erule_new_node, erule_new_concept))
            

        # for every new edge we need to apply only the ∃-rule 2
        for (from_node_name, to_node_name) in new_edges:
            to_node= graph.nodes[to_node_name]
            for concept in to_node.concepts:
                # apply ∃-rule 2
                existential_rule2_results = apply_existential_rule2(to_node, concept, graph, allConcepts)
                # for new_concept in existential_rule2_results:
                #     next_new_concepts.add((to_node_name, new_concept))
                for associated_node_name, new_concept in existential_rule2_results:
                    next_new_concepts.add((associated_node_name, new_concept))
        
        new_nodes, new_concepts, new_edges = next_new_nodes, next_new_concepts, next_new_edges   
        
    
    subsumers = []
    for D0 in D0s:
        if D0 in graph.nodes[d0.name].concepts: # check again
            subsumers.append(D0)
            
    #print(f"Final concepts of {d0.name}:")
    # for concept in graph.nodes[d0.name].concepts:
    #     print(f"{formatter.format(concept)}")
    #subsumers.append(elFactory.getTop())
    return subsumers

