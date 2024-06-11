# Case Técnico Sparta - Desenvolvedor Python

## Descrição

Este projeto é uma aplicação de gerenciamento de dados de companhias, desenvolvida usando Python, PySide6 para a
interface gráfica, e SQLite como banco de dados. Ele permite aos usuários importar dados de companhias a partir de um
arquivo CSV, visualizar os dados em uma tabela, consultar dados por data e exportar os dados para um arquivo Excel.
O sistema também mantém um histórico de alterações, garantindo que todas as mudanças sejam registradas.

## Funcionalidades

1. **Login de Usuário**: Autenticação de usuários com diferentes níveis de acesso (admin e usuário), onde o admin tem
acesso total as funcionalidades, e o usuário tem acesso apenas as ferramentas de consulta.
2. **Importação de Dados CSV**: Importa dados de companhias a partir de um arquivo CSV.
3. **Visualização de Dados**: Exibe os dados das companhias em uma tabela.
4. **Consulta por Data**: Permite consultar dados específicos de uma data.
5. **Exportação para Excel**: Exporta os dados das companhias para um arquivo Excel.
6. **Histórico de Alterações**: Mantém um registro histórico das alterações feitas nos dados das companhias.

## Requisitos

- Sistema Operacional: Windows

## Instruções para Executar

1. **Baixe o executável**: Faça o download do arquivo executável `executavel.exe`.

2. **Execute o arquivo**: Clique duas vezes no arquivo executável para iniciar a aplicação.

### Login

1. **Acesse a janela de login**: Ao abrir a aplicação, você verá a janela de login.

2. **Digite suas credenciais**: Insira seu email e senha. Os logins padrão são:
   - Admin: email: `admin@sparta.com`, senha: `12345678` (acesso total)
   - Usuário: email: `user@sparta.com`, senha: `12345678` (acesso consulta)




![LOGIN](https://github.com/Gui-Setera/CaseTecnicoSparta/assets/148168144/717aa197-2be7-413e-8d8e-82ce268e81da)

3. **Clique em Login**: Após inserir as credenciais, clique no botão "Login" para acessar a aplicação.
![Tela Inicial](https://github.com/Gui-Setera/CaseTecnicoSparta/assets/148168144/f4a17b8e-a1b1-4354-ad5c-8dc5543aa0c2)
   

### Importar Dados CSV

1. **Clique em "Importar dados CSV"**: Disponível apenas para usuários administradores.

2. **Selecione o arquivo CSV**: Escolha o arquivo CSV com os dados das companhias. O arquivo deve ter as
colunas `CNPJ_CIA`, `DENOM_SOCIAL` e `SIT`. Existe um modelo padrão junto a pasta do executável, o mesmo não
deve ter sua extensão alterada. Basta atualizar os dados na própria planilha, salvar e integrar.

3. **Verifique a importação**: Uma mensagem será exibida confirmando a importação ou indicando um erro.

### Visualizar Dados

1. **Clique em "Visualizar todos os dados"**: Exibe todos os dados das companhias na tabela.
   ![Tela de Visualização ](https://github.com/Gui-Setera/CaseTecnicoSparta/assets/148168144/63a4ca0d-0454-42cf-a517-bfaebd53d73f)


3. **Clique em "Consultar por data"**: Digite a data no formato `AAAA-MM-DD` e clique em "Confirmar" para visualizar os
dados daquela data específica.




![Tela de pesquisa por data](https://github.com/Gui-Setera/CaseTecnicoSparta/assets/148168144/366e9c6a-9eae-47c8-879e-78e7d533f6b2)


## Estrutura do Projeto

- `main.py`: Arquivo principal que contém a aplicação (usado para gerar o executável).
- `README.md`: Instruções para rodar a solução e explicações das decisões tomadas.
- `logo.PNG`: Icone usado na aplicação.
- `banco_de_dados_companhias.py`: Código beta utilizado para a versão final. Disponível para análise.
- `modelo de importacao.csv`: Base de importação para subir dados para o sistema.
- `companhias.db`: Banco de dados que contém e persiste os dados integrados.

## Decisões de Design e Implementação

### Estrutura da Interface Gráfica

Optei por usar o PySide6 para a criação da interface gráfica devido à sua robustez e flexibilidade. PySide6 oferece
uma maneira eficiente de criar interfaces gráficas com suporte a diferentes plataformas, garantindo uma experiência de
usuário consistente.

### Organização do Código

O código foi organizado em classes para manter a modularidade e a clareza. As principais classes incluem:

- `LoginDialog`: Gerencia a janela de login.
- `ConsultarData`: Gerencia a janela de consulta por data.
- `VisualizarData`: Exibe os dados das companhias em uma tabela.
- `DadosApp`: Classe principal que gerencia a aplicação e suas funcionalidades.

### Banco de Dados

Utilizei SQLite como banco de dados devido à sua simplicidade e fácil integração com Python. Como a ideia inicial não é
trabalhar com volume maciço de dados, foi a melhor ferramenta a se escolher.

### Histórico de Alterações

Implementei um sistema de histórico de alterações para garantir que todas as mudanças nos dados das companhias sejam
registradas. Isso permite que o usuário acompanhe as alterações feitas ao longo do tempo, garantindo transparência e
rastreabilidade. Dados anteriores estão descritos como "ALTERADO" e os atuais "ALTERAÇÃO ATUAL".

### Tratamento de Erros

Adicionei tratamento de erros para garantir que o sistema lida efetivamente com entradas inválidas e outros erros.
Por exemplo, ao importar um arquivo CSV, o sistema verifica se o formato do arquivo está correto e exibe uma mensagem
de erro caso contrário.

### Tratamento de Duplicidades

Caso o mesmo arquivo seja importado duas vezes, ou o dados ja importados sejam importados novamente, o sistema ignora e
não os armazena.

### Inclusão de ID de integração e ID de CNPJ para melhorar métodos de consulta, bem como a data na qual o titulo foi
incluído no sistema.

### Caso não queira abrir via executável, existe a possibilidade de abrir o arquivo main.py com a IDE de sua preferência.

### Requisitos do teste

- Ser desenvolvido em Python: Desenvolvido na linguagem python.

- O banco de dados deve ser SQL: Utilizado SQLite.

- Deve ser possível consultar as informações das companhias tanto atualmente quanto
em datas passadas se a informação existir ou tiver sido alterada: O banco vem preenchido com dados atualizados no
dia 10/06/2024, retirado do site https://dados.gov.br/dados/conjuntos-dados/cias-abertas-informao-cadastral.
Para efetuar validação do requisito em especifico, sugiro utilizar o modelo de importação que já está alimentado.
Basta acrescentar uma ou mais linhas com situações atualizadas, integrar e validar o comportamento do software.

- Possuir README com instruções para rodar a solução localmente e explicação das
decisões tomadas durante o projeto: README estruturado.
