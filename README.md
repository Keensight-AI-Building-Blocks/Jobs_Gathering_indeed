# Job Scraper for Indeed.com

## Description

This script automates the process of extracting job postings from Indeed.com based on user-defined job title and location. It uses **Selenium** for web scraping and **Pydantic** for input validation and data modeling. The extracted job details are saved into a CSV file for easy analysis.

---

## Features

- **Dynamic URL Generation**: Input job title and location to generate a tailored search query.
- **Automated Web Scraping**: Uses Selenium to navigate and extract job postings.
- **Data Validation**: Ensures scraped data adheres to expected formats using Pydantic schemas.
- **CSV Export**: Saves validated job postings into a CSV file.
- **Error Handling**: Handles missing or invalid data gracefully.

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Chrome
- ChromeDriver

### Dependencies

Install required Python libraries:

```bash
pip install selenium pydantic
```

---

## Usage

1. Clone the repository or download the script.
2. Ensure **ChromeDriver** is installed and its path is correctly set in the script.
3. Run the script:

```bash
python main.py
```

4. When prompted, input the desired job title and location:

   ```bash
   Enter the job title: Python Developer
   Enter the job location: New York, NY
   ```

5. The script will scrape job postings from Indeed.com based on your inputs and save the results in a CSV file named `indeed_jobs.csv`.

---

## File Structure

- `main.py`: The main script to run the scraper.
- `schemas.py`: Contains Pydantic schemas for input validation and data modeling.

---

## Output

The script generates a CSV file named `indeed_jobs.csv`, containing the following fields:

- **Title**: The job title.
- **Company**: The company offering the job.
- **Location**: The job's location.
- **Summary**: A brief description of the job.
- **Job Link**: A direct link to the job posting.

---

## Notes

- Ensure that the Indeed website's layout has not changed, as this may require updates to the scraping logic.
- This script is for educational purposes and complies with Indeed's terms of service.

---

## License

This project is licensed under the MIT License.

