from neo4j import GraphDatabase


class GraphManager:

    def __init__(self):
        self.driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "bhumika.1251090135")
        )

    # ----------------------------
    # Create Equipment
    # ----------------------------
    def create_equipment(self, equipment_id, name, status):

        query = """
        MERGE (e:Equipment {id:$id})
        SET e.name=$name,
            e.status=$status
        """

        with self.driver.session() as session:
            session.run(
                query,
                id=equipment_id,
                name=name,
                status=status
            )

        print("Equipment Created")

    # ----------------------------
    # Create Engineer
    # ----------------------------
    def create_engineer(self, engineer_id, name):

        query = """
        MERGE (e:Engineer {id:$id})
        SET e.name=$name
        """

        with self.driver.session() as session:
            session.run(
                query,
                id=engineer_id,
                name=name
            )

        print("Engineer Created")

    # ----------------------------
    # Assign Engineer
    # ----------------------------
    def assign_engineer(self, equipment_id, engineer_id):

        query = """
        MATCH (eq:Equipment {id:$equipment_id})
        MATCH (en:Engineer {id:$engineer_id})
        MERGE (eq)-[:MAINTAINED_BY]->(en)
        """

        with self.driver.session() as session:
            session.run(
                query,
                equipment_id=equipment_id,
                engineer_id=engineer_id
            )

        print("Relationship Created")

    # ----------------------------
    # Search Equipment
    # ----------------------------
    def search_equipment(self, equipment_id):

        query = """
        MATCH (e:Equipment {id:$id})
        RETURN e.id AS id,
               e.name AS name,
               e.status AS status
        """

        with self.driver.session() as session:

            result = session.run(query, id=equipment_id)
            record = result.single()

            if record:
                print("Equipment ID:", record["id"])
                print("Equipment:", record["name"])
                print("Status:", record["status"])
            else:
                print("Equipment not found")

    # ----------------------------
    # Get Equipment Details
    # ----------------------------
    def get_equipment(self, equipment_id):

        query = """
        MATCH (e:Equipment {id:$id})
        OPTIONAL MATCH (e)-[:MAINTAINED_BY]->(en:Engineer)

        RETURN
            e.id AS id,
            e.name AS name,
            e.status AS status,
            en.name AS engineer
        """

        with self.driver.session() as session:

            result = session.run(query, id=equipment_id)
            record = result.single()

            if record:
                return {
                    "id": record["id"],
                    "name": record["name"],
                    "status": record["status"],
                    "engineer": record["engineer"]
                }

            return None

    # ----------------------------
    # Close Connection
    # ----------------------------
    def close(self):
        self.driver.close()