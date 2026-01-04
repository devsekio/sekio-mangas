import schedule
import time
from fetch_mangas import fetch_top_mangas
from update_links import update_links

def job():
    print("Starting scheduled job...")
    try:
        print("Fetching latest top mangas...")
        fetch_top_mangas()
        print("Updating links...")
        update_links()
        print("Job completed successfully.")
    except Exception as e:
        print(f"Job failed: {e}")

# Schedule the job every day at a specific time (e.g., 10:00 AM) or just every 24 hours
# Here getting it to run once a day
schedule.every().day.at("16:05").do(job)

if __name__ == "__main__":
    print("Scheduler started. Jobs will run every day at 16:05 AM.")
    
    # Run once immediately on startup just to be sure everything is fresh (optional, but good for testing)
    # job() 
    
    while True:
        schedule.run_pending()
        time.sleep(60)
