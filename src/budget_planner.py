import pandas as pd
from typing import List, Dict

class SteamBudgetPlanner:
    def __init__(self, data_path: str = "dataset/steam.csv"):
        # Inizializza il pianificatore di budget con il percorso del dataset.
        self.df = self._load_and_preprocess_data(data_path)
    
    def _load_and_preprocess_data(self, path: str) -> pd.DataFrame:
        # Carica i dati da un file CSV e li pre-elabora.
        # Carica il dataset
        df = pd.read_csv(path, delimiter=',')
        
        # Converte la colonna 'price' in numerico, sostituisce i valori non validi con 0
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
        
        # Calcola il rating a stelle (1-5) basato sulle recensioni positive/negative
        df['star'] = (df['positive_ratings'] / (df['positive_ratings'] + df['negative_ratings'])) * 5
        df['star'] = df['star'].round(1)  # Arrotonda a 1 decimale
        
        # Mantiene solo le colonne rilevanti
        return df[['name', 'price', 'star', 'genres', 'average_playtime']].copy()

    def recommend(
        self, 
        budget: float, 
        min_rating: float = 3.5, 
        genre: str = None,
        max_playtime: int = None
    ) -> List[Dict]:
        # Raccomanda giochi in base al budget e alle preferenze dell'utente.
        # Filtra i giochi con prezzo valido, nel budget e con rating sufficiente
        filtered = self.df[
            (self.df['price'] > 0) & 
            (self.df['price'] <= budget) & 
            (self.df['star'] >= min_rating)
        ]
        
        # Filtra ulteriormente per genere se specificato
        if genre:
            filtered = filtered[filtered['genres'].str.contains(genre, case=False)]
        
        # Filtra per tempo di gioco massimo se specificato
        if max_playtime:
            filtered = filtered[filtered['average_playtime'] <= max_playtime]
        
        # Ordina per prezzo (dal più alto al più basso) e restituisce i primi 10 risultati
        filtered = filtered.sort_values('price', ascending=False)
        return filtered.head(10).to_dict('records')

    def interactive_planner(self):
        # Interfaccia interattiva per l'utente per inserire le preferenze e visualizzare le raccomandazioni.
        print("\n🎮 Steam Budget Planner")
        print("---------------------")
        
        # Richiede input all'utente
        budget = float(input("Inserisci il tuo budget (€): "))
        min_rating = float(input("Rating minimo (1-5, default 3.5): ") or 3.5)
        genre = input("Genere preferito (opzionale, premi Invio per saltare): ")
        max_playtime = input("Tempo di gioco massimo in ore (opzionale): ")
        
        # Ottiene le raccomandazioni basate sugli input
        recommendations = self.recommend(
            budget=budget,
            min_rating=min_rating,
            genre=genre if genre else None,
            max_playtime=int(max_playtime) if max_playtime else None
        )
        
        # Stampa i risultati
        print("\n🔥 Migliori acquisti per te:")
        for i, game in enumerate(recommendations, 1):
            print(f"{i}. {game['name']} - €{game['price']:.2f}")
            print(f"   ⭐ {game['star']}/5 | 🕒 {game['average_playtime']}h")
            print(f"   🏷️ {game['genres']}\n")

def main_budget():
    # Funzione principale per avviare il pianificatore di budget.
    print("=== INIZIO PIANIFICATORE BUDGET STEAM ===")
    planner = SteamBudgetPlanner()
    planner.interactive_planner()

if __name__ == "__main__":
    main_budget()