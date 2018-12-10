# ADAH-EviDENce baseline search
> Query expansion method to select violence documents in a corpus

The EviDENce project explores new ways of searching historical text sources by applying digital technologies, i.e., semantic web technologies and machine learning. The project focuses on events referring to war and violence and how these are described by eyewitnesses. 

This repository contains a basic, top-down approach to select relevant documents, i.e., documents containing descriptions of violent events, using a set of predefined keywords.

#### Query expansion
We base our keywords on classes from the [Circumstantial Event Ontology (CEO)](https://github.com/RoxaneSegers/CEO-Ontology), a shared vocabulary that formalizes the context of calamity events. As the classes in the CEO are defined on a high level of abstraction, e.g., "IntentionalDamaging", we used [instances](https://github.com/RoxaneSegers/CEO-Ontology/blob/master/CEO%20Vocabulary/vocabulary-ECBCEO.xlsx) of these classes, e.g., "beat", as found in the ECB+ corpus to build our initial list of keywords.
From this list we [manually selected](./data/MdV_selectedCEOECB.csv) all keywords that are related to violence, lemmatized these and translated these to Dutch. 


## Getting started

The baseline_search is running as a Jupyter notebook in the Anaconda Python environment with Python version 3.6.5. Dependencies are listed in [requirements.txt](requirements.txt)

Install the baseline_search by cloning this repository

```
git clone https://github.com/ADAH-EviDENce/baseline_search.git
cd baseline_search 
jupyter notebook
```
Browse to: 
```
http://localhost:8888/notebooks/notebooks/EviDENce_baseline_search_engine.ipynb
```
and you should get a local copy of the notebook containing the baseline_search engine.


#### Configuration
To run the notebook locally make sure to adapt in the first cell:

* the path to the directory containing the corpus you are searching
* the path to the directory where you want to save search results



## Features
The baseline_search allows you to:
* index a corpus of text documents
* search the corpus using customized queries
* analyze the search results in a pandas dataframe


## References
CEO ontology: Segers, R., T.Caselli, P. Vossen (2018). “The Circumstantial Event Ontology (CEO) and ECB+/CEO; an Ontology and Corpus for Implicit Causal Relations between Events”. In: Proceedings of the 11th edition of the Language Resources and Evaluation Conference LREC, Miyazaki, Japan, May 7-12, 2018.



## Licensing
The [data](./data) in this project is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License. Based on a work at https://github.com/RoxaneSegers/CEO-Ontology.

The code in this project is licensed under Apache License 2.0
