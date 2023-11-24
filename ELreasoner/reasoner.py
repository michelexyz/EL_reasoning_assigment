
from tbox_conversion import get_no_equivalence_tbox, get_tbox
from resources import parser, formatter, elFactory
from subsumption_algorithm import check_subsumed
import os
import sys




def compute_subsumers_of_class(D0, tbox, allConcepts):

    subsumers = []
    conceptNames = ontology.getConceptNames()

    # loop through all concept names to compute subsumers for every concept name
    for concept in conceptNames:
        print(f"Computimg subsution of {formatter.format(concept)}, with respect to {formatter.format(D0)}")
        if check_subsumed(concept, D0, tbox, allConcepts):
            subsumers.append(concept)
        
    return subsumers


if __name__ == "__main__":

    current_directory = os.path.dirname(os.path.abspath(__file__))
    ontology_path = os.path.join(current_directory, 'pizza.owl')

    ontology = parser.parseFile(ontology_path)
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




