from collections import defaultdict
from py4j.java_gateway import JavaGateway
from tbox_conversion import get_no_equivalence_tbox, get_tbox
from resources import ontology, parser, formatter, elFactory
from subsumption_algorithm import check_subsumed





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




