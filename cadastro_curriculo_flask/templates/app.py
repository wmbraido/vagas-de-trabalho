from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'chave_super_secreta'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        if usuario == 'admin' and senha == 'admin123':
            session['perfil'] = 'admin'
        else:
            session['perfil'] = 'usuario'
        return redirect(url_for('index'))
    return render_template('login.html', perfil=session.get('perfil'))

# --------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.pop('perfil', None)
    return redirect(url_for('login'))

# --------- CADASTRO DE CURRÍCULOS ----------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        area = request.form['area']
        experiencia = request.form['experiencia']
        arquivo = request.files['curriculo']

        if arquivo and arquivo.filename.endswith('.pdf'):
            caminho_arquivo = os.path.join(UPLOAD_FOLDER, arquivo.filename)
            arquivo.save(caminho_arquivo)
        else:
            caminho_arquivo = ''

        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS curriculos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT, email TEXT, telefone TEXT,
                area TEXT, experiencia TEXT, arquivo TEXT
            )
        ''')
        cursor.execute('''
            INSERT INTO curriculos (nome, email, telefone, area, experiencia, arquivo)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nome, email, telefone, area, experiencia, arquivo.filename if arquivo else ''))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('index.html', perfil=session.get('perfil'))

# --------- LISTAR CURRÍCULOS (ADMIN) ----------
@app.route('/curriculos')
def listar_curriculos():
    if session.get('perfil') != 'admin':
        return "Acesso negado. Somente administradores podem ver os relatórios."

    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, telefone, area, experiencia, arquivo FROM curriculos")
    curriculos = cursor.fetchall()
    conn.close()
    return render_template('lista.html', curriculos=curriculos, perfil=session.get('perfil'))

# --------- APAGAR CURRÍCULO ----------
@app.route('/curriculos/apagar/<int:id>', methods=['POST'])
def apagar_curriculo(id):
    if session.get('perfil') != 'admin':
        return "Acesso negado."

    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM curriculos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('listar_curriculos'))

# --------- DOWNLOAD DE ARQUIVOS ----------
@app.route('/uploads/<nome_arquivo>')
def download_arquivo(nome_arquivo):
    return send_from_directory(UPLOAD_FOLDER, nome_arquivo)

# --------- CADASTRO E LISTAGEM DE VAGAS ----------
@app.route('/vagas', methods=['GET', 'POST'])
def vagas():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vagas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            empresa TEXT NOT NULL,
            descricao TEXT NOT NULL,
            contato TEXT NOT NULL
        )
    ''')

    if request.method == 'POST':
        titulo = request.form['titulo']
        empresa = request.form['empresa']
        descricao = request.form['descricao']
        contato = request.form['contato']

        cursor.execute('''
            INSERT INTO vagas (titulo, empresa, descricao, contato)
            VALUES (?, ?, ?, ?)
        ''', (titulo, empresa, descricao, contato))
        conn.commit()

    cursor.execute("SELECT id, titulo, empresa, descricao, contato FROM vagas ORDER BY id DESC")
    vagas = cursor.fetchall()
    conn.close()
    return render_template('vagas.html', vagas=vagas, perfil=session.get('perfil'))

# --------- APAGAR VAGA ----------
@app.route('/vagas/apagar/<int:id>', methods=['POST'])
def apagar_vaga(id):
    if session.get('perfil') != 'admin':
        return "Acesso negado."

    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM vagas WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('vagas'))

# --------- LISTAGEM PÚBLICA DAS VAGAS ----------
@app.route('/ver-vagas')
def ver_vagas():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo, empresa, descricao, contato FROM vagas ORDER BY id DESC")
    vagas = cursor.fetchall()
    conn.close()
    return render_template('ver_vagas.html', vagas=vagas, perfil=session.get('perfil'))

# --------- RODAR O SERVIDOR ----------
if __name__ == '__main__':
    app.run(debug=True)



