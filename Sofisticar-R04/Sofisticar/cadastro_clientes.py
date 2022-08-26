from ast import FunctionDef
from asyncio.windows_events import NULL
from distutils.log import info
from doctest import debug
from pickle import TRUE
from sre_constants import SUCCESS

from flask import Flask, flash, redirect, render_template, request, url_for,Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (Column, Date, ForeignKey, Integer, String, Table,
                        create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


app = Flask(__name__, template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clientes.db'

db = SQLAlchemy(app)


# Classe do Veículo
class Veiculo(db.Model):
    __tablename__ = 'veiculos'
    id = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    marca = db.Column('Marca', db.String(150), nullable=False)
    modelo = db.Column('Modelo', db.String(150), nullable=False)
    cor = db.Column('Cor', db.String(150), nullable=False)
    placa = db.Column('Placa', db.String(150), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.ID'))
    cliente = relationship('Cliente')

    def __init__(self, marca, modelo, cor, placa, cliente):
        self.marca = marca
        self.modelo = modelo
        self.cor = cor
        self.placa = placa
        self.cliente = cliente


# Classe do Cliente
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column('Nome', db.String(150), nullable=False)
    email = db.Column('Email', db.String(150), nullable=False)
    telefone = db.Column('Telefone', db.String(150), nullable=False)
    celular = db.Column('Celular', db.String(150), nullable=False)
    veiculos = relationship(Veiculo, backref="clientes")

    def __init__(self, nome, email, telefone, celular):
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.celular = celular


# Classe do Funcionário
class Funcionario(db.Model):
    __tablename__ = 'funcionarios'
    id = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column('Nome', db.String(150), nullable=False)
    email = db.Column('Email', db.String(150), nullable=False)
    telefone = db.Column('Telefone', db.String(150), nullable=False)
    celular = db.Column('Celular', db.String(150), nullable=False)
    dataAniversario = db.Column(
        'Data Aniversário', db.String(10), nullable=False)
    dataContrato = db.Column('Data Contrato', db.String(10), nullable=False)
    funcao = db.Column('Função', db.String(150), nullable=False)
    senha = db.Column('Senha', db.String(50))

    def __init__(self, nome, email, telefone, celular, dataAniversario, dataContrato, funcao, senha):
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.celular = celular
        self.dataAniversario = dataAniversario
        self.dataContrato = dataContrato
        self.funcao = funcao
        self.senha = None


'''
class Servico(db.Model):
    __tablename__ = 'servicos'
    id = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column('Nome', db.String(150), nullable=False)
    descricao = db.Column('Descrição', db.String(250), nullable=False)
    valor = db.Column('Valor', db.String(20), nullable=False)

    def __init__(self, nome, descricao, valor):
        self.nome = nome
        self.descricao = descricao
        self.valor = valor
'''


class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column('Nome', db.String(150), nullable=False)
    descricao = db.Column('Descrição', db.String(250), nullable=False)
    valor = db.Column('Valor', db.String(20), nullable=False)

    def __init__(self, nome, descricao, valor):
        self.nome = nome
        self.descricao = descricao
        self.valor = valor
             


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    #remember = True if request.form.get('remember') else False

    user = Funcionario.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    #if not user or not check_password_hash(user.senha, password):
    if user == None:
        flash('Usuario ou senha incorreto')
        return redirect(url_for('login'))

    if user.senha == password:
        return redirect(url_for('index')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    flash('Usuario ou senha incorreto')
    return redirect(url_for('login'))


#region 
@app.route('/validalogin/<string:_email>/<string:_senha>',methods=['GET'])
def valida_login(_email,_senha):
    funcionario = Funcionario.query.filter_by(email=_email).first()

    if funcionario.senha == None:
        return SUCCESS
    elif funcionario.senha == _senha:
        return "Sucesso"
    elif funcionario == None:
        return "Não encontrado"


#endregion

@app.route('/index')
def index():
    cliente = Cliente.query.all()
    return render_template("index.html", clientes=cliente)


@app.route('/cadastrar_clientes', methods=['GET', 'POST'])
def adiciona_cliente():
    if request.method == 'POST':
        cliente = Cliente(request.form['nome'], request.form['email'],
                          request.form['telefone'], request.form['celular'])
        veiculo = Veiculo(request.form['marca'], request.form['modelo'],
                          request.form['cor'], request.form['placa'], cliente)
        if cliente.nome == '' or cliente.celular == '':
            mensagem = 'Não deixe campos obrigatórios em branco!'
            return render_template('cadastrar_clientes.html', mensagem=mensagem)
        elif veiculo.marca == '' or veiculo.modelo == '' or veiculo.cor == '' or veiculo.placa == '':
            mensagem = 'Não deixe campos obrigatórios em branco!'
            return render_template('cadastrar_clientes.html', mensagem=mensagem)
        else:
            db.session.add(cliente)
            db.session.add(veiculo)
            db.session.commit()
            mensagem_sucesso = f'{cliente.nome.upper()} foi cadastrado(a) com SUCESSO!'
            return render_template('cadastrar_clientes.html', mensagem_ok=mensagem_sucesso)
    return render_template('cadastrar_clientes.html')


@app.route('/consultar_clientes', methods=['GET', 'POST'])
def consulta_cliente():
    if request.method == 'POST':
        return redirect(url_for('resultado_cliente'))
    return render_template("consultar_clientes.html")


@app.route('/resultado_clientes', methods=['GET', 'POST'])
def resultado_cliente():
    cliente = Cliente.query.all()
    veiculo = Veiculo.query.all()
    mensagem_info = 'Pesquise por informações do cliente ou deixe em branco para retornar todos os resultados.'
    if request.method == 'POST':
        opcao = request.form['opcao_cliente']  # pega a informação das opções
        # pega a informação do que foi preenchido
        campo = request.form['campo_cliente']
        return render_template("resultado_clientes.html", clientes=cliente, veiculos=veiculo, opcao_cliente=opcao, campo_cliente=campo)
    return render_template("resultado_clientes.html", mensagem_info=mensagem_info)


@app.route('/editar_clientes/<int:id>', methods=['GET', 'POST'])
def edita_cliente(id):
    cliente = Cliente.query.get(id)
    veiculo = Veiculo.query.all()
    if request.method == 'POST':
        # salva com as novas informações inseridas
        cliente.nome = request.form['nome']
        cliente.email = request.form['email']
        cliente.telefone = request.form['telefone']
        cliente.celular = request.form['celular']
        db.session.commit()
        # validação
        mensagem = f"{cliente.nome} foi editado(a) com sucesso! Clique novamente em pesquisar para ver os registros!"
        return render_template("resultado_clientes.html", mensagem_editar=mensagem, veiculos=veiculo)
    return render_template('editar_clientes.html', cliente=cliente, veiculos=veiculo)


@app.route('/deletar_clientes/<int:id>')
def deleta_cliente(id):
    cliente = Cliente.query.get(id)
    db.session.delete(cliente)  # deleta os dados daquele cliente
    db.session.commit()
    # validação
    mensagem = f"{cliente.nome} foi DELETADO(A)! Clique novamente em pesquisar para ver os registros!"
    return render_template("resultado_clientes.html", mensagem_deletar = mensagem)
    # return render_template("resultado_clientes.html", mensagem_deletar = mensagem)


@app.route('/info_clientes/<int:id>')
def info_cliente(id):
    cliente = Cliente.query.get(id)
    veiculo = Veiculo.query.all()
    return render_template('info_clientes.html', cliente=cliente, veiculos=veiculo)


@app.route('/cadastrar_veiculo', methods=['GET', 'POST'])
def cadastro_veiculo():
    cliente = Cliente.query.all()
    mensagem_info = 'Pesquise por informações do cliente ou deixe em branco para retornar todos os resultados.'
    if request.method == 'POST':
        opcao = request.form['opcao_cliente']  # pega a informação das opções
        # pega a informação do que foi preenchido
        campo = request.form['campo_cliente']
        return render_template("cadastrar_veiculo.html", clientes=cliente, opcao_cliente=opcao, campo_cliente=campo)
    return render_template("cadastrar_veiculo.html", mensagem_info=mensagem_info)


@app.route('/veiculos/<int:id>', methods=['GET', 'POST'])
def adiciona_veiculo(id):
    cliente = Cliente.query.get(id)
    veiculo_cliente = Veiculo.query.all()
    if request.method == 'POST':
        veiculo = Veiculo(request.form['marca'], request.form['modelo'],
                          request.form['cor'], request.form['placa'], cliente)
        if veiculo.marca == '' or veiculo.modelo == '' or veiculo.cor == '' or veiculo.placa == '':
            mensagem = 'Não deixe campos obrigatórios em branco!'
            return render_template('veiculos.html', cliente=cliente, veiculos=veiculo_cliente, mensagem=mensagem)
        else:
            db.session.add(veiculo)
            db.session.commit()
            mensagem_sucesso = f'Veículo cadastrado com SUCESSO!'
            flash(mensagem_sucesso, 'info')
            return redirect(f'/veiculos/{cliente.id}')
            # return render_template('veiculos.html', cliente = cliente, veiculos = veiculo_cliente, mensagem_sucesso = mensagem_sucesso)
    return render_template('veiculos.html', cliente=cliente, veiculos=veiculo_cliente)


@app.route('/editar_veiculo/<int:id>', methods=['GET', 'POST'])
def edita_veiculo(id):
    veiculo = Veiculo.query.get(id)
    id_cliente = veiculo.cliente_id
    cliente = Cliente.query.get(id_cliente)
    if request.method == 'POST':
        # salva com as novas informações inseridas
        veiculo.marca = request.form['marca']
        veiculo.modelo = request.form['modelo']
        veiculo.cor = request.form['cor']
        veiculo.placa = request.form['placa']
        db.session.commit()
        mensagem_sucesso = f'Veículo editado com SUCESSO!'
        return render_template("veiculos.html", mensagem_sucesso=mensagem_sucesso, cliente=cliente, veiculo=veiculo)
    return render_template("editar_veiculo.html", cliente=cliente, veiculo=veiculo)


@app.route('/deletar_veiculo/<int:id>')
def deleta_veiculo(id):
    veiculo = Veiculo.query.get(id)
    id_cliente = veiculo.cliente_id
    cliente = Cliente.query.get(id_cliente)
    db.session.delete(veiculo)
    db.session.commit()
    mensagem = f"Veículo placa {veiculo.placa} foi DELETADO(A)!"  # validação
    flash(mensagem, 'error')
    return redirect(f'/veiculos/{cliente.id}')
    # return render_template("veiculos.html", cliente = cliente, mensagem_deletar = mensagem)


@app.route('/cadastrar_funcionario', methods=['GET', 'POST'])
def adiciona_funcionario():
    if request.method == 'POST':
        funcionario = Funcionario(request.form['nome'], request.form['email'], request.form['telefone'],
                                  request.form['celular'], request.form['dataAniversario'], request.form['dataContrato'], request.form['funcao'], senha=None)
        if funcionario.nome == '' or funcionario.celular == '' or funcionario.dataAniversario == '' or funcionario.dataContrato == '' or funcionario.funcao == '':
            mensagem = 'Não deixe campos obrigatórios em branco!'
            return render_template('cadastrar_funcionario.html', mensagem=mensagem)
        else:
            db.session.add(funcionario)
            db.session.commit()
            mensagem_sucesso = f'{funcionario.nome.upper()} foi cadastrado(a) com SUCESSO!'
            return render_template('cadastrar_funcionario.html', mensagem_ok=mensagem_sucesso)
    return render_template('cadastrar_funcionario.html')


@app.route('/resultado_funcionarios', methods=['GET', 'POST'])
def resultado_funcionario():
    funcionario = Funcionario.query.all()
    opcao = ''
    campo = ''
    if request.method == 'POST':
        opcao = request.form['opcao']  # pega a informação das opções
        # pega a informação do que foi preenchido
        campo = request.form['campo']
        return render_template("resultado_funcionarios.html", funcionarios=funcionario, opcao=opcao, campo=campo)
    return render_template("resultado_funcionarios.html", funcionarios=funcionario, opcao=opcao, campo=campo)


@app.route('/editar_funcionarios/<int:id>', methods=['GET', 'POST'])
def edita_funcionario(id):
    funcionario = Funcionario.query.get(id)
    if request.method == 'POST':
        # salva com as novas informações inseridas
        funcionario.nome = request.form['nome']
        funcionario.email = request.form['email']
        funcionario.telefone = request.form['telefone']
        funcionario.celular = request.form['celular']
        funcionario.dataAniversario = request.form['dataAniversario']
        funcionario.dataContrato = request.form['dataContrato']
        funcionario.funcao = request.form['funcao']
        funcionario.senha = None
        db.session.commit()
        # validação
        mensagem = f"{funcionario.nome} foi editado(a) com sucesso! Clique novamente em pesquisar para ver os registros!"
        return render_template("resultado_funcionarios.html", mensagem_editar=mensagem)
    return render_template('editar_funcionarios.html', funcionario=funcionario)


@app.route('/deletar_funcionarios/<int:id>')
def deleta_funcionario(id):
    funcionario = Funcionario.query.get(id)
    db.session.delete(funcionario)
    db.session.commit()
    # validação
    mensagem = f"{funcionario.nome} foi DELETADO(A)! Clique novamente em pesquisar para ver os registros!"
    return render_template("resultado_funcionarios.html", mensagem_deletar=mensagem)


@app.route('/info_funcionarios/<int:id>')
def info_funcionario(id):
    funcionario = Funcionario.query.get(id)
    return render_template('info_funcionarios.html', funcionario=funcionario)


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/cadastrar_produto', methods=['GET', 'POST'])
def adiciona_produto():
    if request.method == 'POST':
        produto = Produto(
            request.form['nome'], request.form['descricao'], request.form['valor'])
        if produto.nome == '' or produto.descricao == '' or produto.valor == '':
            mensagem = 'Não deixe campos obrigatórios em branco!'
            return render_template('cadastrar_produto.html', mensagem=mensagem)
        else:
            db.session.add(produto)
            db.session.commit()
            mensagem_sucesso = f'{produto.nome.upper()} foi cadastrado(a) com SUCESSO!'
            return render_template('cadastrar_produto.html', mensagem_ok=mensagem_sucesso)
    return render_template('cadastrar_produto.html')


@app.route('/resultado_produto', methods=['GET', 'POST'])
def resultado_produto():
    produto = Produto.query.all()
    opcao = ''
    campo = ''
    if request.method == 'POST':
        opcao = request.form['opcao']  # pega a informação das opções
        # pega a informação do que foi preenchido
        campo = request.form['campo']
        return render_template("resultado_produto.html", produtos=produto, opcao=opcao, campo=campo)
    return render_template("resultado_produto.html", produtos=produto, opcao=opcao, campo=campo)


@app.route('/editar_produto/<int:id>', methods=['GET', 'POST'])
def edita_produto(id):
    produto = Produto.query.get(id)
    if request.method == 'POST':
        # salva com as novas informações inseridas
        produto.nome = request.form['nome']
        produto.descricao = request.form['descricao']
        produto.valor = request.form['valor']
        db.session.commit()
        # validação
        mensagem = f"{produto.nome} foi editado(a) com sucesso! Clique novamente em pesquisar para ver os registros!"
        return render_template("resultado_produto.html", mensagem_editar=mensagem)
    return render_template('editar_produto.html', produto=produto)


@app.route('/deletar_produto/<int:id>')
def deleta_produto(id):
    produto = Produto.query.get(id)
    db.session.delete(produto)
    db.session.commit()
    # validação
    mensagem = f"{produto.nome} foi DELETADO(A)! Clique novamente em pesquisar para ver os registros!"
    return render_template("resultado_produto.html", mensagem_deletar=mensagem)


@app.route('/info_produto/<int:id>')
def info_produto(id):
    produto = Produto.query.get(id)
    return render_template('info_produto.html', produto=produto)


if __name__ == '__main__':
    db.create_all()
    app.secret_key = "superchavesecreta"
    app.run()
     