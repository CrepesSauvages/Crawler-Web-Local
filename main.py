import tkinter as tk
from tkinter import ttk, messagebox
import threading
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
            file.flush()  # Force l'écriture immédiate sur le disque
            os.fsync(file.fileno())  # Synchronisation avec le disque pour s'assurer que toutes les données sont écrites
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
        info = extract_info(url)
        if info:
            metadata['count'] += 1
            index = str(metadata['count'])
            webpages[index] = info
            visited.append(url)

            # Ajouter des messages de débogage pour afficher l'URL traitée
            print(f"Traitement de l'URL: {url}")

            # Sauvegarder les données et vérifier si un nouveau fichier info doit être créé
            if metadata['count'] % 50 == 0:
                save_json_file(current_info_file, webpages)
                metadata['file_index'] += 1
                current_info_file = get_current_info_file()
                webpages.clear()
            
            save_json_file(current_info_file, webpages)
            save_json_file('data/metadata.json', metadata)
            save_json_file('data/visited.json', visited)
            
            base_url = url.rsplit('/', 1)[0]
            for link in info['links']:
                absolute_link = urljoin(base_url, link)
                if is_valid_url(absolute_link) and absolute_link not in visited and absolute_link not in queue:
                    queue.append(absolute_link)
                    print(f"Ajouté à la file d'attente: {absolute_link}")
                    
            save_json_file('data/queue.json', queue)

# Vérifier si l'URL est valide
def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)

# Fonction pour démarrer le crawling
def crawler(start_url=None):
    if start_url:
        queue.append(start_url)
    while queue:
        url = queue.pop(0)
        process_url(url)
        save_json_file('data/queue.json', queue)

# Interface graphique avec Tkinter
class CrawlerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Crawler")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.start_url_label = ttk.Label(frame, text="URL de départ:")
        self.start_url_label.grid(row=0, column=0, sticky=tk.W)

        self.start_url_entry = ttk.Entry(frame, width=50)
        self.start_url_entry.grid(row=0, column=1, padx=5, pady=5)

        self.new_crawl_button = ttk.Button(frame, text="Nouveau Crawler", command=self.start_new_crawler)
        self.new_crawl_button.grid(row=0, column=2, padx=5, pady=5)

        self.continue_crawl_button = ttk.Button(frame, text="Continuer Crawler", command=self.continue_crawler)
        self.continue_crawl_button.grid(row=1, column=2, padx=5, pady=5)

        self.view_queue_button = ttk.Button(frame, text="File d'attente (Voir nombre)", command=self.view_queue_count)
        self.view_queue_button.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.view_queue_urls_button = ttk.Button(frame, text="File d'attente (Voir URLs)", command=self.view_queue_urls)
        self.view_queue_urls_button.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        self.count_button = ttk.Button(frame, text="Nombre de pages web enregistrées", command=self.count_webpages)
        self.count_button.grid(row=2, column=2, padx=5, pady=5)

        self.search_label = ttk.Label(frame, text="Rechercher une page web:")
        self.search_label.grid(row=3, column=0, sticky=tk.W)

        self.search_entry = ttk.Entry(frame, width=50)
        self.search_entry.grid(row=3, column=1, padx=5, pady=5)

        self.search_button = ttk.Button(frame, text="Rechercher", command=self.search_webpage)
        self.search_button.grid(row=3, column=2, padx=5, pady=5)

        self.clean_data_button = ttk.Button(frame, text="Nettoyer les données", command=self.clean_data)
        self.clean_data_button.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

        self.clean_messagebox_button = ttk.Button(frame, text="Nettoyer la messagebox", command=self.clean_messagebox)
        self.clean_messagebox_button.grid(row=4, column=1, padx=5, pady=5)

        self.quit_button = ttk.Button(frame, text="Quitter", command=self.root.quit)
        self.quit_button.grid(row=4, column=2, padx=5, pady=5)

        self.log_text = tk.Text(self.root, height=10, width=80)
        self.log_text.grid(row=1, column=0, padx=10, pady=10, columnspan=3, sticky=(tk.W, tk.E))

    def start_new_crawler(self):
        start_url = self.start_url_entry.get()
        if start_url:
            threading.Thread(target=crawler, args=(start_url,), daemon=True).start()
            self.log_text.insert(tk.END, f"Web Crawler démarré pour l'URL: {start_url}\n")

    def continue_crawler(self):
        if queue:
            threading.Thread(target=crawler, daemon=True).start()
            self.log_text.insert(tk.END, "Continuation du Web Crawler avec les URLs dans la file d'attente.\n")
        else:
            self.log_text.insert(tk.END, "La file d'attente est vide. Veuillez démarrer un nouveau crawler.\n")

    def view_queue_count(self):
        self.log_text.insert(tk.END, f"Nombre d'URLs dans la file d'attente: {len(queue)}\n")

    def view_queue_urls(self):
        self.log_text.insert(tk.END, "URLs dans la file d'attente:\n")
        for url in queue:
            self.log_text.insert(tk.END, f"{url}\n")

    def count_webpages(self):
        self.log_text.insert(tk.END, f"Nombre de pages web enregistrées: {metadata['count']}\n")

    def search_webpage(self):
        search_term = self.search_entry.get()
        found = False
        for index, info in webpages.items():
            if search_term in info['url']:
                self.log_text.insert(tk.END, f"Trouvé: {info['url']}\n")
                found = True
                break
        if not found:
            self.log_text.insert(tk.END, "Aucune page web trouvée avec ce terme de recherche.\n")

    def clean_data(self):
        global queue, visited, metadata, webpages, current_info_file
        queue = []
        visited = []
        metadata = {"count": 0, "file_index": 1}
        webpages = {}
        current_info_file = get_current_info_file()
        save_json_file('data/queue.json', queue)
        save_json_file('data/visited.json', visited)
        save_json_file('data/metadata.json', metadata)
        save_json_file(current_info_file, webpages)
        self.log_text.insert(tk.END, "Toutes les données ont été nettoyées.\n")

    def clean_messagebox(self):
        self.log_text.delete('1.0', tk.END)

def main():
    root = tk.Tk()
    app = CrawlerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
