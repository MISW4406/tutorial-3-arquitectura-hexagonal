import pulsar

client = pulsar.Client('pulsar://localhost:6650')
producer = client.create_producer('comandos-reservas')

for i in range(10):
    producer.send(('Hola-Pulsar-%d' % i).encode('utf-8'))

client.close()