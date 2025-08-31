celery -A shinsa.celery_app.app flower --broker=redis://:Eiaung123@localhost:6379/0 --port=5555

Method	Sync/Async	Uses broker	Notes	Queue Support
apply()	Sync	No	Direct call, good for testing	queue= (optional, mostly ignored since runs locally)
apply_async()	Async	Yes	Real task scheduling	queue="my-queue"
s()	Signature	Optional	Flexible, for chains/groups	set(queue="my-queue")
send_task()	Async	Yes	Uses task name, good for decoupled code	queue="my-queue"