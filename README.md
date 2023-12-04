# Knowlege Representation Assigment
This repo was made for the Knowledge representation course at Vrije Universiteit, Amsterdam.
## The EL reasoner
The repo was made to work on an implementation of a reasoner that uses EL logic rules to compute the subsumers of a class of a OWL ontology.
The reasoner algorithm applies the classical EL reasoning rules (top rule, subsumption rule, the two conjunction rules and the two existential rules) only considering newly genereated nodes edges or concepts of the graph. This way it doesn't waste computational time and complexity appling rules between nodes on which have already been applied.
## The Sushi ontology
For the assigment we also designed a [custom ontology](https://github.com/michelexyz/Knowlege_Representation_Assigment/blob/main/src/ELreasoner/Sushi23_11.owl) for an hypothetical sushi restaurant.
## The report
Finally we have discussed the design of our project and a research question inside a paper-like [report](https://github.com/michelexyz/Knowlege_Representation_Assigment/blob/main/report.pdf) on which you can find more details. 
## Contributors
The ontology and the report was made in collaboration with two fellow students of mine: [Eli Partodikromo](https://github.com/eliparto) and [Mirthe Kemp](https://github.com/mirthekemp).


## Usage
First, create a venv environment on the root of the project using "python -m venv .venv"

Second, run "pip install -e ." on the root of the project

Finally, run the dl4python-0.1-jar-with-dependencies.jar file and leave it running

The resonerCLI.py file can be called from command line, to print the subsumers of a specific class, with the syntax:

python FULL_PATH_TO_ONTOLOGY CLASS_NAME


