import sqlite3 as sql

class db:
    def __init__(self, db):
        """
        param db: Recebe o Banco de Dados.
        """
        self.db = db
        self.conection = None 

    def create_table(self):
        """Cria a tabela 'tarefas' se ela não existir."""
        cursor = self.conection.cursor()
    
        # Criar a tabela se ela não existir 
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id       INTEGER PRIMARY KEY,
            tarefa     TEXT,
            descTarefa    TEXT,
            concluida INTEGER
        );
        ''')

    def execute_query(self, query, parametros=None):
        """
        Execute uma consulta SQL.

        Args:
            query (str): A consulta SQL a ser executada.
            parametros (tuple, opcional): Uma tupla contendo os parâmetros da consulta.

        Returns:
            list: Retorna o resultado da consulta se for uma operação SELECT.
        """
        cursor = self.conection.cursor()

        try: 
            if parametros:
                cursor.execute(query, parametros) 
            else:
                cursor.execute(query)
            
            # Se a operação for uma seleção, retorne os resultados
            if query.startswith("SELECT"):
                return cursor.fetchall()
            
            self.conection.commit() 

        except sql.OperationalError as e:
            return f"Erro Operacional: {e}"
        except sql.IntegrityError as e:
            return f"Erro de integridade: {e}"
        except Exception as e:
            return f"Erro inesperado: {e}"
        finally:
            cursor.close()

    def connect_db(self):
        """Conecta ao banco de dados SQLite e define a conexão como self.conection."""
        try:
            self.conection = sql.connect(self.db)
            return self.conection
        except Exception as e:
            print(f"Erro ao conectar: {e}")

    def desconect_db(self):
        """Desconecta do banco de dados SQLite."""
        if self.conection: 
            self.conection.close()
        else:
            print(f"Sem conexões para encerrar.")

    def add_task(self, valores):
        """
        Adiciona um novo contato à tabela.

        Args:
            valores (tuple): Uma tupla contendo os valores para (nome, email, telefone).
        """
        query = "INSERT INTO tarefas (tarefa, descTarefa, concluida) VALUES (?, ?, ?)" 
        self.execute_query(query, valores)
    
    def remove_task(self, valor):
        """
        Remove um contato baseado em uma coluna e valor.

        Args:
            valor (str): Recebe uma tupla dos valores que vão ser removidos.
        """
        query = "DELETE FROM tarefas WHERE tarefa = ? AND descTarefa = ? AND concluida = ?"
        self.execute_query(query, valor)

    def update_task_status(self, task_details, new_status):
        # Desempacotando os valores necessários
        nome_tarefa, descricao, status_atual = task_details

        # Consulta SQL para atualizar o status baseado em descrição, data de início, data de término e status atual
        query = "UPDATE tarefas SET concluida = ? WHERE tarefa = ? AND descTarefa = ? AND concluida = ?"
        self.execute_query(query, (new_status, nome_tarefa, descricao, status_atual))

    def search_task(self, valor=None, filter=None):
        """
        Busca tarefas baseado em valor inserido e/ou estado da tarefa.

        Args:
            valor (str): Chave de Busca
            filter (str): Estado da tarefa ('Concluída' ou 'Pendente')

        Returns:
            list: Uma lista de tuplas contendo os resultados da busca ou todas as tarefas.    
        """
         # Definindo as colunas que desejamos recuperar (excluindo o ID)
        columns = "tarefa, descTarefa, concluida"

        if valor or filter:
            search_value = '%' + valor + '%' if valor else '%'
            query = f"SELECT {columns} FROM tarefas WHERE (tarefa LIKE ? OR descTarefa LIKE ?)"
            parameters = [search_value, search_value]

            if filter:
                # Adiciona a condição do filtro à consulta
                query += " AND concluida = ?"
                parameters.append(filter)
            
            return self.execute_query(query, tuple(parameters))
        
        else:
            # Caso não receba parâmetros, retorna todas as tarefas.
            query = f"SELECT {columns} FROM tarefas;"
            return self.execute_query(query)