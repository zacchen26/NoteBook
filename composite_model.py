import os
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from rank_bm25 import BM25Okapi
from alpha.text_processor import TextProcessor

class CompositeModel:
    def __init__(self, glove_file='glove.6B.100d.txt', model_file='historyBM25.pkl'):
        self.text_processor = TextProcessor()
        self.word_embeddings = self.load_glove_embeddings(glove_file)
        self.documents = []  # Stores processed documents
        self.original_documents = {}  # Maps processed text to original text
        self.model_file = model_file
        self.bm25 = None
        self.load_model(model_file)

    def load_glove_embeddings(self, glove_file):
        print(f"Loading GloVe embeddings from {glove_file}")
        embeddings = {}
        with open(glove_file, 'r', encoding='utf-8') as f:
            for line in f:
                values = line.split()
                word = values[0]
                vector = np.asarray(values[1:], dtype='float32')
                embeddings[word] = vector
        return embeddings

    def load_model(self, model_file):
        if not os.path.exists(model_file):
            print(f"No pre-existing model found at {model_file}. Initializing from scratch.")
            return

        try:
            with open(model_file, 'rb') as f:
                saved_model = pickle.load(f)
                self.documents = saved_model.get('documents', self.documents)
                self.original_documents = saved_model.get('original_documents', self.original_documents)
                tokenized_docs = [doc.split(" ") for doc in self.documents]
                self.bm25 = BM25Okapi(tokenized_docs)
                print(f"Loaded model from {model_file}")
        except Exception as e:
            print(f"Error loading model: {e}. Initializing from scratch.")

    def save_model(self, file_name=None):
        if not file_name:
            file_name = self.model_file
        os.makedirs(os.path.dirname(file_name) or '.', exist_ok=True)
        try:
            with open(file_name, 'wb') as f:
                data_to_save = {
                    'documents': self.documents,
                    'original_documents': self.original_documents
                }
                pickle.dump(data_to_save, f)
                print(f"Model saved to {file_name}")
        except Exception as e:
            print(f"Error saving model: {e}")

    def get_text_vector(self, text):
        words = text.split()
        vectors = [self.word_embeddings.get(word, np.zeros(100)) for word in words]
        return np.mean(vectors, axis=0) if vectors else np.zeros(100)

    def update(self, processed_docs, original_docs=None):
        # Check if original_docs is provided and has the same length as processed_docs
        if original_docs and len(processed_docs) == len(original_docs):
            for orig, proc in zip(original_docs, processed_docs):
                # Update the documents and original_documents only if not already present
                if proc not in self.documents:
                    self.documents.append(proc)
                    self.original_documents[proc] = orig
        else:
            # If no original_docs provided, just add the processed_docs that are not already present
            for proc in processed_docs:
                if proc not in self.documents:
                    self.documents.append(proc)
                    # Since no original document is provided, map processed doc to itself
                    self.original_documents[proc] = proc

        # Tokenize documents for BM25
        tokenized_docs = [doc.split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        self.save_model()  # Save the model after updating

    def retrieve_ranklist(self, query):
        query_processed = self.text_processor.process(query)
        query_tokenized = query_processed.split()

        bm25_scores = self.bm25.get_scores(query_tokenized)

        if len(bm25_scores) > 0:
            max_bm25 = max(bm25_scores)
            if max_bm25 > 0:
                normalized_bm25_scores = [score / max_bm25 for score in bm25_scores]
            else:
                normalized_bm25_scores = [0 for _ in bm25_scores]  # Avoid division by zero
        else:
            normalized_bm25_scores = []

        scores = []
        for idx, doc in enumerate(self.documents):
            original_text = self.original_documents.get(doc, doc)
            
            doc_w2v = self.get_text_vector(doc)
            query_w2v = self.get_text_vector(query_processed)
            word2vec_score = np.dot(doc_w2v, query_w2v) / (np.linalg.norm(doc_w2v) * np.linalg.norm(query_w2v)) if np.any(doc_w2v) and np.any(query_w2v) else 0

            bm25_score = normalized_bm25_scores[idx] if idx < len(normalized_bm25_scores) else 0
            final_score = 0.5* bm25_score + 0.5 * word2vec_score
            scores.append((final_score, original_text, bm25_score, word2vec_score))

        scores.sort(reverse=True, key=lambda x: x[0])
        unique_scores = []
        for score in scores:
            if score[1] not in [u[1] for u in unique_scores]:
                unique_scores.append(score)
            if len(unique_scores) == 3:
                break

        return unique_scores