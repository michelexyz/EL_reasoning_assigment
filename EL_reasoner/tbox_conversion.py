from collections import defaultdict
from py4j.java_gateway import JavaGateway

# connect to the java gateway of dl4python
gateway = JavaGateway()

# get a parser from OWL files to DL ontologies
parser = gateway.getOWLParser()

# get a formatter to print in nice DL format
formatter = gateway.getSimpleDLFormatter()

elFactory = gateway.getELFactory()



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
    uncovered_axioms_types = set()

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
        elif axiomType == 'GeneralConceptInclusion': 
            new_tbox.append(axiom)
        else:
            uncovered_axioms_types.add(axiomType)
    print("These are the uncovered axiom types:")
    for uncovered_axiom_type in uncovered_axioms_types:
        print(uncovered_axiom_type)

    return new_tbox

if __name__ == "__main__":
    
    # load an ontology from a file
    ontology = parser.parseFile("pizza.owl")
    tbox = get_tbox(ontology)
    axioms = tbox.getAxioms()    
    
    #print("These are the axioms in the TBox:")
    #for axiom in axioms:
    #    print(formatter.format(axiom))

    # Get no equivalence tboxp
    new_tbox = get_no_equivalence_tbox(tbox)
    #print("These are the axioms in the TBox without equivalence axioms:")
    for axiom in new_tbox:
        left_concept = axiom.lhs()
        print(formatter.format(left_concept))

