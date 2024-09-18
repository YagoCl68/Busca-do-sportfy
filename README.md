# Spotify Fake
 Trabalho de Engenharia de Software

## Antes de tudo...
 Primeiro passo vai criar e inicializar um ambiente virtual para este projeto
 - ```pip install poetry```
 - ```poetry new {nome_projeto}```
 - ```cd {nome_projeto}```
 - ```poetry shell```
   
Em seguida vamos instalar as bibliotecas necessárias como fastapi (que é a principal ferramenta para abrir o servidor e realizar as operações), pydantic (para validação de entrada e saída de dados), ruff (para "legibilidade"), taskipy (para abstrair comandos longos) e pytest (para realizar testes - como o próprio nome fala...)

 - ```poetry add {nome_biblioteca}```
 - ```poetry update``` (é importante que sempre faça isso para atualizar alguma ferramenta e evitar erros)
   
Recomendo que antes do poetry update escrever o seu arquivo .toml semelhante a meu. E por fim, já podemos iniciar o "servidor" e por a mão na massa! como ```task run``` (personalizei este comando para iniciar o fastapi e o servidor)
