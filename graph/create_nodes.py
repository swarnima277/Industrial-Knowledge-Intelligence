from neo4j import GraphDatabase

URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "bhumika.1251090135"

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

query = """
CREATE (e:Equipment {
    id: 'P101',
    name: 'Water Pump',
    status: 'Running'
})
"""

with driver.session() as session:
    session.run(query)

print("Equipment node created successfully!")

driver.close()