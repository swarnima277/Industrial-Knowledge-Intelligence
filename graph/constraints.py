from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "bhumika.1251090135"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

constraints = [

"""
CREATE CONSTRAINT equipment_id IF NOT EXISTS
FOR (e:Equipment)
REQUIRE e.id IS UNIQUE
""",

"""
CREATE CONSTRAINT engineer_id IF NOT EXISTS
FOR (e:Engineer)
REQUIRE e.id IS UNIQUE
""",

"""
CREATE CONSTRAINT issue_id IF NOT EXISTS
FOR (i:Issue)
REQUIRE i.id IS UNIQUE
""",

"""
CREATE CONSTRAINT manual_id IF NOT EXISTS
FOR (m:Manual)
REQUIRE m.id IS UNIQUE
"""

]

with driver.session() as session:

    for query in constraints:
        session.run(query)

print("Constraints Created Successfully")

driver.close()