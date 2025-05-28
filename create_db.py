from app import app, db

print("Tentando criar tabelas no banco de dados...")
with app.app_context():
    db.create_all()
print("Tabelas criadas ou já existentes no banco de dados.")
