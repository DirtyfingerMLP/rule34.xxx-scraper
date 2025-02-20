import os
import requests
from bs4 import BeautifulSoup
import argparse
import re
import csv
from datetime import datetime

VERSION = "1.1.0"  # Update as necessary

def get_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching {url}: {response.status_code}")
        return None
    return BeautifulSoup(response.text, 'html.parser')

def extract_tags(soup, tag_type):
    tags = []
    for li in soup.select(f'li.tag-type-{tag_type.lower()} a:nth-of-type(2)'):
        tags.append(li.text.strip().replace(' ', '_'))
    return tags

def extract_datetime(text):
    match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', text)
    return match.group(0) if match else None

def get_post_date(soup):
    stats_div = soup.select("div#stats ul li")
    if len(stats_div) > 1 and "Posted:" in stats_div[1].text:        
        try:
            return extract_datetime(stats_div[1].text)
        except ValueError:
            return "Unknown"
    return "Unknown"

def get_media_page_data(url):
    soup = get_soup(url)
    if not soup:
        return None, None, [], [], [], [], [], "Unknown"
    
    video_tag = soup.select_one("video source")
    image_tag = soup.select_one("#image")
    media_url = video_tag['src'] if video_tag else (image_tag['src'] if image_tag else None)
    
    copyright_tags = extract_tags(soup, 'copyright')
    character_tags = extract_tags(soup, 'character')
    artist_tags = extract_tags(soup, 'artist')
    general_tags = extract_tags(soup, 'general')
    meta_tags = extract_tags(soup, 'metadata')
    post_date = get_post_date(soup)
    
    return media_url, "video" if video_tag else "image" if image_tag else None, copyright_tags, character_tags, artist_tags, general_tags, meta_tags, post_date

def sanitize_filename(filename):
    return re.sub(r'[\/:*?"<>|]', '_', filename)

def file_exists(download_dir, post_id):
    for file in os.listdir(download_dir):
        if file.startswith(post_id + " "):
            return True
    return False

def download_file(url, filename, download_dir):
    file_path = os.path.join(download_dir, filename)
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://rule34.xxx/'  # Ensure the referer is set correctly
    }
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        else:
            print(f"Error downloading {filename}: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Download failed for {filename}: {e}")


def construct_gallery_url(tags, page=1):
    base_url = "https://rule34.xxx/index.php?page=post&s=list&tags="
    return f"{base_url}{'+'.join(tags)}&pid={(page - 1) * 42}"

def write_to_csv(file, results):
    with open(file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='|')
        writer.writerow(["post_id", "post_date", "download_date", "Copyright", "Characters", "Artist", "General", "Meta", "Filename"])
        writer.writerows(results)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('tags', nargs='+', help='Tags')
    parser.add_argument('-f', '--file', help='Output file', default='results.csv')
    parser.add_argument('-limit', type=int, default=20, help='Limit of results')
    parser.add_argument('-d', '--download_dir', default='.', help='Directory to save files')
    args = parser.parse_args()

    os.makedirs(args.download_dir, exist_ok=True)
    results = []
    fetch_count = 0
    page = 1

    while fetch_count < args.limit:
        gallery_url = construct_gallery_url(args.tags, page)
        print(f"Fetching gallery page: {gallery_url}")
        
        gallery_soup = get_soup(gallery_url)
        if not gallery_soup:
            break
        
        posts = gallery_soup.select('.thumb')
        if not posts:
            break
        
        for post in posts:
            if fetch_count >= args.limit:
                break
            
            post_id_match = re.search(r'\d+', post['id'])
            post_id = post_id_match.group() if post_id_match else "Unknown"
            href = post.a['href']
            full_url = requests.compat.urljoin(gallery_url, href)
            
            print(f"Fetching {post_id}")
            duplicate = file_exists(args.download_dir, post_id)
            
            if duplicate:
                print(f"Skipping {post_id}")
                results.append([post_id, "", "skipped", "", "", "", "", "", ""])
            else:
                media_url, media_type, copyright_tags, character_tags, artist_tags, general_tags, meta_tags, post_date = get_media_page_data(full_url)
                
                if not media_url:
                    print(f"No media found for {post_id}, skipping.")
                    continue
                
                file_extension = os.path.splitext(media_url.split('?')[0])[-1]
                filename = sanitize_filename(f"{post_id} [{' '.join(tag.replace(' ', '_') for tag in args.tags)}] {' '.join(copyright_tags)} # {' '.join(character_tags)} # {' '.join(artist_tags)}{file_extension}")
                
                print(f"Downloading {post_id}")
                download_file(media_url, filename, args.download_dir)
                download_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")      
                results.append([
                    post_id, 
                    post_date if isinstance(post_date, str) else post_date.strftime("%Y-%m-%d %H:%M:%S"), 
                    download_date, 
                    ', '.join(copyright_tags), 
                    ', '.join(character_tags), 
                    ', '.join(artist_tags), 
                    ', '.join(general_tags), 
                    ', '.join(meta_tags), 
                    filename if not duplicate else ""
                ])
              
            fetch_count += 1
            write_to_csv(args.file, results)
        
        page += 1

if __name__ == "__main__":
    main()
