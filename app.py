from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
# A URL do banco de dados virá de uma variável de ambiente no Render ('DATABASE_URL').
# Se não encontrar (por exemplo, rodando localmente), ele usará SQLite.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///brincadeiras.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Boa prática para evitar warnings
# A SECRET_KEY é essencial para a segurança do Flask, especialmente para 'flash messages'.
# No Render, você a definirá como uma variável de ambiente. Localmente, usa um valor padrão.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua_chave_secreta_padrao_muito_segura_e_longa_aqui')

db = SQLAlchemy(app) # Inicializa o SQLAlchemy com seu app Flask

# --- DEFINIÇÃO DO MODELO (SUA TABELA 'BRINCADEIRAS') ---
# Esta classe representa a tabela 'brincadeiras' no seu banco de dados.
class Brincadeira(db.Model):
    __tablename__ = 'brincadeiras' # O nome real da tabela no DB

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(30), unique=True, nullable=False) # 'unique=True' garante que nomes de brincadeiras são únicos
    descricao = db.Column(db.String(580), nullable=False)

    def __repr__(self):
        return f'<Brincadeira {self.nome}>'

# --- ROTAS DA APLICAÇÃO ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/adicionar')
def adicionar_brincadeira_form():
    return render_template('adicionar.html')

@app.route('/salvar_brincadeira', methods=['POST'])
def salvar_brincadeira():
    if request.method == 'POST':
        nome = request.form['nome'].strip() # .strip() remove espaços em branco extras
        descricao = request.form['descricao'].strip()

        # Validação de campos vazios
        if not nome:
            flash('O nome da brincadeira é obrigatório!', 'error')
            return render_template('adicionar.html', erro='O nome da brincadeira é obrigatório!')
        if not descricao:
            flash('A descrição da brincadeira é obrigatória!', 'error')
            return render_template('adicionar.html', erro='A descrição da brincadeira é obrigatória!')

        # Verifica se a brincadeira já existe pelo nome
        existing_brincadeira = Brincadeira.query.filter_by(nome=nome).first()
        if existing_brincadeira:
            flash(f'Já existe uma brincadeira com o nome "{nome}". Por favor, escolha outro.', 'error')
            return render_template('adicionar.html', erro=f'Já existe uma brincadeira com o nome "{nome}".')

        nova_brincadeira = Brincadeira(nome=nome, descricao=descricao)
        try:
            db.session.add(nova_brincadeira) # Adiciona a nova brincadeira à sessão do banco de dados
            db.session.commit() # Salva as mudanças permanentemente no banco de dados
            flash('Brincadeira adicionada com sucesso!', 'success') # Mensagem de sucesso
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback() # Em caso de erro, desfaz a operação no banco de dados
            flash(f'Erro ao salvar a brincadeira: {e}', 'error')
            return render_template('adicionar.html', erro=f'Erro ao salvar a brincadeira: {e}')

@app.route('/selecionar')
def selecionar_brincadeira_form():
    # Consulta todas as brincadeiras do banco de dados e as ordena por nome
    brincadeiras = Brincadeira.query.order_by(Brincadeira.nome).all()
    return render_template('selecionar.html', brincadeiras=brincadeiras)

@app.route('/exibir_descricao', methods=['GET'])
def exibir_descricao():
    brincadeira_id = request.args.get('brincadeira_id')
    if brincadeira_id:
        # Busca a brincadeira pelo ID no banco de dados
        brincadeira = Brincadeira.query.get(brincadeira_id)
        if brincadeira:
            return render_template('exibir_descricao.html', brincadeira=brincadeira)
        else:
            flash("Brincadeira não encontrada.", 'error')
            return "Brincadeira não encontrada.", 404
    else:
        flash("ID da brincadeira não fornecido.", 'error')
        return "ID da brincadeira não fornecido.", 400

# --- INICIALIZAÇÃO DA APLICAÇÃO ---
if __name__ == '__main__':
    # Cria as tabelas no banco de dados (se elas não existirem)
    # Isso é feito dentro de um 'app context' para que o SQLAlchemy funcione corretamente
    with app.app_context():
        db.create_all()
    app.run(debug=True) # debug=True é bom para desenvolvimento local