from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
from datetime import datetime

# 1. CONFIGURAÇÃO DO APP
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

# 2. PORTEIRO DE ADMIN
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if current_user.role != 'admin':
            return redirect(url_for('pagina_perfil')) 
        return f(*args, **kwargs)
    return decorated_function

# 3. MODELOS DO BANCO DE DADOS
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    nome = db.Column(db.String(100), nullable=True)
    comentario = db.Column(db.String(500), nullable=False)
    
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
    endereco = db.Column(db.String(255), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(50), nullable=True)
    cep = db.Column(db.String(10), nullable=True)
    
    # Relação com Reservas
    reservas_cliente = db.relationship('Reserva', backref='cliente', lazy=True)

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
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    
    destaques = db.Column(db.String(500), nullable=True) 
    
    reservas_veiculo = db.relationship('Reserva', backref='veiculo_alugado', lazy=True)
    
    def __repr__(self):
        return f'<Veiculo {self.nome}>'

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 

# ==================================
# 6. ROTAS (PÁGINAS) DO SITE
# ==================================

@app.route('/')
def homepage():
    termo_busca = request.args.get('q')
    
    try:
        query = Veiculo.query.filter_by(is_available=True)
        
        if termo_busca:
            # Se houver busca, filtre e aplique o limite de 3
            query = query.filter(
                (Veiculo.nome.ilike(f'%{termo_busca}%')) | 
                (Veiculo.modelo.ilike(f'%{termo_busca}%'))
            ).limit(3) # <--- LIMITE DE 3 CARROS AQUI!
        else:
            # Se não houver busca, mostre apenas os 3 primeiros
            query = query.limit(3) # <--- LIMITE DE 3 CARROS AQUI!

        todos_veiculos = query.all()
        
    except Exception as e:
        todos_veiculos = []
        
    return render_template('index.html', veiculos=todos_veiculos)
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
    reserva_dados = session.get('reserva')
    if not reserva_dados:
        return redirect(url_for('pagina_veiculos'))
        
    try:
        nova_reserva = Reserva(
            data_inicio = datetime.strptime(reserva_dados['data_inicio'], '%Y-%m-%d').date(),
            data_fim = datetime.strptime(reserva_dados['data_fim'], '%Y-%m-%d').date(),
            preco_total = reserva_dados['preco_total'],
            user_id = current_user.id,
            veiculo_id = reserva_dados['carro_id']
        )
        db.session.add(nova_reserva)
        
        # BLOQUEIA O CARRO NO INVENTÁRIO
        carro_reservado = Veiculo.query.get(reserva_dados['carro_id'])
        carro_reservado.is_available = False # Marque como indisponível
        
        db.session.commit() # Salva as duas mudanças (Reserva e Veiculo)
        
    except Exception as e:
        db.session.rollback()
        return "Houve um erro ao salvar sua reserva."
    
    session.pop('reserva', None)
    return redirect(url_for('pagina_pagamento_sucesso'))

@app.route('/feedback')
def pagina_feedback():
    return render_template('feedback.html')

@app.route('/processar-feedback', methods=['POST'])
def processar_feedback():
    if request.method == 'POST':
        rating = request.form['rating']
        nome = request.form['nome_feedback']
        comentario = request.form['comentario_feedback']
        if nome:
            nome_criptografado = cipher.encrypt(nome.encode()).decode()
        else:
            nome_criptografado = None
        novo_feedback = Feedback(
            rating=rating,
            nome=nome_criptografado,
            comentario=comentario
        )
        try:
            db.session.add(novo_feedback)
            db.session.commit()
            return redirect(url_for('homepage'))
        except Exception as e:
            print(e)
            return "Erro ao salvar"
    return redirect(url_for('homepage'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def pagina_admin():
    # 1. Verificação de Permissão
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem acessar esta página.', 'danger')
        return redirect(url_for('homepage'))

    # 2. Lógica para ADICIONAR NOVO VEÍCULO (POST)
    if request.method == 'POST':
        try:
            nome = request.form['nome_veiculo']
            modelo = request.form['modelo_veiculo']
            ano = request.form['ano_veiculo']
            # Garante que o preço seja um float
            preco_diaria = float(request.form['preco_veiculo']) 
            foto_url = request.form['foto_veiculo']
            placa = request.form['placa_veiculo']
            cor = request.form['cor_veiculo']
            destaques = request.form['destaques_veiculo']
            descricao = request.form['desc_veiculo']
            
            # Verificação de unicidade da placa
            if Veiculo.query.filter_by(placa=placa).first():
                flash('Erro: Já existe um veículo com esta placa cadastrado.', 'danger')
                return redirect(url_for('pagina_admin'))

            novo_veiculo = Veiculo(
                nome=nome,
                modelo=modelo,
                ano=ano,
                preco_diaria=preco_diaria,
                foto_url=foto_url,
                placa=placa,
                cor=cor,
                destaques=destaques,
                descricao=descricao
            )
            db.session.add(novo_veiculo)
            db.session.commit()
            print("Foto cadastrada:", foto_url)
            flash('Veículo cadastrado com sucesso!', 'success')
            return redirect(url_for('pagina_admin'))
            
        except ValueError:
            flash('Erro: O preço da diária deve ser um número válido.', 'danger')
            db.session.rollback()
            return redirect(url_for('pagina_admin'))
        except Exception as e:
            flash(f'Erro ao cadastrar veículo: {e}', 'danger')
            db.session.rollback()
            return redirect(url_for('pagina_admin'))

    # 3. Lógica para EXIBIR DADOS (GET)
    try: 
        # ESTA QUERY BUSCA AS RESERVAS, JUNTA COM O NOME DO USUÁRIO E O NOME DO VEÍCULO.
        # É aqui que o sistema "sabe" quem pegou o quê.
        reservas_ativas = db.session.query(Reserva, User, Veiculo).join(User, Reserva.user_id == User.id).join(Veiculo, Reserva.veiculo_id == Veiculo.id).filter(Reserva.status == 'Confirmada').order_by(Reserva.data_inicio.asc()).all()
        
        # Query normal de veículos para a tabela de inventário
        todos_veiculos = Veiculo.query.all() 
        
    except Exception as e: 
        print(f"Erro ao buscar dados: {e}")
        reservas_ativas = []
        todos_veiculos = []

    # 4. Renderiza o template com os dois conjuntos de dados
    return render_template(
        'admin.html', 
        veiculos=todos_veiculos,
        reservas_ativas=reservas_ativas # <--- NOVO: O dado de rastreamento é enviado aqui!
    )
# app.py - ROTA DE PERFIL

@app.route('/perfil')
@login_required
def pagina_perfil():
    
    # === BLOQUEIO DE ADMIN: ===
    if current_user.role == 'admin':
        return redirect(url_for('pagina_admin')) # Admin é sempre redirecionado para o painel!
    
    # === LÓGICA DO CLIENTE (MOSTRAR HISTÓRICO) ===
    try:
        # A query só roda se o usuário for um cliente
        reservas_do_usuario = Reserva.query.filter_by(user_id=current_user.id).order_by(Reserva.data_inicio.desc()).all()
    except Exception as e:
        reservas_do_usuario = []
        
    return render_template('perfil.html', reservas=reservas_do_usuario)

@app.route('/perfil/atualizar_dados', methods=['GET', 'POST'])
@login_required
def atualizar_dados():
    user = current_user
    
    if request.method == 'POST':
        # 1. Atualiza os campos do formulário
        user.nome = request.form.get('nome', user.nome)
        user.telefone = request.form.get('telefone', user.telefone)
        user.endereco = request.form.get('endereco', user.endereco)
        user.cidade = request.form.get('cidade', user.cidade)
        user.estado = request.form.get('estado', user.estado)
        user.cep = request.form.get('cep', user.cep)
        
        # 2. Processa a senha, se foi preenchida
        new_password = request.form.get('new_password')
        if new_password:
            # Hash da nova senha
            user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

        # 3. Salva no banco
        try:
            db.session.commit()
            return redirect(url_for('pagina_perfil'))
        except Exception as e:
            db.session.rollback()
            return f"Erro ao atualizar dados: {e}"

    # GET request: Renderizar o formulário
    return render_template('atualizar_dados.html', user=user)

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
            'carro_id': carro_id,
            'carro_nome': carro.nome,
            'carro_foto': carro.foto_url,
            'data_inicio': data_inicio_str,
            'data_fim': data_fim_str,
            'dias': dias_aluguel,
            'preco_total': preco_total
        }
        return redirect(url_for('pagina_pagamento'))

# app.py - ROTA DE LOGIN

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))

    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, request.form['password']):
            login_user(user, remember=True)
            
            # === VERIFICAÇÃO DE CARGO ===
            if user.role == 'admin':
                return redirect(url_for('pagina_admin')) # ADMIN VAI PARA O PAINEL
            else:
                return redirect(url_for('pagina_perfil')) # CLIENTE VAI PARA O PERFIL
        
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
        end_form = request.form.get('enderecoCadastro')
        cidade_form = request.form.get('cidadeCadastro')
        estado_form = request.form.get('estadoCadastro')
        cep_form = request.form.get('cepCadastro')
        
        user_exists = User.query.filter_by(email=email_form).first()
        if user_exists: return "Erro ao criar usuário. Esse email já existe."
        if cnh_form:
             cnh_exists = User.query.filter_by(cnh=cnh_form).first()
             if cnh_exists: return "Erro ao criar usuário. Essa CNH já está cadastrada."

        hashed_password = bcrypt.generate_password_hash(senha_form).decode('utf-8')
        
        new_user = User(
            username=email_form, email=email_form, nome=nome_form,
            telefone=tel_form, cnh=cnh_form, password_hash=hashed_password,
            endereco=end_form, cidade=cidade_form, estado=estado_form, cep=cep_form
        ) 
        try:
            db.session.add(new_user); db.session.commit()
            login_user(new_user); return redirect(url_for('pagina_cadastro_sucesso'))
        except Exception as e:
            db.session.rollback(); print(f"Erro ao criar usuário: {e}")
            return "Erro ao criar usuário, tente novamente."
    return render_template('clientes.html') 

@app.route('/sobre')
def pagina_sobre():
    return render_template('sobre.html')

@app.route('/veiculo/<int:carro_id>')
def pagina_detalhe_veiculo(carro_id):
    try:
        carro = Veiculo.query.get_or_404(carro_id)
    except Exception as e:
        return redirect(url_for('homepage'))
    return render_template('detalhe_veiculo.html', carro=carro)

@app.route('/veiculos')
def pagina_veiculos():
    # 1. Pega os parâmetros
    termo_busca = request.args.get('q')
    categoria = request.args.get('categoria')
    ano = request.args.get('ano')
    sort_by = request.args.get('sort') 
    
    try:
        # 2. Lógica de Filtragem (igual a que fizemos)
        query = Veiculo.query.filter_by(is_available=True)
        
        if categoria:
            query = query.filter_by(modelo=categoria)
            
        if ano:
            query = query.filter_by(ano=int(ano))
            
        if sort_by == 'asc':
            query = query.order_by(Veiculo.preco_diaria.asc())
        elif sort_by == 'desc':
            query = query.order_by(Veiculo.preco_diaria.desc())
            
        if termo_busca:
             query = query.filter(
                (Veiculo.nome.ilike(f'%{termo_busca}%')) | 
                (Veiculo.modelo.ilike(f'%{termo_busca}%'))
            )
            
        todos_veiculos = query.all()
        
        # === A MUDANÇA ESTÁ AQUI ===
        carro_count = len(todos_veiculos) # Conta os carros
        # ===========================
        
    except Exception as e:
        print(f"Erro ao buscar veículos: {e}")
        todos_veiculos = []
        carro_count = 0 # Se der erro, a contagem é 0
        
    # 3. Envia o count para o template
    return render_template('veiculos.html', 
                           veiculos=todos_veiculos,
                           carro_count=carro_count)
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

@app.route('/cancelar_reserva/<int:reserva_id>', methods=['POST'])
@login_required 
def cancelar_reserva(reserva_id):
    try:
        reserva = Reserva.query.get_or_404(reserva_id)
        if reserva.user_id != current_user.id:
            return "Acesso negado. Esta não é sua reserva."
            
        carro_id = reserva.veiculo_id
        carro = Veiculo.query.get(carro_id)
        reserva.status = 'Cancelada'
        carro.is_available = True
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        return "Erro ao cancelar reserva. Tente novamente."
    return redirect(url_for('pagina_perfil'))

@app.route('/admin/delete_veiculo/<int:carro_id>', methods=['POST'])
@admin_required
def delete_veiculo(carro_id):
    # --- O RECHEIO INTEIRO PRECISA DE 1 RECUO (TAB) ---
    try:
        # 1. Encontra o carro no banco
        carro_para_deletar = Veiculo.query.get_or_404(carro_id)
        
        # 2. Verifique se há reservas ativas
        reservas_ativas = Reserva.query.filter_by(veiculo_id=carro_id, status='Confirmada').first()
        if reservas_ativas:
            print("Tentativa de deletar carro com reservas ativas.")
            return redirect(url_for('pagina_admin'))

        # 3. Se não há reservas, pode deletar
        db.session.delete(carro_para_deletar)
        db.session.commit()
        print(f"Veículo '{carro_para_deletar.nome}' DELETADO do banco.")
        
    except Exception as e:
        print(f"Erro ao deletar veículo: {e}")
        db.session.rollback()

    # Redireciona o usuário de volta para o painel
    return redirect(url_for('pagina_admin'))
@app.route('/admin/toggle_veiculo_status/<int:carro_id>', methods=['POST'])
@admin_required
def toggle_veiculo_status(carro_id):
    try:
        carro = Veiculo.query.get_or_404(carro_id)
        
        # Inverte o valor (Se for True, vira False, e vice-versa)
        carro.is_available = not carro.is_available 
        db.session.commit()
        
    except Exception as e:
        print(f"Erro ao alterar status do veículo: {e}")
        db.session.rollback()

    # Redireciona de volta para o painel
    return redirect(url_for('pagina_admin'))

if __name__ == '__main__':
    app.run(debug=True)
