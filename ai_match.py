import requests
import json
from datetime import datetime

def find_jobs_for_user(job_wanted, eme_job_titles):
    """
    Match user with relevant jobs from the internet
    Returns a list of job matches
    """
    
    # Combine user's desired job with EME's required jobs
    keywords = set([job_wanted.lower()] + [title.lower() for title in eme_job_titles if title])
    
    # Option 1: Mock data (for testing)
    mock_jobs = [
        {
            "title": "Senior Python Developer",
            "company": "Tech Corp SA",
            "link": "https://www.indeed.com/viewjob?123",
            "source": "Indeed",
            "location": "Johannesburg",
            "salary": "R600k - R800k"
        },
        {
            "title": "Data Analyst",
            "company": "Data Solutions",
            "link": "https://www.linkedin.com/jobs/view/456",
            "source": "LinkedIn",
            "location": "Cape Town",
            "salary": "R450k - R550k"
        },
        {
            "title": job_wanted,
            "company": "EME Recruitment",
            "link": "#",
            "source": "EME AI Match",
            "location": "South Africa",
            "salary": "Competitive"
        }
    ]
    
    # Filter jobs based on keywords
    matched_jobs = []
    for job in mock_jobs:
        job_title_lower = job['title'].lower()
        if any(keyword in job_title_lower for keyword in keywords):
            matched_jobs.append(job)
    
    # If no matches, return a default message
    if not matched_jobs:
        matched_jobs = [{
            "title": "No exact matches found",
            "company": "Keep checking",
            "link": "#",
            "source": "System",
            "location": "Various",
            "salary": "Various"
        }]
    
    return matched_jobs

# Option 2: Real API integration (commented out - requires API keys)
"""
def fetch_adzuna_jobs(term, country='za'):
    '''Fetch real jobs from Adzuna API (South Africa)'''
    # You need to register at https://developer.adzuna.com/
    APP_ID = "YOUR_APP_ID"
    APP_KEY = "YOUR_APP_KEY"
    
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
    params = {
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'results_per_page': 10,
        'what': term,
        'content-type': 'application/json'
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            jobs = []
            for result in data.get('results', []):
                jobs.append({
                    'title': result.get('title'),
                    'company': result.get('company', {}).get('display_name'),
                    'link': result.get('redirect_url'),
                    'source': 'Adzuna',
                    'location': result.get('location', {}).get('display_name'),
                    'salary': result.get('salary_min', 'Not specified')
                })
            return jobs
    except Exception as e:
        print(f"Error fetching jobs: {e}")
    
    return []
"""