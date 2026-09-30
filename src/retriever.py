import bm25s

# on tokenise avec corpus_token = bm25s.tokenize(corpus = liste de tous les chunks)
# cela met en minuscules et decoupe les mots (regex), retire les stopwords
# peut appliquer un stemmer avec PyStemmer pour que running et runs soit ramené à run par exemple
# et construit le vocabulaire (mot -> identifiant) et renvoie des identifiants
# et on met dans un index avec bm25s : retriever = bm25s.BM25() puis
# retriever.index(corpus_token) et retriever.save("data/processed/bm25_index")
# et tout ca en moins de 5 minutes
