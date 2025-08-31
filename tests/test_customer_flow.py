from shinsa.utils.logger import get_logger
from datetime import datetime, timedelta, timezone
from celery import chord, chain, group
from shinsa.celery_app.app import celery_app
from shinsa.celery_app.tasks.customer_tasks import find_customer_links, process_customer_workflow
from shinsa.celery_app.tasks.report_tasks import batch_generate_report

logger = get_logger("test_customer_flow")

logger.info("Customer flow test module initialized.")

customer = {
    "name": "Aung Myo Tun",
    "email": "aungmyotun@gmail.com",
    "address": "Tokyo",
}


def test_apply() -> None:
    # Synchronous call
    # No calling queue
    result = find_customer_links.apply(args=[customer], queue="coordination")
    print("Result (apply):", result.get())  # .get() returns the task result


def test_apply_async() -> None:
    # Asynchronous call
    # Calling Queues (coordination,default)
    result = find_customer_links.apply_async(args=[customer], queue="coordination")
    print(f"Task ID {result.id}")
    print(result.get(timeout=10))
    # Check which queue the task was sent to
    from celery.result import AsyncResult

    task_result = AsyncResult(result.id)
    print(task_result.queue)  # Should print 'coordination'


def test_scehdule():
    # Schedule a task to run after a delay
    eta = datetime.now(timezone.utc) + timedelta(minutes=3)
    result = find_customer_links.apply_async(args=[customer], eta=eta, queue="coordination")
    logger.info(f"Scheduled Task ID {result.id} to run at {eta}")
    # print(result.get(timeout=40))


def test_singature():
    sig = find_customer_links.s(customer).set(queue="coordination")
    async_result = sig.apply_async()
    print(async_result.id)
    print(async_result.get(timeout=10))


def test_send_task():
    result = celery_app.send_task("find_customer_links", args=[customer], queue="coordination")
    print(result.id)
    print(result.get(timeout=10))


def test_batch_job():
    # Create individual customer workflows
    customers = [
        {
            "name": "Aung Myo Tun",
            "email": "aungmyotun@gmail.com",
            "address": "Tokyo",
        },
        {
            "name": "清水 勝美",
            "email": "shimizu@example.com",
            "address": "Osaka",
        },
    ]

    customer_workflows = []
    customer_task_mapping = []

    for i, customer in enumerate(customers):
        # Create workflow chain for this customer
        workflow = chain(
            find_customer_links.s(customer),
            process_customer_workflow.s(),
        )
        customer_workflows.append(workflow)

        # Track customer workflow info
        customer_task_mapping.append(
            {
                "customer": customer,
                "customer_index": i,
                "workflow": workflow,
            }
        )

    # Execute the batch workflow
    batch_job = chord(group(customer_workflows), batch_generate_report.s()).apply_async()


if __name__ == "__main__":
    # test_apply()
    # test_apply_async()
    # test_singature()
    test_send_task()
    # test_batch_job()
    # test_scehdule()
    logger.info("Test module execution completed.")
