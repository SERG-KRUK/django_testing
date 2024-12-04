import http
import pytest

from django.contrib.auth.models import User
from django.urls import reverse

from news.models import Comment


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


# Анонимный пользователь не может отправить комментарий.
def test_anonymous_user_cannot_submit_comment(
        client, news_item, comment_data, responce_login_url):

    response = client.post(reverse(
        'news:detail', args=[news_item.pk]), data=comment_data)

    assert response.status_code == http.HTTPStatus.FOUND
    assert response.url == responce_login_url
    assert Comment.objects.count() == 0


# Авторизованный пользователь может отправить комментарий.
def test_authenticated_user_can_submit_comment(submit_comment, news_item,
                                               comment_data):
    response = submit_comment

    assert response.status_code == http.HTTPStatus.FOUND
    comment = Comment.objects.first()
    assert comment is not None
    assert comment.text == comment_data['text']
    assert comment.news == news_item
    assert comment.author.username == 'testuser'


BAD_WORDS = (
    'редиска',
    'негодяй',
)


def test_comment_with_bad_word_is_not_saved(client, news_item,
                                            comment_bad_data):

    User.objects.create_user(
        username='testuser', password='testpassword')

    client.login(username='testuser', password='testpassword')

    response = client.post(
        reverse('news:detail', args=[news_item.pk]), data=comment_bad_data)

    # Проверяем, что статус ответа не 302 (т.е. комментарий не был принят)
    assert response.status_code != http.HTTPStatus.FOUND

    # Проверяем, что комментарий не был создан
    assert Comment.objects.count() == 0


# Авторизованный пользователь может редактировать свои комментарии.
def test_authenticated_user_can_edit_own_comment(client, comment_edit,
                                                 comment_update_data):
    client.login(username='testuser', password='testpassword')

    response = client.post(reverse(
        'news:edit', args=[comment_edit.pk]), data=comment_update_data)

    assert response.status_code == http.HTTPStatus.FOUND

    updated_comment = Comment.objects.get(pk=comment_edit.pk)
    assert updated_comment.text == comment_update_data['text']


# Авторизованный пользователь может удалять свои комментарии.
def test_authenticated_user_can_delete_own_comment(client, comment_edit):

    client.login(username='testuser', password='testpassword')

    response = client.post(reverse('news:delete', args=[comment_edit.pk]))

    assert response.status_code == http.HTTPStatus.FOUND

    assert Comment.objects.count() == 0
