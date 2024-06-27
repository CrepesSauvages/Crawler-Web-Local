import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin, urlparse

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