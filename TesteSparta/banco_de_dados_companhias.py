#CÓDIGO UTILIZADO PARA TESTE, NÃO UTILIZAR!!!!!!


import sqlite3
import pandas as pd


# Função para carregar arquivo CSV (descomente para uso)
def carregar_arquivo_csv(caminho_arquivo):
    df = pd.read_csv(caminho_arquivo, delimiter=';')
    return df

# Passo 2: Formatar o DataFrame
def formatar_dataframe(df):
    df.columns = df.columns.str.strip()
    return df


# Passo 3: Criar ou conectar ao banco de dados SQLite
def conectar_banco_dados(nome_banco):
    conexao = sqlite3.connect(nome_banco)
    return conexao


# Função para gerar um código numérico único para cada CNPJ
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
    return True


# Função para obter o último status do histórico
def ultimo_status(conexao, cnpj):
    query = f"SELECT SIT FROM historico_sit WHERE CNPJ_CIA = ? ORDER BY DATA_INSERCAO DESC LIMIT 1"
    resultado = conexao.execute(query, (cnpj,)).fetchone()
    if resultado:
        return resultado[0]
    return None


# Função para atualizar ou inserir dados no banco de dados
def atualizar_ou_inserir_dados(df, conexao, nome_tabela):
    for index, row in df.iterrows():
        cnpj = row['CNPJ_CIA']
        denominacao = row['DENOM_SOCIAL']
        situacao = row['SIT']
        data_insercao = row['DATA_INSERCAO']
        usuario_insercao = row['USUARIO_INSERCAO']
        cnpj_id = row['CNPJ_ID']

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
                    conexao.execute(query_insert,
                                    (cnpj, denominacao, situacao, data_insercao, usuario_insercao, cnpj_id))

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


# Função para criar ou alterar a tabela no banco de dados se não existir
def criar_ou_alterar_tabela(conexao, nome_tabela):
    resultado = conexao.execute(f"PRAGMA table_info({nome_tabela})").fetchall()
    colunas_existentes = [coluna[1] for coluna in resultado]

    if not colunas_existentes:
        conexao.execute(f"""
            CREATE TABLE {nome_tabela} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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


# Função principal
def main():
    # Passo 1: Carregar arquivo CSV
    caminho_arquivo = 'data.csv'
    df = pd.read_csv(caminho_arquivo, delimiter=';')
    df = formatar_dataframe(df)

    # Adicionar coluna de DATA_INSERCAO e USUARIO_INSERCAO
    df['DATA_INSERCAO'] = pd.Timestamp.now().strftime('%Y-%m-%d')
    df['USUARIO_INSERCAO'] = 'usuario@example.com'  # Exemplo de usuário

    # Passo 3: Criar ou conectar ao banco de dados SQLite
    nome_banco = 'companhias.db'
    conexao = conectar_banco_dados(nome_banco)

    # Passo 4: Criar ou alterar a tabela se não existir
    nome_tabela = 'banco_companhias'
    criar_ou_alterar_tabela(conexao, nome_tabela)
    criar_tabela_historico(conexao)

    # Passo 5: Gerar código único para cada CNPJ
    df = gerar_codigo_unico(conexao, df, nome_tabela)

    # Passo 6: Atualizar ou inserir dados no banco de dados
    atualizar_ou_inserir_dados(df, conexao, nome_tabela)

    # Passo 7: Encerrar conexão
    encerrar_conexao(conexao)


# Função para encerrar conexão
def encerrar_conexao(conexao):
    conexao.close()


if __name__ == "__main__":
    main()