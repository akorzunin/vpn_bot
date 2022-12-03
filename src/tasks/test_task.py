import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from periodiq import PeriodiqMiddleware, cron
from datetime import datetime

rabbitmq_broker = RabbitmqBroker(url="amqp://guest:guest@127.0.0.1:5672")
rabbitmq_broker.add_middleware(PeriodiqMiddleware(skip_delay=30))
dramatiq.set_broker(rabbitmq_broker)

@dramatiq.actor
def count_words(url):
    # response = requests.get(url)
    # count = len(response.text.split(" "))
    print(f"There are 123 words at {url!r}.")

@dramatiq.actor(periodic=cron("* * * * *"))
def hourly():
    # Do something each hour…
    ...
    print(datetime.now())

if __name__ == "__main__":
    # Synchronously count the words on example.com in the current process
    # count_words("http://example.com")

    # or send the actor a message so that it may perform the count
    # later, in a separate process.
    count_words.send("http://example.com")
    # hourly.send()

# run in console:
# dramatiq src.tasks.test_task

# run in wsl
# periodiq -v src.tasks.test_task