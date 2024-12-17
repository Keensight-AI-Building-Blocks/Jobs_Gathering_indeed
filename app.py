from flask import Flask, render_template, request, jsonify
from main import initialize_driver, scrape_job_cards, extract_job_details
from src.schemas import JobSearchInput, JobPosting
from src.AgentGEMINI import run_agent_processing
import json
import csv
from pydantic import ValidationError
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        # Get form data
        job_title = request.form.get('job')
        location = request.form.get('location')
        
        # Validate input
        job_search_input = JobSearchInput(job=job_title, location=location)
        url = job_search_input.build_url()
        
        # Initialize WebDriver
        chromedriver_path = "/usr/bin/chromedriver"
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
                    # Convert model to dict and ensure URL is converted to string
                    job_dict = job_posting.model_dump()
                    if job_dict.get('job_link'):
                        job_dict['job_link'] = str(job_dict['job_link'])
                    job_postings.append(job_dict)
                except ValidationError as e:
                    print(f"Validation error for job posting: {e}")
            
            # Save to temporary CSV for agent processing
            temp_csv = 'output/temp_jobs.csv'
            fieldnames = ['title', 'company', 'location', 'summary', 'job_link']
            
            with open(temp_csv, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for job in job_postings:
                    writer.writerow(job)
            
            # Process with AI agent
            input_params = {
                "job_title": job_title,
                "location": location
            }
            agent_results = run_agent_processing(
                input_csv=temp_csv,
                input_params=input_params
            )
            
            # Attach AI analysis results to each job posting
            if agent_results:
                for i, job in enumerate(job_postings):
                    if i < len(agent_results):
                        job['RecommendedCertifications'] = agent_results[i].get('RecommendedCertifications', '')
                        job['RoadMap'] = agent_results[i].get('RoadMap', '')
            
            return jsonify({
                'success': True,
                'jobs': job_postings
            })
            
        finally:
            driver.quit()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    app.run(debug=True)
