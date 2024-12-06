from http import HTTPStatus

from .urls_basetest import (
    ADD_REDIRECT_URL, ADD_URL, DELETE_REDIRECT_URL, DELETE_URL,
    DETAIL_REDIRECT_URL, DETAIL_URL, EDIT_URL, EDIT_REDIRECT_URL, HOME_URL,
    LIST_REDIRECT_URL, LIST_URL, LOGIN_URL, LOGOUT_URL, SIGNUP_URL,
    SUCCESS_REDIRECT_URL, SUCCESS_URL, BaseTest
)


class TestRoutes(BaseTest):
    """Тестирование маршрутов."""

    def test_pages_availability(self):
        """Проверка доступности страниц.

        Главная страница, регистрация, вход и выход доступны анониму.
        Список заметок и страницы добавления доступны пользователю.
        Редактирование и удаление заметки доступно только её автору.
        """
        routes = [
            [HOME_URL, self.client, HTTPStatus.OK],
            [SIGNUP_URL, self.client, HTTPStatus.OK],
            [LOGIN_URL, self.client, HTTPStatus.OK],
            [LOGOUT_URL, self.client, HTTPStatus.OK],
            [LIST_URL, self.client_author, HTTPStatus.OK],
            [ADD_URL, self.client_author, HTTPStatus.OK],
            [SUCCESS_URL, self.client_author, HTTPStatus.OK],
            [DELETE_URL, self.client_author, HTTPStatus.OK],
            [EDIT_URL, self.client_author, HTTPStatus.OK],
            [DELETE_URL, self.client_reader, HTTPStatus.NOT_FOUND],
            [EDIT_URL, self.client_reader, HTTPStatus.NOT_FOUND],
            [EDIT_URL, self.client, HTTPStatus.FOUND],
            [EDIT_REDIRECT_URL, self.client, HTTPStatus.OK],
            [DELETE_URL, self.client, HTTPStatus.FOUND],
            [DELETE_REDIRECT_URL, self.client, HTTPStatus.OK],
            [LIST_URL, self.client, HTTPStatus.FOUND],
            [LIST_REDIRECT_URL, self.client, HTTPStatus.OK],
            [ADD_URL, self.client, HTTPStatus.FOUND],
            [ADD_REDIRECT_URL, self.client, HTTPStatus.OK],
            [SUCCESS_URL, self.client, HTTPStatus.FOUND],
            [SUCCESS_REDIRECT_URL, self.client, HTTPStatus.OK],
            [DETAIL_URL, self.client, HTTPStatus.FOUND],
            [DETAIL_REDIRECT_URL, self.client, HTTPStatus.OK],

        ]
        for url, client, status in routes:
            with self.subTest(url=url, client=client, status=status):
                self.assertEqual(client.get(url).status_code, status)

    def test_redirect_for_anon(self):
        """Перенаправления для анонимного пользователя."""
        routes = [
            [EDIT_URL, EDIT_REDIRECT_URL],
            [DELETE_URL, DELETE_REDIRECT_URL],
            [LIST_URL, LIST_REDIRECT_URL],
            [ADD_URL, ADD_REDIRECT_URL],
            [SUCCESS_URL, SUCCESS_REDIRECT_URL],
            [DETAIL_URL, DETAIL_REDIRECT_URL],
        ]
        for url, redir_url in routes:
            with self.subTest(url=url, redir_url=redir_url):
                self.assertRedirects(self.client.get(url), redir_url)
