from math import log
import time
import logging
from celery import shared_task, chord, chain, group
from shinsa.celery_app.app import celery_app
from shinsa.utils.logger import get_logger

# logger = logging.getLogger(__name__)
logger = get_logger("coordination", console=True)


@shared_task(bind=True, max_retries=3, name="find_customer_links")
def find_customer_links(self, customer):
    try:
        customer_name = customer.get("name", "")
        logger.info(f"[Find Links] Processing customer: {customer_name}")

        # Simulate finding links (replace with real logic)
        time.sleep(120)  # Minimal processing time

        links = [
            f"https://example.com/{customer_name.replace(' ', '_').lower()}",
            f"https://socialmedia.com/{customer_name.split()[0].lower()}",
            f"https://linkedin.com/in/{customer_name.replace(' ', '-').lower()}",
            f"https://twitter.com/{customer_name.split()[0].lower()}",
        ]
        result = {"customer": customer, "links": links, "task_id": self.request.id}

        logger.info(f"[Find Links] Found {len(links)} links for {customer_name}")
        return result
    except Exception as exc:
        logger.error(f"[Find Links] Error processing {customer.get('name', 'unknown')}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(bind=True, max_retries=3, name="process_customer_workflow")
def process_customer_workflow(self, links_result):
    try:
        customer = links_result["customer"]
        links = links_result["links"]
        customer_name = customer.get("name", "Unknown")

        logger.info(f"[Workflow] Starting workflow for {customer_name} with {len(links)} links")

        # Import here to avoid circular imports
        from shinsa.celery_app.tasks.crawl_tasks import crawl_link
        from shinsa.celery_app.tasks.analysis_tasks import analyze_content
        from shinsa.celery_app.tasks.report_tasks import generate_customer_report

        # Create processing chain for each link
        link_chains = []
        for link in links:
            chain_task = chain(
                crawl_link.s({"customer": customer, "link": link}),
                analyze_content.s(),
            )
            link_chains.append(chain_task)

        # Execute all chains and collect results
        chord_job = chord(group(link_chains), generate_customer_report.s()).apply_async()

        result = {
            "customer": customer,
            "workflow_task_id": self.request.id,
            "report_task_id": chord_job.id,
            "links_count": len(links),
        }

        logger.info(f"[Workflow] Started processing for {customer_name}, report task: {chord_job.id}")
        return result

    except Exception as exc:
        customer_name = links_result.get("customer", {}).get("name", "unknown")
        logger.error(f"[Workflow] Error processing workflow for {customer_name}: {str(exc)}")
        raise self.retry(exc=exc, countdown=120, max_retries=3)
