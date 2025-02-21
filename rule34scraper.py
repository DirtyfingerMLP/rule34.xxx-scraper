import os
import requests
from bs4 import BeautifulSoup
import argparse
import re
import csv
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="script.log",
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger()

VERSION = "1.3.5"  # Updated version

def get_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

def extract_tags(soup, tag_type):
    tags = [li.text.strip().replace(' ', '_') for li in soup.select(f'li.tag-type-{tag_type.lower()} a:nth-of-type(2)')]
    return tags

def extract_datetime(text):
    match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', text)
    return match.group(0) if match else None

def get_post_date(soup):
    stats_div = soup.select("div#stats ul li")
    if len(stats_div) > 1 and "Posted:" in stats_div[1].text:
        return extract_datetime(stats_div[1].text) or "Unknown"
    return "Unknown"

def get_media_page_data(url):
    soup = get_soup(url)
    if not soup:
        return None, None, [], [], [], [], [], "Unknown"
    
    media_url = soup.find("a", string=re.compile(r'Original\s*image', re.I))['href']
    copyright_tags = extract_tags(soup, 'copyright')
    character_tags = extract_tags(soup, 'character')
    artist_tags = extract_tags(soup, 'artist')
    general_tags = extract_tags(soup, 'general')
    meta_tags = extract_tags(soup, 'metadata')
    post_date = get_post_date(soup)
    
    logger.info(f"Fetched media data from {url}")
    return media_url, copyright_tags, character_tags, artist_tags, general_tags, meta_tags, post_date

def sanitize_filename(filename):
    return re.sub(r'[\/:*?"<>|]', '_', filename)

def file_exists(download_dir, post_id):
    for file in os.listdir(download_dir):
        if file.startswith(post_id + " "):
            return file
    return None

def download_file(url, filename, download_dir):
    file_path = os.path.join(download_dir, filename)
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://rule34.xxx/'
    }
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        logger.info(f"Downloaded file: {filename}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Download failed for {filename}: {e}")

def construct_gallery_url(tags, start=0):
    base_url = "https://rule34.xxx/index.php?page=post&s=list&tags="
    return f"{base_url}{'+'.join(tags)}&pid={start}"

def write_to_csv(file, results):
    with open(file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='|')
        if f.tell() == 0:
            writer.writerow(["post_id", "post_date", "download_date", "Copyright", "Characters", "Artist", "General", "Meta", "Filename"])
        writer.writerows(results)
    logger.info(f"Data written to CSV: {file}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('tags', nargs='+', help='Tags')
    parser.add_argument('-f', '--file', help='Output file')
    parser.add_argument('-d', '--download_dir', help='Directory to save files')
    parser.add_argument('-l', '--limit', type=int, default=42, help='Limit of results')
    parser.add_argument('-s', '--start', type=int, default=0, help='Starting pid for pagination')

    args = parser.parse_args()
    tag_string = ' '.join(args.tags)
    args.file = args.file or f'{tag_string}.csv'
    if not args.file.endswith(".csv"): args.file += (".csv")
    args.download_dir = args.download_dir or tag_string
    os.makedirs(args.download_dir, exist_ok=True)
    fetch_count = 0
    page_start = args.start

    logger.info("Script started with tags: " + tag_string)

    while fetch_count < args.limit:
        gallery_url = construct_gallery_url(args.tags, page_start)
        logger.info(f"Fetching gallery page: {gallery_url}")
        print(f"Fetching gallery page: {gallery_url}")
        
        gallery_soup = get_soup(gallery_url)
        if not gallery_soup:
            break
        
        posts = gallery_soup.select('.thumb')
        if not posts:
            break
        
        results = []
        for post in posts:
            if fetch_count >= args.limit:
                break
            
            post_id_match = re.search(r'\d+', post['id'])
            post_id = post_id_match.group() if post_id_match else "Unknown"
            href = post.a['href']
            full_url = requests.compat.urljoin(gallery_url, href)
            
            logger.info(f"Fetching post {post_id}")
            print(f"Fetching {post_id}")
            duplicate = file_exists(args.download_dir, post_id)
            
            if duplicate:
                logger.info(f"Skipping {post_id}, duplicate found: {duplicate}")
                print(f"Skipping - duplicate found: {duplicate}")
                results.append([post_id, "", "skipped", "", "", "", "", "", duplicate])
            else:
                media_url, copyright_tags, character_tags, artist_tags, general_tags, meta_tags, post_date = get_media_page_data(full_url)
                if not media_url:
                    logger.warning(f"No media found for {post_id}, skipping.")
                    continue
                file_extension = os.path.splitext(media_url.split('?')[0])[-1]
                filename = sanitize_filename(f"{post_id} [{' '.join(args.tags)}] {' '.join(copyright_tags)} # {' '.join(character_tags)} # {' '.join(artist_tags)}{file_extension}")
                print(f"Downloading {filename}")
                download_file(media_url, filename, args.download_dir)
                download_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                results.append([post_id, post_date, download_date, ', '.join(copyright_tags), ', '.join(character_tags), ', '.join(artist_tags), ', '.join(general_tags), ', '.join(meta_tags), filename])
            fetch_count += 1
        write_to_csv(args.file, results)
        page_start += 42

    logger.info("Script completed successfully.")

if __name__ == "__main__":
    main()
