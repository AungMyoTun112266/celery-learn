import time
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, name="crawl_link")
def crawl_link(self, link_data):
    try:
        link = link_data["link"]
        customer = link_data["customer"]
        customer_name = customer.get("name", "Unknown")

        logger.info(f"[Crawl] Starting crawl for {customer_name}: {link}")

        # Simulate network request (replace with real crawling)
        time.sleep(130)  # Simulate network latency

        # In real implementation, you would do:
        # response = requests.get(link, timeout=10)
        # content = response.text

        # For demo, generate mock content
        mock_content = """
        Welcome to {customer_name}'s profile page.
        About {customer_name}: A professional in the industry.
        Skills: Python, Data Analysis, Machine Learning, Web Development
        Experience: Senior Developer at Tech Company
        Location: San Francisco, CA
        Interests: Technology, Innovation, Artificial Intelligence
        Recent posts about: Python programming, data science trends, AI developments
        """

        result = {
            "customer": customer,
            "link": link,
            "content": mock_content,
            "content_length": len(mock_content),
            "crawl_task_id": self.request.id,
            "status": "success",
        }

        logger.info(f"[Crawl] Successfully crawled {link} for {customer_name}")
        return result

    except Exception as exc:
        customer_name = link_data.get("customer", {}).get("name", "unknown")
        link = link_data.get("link", "unknown")
        logger.error(f"[Crawl] Error crawling {link} for {customer_name}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(bind=True, max_retries=3, name="fetch_page_content")
def fetch_page_content(self, url, customer_info):
    try:
        logger.info(f"[Fetch] Fetching content from: {url}")

        headers = {"User-Agent": "Mozilla/5.0 (compatible; CustomerProcessor/1.0)"}

        # Real implementation would be:
        # response = requests.get(url, headers=headers, timeout=10)
        # soup = BeautifulSoup(response.content, 'html.parser')
        # content = soup.get_text()

        # Mock response for demo
        time.sleep(2)  # Simulate network request
        content = f"Sample content from {url} for customer analysis"

        return {
            "url": url,
            "customer": customer_info,
            "content": content,
            "fetch_task_id": self.request.id,
        }

    except Exception as exc:
        logger.error(f"[Fetch] Error fetching {url}: {str(exc)}")
        raise self.retry(exc=exc, countdown=30, max_retries=3)
