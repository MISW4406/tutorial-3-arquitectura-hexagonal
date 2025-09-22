import json
import threading
from ....config.pulsar import TOPICS, get_pulsar_client
import pulsar
from ..aplicacion.comandos import ComandoRegistrarClick, ComandoRegistrarConversion
from ..aplicacion.servicios import ServicioTracking

class ConsumidorComandosTracking:
    """Consumidor de comandos desde el BFF para el servicio de tracking"""
    
    def __init__(self, servicio_tracking: ServicioTracking):
        self.pulsar_client = get_pulsar_client()
        self.servicio_tracking = servicio_tracking
        self.client = get_pulsar_client()
        self.running = True
    
    def get_servicio_tracking(self):
        # Configurar e inyectar dependencias del servicio
        from repositorios import RepositorioClicksSQL, RepositorioConversionesSQL
        from despachadores import DespachadorEventosTracking
        from ....config.database import get_db_session
        
        session = next(get_db_session())
        repo_clicks = RepositorioClicksSQL(session)
        repo_conversiones = RepositorioConversionesSQL(session)
        despachador = DespachadorEventosTracking(self.pulsar_client, TOPICS["TRACKING_EVENTOS"])
        
        return ServicioTracking(repo_clicks, repo_conversiones, despachador)
    
    def procesar_comando_registrar_click(self, mensaje):
        """Procesa comando de registrar click desde BFF"""
        print("MENSAJE RECIBIDO EN CONSUMIDOR!")  
        try:
            data = json.loads(mensaje.data().decode('utf-8'))
            comando_data = data.get('data', {})
            
            id_click = self.servicio_tracking.registrar_click(
                id_partner=comando_data.get('id_partner'),
                id_campana=comando_data.get('id_campana'),
                url_origen=comando_data.get('url_origen'),
                url_destino=comando_data.get('url_destino'),
                metadata_cliente=comando_data.get('metadata_cliente', {})
            )

            print(f"Click registrado desde BFF: {id_click}")

        except Exception as e:
            print(f"Error procesando comando registrar click: {e}")
    
    def procesar_comando_registrar_conversion(self, mensaje):
        """Procesa comando de registrar conversión desde BFF"""
        try:
            data = json.loads(mensaje.data().decode('utf-8'))
            comando_data = data.get('data', {})
            
            comando = ComandoRegistrarConversion(
                id_partner=comando_data.get('id_partner'),
                id_campana=comando_data.get('id_campana'),
                tipo_conversion=comando_data.get('tipo_conversion'),
                informacion_monetaria=comando_data.get('informacion_monetaria', {}),
                metadata_cliente=comando_data.get('metadata_cliente', {}),
                id_click=comando_data.get('id_click')
            )
            
            # Ejecutar el comando usando el servicio
            id_conversion = self.servicio_tracking.registrar_conversion(
                comando.id_partner,
                comando.id_campana,
                comando.tipo_conversion,
                comando.informacion_monetaria,
                comando.metadata_cliente,
                comando.id_click
            )
            
            print(f"Conversión registrada desde BFF: {id_conversion}")
            
        except Exception as e:
            print(f"Error procesando comando registrar conversión: {e}")
    
    def iniciar_consumidor(self):
        """Inicia el consumidor en un thread separado"""
        import threading
        import pulsar
        
        def consumir():
            print("THREAD CONSUMIDOR: Iniciando función consumir...")
            try:
                # Importar directamente en lugar de usar self.get_pulsar_client()
                from ....config.pulsar import get_pulsar_client
                client = get_pulsar_client()
                
                if not client:
                    print("ERROR: No se pudo obtener cliente Pulsar")
                    return
                
                from ....config.pulsar import TOPICS
                consumer = client.subscribe(
                    TOPICS["COMANDO_REGISTRAR_CLICK"],
                    "tracking-service-commands"
                )
                
                print("CONSUMIDOR DE COMANDOS TRACKING INICIADO - ENTRANDO AL LOOP")
                
                contador = 0
                while self.running:
                    contador += 1
                    print(f"LOOP CONSUMIDOR: Iteración {contador}")
                    try:
                        print("ESPERANDO MENSAJE...")
                        msg = consumer.receive(timeout_millis=5000)
                        print(f"MENSAJE RECIBIDO! Procesando...")
                        
                        if self.procesar_comando_click(msg):
                            consumer.acknowledge(msg)
                            print("MENSAJE CONFIRMADO")
                        else:
                            consumer.negative_acknowledge(msg)
                            print("MENSAJE RECHAZADO")
                            
                    except pulsar.Timeout:
                        print("TIMEOUT - No hay mensajes")
                    except Exception as e:
                        print(f"ERROR EN LOOP: {e}")
                        
            except Exception as e:
                print(f"ERROR INICIANDO CONSUMIDOR: {e}")
                import traceback
                traceback.print_exc()
        
        thread = threading.Thread(target=consumir, daemon=True)
        thread.start()
        print("THREAD DEL CONSUMIDOR INICIADO")
        return thread