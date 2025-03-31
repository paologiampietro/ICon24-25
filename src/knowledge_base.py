import pytholog as pl
import pandas as pd

# Funzione per ottenere input sì/no dall'utente
def get_yes_no_input(prompt):
    while True:
        response = input(prompt).strip().lower()
        if response in ['s', 'si', 'sì', 'y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Per favore rispondi con 's'/'sì' o 'n'/'no'")

# Costruisce e pre-elabora il dataframe dai dati Steam
def build_dataframe():
    steam_data = pd.read_csv("dataset/steam.csv")

    # Calcola il rating a stelle basato sul rapporto recensioni negative/positive
    steam_data['star'] = (steam_data['negative_ratings'] / steam_data['positive_ratings']) * 100
    steam_data.loc[(steam_data['star'] >= 0) & (steam_data['star'] <= 12.5), ['star']] = 5
    steam_data.loc[(steam_data['star'] > 12.5) & (steam_data['star'] <= 25), ['star']] = 4
    steam_data.loc[(steam_data['star'] > 25) & (steam_data['star'] <= 37.5), ['star']] = 3
    steam_data.loc[(steam_data['star'] > 37.5) & (steam_data['star'] <= 50), ['star']] = 2
    steam_data.loc[(steam_data['star'] > 50), ['star']] = 1
    steam_data['english'] = steam_data['english'].replace({0: 'no', 1: 'yes'})

    # Seleziona solo le colonne rilevanti
    steam_data = steam_data[['name','developer','publisher','english','star','steamspy_tags','price','average_playtime','genres']].copy()
    return steam_data

# Popola la knowledge base con i dati del dataframe
def populate_kb(dataframe):
    steam_kb = pl.KnowledgeBase('Steam Games')
    kb = []

    # Pulisce e standardizza i dati
    dataframe['name'] = dataframe['name'].str.strip().str.lower()
    dataframe['developer'] = dataframe['developer'].str.strip().str.lower()
    dataframe['publisher'] = dataframe['publisher'].str.strip().str.lower()
    dataframe['steamspy_tags'] = dataframe['steamspy_tags'].str.strip().str.lower()

    # Aggiunge fatti alla knowledge base
    for _, row in dataframe.iterrows():
        kb.append(f"developer({row['name']},{row['developer']})")
        kb.append(f"publisher({row['name']},{row['publisher']})")
        kb.append(f"prices({row['name']},{row['price']})")
        kb.append(f"stars({row['name']},{int(row['star'])})")
        kb.append(f"genre({row['name']},{row['steamspy_tags']})")
        kb.append(f"english({row['name']},{row['english']})")

    # Aggiunge regole alla knowledge base
    kb.append("has_price(X, Y) :- prices(Y, X)")
    kb.append("quality(X, Y) :- stars(Y, X)")
    kb.append("developed_by(X, Y) :- developer(Y, X)")
    kb.append("released_by(X, Y) :- publisher(Y, X)")
    kb.append("is_genre(X, Y) :- genre(Y, X)")
    kb.append("has_english(X, Y) :- english(Y, X)")
    kb.append("quality_check(X, Y, T, Z) :- stars(X, T), stars(Y, Z)")

    steam_kb(kb)
    return steam_kb

# Calcola la probabilità che un gioco piaccia all'utente
def liking_prob(dataframe):
    liking_kb = pl.KnowledgeBase('Liking Probability')
    kb = []

    # Ottiene le preferenze dell'utente
    Gioco_Piaciuto = input("Inserisci il nome del gioco che ti è piaciuto: ").lower()
    genere = input("Dimmi il genere del gioco: ").lower()
    tempo_gioco = int(input("E il tempo di gioco medio al mese: "))
    
    # Aggiunge fatti sulla preferenza dell'utente
    kb.append(f"is_genre({Gioco_Piaciuto}, {genere})")
    kb.append(f"avg_playtime({Gioco_Piaciuto}, {tempo_gioco})")
    kb.append(f"liked_game(utente, {Gioco_Piaciuto})")
    
    # Ottiene informazioni sul nuovo gioco da valutare
    Gioco_Nuovo = input("\nInserisci il nome di un gioco di cui vuoi calcolare la probabilità che ti piaccia: ").lower()
    genere_n = input("Dimmi il genere del gioco: ").lower()
    tempo_gioco_n = int(input("E il tempo di gioco medio al mese: "))
    
    kb.append(f"is_genre({Gioco_Nuovo}, {genere_n})")
    kb.append(f"avg_playtime({Gioco_Nuovo}, {tempo_gioco_n})")

    # Ottiene informazioni sullo stile di vita dell'utente
    Orario = int(input("\nQuante ore lavori/studi al giorno? "))
    kb.append(f"has_work(utente, {Orario})")
    kb.append(f"stress(utente, {Orario})")

    # Aggiunge regole per la similarità tra generi
    for genre in set(dataframe['genres']):
        kb.append(f"same_genre({genre.lower()}, {genre.lower()})")

    # Aggiunge regole per il calcolo della probabilità
    kb.append("has_avg_playtime(X, Y) :- avg_playtime(X, Y)")
    kb.append("avg_playtime_comp(Gioco1, Gioco2, Y) :- liked_game(utente, Gioco1), has_avg_playtime(Gioco1, Avg1), has_avg_playtime(Gioco2, Avg2), Y is Avg1 - Avg2")
    kb.append("has_same_genre(Gioco1, Gioco2) :- is_genre(Gioco1, X), is_genre(Gioco2, Y), same_genre(X, Y)")
    kb.append("compatibility(Num1, Num2, S1) :- S1 is Num1 + Num2")
    kb.append("to_like(utente, Num1, Num2, Prob) :- stress(utente, P1), compatibility(Num1, Num2, S1), Prob is P1 + S1")

    liking_kb(kb)

    # Calcola la similarità nel tempo di gioco
    result = liking_kb.query(pl.Expr(f"avg_playtime_comp({Gioco_Piaciuto}, {Gioco_Nuovo}, What)"))
    if result and isinstance(result[0], dict) and 'What' in result[0]:
        try:
            Playtime_Similarity = float(result[0]['What'])
        except ValueError:
            Playtime_Similarity = 0
    else:
        Playtime_Similarity = 0
    Playtime_Similarity = assign_range(Playtime_Similarity)

    # Verifica la similarità di genere
    result = liking_kb.query(pl.Expr(f"has_same_genre({Gioco_Piaciuto}, {Gioco_Nuovo})"))
    if result and isinstance(result, list) and len(result) > 0:
        Genre_Similarity = 2.5 if result[0] == 'Yes' else -2.5
    else:
        Genre_Similarity = -2.5

    # Calcola la probabilità finale
    result = liking_kb.query(pl.Expr(f"to_like(utente, {Playtime_Similarity}, {Genre_Similarity}, What)"))
    if result and isinstance(result[0], dict):
        key = list(result[0].keys())[0]
        try:
            p = float(result[0][key])
        except ValueError:
            p = 0
    else:
        p = 0

    p = max(0, min(100, p))
    print("\nLa probabilità che", Gioco_Nuovo, "ti possa piacere è:", p, "%")

# Assegna un punteggio in base alla differenza nel tempo di gioco
def assign_range(num):
    num = abs(int(num))
    ranges = [
        (0, 100, 100),
        (101, 250, 90),
        (251, 500, 80),
        (501, 750, 70),
        (751, 1000, 60),
        (1001, 1250, 50),
        (1251, 1500, 40),
        (1501, 1750, 30),
        (1751, 2000, 20),
        (2001, 2500, 10),
        (2501, 10000, 5),
        (10001, float('inf'), 0)
    ]
    for min_val, max_val, score in ranges:
        if min_val <= num <= max_val:
            return score
    return 0

# Funzione principale della knowledge base
def main_kb():
    dataframe = build_dataframe()
    kb = populate_kb(dataframe)

    print("\nKNOWLEDGE BASE\n")
    print("Benvenuto, qui puoi eseguire ricerche sui giochi e sulle loro caratteristiche")

    while True:
        print("\nEcco le ricerche che puoi eseguire:")
        print("1) Ricerche sulle caratteristiche di un gioco")
        print("2) Confronti e ricerca di giochi in base ad una caratteristica")
        print("3) Verificare delle caratteristiche")
        print("4) Vedere con quale probabilità ti possa piacere un nuovo gioco")
        print("5) Exit Knowledge Base")
        choice1 = input("\nQuale scegli (inserisci il numero corrispondente alla tua scelta)? ")

        try:
            c1 = int(choice1)
        except ValueError:
            print("Inserisci un numero valido!")
            continue

        # Menu principale
        if c1 == 1:
            while True:
                game_name = input("\nDammi il nome di un gioco: ").strip().lower()
                
                # Verifica se il gioco esiste
                game_exists = dataframe['name'].str.lower().isin([game_name]).any()
                if not game_exists:
                    print(f"\nIl gioco '{game_name}' non è stato trovato nel dataset. Riprova.")
                    continue
                    
                print("\nQueste sono le caratteristiche che puoi cercare:")
                print("1) Chi lo ha sviluppato")
                print("2) Chi lo ha distribuito")
                print("3) Quanto costa")
                print("4) Quante stelle ha (su una scala da 1 a 5)")
                print("5) Di che genere è")
                print("6) Se è disponibile in lingua inglese")
                print("7) Torna indietro")
                choice2 = input("\nSelezionane una: ")

                try:
                    c2 = int(choice2)
                except ValueError:
                    print("Inserisci un numero valido!")
                    continue

                if c2 == 7:
                    break

                try:
                    if c2 == 1:
                        result = kb.query(pl.Expr(f"developed_by(What,{game_name})"))
                        if result:
                            print(f"\n{game_name} è stato sviluppato da: {result[0]['What']}")
                        else:
                            print(f"\nNessuno sviluppatore trovato per il gioco {game_name}")
                    
                    elif c2 == 2:
                        result = kb.query(pl.Expr(f"released_by(What,{game_name})"))
                        if result:
                            print(f"\n{game_name} è stato rilasciato da: {result[0]['What']}")
                        else:
                            print(f"\nNessun publisher trovato per il gioco {game_name}")
                    
                    elif c2 == 3:
                        result = kb.query(pl.Expr(f"has_price(What,{game_name})"))
                        if result:
                            print(f"\n{game_name} costa: {result[0]['What']}")
                        else:
                            print(f"\nNessun prezzo trovato per il gioco {game_name}")
                    
                    elif c2 == 4:
                        result = kb.query(pl.Expr(f"quality(What,{game_name})"))
                        if result:
                            print(f"\n{game_name} ha: {result[0]['What']} stelle")
                        else:
                            print(f"\nNessun rating trovato per il gioco {game_name}")
                    
                    elif c2 == 5:
                        result = kb.query(pl.Expr(f"is_genre(What,{game_name})"))
                        if result:
                            print(f"\nIl genere di {game_name} è: {result[0]['What']}")
                        else:
                            print(f"\nNessun genere trovato per il gioco {game_name}")
                    
                    elif c2 == 6:
                        result = kb.query(pl.Expr(f"has_english(What,{game_name})"))
                        if result:
                            status = "disponibile" if result[0]['What'] == 'yes' else "non disponibile"
                            print(f"\n{game_name} è {status} in lingua inglese")
                        else:
                            print(f"\nNessuna informazione sulla lingua inglese per il gioco {game_name}")
                
                except Exception as e:
                    print(f"\nSi è verificato un errore: {str(e)}")

                if not get_yes_no_input("\nVuoi eseguire un'altra ricerca? (s/n): "):
                    break

        elif c1 == 2:
            while True:
                print("\nQueste sono ricerche che puoi eseguire sulle caratteristiche:")
                print("1) Lista di giochi di un prezzo")
                print("2) Confronto di qualità tra 2 giochi")
                print("3) Indietro")
                choice3 = input("\nSelezionane una: ")

                try:
                    c3 = int(choice3)
                except ValueError:
                    print("Inserisci un numero valido!")
                    continue

                if c3 == 1:
                    try:
                        prezzo = float(input("\nInserisci un prezzo: "))
                        result = kb.query(pl.Expr(f"has_price({prezzo},What)"))
                        if result:
                            print(f"\nEcco la lista dei primi 10 giochi con prezzo {prezzo}:")
                            for i, r in enumerate(result[:100], 1):
                                print(f"{i}) {r[f'{prezzo}']}")
                        else:
                            print("\nNessun gioco trovato con questo prezzo")
                    except ValueError:
                        print("Inserisci un prezzo valido!")

                elif c3 == 2:
                    game1 = input("\nDimmi il nome del primo gioco: ").strip().lower()
                    game2 = input("Dimmi il nome del secondo gioco: ").strip().lower()
                    try:
                        result = kb.query(pl.Expr(f"quality_check({game1}, {game2}, X, Y)"))
                        if result:
                            star1 = result[0]['X']
                            star2 = result[0]['Y']
                            if star1 > star2:
                                print(f"\nIl gioco migliore è: {game1} ({star1} stelle) rispetto a {game2} ({star2} stelle)")
                            elif star1 < star2:
                                print(f"\nIl gioco migliore è: {game2} ({star2} stelle) rispetto a {game1} ({star1} stelle)")
                            else:
                                print(f"\nI due giochi hanno la stessa qualità: {star1} stelle")
                        else:
                            print("\nImpossibile confrontare i giochi specificati")
                    except Exception as e:
                        print(f"\nErrore nel confronto: {str(e)}")

                elif c3 == 3:
                    break

        elif c1 == 3:
            while True:
                print("\nQuesti sono le caratteristiche che puoi verificare:")
                print("1) developer\n2) publisher\n3) prices\n4) stars\n5) genre\n6) english\n7) Indietro")
                fatto = input("\nSelezionane una: ").strip().lower()
                
                if fatto == '7':
                    break

                name = input("\nQuale gioco vuoi controllare? ").strip().lower()
                
                try:
                    game_data = dataframe[dataframe['name'].str.lower() == name]
                    if game_data.empty:
                        print("\nGioco non trovato!")
                        continue
                    
                    if fatto == '5':  
                        user_genre = input("Inserisci il genere da verificare: ").strip().lower()
                        game_genres = game_data['steamspy_tags'].iloc[0].lower().split(';')
                        print("\nRisultato:", "Sì" if user_genre in game_genres else "No")
                    elif fatto == '6':  
                        eng_value = game_data['english'].iloc[0]
                        eng_status = 'yes' if eng_value == 1 or str(eng_value).lower() == 'yes' else 'no'
                        print("\nRisultato:", "Sì" if eng_status == 'yes' else "No")
                    else:
                        char = input("Inserisci un dato corrispondente alla caratteristica scelta: ").strip().lower()
                        result = False
                        if fatto == '1':  
                            result = game_data['developer'].iloc[0].lower() == char.lower()
                        elif fatto == '2':  
                            result = game_data['publisher'].iloc[0].lower() == char.lower()
                        elif fatto == '3':  
                            result = float(game_data['price'].iloc[0]) == float(char)
                        elif fatto == '4':  
                            result = int(game_data['star'].iloc[0]) == int(char)
                        
                        print("\nRisultato:", "Sì" if result else "No")
                        
                except Exception as e:
                    print(f"\nErrore nella verifica: {str(e)}")

                if not get_yes_no_input("\nVuoi eseguire un'altra verifica? (s/n): "):
                    break

        elif c1 == 4:
            while True:
                try:
                    liking_prob(dataframe)
                except Exception as e:
                    print(f"\nErrore nel calcolo della probabilità: {str(e)}")
                
                if not get_yes_no_input("\nVuoi controllare un'altra probabilità? (s/n): "):
                    break

        elif c1 == 5:
            print("\nGrazie per aver usato la Knowledge Base. Arrivederci!")
            break

        else:
            print("\nScelta non valida. Riprova.")

if __name__ == "__main__":
    main_kb()