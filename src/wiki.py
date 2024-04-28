import argparse
import requests
import re
from bs4 import BeautifulSoup
from colorama import Fore, Style

def clean_references(text):
    # Use regular expressions to remove references, e.g., [1], [2], etc.
    return re.sub(r'\[\d+\]', '', text)

def clean_edits(text):
    return re.sub(r'\[edit\]', '', text)

def search_wikipedia(query, args):
    query = query.replace(' ', '_')
    response = requests.get(f"https://en.wikipedia.org/wiki/{query}")

    if response.status_code == 404:
        print(Fore.RED + 'Wikipedia does not have an article with this exact name.')
        return
    elif response.status_code != 200:
        print(Fore.RED + 'There is a problem with fetching data. Please try again!')
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')

    content_div = soup.find(class_='mw-content-ltr')
    content = content_div.find_all(['h2','h3','p', 'li'], recursive=True)
    print(Style.BRIGHT + Fore.CYAN + "========== Summary ==========" + Fore.RESET + Style.RESET_ALL)

    for child in content:
        text = clean_edits(clean_references(child.get_text().strip()))
        if not text:
            continue
        
        if child.name == 'h2':
            if text == 'Other Uses' or text == 'See also' or text == 'References':
                break
            if not args.full:
                break
            print(Style.BRIGHT + Fore.CYAN + '========== ' + text + ' ==========' + Fore.RESET + Style.RESET_ALL)
        elif child.name == 'h3':
            print(Style.BRIGHT + Fore.MAGENTA + '----- ' + text + ' -----' + Fore.RESET + Style.RESET_ALL)
        elif child.name == 'li':
            print(' * ' + text)
        elif child.name == 'p':
            print(text)

    search_url = response.url

    print(Fore.BLUE + "Read more:", search_url)

def search_top_results(args):
    response = requests.get(f"https://en.wikipedia.org/w/index.php?fulltext=1&search={args.query}&title=Special%3ASearch&ns0=1")

    if response.status_code != 200:
        print(Fore.RED + 'There is a problem with fetching data. Please try again!')
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    search_results_ul = soup.find('ul', class_='mw-search-results')
    if not search_results_ul:
        print(f'{Fore.RED}No results could be found for "{args.query}".')
        return

    top_results = search_results_ul.find_all('li', class_='mw-search-result', limit=10)

    print(f'Here are the results for: \"{args.query}\"')
    for i, item in enumerate(top_results):
        title = item.find('a').get('title').strip()
        desc = item.find('div', class_='searchresult').get_text().strip()
        print(f"{Style.BRIGHT}{i+1}. {Fore.CYAN}{title}{Fore.RESET}{Style.RESET_ALL} - {clean_references(desc)}\n")

    # Ask user which article they want
    while True:
        page = input("Pick a page: ")
        if page.lower() == 'q':
            return  # User wants to quit
        elif page.isdigit() and 1 <= int(page) <= len(top_results):
            search_wikipedia(top_results[int(page)-1].find('a').get('title').strip(), args)
            break
        else:
            print(Fore.RED + "Invalid input, please try again.")

def main():
    parser = argparse.ArgumentParser(description='Search for Wikipedia pages.')
    parser.add_argument('query', type=str, help='The Wikipedia page to search for')
    parser.add_argument('-f', '--full', action='store_true', help='Returns full text from Wikipedia article content')
    args = parser.parse_args()
    search_top_results(args)

if __name__ == "__main__":
    main()
