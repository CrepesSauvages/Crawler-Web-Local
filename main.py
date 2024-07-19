import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
import json
import os
import logging
import argparse

# Sys
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
import config
from shared import visited, metadata, webpages, queue

# Emails
from module.emails.extract_emails import extract_emails
from module.emails.save_emails import save_emails
from module.emails.search_emails_in_json import search_emails_in_json


# Core
from module.core.Json_File import load_json_file, save_json_file, initialize_json_file
from module.core.extract_info import extract_info
from module.core.process_url import process_url

# Utils
from module.utils.current_Info_File import get_current_info_file
from module.utils.is_valid_url import is_valid_url
from module.utils.log import logError

def initiate():
    if not os.path.exists("logs/"):
        os.makedirs("logs/")
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists('data/webpages'):
        os.makedirs('data/webpages')
    if not os.path.exists('data/queue.json'):
        with open('data/queue.json', 'w') as f:
            json.dump([], f)
    if not os.path.exists('data/visited.json'):
        with open('data/visited.json', 'w') as f:
            json.dump([], f)
    if not os.path.exists('data/metadata.json'):
        with open('data/metadata.json', 'w') as f:
            json.dump({"count": 0, "file_index": 1}, f)
    if not os.path.exists('data/webpages/info1.json'):
        with open('data/webpages/info1.json', 'w') as f:
            json.dump({}, f)
    logging.basicConfig(
        filename=config.Log_Path,
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    initialize_json_file('data/queue.json', [])
    initialize_json_file('data/visited.json', [])
    initialize_json_file('data/metadata.json', {"count": 0, "file_index": 1})
    initialize_json_file('data/webpages/info1.json', {})

    queue = load_json_file('data/queue.json') or []
    visited = load_json_file('data/visited.json') or []
    metadata = load_json_file('data/metadata.json') or {"count": 0, "file_index": 1}
    current_info_file = get_current_info_file(metadata)
    webpages = load_json_file(current_info_file) or {}

    parser = argparse.ArgumentParser(
        prog="Crawler",
        description="Crawler Web For Save Data WebSite"
    )

    parser.add_argument(
        "-d",
        "--delete",
        nargs="*",
        type=str,
        help="Delete Data"
    )
    args = parser.parse_args()
    config.delete = args.delete



# Fonction pour démarrer le crawling
def crawler(start_url=None):
    if start_url:
        queue.append(start_url)
    while queue:
        url = queue.pop(0)
        try:
            process_url(url, get_current_info_file(metadata))
        except requests.exceptions.RequestException as e:
            logError(e, f"Error fectching URL {url}")
        except Exception as e:
            logError(e, f"Error fectching URL {url}")
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
        current_info_file = get_current_info_file(metadata)
        save_json_file('data/queue.json', queue)
        save_json_file('data/visited.json', visited)
        save_json_file('data/metadata.json', metadata)
        save_json_file(current_info_file, webpages)
        messagebox.showinfo("Nettoyage des Données de Crawl", "Les données de crawl ont été nettoyées.")

# Fonction principale pour lancer l'application
def main():
    initiate()
    root = tk.Tk()
    app = CrawlerApp(root)
    root.mainloop()
    

if __name__ == "__main__":
    main()
