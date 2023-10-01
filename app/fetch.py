from queries import QUERIES_FETCH
from app import controllers


def create_nodes_and_relationships():
    """Construct nodes and relationship of the Knowledge Graph."""
    # Creates all Article, Tag and Resort nodes using the Tagesschau API.
    controllers.query_knowledge_graph(QUERIES_FETCH["create_article_tag_ressort_nodes"])

    # Creates Entity nodes using the Wikifier.
    controllers.query_knowledge_graph(QUERIES_FETCH["create_entity_nodes"])

    # Classifies all entities in the Knowledge Graph.
    controllers.query_knowledge_graph(QUERIES_FETCH["classify_entities"])


if __name__ == "__main__":
    create_nodes_and_relationships()
