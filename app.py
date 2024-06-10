from database.setup import create_tables
from database.connection import get_db_connection
from models.article import Article
from models.author import Author
from models.magazine import Magazine

def get_valid_input(prompt, validation_fn, error_message):
    while True:
        value = input(prompt)
        if validation_fn(value):
            return value
        else:
            print(error_message)

def main():
    # Initialize the database and create tables
    create_tables()

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- CREATE RECORDS ---
    print("\n--- CREATE RECORDS ---")

    # Collect user input with validation
    author_name = get_valid_input(
        "Enter author's name: ",
        lambda name: isinstance(name, str) and len(name.strip()) > 0,
        "Author's name must be a non-empty string."
    )

    magazine_name = get_valid_input(
        "Enter magazine name: ",
        lambda name: isinstance(name, str) and 2 <= len(name.strip()) <= 16,
        "Magazine's name must be a string between 2 and 16 characters."
    )

    magazine_category = get_valid_input(
        "Enter magazine category: ",
        lambda category: isinstance(category, str) and len(category.strip()) > 0,
        "Magazine's category must be a non-empty string."
    )

    article_title = get_valid_input(
        "Enter article title: ",
        lambda title: isinstance(title, str) and 5 <= len(title.strip()) <= 50,
        "Article's title must be a string between 5 and 50 characters."
    )

    article_content = get_valid_input(
        "Enter article content: ",
        lambda content: isinstance(content, str) and len(content.strip()) > 0,
        "Article's content must be a non-empty string."
    )

    try:
        # Create an author
        cursor.execute('INSERT INTO authors (name) VALUES (?)', (author_name,))
        author_id = cursor.lastrowid  # Fetch the ID of the newly created author

        # Create a magazine
        cursor.execute('INSERT INTO magazines (name, category) VALUES (?, ?)', (magazine_name, magazine_category))
        magazine_id = cursor.lastrowid  # Fetch the ID of the newly created magazine

        # Create an article
        cursor.execute(
            'INSERT INTO articles (title, content, author_id, magazine_id) VALUES (?, ?, ?, ?)',
            (article_title, article_content, author_id, magazine_id)
        )
        article_id = cursor.lastrowid  # Fetch the ID of the newly created article

        conn.commit()

        # Display created records
        print("\nCreated Author:", Author(author_id, author_name))
        print("Created Magazine:", Magazine(magazine_id, magazine_name, magazine_category))
        print("Created Article:", Article(article_id, article_title, article_content, author_id, magazine_id))

    except ValueError as e:
        print(f"Error: {e}")
        conn.rollback()

    # --- READ RECORDS ---
    print("\n--- READ RECORDS ---")
    cursor.execute('SELECT * FROM authors WHERE id = ?', (author_id,))
    author_row = cursor.fetchone()
    author = Author(author_row['id'], author_row['name'])

    cursor.execute('SELECT * FROM magazines WHERE id = ?', (magazine_id,))
    magazine_row = cursor.fetchone()
    magazine = Magazine(magazine_row['id'], magazine_row['name'], magazine_row['category'])

    cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
    article_row = cursor.fetchone()
    article = Article(article_row['id'], article_row['title'], article_row['content'], article_row['author_id'], article_row['magazine_id'])

    print("Read Author:", author)
    print("Read Magazine:", magazine)
    print("Read Article:", article)

    # --- UPDATE RECORDS ---
    print("\n--- UPDATE RECORDS ---")

    new_author_name = get_valid_input(
        "Enter new author's name: ",
        lambda name: isinstance(name, str) and len(name.strip()) > 0,
        "Author's name must be a non-empty string."
    )

    new_magazine_name = get_valid_input(
        "Enter new magazine name: ",
        lambda name: isinstance(name, str) and 2 <= len(name.strip()) <= 16,
        "Magazine's name must be a string between 2 and 16 characters."
    )

    new_article_title = get_valid_input(
        "Enter new article title: ",
        lambda title: isinstance(title, str) and 5 <= len(title.strip()) <= 50,
        "Article's title must be a string between 5 and 50 characters."
    )

    try:
        cursor.execute('UPDATE authors SET name = ? WHERE id = ?', (new_author_name, author_id))
        cursor.execute('UPDATE magazines SET name = ? WHERE id = ?', (new_magazine_name, magazine_id))
        cursor.execute('UPDATE articles SET title = ? WHERE id = ?', (new_article_title, article_id))

        conn.commit()

        # Fetch and display updated records
        cursor.execute('SELECT * FROM authors WHERE id = ?', (author_id,))
        updated_author = cursor.fetchone()
        print("Updated Author:", Author(updated_author['id'], updated_author['name']))

        cursor.execute('SELECT * FROM magazines WHERE id = ?', (magazine_id,))
        updated_magazine = cursor.fetchone()
        print("Updated Magazine:", Magazine(updated_magazine['id'], updated_magazine['name'], updated_magazine['category']))

        cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
        updated_article = cursor.fetchone()
        print("Updated Article:", Article(updated_article['id'], updated_article['title'], updated_article['content'], updated_article['author_id'], updated_article['magazine_id']))

    except ValueError as e:
        print(f"Error: {e}")
        conn.rollback()

    # --- DELETE RECORDS ---
    print("\n--- DELETE RECORDS ---")
    delete_author = input("Do you want to delete the author? (yes/no): ").lower() == "yes"
    delete_magazine = input("Do you want to delete the magazine? (yes/no): ").lower() == "yes"
    delete_article = input("Do you want to delete the article? (yes/no): ").lower() == "yes"

    if delete_author:
        cursor.execute('DELETE FROM authors WHERE id = ?', (author_id,))
        print("Author deleted.")

    if delete_magazine:
        cursor.execute('DELETE FROM magazines WHERE id = ?', (magazine_id,))
        print("Magazine deleted.")

    if delete_article:
        cursor.execute('DELETE FROM articles WHERE id = ?', (article_id,))
        print("Article deleted.")

    conn.commit()

    # Close the connection after all operations
    conn.close()
    print("\nFinished testing CRUD operations and relationships.")

if __name__ == "__main__":
    main()
