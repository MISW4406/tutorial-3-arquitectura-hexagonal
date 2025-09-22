# Alpes Partners - Tracking Service

Este servicio implementa un sistema de tracking de clicks y conversiones siguiendo los principios de Domain-Driven Design (DDD) y arquitectura basada en eventos.

## Estructura del Proyecto

```
alpespartners/
├── modulos/
│   └── tracking/
│       ├── dominio/          # Capa de dominio (entidades, objetos valor, etc.)
│       ├── aplicacion/       # Capa de aplicación (servicios)
│       └── infraestructura/  # Capa de infraestructura (repositorios)
├── api/                      # API REST
└── config/                   # Configuraciones
```

## Requisitos

- Docker
- Docker Compose

## Ejecución

1. Clonar el repositorio
2. Navegar al directorio del proyecto:
   ```bash
   cd src/alpespartners
   ```
3. Ejecutar los servicios:
   ```bash
   docker-compose up
   ```

El servicio estará disponible en `http://localhost:8000`

## Endpoints

### 1. Registrar Click
```bash
curl -X POST "http://localhost:8000/v1/tracking/clicks" \
-H "Content-Type: application/json" \
-d '{
    "id_partner": "partner123",
    "id_campana": "campaign456",
    "url_origen": "https://google.com",
    "url_destino": "https://mystore.com/product",
    "metadata_cliente": {
        "user_agent": "Mozilla/5.0",
        "ip_address": "192.168.1.1",
        "referrer": "https://google.com",
        "device_info": {
            "type": "desktop",
            "os": "macOS"
        },
        "location_info": {
            "country": "CO",
            "city": "Bogota"
        }
    }
}'
```

### 2. Registrar Conversión
```bash
curl -X POST "http://localhost:8000/v1/tracking/conversiones" \
-H "Content-Type: application/json" \
-d '{
    "id_partner": "partner123",
    "id_campana": "campaign456",
    "tipo_conversion": "VENTA",
    "informacion_monetaria": {
        "valor": 100.50,
        "moneda": "USD",
        "comision": 10.05,
        "porcentaje_comision": 10.0
    },
    "metadata_cliente": {
        "user_agent": "Mozilla/5.0",
        "ip_address": "192.168.1.1",
        "referrer": "https://google.com",
        "device_info": {
            "type": "desktop",
            "os": "macOS"
        },
        "location_info": {
            "country": "CO",
            "city": "Bogota"
        }
    },
    "id_click": "ID_DEL_CLICK_PREVIO"
}'
```

### 3. Asignar Atribución
```bash
curl -X POST "http://localhost:8000/v1/tracking/atribuciones/ID_DE_LA_CONVERSION" \
-H "Content-Type: application/json" \
-d '{
    "modelo": "ULTIMO_CLICK",
    "porcentaje": 100.0,
    "ventana_atribucion": 30
}'
```

## Arquitectura

- **FastAPI**: API REST
- **PostgreSQL**: Almacenamiento de datos
- **Kafka**: Bus de eventos para publicar eventos de tracking

Cada acción (click, conversión, atribución) genera un evento que se publica en Kafka, permitiendo que otros servicios reaccionen a estos eventos.

## Atributos de calidad
Los atributos de calidad a probar en el proyecto son:
- **Mantenibilidad**
- **Escalabilidad**
- **Disponibilidad**
Para cada uno de estos atributos de calidad se diseñaron 3 escenarios de calidad que se pueden ver a profundidad en la presentación de la entrega 3 del proyecto
