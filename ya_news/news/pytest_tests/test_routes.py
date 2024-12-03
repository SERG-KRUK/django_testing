from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


# Главная страница доступна анонимному пользователю.
@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


# 
@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
# Главная страница доступна анонимному пользователю
# Страницы регистрации пользователей, входа в учётную запись и выхода из неё
#  доступны анонимным пользователям.
@pytest.mark.django_db 
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:detail',)
)
# Страница отдельной новости доступна анонимному пользователю.
@pytest.mark.django_db
def test_detail_pages_availability_for_anonymous_user(client, name,
                                                      news_fixture):
    url = reverse(name, args=(news_fixture.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
# При попытке перейти на страницу редактирования или удаления комментария.
# анонимный пользователь перенаправляется на страницу авторизации.
@pytest.mark.django_db
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
