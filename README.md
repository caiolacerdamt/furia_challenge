# Fúria Challenge - Streamlit + Firebase

Uma aplicação web robusta construída com Streamlit e integrando autenticação e banco de dados via Firebase (Pyrebase e Admin SDK), funcionando como uma rede social simples para os fãs da FURIA acompanharem o time.

---

## 📋 Sumário

1. [Visão Geral](#-visão-geral)
2. [Funcionalidades](#-funcionalidades)
3. [Tecnologias](#-tecnologias)
4. [Pré-requisitos](#-pré-requisitos)
5. [Instalação](#-instalação)
6. [Configuração de Segredos](#-configuração-de-segredos)
7. [Uso](#-uso)
8. [Deploy](#-deploy)
9. [Estrutura de Pastas](#-estrutura-de-pastas)
10. [Contribuição](#-contribuição)
11. [Licença](#-licença)

---

## 🔍 Visão Geral

Este projeto é uma **mini rede social** para fãs da Fúria, construída com Streamlit e Firebase. A aplicação oferece várias páginas dedicadas a:

* **Onboarding**: captura informações iniciais dos usuários após o primeiro login.
* **Feed Principal**: área estilo rede social X, onde fãs podem criar posts, curtir e interagir.
* **Seção Fans**: exibe posts de destaque da Fúria no Instagram e X, atualizados via scraping.
* **Chatbot Interativo**: fornece dados sobre elenco, calendário de jogos, streamers online, redes sociais e loja oficial.
* **Perfil do Usuário**: visualização, edição e exclusão de dados pessoais.

Tudo isso com autenticação, armazenamento e atualização de dados em tempo real via Firebase.

---

## ✨ Funcionalidades

* **Autenticação de Usuário** (email/senha).
* **Confirmação de Email** pós-cadastro.
* **Persistência** de dados no Realtime Database.
* **Operações Avançadas** no Firestore (ex.: ler e gravar coleções).
* **Configuração Segura** via `st.secrets` para credenciais.
* **Tela de Onboarding**: coleta dados do usuário após o primeiro login.
* **Feed Principal**: usuários podem criar posts e curtir como em uma rede social X.
* **Seção Fans**: exibe posts de destaque da Fúria no Instagram e X, atualizados via scraping.
* **Chatbot Interativo**:

  * Responde perguntas sobre o elenco dos times da Fúria.
  * Mostra calendário de jogos, coletado por web scraping com Playwright e armazenado no Firebase.
  * Lista streamers da Fúria online, usando API da Twitch e consumo de Apify para scraping.
  * Exibe redes sociais e loja oficial da Fúria.
  * **Scraping Agendado**: tarefas agendadas para atualizar dados periodicamente.
* **Página de Perfil**: visualização, edição e exclusão de dados do usuário.

---

## 🛠 Tecnologias

* Linguagem: Python 3.x
* Framework Web: Streamlit
* Firebase: Pyrebase (Auth + RTDB) e Firebase Admin SDK (Firestore, Storage)
* Deploy: Streamlit Community Cloud

---

## ⚙️ Pré-requisitos

* Conta no [Firebase](https://firebase.google.com).
* Conta no [GitHub](https://github.com) e [Streamlit Cloud](https://share.streamlit.io).
* Conta no [IMGUR](https://imgur.com/)

---

## 🏗️ Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/furia-challenge.git
   cd furia-challenge
   ```
2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv venv
   # Linux/Mac
   source venv/bin/activate
   # Windows
   venv\Scripts\activate
   ```
3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

---

## 🔐 Configuração de Segredos

1. Crie a pasta e o arquivo localmente (NÃO COMMITAR):

   ```bash
   mkdir .streamlit
   touch .streamlit/secrets.toml
   ```
2. Preencha `.streamlit/secrets.toml` com suas chaves do Firebase:

   ```toml
   [firebase]
   apiKey = "<API_KEY>"
   authDomain = "<PROJECT>.firebaseapp.com"
   databaseURL = "https://<PROJECT>-default-rtdb.firebaseio.com/"
   projectId = "<PROJECT>"
   storageBucket = "<PROJECT>.appspot.com"
   messagingSenderId = "<SENDER_ID>"
   appId = "<APP_ID>"
   measurementId = "<MEASUREMENT_ID>"

   [firebase_admin]
   type = "service_account"
   project_id = "<PROJECT>"
   private_key_id = "<KEY_ID>"
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "<SERVICE_ACCOUNT_EMAIL>"
   client_id = "<CLIENT_ID>"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
   universe_domain = "googleapis.com"

   [imgur]
   imgur_client_id = "seu_client_id"
   imgur_client_secret = "seu_client_secret"
   imgur_access_token = "seu_access_token"
   imgur_refresh_token = "seu_refresh_token"

   [twitch]
   twitch_client_id = "seu_client_id"
   twitch_client_secret = "seu_client_secret"
   twitch_access_token = "seu_access_token"
   
   ```
3. Adicione `.streamlit/secrets.toml` ao `.gitignore`.

---

## ▶️ Uso

Para rodar localmente:

```bash
streamlit run app.py
```

Acesse `http://localhost:8501` no navegador.

---

## 🚀 Deploy no Streamlit Cloud

1. Faça commit e push do código **sem** o `secrets.toml`.
2. Acesse [Streamlit Cloud](https://share.streamlit.io) e crie um novo app.
3. Selecione seu repositório, branch `main` e `app.py` como arquivo principal.
4. Na seção **Settings → Secrets**, cole o conteúdo do seu `.streamlit/secrets.toml`.
5. Salve e aguarde o deploy automático.
6. Abra o link do app para testar em produção.

---

## 📁 Estrutura de Pastas

```
├── .streamlit/
│   └── secrets.toml             # segredos locais (não versionado)
├── app/
│   ├── firebase/
│   │   ├── firebase_admin.py    # inicialização do Admin SDK
│   │   └── auth.py              # autenticação com Pyrebase
│   ├── pages/                   # páginas de cadastro, perfil, etc.
│   │   └── ...                  # arquivos de rotas e views de páginas
│   ├── utils/
│   │   ├── constants.py         # constantes do projeto
│   │   ├── utils.py             # funções utilitárias
│   │   └── session.py           # gerenciamento de sessão do usuário
│   └── views/
│       ├── access.py            # tela de login/acesso
│       ├── main_app.py          # layout principal do app
│       └── onboarding.py        # tela de onboarding pós-login
├── chatbot/
│   ├── handlers.py              # funções do chatbot
│   └── scraping_twitch.py       # coleta de streamers da Twitch
├── static/                      # imagens e recursos estáticos
├── .gitignore                   # arquivos/pastas ignorados pelo Git
├── app.py                       # ponto de entrada da aplicação
└── requirements.txt             # dependências do projeto

---
```

---

## 🤝 Contribuição

Contribuições são bem-vindas! Siga estes passos:

1. Faça um fork do projeto.
2. Crie uma branch para sua feature: `git checkout -b feature/nova-coisa`.
3. Commit suas mudanças: `git commit -m '✨ adiciona nova feature'`.
4. Push para a branch: `git push origin feature/nova-coisa`.
5. Abra um Pull Request.

---

## 📄 Licença

Este projeto está licenciado sob a [MIT License](https://github.com/caiolacerdamt/furia_challenge/blob/main/LICENSE.md).

---

> Desenvolvido por **Caio Lacerda** – [GitHub](https://github.com/caiolacerdamt) | [LinkedIn](https://linkedin.com/in/caiolacerdamt)
