# Utils
from src.module.utils.log import logError

def save_emails(emails):
    try:
        with open('data/emails.txt', 'a') as file:
            for email in emails:
                file.write(email + '\n')
    except Exception as e:
        logError(e, f"Erreur lors de la sauvegarde des emails")
