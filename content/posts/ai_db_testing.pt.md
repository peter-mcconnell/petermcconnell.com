+++
title = "chatGPT - construindo uma ferramenta automatizada de teste de banco de dados"
date = "2022-12-08T11:41:50Z"
author = ""
authorTwitter = "PeteMcConnell_" #do not include @
cover = ""
tags = ["chatGPT", "SQL", "Python"]
keywords = ["chatGPT", "sql"]
description = ""
showFullContent = false
readingTime = false
hideComments = false
color = "" #color from the theme settings
+++

Criando uma ferramenta automatizada de teste de banco de dados com ChatGPT
--------------------------------------------------------------------------

Ontem à noite pensei em tentar fazer com que o ChatGPT criasse um banco de dados automatizado
ferramenta de teste e os resultados foram bastante promissores.

Em conclusão, com orientação, foi capaz de construir um projeto de raiz que
executou um script python e um banco de dados postgres. Ele gerou algum esquema aleatório e
valores para as tabelas geradas aleatoriamente. Ele forneceu um script Python que
faria uma introspecção do banco de dados e executaria consultas nele.

Tudo funcionou fora da caixa? Não. Existem alguns bugs para corrigir no python
script que ele gerou. No entanto, o esforço para consertá-los não é alto e
certamente todo o processo de ponta a ponta é mais barato, em termos de tempo, em comparação com
começando do zero.

Descobri que os bugs encontrados eram em grande parte devido à minha falta de clareza ou
ordenação das questões que lhe são colocadas. Era perfeitamente capaz de consertar seu próprio
erros / atualização do código existente para corresponder aos novos requisitos ao
solicitado a fazê-lo.

O único problema _real_ que encontrei foram erros gerais de API que
esperar de algo tão popular em um estado de visualização inicial.

Saí desta experiência visualizando o ChatGPT e tudo o que o segue como um
auxiliar de desenvolvimento realmente útil para quem já sabe programar. Isto
me ajudou a construir uma ferramenta mais rápido do que eu poderia ter feito se tivesse sentado para fazê-lo de
coçar, arranhão. Ainda não o vejo como um substituto para engenheiros de software para dois
razões principais - em primeiro lugar: para aplicações não triviais, suspeito que a pessoa
requisitos de alimentação no sistema (ou "engenheiro de prompt") precisa ter um
ideia razoável de como construir software em primeiro lugar, para saber como
formular solicitações e corrigir erros / preencher lacunas. em segundo lugar: o código sendo
gerado nem sempre é bom - sem um engenheiro experiente revisando e
tomando posse de qualquer código que seja produzido (propriedade sendo importante para
razões de manutenção), então há pouca garantia de que você obterá o que
estão esperando.

No entanto; isso ainda é muito cedo. Os problemas descritos podem ser fechados
avançar? Absolutamente. Esse tipo de ferramenta será "ruim" para software
engenharia como um todo, a longo prazo? Possivelmente. Pessoalmente, estou muito animado por ter
esta ferramenta em meu arsenal - já me permitiu construir um protótipo de scaffold
aplicações rapidamente. Eu o usaria para código de produção em um local de trabalho? Não
mais ou menos do que eu faria com trechos de stackoverflow ou algo parecido. Por agora.

Repositório Github: https://github.com/peter-mcconnell/gpt_sql_test_generator

Capturas de tela:

![step 2](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/2.png "step 2")
![step 3](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/3.png "step 3")
![step 4](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/4.png "step 4")
![step 5](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/5.png "step 5")
![step 6](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/6.png "step 6")
![step 7](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/7.png "step 7")
![step 8](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/8.png "step 8")
![step 9](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/9.png "step 9")
![step 10](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/10.png "step 10")
![step 11](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/11.png "step 11")
![step 12](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/12.png "step 12")
![step 13](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/13.png "step 13")
![step 14](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/14.png "step 14")
![step 15](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/15.png "step 15")
![step 16](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/16.png "step 16")
