
# LoL Discord Match Viewer

Bot de discord para mostrar informações da partida atual, inclui também um script para visualização pelo proprio terminal com um dataframe




## Funcionalidades

- Chamadas a API optimizadas
- Automaticamente baixa os dados para identificação dos campeões via ID
- Utiliza outros sites de terceiro para obter mais informações
- Busca a partida automaticamente
- Sistema para escolher qual canal enviar as mensagens, emojis customizados de elo


## Tecnologias

- Python 3.10
- Pandas p/ DataFrame
- Configurações em YAML
- Banco de dados com nome e id dos campeões por CSV
- Sistema de cache para evitar pesquisas repetitivas pra API, também via YAML



## ##TODO

Adicionar mais configurações para o bot

Fornecer uma API para consumir os dados gerados pelo script em si

## Screenshots

### Configuração
![Config](https://i.ibb.co/RyBrQPY/config.png)

- ID do canal pode ser alterado pelo discord via comando ***!set_channel*** ou ***!setChannel***

### Mensagem via Embed
![Embed](https://i.ibb.co/K6W9FkP/example1.png)

- Emojis customizados para Winrates maiores e menores que 50% (Adicionarei à configuração mais opções)
- Emoji referente ao elo
- Tipo da partida, tempo e ID
