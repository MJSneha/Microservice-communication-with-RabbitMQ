import pika
import mysql.connector
import json
#docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
#docker compose up
credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.200.180', 5672, '/', credentials))

channel = connection.channel()
channel.exchange_declare(exchange='read', exchange_type='direct')
channel.queue_declare(queue='read_queue')
channel.queue_bind(exchange='read', queue='read_queue')

channel.exchange_declare(exchange='read_response', exchange_type='direct')
channel.queue_declare(queue='read_queue_response')
channel.queue_bind(exchange='read_response', queue='read_queue_response')


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="sneha",
  database="students"
)
def callback(ch, method, properties, body):
    print("Received message for reading record.")
    c = mydb.cursor()
    c.execute("SELECT * FROM STUDENTS_DETAILS")
    records = c.fetchall()
    print(json.dumps(records))
    mydb.commit()
    ch.basic_publish(exchange='read_response', routing_key='read_queue_response', body=json.dumps(records))
    # acknowledge that the message has been received
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(queue='read_queue', on_message_callback=callback)
print('Waiting for messages.')

channel.start_consuming()



