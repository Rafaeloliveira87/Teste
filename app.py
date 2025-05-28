from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///brincadeiras.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua_chave_secreta_padrao_muito_segura_e_longa_aqui')

db = SQLAlchemy(app)



# --- DEFINIÇÃO DO MODELO (SUA TABELA 'BRINCADEIRAS') ---
class Brincadeira(db.Model):
    __tablename__ = 'brincadeiras'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(30), unique=True, nullable=False)
    descricao = db.Column(db.String(580), nullable=False)

    def __repr__(self):
        return f'<Brincadeira {self.nome}>'

# --- ROTAS DA APLICAÇÃO ---
# (O restante do seu código de rotas continua igual)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/adicionar')
def adicionar_brincadeira_form():
    return render_template('adicionar.html')

@app.route('/salvar_brincadeira', methods=['POST'])
def salvar_brincadeira():
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        descricao = request.form['descricao'].strip()

        if not nome:
            flash('O nome da brincadeira é obrigatório!', 'error')
            return render_template('adicionar.html', erro='O nome da brincadeira é obrigatório!')
        if not descricao:
            flash('A descrição da brincadeira é obrigatória!', 'error')
            return render_template('adicionar.html', erro='A descrição da brincadeira é obrigatória!')

        existing_brincadeira = Brincadeira.query.filter_by(nome=nome).first()
        if existing_brincadeira:
            flash(f'Já existe uma brincadeira com o nome "{nome}". Por favor, escolha outro.', 'error')
            return render_template('adicionar.html', erro=f'Já existe uma brincadeira com o nome "{nome}".')

        nova_brincadeira = Brincadeira(nome=nome, descricao=descricao)
        try:
            db.session.add(nova_brincadeira)
            db.session.commit()
            flash('Brincadeira adicionada com sucesso!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar a brincadeira: {e}', 'error')
            return render_template('adicionar.html', erro=f'Erro ao salvar a brincadeira: {e}')

@app.route('/selecionar')
def selecionar_brincadeira_form():
    brincadeiras = Brincadeira.query.order_by(Brincadeira.nome).all()
    return render_template('selecionar.html', brincadeiras=brincadeiras)

@app.route('/exibir_descricao', methods=['GET'])
def exibir_descricao():
    brincadeira_id = request.args.get('brincadeira_id')
    if brincadeira_id:
        brincadeira = Brincadeira.query.get(brincadeira_id)
        if brincadeira:
            return render_template('exibir_descricao.html', brincadeira=brincadeira)
        else:
            flash("Brincadeira não encontrada.", 'error')
            return "Brincadeira não encontrada.", 404
    else:
        flash("ID da brincadeira não fornecido.", 'error')
        return "ID da brincadeira não fornecido.", 400

# --- INICIALIZAÇÃO DA APLICAÇÃO LOCAL (SEM ALTERAÇÃO) ---
if __name__ == '__main__':
    # Esta parte é só para rodar localmente com sqlite.
    # No Render, o gunicorn vai iniciar o app e a criação das tabelas já foi feita acima.
    app.run(debug=True)
