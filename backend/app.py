from flask import Flask, render_template, request, redirect, url_for

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

@app.route('/dashboard/<user>')
def dashboard(user):
    return f"<h1>Bem-vindo, {user}!</h1><p>Esta é a sua página inicial.</p>"

if __name__ == '__main__':
    app.run(debug=True)
