import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin, urlparse


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

        