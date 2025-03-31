from owlready2 import *

# Funzione principale per l'esplorazione dell'ontologia Steam
def main_ontology():
    print("\nBENVENUTO NELLA STEAM-ONTOLOGY\n")
    while True:
        # Menu principale
        print("Seleziona cosa vorresti esplorare:\n\n1) Visualizzazione Classi\n2) Visualizzazione proprietà d'oggetto\n3) Visualizzazione proprietà dei dati\n4) Visualizzazione query d'esempio\n5) Exit Ontologia\n")

        risposta_menù = input("Inserisci qui la tua scelta:\t")

        # Caricamento dell'ontologia
        ontology = get_ontology('dataset/Steam-Ontology.owl').load()

        # Visualizzazione delle classi
        if risposta_menù == '1':
            print("\nClassi presenti nell'ontologia:\n")
            print(list(ontology.classes()))

            # Sottomenu per l'esplorazione delle classi specifiche
            while True:
                print("\nVorresti esplorare meglio qualche classe in particolare?\n\n1) Agent\n2) Game\n3) Developer\n4) Genre\n5) Platform\n6) Publisher\n7) Costumer\n8) Shop\n")
                risposta_class = input("Inserisci qui la tua scelta:\t")

                # Visualizzazione degli agenti
                if risposta_class == '1':
                    print("\nLista di Agenti presenti:\n")
                    agents = ontology.search(is_a = ontology.Agent)
                    print(agents)
                # Visualizzazione dei giochi
                elif risposta_class == '2':
                    print("\nLista dei Giochi presenti:\n")
                    games = ontology.search(is_a = ontology.Game)
                    print(games)
                # Visualizzazione degli sviluppatori
                elif risposta_class == '3':
                    print("\nLista degli Sviluppatori presenti:\n")
                    developers = ontology.search(is_a = ontology.Developer)
                    print(developers)
                # Visualizzazione dei generi
                elif risposta_class == '4':
                    print("\nLista delle Categorie presenti:\n")
                    genres = ontology.search(is_a = ontology.Genre)
                    print(genres)
                # Visualizzazione delle piattaforme
                elif risposta_class == '5':
                    print("\nLista delle Piattaforme presenti:\n")
                    platforms = ontology.search(is_a = ontology.Platform)
                    print(platforms)
                # Visualizzazione dei publisher
                elif risposta_class == '6':
                    print("\nLista delle Case Pubblicatrici presenti:\n")
                    publishers = ontology.search(is_a = ontology.Publisher)
                    print(publishers)
                # Visualizzazione dei clienti
                elif risposta_class == '7':
                    print("\nLista dei Clienti presenti:\n")
                    costumers = ontology.search(is_a = ontology.Costumer)
                    print(costumers)
                # Visualizzazione dei negozi
                elif risposta_class == '8':
                    print("\nLista dei Negozi presenti:\n")
                    shops = ontology.search(is_a = ontology.Shop)
                    print(shops)
                else:
                    print("\nInserisci il numero correttamente tra quelli presentati")
                    continue  

                # Gestione della navigazione
                while True:
                    print("\nVorresti tornare indietro o continuare?\tIndietro (si) Continua (no)")
                    risp = input("\n").strip().lower()  
                    if risp in ('si', 'no'):
                        break
                    else:
                        print("\nPer favore, inserisci 'si' o 'no'.")

                if risp == 'si':
                    break

        # Visualizzazione delle proprietà d'oggetto
        elif risposta_menù == '2':
            print("\nProprietà d'oggetto presenti nell'ontologia:\n")
            print(list(ontology.object_properties()), "\n")
        
        # Visualizzazione delle proprietà dei dati
        elif risposta_menù == '3':
            print("\nProprietà dei dati presenti nell'ontologia:\n")
            print(list(ontology.data_properties()), "\n")
        
        # Visualizzazione delle query d'esempio
        elif risposta_menù == '4':
            print("\nQuery d'esempio:")
            # Query per giochi con genere 'Classic'
            print("\n-Lista di Giochi che presentano la categoria 'Classic':\n")
            games = ontology.search(is_a = ontology.Game, has_genre = ontology.search(is_a = ontology.Classic))
            print(games, "\n")
            # Query per giochi sviluppati da 'Valve'
            print("\n-Lista di Giochi che presentano lo sviluppatore 'Valve':\n")
            games = ontology.search(is_a = ontology.Game, has_developer = ontology.search(is_a = ontology.Valve))
            print(games, "\n")
            # Query per giochi disponibili su 'Windows'
            print("\n-Lista di Giochi che presentano la piattaforma 'Windows':\n")
            games = ontology.search(is_a = ontology.Game, has_platform = ontology.search(is_a = ontology.Windows))
            print(games, "\n")
        
        # Uscita dall'ontologia
        elif risposta_menù == '5':
            break
        
        # Gestione input non valido
        else:
            print("\nInserisci un numero valido tra 1 e 5.")

if __name__ == "__main__":
    main_ontology()