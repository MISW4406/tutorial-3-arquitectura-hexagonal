import pulsar
import json
import asyncio
import os
from typing import List

async def suscribirse_a_topico_partners(topic_name: str, subscription_name: str, topic_path: str, eventos: List):
    """Suscriptor de eventos de partners"""
    pulsar_url = os.getenv("PULSAR_SERVICE_URL", "pulsar://localhost:6650")
    
    try:
        client = pulsar.Client(pulsar_url)
        consumer = client.subscribe(topic_path, subscription_name)
        
        print(f"Suscrito a {topic_path} con nombre {subscription_name}")
        
        while True:
            try:
                msg = consumer.receive(timeout_millis=1000)
                data = json.loads(msg.data().decode('utf-8'))
                
                # Agregar evento a la lista para SSE
                eventos.append({
                    'topic': topic_name,
                    'data': data,
                    'timestamp': data.get('time', 0)
                })
                
                # Mantener solo los últimos 100 eventos
                if len(eventos) > 100:
                    eventos.pop(0)
                
                consumer.acknowledge(msg)
                print(f"Evento procesado de {topic_name}: {data.get('type', 'Unknown')}")
                
            except pulsar.Timeout:
                # Timeout normal, continuar
                pass
            except Exception as e:
                print(f"Error procesando mensaje de {topic_name}: {e}")
                
            await asyncio.sleep(0.1)
            
    except Exception as e:
        print(f"Error en suscripción a {topic_name}: {e}")
    finally:
        if 'consumer' in locals():
            consumer.close()
        if 'client' in locals():
            client.close()