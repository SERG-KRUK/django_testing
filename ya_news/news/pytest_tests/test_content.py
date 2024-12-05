import pytest
import http

from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


def test_news_limit_on_homepage(news_home_url, client, news_bulk):
    """Количество новостей на главной странице — не более 10."""
    assert (client.get(news_home_url).context['object_list'].count()
            == settings.NEWS_COUNT_ON_HOME_PAGE)


def test_news_order_on_homepage(news_home_url, client, news_bulk):
    """Новости на главной отсортированы по дате от новых к старым."""
    timestamps = [news.date for news in
                  client.get(news_home_url).context['object_list']]
    assert timestamps == sorted(timestamps, reverse=True)


def test_comments_order_on_news_page(client, comments_bulk, news_detail_url):
    """Комментарии к новости отсортированы по дате от старых к новым."""
    timestamps = [comment.created for comment in
                  client.get(
                      news_detail_url).context['news'].comment_set.all()]
    assert timestamps == sorted(timestamps)


# Анонимному пользователю недоступна форма для отправки
#  комментария на странице отдельной новости, а авторизованному доступна.
def test_comment_form_access_anonim(client, news_detail_url):
    assert 'form' not in client.get(news_detail_url).context


# а авторизованному доступна.
def test_comment_form_access_user(not_author_client, news, news_detail_url):
    response = not_author_client.get(news_detail_url)
    assert response.status_code == http.HTTPStatus.OK
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
