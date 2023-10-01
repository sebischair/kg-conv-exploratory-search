# -*- coding: utf-8 -*-

import random

from app import controllers
from flask_dialogflow.conversation import V2beta1DialogflowConversation
from .queries import QUERIES_SEARCH
from flask import render_template


# define sub handlers

def news_search_intent(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns response to user for news.search intent."""
    return controllers.log_and_ask(conv, "news_search")


def news_overview_search_intent(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns the most recent articles from domestic, foreign and economy each."""
    controllers.write_to_log_file(conv.query_text, conv.intent)
    results = controllers.query_knowledge_graph(QUERIES_SEARCH["overview_articles"])

    controllers.update_state(last_request=conv, last_response=results)

    response = render_template("news_overview_search_first")
    response += controllers.construct_title_topline_response(results)
    response += render_template("news_article_selection_nudging")

    controllers.write_to_log_file(response, conv.intent)
    conv.ask(response)

    return conv


def news_suggest_search_intent(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns one random of the ten most recent articles from domestic, foreign and economy each."""
    controllers.write_to_log_file(conv.query_text, conv.intent)

    state = controllers.get_state()
    last_request_any = state["last_request_any"]
    last_request_ressort = state["last_request_ressort"]

    results = controllers.query_knowledge_graph(QUERIES_SEARCH["random_suggestion_articles_overview"])
    controllers.update_state(last_request=conv, last_response=results)
    if last_request_ressort:
        results = controllers.query_knowledge_graph(QUERIES_SEARCH["random_suggestion_articles_by_ressort"],
                                                    {"ressort": last_request_ressort})
        controllers.update_state(last_request=conv, last_response=results)
        controllers.update_state_ressort_entity(last_request_ressort, None)
    elif last_request_any:
        entity = last_request_any[0]
        entity = controllers.find_most_similar_entity(entity)
        results = controllers.query_knowledge_graph(QUERIES_SEARCH["random_suggestion_articles_by_entity"],
                                                    {"entity": entity})
        controllers.update_state(last_request=conv, last_response=results)
        controllers.update_state_ressort_entity(None, last_request_any)

    response = render_template("news_suggestion_search_first")
    response += controllers.construct_title_topline_response(results)
    response += render_template("news_article_selection_nudging")

    controllers.write_to_log_file(response, conv.intent)
    conv.ask(response)

    return conv


def news_category_list_intent(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns a list of all available resorts in the knowledge graph."""
    controllers.write_to_log_file(conv.query_text, conv.intent)

    results = controllers.query_knowledge_graph(QUERIES_SEARCH["all_ressorts"])

    controllers.update_state(last_request=conv, last_response=results)

    response = render_template("news_ressort_list_first")
    resorts = [entry["name"] for entry in results]
    random_resorts = random.sample(resorts, 3)

    response += ", <break time=\"350ms\"/>".join(
        random_resorts[:-1]) + "<break time=\"200ms\"/> und <break time=\"200ms\"/>" + \
                random_resorts[-1]

    results = controllers.query_knowledge_graph(QUERIES_SEARCH["top_recent_entities"])
    entities = [entry["name"] for entry in results]

    response += "</s> <s>Außerdem habe ich Nachrichten aus den verschiedensten Themen, wie zum Beispiel <break time=\"350ms\"/> "
    response += ", <break time=\"350ms\"/>".join(
        entities[:-1]) + "<break time=\"200ms\"/> oder <break time=\"200ms\"/>" + \
                entities[-1]

    response += render_template("news_ressort_list_last", entity=entities[0])

    controllers.write_to_log_file(response, conv.intent)
    conv.ask(response)

    return conv


def news_category_search_intent(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns the three most recent articles by the given resort."""
    controllers.write_to_log_file(conv.query_text, conv.intent)

    ressort = conv.parameters["ressort"]
    results = controllers.query_knowledge_graph(QUERIES_SEARCH["top_articles_by_ressort"], {"ressort": ressort})

    controllers.update_state(last_request=conv, last_response=results)

    response = "<speak> <p><s>Ich habe folgende Artikel aus Kategorie " + ressort + " gefunden.</s></p> <break time=\"250ms\"/> <p>"
    response += controllers.construct_title_topline_response(results)
    response += render_template("news_article_selection_nudging")

    controllers.write_to_log_file(response, conv.intent)
    conv.ask(response)

    return conv


def news_entity_search_intent(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns the three most recent articles by the given entity."""
    controllers.write_to_log_file(conv.query_text, conv.intent)

    entity = conv.parameters["any"][0]
    entity = controllers.find_most_similar_entity(entity)
    results = controllers.query_knowledge_graph(QUERIES_SEARCH["top_articles_by_entity"], {"entity": entity})

    controllers.update_state(last_request=conv, last_response=results)

    if len(results) == 0:
        response = "Ich habe leider keine Artikel über " + entity + " gefunden."
        controllers.write_to_log_file(response, conv.intent)
        conv.ask(response)
    else:
        response = "<speak><p><s> Hier sind Artikel über " + entity + " </s></p>. <break time=\"250ms\"/> <p>"
        response += controllers.construct_title_topline_response(results)
        response += render_template("news_article_selection_nudging")

        controllers.write_to_log_file(response, conv.intent)
        conv.ask(response)

    return conv


def news_select_article_by_number(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns the topline, title and text and most related entities of the selected article."""
    controllers.write_to_log_file(conv.query_text, conv.intent)
    index = int(conv.parameters["number"][0]) - 1
    state = controllers.get_state()
    last_response = state["last_response"]

    if index >= len(last_response) or index < 0:
        response = "Bitte sage eine Zahl zwischen 1 und " + str(len(last_response))
        conv.ask(response)
        conv.contexts.set("select", 1)
        controllers.write_to_log_file(response, conv.intent)
    else:
        article = last_response[index]
        response = controllers.construct_similar_entites_response(article)
        conv.ask(response)
        controllers.write_to_log_file(response, conv.intent)
        controllers.update_state(None, None, index)

    return conv


def news_select_article_by_keyword(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns the topline, title and text and most related entities of the selected article."""
    entity = conv.parameters["any"].lower()
    state = controllers.get_state()
    last_response = state["last_response"]

    headlines = []
    for entry in last_response:
        headlines.append(entry["topline"] + ", " + entry["title"])

    index = controllers.determine_most_similar_headline_index(headlines, entity)
    if index == -1:
        conv.contexts.set("select", 1)
        return controllers.log_and_ask(conv, "selection_clarify")

    controllers.write_to_log_file(conv.query_text, conv.intent)

    controllers.update_state(None, None, index)

    article = last_response[index]

    response = controllers.construct_similar_entites_response(article)
    conv.ask(response)
    controllers.write_to_log_file(response, conv.intent)

    return conv


def control_next_article_intent(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns the next Article based on the last searched articles."""
    state = controllers.get_state()
    last_response = state["last_response"]
    last_selected_article = state["last_selected_article"]

    if last_selected_article + 1 >= len(last_response):
        return controllers.log_and_ask(conv, "selection_last")
    else:
        controllers.write_to_log_file(conv.query_text, conv.intent)
        article = last_response[last_selected_article + 1]
        response = controllers.construct_similar_entites_response(article)
        conv.ask(response)
        controllers.write_to_log_file(response, conv.intent)

        controllers.update_state(None, None, last_selected_article + 1)

    return conv


def control_repeat_article_intent(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns the already read Article based on the last searched articles."""
    controllers.write_to_log_file(conv.query_text, conv.intent)
    state = controllers.get_state()
    last_response = state["last_response"]
    last_selected_article = state["last_selected_article"]

    article = last_response[last_selected_article]
    response = controllers.construct_similar_entites_response(article)
    conv.ask(response)
    controllers.write_to_log_file(response, conv.intent)

    return conv


def control_previous_article_intent(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns the already read Article based on the last searched articles."""
    state = controllers.get_state()
    last_response = state["last_response"]
    last_selected_article = state["last_selected_article"]

    if last_selected_article - 1 < 0:
        return controllers.log_and_ask(conv, "selection_first")
    else:
        controllers.write_to_log_file(conv.query_text, conv.intent)
        article = last_response[last_selected_article - 1]
        response = controllers.construct_similar_entites_response(article)
        conv.ask(response)
        controllers.write_to_log_file(response, conv.intent)

        controllers.update_state(None, None, last_selected_article - 1)

    return conv


def control_stop_intent(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns the already read Article based on the last searched articles."""
    return controllers.log_and_ask(conv, "stop")


def help_intent(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns a help response to the user, including example utterances."""
    return controllers.log_and_ask(conv, "help")


# define sub handlers
def help_yes_intent(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns more help and example utterances to the user."""
    return controllers.log_and_ask(conv, "help_yes")


# define sub handlers
def help_no_intent(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns a reminder how to ask for help again."""
    return controllers.log_and_ask(conv, "help_no")


# define sub handlers
def default_welcome_intent(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns a greeting and short explanation."""
    return controllers.log_and_ask(conv, "welcome")


def default_fallback_intent(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns a response if the users utterance not matches any regular intent."""
    controllers.write_to_log_file(conv.query_text, conv.intent)

    if conv.contexts.has("select"):
        conv.contexts.set("select", 1)

    response = controllers.get_random_response()
    controllers.write_to_log_file(response, conv.intent)
    conv.ask(response)

    return conv


def yes_no_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    """Returns a response if the users says yes or no instead of choosing an article."""
    if conv.contexts.has("select"):
        conv.contexts.set("select", 1)

    return controllers.log_and_ask(conv, "yes_no")
