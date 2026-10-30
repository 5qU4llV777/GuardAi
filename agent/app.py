import sqlite3


def criar_banco():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            senha TEXT,
            admin INTEGER
        );
        CREATE TABLE produtos (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            preco REAL
        );
        CREATE TABLE pedidos (
            id INTEGER PRIMARY KEY,
            usuario_id INTEGER,
            produto_id INTEGER
        );
        INSERT INTO usuarios VALUES (1, 'admin', 'admin123', 1);
        INSERT INTO usuarios VALUES (2, 'maria', 'maria456', 0);
        INSERT INTO usuarios VALUES (3, 'joao',  'joao789',  0);
        INSERT INTO produtos VALUES (1, 'Teclado', 120.0);
        INSERT INTO produtos VALUES (2, 'Mouse',    60.0);
        INSERT INTO produtos VALUES (3, 'Monitor', 900.0);
        INSERT INTO pedidos VALUES (1, 2, 1);
        INSERT INTO pedidos VALUES (2, 3, 3);
        """
    )
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# FUNÇÕES SEGURAS (corrigidas)
# ---------------------------------------------------------------------------

def login_seguro(conn, nome, senha):
    """Consulta parametrizada — previne SQL Injection."""
    query = "SELECT id, nome, admin FROM usuarios WHERE nome = ? AND senha = ?"
    return conn.execute(query, (nome, senha)).fetchone()


def buscar_usuario_por_id_seguro(conn, user_id):
    """Conversão de tipo + parâmetro parametrizado."""
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        return []  # ou raise ValueError("ID inválido")
    return conn.execute(
        "SELECT id, nome, admin FROM usuarios WHERE id = ?", (user_id_int,)
    ).fetchall()


def buscar_produtos_seguro(conn, termo):
    """Parâmetro com curinga montado fora da SQL."""
    return conn.execute(
        "SELECT id, nome, preco FROM produtos WHERE nome LIKE ?", (f"%{termo}%",)
    ).fetchall()


COLUNAS_PERMITIDAS = {"id", "nome", "preco"}


def listar_produtos_ordenado_seguro(conn, coluna):
    """ORDER BY validado por allowlist — única forma segura para nomes de coluna."""
    if coluna not in COLUNAS_PERMITIDAS:
        raise ValueError(f"Coluna inválida: {coluna}. Permitidas: {COLUNAS_PERMITIDAS}")
    # f-string seguro pois valor já validado contra allowlist
    return conn.execute(f"SELECT id, nome, preco FROM produtos ORDER BY {coluna}").fetchall()


def deletar_pedido_seguro(conn, pedido_id):
    """Parâmetro parametrizado + execute (não executescript) — um comando apenas."""
    try:
        pedido_id_int = int(pedido_id)
    except (ValueError, TypeError):
        raise ValueError("ID do pedido deve ser um número inteiro")

    query = "DELETE FROM pedidos WHERE id = ?"
    cursor = conn.execute(query, (pedido_id_int,))
    conn.commit()
    return cursor.rowcount  # retorna linhas afetadas


# ---------------------------------------------------------------------------
# DEMONSTRAÇÃO
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    conn = criar_banco()

    print("Login (seguro):           ", login_seguro(conn, "maria", "maria456"))
    print("Login com injeção (falha):", login_seguro(conn, "admin' --", "qualquer"))
    print("Usuário id=2:             ", buscar_usuario_por_id_seguro(conn, "2"))
    print("Usuário id injetado:      ", buscar_usuario_por_id_seguro(conn, "1 OR 1=1"))
    print("Busca 'Mou':              ", buscar_produtos_seguro(conn, "Mou"))
    print("Ordenado por preço:       ", listar_produtos_ordenado_seguro(conn, "preco"))
    print("Ordenado por coluna inválida:", end=" ")
    try:
        listar_produtos_ordenado_seguro(conn, "id; DROP TABLE produtos--")
    except ValueError as e:
        print(f"Bloqueado: {e}")
    print("Deletar pedido 1:         ", deletar_pedido_seguro(conn, "1"))
    print("Tentativa injeção no delete:", end=" ")
    try:
        deletar_pedido_seguro(conn, "1; DROP TABLE usuarios--")
    except ValueError as e:
        print(f"Bloqueado: {e}")