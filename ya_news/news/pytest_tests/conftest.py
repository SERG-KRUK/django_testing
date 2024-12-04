from datetime import timedelta

import pytest

from django.contrib.auth.models import User
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

NEWS_DETAIL_URL = 'news:detail'
NEWS_LIST_URL = 'news:list'
HOME_URL = 'news:home'
LOGIN_URL = 'users:login'
LOGOUT_URL = 'users:logout'
SIGNUP_URL = 'users:signup'
EDIT_URL = 'news:edit'
DELETE_URL = 'news:delete'


@pytest.fixture
def comment_bad_data():
    comment_data = {
        'text': 'Ты редиска!'
    }
    return comment_data


@pytest.fixture
def comment_update_data():
    comment_data = {
        'text': 'Это обновленный комментарий.'
    }
    return comment_data


@pytest.fixture
def submit_comment(authenticated_client, news_item, comment_data):
    response = authenticated_client.post(
        reverse('news:detail', args=[news_item.pk]), data=comment_data)
    return response


@pytest.fixture
def edit_redirect_url(login_url):
    return f'{login_url}?next={EDIT_URL}'


@pytest.fixture
def delete_redirect_url(login_url):
    return f'{login_url}?next={DELETE_URL}'


@pytest.fixture
def expected_login_url(login_url, url):
    return f'{login_url}?next={url}'


@pytest.fixture
def responce_login_url(login_url):
    return f'{login_url}?next=/news/1/'


@pytest.fixture
def delete_url():
    return reverse(DELETE_URL, kwargs={'pk': 1})


@pytest.fixture
def edit_url():
    return reverse(EDIT_URL, kwargs={'pk': 1})


@pytest.fixture
def news_detail_url():
    return reverse(NEWS_DETAIL_URL, kwargs={'pk': 1})


@pytest.fixture
def news_home_url():
    return reverse(HOME_URL)


@pytest.fixture
def news_list_url():
    return reverse(NEWS_LIST_URL)


@pytest.fixture
def signup_url():
    return reverse(LOGOUT_URL)


@pytest.fixture
def logout_url():
    return reverse(LOGOUT_URL)


@pytest.fixture
def login_url():
    return reverse(LOGIN_URL)


@pytest.fixture
def news_per_page():
    return 10


@pytest.fixture
def create_comments(db, author):
    news_item = News.objects.create(
        title='Sample News', text='Sample news content', date=timezone.now()
    )
    comments = [
        Comment(news=news_item, text=f'Comment {i}', author=author,
                created=timezone.now() - timedelta(days=i))
        for i in range(333)
    ]
    Comment.objects.bulk_create(comments)
    return news_item


@pytest.fixture
def test_news_order():
    fresh_news = News.objects.create(
        title='Fresh News', text='Fresh news content',
        date=timezone.now())

    older_news = News.objects.create(
        title='Older News', text='Older news content',
        date=timezone.now() - timedelta(days=1))

    oldest_news = News.objects.create(
        title='Oldest News', text='Oldest news content',
        date=timezone.now() - timedelta(days=2))
    return fresh_news, older_news, oldest_news


@pytest.fixture
def news_page_create():
    def _create_news_items(news_over_page):
        return [News.objects.create(title=f'News {i}',
                                    text='text') for i in range(
                                        news_over_page)]
    return _create_news_items


@pytest.fixture
def news_over_page():
    return 15


@pytest.fixture
def comment_edit(db, news_item):
    author = User.objects.create_user(
        username='testuser', password='testpassword')
    return Comment.objects.create(
        text="Это комментарий.", news=news_item, author=author)


@pytest.fixture
def authenticated_client(client):
    User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')
    return client


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news_fixture():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def news_item():
    news_item = News.objects.create(title="Test News", text="news.")
    return news_item


@pytest.fixture
def comment_data():
    comment_data = {'text': 'This is a test comment.'}
    return comment_data


@pytest.fixture
def comment(author, news_fixture):
    comment_instance = Comment.objects.create(
        text='Текст заметки',
        author=author,
        news=news_fixture
    )
    return comment_instance and news_fixture
