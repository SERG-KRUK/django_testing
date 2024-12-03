from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import NoteForm
from notes.models import Note
from pytils.translit import slugify


User  = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Заголовок'
    COMMENT_TEXT = 'Текст заметки'
    EDITED_TITLE = 'Измененный заголовок'
    EDITED_TEXT = 'Измененный текст'

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='testuser1', password='testpassword1')
        cls.user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        
        cls.auth_client1 = Client()
        cls.auth_client1.force_login(cls.user1)
        
        cls.auth_client2 = Client()
        cls.auth_client2.force_login(cls.user2)

        cls.url = reverse('notes:add')
        
        cls.existing_note = Note.objects.create(
            title='заметка',
            text='Текст заметки',
            slug=slugify('Существующая заметка'),
            author=cls.user1
        )

        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.COMMENT_TEXT,
        }

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        response = self.auth_client1.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))

        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)

        note = Note.objects.get(title=self.NOTE_TITLE)
        self.assertEqual(note.text, self.COMMENT_TEXT)
        self.assertEqual(note.author, self.user1)

        expected_slug = slugify(self.NOTE_TITLE)
        self.assertEqual(note.slug, expected_slug)

    def test_user_can_edit_own_note(self):
        """Автор может редактировать свою заметку."""
        edit_url = reverse('notes:edit', args=[self.existing_note.slug])
        response = self.auth_client1.post(edit_url, {
            'title': self.EDITED_TITLE,
            'text': self.EDITED_TEXT,
        })
        self.assertRedirects(response, reverse('notes:success'))

        self.existing_note.refresh_from_db()
        self.assertEqual(self.existing_note.title, self.EDITED_TITLE)
        self.assertEqual(self.existing_note.text, self.EDITED_TEXT)

    def test_user_can_delete_own_note(self):
        """Автор может удалить свою заметку."""
        new_note = Note.objects.create(
            title='Заметка для удаления',
            text='Текст заметки для удаления',
            slug=slugify('Заметка для удаления'),
            author=self.user1
        )
        delete_url = reverse('notes:delete', args=[new_note.slug])
        response = self.auth_client1.post(delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertFalse(Note.objects.filter(id=new_note.id).exists())

    def test_user_cannot_delete_other_note(self):
        """Пользователь не может удалять чужую заметку."""
        delete_url = reverse('notes:delete', args=[self.existing_note.slug])
        response = self.auth_client2.post(delete_url)
        print(response.content)
        self.assertEqual(response.status_code, 404)

    def test_user_cannot_edit_other_note(self):
        """Пользователь не может редактировать чужую заметку."""
        edit_url = reverse('notes:edit', args=[self.existing_note.slug])
        response = self.auth_client2.post(edit_url, {
            'title': 'Попытка изменить заголовок',
            'text': 'Попытка изменить текст',
        })
        self.assertEqual(response.status_code, 404)
