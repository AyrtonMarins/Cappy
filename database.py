import sqlite3

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect('cappy_database.db')
    return conn

def create_tables():
    """Garante que as tabelas necessárias existam no banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabela de Atividades
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            status TEXT DEFAULT 'Pendente',
            scheduled_for DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de Detalhes da Atividade
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER,
            key TEXT NOT NULL,
            value TEXT,
            FOREIGN KEY (activity_id) REFERENCES activities (id)
        )
    ''')
    
    conn.commit()
    conn.close()