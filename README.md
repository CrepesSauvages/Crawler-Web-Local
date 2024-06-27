# Web Crawler Application

## Overview

This is a web crawler application built using Python and Tkinter. The application allows users to start a new web crawl, continue a previous crawl, view the crawl queue, count the number of web pages crawled, search for specific web pages, and clean the crawl data.

## Features

- **Start a New Crawl**
  - Enter a starting URL and click "Nouveau Crawler" to start a new crawl.
- **Continue a Previous Crawl**
  - Click "Continuer Crawler" to continue a previous crawl using the existing queue.
- **View Crawl Queue**
  - Click "Visualiser la file d'attente" to view the crawl queue.
- **Count Web Pages**
  - Click "Nombre de pages web enregistrées" to count the number of web pages crawled.
- **Search for Web Pages**
  - Enter a search term and click "Rechercher" to search for specific web pages.
- **Clean Crawl Data**
  - Click "Nettoyer les données" to clean the crawl data and start fresh.

## Technical Details

- The application uses the `requests` and `BeautifulSoup` libraries to crawl web pages.
- The application uses the `json` library to store crawl data in JSON files.
- The application uses the `threading` library to run the crawl process in the background.
- The application uses `Tkinter` for the graphical user interface.

## License

This application is licensed under the MIT License. See the LICENSE file for details.

## Author

CrepesSauvages
