from faststream import FastStream
from faststream.rabbit import RabbitBroker


broker = RabbitBroker("amqp://rmuser:rmpassword@localhost:5672/")

app = FastStream(broker)
