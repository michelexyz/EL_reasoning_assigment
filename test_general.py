import pytest
from tbox_conversion import get_no_equivalence_tbox
from py4j.java_gateway import JavaGateway

@pytest.fixture
def gateway_resources():
    # Setup: Initialize JavaGateway and other resources
    gateway = JavaGateway()
    parser = gateway.getOWLParser()
    elFactory = gateway.getELFactory()
    ontology = parser.parseFile("pizza.owl")
    tbox = ontology.tbox()

    # get a formatter to print in nice DL format
    formatter = gateway.getSimpleDLFormatter()

    yield gateway, formatter, elFactory, tbox  # This is what the test function will use

    # Teardown: Close the Java Gateway, etc.
    gateway.close()

def test_get_no_equivalence_tbox(gateway_resources):
    _, _, _, tbox = gateway_resources
    new_tbox = get_no_equivalence_tbox(tbox)
    

    for axiom in new_tbox:
        axiomType = axiom.getClass().getSimpleName()
        assert axiomType in ['GeneralConceptInclusion', 'EquivalenceAxiom']

def test_concepts_equality(gateway_resources):
    _, formatter, elFactory, _ = gateway_resources
    # create a list of conjuctions for test purposes


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