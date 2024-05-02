import logging
import uuid

from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from unstructured.partition.pdf import partition_pdf

from src.schemas import Element

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s  - %(message)s')


def build_dataset():
    raw_pdf_elements = partition_pdf(
        #filename="/home/vinybrasil/random_projects/llms/tutorial_chatbot/data/protocolo-clinico-e-diretrizes-terapeuticas-do-tabagismo.pdf",
        filename="utilities/protocolo-clinico-e-diretrizes-terapeuticas-do-tabagismo.pdf",
        extract_images_in_pdf=False,
        infer_table_structure=True,
        strategy="hi_res",
        chunking_strategy="by_title",
        languages=["por"],
        max_characters=800,
        combine_text_under_n_chars=100,
        #image_output_dir_path="/home/vinybrasil/random_projects/llms/tutorial_chatbot/data/",
    )

    category_counts = {}

    for element in raw_pdf_elements:
        category = str(type(element))
        if category in category_counts:
            category_counts[category] += 1
        else:
            category_counts[category] = 1

    categorized_elements = []
    for element in raw_pdf_elements:
        if "unstructured.documents.elements.Table" in str(type(element)):
            categorized_elements.append(Element(type="table", text=str(element)))
        elif "unstructured.documents.elements.CompositeElement" in str(type(element)):
            categorized_elements.append(Element(type="text", text=str(element)))


    text_elements = [e for e in categorized_elements if e.type == "text"]
    texts = [i.text for i in text_elements]
    # print(len(table_elements))
    logging.info(f'Number of text chunks found: {len(text_elements)}')
    table_elements = [e for e in categorized_elements if e.type == "table"]
    tables = [i.text for i in table_elements]
    logging.info(f'Number of tables chunks found: {len(text_elements)}')

    return texts, tables


def load_vectorstore(folder_path="db22"):
    store = InMemoryStore()
    id_key = "doc_id"

    embedding = FastEmbedEmbeddings()
    vectorstore = Chroma(
        collection_name="summaries11",
        embedding_function=embedding,
        #persist_directory=folder_path,
    )

    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=store,
        id_key=id_key,
    )

    # breakpoint()
    # retriever = vectorstore.as_retriever(
    #     search_type="similarity_score_threshold",
    #     search_kwargs={
    #         "k":10,
    #         "score_threshold": 0.5,
    #     },
    # )

    return retriever, id_key


def add_raw_data(texts, tables, retriever, id_key):
    if len(texts) > 0:
        doc_ids = [str(uuid.uuid4()) for _ in texts]
        summary_texts = [
            Document(page_content=s, metadata={id_key: doc_ids[i]})
            for i, s in enumerate(texts)
        ]
        retriever.vectorstore.add_documents(summary_texts)
        retriever.docstore.mset(list(zip(doc_ids, texts)))

    if len(tables) > 0:
        table_ids = [str(uuid.uuid4()) for _ in tables]
        summary_tables = [
            Document(page_content=s, metadata={id_key: table_ids[i]})
            for i, s in enumerate(tables)
        ]
        retriever.vectorstore.add_documents(summary_tables)
        retriever.docstore.mset(list(zip(table_ids, tables)))

    retriever.vectorstore.persist()


def create_model(retriever):
    template = """Context: Você é um assistente especialista em pesquisar informações em documentos.\
    Responda apenas com as informações do texto e, se você não tiver uma resposta com base nelas, \
        informe-me dizendo que você não tem dados disponíveis para respondê-las. O texto é o seguinte:
    {context}
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    model = Ollama(model="llama3")

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )
    return chain


def build_chain():
    texts, tables = build_dataset()
    retriever, id_key = load_vectorstore()
    add_raw_data(texts, tables, retriever, id_key)
    chain = create_model(retriever)
    return chain
