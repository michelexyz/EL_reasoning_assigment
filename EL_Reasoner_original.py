from collections import defaultdict
from py4j.java_gateway import JavaGateway

# connect to the java gateway of dl4python
gateway = JavaGateway()

# get a parser from OWL files to DL ontologies
parser = gateway.getOWLParser()

# get a formatter to print in nice DL format
formatter = gateway.getSimpleDLFormatter()

elFactory = gateway.getELFactory()

# load an ontology from a file
ontology = parser.parseFile("pizza.owl")

# gateway.convertToBinaryConjunctions(ontology)
# # get the TBox axioms
# tbox = ontology.tbox()

def get_tbox(ontology):
    # Converting to binary conjunctions (change all conjunctions so that they have at most two conjuncts)
    gateway.convertToBinaryConjunctions(ontology)
    tbox = ontology.tbox()
    return tbox

def get_no_equivalence_tbox(tbox):
    # Assume that TBox contains no equivalence axioms
    # If the TBox contains equivalence axioms C ≡ D, replace each such axiom by the two axioms C ⊑ D and D ⊑ C
    new_tbox = []
    axioms = tbox.getAxioms()

    # loop over all axioms in the Tbox
    for axiom in axioms: 
        axiomType = axiom.getClass().getSimpleName()
        # if equivalence axioms C ≡ D, replace each such axiom by the two axioms C ⊑ D and D ⊑ C --> GCI
        if axiomType == 'EquivalenceAxiom':
            # get concepts in equivalence axiom
            concepts = axiom.getConcepts()
            left_concept = concepts[0]
            right_concept = concepts[1]
            gci1 = elFactory.getGCI(left_concept,right_concept)
            gci2 = elFactory.getGCI(right_concept,left_concept)
            new_tbox.append(gci1)
            new_tbox.append(gci2)
        # if axiom is not an equivalence axiom, just add it to the tbox
        else: 
            new_tbox.append(axiom)
    return new_tbox

# get all concepts occurring in the ontology
allConcepts = ontology.getSubConcepts()

conceptNames = ontology.getConceptNames()

#############################################################

def check_subsumed(C0, D0, tbox):

    # loop through all concept names to compute subsumers from every concept name
    for concept in conceptNames:
        model_dict = {} # dict with key d0 and value is a set with intially only C1
        model_dict['d0'] = set() # dictionary values are a set where we add the concepts to 
        # assign C0 to d0 as initial concept
        model_dict['d0'].add(concept)  
        relations_dict = {'d0': dict()}  

        changed = True
        while changed:
            changed = False
            # my_dict = apply_rule(self, axiom, model_dict)
            tbox = ontology.tbox()
            axioms = tbox.getAxioms()
            #loop through all axioms in the Tbox
            for axiom in axioms: #  or for axiom in tbox. axioms -> tbox.getAxioms():
                # check type of axiom in Tbox
                axiomType = axiom.getClass().getSimpleName() 

                # apply rules on d in all possible ways
                if axiomType == "TopConcept$":
                    # apply ⊤-rule
                    apply_top_rule(axiom, model_dict)
                if axiomType == "ConceptConjunction":
                    # apply ⊓-rules:
                    apply_conjunction_rule(axiom, model_dict)
                if axiomType == "ExistentialRoleRestriction":
                    apply_existential_role_rest(axiom, model_dict)

                if axiomType == "GeneralConceptInclusion":
                    # ⊑-rule: If d has C assigned and C ⊑ D ∈ T , then also assign D to d
                    apply_subsumption_rule(axiom, model_dict)

        def apply_top_rule(axiom, model_dict):
            # ⊤-rule: Add ⊤ to any individual.
            for node, value in model_dict.items():
                if axiom not in value:
                    value.add(axiom)
                    changed = True
                    return changed

        def apply_subsumption_rule(axiom, model_dict):
            for node, value in model_dict.items():
                # if d has C (left-hand side) assigned and C ⊑ D ∈ T  
                if axiom.lhs() in value:
                    # then also assign D to d: add right hand side of the axiom to the dicionary
                    value.add(axiom.rhs())
                    changed = True
                    return changed

        def apply_conjunction_rule(axiom, model_dict):
            conjuncts = axiom.getConjuncts()
            # get left and right conjuncts
            left_conjunct = conjuncts[0]
            right_conjunct = conjuncts[1]

            for key, value in model_dict.items():
                # ⊓-rule 1: If d has C ⊓ D assigned, assign also C and D to d.
                if axiom in value:
                    value.add(left_conjunct)
                    value.add(right_conjunct)
                    changed = True
                    return changed
                # ⊓-rule 2: If d has C and D assigned, assign also C ⊓ D to d.
                if left_conjunct in value and right_conjunct in value:
                    value.add(axiom)
                    changed = True
                    return changed

        def apply_existential_role_rest(axiom, model_dict):
            role = concept.role()
            filler = concept.filler()
            for node, concepts in model_dict.items():
                if role not in relations_dict[node]:

                    changed=True
                    return changed

    # If D0 was assigned to d0, return YES (C0 subsumed by D0), otherwise return NO (C0 not subsumed by D0)
    if D0 in model_dict[0]:
        return True
    return False  

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



