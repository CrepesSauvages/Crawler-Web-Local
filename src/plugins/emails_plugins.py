import re
import os
import json

def extract_emails(soup):
    emails = set()
    email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    for text in soup.stripped_strings:
        for match in email_regex.findall(text):
            emails.add(match)
    return emails


def save_emails(emails):
    try:
        with open('data/emails.txt', 'a') as file:
            for email in emails:
                file.write(email + '\n')
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des emails: {e}")

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
