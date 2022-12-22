import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from posts.forms import PostForm, CommentForm
from posts.models import Post, Group, Comment, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug-group',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group,
        )
        cls.another_group = Group.objects.create(
            title='Вторая тестовая группа',
            slug='test-slug-group_two',
            description='Второе тестовое описание',
        )
        cls.form = PostForm()
        cls.form = CommentForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_before = list(Post.objects.values_list('id', flat=True))
        form_data = {
            'text': 'Текст для создания поста',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        new_posts = Post.objects.exclude(id__in=posts_before)
        self.assertRedirects(
            response,
            reverse(
                'posts:profile', kwargs={
                    'username': f'{self.author.username}'
                }
            )
        )
        self.assertEqual(new_posts.count(), 1)
        self.assertEqual(form_data['text'], new_posts.get().text)
        self.assertEqual(form_data['group'], new_posts.get().group_id)
        self.assertEqual(self.post.author, new_posts.get().author)

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный Тестовый текст изменен',
            'group': self.another_group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text='Измененный Тестовый текст изменен',
            ).exists()
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        needed_post = Post.objects.get(id=self.post.id)
        self.assertEqual(
            needed_post.text, form_data['text']
        )
        self.assertEqual(
            needed_post.group_id, form_data['group']
        )
        self.assertEqual(
            needed_post.author, self.post.author
        )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug-group',
            description='Тестовое описание',
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_task(self):
        """Валидная форма создает запись в post с картинкой."""
        tasks_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст для создания поста',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_create'
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.author.username}'}
            )
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group_id=self.group.id,
                text='Текст для создания поста',
                image='posts/small.gif'
            ).exists()
        )


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
        )
        cls.form = PostForm()
        cls.form = CommentForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_add_comment_to_post(self):
        """Валидная форма создает комментарий к посту."""
        count_one = Comment.objects.filter(post_id=self.post.id).count()
        form_data = {
            'text': 'Комментарий создан',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            self.post.id, Comment.objects.get().post_id
        )
        self.assertEqual(
            count_one + 1,
            Comment.objects.filter(post_id=self.post.id).count()
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )

    def test_not_logged_no_comment(self):
        """Незарегестрированный пользователь не может оставить комментарий"""
        count_one = Comment.objects.filter(post_id=self.post.id).count()
        form_data = {
            'text': 'Несуществующий комментарий',
        }
        response = self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        # Не знаю, какой тест лучше подходит
        # Тест №1
        self.assertEqual(
            Comment.objects.values().count(),
            Comment.objects.none().count()
        )
        # Тест №2
        self.assertEqual(
            count_one,
            Comment.objects.filter(post_id=self.post.id).count()
        )
        self.assertFalse(
            Comment.objects.filter(
                text='Несуществующий комментарий',
            ).exists()
        )
        self.assertRedirects(
            response,
            reverse('users:login')
            + '?next='
            + reverse(
                'posts:add_comment', kwargs={'post_id': self.post.id})
        )
