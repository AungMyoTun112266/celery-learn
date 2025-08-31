import time
import logging
import re
from collections import Counter
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, name="analyze_content")
def analyze_content(self, crawled_data):
    try:
        customer = crawled_data["customer"]
        link = crawled_data["link"]
        content = crawled_data["content"]
        customer_name = customer.get("name", "Unknown")

        logger.info(f"[Analysis] Analyzing content from {link} for {customer_name}")

        # Simulate CPU-intensive analysis
        time.sleep(140)

        # Extract keywords and perform analysis
        analysis_result = extract_keywords_and_analyze(content)

        result = {
            "customer": customer,
            "link": link,
            "original_content_length": crawled_data.get("content_length", len(content)),
            "analysis": analysis_result,
            "analysis_task_id": self.request.id,
            "crawl_task_id": crawled_data.get("crawl_task_id"),
        }

        logger.info(f"[Analysis] Completed analysis for {customer_name}: {len(analysis_result['keywords'])} keywords found")
        return result

    except Exception as exc:
        customer_name = crawled_data.get("customer", {}).get("name", "unknown")
        logger.error(f"[Analysis] Error analyzing content for {customer_name}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(bind=True, max_retries=3, name="extract_keywords")
def extract_keywords(self, content, min_length=3, max_keywords=50):
    try:
        logger.info("[Keywords] Extracting keywords from content")

        # Simulate processing time
        time.sleep(0.5)

        # Clean and tokenize content
        words = re.findall(r"\\b[a-zA-Z]{" + str(min_length) + ",}\\b", content.lower())

        # Remove common stop words
        stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "about"}
        filtered_words = [word for word in words if word not in stop_words]

        # Count frequency and get top keywords
        word_freq = Counter(filtered_words)
        keywords = [{"word": word, "count": count} for word, count in word_freq.most_common(max_keywords)]

        result = {
            "keywords": keywords,
            "total_words": len(words),
            "unique_words": len(set(words)),
            "task_id": self.request.id,
        }

        logger.info(f"[Keywords] Extracted {len(keywords)} keywords")
        return result

    except Exception as exc:
        logger.error(f"[Keywords] Error extracting keywords: {str(exc)}")
        raise self.retry(exc=exc, countdown=30, max_retries=3)


def extract_keywords_and_analyze(content):
    # Simple keyword extraction and sentiment analysis
    words = re.findall(r"\\b[a-zA-Z]{3,}\\b", content.lower())

    # Remove stop words
    stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "about", "this", "that", "these", "those", "they", "them", "their"}
    filtered_words = [word for word in words if word not in stop_words]

    # Get keyword frequency
    word_freq = Counter(filtered_words)
    top_keywords = [{"word": word, "count": count} for word, count in word_freq.most_common(20)]

    # Simple sentiment analysis (mock)
    positive_words = ["good", "great", "excellent", "amazing", "wonderful", "professional", "skilled", "experienced"]
    negative_words = ["bad", "poor", "terrible", "awful", "unprofessional"]

    positive_count = sum(1 for word in filtered_words if word in positive_words)
    negative_count = sum(1 for word in filtered_words if word in negative_words)

    sentiment_score = (positive_count - negative_count) / max(len(filtered_words), 1)

    return {
        "keywords": top_keywords,
        "word_count": len(words),
        "unique_words": len(set(filtered_words)),
        "sentiment_score": sentiment_score,
        "sentiment": "positive" if sentiment_score > 0.1 else "negative" if sentiment_score < -0.1 else "neutral",
    }
