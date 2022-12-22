from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, Group, User


class StaticPagesURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug-group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )

    def setUp(self):
        self.user = User.objects.create_user(username='AlexAndreev')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(self.post.author)
        cache.clear()

    def test_homepage(self):
        """Страница / доступна любому пользователю."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_testslug_url_exists_at_desired_location(self):
        """Страница group/test-slug/ доступна любому пользователю."""
        response = self.client.get('/group/test-slug-group/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url_exists_at_desired_location(self):
        """Страница profile/username/ доступна любому пользователю."""
        response = self.client.get(f'/profile/{self.post.author}/')
        self.assertEqual(response.status_code, 200)

    def test_posts_postid_url_exists_at_desired_location(self):
        """Страница posts/test-slug/ доступна любому пользователю."""
        response = self.client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_posts_edit_url_exists_at_desired_location(self):
        """Страница posts/test-slug/edit/ доступна только автору."""
        response = self.another_authorized_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, 200)

    def test_posts_edit_url_redirects_anonymous(self):
        """Страница posts/test-slug/edit/ перенаправляет
         анонимного пользователя.
         """
        guest_response = self.client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(guest_response.status_code, 302)

    def test_posts_edit_url_redirect_anonymous_on_login(self):
        """Страница по адресу posts/test-slug/edit/ перенаправит
        анонимного пользователя на страницу login.
        """
        response = self.client.get(
            f'/posts/{self.post.id}/edit/', follow=True
        )
        self.assertRedirects(
            response, reverse('users:login')
            + '?next='
            + reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            )
        )

    def test_posts_edit_url_redirect_not_author_on_post_detail(self):
        """Страница по адресу posts/test-slug/edit/ перенаправит
        не автора на страницу post_detail.
        """
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/', follow=True
        )
        self.assertRedirects(
            response, f'/posts/{self.post.id}/'
        )

    def test_posts_create_url_exists_at_desired_location(self):
        """Страница create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_posts_create_url_redirects_anonymous(self):
        """Страница create/ перенаправляет
        анонимного пользователя."""
        guest_response = self.client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(guest_response.status_code, 302)

    def test_posts_create_url_redirect_anonymous_on_login(self):
        """Страница по адресу create/ перенаправит
        анонимного пользователя на страницу login.
        """
        response = self.client.get(
            '/create/', follow=True
        )
        self.assertRedirects(
            response, reverse('users:login')
            + '?next='
            + reverse(
                'posts:post_create')
        )

    def test_unexisting_page_url_not_exists_at_desired_location(self):
        """Страница unexisting_page недоступна любому пользователю."""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.another_authorized_client.get(address)
                self.assertTemplateUsed(response, template)
