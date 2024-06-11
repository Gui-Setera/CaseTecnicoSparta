import sys
import sqlite3
import pandas as pd
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                               QLabel, QFileDialog, QLineEdit, QMessageBox, QTableWidget,
                               QTableWidgetItem, QDialog)
from PySide6.QtGui import QIcon

# Classe para a janela de login
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login')
        self.setWindowIcon(QIcon('logo.PNG'))
        self.setFixedSize(300, 150)
        self.user_role = None
        self.user_email = None

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Email:'))
        self.email_input = QLineEdit()
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel('Senha:'))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        login_button = QPushButton('Login')
        login_button.clicked.connect(self.check_login)
        layout.addWidget(login_button)
        self.setLayout(layout)

    # Método para verificar as credenciais de login
    def check_login(self):
        email, password = self.email_input.text(), self.password_input.text()
        if (email, password) == ('admin@sparta.com', '12345678'):
            self.user_role, self.user_email = 'admin', email
            self.accept()
        elif (email, password) == ('user@sparta.com', '12345678'):
            self.user_role, self.user_email = 'user', email
            self.accept()
        else:
            QMessageBox.warning(self, 'Erro de Login', 'Email ou senha incorretos.')

# Classe para a janela de consulta por data
class ConsultarData(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Consulta por Data')
        self.setWindowIcon(QIcon('logo.PNG'))
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Digite a data de consulta (AAAA-MM-DD):'))
        self.date_input = QLineEdit()
        self.date_input.setMaxLength(10)
        self.date_input.setInputMask('0000-00-00')
        layout.addWidget(self.date_input)
        confirm_button = QPushButton('Confirmar')
        confirm_button.clicked.connect(self.accept)
        layout.addWidget(confirm_button)
        self.setLayout(layout)

# Classe para a janela de visualização de dados
class VisualizarData(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setWindowTitle('Visualização de Dados')
        self.setWindowIcon(QIcon('logo.PNG'))
        self.showMaximized()  # Exibe a janela maximizada
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Dados:'))
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)
        self.setLayout(layout)
        self.configurar_tabela()

    # Método para configurar a tabela de visualização
    def configurar_tabela(self):
        if not self.data.empty:
            self.table_widget.setRowCount(len(self.data.index))
            self.table_widget.setColumnCount(len(self.data.columns))
            self.table_widget.setHorizontalHeaderLabels(self.data.columns)
            for i, row in enumerate(self.data.itertuples(index=False)):
                for j, value in enumerate(row):
                    if j == self.data.columns.get_loc('HISTORICO_DE_ALTERACOES'):
                        value = 'ALTERAÇÃO ATUAL' if value == 1 else 'ALTERADO'
                    self.table_widget.setItem(i, j, QTableWidgetItem(str(value)))
            self.table_widget.resizeColumnsToContents()  # Adapta as colunas ao conteúdo

# Classe principal do aplicativo
class DadosApp(QWidget):
    def __init__(self, user_role, user_email):
        super().__init__()
        self.user_role = user_role
        self.user_email = user_email
        self.setWindowTitle('Sistema de gerenciamento de dados')
        self.setWindowIcon(QIcon('logo.PNG'))
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()

        self.add_button(layout, 'Consultar por data', self.inserir_data)
        self.add_button(layout, 'Visualizar todos os dados', self.ver_dados)
        if self.user_role == 'admin':
            self.add_button(layout, 'Importar dados CSV', self.importa_dados)
        self.add_button(layout, 'Emitir todos os dados em Excel', self.exportar_dados)
        self.add_button(layout, 'Encerrar aplicação', QApplication.instance().quit)

        self.setLayout(layout)

    # Método para adicionar botões à interface
    def add_button(self, layout, text, function):
        button = QPushButton(text, self)
        button.clicked.connect(function)
        layout.addWidget(button)

    # Método para consultar e visualizar dados por data
    def consultar_e_visualizar_data(self, data_consulta=None):
        df_resultado = self.consultar_por_data(data_consulta)
        if not df_resultado.empty:
            print(df_resultado)
            self.data_viewer = VisualizarData(df_resultado)
            self.data_viewer.show()
        else:
            QMessageBox.warning(self, "Data Não Encontrada",
                                "A data especificada não foi encontrada no banco de dados.")

    # Método para inserir data de consulta
    def inserir_data(self):
        date_input_dialog = ConsultarData()
        if date_input_dialog.exec():
            self.consultar_e_visualizar_data(date_input_dialog.date_input.text())

    # Método para visualizar todos os dados
    def ver_dados(self):
        self.consultar_e_visualizar_data()

    # Método para exportar dados para Excel
    def exportar_dados(self):
        file, _ = QFileDialog.getSaveFileName(self, "Salvar Relatório em Excel", "",
                                              "Excel Files (*.xlsx);;All Files (*)")
        if file:
            if not file.endswith('.xlsx'):
                file += '.xlsx'
            self.emitir_planilha(file)
            QMessageBox.information(self, "Sucesso", "Planilha emitida com sucesso!")

    # Método para consultar dados por data no banco de dados
    def consultar_por_data(self, data_consulta=None):
        conexao = sqlite3.connect('companhias.db')
        query = "SELECT * FROM banco_companhias"
        params = ()
        if data_consulta:
            query += " WHERE DATE(DATA_INSERCAO) = ?"
            params = (data_consulta,)
        df = pd.read_sql_query(query, conexao, params=params)
        conexao.close()
        return df

    # Método para emitir planilha com dados
    def emitir_planilha(self, nome_arquivo):
        df = self.consultar_por_data()
        df['HISTORICO_DE_ALTERACOES'] = df['HISTORICO_DE_ALTERACOES'].apply(lambda x: 'ALTERAÇÃO ATUAL' if x == 1 else 'ALTERADO')
        df.to_excel(nome_arquivo, index=False)
        print(f"Planilha {nome_arquivo} emitida com sucesso!")

    # Método para importar dados de um arquivo CSV
    def importa_dados(self):
        file, _ = QFileDialog.getOpenFileName(self, "Importar Dados CSV", "", "CSV Files (*.csv);;All Files (*)")
        if file:
            self.carregar_dados_csv(file)

    # Método para carregar dados de um arquivo CSV e atualizar o banco de dados
    def carregar_dados_csv(self, nome_arquivo_csv):
        try:
            df = pd.read_csv(nome_arquivo_csv, delimiter=';')
            expected_columns = ['CNPJ_CIA', 'DENOM_SOCIAL', 'SIT']  # Colunas esperadas no CSV
            if not all(col in df.columns for col in expected_columns):
                raise ValueError("Formato de arquivo inválido")
            df.columns = df.columns.str.strip()
            df['DATA_INSERCAO'] = pd.Timestamp.now().strftime('%Y-%m-%d')
            df['USUARIO_INSERCAO'] = self.user_email
            conexao = sqlite3.connect('companhias.db')
            criar_ou_alterar_tabela(conexao, 'banco_companhias')
            criar_tabela_historico(conexao)
            df = gerar_codigo_unico(conexao, df, 'banco_companhias')
            atualizar_ou_inserir_dados(df, conexao, 'banco_companhias')
            conexao.close()
            QMessageBox.information(self, "Sucesso", "Dados importados com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", "ERRO! Verificar arquivo de importação e tentar novamente!")

# Função para criar ou alterar a tabela no banco de dados
def criar_ou_alterar_tabela(conexao, nome_tabela):
    resultado = conexao.execute(f"PRAGMA table_info({nome_tabela})").fetchall()
    colunas_existentes = [coluna[1] for coluna in resultado]

    if not colunas_existentes:
        conexao.execute(f"""
            CREATE TABLE {nome_tabela} (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                CNPJ_CIA TEXT,
                DENOM_SOCIAL TEXT,
                SIT TEXT,
                DATA_INSERCAO TEXT,
                USUARIO_INSERCAO TEXT,
                CNPJ_ID TEXT,
                HISTORICO_DE_ALTERACOES INTEGER DEFAULT 1
            )
        """)
    else:
        if 'USUARIO_INSERCAO' not in colunas_existentes:
            conexao.execute(f"ALTER TABLE {nome_tabela} ADD COLUMN USUARIO_INSERCAO TEXT")
        if 'CNPJ_ID' not in colunas_existentes:
            conexao.execute(f"ALTER TABLE {nome_tabela} ADD COLUMN CNPJ_ID TEXT")
        if 'HISTORICO_DE_ALTERACOES' not in colunas_existentes:
            conexao.execute(f"ALTER TABLE {nome_tabela} ADD COLUMN HISTORICO_DE_ALTERACOES INTEGER DEFAULT 1")
    conexao.commit()

# Função para criar a tabela de histórico
def criar_tabela_historico(conexao):
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS historico_sit (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CNPJ_CIA TEXT,
            DATA_INSERCAO TEXT,
            SIT TEXT,
            USUARIO_INSERCAO TEXT
        )
    """)
    conexao.commit()

# Função para gerar um código único para cada CNPJ
def gerar_codigo_unico(conexao, df, nome_tabela):
    cnpj_id_map = {}
    query = f"SELECT CNPJ_CIA, CNPJ_ID FROM {nome_tabela}"
    resultado = conexao.execute(query).fetchall()
    cnpj_id_map = {row[0]: row[1] for row in resultado}

    cnpj_unicos = df['CNPJ_CIA'].unique()
    for cnpj in cnpj_unicos:
        if cnpj not in cnpj_id_map:
            novo_id = str(len(cnpj_id_map) + 1).zfill(7)
            cnpj_id_map[cnpj] = novo_id

    df['CNPJ_ID'] = df['CNPJ_CIA'].map(cnpj_id_map)
    return df

# Função para verificar se há mudanças nos dados
def verificar_mudancas(conexao, nome_tabela, cnpj, nova_denominacao, nova_situacao):
    query = f"SELECT DENOM_SOCIAL, SIT FROM {nome_tabela} WHERE CNPJ_CIA = ? AND HISTORICO_DE_ALTERACOES = 1 ORDER BY DATA_INSERCAO DESC LIMIT 1"
    resultado = conexao.execute(query, (cnpj,)).fetchone()

    if resultado:
        denominacao_atual, situacao_atual = resultado
        return denominacao_atual != nova_denominacao or situacao_atual != nova_situacao
    return False

# Função para obter o último status do histórico
def ultimo_status(conexao, cnpj):
    query = f"SELECT SIT FROM historico_sit WHERE CNPJ_CIA = ? ORDER BY DATA_INSERCAO DESC LIMIT 1"
    resultado = conexao.execute(query, (cnpj,)).fetchone()
    if resultado:
        return resultado[0]
    return None

# Função para atualizar ou inserir dados no banco de dados
def atualizar_ou_inserir_dados(df, conexao, nome_tabela):
    for _, row in df.iterrows():
        cnpj, denominacao, situacao = row['CNPJ_CIA'], row['DENOM_SOCIAL'], row['SIT']
        data_insercao, usuario_insercao, cnpj_id = row['DATA_INSERCAO'], row['USUARIO_INSERCAO'], row['CNPJ_ID']

        ultimo_sit = ultimo_status(conexao, cnpj)

        # Verifica se a empresa já existe na tabela principal
        query_existente = f"SELECT * FROM {nome_tabela} WHERE CNPJ_CIA = ? AND HISTORICO_DE_ALTERACOES = 1"
        existente = conexao.execute(query_existente, (cnpj,)).fetchone()

        if existente:
            if verificar_mudancas(conexao, nome_tabela, cnpj, denominacao, situacao):
                if ultimo_sit != situacao:
                    # Marca o registro antigo como "ALTERADO"
                    query_update = f"""
                        UPDATE {nome_tabela}
                        SET HISTORICO_DE_ALTERACOES = 0
                        WHERE CNPJ_CIA = ? AND HISTORICO_DE_ALTERACOES = 1
                    """
                    conexao.execute(query_update, (cnpj,))

                    # Insere um novo registro na tabela principal
                    query_insert = f"""
                        INSERT INTO {nome_tabela} (CNPJ_CIA, DENOM_SOCIAL, SIT, DATA_INSERCAO, USUARIO_INSERCAO, CNPJ_ID, HISTORICO_DE_ALTERACOES)
                        VALUES (?, ?, ?, ?, ?, ?, 1)
                    """
                    conexao.execute(query_insert, (cnpj, denominacao, situacao, data_insercao, usuario_insercao, cnpj_id))

                    # Adiciona uma entrada no histórico
                    query_historico = f"""
                        INSERT INTO historico_sit (CNPJ_CIA, DATA_INSERCAO, SIT, USUARIO_INSERCAO)
                        VALUES (?, ?, ?, ?)
                    """
                    conexao.execute(query_historico, (cnpj, data_insercao, situacao, usuario_insercao))
        else:
            # Insere um novo registro na tabela principal
            query_insert = f"""
                INSERT INTO {nome_tabela} (CNPJ_CIA, DENOM_SOCIAL, SIT, DATA_INSERCAO, USUARIO_INSERCAO, CNPJ_ID, HISTORICO_DE_ALTERACOES)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """
            conexao.execute(query_insert, (cnpj, denominacao, situacao, data_insercao, usuario_insercao, cnpj_id))

            # Adiciona uma entrada no histórico
            query_historico = f"""
                INSERT INTO historico_sit (CNPJ_CIA, DATA_INSERCAO, SIT, USUARIO_INSERCAO)
                VALUES (?, ?, ?, ?)
            """
            conexao.execute(query_historico, (cnpj, data_insercao, situacao, usuario_insercao))

    conexao.commit()

# Função principal para iniciar o aplicativo
def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('logo.PNG'))
    login = LoginDialog()
    if login.exec() == QDialog.Accepted:
        ex = DadosApp(login.user_role, login.user_email)
        ex.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()