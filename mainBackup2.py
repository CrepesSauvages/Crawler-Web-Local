import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urljoin, urlparse



from plugins.emails_plugins import *

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

# Fonction pour extraire les emails d'une page web
def extract_emails(soup):
    emails = set()
    # Utiliser une expression régulière pour trouver les emails
    email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    for text in soup.stripped_strings:
        for match in email_regex.findall(text):
            emails.add(match)
    return emails

# Fonction pour extraire les informations d'une page web
def extract_info(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extraire les titres, sous-titres, texte, liens, et emails
        titles = [title.get_text() for title in soup.find_all(['h1', 'h2', 'h3'])]
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        links = [a['href'] for a in soup.find_all('a', href=True)]
        emails = extract_emails(soup)

        return {
            'url': url,
            'titles': titles,
            'paragraphs': paragraphs,
            'links': links,
            'emails': list(emails)
        }
    except Exception as e:
        print(f"Erreur lors de l'extraction de {url}: {e}")
        return None

# Fonction pour sauvegarder les emails dans un fichier texte
def save_emails(emails):
    try:
        with open('data/emails.txt', 'a') as file:
            for email in emails:
                file.write(email + '\n')
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des emails: {e}")

# Fonction pour chercher et collecter les emails dans les fichiers JSON
def search_emails_in_json():
    try:
        emails = set()
        for filename in os.listdir('data/webpages'):
            if filename.endswith('.json'):
                filepath = os.path.join('data/webpages', filename)
                with open(filepath, 'r') as file:
                    data = json.load(file)
                    for info in data.values():
                        if 'emails' in info:
                            emails.update(info['emails'])
        return list(emails)
    except Exception as e:
        print(f"Erreur lors de la recherche des emails dans les fichiers JSON: {e}")
        return []

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

        self.num_crawlers_label = ttk.Label(frame, text="Nombre de crawlers:")
        self.num_crawlers_label.grid(row=0, column=2, sticky=tk.W)

        self.num_crawlers_entry = ttk.Entry(frame, width=5)
        self.num_crawlers_entry.grid(row=0, column=3, padx=5, pady=5)

        self.new_crawl_button = ttk.Button(frame, text="Nouveau Crawler", command=self.start_new_crawler)
        self.new_crawl_button.grid(row=0, column=4, padx=5, pady=5)

        self.continue_crawl_button = ttk.Button(frame, text="Continuer Crawler", command=self.continue_crawler)
        self.continue_crawl_button.grid(row=1, column=4, padx=5, pady=5)

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

        self.extract_emails_button = ttk.Button(frame, text="Extraire les emails", command=self.extract_emails)
        self.extract_emails_button.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

        self.save_emails_button = ttk.Button(frame, text="Sauvegarder les emails", command=self.save_extracted_emails)
        self.save_emails_button.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        self.search_emails_button = ttk.Button(frame, text="Rechercher les emails dans les fichiers JSON", command=self.search_emails)
        self.search_emails_button.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)

        self.clean_data_button = ttk.Button(frame, text="Nettoyer les données de crawl", command=self.clean_crawl_data)
        self.clean_data_button.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)

        self.log_text = tk.Text(self.root, height=10, width=100)
        self.log_text.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_text.insert(tk.END, "Bienvenue dans l'application Web Crawler!\n")

    def start_new_crawler(self):
        start_url = self.start_url_entry.get()
        num_crawlers = int(self.num_crawlers_entry.get()) if self.num_crawlers_entry.get().isdigit() else 1
        if start_url:
            for _ in range(num_crawlers):
                threading.Thread(target=crawler, args=(start_url,)).start()
                self.log_text.insert(tk.END, f"Démarrage du crawler pour {start_url}\n")

    def continue_crawler(self):
        threading.Thread(target=crawler).start()
        self.log_text.insert(tk.END, "Continuation du crawler...\n")

    def view_queue_count(self):
        count = len(queue)
        messagebox.showinfo("File d'attente", f"Il y a {count} URLs dans la file d'attente.")

    def view_queue_urls(self):
        queue_urls = "\n".join(queue)
        messagebox.showinfo("File d'attente - URLs", f"Liste des URLs dans la file d'attente:\n{queue_urls}")

    def count_webpages(self):
        count = metadata['count']
        messagebox.showinfo("Nombre de pages web enregistrées", f"Nombre de pages web enregistrées: {count}")

    def search_webpage(self):
        search_url = self.search_entry.get()
        if search_url:
            if search_url in webpages:
                messagebox.showinfo("Résultat de la recherche", f"URL trouvée dans les données de crawl:\n{search_url}")
            else:
                messagebox.showinfo("Résultat de la recherche", f"URL non trouvée dans les données de crawl:\n{search_url}")
        else:
            messagebox.showerror("Erreur", "Veuillez entrer une URL à rechercher.")

    def extract_emails(self):
        global webpages
        extracted_emails = set()
        for info in webpages.values():
            if 'emails' in info:
                extracted_emails.update(info['emails'])
        messagebox.showinfo("Emails Extraits", f"Liste des emails extraits:\n{', '.join(extracted_emails)}")

    def save_extracted_emails(self):
        global webpages
        extracted_emails = set()
        for info in webpages.values():
            if 'emails' in info:
                extracted_emails.update(info['emails'])
        try:
            with open('data/extracted_emails.txt', 'w') as file:
                file.write('\n'.join(extracted_emails))
            messagebox.showinfo("Sauvegarde des Emails", "Les emails extraits ont été sauvegardés dans extracted_emails.txt.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde des emails: {e}")

    def search_emails(self):
        extracted_emails = search_emails_in_json()
        messagebox.showinfo("Recherche des Emails dans les JSON", f"Liste des emails trouvés dans les fichiers JSON:\n{', '.join(extracted_emails)}")

    def clean_crawl_data(self):
        global queue, visited, metadata, webpages
        queue = []
        visited = []
        metadata = {"count": 0, "file_index": 1}
        webpages = {}
        save_json_file('data/queue.json', queue)
        save_json_file('data/visited.json', visited)
        save_json_file('data/metadata.json', metadata)
        save_json_file(current_info_file, webpages)
        messagebox.showinfo("Nettoyage des Données de Crawl", "Les données de crawl ont été nettoyées.")

# Fonction principale pour lancer l'application
def main():
    root = tk.Tk()
    app = CrawlerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
