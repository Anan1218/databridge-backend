from apscheduler.schedulers.background import BackgroundScheduler
from app.services.reddit_scanner import fetch_subreddit_posts
from app.services.data_store import add_posts

scheduler = BackgroundScheduler()

def schedule_reddit_scans():
    # Example subreddits
    subreddits_to_scan = ['technology', 'python']
    for subreddit in subreddits_to_scan:
        posts = fetch_subreddit_posts(subreddit, limit=10)
        add_posts(posts, subreddit)
        print(f"Fetched {len(posts)} new posts from r/{subreddit}")

def start_scheduler():
    # Run scan every 30 minutes
    scheduler.add_job(schedule_reddit_scans, 'interval', minutes=30)
    scheduler.start()
