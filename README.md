# Tutorial 3 - Arquitectura Hexagonal

Repositorio con código base para el desarrollo de una arquitectura hexagonal siguiendo los principios y patrones de DDD.


## Ejecutar Aplicación

Desde el directorio principal ejecute el siguiente comando.

```bash
flask --app src/aeroalpes/api run
```

Siempre puede ejecutarlo en modo DEBUG:

```bash
flask --app src/aeroalpes/api --debug run
```


## Request de ejemplo

Los siguientes JSON pueden ser usados para probar el API:

### Reservar

**Endpoint**: `/vuelos/reserva`
**Método**: `POST`
**Headers**: 

```json
{
    "itinerarios": [
        {
            "odos": [
                {
                    "segmentos": [
                        {
                            "legs": [
                                {
                                    "fecha_salida": "2022-11-22T13:10:00Z",
                                    "fecha_llegada": "2022-11-22T15:10:00Z",
                                    "destino": {
                                        "codigo": "JFK",
                                        "nombre": "John F. Kennedy International Airport"
                                    },
                                    "origen": {
                                        "codigo": "BOG",
                                        "nombre": "El Dorado - Bogotá International Airport (BOG)"
                                    }

                                }
                            ]
                        }
                    ]
                }

            ]
        }
    ]
}
```