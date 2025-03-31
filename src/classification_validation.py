import sklearn
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import roc_auc_score
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import RepeatedKFold

from recommender_system import get_recommendation

def RandomizedSearch(hyperparameters, X_train, y_train):
    #Esegue una ricerca randomizzata degli iperparametri per il modello KNN.
    print("\nInizio RandomizedSearch...")
    knn = KNeighborsClassifier()

    # Configura la cross-validation con 10 fold ripetuti 3 volte
    cvFold = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
    randomSearch = RandomizedSearchCV(estimator=knn, cv=cvFold, param_distributions=hyperparameters, n_jobs=-1, verbose=1)
    
    print("Avvio fitting del modello...")
    best_model = randomSearch.fit(X_train, y_train)
    print("RandomizedSearch completata con successo")
    
    return best_model

def modelEvaluation(y_test, y_pred, pred_prob):
    #Valuta le prestazioni del modello utilizzando metriche di classificazione.
    print('\nValutazione modello in corso...')
    print('Classification report: \n', classification_report(y_test, y_pred))

    roc_score = roc_auc_score(y_test, pred_prob, multi_class='ovr')
    print('ROC score: ', roc_score)

    return roc_score

def HyperparametersSearch(X_train, X_test, y_train, y_test):
    #Esegue una ricerca degli iperparametri ottimali per il modello KNN.
    print("\nInizio HyperparametersSearch...")
    result = {}
    n_neighbors = list(range(1,30))
    weights = ['uniform', 'distance']
    metric = ['euclidean', 'manhattan', 'hamming']

    hyperparameters = dict(metric=metric, weights=weights, n_neighbors=n_neighbors)

    i = 0
    max_iterations = 3  
    print(f"Numero massimo di iterazioni: {max_iterations}")
    
    while i < max_iterations:
        print(f"\nIterazione {i+1}/{max_iterations}")
        try:
            best_model = RandomizedSearch(hyperparameters, X_train, y_train)

            bestweights = best_model.best_estimator_.get_params()['weights']
            bestMetric = best_model.best_estimator_.get_params()['metric']
            bestNeighbours = best_model.best_estimator_.get_params()['n_neighbors']

            print(f"Parametri trovati - n_neighbors: {bestNeighbours}, metric: {bestMetric}, weights: {bestweights}")

            knn = KNeighborsClassifier(n_neighbors=bestNeighbours, weights=bestweights, 
                                     metric=bestMetric, n_jobs=-1)
            knn.fit(X_train, y_train)

            pred_prob = knn.predict_proba(X_test)
            roc_score = roc_auc_score(y_test, pred_prob, multi_class='ovr')

            result[i] = {
                'n_neighbors': bestNeighbours,
                'metric': bestMetric,
                'weights': bestweights,
                'roc_score': roc_score
            }
            print(f"ROC score corrente: {roc_score}")
            
        except Exception as e:
            print(f"Errore durante l'iterazione {i}: {str(e)}")
            continue
            
        i += 1

    if not result:
        raise ValueError("Nessun risultato valido ottenuto dalla ricerca di iperparametri")

    result = dict(sorted(result.items(), key=lambda x: x[1]['roc_score'], reverse=True))
    first_el = list(result.keys())[0]
    return list(result[first_el].values())

def SearchingBestModelStats(X_train, X_test, y_train, y_test):
    #Cerca e valuta il miglior modello KNN attraverso tre fasi:

    print('\n\n=== FASE 1: Modello con parametri di base ===')
    knn = KNeighborsClassifier(n_neighbors=5)
    
    print("\nAddestramento modello base...")
    knn.fit(X_train, y_train)

    print('\nPredizioni test:')
    print('Predetti:', knn.predict(X_test)[0:5])
    print('Effettivi:', y_test[0:5])

    y_pred = knn.predict(X_test)
    pred_prob = knn.predict_proba(X_test)

    print('\nValutazione modello base...')
    modelEvaluation(y_test, y_pred, pred_prob)
    print('\nLa nostra accuratezza è bassa, procediamo a migliorare gli iperparametri\n')

    print('=== FASE 2: Ricerca iperparametri ottimali ===')
    try:
        result = HyperparametersSearch(X_train, X_test, y_train, y_test)
    except Exception as e:
        print(f"Errore critico durante la ricerca iperparametri: {str(e)}")
        return None

    print('\n=== MIGLIORI IPERPARAMETRI TROVATI ===')
    bestNeighbours, bestMetric, bestweights, best_roc = result
    print(f'n_neighbors: {bestNeighbours}')
    print(f'metric: {bestMetric}')
    print(f'weights: {bestweights}')
    print(f'ROC score: {best_roc}')

    print('\n=== FASE 3: Modello con iperparametri ottimizzati ===')
    knn = KNeighborsClassifier(n_neighbors=bestNeighbours, 
                              weights=bestweights, 
                              metric=bestMetric,
                              n_jobs=-1)
    knn.fit(X_train, y_train)

    print('\nPredizioni test con modello ottimizzato:')
    print('Predetti:', knn.predict(X_test)[0:5])
    print('Effettivi:', y_test[0:5])

    y_pred = knn.predict(X_test)
    pred_prob = knn.predict_proba(X_test)
    modelEvaluation(y_test, y_pred, pred_prob)

    print('\nModello ottimizzato pronto per le raccomandazioni')
    return knn

def main_recommender():
    print("=== INIZIO SISTEMA DI RACCOMANDAZIONE ===")
    
    print("\nCaricamento dati...")
    steam_data = pd.read_csv('dataset/steam.csv')
    
    print("\nPreparazione dati...")
    # Calcola il rating a stelle basato sul rapporto recensioni negative/positive
    steam_data['star'] = (steam_data['negative_ratings'] / steam_data['positive_ratings']) * 100
    steam_data.loc[(steam_data['star'] >= 0) & (steam_data['star'] <= 12.5), 'star'] = 5
    steam_data.loc[(steam_data['star'] > 12.5) & (steam_data['star'] <= 25), 'star'] = 4
    steam_data.loc[(steam_data['star'] > 25) & (steam_data['star'] <= 37.5), 'star'] = 3
    steam_data.loc[(steam_data['star'] > 37.5) & (steam_data['star'] <= 50), 'star'] = 2
    steam_data.loc[(steam_data['star'] > 50), 'star'] = 1

    steam_data['genres'] = steam_data['steamspy_tags']
    knn_data = steam_data[['appid', 'english', 'achievements', 'star', 'average_playtime', 'median_playtime', 'price']].copy()

    print("\nDivisione dati...")
    x = knn_data.drop(columns=['star'])
    y = knn_data['star'].values
    
    print("\nOttenimento raccomandazioni...")
    
    games_index = get_recommendation()
    recommend_data = steam_data[['name','genres','developer','price', 'star']].iloc[games_index]
    predict_data = steam_data[['appid', 'english', 'achievements','average_playtime','median_playtime', 'price']].iloc[games_index]

    print("\nSplit train-test...")
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=1, stratify=y)

    print("\nNormalizzazione dati...")
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    predict_data = scaler.transform(predict_data)

    print("\nRicerca miglior modello...")
    knn = SearchingBestModelStats(X_train, X_test, y_train, y_test)
    
    if knn is None:
        print("\nErrore: Impossibile creare il modello. Uscita.")
        return

    print("\nPredizione su nuovi dati...")
    predizione_star = knn.predict(predict_data)
    recommend_data['star_prediction'] = predizione_star

    print("\n=== RISULTATI FINALI ===")
    print("\nEcco a te i 5 giochi più simili a quello proposto:")
    print(recommend_data)

if __name__ == '__main__':
    main_recommender()