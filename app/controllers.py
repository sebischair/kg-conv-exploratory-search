# -*- coding: utf-8 -*-

import re
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from app import driver, logs_collection, state_collection
from .queries import QUERIES_SEARCH
from flask_dialogflow.conversation import V2beta1DialogflowConversation
from flask import render_template

from fuzzywuzzy import process


# define functions for conversation controllers
def get_random_response() -> str:
    """
    Return a random response from a hardcoded list of responses.

    Returns:
        str: A randomly selected response from the list.
    """

    responses_list = [
        "Ich verstehe deine Frage leider nicht.",
        "Entschuldige bitte, ich habe deine Frage nicht verstanden.",
        "Ich bin nicht so sicher, ob ich dich richtig verstanden habe.",
        "Kannst du das noch mal anders formulieren?"
    ]
    random_response = random.choice(responses_list)

    return random_response


def remove_html_tags(text):
    """
    Removes all HTML elements from the given text.

    Args:
        text (str): The text to remove HTML elements from.

    Returns:
        str: The text without HTML elements.
    """

    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def write_to_log_file(text, intent):
    """
    Writes the given text to a MongoDB Atlas collection.

    Args:
        text (str): The text to be written to MongoDB Atlas.
        intent (str): The matched intent to be written to MongoDB Atlas.
    """

    # Log a message
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    log_entry = {
        'timestamp': timestamp,
        'message': text,
        'intent': intent
    }

    # Insert the log entry into the MongoDB Atlas collection
    logs_collection.insert_one(log_entry)


def determine_most_similar_headline_index(headlines, utterance: str) -> int:
    """
        Returns the index of the headline in the provided list with the highest similarity to the utterance.

        Args:
            headlines (List[str]): A list of headlines to compare the utterance to.
            utterance (str): The user's input.

        Returns:
            int: The index of the most similar headline in the list.
        """

    closest_match = process.extractOne(utterance, headlines)
    matched_index = headlines.index(closest_match[0])

    if closest_match[1] < 20:
        return -1

    return matched_index


def construct_title_topline_response(query_results: List[Dict[str, Any]]) -> str:
    """
    Constructs the response part of the toplines and titles from the query results.

    Args:
        query_results (List[Dict[str, Any]]): A list of dictionaries containing the toplines and titles.

    Returns:
        str: The constructed response string.
    """

    response = ""
    prefixes = ["Erstens", "Zweitens", "Drittens"]

    for i, result in enumerate(query_results[:3]):
        response += "<s>" + prefixes[i] + "<break time=\"500ms\"/> " + result["topline"] + ", <break time=\"500ms\"/>" + \
                    result[
                        "title"] + "</s> <break time=\"1000ms\"/> "

    return response


def construct_similar_entites_response(article: Dict[str, Any]) -> str:
    """Returns a response with the three most important Entites related to the given article."""
    response = "<speak> <p><s>" + article["topline"] + ": " + article["title"] + ". </s></p><p>"
    response += remove_html_tags(article["text"])

    title = article["title"]
    results = query_knowledge_graph(QUERIES_SEARCH["entities_by_article"], {"title": title})

    entities_list = []
    for entity in results:
        entities_list.append(entity["name"])

    results = query_knowledge_graph(QUERIES_SEARCH["top_entities_from_article_by_relationships"],
                                    {"entities": entities_list})

    if len(results) == 0:
        response += "</p> <p><s>Für weitere Artikel, sagen Sie beispielsweise, ich möchte weitere Artikel haben.</s></p> </speak>"
    else:
        response += "</p> <break time=\"1000ms\"/> <p><s>Für weitere Artikel aus verwandten Themen, wie "
        titles = [element["title"] for element in results]
        response += ", ".join(titles[:-1]) + (f" oder {titles[-1]}" if len(titles) > 1 else "")

        response += " sage ich möchte Nachrichten über " + results.pop(0)["title"] + " haben.</s></p>"

        response += "Um zu einem anderen Artikel aus der Auswahl zu gelangen, sage Wiederholen, <break time=\"350ms\"/> Nächster <break time=\"350ms\"/> oder Zurück. </speak>"

    return response


def query_knowledge_graph(query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Returns result from querying the knowledge graph with given query and parameters."""
    session = driver.session()
    result = session.run(query, parameters).data()
    driver.close()

    return result


def find_most_similar_entity(entity: str) -> str:
    """
        Returns the most similar available entity from the Graph, according to the user-provided entity.

        Args:
            entity (str): The entity provided by the user.

        Returns:
            str: The most similar entity from the Graph.
        """
    entities = query_knowledge_graph(QUERIES_SEARCH["all_entities"])
    entities_list = [entry["title"] for entry in entities]
    closest_match = process.extractOne(entity, entities_list)

    return closest_match[0]


def log_and_ask(conv: V2beta1DialogflowConversation, template_name: str) -> V2beta1DialogflowConversation:
    """
    Logs the user's query, renders the template, logs the response, and asks the user.

    Args:
        conv (V2beta1DialogflowConversation): The current conversation object.
        template_name (str): The name of the template file to render.

    Returns:
        V2beta1DialogflowConversation: The updated conversation object after logging and asking the user.
    """
    write_to_log_file(conv.query_text, conv.intent)
    response = render_template(template_name)
    write_to_log_file(response, conv.intent)
    conv.ask(response)
    return conv


def get_state():
    state = state_collection.find_one()
    if not state:
        state = {
            "last_request_any": None,
            "last_request_ressort": None,
            "last_response": None,
            "last_selected_article": None,
        }
        state_collection.insert_one(state)
    return state


def update_state(last_request=None, last_response=None, last_selected_article=None):
    update = {}
    if last_request is not None:
        update["last_request_any"] = last_request.parameters.get("any") if last_request.parameters else None
        update["last_request_ressort"] = last_request.parameters.get("ressort") if last_request.parameters else None
    if last_response is not None:
        update["last_response"] = last_response
    if last_selected_article is not None:
        update["last_selected_article"] = last_selected_article

    state_collection.update_one({}, {"$set": update})


def update_state_ressort_entity(last_request_ressort=None, last_request_any=None):
    update = {}
    if last_request_ressort is not None:
        update["last_request_ressort"] = last_request_ressort
    if last_request_any is not None:
        update["last_request_any"] = last_request_any

    state_collection.update_one({}, {"$set": update})
