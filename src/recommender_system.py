import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Funzione per ottenere le informazioni del gioco dall'utente
def get_info():
    print("(Ricorda di inserire i dati con la lettera maiuscola iniziale)\n")
    nome = input("Inserisci il nome:\n")
    developer = input("\nInserisci lo sviluppatore:\n")
    publisher = input("\nInserisci la casa pubblicatrice:\n")
    platforms = input("\nInserisci le piattaforme:\t (ricorda tra una parola e l'altra di mettere il simbolo ';' )\n")
    genres = input("\nInserisci il genere:\t (ricorda tra una parola e l'altra di mettere il simbolo ';' )\n")
    
    # Crea un dataframe con i dati inseriti dall'utente
    users_data = pd.DataFrame({
        'name': [nome], 
        'developer': [developer], 
        'publisher': [publisher], 
        'platforms': [platforms], 
        'genres': [genres]
    })
    return users_data

# Funzione per vettorizzare i dati testuali usando TF-IDF
def vectorize_data(steam_data):
    # Gestione valori mancanti e vettorizzazione
    steam_data['all_content'] = steam_data['all_content'].fillna('')
    vectorizer = TfidfVectorizer(analyzer='word')
    return vectorizer.fit_transform(steam_data['all_content'])

# Funzione principale per costruire le raccomandazioni
def construct_recommendation(filename, users_data):
    # Caricamento e preparazione dei dati Steam
    steam_data = pd.read_csv(filename)
    steam_data['positivity_quote'] = steam_data['positive_ratings'] // steam_data['negative_ratings']
    steam_data['genres'] = steam_data['steamspy_tags']
    steam_data = steam_data[['name', 'release_date', 'developer', 'publisher', 'platforms', 
                           'genres', 'positivity_quote', 'average_playtime', 'owners', 'price']].copy()
    
    # Verifica se il gioco inserito esiste già nel dataset
    control = 1
    index = 0
    for i, name in enumerate(steam_data['name']):
        if users_data['name'][0] == name:
            index = i
            control = 0
            break
    
    # Se il gioco non esiste, lo aggiunge all'inizio del dataframe
    if control == 1:
        steam_data = pd.concat([users_data, steam_data], ignore_index=True)
        index = 0  
    
    # Crea una colonna combinata con tutte le informazioni testuali
    steam_data['all_content'] = (steam_data['name'] + ';' + steam_data['developer'] + ';' + 
                                steam_data['publisher'] + ';' + steam_data['platforms'] + ';' + 
                                steam_data['genres'])
    
    # Vettorizzazione dei dati
    tfidf_matrix = vectorize_data(steam_data)
    
    print('\nInizio ricerca di giochi...')
    
    # Calcolo similarità del coseno e selezione top 5 giochi
    cosine_sim = cosine_similarity(tfidf_matrix[index:index+1], tfidf_matrix).flatten()
    correlation = list(enumerate(cosine_sim))
    sorted_corr = sorted(correlation, reverse=True, key=lambda x: x[1])[1:6]  # Esclude se stesso
    games_index = [i[0] for i in sorted_corr]
    
    print('\nPassaggio alla analisi del modello...')
    
    return games_index, steam_data

# Funzione principale del sistema di raccomandazione
def get_recommendation():
    print("RECOMMENDER SYSTEM\n\nBenvenuto, digita le caratteristiche del gioco su cui vuoi che si avvii la raccomandazione\n")
    
    # Ottiene i dati dell'utente e verifica la correttezza
    users_data = get_info()
    
    while True:
        print("\nQuesto è il videogioco che hai inserito:\n")
        print(users_data.head())
        risposta = input("\nÈ corretto? (si/no):\t").strip().lower()
        
        # Validazione input
        while risposta not in ['si', 's', 'yes', 'y', 'no', 'n']:
            print("Risposta non valida. Per favore rispondi con 'si' o 'no'.")
            risposta = input("\nÈ corretto? (si/no):\t").strip().lower()
        
        if risposta in ['no', 'n']:
            users_data = get_info()
        else:
            break
    
    # Costruisce le raccomandazioni
    games_index, steam_data = construct_recommendation('dataset/steam.csv', users_data)
    
    # Stampa i giochi raccomandati
    print("\nEcco i 5 giochi consigliati:")
    for i, idx in enumerate(games_index, 1):
        print(f"{i}. {steam_data.iloc[idx]['name']}")
    
    # Confronto tra diverse metriche di similarità
    from metric_confront import recommend_cosine, recommend_euclidean, recommend_pearson, calculating_sparsity
    
    print("\n[CONFRONTO METRICHE]")
    recommend_cosine(steam_data)
    recommend_pearson(steam_data)
    recommend_euclidean(steam_data)
    sparsity_value = calculating_sparsity(steam_data)
    print(f"\nSparsità del dataset: {sparsity_value * 100:.2f} %")
    return games_index

if __name__ == "__main__":
    get_recommendation()