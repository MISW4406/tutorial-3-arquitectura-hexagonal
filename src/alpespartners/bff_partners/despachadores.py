import pulsar
import json
import os
from typing import Dict, Any

class Despachador:
    """Despachador de comandos hacia Apache Pulsar"""
    
    def __init__(self):
        self.pulsar_url = os.getenv("PULSAR_SERVICE_URL", "pulsar://localhost:6650")
        self.client = None
        self.producer = None
    
    def get_client(self):
        if not self.client:
            self.client = pulsar.Client(self.pulsar_url)
        return self.client
    
    async def publicar_mensaje(self, comando: Dict[Any, Any], topic_name: str, topic_path: str):
        """Publica un comando a un tópico específico"""
        producer = None
        try:
            client = self.get_client()
            producer = client.create_producer(topic_path)
            
            mensaje_json = json.dumps(comando, default=str)
            producer.send(mensaje_json.encode('utf-8'))
            
            print(f"Comando {comando['type']} publicado a {topic_path}")
            
        except Exception as e:
            print(f"Error publicando comando: {e}")
        finally:
            if producer:
                producer.close()