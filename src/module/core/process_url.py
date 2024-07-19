from urllib.parse import urljoin, urlparse
import requests

# Main 
from shared import visited, metadata, webpages, queue
# Core
from src.module.core.extract_info import extract_info
from src.module.core.Json_File import save_json_file

# Utils
from src.module.utils.current_Info_File import get_current_info_file
from src.module.utils.is_valid_url import is_valid_url
from src.module.utils.log import logError


# Fonction pour traiter une URL
def process_url(url, current_info_file):
    if url not in visited:
        try:
            info = extract_info(url)
            if info:
                metadata['count'] += 1
                index = str(metadata['count'])
                webpages[index] = info
                visited.append(url)

                # Add debugging messages to display processed URL
                print(f"Processing URL: {url}")

                # Save data and check if a new info file needs to be created
                if metadata['count'] % 50 == 0:
                    save_json_file(current_info_file, webpages)
                    metadata['file_index'] += 1
                    current_info_file = get_current_info_file(metadata)
                    webpages.clear()

                save_json_file(current_info_file, webpages)
                save_json_file('data/metadata.json', metadata)
                save_json_file('data/visited.json', visited)

                base_url = url.rsplit('/', 1)[0]
                for link in info['links']:
                    absolute_link = urljoin(base_url, link)
                    if is_valid_url(absolute_link) and absolute_link not in visited and absolute_link not in queue:
                        queue.append(absolute_link)
                        print(f"Added to queue: {absolute_link}")

                save_json_file('data/queue.json', queue)
        except requests.exceptions.RequestException as e:
            logError(f"Error fetching URL {url}: {e}")
        except Exception as e:
            logError(f"Error processing URL {url}: {e}")