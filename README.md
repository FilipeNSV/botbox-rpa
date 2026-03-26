# 🤖 Bootbox RPA - Automação com Playwright

Projeto de automação desenvolvido em Python utilizando Playwright para simular o fluxo completo de gerenciamento de tarefas no sistema Bootbox.

---

## 🚀 Objetivo

Automatizar o ciclo completo de uma tarefa dentro do sistema:

1. Login na aplicação  
2. Criação de uma nova tarefa  
3. Execução das etapas do fluxo:
   - Estimativa
   - Desenvolvimento
   - Code Review
4. Adição de comentários em cada etapa  
5. Conclusão da tarefa  
6. Logout do sistema  

---

## 🛠️ Tecnologias utilizadas

- Python 3.x  
- Playwright (automação web)  
- JavaScript Injection (para manipulação de Summernote)  

---

## 📂 Estrutura do projeto

botbox-rpa/
│
├── bootbox_bot.py   # Classe principal com toda a lógica da automação
├── main.py          # Ponto de entrada da aplicação
├── config.py        # Configurações (URL, usuário e senha)
├── .env             # Variáveis sensíveis (não versionadas)
└── README.md

---

## ⚙️ Configuração

### 1. Clone o repositório

git clone https://github.com/FilipeNSV/botbox-rpa.git
cd botbox-rpa

---

### 2. Crie e ative o ambiente virtual

python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

---

### 3. Instale as dependências

pip install playwright
playwright install

---

### 4. Configure as credenciais

No arquivo `config.py`:

BASE_URL = "URL_DO_SISTEMA"
USERNAME = "SEU_EMAIL"
PASSWORD = "SUA_SENHA"

---

## ▶️ Como executar

python main.py

---

## 🔄 Fluxo automatizado

A automação realiza:

- Abertura do sistema
- Login com usuário configurado
- Navegação até a tela de tarefas
- Criação de uma nova tarefa com:
  - Título dinâmico (timestamp)
  - Projeto e fluxo definidos
  - Datas e horários
  - Prioridade
  - Estimativa
  - Detalhes
  - Comentário inicial
- Execução das etapas:
  - Estimativa → comentário + conclusão
  - Desenvolvimento → comentário + conclusão
  - Code Review → comentário + conclusão
- Logout do sistema

---

## 🧠 Decisões técnicas

- Uso de `wait_for` ao invés de `sleep` para maior robustez
- Interação com editor Summernote via `page.evaluate`
- Seletores baseados na estrutura do DOM, evitando dependência de textos dinâmicos
- Organização do código em métodos por responsabilidade

---

## ⚠️ Observações

- O projeto roda com navegador visível (`headless=False`) para facilitar visualização
- Não recomendado uso em produção sem ajustes adicionais

---

## 📌 Possíveis melhorias

- Implementação de logs estruturados
- Tratamento global de exceções
- Captura automática de screenshots em erro
- Execução em modo headless
- Parametrização via `.env`

---

## 👨‍💻 Autor

Filipe Vieira  
Desenvolvedor Full Stack
