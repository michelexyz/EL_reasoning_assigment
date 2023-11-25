
from ELreasoner.tbox_conversion import get_no_equivalence_tbox, get_tbox
from ELreasoner.resources import parser, formatter, elFactory
from ELreasoner.subsumption_algorithm import check_subsumed
import os



def compute_subsumers_of_class(C0, ontology):

    # compute all subsumers for a given class name
    tbox = get_tbox(ontology)
    tbox = get_no_equivalence_tbox(tbox)

    allConcepts = ontology.getSubConcepts() 

    conceptNames = ontology.getConceptNames()    
    if C0 not in conceptNames:
        raise Exception(f"Class {C0} not found in ontology")
    
    return check_subsumed(C0, conceptNames, tbox, allConcepts)




if __name__ == "__main__":

    current_directory = os.path.dirname(os.path.abspath(__file__))
    ontology_path = os.path.join(current_directory, 'Sushi23_11.owl')

    ontology = parser.parseFile(ontology_path)

    testConcept = elFactory.getConceptName('Temaki')

    subsumers = compute_subsumers_of_class(testConcept, ontology)

    print(f"These are the subsumers of {formatter.format(testConcept)}:")
    for subsumer in subsumers:
        print(formatter.format(subsumer))




