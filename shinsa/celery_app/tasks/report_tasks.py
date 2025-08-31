import time
import logging
from datetime import datetime
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, name="generate_customer_report")
def generate_customer_report(self, analysis_results):
    try:
        if not analysis_results:
            return {"error": "No analysis results provided", "task_id": self.request.id}

        customer = analysis_results[0]["customer"]
        customer_name = customer.get("name", "Unknown")

        logger.info(f"[Customer Report] Generating report for {customer_name}")

        # Aggregate data from all link analyses
        total_links = len(analysis_results)
        total_keywords = []
        sentiment_scores = []
        crawled_links = []

        for result in analysis_results:
            analysis = result.get("analysis", {})
            total_keywords.extend(analysis.get("keywords", []))
            sentiment_scores.append(analysis.get("sentiment_score", 0))
            crawled_links.append(
                {
                    "link": result["link"],
                    "content_length": result.get("original_content_length", 0),
                    "keywords_count": len(analysis.get("keywords", [])),
                    "sentiment": analysis.get("sentiment", "neutral"),
                }
            )

        # Calculate aggregated metrics
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

        # Get top keywords across all links
        keyword_counts = {}
        for kw in total_keywords:
            word = kw["word"]
            keyword_counts[word] = keyword_counts.get(word, 0) + kw["count"]

        top_keywords = sorted(
            [{"word": word, "total_count": count} for word, count in keyword_counts.items()],
            key=lambda x: x["total_count"],
            reverse=True,
        )[:15]

        report = {
            "customer": customer,
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "report_task_id": self.request.id,
                "links_processed": total_links,
            },
            "summary": {
                "total_links_analyzed": total_links,
                "average_sentiment_score": round(avg_sentiment, 3),
                "overall_sentiment": "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral",
                "total_unique_keywords": len(top_keywords),
                "top_keywords": top_keywords,
            },
            "link_details": crawled_links,
            "recommendations": generate_recommendations(avg_sentiment, top_keywords, customer),
        }

        logger.info(f"[Customer Report] Generated report for {customer_name}: {total_links} links, sentiment: {report['summary']['overall_sentiment']}")
        return report

    except Exception as exc:
        customer_name = analysis_results[0].get("customer", {}).get("name", "unknown") if analysis_results else "unknown"
        logger.error(f"[Customer Report] Error generating report for {customer_name}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(bind=True, max_retries=3, name="batch_generate_report")
def batch_generate_report(self, customer_workflows):
    try:
        logger.info(f"[Batch Report] Generating batch report for {len(customer_workflows)} customers")

        successful_workflows = [w for w in customer_workflows if isinstance(w, dict) and "customer" in w]
        failed_workflows = len(customer_workflows) - len(successful_workflows)

        # Aggregate batch statistics
        total_links_processed = sum(w.get("links_count", 0) for w in successful_workflows)

        batch_report = {
            "batch_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "batch_task_id": self.request.id,
                "processing_duration": "calculated_externally",
            },
            "batch_summary": {
                "total_customers": len(customer_workflows),
                "successful_customers": len(successful_workflows),
                "failed_customers": failed_workflows,
                "total_links_processed": total_links_processed,
                "average_links_per_customer": round(total_links_processed / max(len(successful_workflows), 1), 2),
            },
            "customer_workflows": successful_workflows,
            "status": "completed",
        }

        logger.info(f"[Batch Report] Batch processing completed: {len(successful_workflows)} successful, {failed_workflows} failed")
        return batch_report

    except Exception as exc:
        logger.error(f"[Batch Report] Error generating batch report: {str(exc)}")
        raise self.retry(exc=exc, countdown=120, max_retries=3)


def generate_recommendations(sentiment_score, top_keywords, customer):
    recommendations = []

    if sentiment_score > 0.2:
        recommendations.append("Strong positive online presence detected")
        recommendations.append("Consider leveraging positive sentiment for marketing")
    elif sentiment_score < -0.2:
        recommendations.append("Negative sentiment detected - may need reputation management")
        recommendations.append("Review and address negative content")
    else:
        recommendations.append("Neutral sentiment - opportunity to build stronger positive presence")

    # Keyword-based recommendations
    tech_keywords = ["python", "programming", "development", "technology", "software"]
    if any(kw["word"] in tech_keywords for kw in top_keywords):
        recommendations.append("Technical expertise evident - highlight in professional materials")

    return recommendations
