from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.models import Note
from notes.urls_constants import (
    DELETE_NOTE_URL, SUCCESS_URL, EDIT_NOTE_URL, ADD_NOTE_URL)


User = get_user_model()


class BaseNoteTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username='testuser1', password='testpassword1')
        cls.user2 = User.objects.create_user(
            username='testuser2', password='testpassword2')

        cls.auth_client1 = Client()
        cls.auth_client1.force_login(cls.user1)

        cls.auth_client2 = Client()
        cls.auth_client2.force_login(cls.user2)

        cls.add_url = reverse(ADD_NOTE_URL)
        cls.success_url = reverse(SUCCESS_URL)


class TestNoteCreation(BaseNoteTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.existing_note_slug = "existing-note"

        cls.edit_other_form_data = {
            'title': 'Попытка изменить заголовок',
            'text': 'Попытка изменить текст',
            'slug': cls.existing_note_slug
        }

        cls.existing_note = Note.objects.create(
            title='заметка',
            text='Текст заметки',
            slug=cls.existing_note_slug,
            author=cls.user1
        )

        cls.new_note_slug = "note-to-delete"
        cls.new_note = Note.objects.create(
            title='Заметка для удаления',
            text='Текст заметки для удаления',
            slug=cls.new_note_slug,
            author=cls.user1
        )
        cls.delete_url = reverse(DELETE_NOTE_URL, args=[cls.new_note_slug])

        cls.edit_form_data = {
            'title': 'izmenennyij-zagolovok',
            'text': 'Измененный текст',
            'slug': cls.existing_note_slug
        }
        cls.edit_url = reverse(EDIT_NOTE_URL, args=[cls.existing_note_slug])

        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст заметки',
            'slug': slugify('Заголовок')
        }

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        initial_note_count = Note.objects.count()
        response = self.auth_client1.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)

        note_count = Note.objects.count()
        self.assertEqual(note_count, initial_note_count + 1)

        new_note = Note.objects.order_by('-id').first()
        self.assertEqual(new_note.title, 'Заголовок')
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.user1)

        self.assertEqual(new_note.slug, slugify(self.form_data['title']))

    def test_user_can_edit_own_note(self):
        """Автор может редактировать свою заметку."""
        response = self.auth_client1.post(self.edit_url, self.edit_form_data)
        self.assertRedirects(response, self.success_url, status_code=302)

        updated_note = Note.objects.get(slug=self.existing_note_slug)

        self.assertEqual(updated_note.title, self.edit_form_data['title'])
        self.assertEqual(updated_note.text, self.edit_form_data['text'])
        self.assertEqual(updated_note.author, self.user1)

    def test_user_can_delete_own_note(self):
        """Автор может удалить свою заметку."""
        response = self.auth_client1.post(self.delete_url)
        self.assertRedirects(response, self.success_url, status_code=302)
        self.assertFalse(Note.objects.filter(id=self.new_note.id).exists())

    def test_user_cannot_delete_other_note(self):
        """Пользователь не может удалять чужую заметку."""
        delete_url = reverse(DELETE_NOTE_URL, args=[self.existing_note_slug])
        response = self.auth_client2.post(delete_url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Note.objects.filter(
            slug=self.existing_note_slug).exists())

    def test_user_cannot_edit_other_note(self):
        """Пользователь не может редактировать чужую заметку."""
        response = self.auth_client2.post(self.edit_url,
                                          self.edit_other_form_data)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Note.objects.filter(
            slug=self.existing_note_slug).exists())
