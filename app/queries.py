# -*- coding: utf-8 -*-

def collect_random_articles(num_articles):
    return f"""
    WITH a
    ORDER BY a.date DESC 
    WITH COLLECT(a)[0..{num_articles}] AS articles 
    WITH apoc.coll.shuffle(articles) AS shuffled_articles 
    WITH CASE 
        WHEN size(shuffled_articles) >= 3 THEN shuffled_articles[0..3]
        ELSE shuffled_articles 
        END AS random_articles 
    UNWIND random_articles AS random_article 
    RETURN random_article.topline AS topline, random_article.title AS title, random_article.text AS text
    """


QUERIES_SEARCH = {
    # Returns the most recent articles from the given categories
    "overview_articles": "MATCH (a:Article)-[:IS_PART_OF]->(r:Ressort) "
                         "WHERE r.name IN ['inland', 'ausland', 'wirtschaft'] "
                         "WITH r, a "
                         "ORDER BY r.name, a.date DESC "
                         "WITH r.name AS category, COLLECT(a)[0..5] AS recentArticles "
                         "WITH category, recentArticles, RAND() AS randomIndex "
                         "WITH category, recentArticles[toInteger(randomIndex * size(recentArticles))] AS randomArticle "
                         "RETURN category, randomArticle.topline AS topline, randomArticle.title AS title, randomArticle.text AS text",

    # Returns one random article from the ten most recent articles of the given categories
    "random_suggestion_articles_overview": "MATCH (a:Article)-[:IS_PART_OF]->(r:Ressort) "
                                           "WHERE r.name IN [\"inland\", \"ausland\", \"wirtschaft\"] "
                                           "WITH r, a "
                                           "ORDER BY r.name, a.date DESC "
                                           "WITH r, COLLECT(a)[0..9] AS articles "
                                           "RETURN r.name, articles[TOINTEGER(rand()*SIZE(articles))].topline AS topline, "
                                           "articles[TOINTEGER(rand()*SIZE(articles))].title AS title, "
                                           "articles[TOINTEGER(rand()*SIZE(articles))].text AS text ",

    # Returns three random articles from the given ressort
    "random_suggestion_articles_by_ressort": f"MATCH (a:Article)-[:IS_PART_OF]->(r:Ressort {{name: $ressort}})"
                                             f"{collect_random_articles(15)}",

    # Returns three random articles containing the given entity
    "random_suggestion_articles_by_entity": f"MATCH (a:Article)-[:HAS_ENTITY]->(e:Entity {{title: $entity}})"
                                            f"{collect_random_articles(15)}",

    # Returns a list of all ressorts
    "all_ressorts": "MATCH (r:Ressort) RETURN r.name as name",

    # Returns three random entities out of the most mentionned Entities in the last two days
    "top_recent_entities": """
                                MATCH (a:Article)-[:HAS_ENTITY]->(e:Entity)
                                WITH a, e, apoc.date.parse(a.date, 'ms', 'yyyy-MM-dd\\'T\\'HH:mm:ss.SSSXXX') AS timestamp
                                WHERE timestamp >= (datetime() - duration('P2DT0S')).epochMillis
                                WITH e, COUNT(a) AS articleCount
                                ORDER BY articleCount DESC
                                LIMIT 15
                                WITH COLLECT({entity: e, count: articleCount}) AS topEntities
                                WITH apoc.coll.shuffle(topEntities)[..2] AS randomEntities
                                UNWIND randomEntities AS randomEntity
                                RETURN randomEntity.entity.title as name
                            """,

    # Returns three random articles by the given ressort
    "top_articles_by_ressort": f"MATCH (a:Article)-[:IS_PART_OF]->(r:Ressort {{name: $ressort}})"
                               f"{collect_random_articles(10)}",

    # Returns three random articles containing the given entity
    "top_articles_by_entity": f"Match (a:Article)-[:HAS_ENTITY]->(e:Entity {{title: $entity}})"
                              f"{collect_random_articles(10)}",

    # Returns an article with the given title and its related entities
    "entities_by_article": "MATCH (a:Article {title: $title})-[:HAS_ENTITY]->(e:Entity) "
                           "RETURN e.title AS name ",

    # Returns the top 3 entities related to the given list of entities, ordered by the number of articles they appear in
    "top_entities_from_article_by_relationships": "MATCH (e:Entity) "
                                                  "WHERE e.title IN  $entities "
                                                  "MATCH (a:Article)-[:HAS_ENTITY]->(e) "
                                                  "WITH e, COUNT(DISTINCT a) AS num_articles "
                                                  "ORDER BY num_articles DESC "
                                                  "RETURN e.title AS title "
                                                  "LIMIT 3",

    # Returns a list of all entities
    "all_entities": "MATCH(e:Entity) return e.title as title"

}

QUERIES_FETCH = {
    "create_article_tag_ressort_nodes": "CALL apoc.periodic.iterate(' "
                                        "CALL apoc.load.json(\"https://www.tagesschau.de/api2/\") YIELD value "
                                        "UNWIND value.news AS n "
                                        "Return n ',' "
                                        "WITH n "
                                        "WHERE n.externalId IS NOT NULL AND n.ressort IS NOT NULL AND n.type = \"story\" "
                                        "UNWIND n.content AS c "
                                        "WITH c, n "
                                        "WHERE c.type = \"text\" OR c.type = \"headline\" "
                                        "WITH apoc.text.join(collect(c.value)[..3],\" \") AS text, n "
                                        "MERGE (article:Article {id: n.externalId}) ON CREATE SET article.date = n.date, "
                                        "article.title = n.title, article.topline = n.topline, article.text = text "
                                        "MERGE (ressort:Ressort {name:n.ressort}) "
                                        "FOREACH(t IN n.tags | MERGE (tag: Tag {name: t.tag}) "
                                        "MERGE (article)-[:TAGGED]->(tag))"
                                        "MERGE(article)-[:IS_PART_OF]->(ressort)', "
                                        "{batchSize:10}) ",

    "create_entity_nodes": "CALL apoc.periodic.iterate(' "
                           "MATCH (a:Article) "
                           "WHERE a.text IS NOT NULL AND NOT (a)-[:HAS_ENTITY]->(:Entity)"
                           "RETURN a "
                           "',' "
                           "WITH a, \"https://www.wikifier.org/annotate-article?\" + "
                           "\"text=\" + apoc.text.urlencode(a.text) + \"&\" + "
                           "\"lang=de&\" + "
                           "\"pageRankSqThreshold=0.80&\" + "
                           "\"applyPageRankSqThreshold=true&\" + "
                           "\"nTopDfValuesToIgnore=200&\" + "
                           "\"nWordsToIgnoreFromList=200&\" + "
                           "\"minLinkFrequency=100&\" + "
                           "\"maxMentionEntropy=10&\" + "
                           "\"wikiDataClasses=false&\" + "
                           "\"wikiDataClassIds=false&\" + "
                           "\"userKey=\" + $userKey as url "
                           "CALL apoc.load.json(url) YIELD value "
                           "UNWIND value.annotations as annotation "
                           "WITH annotation, a "
                           "WHERE annotation.wikiDataItemId IS NOT NULL "
                           "MERGE (e:Entity{wikiDataItemId:annotation.wikiDataItemId}) "
                           "ON CREATE SET e.title = annotation.title, e.url = annotation.url "
                           "MERGE (a)-[:HAS_ENTITY]->(e)', "
                           "{batchSize:2, params: {userKey:\"vkdzoiypxiswqudqrsdgvilfhbgead\"}})",

    "classify_entities": "MATCH (e:Entity) "
                         "WITH 'SELECT * "
                         "WHERE{ "
                         "?item rdfs:label ?name . "
                         "filter (?item = wd:' + e.wikiDataItemId + ') "
                         "filter (lang(?name) = \"de\" ) . "
                         "OPTIONAL{ "
                         "?item wdt:P31 [rdfs:label ?class] . "
                         "filter (lang(?class)=\"de\") "
                         "}}' AS sparql, e "
                         "CALL apoc.load.jsonParams( "
                         "\"https://query.wikidata.org/sparql?query=\" + "
                         "apoc.text.urlencode(sparql), "
                         "{Accept: \"application/sparql-results+json\"}, null) "
                         "YIELD value "
                         "UNWIND value['results']['bindings'] as row "
                         "FOREACH(ignoreme IN CASE WHEN row['class'] IS NOT NULL THEN[1] ELSE [] END | "
                         "MERGE(c: Class {name: row['class']['value']}) "
                         "MERGE(e) - [: INSTANCE_OF]->(c)); "
}
