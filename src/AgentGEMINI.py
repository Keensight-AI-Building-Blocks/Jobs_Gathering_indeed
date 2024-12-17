import csv
import json
from pydantic_ai import Agent
from dotenv import load_dotenv
import os
from src.schemas import JobPosting, AgentResult
from pydantic import ValidationError
import time
import asyncio
import nest_asyncio

# Enable nested event loops
nest_asyncio.apply()

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file. Please add it.")

agent = Agent(
    'gemini-1.5-flash',
    deps_type=str,
    result_type=AgentResult,
    system_prompt='''You are a professional career advisor specialized in analyzing job offers.
    For each job, provide:
    1. RecommendedCertifications: A concise list of relevant certifications that would enhance the candidate's profile
    2. RoadMap: A clear, step-by-step learning path to acquire the necessary skills'''
)

def fetch_job_data(csv_file: str):
    """Lire les données depuis le fichier CSV et les convertir en instances de JobPosting."""
    job_postings = []
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    job_posting = JobPosting(**row)
                    job_postings.append(job_posting)
                except ValidationError as e:
                    print(f"Validation error for row {row}: {e}")
    except FileNotFoundError:
        print(f"File {csv_file} not found.")
    return job_postings


def format_job_posting(job_posting: JobPosting) -> str:
    """Formater un JobPosting en une chaîne descriptive pour l'agent."""
    return (
        f"Job Title: {job_posting.title}\n"
        f"Company: {job_posting.company}\n"
        f"Location: {job_posting.location}\n"
        f"Summary: {job_posting.summary}\n"
        f"Job Link: {job_posting.job_link}"
    )


def save_results_to_csv(output_file: str, results: list):
    """Enregistrer les résultats dans un fichier CSV."""
    fieldnames = ['title', 'company', 'location', 'summary', 'job_link',
                  'RecommendedCertifications', 'RoadMap']
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)


def save_combined_results(input_data: dict, results: list, output_file: str = "output/results.json"):
    """
    Save both input parameters and processing results in a single JSON file.
    
    Args:
        input_data: Dictionary containing input parameters (job title and location)
        results: List of processed job postings with agent recommendations
        output_file: Path to the output JSON file
    """
    combined_data = {
        "input_parameters": input_data,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "results": results
    }
    
    with open(output_file, mode='w', encoding='utf-8') as json_file:
        json.dump(combined_data, json_file, indent=4, ensure_ascii=False)
    print(f"Combined results saved to {output_file}")


def run_agent_processing(input_csv: str = "output/indeed_jobs.csv", 
                        output_csv: str = "output/agent_results.csv",
                        input_params: dict = None):
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        job_postings = fetch_job_data(input_csv)
        if not job_postings:
            print("No job postings found to process")
            return None

        results = []
        for job_posting in job_postings:
            try:
                formatted_input = format_job_posting(job_posting)
                print(f"Processing job: {job_posting.title}")
                
                # Run the agent in the event loop
                run_result = loop.run_until_complete(agent.run(formatted_input))
                
                # Handle the response format
                if hasattr(run_result, 'data'):
                    result = run_result.data
                else:
                    result = run_result  # If result is already the data
                
                # Convert Pydantic model to dict and handle HttpUrl
                job_data = job_posting.model_dump()
                job_data['job_link'] = str(job_data['job_link']) if job_data['job_link'] else None
                
                processed_result = {
                    **job_data,  # Spread the job data
                    "RecommendedCertifications": result.RecommendedCertifications,
                    "RoadMap": result.RoadMap
                }
                results.append(processed_result)
                print(f"Successfully processed job: {job_posting.title}")
                
            except Exception as e:
                print(f"Error processing job {job_posting.title}: {str(e)}")
                continue
            
        if results:
            save_results_to_csv(output_csv, results)
            if input_params:
                save_combined_results(input_params, results)
            
            # Return all results
            return results
        
        return None
        
    except Exception as e:
        print(f"Error in agent processing: {str(e)}")
        return None
    finally:
        try:
            loop.close()
        except:
            pass


def csv_to_json(csv_file_path, json_file_path):
    data = []
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # Parse columns with special structures
            for key in row:
                # Clean up fields with embedded quotes
                if row[key] and isinstance(row[key], str):
                    row[key] = row[key].strip('"')
            data.append(row)
    
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
