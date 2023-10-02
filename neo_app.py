import os

from flask import Flask, request, jsonify
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from flask_cors import CORS

## updated langchain folder with custom prompts and custom chains

app = Flask(__name__)
CORS(app)
vectorstore = Chroma(persist_directory="./neo_storage", embedding_function=OpenAIEmbeddings())

model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.1)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

qa = ConversationalRetrievalChain.from_llm(
    model,
    vectorstore.as_retriever(),
    return_source_documents=True
)

def get_query_with_contract(query, contract):
    return """Given the smart contract code on Neo Blockchain: \n {contract}\n\n{query}"""

@app.route("/chat", methods=["POST"])
def chat():
    """Chat with the Neo Assistant."""
    query = request.json["query"]
    chat_history = request.json.get("chat_history", [])
    contract_code = request.json.get("contract_code", "")
    # chat_history = [tuple(x) for x in chat_history]

    if contract_code is not "":
        query = get_query_with_contract(query, contract_code)

    result = qa({"question": query, "chat_history": []})
    answer = result["answer"]
    source_documents = list(set([result["source_documents"][i].metadata["source"] for i in range(len(result["source_documents"]))]))

    response = {"answer": answer, "source_documents": source_documents}
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
