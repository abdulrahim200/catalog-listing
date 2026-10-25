from sqlalchemy import text
from backend.app.database import engine

with engine.connect() as connection:
    result = connection.execute(text("SELECT current_database(),version()"))
    print(result.fetchone())

    