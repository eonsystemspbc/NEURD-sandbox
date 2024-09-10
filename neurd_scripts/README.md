# NEURD_scripts

This folder contains scripts to run the various steps of the NEURD proofreading pipeline while saving intermediate results wherever possible. To run, copy scripts into the docker container and run them there. Scripts are numbered according to the order in which they should be executed. Each script takes a segment ID for a MICrONs neuron (v117) as well as a directory name as input

---
01_data_collection.py: downloads mesh and synapses relating to neuron segment_id and saves them in appropriate format

02_decimation.py: loads a mesh and decimates it by factor 0.0625, saving result and products

03_soma_identification.py: loads products and a mesh and runs soma identification, saving results in products

04_decomposition.py: loads mesh and products and decomposes it into a neurd neuron object

05_soma_splitting.py: loads neuron object and splits it into component neurons, if applicable. Each component neuron is saved with suffix _split_i
