import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from sqlalchemy import create_engine, Column, String, Integer, MetaData, Table, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
import time

# Supabase PostgreSQL connection URL
SUPABASE_DB_URL = "postgresql://postgres.brqkzxsrbufimcytlind:sXbanPwEfN51v7ef@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"

# Connect to Supabase PostgreSQL
engine = create_engine(SUPABASE_DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Create table for storing scraped data
metadata = MetaData()

scraped_data = Table(
    'scraped_data', metadata,
    Column('id', Integer, primary_key=True),
    Column('type', String),
    Column('title', String),
    Column('url', String),
    Column('source', String),
    Column('query', String),
)

metadata.create_all(engine)

# Set up the Chrome WebDriver only once
if 'driver' not in st.session_state:
    # Path to your ChromeDriver
    chrome_driver_path = "D:\ABYSS\CODE\PY\SCRAPING\scrap\chromedriver.exe"

    # Path to your Chrome binary (make sure this path is correct)
    chrome_binary_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.binary_location = chrome_binary_path

    # Setup ChromeDriver using Selenium
    service = Service(executable_path=chrome_driver_path)
    st.session_state.driver = webdriver.Chrome(service=service, options=chrome_options)

# Access WebDriver from session state
driver = st.session_state.driver

# Streamlit UI
st.title("Web Scraping for Indian Students")

st.subheader("Enter Your Preferences")
class_grade = st.selectbox("Select Your Class", ["10", "12", "UG", "PG"])
subject = st.text_input("Enter Subject (e.g., Physics, Math)")
topic = st.text_input("Enter Topic (e.g., Quadratic Equations, Electrostatics)")
board = st.selectbox("Select Your Board", ["CBSE", "ICSE", "State Board", "JEE", "NEET"])
language = st.selectbox("Preferred Language", ["English", "Hindi"])
resource_type = st.selectbox("Preferred Resource Type", ["Videos", "Blogs", "Articles", "PDFs", "All"])
difficulty = st.selectbox("Select Difficulty Level", ["Beginner", "Intermediate", "Advanced"])
platforms = st.selectbox("Preferred Platforms", ["YouTube", "Blogs", "Articles", "Websites", "All"])
scholarship_prefs = st.selectbox("Looking for Scholarships?", ["UG", "PG", "National", "International", "None"])

# Function to scrape YouTube for videos
def scrape_youtube_videos(search_query):
    driver.get(f"https://www.youtube.com/results?search_query={search_query}")
    time.sleep(2)
    
    video_titles = driver.find_elements(By.XPATH, '//a[@id="video-title"]')
    data = []
    
    for title in video_titles[:10]:
        video_url = title.get_attribute('href')
        video_text = title.text
        data.append({"type": "Video", "title": video_text, "url": video_url, "source": "YouTube"})
    
    return data

# Function to scrape blogs based on user preferences
def scrape_blogs(search_query):
    driver.get(f"https://www.google.com/search?q={search_query}+blog")
    time.sleep(2)
    
    results = driver.find_elements(By.XPATH, '//div[@class="g"]//h3')
    links = driver.find_elements(By.XPATH, '//div[@class="g"]//a')
    
    data = []
    for i in range(min(10, len(results))):
        blog_title = results[i].text
        blog_link = links[i].get_attribute('href')
        data.append({"type": "Blog", "title": blog_title, "url": blog_link, "source": "Google"})
    
    return data

# Function to store scraped data in Supabase PostgreSQL
def store_in_db(data, query):
    for item in data:
        session.execute(scraped_data.insert().values(
            type=item['type'],
            title=item['title'],
            url=item['url'],
            source=item['source'],
            query=query
        ))
    session.commit()

# Start Scraping
if st.button("Start Scraping"):
    search_query = f"{topic} {subject} {class_grade} {board} {language} {difficulty}"
    
    if "YouTube" in platforms or "All" in platforms:
        st.write("Scraping YouTube...")
        youtube_videos = scrape_youtube_videos(search_query)
        store_in_db(youtube_videos, search_query)
        st.write(f"Scraped {len(youtube_videos)} YouTube videos.")

    if "Blogs" in platforms or "All" in platforms:
        st.write("Scraping Blogs...")
        blogs = scrape_blogs(search_query)
        store_in_db(blogs, search_query)
        st.write(f"Scraped {len(blogs)} blogs.")

    st.success("Scraping Completed!")

# Show stored data from Supabase PostgreSQL
if st.button("Show Data"):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM scraped_data"))
        data = pd.DataFrame(result.fetchall(), columns=result.keys())
        st.write(data)