import warnings

import gensim
import pandas as pd
from gensim.models import Word2Vec
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
warnings.filterwarnings(action='ignore')

"""WORD2VEC"""
# DO NOT CHANGE THE CLASS NAME
class SearchEngine:

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        self._config = config
        self._parser = Parse()
        self._indexer = Indexer(config)
        self._model = None

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def build_index_from_parquet(self, fn):
        """
        Reads parquet file and passes it to the parser, then indexer.
        Input:
            fn - path to parquet file
        Output:
            No output, just modifies the internal _indexer object.
        """

        df = pd.read_parquet(fn, engine="pyarrow")
        documents_list = df.values.tolist()
        # Iterate over every document in the file
        self._indexer.setWord2Vec(True)
        for idx, document in enumerate(documents_list):
            # parse the document
            parsed_document = self._parser.parse_doc(document)
            if parsed_document is None:
                continue
            # index the document data
            self._indexer.add_new_doc(parsed_document)
        # open pickle to save the index
        #TODO change the inverted index file name before summbit and save the idx_bench.pkl
        self._config.set_saveFilesWithoutStem('idx_bench.pkl')

        # run on all of the documents and insert to dict
        self._indexer.insert_to_tweets_dict()
        self.save_index(self._config.get_saveFilesWithoutStem())
        # before printing -> we'll insert to the tweet of docs
        print('Finished parsing and indexing.')

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        self._indexer.load_index(fn)

    def save_index(self, fn):
        self._indexer.save_index(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_precomputed_model(self, model_dir=None):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and
        assign to self._model, which is passed on to the searcher at query time.
        """
        # self._model = gensim.models.KeyedVectors.load_word2vec_format(model_dir + '\\word2vec_model')
        # self._config.set_download_model(False)

        self._model = gensim.models.KeyedVectors.load_word2vec_format('w2v_model',binary=True, encoding='utf-8', unicode_errors='ignore')


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query):
        """
        Executes a query over an existing index and returns the number of
        relevant docs and an ordered list of search results.
        Input:
            query - string.
        Output:
            A tuple containing the number of relevant search results, and
            a list of tweet_ids where the first element is the most relavant
            and the last is the least relevant result.
        """
        searcher = Searcher(self._parser, self._indexer,  model=self._model)
        return searcher.search(query)


