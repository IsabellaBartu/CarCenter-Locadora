# init_db.py

from app import app, db, bcrypt, User, Veiculo, Feedback

print("Iniciando a criação do banco de dados...")

# Deleta o banco antigo (se existir) e cria um novo
with app.app_context():
    
    # 1. Crie todas as tabelas (User, Feedback, Veiculo)
    db.drop_all() # Apaga tudo (só para garantir)
    db.create_all() # Cria do zero

    print("Tabelas criadas com sucesso.")

    # 2. Crie o usuário Admin (com os campos novos)
    hash_admin = bcrypt.generate_password_hash('senhaforte123').decode('utf-8')
    
    admin_user = User(
        username='admin@email.com', 
        password_hash=hash_admin, 
        role='admin',
        email='admin@email.com',
        nome='Administrador',
        telefone='(00) 00000-0000', # Adicionado
        cnh='00000000000'         # Adicionado
    )
    
    # 3. Salve o Admin no banco
    db.session.add(admin_user)
    db.session.commit()

    print("=============================================")
    print("Banco NOVO (com Veiculos) recriado com ADMIN!")
    print("Usuário: admin@email.com")
    print("Senha:   senhaforte123")
    print("=============================================")
    print("Pode manter este arquivo para futuras atualizações!")