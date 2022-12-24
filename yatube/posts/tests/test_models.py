from django.test import TestCase

from django.conf import settings
from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост больше пятнадцати символов',
        )

    def test_models_have_correct_object_names_group(self):
        """Проверяем, что у моделей корректно работает __str__."""
        expected_object_name = self.group.title
        self.assertEqual(expected_object_name, str(self.group))

    def test_models_have_correct_object_names_text(self):
        """Проверяем, что у моделей корректно работает __str__."""
        expected_object_name = self.post.text[:settings.TEXT_LEN]
        self.assertEqual(expected_object_name, str(self.post))
