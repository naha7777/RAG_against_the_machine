    # on check qu'on a bien le bon dossier avec le .zip (permissions etc)
    # on extrait le .zip
    # on boucle pour chunk les fichiers un par un
    # une fonction pour les .py et une autre pour les .md ou .txt
    # quand tout est chunk on appelle la fonction qui utilise bm25
    # avec en parametre la liste de tous les chunks

    # parallelement sauvegarder les chunks a cote dans un JSON par exemple,
    # avec le texte, le fichier source, les positions de debut et de fin
    # pour retrouver le chunk 42 par exemple
    # retriever.save("data/processed/bm25_index")
    # # + ton propre fichier chunks.json
    # # à la recherche :
    # results, scores = retriever.retrieve(q_tokens, k=k)   # results = indices
    # best = [chunks[i] for i in results[0]]

    # on tokenise avec corpus_token = bm25s.tokenize(corpus = liste de tous les chunks)
    # cela met en minuscules et decoupe les mots (regex), retire les stopwords
    # peut appliquer un stemmer avec PyStemmer pour que running et runs soit ramené à run par exemple
    # et construit le vocabulaire (mot -> identifiant) et renvoie des identifiants
    # et on met dans un index avec bm25s : retriever = bm25s.BM25() puis
    # retriever.index(corpus_token) et retriever.save("data/processed/bm25_index")
    # et tout ca en moins de 5 minutes
