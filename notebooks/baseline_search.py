""" 
Main functions for EviDENce baseline search,
i.e., search engine for performing keyword search on the EviDENce text corpus

author: Martine de Vos
email: mgdevos@gmail.com
"""

from collections import defaultdict
from googletrans import Translator 
import nltk
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer
import os
import pandas as pd
import shutil
from stop_words import get_stop_words
from translate import Translator # use this module as alternative for googletrans 

from whoosh import scoring
from whoosh import qparser
from whoosh.analysis import StandardAnalyzer
from whoosh.fields import Schema, TEXT, ID
from whoosh.filedb.filestore import FileStorage
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.writing import AsyncWriter



def get_nltk_pos(text):
    
    ''' 
    Tokenize text and derive POS tags from nltk/treebank
    ''' 
    toks = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(toks)

    return tagged


def get_wordnet_pos(treebank_tag):

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        # As default pos in lemmatization is NOUN
        return wordnet.NOUN



def create_lemma(expr):
    
    '''
    Convert expression to wordnet lemma 
    '''
    
    lemmatizer = WordNetLemmatizer()
    toktag = get_nltk_pos(expr)
    lemmas = []
    
    for tok,treebank_tag in toktag:
        pos = get_wordnet_pos(treebank_tag)
        lemma = lemmatizer.lemmatize(tok, pos)
        lemmas.append(lemma)
 
    string = " ".join(lemmas)
    
    return string


def eng_to_dutch(expr):
    
    '''
    Translate english expression to dutch using googletrans module
    '''    

    translator = Translator(provider = 'microsoft',to_lang='nl')
    translation = translator.translate(expr)
    
    ## The following lines are for use with googletrans module
    #translator = Translator()
    #translation = translator.translate(expr,dest='nl')
      
    return translation


def eng_to_dutch_list(eng_list):
    
    '''
    Translate list of english words to dutch using python translator module
    '''    
    
    #translator = Translator(to_lang = 'nl')
    translator = Translator()
    dutch_list = []

    for lemmas in eng_list:
        string = ' '.join(lemmas)
        translation = translator.translate(string,dest='nl')
        dutch_list.append(translation.text)  
        
    return dutch_list


def remove_stopwords(mylist):
    
    '''
    Remove stopwords from list of terms
    '''
    
    stop_nl = get_stop_words('dutch')
    analyzer = StandardAnalyzer(stoplist=stop_nl)

    no_stops = []
    for item in mylist:
        result = [token.text for token in analyzer(item)]
        no_stops.append(tuple(result))   
    
    return no_stops


def quote_phrase (term):
    '''
    Add double quotes to term that contains multiple words,
    so this is treated as a phrase in a query
    '''
    if len(term.split()) > 1:
        new_term ='"{}"'.format(term) 
    else:
        new_term = term

    return new_term


def create_searchable_data(folder):
    
    '''
    Create index for documents in a given directory 
    Schema definition: title(name of file), path(as ID), content(indexed
    but not stored),textdata (stored text content)
    
    '''
    schema = Schema(title=TEXT(stored=True),path=ID(stored=True),\
              content=TEXT,textdata=TEXT(stored=True)) 
    indexdir = os.path.join(os.sep,folder,"indexdir")
    if not os.path.exists(indexdir):
        os.mkdir(indexdir)

    #ix = create_in(indexdir,schema)    
    storage = FileStorage(indexdir)    
    ix = storage.create_index(schema)
    # Create an index writer to add documents as per schema 
    # Use Async instead of regular writer to prevent fail due to locking
    writer = AsyncWriter(ix)

    for file in os.listdir(folder):
        fpath = os.path.join(folder,file)
        if os.path.isfile(fpath):
            title,ext = os.path.splitext(file)
            fp = open(fpath, 'r')
            text = fp.read()
            writer.add_document(title = title,path=fpath,content=text,textdata=text)
            fp.close()
        else:
            pass
    writer.commit()  


def create_searchable_data2(folder):
    
    '''
    Create index for documents in a (NB: double nested) directory
    Schema definition: title(name of file), path(as ID), content(indexed
    but not stored),textdata (stored text content)
    
    '''
    schema = Schema(title=TEXT(stored=True),path=ID(stored=True),\
              content=TEXT,textdata=TEXT(stored=True)) 
    indexdir = os.path.join(os.sep,folder,"indexdir")
    if not os.path.exists(indexdir):
        os.mkdir(indexdir)

    #ix = create_in(indexdir,schema)    
    storage = FileStorage(indexdir)    
    ix = storage.create_index(schema)
    # Create an index writer to add documents as per schema 
    # Use Async instead of regular writer to prevent fail due to locking
    writer = AsyncWriter(ix)

    dirpaths = [os.path.join(folder,i) for i in os.listdir(folder)]
    for dpath in dirpaths:
        # Loop over directories and add the corresponding files; skip indexdir
        if not dpath == os.path.join(folder,"indexdir"):
            filepaths = [os.path.join(dpath,j) for j in os.listdir(dpath)]
            for fpath in filepaths:  
                head,tail = os.path.split(fpath)
                title,ext = os.path.splitext(tail)
                #print("Title: %s "%title)
                fp = open(fpath, 'r')
                text = fp.read()
                writer.add_document(title = title, path=fpath,\
                                content = text, textdata = text)
                fp.close()
        else:
            pass
    writer.commit()   
 


 
def search_corpus(indexdir,query):
    """
    Given an indexdir and a query, perform search on the corresponding corpus
    NB OR group, TF-IDF scoring 
    Returns a pandas dataframe
    """
    
    ix = open_dir(indexdir)

    parser = qparser.QueryParser("content", schema=ix.schema,group=qparser.OrGroup)
    my_query = parser.parse(query)

    cols_list = []
    titles_list = []

    with ix.searcher(weighting=scoring.TF_IDF()) as searcher:
        results = searcher.search(my_query,limit=None, terms = True)
        for res in results:
            titles_list.append(res["title"])
            col_dict = defaultdict(int)
            hits = [term.decode('utf8')  for where,term in res.matched_terms()]
            for hit in hits:
                col_dict[hit]+= 1
            cols_list.append(col_dict)

    results_df = pd.DataFrame(cols_list)
    results_df.set_index([titles_list], inplace=True)
    
    return results_df





 
def copy_fragments (file,source,dest):
    
    '''
    For every textfragment mentioned in the csv file for manual annotation copy the corresponding lemma-based fragment from the  
    corpus folder into a separate folder. The automatic analyses, i.e., keyword search and machine learning, can be performed on 
    the fragments in that folder
    '''
    
    # Collect titles in csv file NB these are files with text and not lemmas
    file_df = pd.read_csv(file, sep=',', encoding = "ISO-8859-1").dropna(how='all')
    
    delimiter = '_clipped'
    
    for title in file_df['Titel'].iloc[:-1].tolist():
        # Recreate folder name from file title
        fol,rest = title.split(delimiter)
        fol = fol + delimiter
        # Adapt title to point to lemma -and not text-file
        file = title.replace("text","lemma.txt")
        srcpath = os.path.join(os.sep,source,fol,file)
        destpath = os.path.join(os.sep,dest)
        # Copy file to destination folder
        shutil.copy(srcpath, destpath)
