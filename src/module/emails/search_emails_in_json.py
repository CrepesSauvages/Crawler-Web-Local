import os
import json

# Utils
from src.module.utils.log import logError

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
        logError(e, f"Erreur lors de la recherche des emails dans les fichiers JSON:")
        return []
