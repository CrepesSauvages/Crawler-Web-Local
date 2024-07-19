import re

def extract_emails(soup):
    emails = set()
    email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    for text in soup.stripped_strings:
        for match in email_regex.findall(text):
            emails.add(match)
    return emails
