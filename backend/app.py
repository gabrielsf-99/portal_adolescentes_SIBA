from flask import Flask, render_template, request, redirect, url_for
from plano_leitura import plano

app = Flask(__name__)

# Usuários fictícios para teste
usuarios = {"lider": "1234", "usuario": "abcd"}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in usuarios and usuarios[username] == password:
            return redirect(url_for('dashboard', user=username))
        else:
            return render_template('login.html', error="Usuário ou senha inválidos!", show_header=False)
    
    return render_template('login.html', show_header=False)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', show_title=False)

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


@app.route('/plano_leitura')
def plano_leitura():
    return render_template('plano_leitura.html', plano=plano, show_title=False)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
