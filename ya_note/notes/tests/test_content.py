from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.forms import NoteForm


User = get_user_model()


class NoteViewTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', password='password1')
        
        self.user2 = User.objects.create_user(
            username='user2', password='password2')
        
        self.note1 = Note.objects.create(
            author=self.user1, title='Note 1', text='Content for note 1')
        
        self.note2 = Note.objects.create(
            author=self.user1, title='Note 2', text='Content for note 2')
        
        self.note3 = Note.objects.create(
            author=self.user2, title='Note 3', text='Content for note 3')

    def test_note_list_view(self):
        """Проверка, что отдельная заметка передается в контексте."""
        self.client.login(username='user1', password='password1')
        response = self.client.get(reverse('notes:list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context)
        self.assertEqual(len(response.context['object_list']), 2)
        self.assertIn(self.note1, response.context['object_list'])
        self.assertIn(self.note2, response.context['object_list'])
        self.assertNotIn(self.note3, response.context['object_list'])

    def test_note_create_view(self):
        """Проверка, что на странице создания заметки передается форма."""
        self.client.login(username='user1', password='password1')
        response = self.client.get(reverse('notes:add'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_edit_view(self):
        """Проверка, что на странице редактирования заметки передается форма"""
        self.client.login(username='user1', password='password1')
        response = self.client.get(
            reverse('notes:edit', args=[self.note1.slug]))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_edit_view_other_user(self):
        """пользователь не может редактировать заметку другого пользователя."""
        self.client.login(username='user1', password='password1')
        response = self.client.get(
            reverse('notes:edit', args=[self.note3.slug]))
        
        self.assertEqual(response.status_code, 404)

