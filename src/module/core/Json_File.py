import json
import os

from src.module.utils.log import logError

def initialize_json_file(filename, initial_data):
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            json.dump(initial_data, file)

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        logError(e,f"Erreur de décodage JSON dans le fichier {filename}")
        return None
    except Exception as e:
        
        logError(e,f"Erreur lors du chargement du fichier {filename}")
        return None

def save_json_file(filename, data):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
            file.flush()  # Force l'écriture immédiate sur le disque
            os.fsync(file.fileno())  # Synchronisation avec le disque pour s'assurer que toutes les données sont écrites
    except Exception as e:
        logError(e ,f"Erreur lors de la sauvegarde du fichier {filename}")
