import sqlite3

class ExamDataStore:
    def __init__(self, db_path='database/exam_platform.db'):
        self.db_path = db_path

    # تأكد أن هذه الدالة موجودة داخل الكلاس وبدايتها self
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_all_books(self):
        conn = self.get_connection()
        rows = conn.execute('SELECT subject_name, book_pdf_path FROM subjects').fetchall()
        conn.close()
        return [
            {
                "title": row['subject_name'],
                "view_url": row['book_pdf_path'],  # شيل السلاش من هنا
                "download_url": row['book_pdf_path']  # شيل السلاش من هنا
            } for row in rows
        ]

    def get_all_papers(self):
        conn = self.get_connection()
        rows = conn.execute('SELECT subject_name, questions_pdf_path FROM subjects').fetchall()
        conn.close()
        return [
            {
                "title": row['subject_name'],
                "view_url": row['questions_pdf_path'],  # شيل السلاش من هنا
                "download_url": row['questions_pdf_path']  # شيل السلاش من هنا
            } for row in rows
        ]