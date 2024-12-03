import pytest
from django.utils import timezone
from datetime import timedelta

from django.urls import reverse
from news.forms import CommentForm
from news.models import News, Comment


# Количество новостей на главной странице — не более 10.
@pytest.mark.django_db
def test_news_limit_on_homepage(client):
    for i in range(15):
        News.objects.create(title=f'News {i}', text='text')

    response = client.get(reverse('news:home'))
    assert response.status_code == 200
    assert len(response.context['object_list']) <= 10


# Новости отсортированы от самой свежей к самой старой.
#  Свежие новости в начале списка.
@pytest.mark.django_db
def test_news_order_on_homepage(client):
    fresh_news = News.objects.create(
        title='Fresh News', text='Fresh news content',
        date=timezone.now())

    older_news = News.objects.create(
        title='Older News', text='Older news content',
        date=timezone.now() - timedelta(days=1))

    oldest_news = News.objects.create(
        title='Oldest News', text='Oldest news content',
        date=timezone.now() - timedelta(days=2))

    response = client.get(reverse('news:home'))

    assert response.status_code == 200
    news_list = response.context['object_list']
    assert list(news_list) == [fresh_news, older_news, oldest_news]


# Комментарии на странице отдельной новости отсортированы
#  в хронологическом порядке: старые в начале списка, новые — в конце.
@pytest.mark.django_db
def test_comments_order_on_news_page(client, author):
    news_item = News.objects.create(
        title='Sample News', text='Sample news content', date=timezone.now())

    first_comment = Comment.objects.create(
        news=news_item, text='First comment',
        author=author, created=timezone.now() - timedelta(days=2))

    second_comment = Comment.objects.create(
        news=news_item, text='Second comment',
        author=author, created=timezone.now() - timedelta(days=1))

    third_comment = Comment.objects.create(
        news=news_item, text='Third comment',
        author=author, created=timezone.now())

    response = client.get(reverse('news:detail', args=[news_item.id]))

    assert response.status_code == 200

    comments_list = response.context['news'].comment_set.all()

    assert list(comments_list) == [
        first_comment, second_comment, third_comment]


# Анонимному пользователю недоступна форма для отправки
#  комментария на странице отдельной новости, а авторизованному доступна.
def test_comment_form_access_anonim(client):
    assert 'form' not in client.get('news:detail').context


# а авторизованному доступна.
@pytest.mark.django_db
def test_comment_form_access_user(not_author_client, news_fixture):
    response = not_author_client.get(reverse(
        'news:detail', args=[news_fixture.id]))
    assert response.status_code == 200
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
