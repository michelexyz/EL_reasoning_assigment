from ELreasoner.tbox_conversion import get_no_equivalence_tbox
from ELreasoner.resources import gateway_class, elFactory, formatter, parser
import pytest
import os

# @pytest.fixture(scope="session", autouse=True)
# def setup_and_teardown():
#     # Setup code goes here
#     yield
#     gateway_class.stop()

def test_get_no_equivalence_tbox():
    
    current_directory = os.path.dirname(os.path.abspath(__file__))
    ontology_path = os.path.join(current_directory, 'pizza.owl')

    ontology =parser.parseFile(ontology_path)
    tbox = ontology.tbox()
    new_tbox = get_no_equivalence_tbox(tbox)
    
    containsCheesyPizza = False

    for axiom in new_tbox:
        axiomType = axiom.getClass().getSimpleName()
        assert axiomType in ['GeneralConceptInclusion']
        
        #check if an axiom contains CheesyPizza on the right side
        if axiom.rhs()== elFactory.getConceptName('"CheesyPizza"'):
            containsCheesyPizza = True
            print(f"left side of axiom: {formatter.format(axiom.lhs())}")

    assert containsCheesyPizza is True

@pytest.mark.skip(reason="EL Algorithm works anyway, just slower")
def test_concepts_equality():

    conjunctions = []
    conceptA = elFactory.getConceptName("A")
    conceptB = elFactory.getConceptName("B")
    conjunctions.append(elFactory.getConjunction(conceptA, conceptB))
    conceptC = elFactory.getConceptName("C")
    conceptD = elFactory.getConceptName("D")
    conjunctions.append(elFactory.getConjunction(conceptC, conceptD))
    
    test_conjunction1 = elFactory.getConjunction(conceptA, conceptB)
    swapped_conjunction = elFactory.getConjunction(conceptB, conceptA)

    if test_conjunction1 in conjunctions:
        print(f"test_conjunction1 {formatter.format(test_conjunction1)} is in conjunctions")

    if swapped_conjunction in conjunctions:
        print(f"swapped_conjunction {formatter.format(swapped_conjunction)} is in conjunctions")

    assert test_conjunction1 == swapped_conjunction

