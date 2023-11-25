import sys
from ELreasoner.reasoner import compute_subsumers_of_class
from ELreasoner.resources import parser, elFactory, formatter

args = sys.argv[1:]
if len(args) != 2:
    print("Usage: python3 FULL_PATH_TO_ONTOLOGY CLASS_NAME")
    sys.exit(1)

ontology_path = args[0]
class_name = args[1]

try:
    
    ontology = parser.parseFile(ontology_path)
except Exception as e:
    print("Error: ontology file not found")
    print("Usage: python3 FULL_PATH_TO_ONTOLOGY CLASS_NAME")
    print(f"Error message: {e}")
    
    sys.exit(1)
try:
    userConcept = elFactory.getConceptName(class_name)
    subsumers = compute_subsumers_of_class(userConcept, ontology)

except Exception as e:
    print("Error: class name not found in ontology")
    print("Usage: python3 FULL_PATH_TO_ONTOLOGY CLASS_NAME")
    print(f"Error message: {e}")
    
    sys.exit(1)
for subsumer in subsumers:
    print(formatter.format(subsumer))

sys.exit(0)
