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



