from sqlalchemy.orm import Session
from alpespartners.config.database import get_db
from alpespartners.modulos.analytics.infraestructura.consumidores import ConsumidorEventos

def main():
    db = next(get_db())
    try:
        consumidor = ConsumidorEventos(db)
        consumidor.iniciar()
    finally:
        db.close()

if __name__ == "__main__":
    main()
