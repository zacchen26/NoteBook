import sqlite3
from alpha.composite_model import CompositeModel
from alpha.text_processor import TextProcessor

class SearchEngineBot1:
    def __init__(self, db_file='knowledge_base.db'):
        self.db_file = db_file
        self.processor = TextProcessor()
        self.model = CompositeModel()
        self.load_knowledge_base()

    def log_interaction(self, query, response, feedback, bm25_score, word2vec_score):
        text, final_score = response  # Unpack the response tuple
        with open('user_interactions.csv', 'a') as file:
            file.write(f"{query},{text},{final_score},{bm25_score},{word2vec_score},{feedback}\n")

    def load_knowledge_base(self):
        knowledge_entries = self.fetch_knowledge_entries()
        processed_entries = []
        original_texts = []
        for entry in knowledge_entries:
            original_text = entry[1] + ' ' + entry[2]
            processed_text = self.processor.process(original_text)
            processed_entries.append(processed_text)
            original_texts.append(original_text)
        self.model.update(processed_entries, original_texts)

    def fetch_knowledge_entries(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT id, question, answer FROM knowledge")
            entries = cursor.fetchall()
            conn.close()
            return entries
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def update_knowledge_base(self, question, answer):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO knowledge (question, answer) VALUES (?, ?)", (question, answer))
            conn.commit()
            conn.close()
        
            processed_entry = self.processor.process(question + ' ' + answer)
            self.model.update([processed_entry])
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def run(self):
        print("Hello! I'm a knowledge bot. Ask me anything or type 'quit' to exit.")
        while True:
            user_input = input("\nWhat would you like to know?\n> ")
            if user_input.lower() == 'quit':
                break

            processed_query = self.processor.process(user_input)
            ranked_docs = self.model.retrieve_ranklist(processed_query)

            if ranked_docs:
                print("\nI found some information that might help:")
                for idx, (score, doc, bm25_score, word2vec_score) in enumerate(ranked_docs, 1):
                    print(f"{idx}. {doc} (Score: {score})")

                feedback = input("\nDid this answer your question? [yes/no]\n> ").lower()
                if feedback == 'no':
                    correct_answer = input("What is the correct answer?\n> ")
                    self.update_knowledge_base(user_input, correct_answer)
                    print("Thank you! I've learned something new.")

                # Log interaction after feedback
                top_response = ranked_docs[0][1], ranked_docs[0][0]
                self.log_interaction(user_input, top_response, feedback, ranked_docs[0][2], ranked_docs[0][3])

            else:
                print("\nI don't have the answer to that. Can you provide more context or ask another question?")

    """
    def run(self):
        print("Hello! I'm a knowledge bot. Ask me anything or type 'quit' to exit.")
        while True:
            user_input = input("\nWhat would you like to know?\n> ")
            if user_input.lower() == 'quit':
                break

            processed_query = self.processor.process(user_input)
            ranked_docs = self.model.retrieve_ranklist(processed_query)

            if ranked_docs:
                print("\nI found some information that might help:")
                for idx, (score, doc, bm25_score, word2vec_score) in enumerate(ranked_docs, 1):
                    print(f"{idx}. {doc} (Score: {score})")

                feedback = input("\nDid this answer your question? [yes/no]\n> ").lower()
                if feedback == 'no':
                    correct_answer = input("What is the correct answer?\n> ")
                    self.update_knowledge_base(user_input, correct_answer)
                    print("Thank you! I've learned something new.")
            else:
                print("\nI don't have the answer to that. Can you provide more context or ask another question?")
                continue  # Continue to the next loop iteration without asking for feedback

            if ranked_docs:
                top_response = ranked_docs[0][1], ranked_docs[0][0]
                self.log_interaction(user_input, top_response, feedback, ranked_docs[0][2], ranked_docs[0][3])
    """

    