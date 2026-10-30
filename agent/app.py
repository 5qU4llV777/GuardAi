import sqlite3                                                                                                                          
  import bcrypt                                                                                                                           
                                                                                                                                          
                                                                                                                                          
  def criar_tabela_usuarios():                                                                                                            
      """Cria a tabela com coluna para hash da senha."""                                                                                  
      conexao = sqlite3.connect('banco_de_dados.db')                                                                                      
      cursor = conexao.cursor()                                                                                                           
      cursor.execute("""                                                                                                                  
          CREATE TABLE IF NOT EXISTS usuarios (                                                                                           
              id INTEGER PRIMARY KEY AUTOINCREMENT,                                                                                       
              username TEXT UNIQUE NOT NULL,                                                                                              
              password_hash BLOB NOT NULL                                                                                                 
          )                                                                                                                               
      """)                                                                                                                                
      conexao.commit()                                                                                                                    
      conexao.close()                                                                                                                     
                                                                                                                                          
                                                                                                                                          
  def cadastrar_usuario(usuario, senha):                                                                                                  
      """Registra novo usuário com senha hasheada."""                                                                                     
      if not usuario or not senha:                                                                                                        
          return "Usuário e senha são obrigatórios."                                                                                      
                                                                                                                                          
      # Gera salt + hash (bcrypt inclui o salt no hash final)                                                                             
      hash_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())                                                                 
                                                                                                                                          
      conexao = sqlite3.connect('banco_de_dados.db')                                                                                      
      cursor = conexao.cursor()                                                                                                           
                                                                                                                                          
      try:                                                                                                                                
          cursor.execute(                                                                                                                 
              "INSERT INTO usuarios (username, password_hash) VALUES (?, ?)",                                                             
              (usuario, hash_senha)                                                                                                       
          )                                                                                                                               
          conexao.commit()                                                                                                                
          return "Usuário cadastrado com sucesso!"                                                                                        
      except sqlite3.IntegrityError:                                                                                                      
          return "Usuário já existe."                                                                                                     
      finally:                                                                                                                            
          conexao.close()                                                                                                                 
                                                                                                                                          
                                                                                                                                          
  def fazer_login(usuario, senha):                                                                                                        
      """Autentica usuário verificando hash da senha."""                                                                                  
      if not usuario or not senha:                                                                                                        
          return "Acesso Negado."                                                                                                         
                                                                                                                                          
      conexao = sqlite3.connect('banco_de_dados.db')                                                                                      
      cursor = conexao.cursor()                                                                                                           
                                                                                                                                          
      # Busca APENAS o hash - query parametrizada (previne SQLi)                                                                          
      cursor.execute(                                                                                                                     
          "SELECT password_hash FROM usuarios WHERE username = ?",                                                                        
          (usuario,)                                                                                                                      
      )                                                                                                                                   
      row = cursor.fetchone()                                                                                                             
      conexao.close()                                                                                                                     
                                                                                                                                          
      if not row:                                                                                                                         
          return "Acesso Negado."  # Usuário não existe (mesma msg p/ não vazar info)                                                     
                                                                                                                                          
      hash_armazenado = row[0]                                                                                                            
                                                                                                                                          
      # Verifica senha contra hash (bcrypt gerencia salt + comparação timing-safe)                                                        
      if bcrypt.checkpw(senha.encode('utf-8'), hash_armazenado):
          return "Acesso Permitido!"                                                                                                      
      else:                                                                                                                               
          return "Acesso Negado."                                                                                                         
                                           