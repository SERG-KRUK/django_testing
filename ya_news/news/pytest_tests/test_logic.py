import pytest
import http

from pytest_django.asserts import assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


COMMENT = {'text': 'Текст комментария', }
MODIFIED_COMMENT = {'text': 'Новый текст', }


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


# Анонимный пользователь не может отправить комментарий.
def test_anonymous_user_cannot_submit_comment(
        client, news_detail_url):

    comments = set(Comment.objects.all())
    response = client.post(news_detail_url, data=COMMENT)
    assert set(Comment.objects.all()) == comments
    assert response.status_code == http.HTTPStatus.FOUND
    assert Comment.objects.count() == 0


# Авторизованный пользователь может отправить комментарий.
def test_authenticated_user_can_submit_comment(author_client,
                                               news_detail_url, news, author):
    comments = set(Comment.objects.all())
    author_client.post(news_detail_url, data=COMMENT)
    new_comments = set(Comment.objects.all()) - comments

    assert Comment.objects.count() == 1
    assert len(new_comments) == 1
    new_comment = new_comments.pop()
    assert new_comment.news == news
    assert new_comment.author == author
    assert new_comment.text == COMMENT['text']


@pytest.mark.parametrize(
    'test_data',
    [{'text': f'Это {word} текст'} for word in BAD_WORDS]
)
# Форма не принимает комментарий с запрещёнными словами.
def test_form_refuses_bad_words(author_client, news_detail_url, test_data):
    comments = set(Comment.objects.all())
    assertFormError(
        author_client.post(news_detail_url, test_data),
        'form', 'text', errors=(WARNING))
    assert set(Comment.objects.all()) == comments
    assert Comment.objects.count() == 0


# Авторизованный пользователь может редактировать свои комментарии.
def test_authenticated_user_can_edit_own_comment(
        author_client, comment, edit_url):
    author_client.post(edit_url, data=MODIFIED_COMMENT)
    attempt_comment = Comment.objects.get(id=comment.id)

    assert comment.news == attempt_comment.news
    assert comment.author == attempt_comment.author
    assert attempt_comment.text == MODIFIED_COMMENT['text']


# Авторизованный пользователь может удалять свои комментарии.
def test_authenticated_user_can_delete_own_comment(
        author_client, comment, delete_url):
    comments_count = Comment.objects.all().count()
    author_client.delete(delete_url)
    assert comments_count - Comment.objects.all().count() == 1
    assert not Comment.objects.filter(id=comment.id).exists()
