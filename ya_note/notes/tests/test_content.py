from notes.forms import NoteForm
from .urls_basetest import ADD_URL, EDIT_URL, LIST_URL, BaseTest


class TestNotes(BaseTest):
    """Тестирование передачи данных на страницы."""

    def test_note_is_in_list_context(self):
        """Передача заметки на страницу.

        Отдельная заметка передаётся на страницу со списком заметок
        в списке object_list в словаре context.
        """
        notes_list = self.client_author.get(LIST_URL).context['object_list']
        self.assertIn(self.note, notes_list)
        sent_note = notes_list.get(id=self.note.id)
        self.assertEqual(self.note.title, sent_note.title)
        self.assertEqual(self.note.text, sent_note.text)
        self.assertEqual(self.note.author, sent_note.author)
        self.assertEqual(self.note.slug, sent_note.slug)

    def test_forms_is_on_pages(self):
        """Передача форм на страницы создания и редактирования заметки."""
        urls = (ADD_URL, EDIT_URL)
        for url in urls:
            with self.subTest(url=url):
                context = self.client_author.get(url).context
                self.assertIn('form', context)
                self.assertIsInstance(context['form'], NoteForm)

    def test_no_alien_notes_in_users_notes(self):
        """В заметки одного пользователя не попадают заметки другого."""
        self.assertNotIn(
            self.note,
            self.client_reader.get(LIST_URL).context['object_list']
        )
