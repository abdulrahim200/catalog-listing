
from backend.app.database import Base, engine
from backend.app.models import ProductModel

Base.metadata.create_all(bind=engine)

print("Database tables created successfully.")
