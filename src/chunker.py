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
