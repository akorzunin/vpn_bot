import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker


# rabbitmq_broker = RabbitmqBroker(host="rabbitmq")
# dramatiq.set_broker(rabbitmq_broker)


@dramatiq.actor
def count_words(url):
    # response = requests.get(url)
    # count = len(response.text.split(" "))
    print(f"There are 123 words at {url!r}.")


if __name__ == "__main__":
    # Synchronously count the words on example.com in the current process
    count_words("http://example.com")

    # or send the actor a message so that it may perform the count
    # later, in a separate process.
    count_words.send("http://example.com")
