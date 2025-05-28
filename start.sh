#!/usr/bin/env bash

# Garante que as tabelas do banco de dados sejam criadas
# Este comando executa um script Python que contém a lógica db.create_all()
python -c "from app import app, db; with app.app_context(): db.create_all()"

# Inicia o servidor Gunicorn
gunicorn app:app
