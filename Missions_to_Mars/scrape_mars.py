from splinter import Browser
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "C:/webdrivers/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()
    full_mars_dict = {}

    # the Url that will be used to scrape information
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # HTML object and Parse HTML with Beautiful Soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # Find the latest News Title Text and store in variable
    news_title = soup.find_all('div', class_='content_title')[1].text.strip()

    # Find the latest News Paragraph Text and store in variable
    news_p = soup.find_all('div', class_='article_teaser_body')[0].text.strip()

    # New Url that will be used to scrape information
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # New HTML object and Parse HTML with Beautiful Soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # Find the current Featured Mars Image location
    jpl_image =soup.find('a', class_ = 'fancybox-thumbs')['href']

    # Create full image url link by combining base link and image location
    featured_image_url= 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/'+ jpl_image

    # New Url that will be used to scrape information
    url = 'https://space-facts.com/mars/'

    # Read html table in Pandas
    tables = pd.read_html(url)

    # First table in the list as dataframe
    facts_df = tables[0]

    # Set column names and index
    facts_df.columns = ['Description', 'Mars']
    facts_df.set_index('Description',inplace=True)

    # Convert dataframe to html
    facts_html = facts_df.to_html(classes="table table-bordered table-striped table-hover")

    # New Url that will be used to scrape information
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # New HTML object and Parse HTML with Beautiful Soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # Find the location of class for title and img url
    hemis = soup.find_all('div', class_='item')

    # Create empty list to store dictionaries with title and img url
    hemisphere_image_urls = []

    # Iterate through each location
    for hemi in hemis:
        
        # Collect Title
        title = hemi.find('h3').text.strip()

        # Find page to where full image is stored and create a url to go to page
        hemiloc = hemi.find('div', class_="description")
        hemi_link = hemiloc.a["href"]    
        browser.visit('https://astrogeology.usgs.gov' + hemi_link)

        # New HTML object and Parse HTML with Beautiful Soup
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')

        # Find full image url from the page and store url in variable
        hemi_img_loc = soup.find('div', class_='downloads')
        hemi_img_link = hemi_img_loc.find('li').a['href']

        # Create empty list
        # Store title and img url in dictionary
        hemi_image_dict = {}
        hemi_image_dict['title'] = title
        hemi_image_dict['img_url'] = hemi_img_link

        # store dictionaries with title and img url
        hemisphere_image_urls.append(hemi_image_dict)

    full_mars_dict = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "mars_facts": facts_html,
        "mars_hemispheres": hemisphere_image_urls
    }
    # Close the browser after scraping
    browser.quit()    
    
    return full_mars_dict
