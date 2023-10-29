from langchain.embeddings import GPT4AllEmbeddings
from langchain.vectorstores import Qdrant

from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory


from langchain.text_splitter import CharacterTextSplitter
import os

import streamlit as st
from langchain.schema.document import Document


class runqa():

    def __init__(self, llm, text) -> None:
        self.llm = llm
        self.text = text

    def runChat(self):

        # os.environ["OPENAI_API_KEY"] = "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"

        text_splitter = CharacterTextSplitter(
            separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
        )

        # qaPromptText = """
        
        # """

        qaPromptText = PromptTemplate(
            input_variables=[
                "human_input",
                "chat_history",
                "context"
            ],
            template=(
                """
                [INST]
                <<SYS>>
                    You are a AI assistant whose expertise is reading and summarizing scientific papers.
                    You are given the chat history and a query.
                    Also attached, are the text embeddings that are most relevant to the document.
                    You are freely allowed to use / not use these to form your answer. The final answer is always dependant on you.
                    Skip the salutations and formalities, only output the answer.

                    {context}
                    History of the chat so far: 
                    {chat_history}

                    Query: 
                    {human_input}
                <</SYS>>

                Summary: [/INST]
                """
            )
        )

        chunks = text_splitter.split_text(self.text)

        # Declare the Memory
        # Should autoupdate once attached to the chain
        memory = ConversationBufferMemory(
            memory_key="chat_history", input_key="human_input")

        # Load the qa chain
        # Type: stuff, stuffs the whole document as context in the prompt
        chain = load_qa_chain(self.llm, chain_type="stuff",
                              memory=memory, prompt=qaPromptText)

        if "Helpful Answer:" in chain.llm_chain.prompt.template:
            chain.llm_chain.prompt.template = (
                f"### Human:{chain.llm_chain.prompt.template}".replace(
                    "Helpful Answer: You are a AI assistant whose expertise is reading and summarizing scientific papers. You are given a query, a series of text embeddings from a paper in order of their cosine similarity to the query. You must take the given embeddings and return a very detailed summary of the paper in the languange of the query.:", "\n### Assistant:"
                )
            )

        embeddings = GPT4AllEmbeddings()
        #embeddings = SentenceTransformerEmbeddings(model_name="flax-sentence-embeddings/all_datasets_v4_MiniLM-L6")

        knowledge_base = Qdrant.from_texts(
            chunks,
            embeddings,
            location=":memory:",
            collection_name="doc_chunks",
        )

        user_question = st.text_input("Ask a question about your PDF:")

        if user_question and user_question != "":
            docs = knowledge_base.similarity_search(user_question, k=4)
            # st.write(input_documents)
#             srcDocs = [Document(page_content="""
#     Just have the associate sign the back and then deposit it. It\'s called a third party cheque and is perfectly legal. I wouldn\'t be surprised if it has a longer hold period and, as always, you don\'t get the money if the cheque doesn\'t clear. Now, you may have problems if it\'s a large amount or you\'re not very well known at the bank. In that case you can have the associate go to the bank and endorse it in front of the teller with some ID. You don\'t even technically have to be there. Anybody can deposit money to your account if they have the account number. He could also just deposit it in his account and write a cheque to the business."I have checked with Bank of America, and they say the ONLY way to cash (or deposit, or otherwise get access to the funds represented by a check made out to my business) is to open a business account. They tell me this is a Federal regulation, and every bank will say the same thing. To do this, I need a state-issued ""dba"" certificate (from the county clerk\'s office) as well as an Employer ID Number (EIN) issued by the IRS. AND their CHEAPEST business banking account costs $15 / month. I think I can go to the bank that the check is drawn upon, and they will cash it, assuming I have documentation showing that I am the sole proprietor. But I\'m not sure.... What a racket!!"When a business asks me to make out a cheque to a person rather than the business name, I take that as a red flag. Frankly it usually means that the person doesn\'t want the money going through their business account for some reason - probably tax evasion. I\'m not saying you are doing that, but it is a frequent issue. If the company makes the cheque out to a person they may run the risk of being party to fraud. Worse still they only have your word for it that you actually own the company, and aren\'t ripping off your employer by pocketing their payment. Even worse, when the company is audited and finds that cheque, the person who wrote it will have to justify and document why they made it out to you or risk being charged with embezzlement. It\'s very much in their interests to make the cheque out to the company they did business with. Given that, you should really have an account in the name of your business. It\'s going to make your life much simpler in the long run.

# """)]
            # Grab and print response

            response = chain.run(
                input_documents=docs,
                human_input=user_question
            )
            # ValueError: Missing some input keys: {'input_documents', 'question'}
            # from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
            # from ragas.langchain import RagasEvaluatorChain

            # context = [""" """]
            # srcDocs = [doc for doc in docs]
            # # for doc in docs:
            # #      context += doc.page_content

            # queryDict = {'query': user_question,'ground_truths': context, 'source_documents': srcDocs, 'result': response}

            # # make eval chains
            # eval_chains = {
            #     m.name: RagasEvaluatorChain(metric=m)
            #     for m in [faithfulness, answer_relevancy, context_recall, context_precision]
            # }

            # for name, eval_chain in eval_chains.items():
            #     score_name = f"{name}_score"
            #     print(f"{score_name}: {eval_chain(queryDict)[score_name]}")

            # st.write("User: " + user_question)
            # st.write("AI: " + response)

            # questions_history.append(user_question)
            # answers_history.append(response)

            if 'questions_history' in st.session_state:
                questions_history = st.session_state['questions_history']
                questions_history.append(user_question)
                st.session_state['questions_history'] = questions_history

                answers_history = st.session_state['answers_history']
                answers_history.append(response)
                st.session_state['answers_history'] = answers_history

                reference_history = st.session_state['reference_history']
                reference_history.append(docs)
                st.session_state['reference_history'] = reference_history

            else:
                questions_history = []
                questions_history.append(user_question)

                answers_history = []
                answers_history.append(response)

                reference_history = []
                reference_history.append(docs)

                st.session_state['questions_history'] = questions_history
                st.session_state['answers_history'] = answers_history
                st.session_state['reference_history'] = reference_history

            # st.subheader("Answer: ")
            # st.success(response)

            # st.subheader("Referenced Chunks: ")
            # for i in range(len(docs)):
            #      st.info(docs[i].page_content)

        if 'questions_history' in st.session_state:
            questions_history = st.session_state.questions_history
            answers_history = st.session_state.answers_history
            reference_history = st.session_state.reference_history
            for i in range(len(answers_history)):
                # with st.chat_message("user"):
                #     st.write(questions_history[i])
                st.markdown(
                    f'<div class="user">{questions_history[i]}</div>', unsafe_allow_html=True)
                # st.write("User: " + questions_history[i])

                # with st.chat_message("assistant"):
                #     st.write(answers_history[i])

                st.markdown(
                    f'<div class="ai">{answers_history[i]}</div>', unsafe_allow_html=True)
                with st.expander("Referenced chunks: "):
                    for j in reference_history[i]:
                        st.write(j.page_content)
