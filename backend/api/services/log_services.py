import requests


#def debugLog(text):
#    # L'indirizzo del tuo server Django (esposto tramite Docker)
#    url = "http://localhost:8000/createlog/"
#    
#    # I dati devono corrispondere a quanto estratto nella vista (log_text)
#    payload = {'log_text': text}
#    
#    try:
#        # Invi della HttpRequest POST
#        response = requests.post(url, json=payload)
#        
#        if response.status_code == 201:
#            print("Successo: Log inviato e salvato nel DB.")
#        else:
#            print(f"Errore log{response.status_code}: {response.text}")
#            
#    except requests.exceptions.RequestException as e:
#        print(f"Errore di connessione: {e}")
#    
## Esempio di utilizzo
#debugLog("prova")