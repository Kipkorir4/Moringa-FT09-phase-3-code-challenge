from database.connection import get_db_connection

class Magazine:
    def __init__(self, id, name, category=None):
        if not isinstance(id, int):
            raise ValueError("ID must be an integer")
        if not isinstance(name, str) or not (2 <= len(name) <= 16):
            raise ValueError("Name must be a string between 2 and 16 characters")

        self._id = id
        self._name = name
        self._category = category or "General"

        # Insert into the database if it does not exist
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO magazines (id, name, category)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET name = excluded.name, category = excluded.category
        ''', (id, name, self._category))
        conn.commit()
        conn.close()

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if isinstance(new_name, str) and 2 <= len(new_name) <= 16:
            self._name = new_name
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE magazines SET name = ? WHERE id = ?', (new_name, self._id))
            conn.commit()
            conn.close()
        else:
            raise ValueError("Name must be a string between 2 and 16 characters")

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, new_category):
        if isinstance(new_category, str) and len(new_category) > 0:
            self._category = new_category
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE magazines SET category = ? WHERE id = ?', (new_category, self._id))
            conn.commit()
            conn.close()
        else:
            raise ValueError("Category must be a non-empty string")

    def articles(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*
            FROM articles a
            WHERE a.magazine_id = ?
        ''', (self.id,))
        rows = cursor.fetchall()
        conn.close()
        return [Article(row['id'], row['title'], row['content'], row['author_id'], row['magazine_id']) for row in rows]

    def contributors(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT au.*
            FROM authors au
            JOIN articles a ON au.id = a.author_id
            WHERE a.magazine_id = ?
        ''', (self.id,))
        rows = cursor.fetchall()
        conn.close()
        return [Author(row['id'], row['name']) for row in rows]

    def article_titles(self):
        articles = self.articles()
        return [article.title for article in articles] if articles else None

    def contributing_authors(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT au.*, COUNT(a.id) as article_count
            FROM authors au
            JOIN articles a ON au.id = a.author_id
            WHERE a.magazine_id = ?
            GROUP BY au.id
            HAVING article_count > 2
        ''', (self.id,))
        rows = cursor.fetchall()
        conn.close()
        return [Author(row['id'], row['name']) for row in rows] if rows else None

    def __repr__(self):
        return f'<Magazine {self.name}>'
