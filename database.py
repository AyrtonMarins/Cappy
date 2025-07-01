import sqlite3
import os

DB_FILE = "cappy.db"

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect(DB_FILE)
    # Isso permite que a gente acesse os resultados por nome de coluna
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Cria as tabelas no banco de dados se elas ainda não existirem."""
    if os.path.exists(DB_FILE):
        print("Banco de dados já existe. Tabelas não foram recriadas.")
        return

    print("Criando banco de dados e tabelas...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabela principal para as atividades
    cursor.execute('''
        CREATE TABLE activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pendente',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            scheduled_for TIMESTAMP
        )
    ''')

    # Tabela para os detalhes de cada atividade (a parte "Notion")
    cursor.execute('''
        CREATE TABLE activity_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            FOREIGN KEY (activity_id) REFERENCES activities (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("Tabelas 'activities' e 'activity_details' criadas com sucesso.")

if __name__ == '__main__':
    # Este bloco só será executado quando você rodar o arquivo diretamente
    # Ex: python database.py
    create_tables()