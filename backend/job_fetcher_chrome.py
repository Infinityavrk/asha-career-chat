from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# -------------------------------
#  Helper: Create Chrome driver
# -------------------------------
def create_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Headless mode for server
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    # Path to chromedriver
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# -------------------------------
#  Job Fetching Function (Fixed Safari)
# -------------------------------
def fetch_herkey_jobs_safari_fixed(url):
    driver = create_chrome_driver()
    driver.get(url)

    jobs = []

    try:
        # Before scraping, ensure full page load
        WebDriverWait(driver, 30).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        
        # Wait for specific element
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-test-id="job-details"]'))
        )
        print(f"Job titles loaded successfully from {url}!")
        time.sleep(5)
        job_cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-test-id="job-details"]')

        for card in job_cards:
            try:
                title_element = card.find_element(By.CSS_SELECTOR, 'p[data-test-id="job-title"]')
                company_element = card.find_element(By.CSS_SELECTOR, 'p[data-test-id="company-name"]')

                # Location, Work Type, Experience
                info_element = card.find_element(By.CSS_SELECTOR, 'p.MuiTypography-root.MuiTypography-body2.capitalize')
                info_text = info_element.text.strip() if info_element else ""

                location = work_type = experience = "N/A"
                if info_text:
                    parts = [p.strip() for p in info_text.split('|')]
                    if len(parts) >= 1:
                        location = parts[0]
                    if len(parts) >= 2:
                        work_type = parts[1]
                    if len(parts) >= 3:
                        experience = parts[2]

                job = {
                    "title": title_element.text.strip() if title_element else "N/A",
                    "company": company_element.text.strip() if company_element else "N/A",
                    "location": location,
                    "work_type": work_type,
                    "experience": experience
                }
                jobs.append(job)

            except Exception as e:
                print("Error extracting a job card:", e)

    except Exception as e:
        print("Timeout: Job details did not load properly.", e)

    finally:
        driver.quit()

    return jobs

# -------------------------------
#  Event Fetching Function (Fixed Safari)
# -------------------------------
def fetch_herkey_featured_events_safari():
    driver = create_chrome_driver()
    driver.get("https://events.herkey.com/events/")

    events = []

    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.card.event-details-card.mb-2.featured-events'))
        )
        print(f"Event titles loaded successfully from https://events.herkey.com/events/!")
        time.sleep(3)

        event_cards = driver.find_elements(By.CSS_SELECTOR, 'div.card.event-details-card.mb-2.featured-events')

        for card in event_cards:
            try:
                title_element = card.find_element(By.CSS_SELECTOR, 'a.card-heading')
                event_name = title_element.text.strip()
                event_link = title_element.get_attribute('href')

                event = {
                    "name": event_name,
                    "link": event_link,
                }
                events.append(event)

            except Exception as e:
                print("Error extracting an event card:", e)

    except Exception as e:
        print("Timeout: Event details did not load properly.", e)

    finally:
        driver.quit()

    return events

# -------------------------------
#  Functions for different types
# -------------------------------
def get_all_jobs():
    return fetch_herkey_jobs_safari_fixed(url="https://www.herkey.com/jobs")

def get_work_from_home_jobs():
    return fetch_herkey_jobs_safari_fixed(url="https://www.herkey.com/jobs/search?work_mode=work-from-home")

def get_jobs_by_keyword(keyword):
    keyword = keyword.strip().lower().replace(' ', '-')
    search_url = f"https://www.herkey.com/jobs/search?keyword={keyword}"
    return fetch_herkey_jobs_safari_fixed(url=search_url)

def get_all_events():
    return fetch_herkey_featured_events_safari()

# -------------------------------
# Example usage:
# -------------------------------
if __name__ == "__main__":
    '''
    print("\nFetching ALL JOBS...\n")
    all_jobs = get_all_jobs()
    for idx, job in enumerate(all_jobs, start=1):
        print(f"{idx}. {job['title']} at {job['company']} ({job['location']}, {job['work_type']}, {job['experience']})")

    print("\nFetching WORK FROM HOME JOBS...\n")
    wfh_jobs = get_work_from_home_jobs()
    for idx, job in enumerate(wfh_jobs, start=1):
        print(f"{idx}. {job['title']} at {job['company']} ({job['location']}, {job['work_type']}, {job['experience']})")

    print("\nFetching JOBS for Keyword: UI/UX Design...\n")
    keyword_jobs = get_jobs_by_keyword("ui ux design")
    for idx, job in enumerate(keyword_jobs, start=1):
        print(f"{idx}. {job['title']} at {job['company']} ({job['location']}, {job['work_type']}, {job['experience']})")
    '''
    print("\nFetching FEATURED EVENTS...\n")
    featured_events = get_all_events()
    for idx, event in enumerate(featured_events, start=1):
        print(f"{idx}. {event['name']}")
        print(f"   Link: {event['link']}\n")
