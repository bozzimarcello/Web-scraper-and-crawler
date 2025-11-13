import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Set per tenere traccia degli URL già visitati ed evitare cicli infiniti
# e crawling duplicati.
VISITED_URLS = set()
MAX_PAGES_TO_CRAWL = 10000  # Limite per evitare un crawling eccessivo

def crawl_page(url, depth=0):
    """
    Esegue lo scraping di una pagina e cerca tutti i link per il crawling.

    Args:
        url (str): L'URL della pagina da visitare.
        depth (int): La profondità del crawling (numero di salti dalla pagina iniziale).
    """
    if url in VISITED_URLS or len(VISITED_URLS) >= MAX_PAGES_TO_CRAWL:
        return
    
    # Aggiunge l'URL al set di quelli visitati
    VISITED_URLS.add(url)
    print(f"[{len(VISITED_URLS)}/{MAX_PAGES_TO_CRAWL}] Crawling: {url} (Profondità: {depth})")

    try:
        # 1. Richiesta HTTP
        response = requests.get(url, timeout=5)
        response.raise_for_status() # Genera un'eccezione per status code di errore (4xx o 5xx)
        
        # 2. Parsing della pagina
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # --- LOGICA DI SCRAPING (Esempio: estrazione del titolo della pagina) ---
        title = soup.title.string if soup.title else "Nessun Titolo Trovato"
        print(f"   [SCRAPING] Titolo della pagina: {title}")
        
        # Se devi estrarre dati specifici (es. prezzi, paragrafi), la logica 
        # va implementata qui utilizzando i selettori CSS o XPath
        # Esempio:
        # product_name = soup.find('h1', class_='product-title').text
        
        # --------------------------------------------------------------------
        
        # 3. Estrazione dei Link (Crawling)
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            
            # Converte i percorsi relativi in URL assoluti
            absolute_url = urljoin(url, href)
            
            # Analizza l'URL assoluto per filtrare i link esterni o non validi
            parsed_root = urlparse(BASE_URL)
            parsed_link = urlparse(absolute_url)
            
            # Filtro: Assicura che il link sia all'interno dello stesso dominio (stesso netloc)
            # ed è un link HTTP/HTTPS
            if parsed_link.scheme in ['http', 'https'] and \
               parsed_link.netloc == parsed_root.netloc:
                
                # Chiama ricorsivamente la funzione per l'URL trovato
                # In questo esempio, il crawling non aumenta la profondità
                # per evitare di esplodere in troppe pagine, ma può essere modificato.
                if len(VISITED_URLS) < MAX_PAGES_TO_CRAWL:
                    crawl_page(absolute_url, depth + 1)
                else:
                    break # Interrompe l'estrazione dei link se è stato raggiunto il limite
                    
    except requests.exceptions.RequestException as e:
        print(f"   [ERRORE] Errore durante il recupero di {url}: {e}")
    except Exception as e:
        print(f"   [ERRORE] Errore generico durante l'elaborazione di {url}: {e}")

# --- Configurazione e Avvio ---

# IMPORTANTE: L'URL iniziale viene caricato dall'ambiente
BASE_URL = os.getenv("BASE_URL")

# Controlla se la variabile BASE_URL è stata caricata correttamente
if not BASE_URL:
    raise ValueError("La variabile d'ambiente BASE_URL non è stata impostata. Creare un file .env o esportarla.")

# Avvia il crawling dalla pagina base
if __name__ == "__main__":
    print(f"Avvio del crawling da: {BASE_URL}")
    print("---------------------------------------")
    
    # Inizia il processo di crawling
    crawl_page(BASE_URL)
    
    print("\n---------------------------------------")
    print(f"Crawling completato. Pagine totali visitate: {len(VISITED_URLS)}")
    # print("URL visitati:", VISITED_URLS) # Decommenta per vedere la lista completa