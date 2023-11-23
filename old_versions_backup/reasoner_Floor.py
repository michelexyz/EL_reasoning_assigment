from py4j.java_gateway import JavaGateway

def convert_tbox(tbox):
        new_tbox = []
        axioms = tbox.getAxioms()
        # Loop over all axioms in the Tbox
        for axiom in axioms: 
            axiomType =axiom.getClass().getSimpleName()
            # If the axiom is an equivalence axiom, replace by CGIs
            if axiomType == 'EquivalenceAxiom': 
                concepts = axiom.getConcepts()
                A = concepts[0]
                B = concepts[1]
                gci1 = elFactory.getGCI(A, B)
                gci2 = elFactory.getGCI(B, A)
                new_tbox.append(gci1)
                new_tbox.append(gci2)
            else: 
                new_tbox.append(axiom)
        return new_tbox


def check_subsumption(C0, D0, tbox, allConcepts):
    model_assigned = {'d0': {C0}}   #keeps track of all the concept assigned to each element/node
    model_relations = {'d0': dict()} #keeps track of all the relations where it has the form of predecessor: {role:[list of successor elements]}
    # example: model_relations = {
    # 'd0': {'hasTopping': ['d1', 'd2', 'd3'], 'hasBase': ['d4']},
    # 'd1': {'isIngredientOf': ['d0']}        
    # }

    # example: model_assigned = {
    #     'd0': {'∃hasIngredient.B','A ⊓ ∃hasTopping.B', 'A', '∃hasTopping.B'},
    #     #'d1': {'B', 'C', '∃r.∃t.B'}
    # }
    
    changed = True
    while changed:
        changed = False
        for node, assigned in list(model_assigned.items()):
            #print("assigned", [formatter.format(x) for x in assigned])

            # ⊤-rule: Add ⊤ to any individual
            top = elFactory.getTop()
            if top not in assigned:
                assigned.add(top)
                changed = True

            # ⊑-rule: If d has C assigned and C ⊑ D ∈ T , then also assign D to d
            for axiom in tbox:
                conceptType = axiom.getClass().getSimpleName()
                if conceptType == "GeneralConceptInclusion":
                    if axiom.lhs() in assigned and axiom.rhs() not in assigned:
                        assigned.add(axiom.rhs())
                        changed = True
                    
            # ⊓-rule 2: If d has C and D assigned, assign also C ⊓ D to d.2
            for concept in allConcepts:
                conceptType = concept.getClass().getSimpleName()
                
                if conceptType == "ConceptConjunction":
                    conjuncts = concept.getConjuncts()
                    element_0 = conjuncts[0]
                    element_1 =  conjuncts[1]
                    if element_0 in assigned and element_1 in assigned and concept not in assigned:
                        assigned.add(concept)
                        changed = True

            #∃-rule 2: If d has an r-successor with C assigned, add ∃r.C to d
            if node in model_relations:
                for role, successors in list(model_relations[node].items()):
                    for successor in list(successors):
                        for x in set(model_assigned[successor]):
                            rolerestriction = elFactory.getExistentialRoleRestriction(role, x)
                            if rolerestriction not in model_assigned[node]:
                                model_assigned[node].add(rolerestriction)
                                changed = True
            
            for concept in set(assigned):
                conceptType = concept.getClass().getSimpleName()
                
                if conceptType == "ConceptConjunction":
                    conjuncts= concept.getConjuncts()
                    element_0 = conjuncts[0]
                    element_1 =  conjuncts[1]

                    #⊓-rule 1: If d has C ⊓ D assigned, assign also C and D to d.
                    if element_0 not in assigned:
                        assigned.add(element_0)
                        changed = True
                        
                    if element_1 not in assigned:
                        assigned.add(element_1)
                        changed = True
                        
                    
                if conceptType == "ExistentialRoleRestriction":
                    role = concept.role()
                    filler = concept.filler()
                    
                    element_found = False
                    #∃-rule 1.1 - If d has ∃r.C assigned and there is an element e with initial concept C assigned, 
                            # --> make e the r-successor of d
                    for element, assignments in list(model_assigned.items()):
                        if filler in assignments:
                            if role not in model_relations[node]:
                                model_relations[node][role] = set()
                            model_relations[node][role].add(element)
                            element_found = True
                            changed = True

                    #∃-rule 1.2 - If d has ∃r.C assigned and there is no element e with initial concept C assigned, 
                            # -->  add a new r-successor to d, and assign to it as initial concept C.
                    if not element_found:
                        new_assignment = f'd{len(model_assigned)}'
                        if role not in model_relations[node]:
                            model_relations[node][role] = set()
                        model_relations[node][role].add(new_assignment)
                        model_assigned[new_assignment] = {filler}  # Assign initial concept C
                        changed = True
  
        if changed:
            #print(model_assigned)
            #print(model_relations)
            break
    
    
    return D0 in model_assigned['d0']

# Example usage
gateway = JavaGateway()  # Assuming gateway is already set up
formatter = gateway.getSimpleDLFormatter()
ontology = gateway.getOWLParser().parseFile("pizza.owl")
gateway.convertToBinaryConjunctions(ontology)
elFactory = gateway.getELFactory()

allConcepts = ontology.getSubConcepts()
tbox = ontology.tbox()
tbox = convert_tbox(tbox)
# print([formatter.format(x) for x in tbox])

C0 = elFactory.getConceptName("kappamaki")
subsumers =[]
for concept in ontology.getConceptNames():
    D0 = concept
    if D0 != C0:
        if check_subsumption(C0, D0, tbox, allConcepts): 
            print(f"{D0} is a subsumer of {C0}")
            subsumers.append(C0)
print([formatter.format(x) for x in subsumers])






