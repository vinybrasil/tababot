TABABOT: A RAG question answering bot to provide tabacco related information in Portuguese
===

TABABOT is a RAG question answering bot that provides tabacco related information in Portuguese. The source of the answers is the Clinical Protocol and
Therapeutic Guidelines for Smoking of the Brazilian Ministry of Health and it can be downloaded [here](https://www.inca.gov.br/sites/ufu.sti.inca.local/files//media/document//protocolo-clinico-e-diretrizes-terapeuticas-do-tabagismo.pdf). 

About the engine of the bot, the LLM model used is [LLama3 8B](https://llama.meta.com/llama3/). An improvement for the future of the bot is to use a finetuned model in Portuguese.

Quickstart
---

The project uses Ollama as the backend for the LLM. 
```bash
ollama serve
```
To serve the API, run
```bash
uvicorn src.main:app
```
The request must be a JSON with a "question" key:
```python
import requests

data = {"question": " Quais as contraindicações específicas da pastilha de nicotina?"}

print(requests.post('http://localhost:8000/api/v1/question', json=data))

```

Install 
---

The dependencies of the project can be install using

```bash
pip install -r requirements.txt
```

It was developed using Python 3.8. 


Examples
---
Here's a question from the first paragraph of page 16:
* Question: No que consiste o tratamento para cessação do tabagismo no SUS?
* Answer: O tratamento para cessação do tabagismo no SUS consiste no aconselhamento terapêutico estruturado/abordagem intensiva, acompanhado pelo tratamento medicamentoso. O tempo de tratamento total preconizado é de 12 meses e envolve as etapas de avaliação, intervenção e manutenção da abstinência.

It can answer in a list format. Here's a question from the first paragraph of page 22:
* Question: Quais as contraindicações específicas da pastilha de nicotina?
* Answer: Contraindicações específicas para a pastilha de nicotina mencionadas no texto são:
    * Lesões na mucosa bucal
    * Úlcera péptica
    * Uso de próteses dentárias móveis
    * Edema de corda vocal (edema de Reinke)

There's still some problems with the response (the year is poorly formatted):
* Question: Quantas mortes por tabaco foram estimadas pela OMS para 2030?
* Answer: Segundo o texto, a Organização Mundial de Saúde (OMS) estimou que, caso não sejam adotadas medidas para o controle e cessação do tabagismo, haveriam aproximadamente 8 milhões de mortes em todo o mundo por doenças relacionadas ao tabaco no ano de 20[30].


Since it only answers questions about tabacco, it cannot answer questions about crack, for example.
* Question: Como é classificado o crack?
* Answer: Não tem dados disponíveis para responder essa pergunta. O texto não menciona o crack em nenhum momento, portanto não posso fornecer uma resposta com base nas informações fornecidas.

TODO
---
* Containerize with Docker
* Handle stream response from Ollama
* Use poetry for dependency management
* Save the vectorstore and load it
* Unit tests
* Save to a database the requests and their statuses
* use Fields in the APIs ID scheme
* use a embedding model with portuguese