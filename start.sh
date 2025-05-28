#!/usr/bin/env bash

# Garante que as tabelas do banco de dados sejam criadas usando o script dedicado
python create_db.py

# Inicia o servidor Gunicorn
gunicorn app:app
