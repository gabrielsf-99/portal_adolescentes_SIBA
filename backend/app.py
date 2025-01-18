from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from plano_leitura import plano

app = Flask(__name__)

# Configuração da chave secreta para sessões
app.secret_key = "sua_chave_secreta_aqui"  # Substitua por algo seguro e único

# Conexão com o banco de dados
def db_connection():
    conn = sqlite3.connect("portal.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return redirect(url_for('login'))

# Página de Cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        endereco = request.form['endereco']
        telefone = request.form['telefone']
        
        conn = db_connection()
        cursor = conn.cursor()
        
        try:
            # Insere o usuário no banco de dados
            cursor.execute(
                "INSERT INTO usuarios (nome, email, senha, endereco, telefone) VALUES (?, ?, ?, ?, ?)",
                (nome, email, senha, endereco, telefone)
            )
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error="Email já cadastrado!")
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        senha = request.form['password']
        
        conn = db_connection()
        cursor = conn.cursor()
        
        # Verifica se o usuário existe
        cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['nome']
            session['user_email'] = user['email']  # Salva o e-mail na sessão
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Email ou senha inválidos!", show_header=False)
    
    return render_template('login.html', show_header=False)


# Página do Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user_name=session['user_name'])

# Página do Devocional
@app.route('/devocional')
def devocional():
    # Conteúdo fictício do devocional
    devocional_do_dia = {
        "titulo": "Confie no Senhor",
        "versiculo": "Provérbios 3:5-6",
        "texto": (
            "Confie no Senhor de todo o seu coração e não se apoie "
            "em seu próprio entendimento. Reconheça o Senhor em todos os seus caminhos, "
            "e ele endireitará as suas veredas."
        ),
        "data": "14 de Janeiro de 2025"
    }
    return render_template('devocional.html', devocional=devocional_do_dia)

# Página do Plano de Leitura
@app.route('/plano_leitura')
def plano_leitura():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM progresso WHERE usuario_id = ?", (session['user_id'],))
    progresso = cursor.fetchall()
    conn.close()
    
    progresso_dict = {(p['mes'], p['dia']): p['concluido'] for p in progresso}
    
    return render_template('plano_leitura.html', progresso=progresso_dict, plano=plano)

# Atualizar Progresso do Plano de Leitura
@app.route('/update_progress', methods=['POST'])
def update_progress():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    dia = request.form['dia']
    mes = request.form['mes']
    concluido = request.form['concluido'] == 'true'
    
    conn = db_connection()
    cursor = conn.cursor()
    
    # Atualiza o progresso do usuário
    cursor.execute("""
        INSERT INTO progresso (usuario_id, dia, mes, concluido)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(usuario_id, dia, mes)
        DO UPDATE SET concluido = ?
    """, (session['user_id'], dia, mes, concluido, concluido))
    conn.commit()
    conn.close()
    return "Progresso atualizado!"

@app.route('/painel_gestao')
def painel_gestao():
    # Verifica se o usuário está logado e se é o líder
    if 'user_id' not in session or session.get('user_email') != "souzafonseca.gsf@gmail.com":
        return redirect(url_for('login'))

    conn = db_connection()
    cursor = conn.cursor()

    # 1. Calcular o progresso geral do grupo
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_itens,
            COUNT(CASE WHEN progresso.concluido = 1 THEN 1 END) AS itens_lidos
        FROM progresso
    """)
    progresso_grupo = cursor.fetchone()
    total_itens = progresso_grupo['total_itens'] or 1  # Evitar divisão por zero
    itens_lidos = progresso_grupo['itens_lidos'] or 0
    progresso_geral = (itens_lidos / total_itens) * 100

    # 2. Calcular o progresso pessoal por mês
    cursor.execute("""
        SELECT 
            usuarios.nome AS usuario,
            progresso.mes,
            COUNT(*) AS total_mes,
            COUNT(CASE WHEN progresso.concluido = 1 THEN 1 END) AS lidos_mes
        FROM usuarios
        LEFT JOIN progresso ON usuarios.id = progresso.usuario_id
        GROUP BY usuarios.nome, progresso.mes
    """)
    progresso_pessoal = cursor.fetchall()

    # Organiza os dados para o gráfico
    progresso_por_mes = {}
    usuarios = set()
    for row in progresso_pessoal:
        mes = row['mes']
        usuario = row['usuario']
        total_mes = row['total_mes'] or 1
        lidos_mes = row['lidos_mes'] or 0
        progresso = (lidos_mes / total_mes) * 100

        usuarios.add(usuario)
        if mes not in progresso_por_mes:
            progresso_por_mes[mes] = {}
        progresso_por_mes[mes][usuario] = round(progresso, 2)

    conn.close()

    return render_template(
        'painel_gestao.html', 
        progresso_geral=round(progresso_geral, 2), 
        progresso_por_mes=progresso_por_mes, 
        usuarios=list(usuarios)
    )



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
