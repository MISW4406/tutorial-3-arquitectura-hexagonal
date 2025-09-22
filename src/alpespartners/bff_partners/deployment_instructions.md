## Pasos para desplegar el BFF de Alpes Partners

### 1. Estructura de directorios
```
proyecto/
├── src/
│   ├── alpespartners/          # Microservicios existentes
│   └── bff_partners/           # Nuevo BFF
│       ├── main.py
│       ├── api/
│       ├── consumidores.py
│       ├── despachadores.py
│       ├── utils.py
│       ├── requirements.txt
│       └── Dockerfile
├── docker-compose.yml          # Actualizado con BFF
└── bff_partners_collection.json # Postman collection
```

### 2. Variables de entorno necesarias
```bash
ALPES_PARTNERS_HOST=localhost    # Host del servicio principal
ALPES_PARTNERS_PORT=8000         # Puerto del servicio principal  
PULSAR_SERVICE_URL=pulsar://localhost:6650
PULSAR_ADMIN_URL=http://localhost:8080
```

### 3. Comandos de despliegue
```bash
# 1. Construir y levantar todos los servicios
docker-compose up --build

# 2. Verificar que el BFF esté funcionando
curl http://localhost:8080/health

# 3. Acceder a GraphQL Playground
# Ir a: http://localhost:8080/v1/graphql
```

### 4. URLs importantes
- **BFF GraphQL**: http://localhost:8080/v1/graphql
- **BFF Health**: http://localhost:8080/health  
- **BFF Events Stream**: http://localhost:8080/stream
- **Microservicios**: http://localhost:8000

### 5. Probar con Postman
1. Importar `bff_partners_collection.json`
2. Configurar variable `BFF_URL = http://localhost:8080`
3. Ejecutar requests de ejemplo

### 6. Monitoreo
- Los eventos se pueden ver en tiempo real en `/stream`
- Los logs de cada servicio están disponibles via `docker-compose logs`
- GraphQL Playground permite explorar el schema interactivamente