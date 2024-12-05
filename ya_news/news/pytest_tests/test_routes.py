from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


# Урлы
DELETE_URL = lazy_fixture('delete_url')
EDIT_URL = lazy_fixture('edit_url')
DELETE_REDIRECT_URL = lazy_fixture('delete_redirect_url')
NEWS_DETAIL_URL = lazy_fixture('news_detail_url')
EDIT_REDIRECT_URL = lazy_fixture('edit_redirect_url')
HOME_URL = lazy_fixture('news_home_url')
LOGIN_URL = lazy_fixture('login_url')
LOGOUT_URL = lazy_fixture('logout_url')
SIGNUP_URL = lazy_fixture('signup_url')

# Клиенты
ANON_CLIENT = lazy_fixture('client')
AUTHOR_CLIENT = lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = lazy_fixture('not_author_client')


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, user_client, status',
    (
        (HOME_URL, ANON_CLIENT, HTTPStatus.OK),
        (LOGIN_URL, ANON_CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, ANON_CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, ANON_CLIENT, HTTPStatus.OK),
        (NEWS_DETAIL_URL, ANON_CLIENT, HTTPStatus.OK),
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (EDIT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (DELETE_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (EDIT_URL, ANON_CLIENT, HTTPStatus.FOUND),
        (DELETE_URL, ANON_CLIENT, HTTPStatus.FOUND),
    )
)
def test_pages_availability(user_client, url, status):
    """Тест доступности страниц."""
    assert user_client.get(url).status_code == status


@pytest.mark.parametrize(
    'url, expected_url',
    [
        [EDIT_URL, EDIT_REDIRECT_URL],
        [DELETE_URL, DELETE_REDIRECT_URL],
    ]
)
def test_edit_delete_pages_redirects(client, url, expected_url):
    """Страницы удаления, редактирования переадресовывают анонима."""
    assertRedirects(client.get(url), expected_url)
