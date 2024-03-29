+++
title = "chatGPT: creación de una herramienta de prueba de base de datos automatizada"
date = "2022-12-08T11:41:50Z"
author = ""

cover = ""
tags = ["chatGPT", "SQL", "Python"]
keywords = ["chatGPT", "sql"]
description = ""
showFullContent = false
readingTime = false
hideComments = false
color = "" #color from the theme settings
+++

Creación de una herramienta de prueba de base de datos automatizada con ChatGPT
-------------------------------------------------------------------------------

Anoche pensé en intentar que ChatGPT creara una base de datos automatizada
herramienta de prueba y los resultados fueron bastante prometedores.

En conclusión, con orientación, fue capaz de construir un proyecto desde cero que
ejecutó un script de python y una base de datos de postgres. Generó un esquema aleatorio y
valores para las tablas generadas aleatoriamente. Proporcionó un script de Python que
introspeccionaría la base de datos y ejecutaría consultas contra ella.

¿Funcionó todo fuera de la caja? No. Hay algunos errores que corregir en python.
guión que generó. Sin embargo, el esfuerzo para entrar y arreglarlos no es alto y
ciertamente, todo el proceso de extremo a extremo es más barato, en términos de tiempo, en comparación con
comenzando desde cero.

Descubrí que los errores que encontró se debían en gran medida a mi falta de claridad o
orden de las preguntas que se le plantean. Era bastante capaz de arreglar su propio
errores / actualizar el código existente para que coincida con los nuevos requisitos cuando
solicitado para hacerlo.

El único problema _real_ que encontré fueron los errores generales de API que uno
esperar de algo tan popular en un estado de vista previa temprana.

Salí de este experimento viendo ChatGPT y todo lo que sigue como un
ayudante de desarrollo realmente útil para aquellos que ya saben programar. Eso
me ayudó a construir una herramienta más rápido de lo que podría haberlo hecho si me hubiera sentado a hacerlo desde
rasga. Todavía no lo veo como un reemplazo para los ingenieros de software para dos
razones principales - en primer lugar: para aplicaciones no triviales sospecho que la persona
requisitos de alimentación en el sistema (o "ingeniero rápido") necesita tener un
idea razonable de cómo construir software en primer lugar, para saber cómo
para formar solicitudes y para corregir errores / cerrar brechas. en segundo lugar: el código siendo
generado no siempre es sólido, sin un ingeniero experimentado que revise y
tomar posesión de cualquier código que se produzca (la propiedad es importante para
razones de mantenimiento), entonces hay pocas garantías de que obtendrá lo que desea.
están esperando.

Sin embargo; esto es todavía muy pronto. ¿Se pueden cerrar los problemas descritos?
¿más lejos? Absolutamente. ¿Será este tipo de herramientas "malas" para el software?
ingeniería en su conjunto, a largo plazo? Tal vez. Personalmente, estoy muy emocionado de tener
esta herramienta en mi arsenal - ya me ha permitido andamiar prototipo
aplicaciones rápidamente. ¿Lo usaría para el código de producción en un lugar de trabajo? No
más o menos de lo que haría con fragmentos de stackoverflow o de su calaña. Por ahora.

Repositorio Github: https://github.com/peter-mcconnell/gpt_sql_test_generator

Capturas de pantalla:

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
