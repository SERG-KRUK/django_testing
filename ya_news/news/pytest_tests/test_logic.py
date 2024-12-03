import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from news.forms import CommentForm
from news.models import News, Comment
from news.forms import CommentForm


# Анонимный пользователь не может отправить комментарий.
@pytest.mark.django_db
def test_anonymous_user_cannot_submit_comment(client):
    news_item = News.objects.create(title="Test News", text="news.")

    comment_data = {
        'text': 'This is a test comment.'
    }

    response = client.post(reverse(
        'news:detail', args=[news_item.pk]), data=comment_data)

    assert response.status_code == 302
    assert response.url == '/auth/login/?next=/news/1/'
    assert Comment.objects.count() == 0


# Авторизованный пользователь может отправить комментарий.
@pytest.mark.django_db
def test_authenticated_user_can_submit_comment(client):
    user = User.objects.create_user(
        username='testuser', password='testpassword')

    client.login(username='testuser', password='testpassword')

    news_item = News.objects.create(
        title="Test News", text="This is a test news.")

    comment_data = {
        'text': 'This is a test comment.'
    }

    response = client.post(
        reverse('news:detail', args=[news_item.pk]), data=comment_data)

    assert response.status_code == 302

    assert Comment.objects.count() == 1
    assert Comment.objects.first().text == 'This is a test comment.'
    assert Comment.objects.first().news == news_item
    assert Comment.objects.first().author == user


BAD_WORDS = (
    'редиска',
    'негодяй',
)


# Если комментарий содержит запрещённые слова,
#  он не будет опубликован, а форма вернёт ошибку.
@pytest.mark.django_db
def test_comment_with_bad_word_is_not_saved(client):
    User.objects.create_user(
        username='testuser', password='testpassword')

    client.login(username='testuser', password='testpassword')

    news_item = News.objects.create(
        title="Test News", text="This is a test news.")

    comment_data = {
        'text': 'Ты редиска!'
    }

    response = client.post(
        reverse('news:detail', args=[news_item.pk]), data=comment_data)

    # Проверяем, что статус ответа не 302 (т.е. комментарий не был принят)
    assert response.status_code != 302

    # Проверяем, что комментарий не был создан
    assert Comment.objects.count() == 0


# Если комментарий содержит запрещённые слова,
#  он не будет опубликован, а форма вернёт ошибку.
@pytest.mark.django_db
def test_comment_without_bad_word_is_saved(client):

    user = User.objects.create_user(
        username='testuser', password='testpassword')

    client.login(username='testuser', password='testpassword')

    news_item = News.objects.create(title="Test News", text="This is a test news.")

    comment_data = {
        'text': 'Это хороший комментарий.'
    }

    response = client.post(reverse(
        'news:detail', args=[news_item.pk]), data=comment_data)

    assert response.status_code == 302

    assert Comment.objects.count() == 1
    assert Comment.objects.first().text == 'Это хороший комментарий.'
    assert Comment.objects.first().author == user

@pytest.mark.django_db
def test_comment_form_validation_with_bad_word():
    form_data = {'text': 'Ты негодяй!'}
    form = CommentForm(data=form_data)

    assert not form.is_valid()
    assert 'Не ругайтесь!' in form.errors['text']


# Авторизованный пользователь может редактировать свои комментарии.
@pytest.mark.django_db
def test_authenticated_user_can_edit_own_comment(client):

    author = User.objects.create_user(
        username='testuser', password='testpassword')

    client.login(username='testuser', password='testpassword')

    news_item = News.objects.create(
        title="Test News", text="This is a test news.")

    comment = Comment.objects.create(
        text="Это комментарий.", news=news_item, author=author)

    updated_comment_data = {
        'text': 'Это обновленный комментарий.'
    }

    response = client.post(reverse(
        'news:edit', args=[comment.pk]), data=updated_comment_data)

    assert response.status_code == 302

    comment.refresh_from_db()
    assert comment.text == 'Это обновленный комментарий.'


# Авторизованный пользователь может удалять свои комментарии.
@pytest.mark.django_db
def test_authenticated_user_can_delete_own_comment(client):

    author = User.objects.create_user(
        username='testuser', password='testpassword')

    client.login(username='testuser', password='testpassword')

    news_item = News.objects.create(
        title="Test News", text="This is a test news.")

    comment = Comment.objects.create(
        text="Это комментарий.", news=news_item, author=author)

    response = client.post(reverse('news:delete', args=[comment.pk]))

    assert response.status_code == 302

    assert Comment.objects.count() == 0
