from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from pydantic import ValidationError
from typing import List
import csv
import time
from src.schemas import JobPosting, JobSearchInput
from src.AgentGEMINI import run_agent_processing, csv_to_json


def initialize_driver(chromedriver_path: str) -> webdriver.Chrome:
    """Initialize the Selenium WebDriver."""
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)
    return driver


def scrape_job_cards(driver: webdriver.Chrome, url: str, wait_time: int = 10) -> List[webdriver.remote.webelement.WebElement]:
    """Navigate to the URL and scrape job cards."""
    driver.get(url)
    WebDriverWait(driver, wait_time).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "resultContent")))
    return driver.find_elements(By.CLASS_NAME, "resultContent")


def extract_job_details(card) -> dict:
    """Extract job details from a single job card."""
    try:
        title = card.find_element(By.CSS_SELECTOR, "h2.jobTitle span").text
    except NoSuchElementException:
        title = ""

    try:
        company = card.find_element(By.CSS_SELECTOR, 'span[data-testid="company-name"]').text
    except NoSuchElementException:
        company = ""

    try:
        location = card.find_element(By.CSS_SELECTOR, 'div[data-testid="text-location"]').text
    except NoSuchElementException:
        location = ""

    try:
        summary = card.find_element(By.CSS_SELECTOR, "ul li").text
    except NoSuchElementException:
        summary = ""

    try:
        job_link = card.find_element(By.CSS_SELECTOR, "h2.jobTitle a").get_attribute('href')
    except NoSuchElementException:
        job_link = None

    return {
        "title": title,
        "company": company,
        "location": location,
        "summary": summary,
        "job_link": job_link
    }


def save_to_csv(filename: str, fieldnames: List[str], job_data: List[JobPosting]):
    """Save job postings to a CSV file."""
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for job in job_data:
            writer.writerow(job.model_dump())


def main():
    # Configuration
    chromedriver_path = "/usr/bin/chromedriver"
    csv_filename = 'output/indeed_jobs.csv'
    fieldnames = ['title', 'company', 'location', 'summary', 'job_link']

    # Get user input for job and location
    try:
        job_search_input = JobSearchInput(
            job=input("Enter the job title: ").strip(),
            location=input("Enter the location: ").strip()
        )
        url = job_search_input.build_url()
    except ValidationError as e:
        print("Invalid input. Please ensure all fields are filled correctly.")
        print(f"Details: {e}")
        return

    # Initialize WebDriver
    driver = initialize_driver(chromedriver_path)

    try:
        # Scrape job cards
        job_cards = scrape_job_cards(driver, url)

        # Extract job details
        job_postings = []
        for card in job_cards:
            job_details = extract_job_details(card)
            try:
                job_posting = JobPosting(**job_details)
                job_postings.append(job_posting)
            except ValidationError as e:
                print(f"Validation error for job posting: {e}")

        # Save to CSV
        save_to_csv(csv_filename, fieldnames, job_postings)
        print(f"Job postings saved to {csv_filename}")

        # Process with AI agent
        input_params = {
            "job_title": job_search_input.job,
            "location": job_search_input.location
        }
        run_agent_processing(input_csv=csv_filename, input_params=input_params)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
