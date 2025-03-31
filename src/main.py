# Importazione dei moduli necessari dalle diverse cartelle del progetto
from ontology import main_ontology
from classification_validation import main_recommender
from knowledge_base import main_kb
from budget_planner import main_budget

def avvio():
    # Funzione principale che gestisce il menu interattivo dell'applicazione.
    print("BENVENUTO\n")

    while True:
        # Stampa le opzioni disponibili per l'utente
        print("Scegli una tra le seguenti opzioni:\n\n1) Recommender System\n2) Knowledge Base\n3) Ontologia\n4) Budget Planner\n5) Exit\n\nInserisci qui:\t")
        
        # Legge l'input dell'utente
        risposta = input()
        
        # Gestisce la scelta dell'utente
        if risposta == '1':
            main_recommender()  # Avvia il sistema di raccomandazione
        elif risposta == '2':
            main_kb()  # Avvia la knowledge base
        elif risposta == '3':
            main_ontology()  # Avvia l'ontologia
        elif risposta == '4': 
            main_budget()  # Avvia il budget planner
        elif risposta == '5':
            print("\nArrivederci!")
            break  # Termina il programma
        else:
            print("Inserisci correttamente il numero")
            continue  # Richiede un nuovo input se la scelta non è valida
        
        # Loop per chiedere all'utente se vuole continuare o terminare
        while True:
            print("\nVuoi terminare o continuare?\tTermina (si) Continua (no)\n")
            risposta2 = input().strip().lower()
            
            if risposta2 == 'si':
                print("\nArrivederci!")
                return  # Termina la funzione avvio() e quindi il programma
            elif risposta2 == 'no':
                break  # Torna al menu principale
            else:
                print("Per favore, inserisci 'si' o 'no'.")  # Richiede un input valido

# Punto di ingresso del programma
if __name__ == '__main__':
    avvio()  # Avvia l'applicazione