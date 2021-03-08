# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

def scrape_all():
   # Initiate headless driver for deployment
   executable_path = {'executable_path': 'chromedriver.exe'}
   browser = Browser("chrome", **executable_path)

   news_title, news_paragraph = mars_news(browser)

   # Run all scraping functions and store results in dictionary
   data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now(),
      "hemispheres": hemisphere_data(browser)
   }

    # Stop webdriver and return data
   browser.quit()
   return data


def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        slide_elem.find("div", class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
        
        # To scrape the article summary
        news_p = slide_elem.find("div", class_='article_teaser_body').get_text()
        
    except AttributeError:
        return None, None

    return news_title, news_p

# ### JPL Space Featured Images


def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html,'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'
    
    return img_url

# ## Mars Facts

def mars_facts():
    # Add try/except for error handling
    try:
        # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)
    
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

# ## Hemisphere Images and Titles

def hemisphere_data(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    html = browser.html
    imgs_soup = soup(html, 'html.parser')

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Write code to retrieve the image urls and titles for each hemisphere.
    title_container = imgs_soup.find_all("div", class_="description")

    try:
        for title in title_container:
            # Creating empty dictionary
            hemispheres = {}
            
            # Fetching the Titles of the hemisphere images
            hemis_title = title.find("h3").get_text()

            # Visiting the hemisphere details pages and getting the URLs of large images 
            hemis_url = title.find("a", class_="itemLink product-item").get('href')
            hemis_full_url = f'https://astrogeology.usgs.gov{hemis_url}'
            browser.visit(hemis_full_url)
            browser.is_element_present_by_text('Sample', wait_time=2)
            final_image_url = browser.links.find_by_text('Sample')['href']

            # Adding image URLs and titles in the dictionary
            hemispheres["img_url"] = final_image_url
            hemispheres["title"] = hemis_title

            # Appending dictionary in the list
            hemisphere_image_urls.append(hemispheres.copy())

    
    except BaseException:
            return None

    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())

