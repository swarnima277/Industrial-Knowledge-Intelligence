from neo4j import GraphDatabase

# Neo4j connection details
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "bhumika.1251090135"   # Replace with your Neo4j password


class Neo4jConnection:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            URI,
            auth=(USERNAME, PASSWORD)
        )

    def close(self):
        self.driver.close()

    def test_connection(self):
        with self.driver.session() as session:
            result = session.run(
                "RETURN 'Connection Successful!' AS message"
            )
            print(result.single()["message"])


if __name__ == "__main__":
    db = Neo4jConnection()
    db.test_connection()
    db.close()