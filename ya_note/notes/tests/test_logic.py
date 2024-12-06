from pytils.translit import slugify

from notes.models import Note
from .urls_basetest import ADD_URL, DELETE_URL, EDIT_URL, SLUG, BaseTest


class TestNoteCRUD(BaseTest):
    """Тестирование работы с заметками."""

    def test_anonymous_user_cannot_create_note(self):
        """Аноним не может создавать заметки."""
        notes = set(Note.objects.all())
        self.client.post(ADD_URL, data=self.new_data)
        self.assertEqual(set(Note.objects.all()), notes)

    def test_user_can_create_note(self):
        """Пользователь может создавать заметки."""
        notes_before = set(Note.objects.all())
        self.client_author.post(ADD_URL, data=self.new_data)
        notes_diff = set(Note.objects.all()) - notes_before
        self.assertEqual(len(notes_diff), 1)
        new_note = notes_diff.pop()
        self.assertEqual(new_note.title, self.new_data['title'])
        self.assertEqual(new_note.text, self.new_data['text'])
        self.assertEqual(new_note.slug, self.new_data['slug'])
        self.assertEqual(new_note.author, self.author_user)

    def test_creation_with_same_slug(self):
        """Нельзя создать заметки с одинаковым слагом."""
        notes_before = set(Note.objects.all())
        self.new_data['slug'] = SLUG
        self.client_author.post(ADD_URL, data=self.new_data,)
        self.assertEqual(set(Note.objects.all()), notes_before)

    def test_slugify_slug_matching(self):
        """Сгенерированный слаг заметки идентичен полученному через slugify."""
        notes = set(Note.objects.all())
        del self.new_data['slug']
        self.client_author.post(ADD_URL, data=self.new_data)
        new_notes = (set(Note.objects.all()) - notes)
        self.assertEqual(len(new_notes), 1)
        new_note = new_notes.pop()
        self.assertEqual(new_note.title, self.new_data['title'])
        self.assertEqual(new_note.text, self.new_data['text'])
        self.assertEqual(new_note.slug, slugify(self.new_data['title']))
        self.assertEqual(new_note.author, self.author_user)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свою заметку."""
        self.client_author.post(EDIT_URL, data=self.new_data)
        modified_note = Note.objects.get(id=self.note.id)
        self.assertEqual(modified_note.title, self.new_data['title'])
        self.assertEqual(modified_note.text, self.new_data['text'])
        self.assertEqual(modified_note.slug, self.new_data['slug'])
        self.assertEqual(modified_note.author, self.note.author)

    def test_reader_cannot_edit_note(self):
        """Пользователь не может редактировать чужую заметку."""
        self.client_reader.post(EDIT_URL, data=self.new_data)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, updated_note.title)
        self.assertEqual(self.note.text, updated_note.text)
        self.assertEqual(self.note.slug, updated_note.slug)
        self.assertEqual(self.note.author, updated_note.author)

    def test_author_can_delete_note(self):
        """Пользователь может удалить свою заметку."""
        notes_count = Note.objects.all().count()
        self.client_author.delete(DELETE_URL)
        self.assertEqual(notes_count - Note.objects.all().count(), 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_user_cannot_delete_note(self):
        """Пользователь не может удалить чужую заметку."""
        notes = set(Note.objects.all())
        note = Note.objects.get(id=self.note.id)
        self.client_reader.delete(DELETE_URL)
        self.assertEqual(notes, set(Note.objects.all()))
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, updated_note.title)
        self.assertEqual(note.text, updated_note.text)
        self.assertEqual(note.slug, updated_note.slug)
        self.assertEqual(note.author, updated_note.author)