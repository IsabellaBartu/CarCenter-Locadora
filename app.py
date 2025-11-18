from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
from datetime import datetime # <-- A IMPORTAÇÃO QUE FALTAVA!

# ==================================
# 2. CONFIGURAÇÃO DO APP
# ==================================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-longa-e-dificil-de-adivinhar'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meu_site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Chave de Criptografia AES
chave_secreta = b'J7gpuJ8t0DAwQshL6C_Rq2RG37_zkrcBtbSQIlJdk7M=' 
cipher = Fernet(chave_secreta)

# ==================================
# 3. PORTEIRO DE ADMIN
# ==================================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if current_user.role != 'admin':
            return redirect(url_for('pagina_perfil')) 
        return f(*args, **kwargs)
    return decorated_function

# ==================================
# 4. MODELOS DO BANCO DE DADOS (Com Reserva!)
# ==================================
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    nome = db.Column(db.String(100), nullable=True)
    comentario = db.Column(db.String(500), nullable=False)
    
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    def __repr__(self):
        return f'<Feedback {self.id}: {self.rating} estrelas>'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False) 
    password_hash = db.Column(db.String(128), nullable=False) 
    role = db.Column(db.String(50), nullable=False, default='cliente')
    nome = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    cnh = db.Column(db.String(20), unique=True, nullable=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Veiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100))
    ano = db.Column(db.Integer)
    preco_diaria = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    foto_url = db.Column(db.String(300), nullable=True)
    placa = db.Column(db.String(10), unique=True, nullable=True)
    cor = db.Column(db.String(50), nullable=True)
    
    def __repr__(self):
        return f'<Veiculo {self.nome}>'

# --- O "MOLDE" DE RESERVA QUE FALTAVA ---
class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_reserva = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    preco_total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Confirmada')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculo.id'), nullable=False)

    def __repr__(self):
        return f'<Reserva {self.id}>'

# ==================================
# 5. CARREGADOR DE USUÁRIO (Flask-Login)
# ==================================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 

# ==================================
# 6. ROTAS (PÁGINAS) DO SITE
# ==================================

@app.route('/')
def homepage():
    try:
        todos_veiculos = Veiculo.query.all()
    except Exception as e:
        todos_veiculos = []
    return render_template('index.html', veiculos=todos_veiculos)

# --- ROTA DE PAGAMENTO (QUE LÊ A SESSÃO) ---
@app.route('/pagamento')
@login_required 
def pagina_pagamento():
    reserva_dados = session.get('reserva')
    if not reserva_dados:
        return redirect(url_for('pagina_veiculos'))
    return render_template('pagamento.html', reserva=reserva_dados)

@app.route('/processar-pagamento', methods=['POST'])
@login_required
def processar_pagamento():
    
    # 1. Puxe os dados da reserva da memória (session)
    reserva_dados = session.get('reserva')
    
    # 2. Verifique se a reserva ainda existe na memória
    if not reserva_dados:
        print("Erro: Usuário tentou pagar sem uma reserva na sessão.")
        return redirect(url_for('pagina_veiculos'))
        
    # --- INÍCIO DA LÓGICA DE SALVAR E BLOQUEAR ---
    try:
        # 3. Crie o objeto "Reserva" (SALVANDO)
        nova_reserva = Reserva(
            data_inicio = datetime.strptime(reserva_dados['data_inicio'], '%Y-%m-%d').date(),
            data_fim = datetime.strptime(reserva_dados['data_fim'], '%Y-%m-%d').date(),
            preco_total = reserva_dados['preco_total'],
            user_id = current_user.id,
            veiculo_id = reserva_dados['carro_id']
        )
        
        # 4. SALVE A RESERVA NO BANCO DE DADOS
        db.session.add(nova_reserva)
        db.session.commit()
        print(f"Nova reserva {nova_reserva.id} salva no banco!")
        
        # 5. BLOQUEIA O CARRO NO INVENTÁRIO (O que você queria!)
        carro_reservado = Veiculo.query.get(reserva_dados['carro_id'])
        carro_reservado.is_available = False # Marque como indisponível
        db.session.commit() # Salve essa mudança também!
        print(f"Veículo '{carro_reservado.nome}' marcado como INDISPONÍVEL.")
            
    except Exception as e:
        # Se falhar, desfaz a transação e mostra o erro
        db.session.rollback()
        print(f"Erro ao SALVAR reserva no banco: {e}")
        return "Houve um erro ao salvar sua reserva."
    
    # 6. LIMPE A MEMÓRIA E REDIRECIONE PARA O SUCESSO
    session.pop('reserva', None)
    return redirect(url_for('pagina_pagamento_sucesso'))

@app.route('/feedback')
def pagina_feedback():
    return render_template('feedback.html')

@app.route('/processar-feedback', methods=['POST'])
def processar_feedback():
    if request.method == 'POST':
        # ... (código de processar feedback) ...
        pass # (Resumido para economizar espaço)
    return redirect(url_for('homepage'))

# --- ROTA DE ADMIN (QUE ADICIONA CARRO) ---
@app.route('/admin', methods=['GET', 'POST'])
@admin_required
def pagina_admin():
    if request.method == 'POST':
        nome = request.form.get('nome_veiculo')
        modelo = request.form.get('modelo_veiculo')
        ano = request.form.get('ano_veiculo')
        preco = request.form.get('preco_veiculo')
        descricao = request.form.get('desc_veiculo')
        foto = request.form.get('foto_veiculo')
        placa = request.form.get('placa_veiculo')
        cor = request.form.get('cor_veiculo')
        
        novo_veiculo = Veiculo(
            nome=nome, modelo=modelo, ano=int(ano), preco_diaria=float(preco),
            descricao=descricao, foto_url=foto, placa=placa, cor=cor
        )
        try:
            db.session.add(novo_veiculo)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        return redirect(url_for('pagina_admin'))
    
    # Lógica GET (Mostrar tudo)
    try:
        todos_feedbacks_db = Feedback.query.order_by(Feedback.id.desc()).all()
        lista_feedbacks_para_exibir = []
        for item in todos_feedbacks_db:
            nome_real = "Anônimo"
            if item.nome:
                try: nome_real = cipher.decrypt(item.nome.encode()).decode()
                except: nome_real = item.nome
            feedback_temp = {'id': item.id, 'rating': item.rating, 'nome': nome_real, 'comentario': item.comentario}
            lista_feedbacks_para_exibir.append(feedback_temp)
    except: lista_feedbacks_para_exibir = []
    try: todos_usuarios = User.query.all()
    except: todos_usuarios = []
    try: todos_veiculos = Veiculo.query.all()
    except: todos_veiculos = []

    return render_template(
        'admin.html', 
        feedbacks=lista_feedbacks_para_exibir, 
        usuarios=todos_usuarios,
        veiculos=todos_veiculos
    )

@app.route('/admin/toggle/<int:carro_id>', methods=['POST'])
@admin_required
def toggle_veiculo_status(carro_id):
    try:
        carro = Veiculo.query.get_or_404(carro_id)
        
        # Inverte o valor (Se for True, vira False, e vice-versa)
        carro.is_available = not carro.is_available 
        db.session.commit()
        
        print(f"Status do carro {carro.nome} alterado para {carro.is_available}")
        
    except Exception as e:
        print(f"Erro ao alterar status do veículo: {e}")
        db.session.rollback()

    # Redireciona de volta para o painel
    return redirect(url_for('pagina_admin'))

# --- ROTA DE PERFIL (QUE LÊ AS RESERVAS!) ---
@app.route('/perfil')
@login_required
def pagina_perfil():
    try:
        reservas_do_usuario = db.session.query(Reserva, Veiculo).join(Veiculo).filter(Reserva.user_id == current_user.id).order_by(Reserva.data_inicio.desc()).all()
    except Exception as e:
        print(f"Erro ao buscar reservas: {e}")
        reservas_do_usuario = []
    return render_template('perfil.html', reservas=reservas_do_usuario)

# --- ROTA DE INICIAR RESERVA (QUE SALVA NA SESSÃO) ---
@app.route('/iniciar-reserva', methods=['POST'])
@login_required
def iniciar_reserva():
    if request.method == 'POST':
        carro_id = request.form.get('carro_id')
        data_inicio_str = request.form.get('data_inicio')
        data_fim_str = request.form.get('data_fim')
        
        carro = Veiculo.query.get(carro_id)
        
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
            diff = data_fim - data_inicio
            dias_aluguel = diff.days
            
            if dias_aluguel <= 0:
                return "Erro: A data de devolução deve ser depois da data de retirada."
            
            preco_total = dias_aluguel * carro.preco_diaria
        except Exception as e:
            return "Erro ao processar as datas."

        session['reserva'] = {
            'carro_id': carro_id, # <-- O ID que faltava
            'carro_nome': carro.nome,
            'carro_foto': carro.foto_url,
            'data_inicio': data_inicio_str,
            'data_fim': data_fim_str,
            'dias': dias_aluguel,
            'preco_total': preco_total
        }
        return redirect(url_for('pagina_pagamento'))

# --- ROTAS DE LOGIN/LOGOUT/REGISTER (JÁ ESTAVAM OK) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and bcrypt.check_password_hash(user.password_hash, request.form['password']):
            login_user(user, remember=True)
            if user.role == 'admin':
                return redirect(url_for('pagina_admin'))
            else:
                return redirect(url_for('pagina_perfil'))
        else:
            return render_template('login.html', error="Usuário ou senha inválidos.")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    if request.method == 'POST':
        email_form = request.form.get('emailCadastro')
        nome_form = request.form.get('nomeCadastro')
        tel_form = request.form.get('telCadastro')
        cnh_form = request.form.get('cnhCliente')
        senha_form = request.form.get('senhaCadastro')
        user_exists = User.query.filter_by(email=email_form).first()
        if user_exists:
            return "Erro ao criar usuário. Esse email já existe."
        if cnh_form:
             cnh_exists = User.query.filter_by(cnh=cnh_form).first()
             if cnh_exists:
                 return "Erro ao criar usuário. Essa CNH já está cadastrada."
        hashed_password = bcrypt.generate_password_hash(senha_form).decode('utf-8')
        new_user = User(
            username=email_form, email=email_form, nome=nome_form,
            telefone=tel_form, cnh=cnh_form, password_hash=hashed_password
        ) 
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user) 
            return redirect(url_for('pagina_cadastro_sucesso')) 
        except Exception as e:
            db.session.rollback(); print(f"Erro ao criar usuário: {e}")
            return "Erro ao criar usuário, tente novamente."
    return render_template('clientes.html') 

# --- ROTAS DE PÁGINAS ESTÁTICAS (JÁ ESTAVAM OK) ---
@app.route('/sobre')
def pagina_sobre():
    return render_template('sobre.html')

@app.route('/veiculo/<int:carro_id>')
def pagina_detalhe_veiculo(carro_id):
    # 1. Busca no banco o carro com AQUELE ID
    try:
        # get_or_404 é um atalho que já dá erro 404 se não achar
        carro = Veiculo.query.get_or_404(carro_id)
    except Exception as e:
        print(e)
        return redirect(url_for('homepage')) # Se não achar, volta pra Home
    
    # 2. Mostra a nova página de detalhes e envia os dados do carro
    return render_template('detalhe_veiculo.html', carro=carro)

@app.route('/veiculos')
def pagina_veiculos():
    try:
        todos_veiculos = Veiculo.query.all()
    except Exception as e:
        todos_veiculos = []
    return render_template('veiculos.html', veiculos=todos_veiculos)

@app.route('/tutorial')
def pagina_tutorial():
    return render_template('tutorial.html')

@app.route('/cadastro-sucesso')
@login_required 
def pagina_cadastro_sucesso():
    return render_template('cadastro-sucesso.html')

@app.route('/pagamento-sucesso')
def pagina_pagamento_sucesso():
    return render_template('pagamento-sucesso.html')

# ==================================
# 7. INICIA O SERVIDOR
# ==================================
if __name__ == '__main__':
    app.run(debug=True)