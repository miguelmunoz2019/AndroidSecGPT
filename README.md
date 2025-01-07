# AndroidSecGPT
## Chunks
Carpeta que almacena todos los chunks procesados de los diferentes documentos utilizados para poblar la base de datos
## chroma.py
Archivo .py que pobla la base de datos Chromadb_store
## chromaL.py
Archivo .py que pobla la base de datos Chromadb_storeL
## Chromadb_store
Contiene la base de datos para el modelo xlm-roberta-base
## Chromadb_storeL
Contiene la base de datos para el modelo xlm-roberta-large
## AndroidSecGPT.py
El archivo principal para el funcionamiento del proyecto es AndroidSecGPT.py. Al ejecutarlo le pide al usuario su llave para el API de Open IA dado que necesita una llave de este tipo para poder hacer uso del API y comunicarse con los modelos GPT, despues solicita que tipo de modelo xlm-roberta desea usar y que tipo de modelo GPT desea utilizar. Una vez obtenida esta informacion, hace uso de Chromadb_store y Chromadb_storeL para usar el modelo xlm-roberta-base o xlm-roberta-large respectivamente, despues de cargar la coleccion que hay en la respectiva base de datos y solicita al usuario que indique como desea realizar las preguntas. Hay 3 opciones. La primera opcion es para realizar una pregunta individual que tendrá una respuesta especifica y esta respuesta quedará almacenada en el archivo AndroidSecGPTAnswer.txt . La segunda opcion permite realizar multiples preguntas en sucesion, respondera cada una pero solo almaccenara la ultima de estas en el archivo AndroidSecGPTAnswer.txt . Finalmente la tercera opcion permite responder un grupo de preguntas que esten en el archivo Excel questions.xlsx,respondera todas las preguntas del archivo, almacenando adicionalmente la respuesta hipotetica y el contexto utilizado para responder la pregunta.
## CalcularMetricas.py
Archivo que fue utilizado para calcular las metricas BERT, Rouge-L y BLEU
## Questions.xlsx
Archivo excel donde se deben almacenar las preguntas que se desea se respondan con la opcion 3 de AndroidSecGPT.py
## AndroidSecGPTAnswer.txt
Archivo para almacenar la ultima respuesta producida por el modelo en las opciones 1 y 2 de AndroidSecGPT.py

