# Conhecimentos Básicos de Segurança da Informação

Base de conhecimento de apoio para análise de vulnerabilidades e revisão de segurança. Conteúdo de caráter defensivo e educacional.

---

## 1. Fundamentos

### Tríade CIA
| Pilar | Significado | Exemplo de violação |
|---|---|---|
| **Confidencialidade** | Só quem tem permissão acessa a informação | Vazamento de banco de dados |
| **Integridade** | A informação não é alterada indevidamente | Alteração de saldo sem autorização |
| **Disponibilidade** | O sistema está acessível quando necessário | Ataque de negação de serviço, ransomware |

### Conceitos-chave
- **Ameaça:** algo que pode causar dano (atacante, falha, desastre).
- **Vulnerabilidade:** fraqueza que pode ser explorada (bug, má configuração).
- **Risco:** probabilidade × impacto de uma ameaça explorar uma vulnerabilidade.
- **Exploit:** técnica ou código que aproveita uma vulnerabilidade.
- **Superfície de ataque:** conjunto de pontos pelos quais um atacante pode interagir com o sistema.
- **Vetor de ataque:** caminho usado para chegar ao alvo.
- **Zero-day:** vulnerabilidade sem correção disponível ou desconhecida do fornecedor.

### Princípios de design seguro
1. **Menor privilégio:** dar apenas o acesso necessário.
2. **Defesa em profundidade:** várias camadas de proteção, sem ponto único de falha.
3. **Falha segura (fail-safe):** em caso de erro, negar acesso.
4. **Separação de funções:** ações críticas exigem mais de uma pessoa ou componente.
5. **Segurança por padrão (secure by default):** a configuração inicial deve ser a mais segura.
6. **Mediação completa:** toda requisição é verificada, sempre.
7. **Simplicidade:** sistemas simples têm menos erros e são mais fáceis de auditar.
8. **Não confiar em entrada externa (zero trust):** validar tudo que vem de fora.
9. **Segurança não depende de obscuridade:** o sistema deve ser seguro mesmo que o projeto seja conhecido.

---

## 2. OWASP Top 10 (Aplicações Web)

| # | Categoria | Resumo | Defesa principal |
|---|---|---|---|
| A01 | **Quebra de controle de acesso** | Usuário acessa dados ou funções que não deveria (IDOR, rotas admin expostas) | Autorização no servidor em toda requisição, negar por padrão |
| A02 | **Falhas criptográficas** | Dados sensíveis sem proteção adequada | TLS, algoritmos modernos, gestão correta de chaves |
| A03 | **Injeção** | Entrada do usuário interpretada como comando (SQL, shell, template) | Consultas parametrizadas, validação, escape contextual |
| A04 | **Design inseguro** | Falhas na concepção, não só na implementação | Modelagem de ameaças, requisitos de segurança |
| A05 | **Configuração incorreta** | Debug ligado, credenciais padrão, headers ausentes | Hardening, revisão de configuração, automação |
| A06 | **Componentes vulneráveis e desatualizados** | Bibliotecas com CVEs conhecidos | Inventário (SBOM), atualização, scanners de dependência |
| A07 | **Falhas de identificação e autenticação** | Senhas fracas, sessões mal gerenciadas | MFA, hash forte, limite de tentativas |
| A08 | **Falhas de integridade de software e dados** | Atualizações e pipelines sem verificação, desserialização insegura | Assinatura, verificação de integridade, CI/CD protegido |
| A09 | **Falhas de registro e monitoramento** | Ataques não detectados | Logs de segurança, alertas, retenção |
| A10 | **SSRF** | Servidor induzido a fazer requisições a destinos internos | Allowlist de destinos, bloqueio de rede interna |

---

## 3. Vulnerabilidades comuns: o que são e como corrigir

### 3.1 Injeção SQL (CWE-89)
**Problema:** a entrada do usuário é concatenada na consulta.

```python
# Vulnerável
query = f"SELECT * FROM users WHERE email = '{email}'"

# Correto: consulta parametrizada
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```
**Defesas:** parametrização/ORM, menor privilégio no usuário do banco, validação de entrada.

### 3.2 Injeção de comandos (CWE-78)
```python
# Vulnerável
os.system(f"ping {host}")

# Correto: sem shell, argumentos em lista, validação
subprocess.run(["ping", "-c", "1", host], check=True)
```
**Defesas:** evitar shell, usar APIs nativas, validar com allowlist.

### 3.3 Cross-Site Scripting, XSS (CWE-79)
**Problema:** conteúdo do usuário é renderizado como HTML/JS.
- **Refletido:** vem na requisição e volta na resposta.
- **Armazenado:** fica salvo e atinge outros usuários.
- **DOM-based:** ocorre no JavaScript do cliente.

**Defesas:** escape de saída conforme o contexto (HTML, atributo, JS, URL), evitar `innerHTML`/`v-html`/`dangerouslySetInnerHTML`, Content-Security-Policy, sanitização com biblioteca confiável.

### 3.4 CSRF (CWE-352)
**Problema:** o navegador envia cookies automaticamente em requisições forjadas por outro site.
**Defesas:** tokens anti-CSRF, cookies `SameSite=Lax/Strict`, verificação de `Origin`/`Referer`.

### 3.5 IDOR / Controle de acesso quebrado (CWE-639, 862)
**Problema:** `GET /pedidos/123` retorna o pedido sem verificar se pertence ao usuário.
```python
# Correto
pedido = Pedido.query.get_or_404(id)
if pedido.user_id != current_user.id:
    abort(403)
```
**Defesas:** checar autorização no servidor em cada acesso a objeto, IDs não previsíveis como complemento (não como substituto).

### 3.6 SSRF (CWE-918)
**Problema:** o servidor busca uma URL fornecida pelo usuário, que pode apontar para serviços internos ou metadados de nuvem.
**Defesas:** allowlist de domínios, resolver DNS e bloquear IPs privados/loopback/link-local, desabilitar redirecionamentos, isolamento de rede.

### 3.7 Desserialização insegura (CWE-502)
**Problema:** desserializar dados não confiáveis pode executar código.
**Defesas:** usar formatos simples (JSON), evitar `pickle`, `yaml.load` (usar `safe_load`), `unserialize`, `ObjectInputStream` com dados externos; assinar e validar dados.

### 3.8 Path traversal e upload inseguro (CWE-22, 434)
**Defesas:** normalizar caminhos e checar que permanecem no diretório base, gerar nomes de arquivo próprios, validar tipo (conteúdo, não só extensão) e tamanho, armazenar fora do diretório web, nunca executar arquivos enviados.

### 3.9 Exposição de segredos (CWE-798, 532)
**Defesas:** variáveis de ambiente ou gerenciador de segredos, `.env` no `.gitignore`, scanners (gitleaks), **rotação imediata** se vazar, nunca registrar segredos em logs.

### 3.10 Condições de corrida (CWE-362)
**Problema:** duas operações simultâneas violam regras de negócio (ex.: usar o mesmo cupom duas vezes).
**Defesas:** transações, bloqueios, restrições únicas no banco, operações atômicas.

### 3.11 Falhas de lógica de negócio
Valores negativos, pular etapas de um fluxo, reaproveitar tokens, manipular preço no cliente. **Defesa:** validar regras sempre no servidor e testar fluxos fora do caminho esperado.

---

## 4. Autenticação e sessão

### Senhas
- Armazenar com hash **lento e com sal**: **Argon2id** (preferido), **bcrypt** ou **scrypt**. Nunca MD5, SHA-1 ou SHA-256 simples.
- Exigir comprimento mínimo (12+), permitir frases longas, checar contra senhas vazadas.
- Limitar tentativas (rate limiting, bloqueio progressivo).
- Mensagens de erro genéricas ("usuário ou senha inválidos").

### MFA
Ofereça segundo fator: app autenticador (TOTP), chave de segurança (FIDO2/WebAuthn). SMS é o mais fraco dos fatores.

### Sessões e cookies
- `HttpOnly`, `Secure`, `SameSite`.
- Regenerar o ID da sessão após login.
- Expiração e invalidação no logout.

### JWT
- Verificar assinatura e algoritmo esperado (rejeitar `none`).
- Validar `exp`, `iss`, `aud`.
- Tokens de curta duração; segredo/chave forte.
- Não guardar dados sensíveis no payload (é apenas codificado, não criptografado).

### OAuth 2.0 / OIDC
Usar fluxo Authorization Code com PKCE, validar `state` e `redirect_uri` exatos.

---

## 5. Criptografia básica

| Necessidade | Use | Evite |
|---|---|---|
| Hash de senha | Argon2id, bcrypt, scrypt | MD5, SHA-1, SHA-256 puro |
| Integridade/hash geral | SHA-256, SHA-3 | MD5, SHA-1 |
| Criptografia simétrica | AES-GCM, ChaCha20-Poly1305 | DES, 3DES, RC4, AES-ECB |
| Assimétrica | RSA ≥ 2048 (ideal 3072), ECDSA/Ed25519, X25519 | RSA 1024 |
| Aleatoriedade | CSPRNG (`secrets`, `crypto.randomBytes`, `/dev/urandom`) | `random()`, `Math.random()` |
| Transporte | TLS 1.2+ (preferir 1.3) | SSL, TLS 1.0/1.1 |

Regras de ouro:
- **Não invente sua própria criptografia;** use bibliotecas consolidadas.
- Nunca reutilize IV/nonce com a mesma chave.
- Gerencie chaves fora do código (KMS, cofre de segredos) e planeje rotação.
- Criptografar em trânsito e em repouso para dados sensíveis.

---

## 6. Segurança de rede e infraestrutura

- **Segmentação de rede** e firewall com política "negar por padrão".
- Expor apenas portas necessárias; serviços internos (bancos, caches) nunca na internet pública.
- **Hardening:** remover serviços e contas desnecessárias, desabilitar credenciais padrão, manter patches em dia.
- **SSH:** chaves em vez de senha, desabilitar login root, `fail2ban` ou equivalente.
- **Headers HTTP de segurança:**
  - `Strict-Transport-Security`
  - `Content-Security-Policy`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options` / `frame-ancestors`
  - `Referrer-Policy`
  - `Permissions-Policy`
- **CORS:** nunca `*` junto com credenciais; liste origens específicas.
- **DDoS e abuso:** rate limiting, WAF, CDN.

### Contêineres e nuvem
- Imagens mínimas e atualizadas; não rodar como root; sem `--privileged`.
- Não embutir segredos em imagens ou `Dockerfile`.
- Scanner de imagens (Trivy).
- IAM com menor privilégio, sem chaves de longa duração, MFA em contas administrativas.
- Buckets/armazenamento privados por padrão; revisar políticas públicas.
- Bloquear acesso indevido a metadados da instância (usar IMDSv2 na AWS).
- Registrar e monitorar (CloudTrail e equivalentes).

---

## 7. Desenvolvimento seguro (SDLC)

1. **Requisitos:** definir requisitos de segurança e privacidade.
2. **Design:** modelagem de ameaças (STRIDE).
3. **Código:** revisão por pares, guias de codificação segura, linters de segurança.
4. **Teste:** SAST, SCA, DAST, testes de segurança automatizados.
5. **Build/CI-CD:** proteger pipelines, assinar artefatos, segredos fora do repositório.
6. **Deploy:** configuração segura, infraestrutura como código revisada.
7. **Operação:** monitoramento, patching, resposta a incidentes.

### STRIDE (modelagem de ameaças)
| Letra | Ameaça | Propriedade violada |
|---|---|---|
| **S** | Spoofing (falsificação de identidade) | Autenticidade |
| **T** | Tampering (adulteração) | Integridade |
| **R** | Repudiation (negação de autoria) | Não repúdio |
| **I** | Information disclosure (vazamento) | Confidencialidade |
| **D** | Denial of service | Disponibilidade |
| **E** | Elevation of privilege | Autorização |

### Cadeia de suprimentos
- Fixar versões e usar lockfiles.
- Gerar e manter um **SBOM**.
- Desconfiar de pacotes novos/pouco usados (typosquatting).
- Habilitar alertas (Dependabot, Renovate, `npm audit`, `pip-audit`).
- Verificar integridade e assinatura de artefatos.

---

## 8. Validação de entrada e saída

- **Valide na entrada** (tipo, tamanho, formato, faixa) usando **allowlist**, não blocklist.
- **Escape na saída** conforme o contexto (HTML, SQL, shell, URL, JSON).
- Validar no **servidor**; validação no cliente é só conveniência.
- Tratar erros sem revelar detalhes internos (stack traces, caminhos, versões).
- Limitar tamanho de requisições e uploads.

---

## 9. Logs, monitoramento e resposta a incidentes

### O que registrar
Logins (sucesso/falha), mudanças de permissão, acessos negados, ações administrativas, alterações de dados críticos, erros de validação repetidos.

### O que NÃO registrar
Senhas, tokens, chaves, números completos de cartão, dados pessoais desnecessários.

### Resposta a incidentes (ciclo)
1. **Preparação:** plano, contatos, ferramentas.
2. **Detecção e análise:** confirmar e dimensionar o incidente.
3. **Contenção:** isolar sistemas, revogar credenciais.
4. **Erradicação:** remover a causa (corrigir vulnerabilidade, remover persistência).
5. **Recuperação:** restaurar serviços com segurança.
6. **Lições aprendidas:** documentar e melhorar.

Mantenha **backups** testados, offline/imutáveis, para recuperação de ransomware.

---

## 10. Classificação de vulnerabilidades

### CVSS (resumo)
| Pontuação | Severidade |
|---|---|
| 0.0 | Nenhuma |
| 0.1 – 3.9 | Baixa |
| 4.0 – 6.9 | Média |
| 7.0 – 8.9 | Alta |
| 9.0 – 10.0 | Crítica |

Métricas base: vetor de ataque, complexidade, privilégios necessários, interação do usuário, escopo, impacto em C/I/A.

### Identificadores
- **CVE:** identificador de vulnerabilidade pública (ex.: `CVE-2024-12345`).
- **CWE:** tipo de fraqueza (ex.: `CWE-89` SQL Injection).
- **CPE:** identificação de produto/versão.
- **EPSS:** probabilidade de exploração real; **KEV (CISA):** catálogo de vulnerabilidades exploradas ativamente. Use ambos para priorizar.

### Priorização prática
1. Segredos expostos e vulnerabilidades exploradas ativamente.
2. Falhas críticas/altas em sistemas expostos à internet.
3. Falhas que dão acesso a dados sensíveis.
4. Demais achados por severidade e facilidade de correção.

---

## 11. Privacidade e conformidade (Brasil)

### LGPD (Lei 13.709/2018) — pontos essenciais
- **Dados pessoais** e **dados sensíveis** (saúde, biometria, origem racial, religião etc.) exigem base legal.
- Princípios: finalidade, adequação, necessidade (minimização), segurança, transparência, prevenção.
- Direitos do titular: acesso, correção, anonimização, eliminação, portabilidade, informação sobre compartilhamento.
- Medidas de segurança técnicas e administrativas são obrigatórias.
- **Incidentes** que possam causar risco ou dano relevante devem ser comunicados à **ANPD** e aos titulares.
- Papéis: controlador, operador, encarregado (DPO).

### Outras referências
- **PCI-DSS:** dados de cartão de pagamento.
- **ISO/IEC 27001 / 27002:** gestão de segurança da informação.
- **NIST CSF e NIST SP 800-53:** frameworks de controles.
- **CIS Controls / CIS Benchmarks:** boas práticas e hardening.

---

## 12. Engenharia social e fator humano

- **Phishing:** e-mails/mensagens que induzem a clicar ou fornecer credenciais. Sinais: urgência, remetente suspeito, links divergentes, anexos inesperados.
- **Vishing/Smishing:** golpes por voz e SMS.
- **BEC:** fraude por e-mail corporativo (falsa ordem de pagamento).
- **Defesas:** MFA resistente a phishing (FIDO2), treinamento e simulações, canais de confirmação alternativos para pedidos financeiros, filtros de e-mail (SPF, DKIM, DMARC).

---

## 13. Checklists rápidos

### Revisão de código web
- [ ] Todas as consultas ao banco são parametrizadas?
- [ ] Toda rota sensível verifica autenticação **e** autorização no servidor?
- [ ] Saídas escapadas conforme o contexto?
- [ ] Segredos fora do código e do repositório?
- [ ] Senhas com Argon2id/bcrypt?
- [ ] Cookies com `HttpOnly`, `Secure`, `SameSite`?
- [ ] Uploads validados e armazenados com segurança?
- [ ] URLs fornecidas pelo usuário controladas (SSRF)?
- [ ] Erros não expõem detalhes internos?
- [ ] Rate limiting em login e endpoints sensíveis?
- [ ] Dependências sem CVEs críticos conhecidos?
- [ ] Logs de segurança sem dados sensíveis?

### Configuração de servidor/nuvem
- [ ] Portas e serviços mínimos expostos?
- [ ] Debug desativado em produção?
- [ ] TLS atualizado e headers de segurança ativos?
- [ ] IAM com menor privilégio e MFA?
- [ ] Armazenamento privado por padrão?
- [ ] Backups testados e protegidos?
- [ ] Patches aplicados e inventário atualizado?

### Antes de publicar um repositório
- [ ] Sem chaves, tokens ou `.env` no histórico do Git?
- [ ] `.gitignore` cobrindo arquivos sensíveis?
- [ ] Dependências auditadas?
- [ ] Política de segurança (`SECURITY.md`) com canal de contato?

---

## 14. Glossário

| Termo | Significado |
|---|---|
| **SAST** | Análise estática do código-fonte |
| **DAST** | Teste dinâmico da aplicação em execução |
| **SCA** | Análise de composição de software (dependências) |
| **IAST** | Análise interativa durante a execução |
| **SBOM** | Lista de componentes de um software |
| **WAF** | Firewall de aplicação web |
| **IDS/IPS** | Detecção/prevenção de intrusão |
| **SIEM** | Centralização e correlação de logs |
| **EDR** | Detecção e resposta em endpoints |
| **MFA / 2FA** | Autenticação com mais de um fator |
| **PKI** | Infraestrutura de chaves públicas |
| **Hardening** | Endurecimento da configuração |
| **Pentest** | Teste de intrusão autorizado |
| **Red/Blue Team** | Equipe ofensiva / defensiva |
| **Bug bounty** | Programa de recompensa por vulnerabilidades |
| **Zero Trust** | Modelo que não confia implicitamente em ninguém |
| **RCE** | Execução remota de código |
| **LFI/RFI** | Inclusão de arquivo local/remoto |
| **XXE** | Injeção de entidade externa em XML |
| **Clickjacking** | Enganar o usuário a clicar em elemento oculto |

---

## 15. Fontes de consulta

- OWASP Top 10, ASVS, Cheat Sheet Series — https://owasp.org
- CWE — https://cwe.mitre.org
- NVD — https://nvd.nist.gov
- OSV — https://osv.dev
- GitHub Advisory Database — https://github.com/advisories
- CISA KEV — https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- CIS Benchmarks — https://www.cisecurity.org
- MITRE ATT&CK — https://attack.mitre.org
- ANPD / LGPD — https://www.gov.br/anpd
- CERT.br — https://www.cert.br

---

> **Aviso:** conteúdo educacional e defensivo. Aplique somente em sistemas próprios ou com autorização explícita, e valide as recomendações no contexto de cada projeto.