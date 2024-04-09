import sqlite3
import csv

class KnowledgeBaseManager:
    def __init__(self, db_file='knowledge_base.db'):
        self.db_file = db_file

    def connect_db(self):
        return sqlite3.connect(self.db_file)
    
    def update_data(self, question, new_answer):
        """
        kb_manager = KnowledgeBaseManager()
        question_to_update = "What is the capital of Italy?"
        new_answer = "Rome is the capital of Italy."
        kb_manager.update_data(question_to_update, new_answer)
        """
        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE knowledge SET answer = ? WHERE question = ?", (new_answer, question))
            conn.commit()
            print(f"Successfully updated the record with question: {question}")
        except sqlite3.Error as e:
            print(f"Error occurred: {e}")
        finally:
            conn.close()

    def insert_bulk_data(self, data):

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            cursor.executemany("INSERT INTO knowledge (question, answer) VALUES (?, ?)", data)
            conn.commit()
            print(f"Successfully inserted {len(data)} records into the database.")
        except sqlite3.IntegrityError as e:
            print(f"Error occurred: {e}")
        finally:
            conn.close()

    def insert_data_from_csv(self, csv_file):##############
        """
        Inserts data from a CSV file into the database.
        The CSV file should have two columns, where the first column is the question and the second is the answer.

        :param csv_file: The path to the CSV file to import
        """
        data = []
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                # Assuming the first column is the question and the second column is the answer
                data.append((row[0], row[1]))

        self.insert_bulk_data(data)

    def remove_data_bulk(self, questions):
    
        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            question_placeholders = ','.join(['?' for _ in questions])  # Create placeholders for the query
            cursor.execute(f"DELETE FROM knowledge WHERE question IN ({question_placeholders})", questions)
            conn.commit()
            print(f"Successfully removed records for questions: {', '.join(questions)}")
        except sqlite3.Error as e:
            print(f"Error occurred: {e}")
        finally:
            conn.close()

    def view_all_data(self):
    
        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM knowledge")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
        finally:
            conn.close()

    def delete_all_data(self):
     
        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM knowledge")
            conn.commit()
            print("Successfully deleted all records from the database.")
        except sqlite3.Error as e:
            print(f"Error occurred: {e}")
        finally:
            conn.close()
