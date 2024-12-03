import pytest

# Импортируем класс клиента.
from django.test.client import Client

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import Comment, News


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def anonim(django_user_model):
    return django_user_model.objects.create(username='Аноним')


@pytest.fixture
def anonim_client():
    # Создаём новый экземпляр клиента без аутентификации.
    return Client()


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news_fixture():
    news = News.objects.create(  # Создаём объект заметки.
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def comment(author):
    # Создаем объект news
    news_instance = News.objects.create(
        title='Test News',
        text='Текст заметки'
    )

    # Создаем объект comment, связанный с news_instance
    comment_instance = Comment.objects.create(
        text='Текст заметки',
        author=author,
        news=news_instance,
    )
    return comment_instance
