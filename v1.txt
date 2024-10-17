import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from sqlalchemy import create_engine, Column, String, Integer, MetaData, Table, insert, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
import time
import random
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)

# Supabase PostgreSQL connection URL
SUPABASE_DB_URL = "postgresql://postgres.mqilfnfcwwfwjekpmqrm:sXbanPwEfN51v7ef@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

# Connect to Supabase PostgreSQL
engine = create_engine(SUPABASE_DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Create metadata and tables for storing scraped data
metadata = MetaData()

# Separate tables for YouTube, Blogs, Websites, and Scholarships
youtube_data = Table(
    'youtube_data', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String),
    Column('url', String),
    Column('source', String),
    Column('query', String),
    Column('user_id', String),
)

blogs_data = Table(
    'blogs_data', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String),
    Column('url', String),
    Column('source', String),
    Column('query', String),
    Column('user_id', String),
)

websites_data = Table(
    'websites_data', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String),
    Column('url', String),
    Column('source', String),
    Column('query', String),
    Column('user_id', String),
)

scholarships_data = Table(
    'scholarships_data', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String),
    Column('url', String),
    Column('source', String),
    Column('query', String),
    Column('user_id', String),
)

metadata.create_all(engine)

# Setup ChromeDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Anti-bot
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Set your ChromeDriver path
    chrome_driver_path = "D:/ABYSS/CODE/PY/SCRAPING/scrap/chromedriver.exe"
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Hide WebDriver flag
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    
    return driver

# Initialize WebDriver
if 'driver' not in st.session_state:
    st.session_state.driver = init_driver()

driver = st.session_state.driver

# Streamlit UI
st.title("Web Scraping for Study Materials or Scholarships")

# Ask if the user is looking for Study Material or Scholarship
purpose = st.radio("What are you looking for?", ("Study Material", "Scholarship"))

user_id = st.text_input("Enter your User ID")  # To identify the user for history purposes

if purpose == "Study Material":
    # Ask if they are in class or course
    study_type = st.radio("Are you looking for study material for a class or course?", ("Class", "Course"))

    if study_type == "Class":
        class_grade = st.selectbox("Select Your Class", ["10", "12"])
        board = st.selectbox("Select Your Board", ["CBSE", "ICSE", "State Board"])
    else:
        course = st.selectbox("Select Your Course", ["BCA", "BBA", "BCom", "BA", "BSc", "BTech", "MCA", "MBA", "MCom", "MA", "MSc", "MTech"])
        university = st.text_input("Enter Your University")

    subject = st.text_input("Enter Subject")
    topic = st.text_input("Enter Topic")
    language = st.selectbox("Preferred Language", ["English", "Hindi"])
    difficulty = st.selectbox("Select Difficulty Level", ["Beginner", "Intermediate", "Advanced"])
    platforms = st.multiselect("Preferred Platforms", ["YouTube", "Blogs", "Websites", "All"], default="All")

elif purpose == "Scholarship":
    # Inputs for scholarship search
    scholarship_level = st.selectbox("Looking for Scholarships for?", ["UG", "PG", "Doctorate"])
    category = st.selectbox("Scholarship Category", ["Merit-Based", "Need-Based", "Cultural", "Sports", "Others"])
    country = st.selectbox("Select the Country", ["India", "USA", "UK", "Australia", "Others"])
    scholarship_type = st.selectbox("Type of Scholarship", ["Government", "Private", "International"])
    st.write("We will search for scholarships based on the options provided.")

# Function to scrape YouTube
def scrape_youtube_videos(search_query, user_id):
    driver.get(f"https://www.youtube.com/results?search_query={search_query}")
    time.sleep(random.uniform(2, 5))  # Random sleep
    
    # Simulate scrolling
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(random.uniform(1, 2))
    
    video_titles = driver.find_elements(By.XPATH, '//a[@id="video-title"]')
    data = []
    
    for title in video_titles[:10]:
        video_url = title.get_attribute('href')
        video_text = title.text
        data.append({"title": video_text, "url": video_url, "source": "YouTube", "query": search_query, "user_id": user_id})
    
    return data

# Function to scrape blogs
def scrape_blogs(search_query, user_id):
    driver.get(f"https://www.google.com/search?q={search_query}+blog")
    time.sleep(random.uniform(2, 5))
    
    results = driver.find_elements(By.XPATH, '//div[@class="g"]//h3')
    links = driver.find_elements(By.XPATH, '//div[@class="g"]//a')
    
    data = []
    for i in range(min(10, len(results))):
        blog_title = results[i].text
        blog_link = links[i].get_attribute('href')
        data.append({"title": blog_title, "url": blog_link, "source": "Google", "query": search_query, "user_id": user_id})
    
    return data

# Function to scrape websites
def scrape_websites(search_query, user_id):
    driver.get(f"https://www.google.com/search?q={search_query}+website")
    time.sleep(random.uniform(2, 5))

    results = driver.find_elements(By.XPATH, '//div[@class="g"]//h3')
    links = driver.find_elements(By.XPATH, '//div[@class="g"]//a')

    data = []
    for i in range(min(10, len(results))):
        website_title = results[i].text
        website_link = links[i].get_attribute('href')
        data.append({"title": website_title, "url": website_link, "source": "Google", "query": search_query, "user_id": user_id})

    return data

# Function to scrape scholarships
def scrape_scholarships(search_query, user_id):
    driver.get(f"https://www.google.com/search?q={search_query}+scholarship")
    time.sleep(random.uniform(2, 5))

    results = driver.find_elements(By.XPATH, '//div[@class="g"]//h3')
    links = driver.find_elements(By.XPATH, '//div[@class="g"]//a')

    data = []
    for i in range(min(10, len(results))):
        scholarship_title = results[i].text
        scholarship_link = links[i].get_attribute('href')
        data.append({"title": scholarship_title, "url": scholarship_link, "source": "Google", "query": search_query, "user_id": user_id})

    return data

# Function to store data in the appropriate table
def store_data_in_table(data, table):
    try:
        stmt = insert(table).values(data)
        session.execute(stmt)
        session.commit()
    except Exception as e:
        logging.error(f"Failed to store data: {e}")

# Start scraping
if st.button("Start Scraping"):
    if purpose == "Study Material":
        if study_type == "Class":
            search_query = f"{topic} {subject} {class_grade} {board} {language} {difficulty}"
        else:
            search_query = f"{topic} {subject} {course} {university} {language} {difficulty}"
        
        results = []
        
        if "YouTube" in platforms or "All" in platforms:
            st.write("Scraping YouTube...")
            youtube_videos = scrape_youtube_videos(search_query, user_id)
            store_data_in_table(youtube_videos, youtube_data)
            st.write(f"Scraped {len(youtube_videos)} YouTube videos.")
            results.extend(youtube_videos)
        
        if "Blogs" in platforms or "All" in platforms:
            st.write("Scraping Blogs...")
            blogs = scrape_blogs(search_query, user_id)
            store_data_in_table(blogs, blogs_data)
            st.write(f"Scraped {len(blogs)} blogs.")
            results.extend(blogs)
        
        if "Websites" in platforms or "All" in platforms:
            st.write("Scraping Websites...")
            websites = scrape_websites(search_query, user_id)
            store_data_in_table(websites, websites_data)
            st.write(f"Scraped {len(websites)} websites.")
            results.extend(websites)

    elif purpose == "Scholarship":
        search_query = f"{scholarship_level} {category} {country} {scholarship_type}"
        st.write(f"Scraping Scholarships for {scholarship_level} level, {category} category in {country}...")
        scholarships = scrape_scholarships(search_query, user_id)
        store_data_in_table(scholarships, scholarships_data)
        st.write(f"Scraped {len(scholarships)} scholarships.")
        results = scholarships

    # Display all results
    st.write("### Scraping Results")
    df = pd.DataFrame(results)
    st.write(df)

    st.success("Scraping Completed!")

# Function to view user's search history in separate tables
if st.button("View My Search History"):
    with engine.connect() as conn:
        # Query YouTube history
        youtube_query = text("SELECT * FROM youtube_data WHERE user_id = :user_id")
        youtube_result = conn.execute(youtube_query, {'user_id': user_id})
        youtube_data = pd.DataFrame(youtube_result.fetchall(), columns=youtube_result.keys())

        # Query Blogs history
        blogs_query = text("SELECT * FROM blogs_data WHERE user_id = :user_id")
        blogs_result = conn.execute(blogs_query, {'user_id': user_id})
        blogs_data = pd.DataFrame(blogs_result.fetchall(), columns=blogs_result.keys())

        # Query Websites history
        websites_query = text("SELECT * FROM websites_data WHERE user_id = :user_id")
        websites_result = conn.execute(websites_query, {'user_id': user_id})
        websites_data = pd.DataFrame(websites_result.fetchall(), columns=websites_result.keys())

        # Query Scholarships history
        scholarships_query = text("SELECT * FROM scholarships_data WHERE user_id = :user_id")
        scholarships_result = conn.execute(scholarships_query, {'user_id': user_id})
        scholarships_data = pd.DataFrame(scholarships_result.fetchall(), columns=scholarships_result.keys())

    # Display each table separately
    st.write("### YouTube Search History")
    st.write(youtube_data if not youtube_data.empty else "No YouTube history found.")

    st.write("### Blogs Search History")
    st.write(blogs_data if not blogs_data.empty else "No Blogs history found.")

    st.write("### Websites Search History")
    st.write(websites_data if not websites_data.empty else "No Websites history found.")

    st.write("### Scholarships Search History")
    st.write(scholarships_data if not scholarships_data.empty else "No Scholarships history found.")
