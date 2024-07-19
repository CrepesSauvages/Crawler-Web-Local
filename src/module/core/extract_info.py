import requests
from bs4 import BeautifulSoup

# Emails
from src.module.emails.extract_emails import extract_emails

# Utils
from src.module.utils.log import logError

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
        logError(e, f"Erreur lors de l'extraction de {url}")
        return None