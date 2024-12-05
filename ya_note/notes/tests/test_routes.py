from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.urls_constants import (
    HOME_URL, USER_LOGOUT, USER_LOGIN, DETAIL_NOTE_URL, DELETE_NOTE_URL,
    SUCCESS_URL, USER_SIGNUP, NOTES_LIST_URL, EDIT_NOTE_URL, ADD_NOTE_URL)


User = get_user_model()


class BaseTestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.notes = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.anonymous_client = Client()
        cls.users_statuses = (
            (cls.reader, HTTPStatus.OK),
        )
        cls.test_cases = [
            (reverse(EDIT_NOTE_URL, args=[cls.notes.slug]),
             cls.author_client, HTTPStatus.OK),
            (reverse(EDIT_NOTE_URL, args=[cls.notes.slug]),
             cls.reader_client, HTTPStatus.NOT_FOUND),
            (reverse(DELETE_NOTE_URL, args=[cls.notes.slug]),
             cls.author_client, HTTPStatus.OK),
            (reverse(DELETE_NOTE_URL, args=[cls.notes.slug]),
             cls.reader_client, HTTPStatus.NOT_FOUND),
            (reverse(DETAIL_NOTE_URL, args=[cls.notes.slug]),
             cls.author_client, HTTPStatus.OK),
            (reverse(DETAIL_NOTE_URL, args=[cls.notes.slug]),
             cls.reader_client, HTTPStatus.NOT_FOUND),
        ]


class TestRoutes(BaseTestRoutes):
    def setUp(self):
        super().setUp()
        self.login_url = reverse(USER_LOGIN)
        args_short = (self.notes.slug,)
        self.urls_with_args = {
            name: f'{self.login_url}?next={reverse(name, args=args_short )}'
            for name in (EDIT_NOTE_URL, DELETE_NOTE_URL, DETAIL_NOTE_URL)
        }
        self.urls_without_args = {
            name: f'{self.login_url}?next={reverse(name)}'
            for name in (NOTES_LIST_URL, SUCCESS_URL, ADD_NOTE_URL)
        }

    def test_pages_availability(self):
        """Проверка доступности страниц всем пользователям."""
        urls = (
            (HOME_URL, None),
            (USER_LOGIN, None),
            (USER_LOGOUT, None),
            (USER_SIGNUP, None),
        )
        url_map = {name: reverse(name, args=args) for name, args in urls}

        for name, args in urls:
            with self.subTest(name=name):
                url = url_map[name]
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_detail_delete(self):
        """Проверка доступности страниц заметки."""
        for url, client, expected_status in self.__class__.test_cases:
            with self.subTest(url=url, client=client,
                              expected_status=expected_status):
                response = client.get(url)
                self.assertEqual(
                    response.status_code, expected_status,
                    f"Incorrect status for URL: {url}, client: {client}")

    def test_redirect_for_anonymous_client(self):
        """Проверка редиректа анонимного пользователя."""
        for name, redirect_url in self.urls_with_args.items():
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=(
                    self.notes.slug,)))
                self.assertRedirects(response, redirect_url)

        for name, redirect_url in self.urls_without_args.items():
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertRedirects(response, redirect_url)

    def test_availability_for_list_add_success(self):
        """Аутентифиц. пользователю доступна страница list,success,add."""
        for user, status in self.__class__.users_statuses:
            with self.subTest(user=user):
                self.client.force_login(user)
                for name in (NOTES_LIST_URL, SUCCESS_URL, ADD_NOTE_URL):
                    with self.subTest(name=name):
                        url = reverse(name)
                        response = self.client.get(url)
                        self.assertEqual(response.status_code, status)
