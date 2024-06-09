from database.connection import get_db_connection

class Article:
    def __init__(self, id, title, content, author_id, magazine_id):
        if not isinstance(id, int):
            raise ValueError("ID must be an integer")
        if not isinstance(title, str) or not (5 <= len(title) <= 50):
            raise ValueError("Title must be a string between 5 and 50 characters")
        if not isinstance(content, str) or len(content) == 0:
            raise ValueError("Content must be a non-empty string")
        if not isinstance(author_id, int):
            raise ValueError("Author ID must be an integer")
        if not isinstance(magazine_id, int):
            raise ValueError("Magazine ID must be an integer")

        self._id = id
        self._title = title
        self._content = content
        self._author_id = author_id
        self._magazine_id = magazine_id

        # Insert into the database if it does not exist
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO articles (id, title, content, author_id, magazine_id)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET title = excluded.title, content = excluded.content,
            author_id = excluded.author_id, magazine_id = excluded.magazine_id
        ''', (id, title, content, author_id, magazine_id))
        conn.commit()
        conn.close()

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @property
    def content(self):
        return self._content

    @property
    def author(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT au.*
            FROM authors au
            JOIN articles a ON au.id = a.author_id
            WHERE a.id = ?
        ''', (self.id,))
        author_row = cursor.fetchone()
        conn.close()
        return Author(author_row['id'], author_row['name'])

    @property
    def magazine(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.*
            FROM magazines m
            JOIN articles a ON m.id = a.magazine_id
            WHERE a.id = ?
        ''', (self.id,))
        magazine_row = cursor.fetchone()
        conn.close()
        return Magazine(magazine_row['id'], magazine_row['name'], magazine_row['category'])

    def __repr__(self):
        return f'<Article {self.title}>'
