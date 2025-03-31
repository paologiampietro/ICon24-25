import time
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.stats import pearsonr
from recommender_system import vectorize_data

# Decoratore per misurare il tempo di esecuzione delle funzioni
def calculate_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\nTempo di esecuzione: {execution_time:.4f} secondi")
        return result
    return wrapper

# Calcola raccomandazioni usando la similarità del coseno
@calculate_time
def recommend_cosine(steam_data):
    print("\nCalcolo raccomandazioni con similarità del coseno...")
    print("Risultati con similarità del coseno:")
    
    # Vettorizzazione dei dati
    tfidf_matrix = vectorize_data(steam_data)
    tfidf_matrix_array = tfidf_matrix.toarray()
    
    # Calcolo similarità del coseno tra il primo gioco e tutti gli altri
    cosine_sim = cosine_similarity(tfidf_matrix_array[0:1], tfidf_matrix_array).flatten()
    
    # Ottenimento degli indici dei 5 giochi più simili (escludendo se stesso)
    related_indices = cosine_sim.argsort()[::-1][1:6]
    
    # Stampa risultati
    for i, idx in enumerate(related_indices, 1):
        print(f"{i}. {steam_data.iloc[idx]['name']} (score: {cosine_sim[idx]:.4f})")

# Calcola raccomandazioni usando la distanza euclidea
@calculate_time
def recommend_euclidean(steam_data):
    print("\nCalcolo raccomandazioni con distanza euclidea...")
    print("Risultati con distanza euclidea:")
    
    # Vettorizzazione dei dati
    tfidf_matrix = vectorize_data(steam_data)
    tfidf_matrix_array = tfidf_matrix.toarray()
    
    # Calcolo distanza euclidea e conversione a similarità
    euclidean_dist = euclidean_distances(tfidf_matrix_array[0:1], tfidf_matrix_array).flatten()
    euclidean_sim = 1 / (1 + euclidean_dist)  # Conversione a valore di similarità
    
    # Ottenimento degli indici dei 5 giochi più simili
    related_indices = euclidean_sim.argsort()[::-1][1:6]
    
    # Stampa risultati
    for i, idx in enumerate(related_indices, 1):
        print(f"{i}. {steam_data.iloc[idx]['name']} (score: {euclidean_sim[idx]:.4f})")

# Calcola raccomandazioni usando la correlazione di Pearson
@calculate_time
def recommend_pearson(steam_data):
    print("\nCalcolo raccomandazioni con correlazione di Pearson...")
    print("Risultati con correlazione di Pearson:")

    # Vettorizzazione dei dati
    tfidf_matrix = vectorize_data(steam_data)
    tfidf_matrix_array = tfidf_matrix.toarray()
    
    # Calcolo correlazione di Pearson per ogni coppia di giochi
    pearson_corr = []
    reference_vector = tfidf_matrix_array[0]
    
    for i in range(len(tfidf_matrix_array)):
        current_vector = tfidf_matrix_array[i]
        
        # Gestione casi speciali (vettori costanti)
        if np.all(reference_vector == reference_vector[0]) or np.all(current_vector == current_vector[0]):
            pearson_corr.append(0.0)
        else:
            corr, _ = pearsonr(reference_vector, current_vector)
            pearson_corr.append(corr)
    
    # Ottenimento degli indici dei 5 giochi più correlati
    related_indices = np.array(pearson_corr).argsort()[::-1][1:6]
    
    # Stampa risultati
    for i, idx in enumerate(related_indices, 1):
        print(f"{i}. {steam_data.iloc[idx]['name']} (score: {pearson_corr[idx]:.4f})")

# Funzione per vettorizzare i dati testuali usando TF-IDF
def vectorize_data(steam_data):
    # Gestione valori mancanti e vettorizzazione
    steam_data['all_content'] = steam_data['all_content'].fillna('')
    vectorizer = TfidfVectorizer(analyzer='word')
    return vectorizer.fit_transform(steam_data['all_content'])

# Calcola la sparsità della matrice dei dati
def calculating_sparsity(data): 
    data = data.to_numpy()
    sparsity = 1.0 - (np.count_nonzero(data) / float(data.size))
    return sparsity


if __name__ == "__main__":
    # Caricamento e preparazione dei dati
    steam_data = pd.read_csv('dataset/steam.csv')
    steam_data['positivity_quote'] = steam_data['positive_ratings'] / steam_data['negative_ratings']
    steam_data['genres'] = steam_data['steamspy_tags']
    steam_data = steam_data[['name','release_date','developer','publisher','platforms','genres','positivity_quote', 'average_playtime','owners','price']].copy()
    
    # Calcolo e stampa della sparsità del dataset
    print("\nCalcolo sparsità del dataset...")
    sparsity_value = calculating_sparsity(steam_data)
    print(f"\nSparsità del dataset: {sparsity_value * 100:.2f} %\n")
    
    # Esecuzione dei metodi di raccomandazione
    recommend_cosine(steam_data)
    recommend_euclidean(steam_data)
    recommend_pearson(steam_data)
    