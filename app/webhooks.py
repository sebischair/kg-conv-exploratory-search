# -*- coding: utf-8 -*-

from app import agent
from app import handlers
from flask_dialogflow.conversation import V2beta1DialogflowConversation


@agent.handle(intent="news.search")
def news_search_intent_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.news_search_intent(conv)


@agent.handle(intent="news.overview.search")
def news_overview_search_intent_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.news_overview_search_intent(conv)


@agent.handle(intent="news.suggest.search")
def news_suggest_search_intent_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.news_suggest_search_intent(conv)


@agent.handle(intent="news.category.list")
def news_category_list_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.news_category_list_intent(conv)


@agent.handle(intent="news.category.search")
def news_category_search_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.news_category_search_intent(conv)


@agent.handle(intent="news.entity.search")
def news_entity_search_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.news_entity_search_intent(conv)


@agent.handle(intent="news.select.article.by.number")
def news_select_article_by_number(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.news_select_article_by_number(conv)


@agent.handle(intent="news.select.article.by.keyword")
def news_select_article_by_keyword(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.news_select_article_by_keyword(conv)


@agent.handle(intent="control.next.article")
def control_next_article_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.control_next_article_intent(conv)


@agent.handle(intent="control.repeat.article")
def control_repeat_article_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.control_repeat_article_intent(conv)


@agent.handle(intent="control.previous.article")
def control_previous_article_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.control_previous_article_intent(conv)


@agent.handle(intent="control.stop")
def control_stop_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.control_stop_intent(conv)


@agent.handle(intent="help")
def help_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.help_intent(conv)


@agent.handle(intent="help.yes")
def help_yes_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.help_yes_intent(conv)


@agent.handle(intent="help.no")
def help_no_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.help_no_intent(conv)


@agent.handle(intent="default.welcome")
def default_welcome_intent_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.default_welcome_intent(conv)


@agent.handle(intent="default.fallback")
def default_fallback_intent_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.default_fallback_intent(conv)


@agent.handle(intent="news.entity.search - yes")
def news_entity_search_yes_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.yes_no_handler(conv)


@agent.handle(intent="news.entity.search - no")
def news_entity_search_no_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.yes_no_handler(conv)


@agent.handle(intent="news.overview.search - yes")
def news_overview_search_yes_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.yes_no_handler(conv)


@agent.handle(intent="news.overview.search - no")
def news_overview_search_no_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.yes_no_handler(conv)


@agent.handle(intent="news.category.search - yes")
def news_category_search_yes_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.yes_no_handler(conv)


@agent.handle(intent="news.category.search - no")
def news_category_search_no_handler(conv: V2beta1DialogflowConversation) -> V2beta1DialogflowConversation:
    return handlers.yes_no_handler(conv)
