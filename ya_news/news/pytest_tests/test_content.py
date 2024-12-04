import http

import pytest

from news.forms import CommentForm
from news.models import Comment

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.mark.parametrize('url', [
    pytest.lazy_fixture('news_home_url'),
])
# Количество новостей на главной странице — не более 10.
def test_news_limit_on_homepage(client, url, news_per_page, news_page_create):
    news_page_create
    response = client.get(url)
    assert response.status_code == http.HTTPStatus.OK
    assert len(response.context['object_list']) <= news_per_page


@pytest.mark.parametrize('url', [
    pytest.lazy_fixture('news_home_url'),
])
def test_news_order_on_homepage(client, url, test_news_order):
    news_list = list(test_news_order)

    response = client.get(url)

    assert response.status_code == http.HTTPStatus.OK
    returned_news_list = response.context['object_list']

    assert len(returned_news_list) == len(news_list)

    for i in range(len(returned_news_list) - 1):
        assert returned_news_list[i].date >= returned_news_list[i + 1].date, \
            (f"News item {returned_news_list[i]} должен быть более свежим, "
             f"чем {returned_news_list[i + 1]}.")


@pytest.mark.parametrize('url', [
    pytest.lazy_fixture('news_detail_url'),
])
def test_comments_order_on_news_page(client, create_comments, url):
    news_item = create_comments

    response = client.get(url)

    assert response.status_code == http.HTTPStatus.OK

    comments_list = response.context['news'].comment_set.all()

    assert list(comments_list) == list(Comment.objects.filter(
        news=news_item).order_by('created'))


@pytest.mark.parametrize('url', [
    pytest.lazy_fixture('news_detail_url'),
])
# Анонимному пользователю недоступна форма для отправки
#  комментария на странице отдельной новости, а авторизованному доступна.
def test_comment_form_access_anonim(client, url):
    assert 'form' not in client.get(url).context


@pytest.mark.parametrize('url', [
    pytest.lazy_fixture('news_detail_url'),
])
# а авторизованному доступна.
def test_comment_form_access_user(not_author_client, news_fixture, url):
    response = not_author_client.get(url)
    assert response.status_code == http.HTTPStatus.OK
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
