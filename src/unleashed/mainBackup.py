import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin, urlparse

# Créer le dossier data et sous-dossier webpages s'ils n'existent pas
if not os.path.exists('data'):
    os.makedirs('data')
if not os.path.exists('data/webpages'):
    os.makedirs('data/webpages')

# Initialiser les fichiers JSON s'ils n'existent pas
def initialize_json_file(filename, initial_data):
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            json.dump(initial_data, file)

initialize_json_file('data/queue.json', [])
initialize_json_file('data/visited.json', [])
initialize_json_file('data/metadata.json', {"count": 0, "file_index": 1})
initialize_json_file('data/webpages/info1.json', {})

# Charger les données depuis les fichiers JSON
def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON dans le fichier {filename}: {e}")
        return None
    except Exception as e:
        print(f"Erreur lors du chargement du fichier {filename}: {e}")
        return None

def save_json_file(filename, data):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier {filename}: {e}")

queue = load_json_file('data/queue.json') or []
visited = load_json_file('data/visited.json') or []
metadata = load_json_file('data/metadata.json') or {"count": 0, "file_index": 1}

# Déterminer le nom du fichier info.json courant
def get_current_info_file():
    return f"data/webpages/info{metadata['file_index']}.json"

current_info_file = get_current_info_file()
webpages = load_json_file(current_info_file) or {}

# Fonction pour extraire les informations d'une page web
def extract_info(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extraire les titres, sous-titres, texte, et liens
        titles = [title.get_text() for title in soup.find_all(['h1', 'h2', 'h3'])]
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        links = [a['href'] for a in soup.find_all('a', href=True)]

        return {
            'url': url,
            'titles': titles,
            'paragraphs': paragraphs,
            'links': links
        }
    except Exception as e:
        print(f"Erreur lors de l'extraction de {url}: {e}")
        return None

# Fonction pour traiter une URL
def process_url(url):
    global current_info_file
    if url not in visited:
        print(f"Traitement de {url}")
        info = extract_info(url)
        if info:
            metadata['count'] += 1
            index = str(metadata['count'])
            webpages[index] = info
            visited.append(url)

            # Sauvegarder les données et vérifier si un nouveau fichier info doit être créé
            if metadata['count'] % 50 == 0:
                save_json_file(current_info_file, webpages)
                metadata['file_index'] += 1
                current_info_file = get_current_info_file()
                webpages.clear()
            
            save_json_file(current_info_file, webpages)
            save_json_file('data/metadata.json', metadata)
            save_json_file('data/visited.json', visited)
            
            for link in info['links']:
                absolute_link = urljoin(url, link)
                if is_valid_url(absolute_link) and absolute_link not in visited and absolute_link not in queue:
                    queue.append(absolute_link)

# Vérifier si l'URL est valide
def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)

# Fonction pour visualiser la file d'attente
def view_queue():
    print("File d'attente:", queue)

# Fonction pour connaître le nombre de pages web enregistrées
def count_webpages():
    print("Nombre de pages web enregistrées:", metadata['count'])

# Fonction pour rechercher une page web dans la base de données
def search_webpage(url):
    for i in range(1, metadata['file_index'] + 1):
        info_file = f"data/webpages/info{i}.json"
        data = load_json_file(info_file) or {}
        for key, value in data.items():
            if value['url'] == url:
                print(f"Page trouvée dans {info_file}: {value}")
                return
    print("Page non trouvée.")

# Fonction principale du crawler
def crawler(start_url=None):
    if start_url and is_valid_url(start_url) and start_url not in visited and start_url not in queue:
        queue.append(start_url)
    
    while queue:
        current_url = queue.pop(0)
        process_url(current_url)
        save_json_file('data/queue.json', queue)

    print("Crawling terminé.")

# Menu pour les actions de l'utilisateur
def menu():
    while True:
        print("\nActions disponibles:")
        print("1. Démarrer le crawler")
        print("2. Visualiser la file d'attente")
        print("3. Connaître le nombre de pages web enregistrées")
        print("4. Rechercher une page web dans la base de données")
        print("5. Quitter")
        
        choice = input("Choisissez une action (1-5): ")
        
        if choice == '1':
            start_url = input("Entrez l'URL de départ: ")
            crawler(start_url)
        elif choice == '2':
            view_queue()
        elif choice == '3':
            count_webpages()
        elif choice == '4':
            url = input("Entrez l'URL à rechercher: ")
            search_webpage(url)
        elif choice == '5':
            print("Au revoir!")
            break
        else:
            print("Choix invalide, veuillez réessayer.")

# Lancer le menu
menu()
