## Introduction
This is a simple command-line tool to batch download images and videos from [rule34.xxx](https://rule34.xxx/).

It was written with the intent of getting proper, descriptive filenames from the site 
instead of something like 234524664.mp4 when you use jdownloader or other dl-managers.

Also, I wanted it to be easy to keep your local folders up-to-date and to avoid
downloading duplicate files.
With this script you can do that easily. You can even rename your downloaded files if my
default naming convention isn't to your liking.

It should work with any OS that can run python.

## Features:
- simple syntax with sensible default values
- auto-generates a sensible filename like this: POST_ID [search-tags] copyright_tags#character_tags#artist_tags.file_extension
- detects and skips duplicates in download folders, even if you renamed them. only condition: don't change the leading POST_ID!
- downloads ALL tags in a separate csv file. appends to existing csv file.
- specify custom download directory.(default: .\your-search-tags  -  this means I generate a folder name based on what you downloaded)
- specify custom csv name & location (default: your-search-tags.csv)
- limit number of downloads (default: 42 - that's 1 page. you can go as high as you want)
- specify starting point for downloads (default:0 - to skip the first page, enter 41)

## Some usage examples:

You want the first page of results from the magnificent pmv-editor dirtyfinger:

    python .\rule34xxx-scraper.py dirtyfinger

You want the latest 10 uploads from top-artist rexyvexi:

    python .\rule34xxx-scraper.py -l 10 rexyvexi

Download everything involving sex from legend of korra, but without the disgusting stuff:
    
    python .\rule34xxx-scraper.py -l 2000 "the_legend_of_korra sex" "-vore -guro -scat -torture" 

Start downloading but skip the first, newest 500 posts:
    
    python .\rule34xxx-scraper.py -s 500 the_owl_house

You want to save the downloads in a specific directory:
    
    python .\rule34xxx-scraper.py --download_dir "C:\Documents\Taxes\r34\clop" my_little_pony

Custom name and location for the csv file
    
    python .\rule34xxx-scraper.py -f "tags.csv" sesame_street

## INSTALLATION

You need python on your system. Google it, if you don't know what that means.
Anyway, you need to use your system's command line console to use this script.

### Install Python

This site will tell you how to install python: https://wiki.python.org/moin/BeginnersGuide/Download

After installing python, you'll need to install some libraries. DON'T PANIC, this is easy.
Open the console, aka command prompt or terminal.
Run the following command to install all required libraries:

    pip install requests beautifulsoup4 argparse

This will install the following (nerd-stuff - ignore if not a coder):
* requests: To make HTTP requests.
* beautifulsoup4: For parsing HTML.
* argparse: To handle command-line arguments.

Note: You may need to use pip3 instead of pip on Mac if pip is linked to Python 2.x.

### Download the Script
Just put the file rule34xxx-scraper.py into any folder. 

That's all.

### Run the Script
Open the console and navigate to wherever you put the script.
Running the script without any parameters will give you a short info on the parameters you can use.
If you're impatient, just try one of the usage examples listed at the top.

The parameters are:
```
-h                    Help. not that helpful at the moment. maybe later.
-f or --file          Let's you choose your own name and location for the
                      csv file. Useful if you automate stuff and want to
                      separate tag files for different folders.
-d or --download_dir  Specify your desired download folder for this search.
                      It defaults to whatever your search terms were,
                      which is not always optimal.
-l or --limit         The amount of files you download in one go. It
                      defaults to 42 (one entire page) because we wouldn't
                      want to start a gigabyte-sized download by accident, eh?
-s or --start         By default, you start downloading with the first
                      (i.e. the newest) file. The first file has the number 0.
                      It's a coder thing. If you want to start downloading
                      while skipping the newest files, just specify the
                      number where you want to start.
tags                  Every word you type in that doesn't have a leading
                      '-' will be considered a search tag. The tags are the
                      same as on the website, so create your perfect
                      search-tags there. You can put the tags in "quotation
                      marks" but you don't need to, unless you use exclusion
                      tags (e.g. "-guro" if you don't want to download guro).
                      For clarity, put the search tags last.
```

Example:

    python .\rule34xxx-scraper.py -d "happy sex" "equestria_girls show_accurate happy_sex"

I recommend you test your search queries on the website itself first and then use the script.

That's all.
Enjoy!

PS:
If you thought that was useful and want to say thanks - I have a patreon where you can give me all your money!
It's about My Little Pony PMVs (I know, I know) and I understand if you don't want to donate because you don't
want to answer pointed questions to whomever can see your patreon membership status, but right now it's the 
only thing I have set up.

https://www.patreon.com/c/Dirtyfinger
