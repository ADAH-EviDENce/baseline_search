from googletrans import Translator 
import nltk
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer
import os
import pandas as pd
from stop_words import get_stop_words
#from translate import Translator # use this module instead of googletrans for stability 
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



def create_lemma_list(file):
    
    '''
    Convert csv file with ceo mentions to list of wordnet lemma's  
    '''
    pre_list = pd.read_csv(file,sep=';')
    mention_list = list(pre_list["Mention"].dropna())
    
    lemmatizer = WordNetLemmatizer()
    lemmas = []

    for mention in mention_list:
        toktag = get_nltk_pos(mention)
        lemma = []
        for tok,treebank_tag in toktag:
            pos = get_wordnet_pos(treebank_tag)
            res = lemmatizer.lemmatize(tok, pos)
            lemma.append(res)
        lemmas.append(lemma)
    
    return lemmas


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


def create_searchable_data(folder):
    
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
 