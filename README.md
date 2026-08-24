# Service Management — Base

Módulo base para **Odoo 18** destinado à construção de um sistema de gestão de serviços e assistência técnica.

> 🚧 **Status:** Em desenvolvimento
> 📚 **Projeto de aprendizagem:** Odoo Development
> 👨‍💻 **Autor:** Alício Mussenga

---

## 📋 Sobre o projeto

O **Service Management** é um módulo desenvolvido para servir como núcleo de uma solução de gestão de serviços e assistência técnica.

A proposta é construir o sistema de forma incremental, utilizando boas práticas de desenvolvimento em Odoo e aplicando os conceitos aprendidos ao longo do projeto.

Nesta primeira etapa, o módulo fornece a estrutura inicial sobre a qual serão construídas as funcionalidades de gestão de serviços.

### Objetivos

* Estruturar um módulo personalizado para Odoo 18.
* Criar uma base organizada para futuras funcionalidades.
* Estender o cadastro de parceiros para atender às necessidades do negócio.
* Criar uma estrutura de categorização de serviços.
* Aplicar conceitos de modelos, views, segurança, relações e regras de negócio do Odoo.
* Desenvolver o projeto de forma incremental e documentada.

---

## 🧩 Funcionalidades planejadas

### Núcleo

* [x] Estrutura inicial do módulo
* [x] Manifesto do módulo
* [x] Configuração das dependências
* [ ] Modelos de negócio
* [ ] Dados iniciais
* [ ] Regras de segurança
* [ ] Views
* [ ] Menus e ações

### Gestão de serviços

* [ ] Cadastro de serviços
* [ ] Categorias de serviços
* [ ] Técnicos
* [ ] Clientes
* [ ] Solicitações de assistência
* [ ] Ordens de serviço
* [ ] Estados e fluxo de atendimento

### Futuras funcionalidades

* [ ] Gestão de técnicos
* [ ] Agenda de atendimentos
* [ ] Histórico de serviços
* [ ] Avaliação dos serviços
* [ ] Relatórios
* [ ] Dashboard
* [ ] Gestão de equipamentos
* [ ] Gestão de peças e materiais
* [ ] Integração com faturação

---

## 🏗️ Arquitetura do módulo

A estrutura inicial do módulo segue a organização recomendada para módulos personalizados do Odoo:

```text
sm_base/
├── __init__.py
├── __manifest__.py
│
├── models/
│   └── __init__.py
│
├── views/
│
├── security/
│
└── data/
```

À medida que o desenvolvimento avançar, novos componentes serão adicionados à estrutura.

---

## ⚙️ Tecnologias

| Tecnologia | Versão |
| ---------- | ------ |
| Odoo       | 18.0   |
| Python     | 3.x    |
| PostgreSQL | 17.x   |
| Git        | —      |
| GitHub     | —      |

---

## 📦 Instalação

Clone o repositório dentro do diretório de addons personalizados do Odoo:

```bash
git clone git@github.com:aliciomussenga/sm_base.git
```

Entre no diretório:

```bash
cd sm_base
```

Certifique-se de que o diretório que contém o módulo está incluído no `addons_path` da configuração do Odoo.

Depois, reinicie o servidor Odoo e atualize a lista de aplicações.

---

## 🔧 Desenvolvimento

Este projeto utiliza Git para controle de versão.

Para obter as últimas alterações:

```bash
git pull
```

Para criar uma nova funcionalidade:

```bash
git checkout -b feature/nome-da-funcionalidade
```

Depois de concluir as alterações:

```bash
git add .
git commit -m "feat: descrição da alteração"
git push -u origin feature/nome-da-funcionalidade
```

---

## 📚 Estrutura de aprendizagem

Este projeto também funciona como um laboratório prático para estudar desenvolvimento de módulos no Odoo.

O desenvolvimento será dividido em aulas:

```text
Aula 01 — Módulos em Odoo
Aula 02 — Modelos e ORM
Aula 03 — Campos
Aula 04 — Relacionamentos
Aula 05 — Views
Aula 06 — Menus e Actions
Aula 07 — Segurança e Access Rights
Aula 08 — Dados e XML
Aula 09 — Regras de negócio
Aula 10 — Herança de modelos
Aula 11 — Relatórios
Aula 12 — Testes
...
```

Cada etapa será aplicada diretamente ao projeto `sm_base`.

---

## 🎯 Objetivo final

Transformar o módulo base em uma solução completa de **gestão de serviços e assistência técnica**, aplicando progressivamente os principais conceitos do desenvolvimento de módulos personalizados no Odoo.

O objetivo não é apenas concluir o sistema, mas **compreender como e por que cada parte do Odoo funciona**.

---

## 👨‍💻 Autor

**Alício Mussenga**

Desenvolvedor em formação e estudante de desenvolvimento de sistemas ERP com foco em **Odoo, Python e desenvolvimento de aplicações empresariais**.

---

## 📄 Licença

Este projeto está licenciado sob a **LGPL-3**.

Consulte o arquivo `LICENSE` para mais informações.
