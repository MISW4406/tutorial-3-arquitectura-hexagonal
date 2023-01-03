# Tutorial 3 - Arquitectura Hexagonal

Repositorio con código base para el desarrollo de una arquitectura hexagonal siguiendo los principios y patrones de DDD.


## Estructura del proyecto

El repositorio en su raíz está estructurado de la siguiente forma:

- **.github**: Directorio donde se localizan templates para Github y los CI/CD workflows 
- **src**: En este directorio encuentra el código fuente para AeroAlpes. En la siguiente sección se explica un poco mejor la estructura del mismo ([link](https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure%3E) para más información)
- **tests**: Directorio con todos los archivos de prueba, tanto unitarios como de integración. Sigue el estándar [recomendado por pytest](https://docs.pytest.org/en/7.1.x/explanation/goodpractices.html) y usado por [boto](https://github.com/boto/boto).
- **.gitignore**: Archivo con la definición de archivos que se deben ignorar en el repositorio GIT
- **.gitpod.yml**: Archivo que define las tareas/pasos a ejecutar para configurar su workspace en Gitpod
- **README.md**: El archivo que está leyendo :)
- **requirements.txt**: Archivo con los requerimientos para el correcto funcionamiento del proyecto (librerias Python)


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

- **Endpoint**: `/vuelos/reserva`
- **Método**: `POST`
- **Headers**: `Content-Type='aplication/json'`

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

### Ver Reserva(s)

- **Endpoint**: `/vuelos/reserva/{id}`
- **Método**: `GET`
- **Headers**: `Content-Type='aplication/json'`

## Ejecutar pruebas

```bash
coverage run -m pytest
```

# Ver reporte de covertura
```bash
coverage report
```
