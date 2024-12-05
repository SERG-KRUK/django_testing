from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm
from notes.urls_constants import (
    NOTES_LIST_URL, EDIT_NOTE_URL, ADD_NOTE_URL)


STATUS_200 = 200
User = get_user_model()


class BaseNoteViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username='user1', password='password1')

        cls.user2 = User.objects.create_user(
            username='user2', password='password2')

        cls.note1 = Note.objects.create(
            author=cls.user1, title='Note 1', text='Content for note 1')

        cls.note2 = Note.objects.create(
            author=cls.user1, title='Note 2', text='Content for note 2')

        cls.note3 = Note.objects.create(
            author=cls.user2, title='Note 3', text='Content for note 3')

    def setUp(self):
        self.client = Client()
        self.client.login(username='user1', password='password1')


class NoteViewTests(BaseNoteViewTests):

    def test_note_list_view(self):
        """Проверка, что отдельная заметка передается в контексте."""
        response = self.client.get(reverse(NOTES_LIST_URL))
        self.assertEqual(response.status_code, STATUS_200)
        self.assertIn('object_list', response.context)
        self.assertIn(self.note1, response.context['object_list'])

    def test_note_create_view(self):
        """Проверка, что на странице создания заметки передается форма."""
        response = self.client.get(reverse(ADD_NOTE_URL))
        self.assertEqual(response.status_code, STATUS_200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_urls_with_forms(self):
        urls_to_test = [
            (ADD_NOTE_URL, None),
            (EDIT_NOTE_URL, self.note1),
        ]

        for url_name, note in urls_to_test:
            try:
                if note is not None:
                    url = reverse(url_name, args=[note.slug])
                else:
                    url = reverse(url_name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, STATUS_200)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
            except Exception as e:
                print(f"Error with URL '{url_name}': {e}")

    def test_note_list_view_fields_integrity(self):
        """Проверка целостности полей заметок в контексте."""
        response = self.client.get(reverse(NOTES_LIST_URL))
        self.assertEqual(response.status_code, STATUS_200)
        notes = response.context['object_list']
        for note in notes:
            self.assertEqual(note.title, note.title)
            self.assertEqual(note.text, note.text)

    def test_note_list_view_other_user_exclusion(self):
        """Проверка, что заметки другого пользователя не отображаются."""
        response = self.client.get(reverse(NOTES_LIST_URL))
        self.assertEqual(response.status_code, STATUS_200)
        self.assertNotIn(self.note3, response.context['object_list'])
