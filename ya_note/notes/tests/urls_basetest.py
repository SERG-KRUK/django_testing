from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

SLUG = 'zametka'
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
EDIT_URL = reverse('notes:edit', args=(SLUG,))
DELETE_URL = reverse('notes:delete', args=(SLUG,))
HOME_URL = reverse('notes:home')
SIGNUP_URL = reverse('users:signup')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SUCCESS_URL = reverse('notes:success', args=None)
DETAIL_URL = reverse('notes:detail', args=(SLUG,))
EDIT_REDIRECT_URL = f'{LOGIN_URL}?next={EDIT_URL}'
DELETE_REDIRECT_URL = f'{LOGIN_URL}?next={DELETE_URL}'
LIST_REDIRECT_URL = f'{LOGIN_URL}?next={LIST_URL}'
SUCCESS_REDIRECT_URL = f'{LOGIN_URL}?next={SUCCESS_URL}'
DETAIL_REDIRECT_URL = f'{LOGIN_URL}?next={DETAIL_URL}'
ADD_REDIRECT_URL = f'{LOGIN_URL}?next={ADD_URL}'

User = get_user_model()


class BaseTest(TestCase):
    """Базовый класс тестов."""

    @classmethod
    def setUpTestData(cls):
        cls.author_user = User.objects.create(username='Писатель')
        cls.client_author = Client()
        cls.client_author.force_login(cls.author_user)
        cls.note = Note.objects.create(title='Заголовок заметки', text='Текст',
                                       author=cls.author_user, slug=SLUG)
        cls.reader_user = User.objects.create(username='Читатель')
        cls.client_reader = Client()
        cls.client_reader.force_login(cls.reader_user)
        cls.readers_note = Note.objects.create(title='Заметка Читателя',
                                               text='Текст',
                                               author=cls.reader_user)

        cls.new_data = {'title': 'Новый заг',
                        'text': 'Новый текст',
                        'slug': 'new_slug', }