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

    yield gateway, tbox  # This is what the test function will use

    # Teardown: Close the Java Gateway, etc.
    gateway.close()

def test_get_no_equivalence_tbox(gateway_resources):
    gateway, tbox = gateway_resources
    new_tbox = get_no_equivalence_tbox(tbox)
    

    for axiom in new_tbox:
        axiomType = axiom.getClass().getSimpleName()
        assert axiomType in ['GeneralConceptInclusion', 'EquivalenceAxiom']
