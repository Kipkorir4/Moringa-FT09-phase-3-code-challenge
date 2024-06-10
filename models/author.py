# from models.article import Article
from database.connection import get_db_connection

class Author:
    def __init__(self, id, name):
        if not isinstance(id, int):
            raise ValueError("ID must be an integer")
        if not isinstance(name, str) or len(name) == 0:
            raise ValueError("Name must be a non-empty string")

        self._id = id
        self._name = name

        # Insert into the database if it does not exist
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO authors (id, name)
            VALUES (?, ?)
            ON CONFLICT(id) DO UPDATE SET name = excluded.name
        ''', (id, name))
        conn.commit()
        conn.close()

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    def articles(self):
        from models.article import Article  # Delayed import
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM articles WHERE author_id = ?', (self.id,))
        articles_rows = cursor.fetchall()
        conn.close()
        return [Article(row['id'], row['title'], row['content'], row['author_id'], row['magazine_id']) for row in articles_rows]

    def magazines(self):
        from models.magazine import Magazine  # Delayed import
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT magazines.* FROM magazines
            JOIN articles ON magazines.id = articles.magazine_id
            WHERE articles.author_id = ?
        ''', (self.id,))
        magazine_rows = cursor.fetchall()
        conn.close()
        return [Magazine(row['id'], row['name'], row['category']) for row in magazine_rows]
    
    def __repr__(self):
        return f'<Author {self.name}>'
