from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

@pytest.mark.parametrize('url', [
    pytest.lazy_fixture('news_home_url'),
])
# Главная страница доступна анонимному пользователю.
def test_home_availability_for_anonymous_user(client, url):
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url', [
    pytest.lazy_fixture('news_home_url'),
    pytest.lazy_fixture('signup_url'),
    pytest.lazy_fixture('login_url'),
    pytest.lazy_fixture('logout_url'),
])
# Главная страница доступна анонимному пользователю
# Страницы регистрации пользователей, входа в учётную запись и выхода из неё
#  доступны анонимным пользователям.
def test_pages_availability_for_anonymous_user(client, url):
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url', [
    pytest.lazy_fixture('news_detail_url'),
])
# Страница отдельной новости доступна анонимному пользователю.
def test_detail_pages_availability_for_anonymous_user(client, url,
                                                      news_fixture):
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
# При попытке перейти на страницу редактирования или удаления комментария.
# анонимный пользователь перенаправляется на страницу авторизации.
def test_comment_pages_disable_for_anonymous_user(client, name, comment):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
# Авторизованный пользователь не может зайти на страницы редактирования или
#  удаления чужих комментариев возвращается 404.
# Страницы удаления и редактирования комментария доступны автору комментария.
def test_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status
