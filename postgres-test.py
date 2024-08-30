import psycopg2

try:
    connection = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="Luri@Complainer",
        host="luri-db.postgres.database.azure.com",
        port="5432",
        sslmode="require"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"Connection successful with db version: {db_version}")
except Exception as e:
    print(f"Connection failed: {e}")
finally:
    if 'connection' in locals():
        connection.close()


# DB_HOST='luri-db.postgres.database.azure.com'
# DB_NAME='postgres'
# DB_USERNAME='postgres'
# DB_PASSWORD='Luri@Complainer'
# DB_PORT='5432'