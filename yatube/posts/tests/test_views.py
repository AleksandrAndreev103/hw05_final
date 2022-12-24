from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from django import forms
from django.conf import settings

from posts.models import Post, Group, Follow, User


class StaticURLTests(TestCase):
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
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
        )

    def setUp(self):
        self.user = User.objects.create_user(username='AlexAndreev')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(self.post.author)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.post.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):

                response = self.another_authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def context_test_helper(self, object):
        return (
            self.assertEqual(object.id, self.post.id),
            self.assertEqual(object.text, self.post.text),
            self.assertEqual(object.group, self.post.group),
            self.assertEqual(object.author, self.post.author),
            self.assertEqual(object.image, self.post.image)
        )

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован c правильным контекстом."""
        response = self.client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.context_test_helper(first_object)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован c правильным контекстом."""
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        self.context_test_helper(first_object)
        self.assertEqual(
            response.context.get('group').title, self.post.group.title
        )
        self.assertEqual(
            response.context.get('group').slug, self.post.group.slug
        )
        self.assertEqual(
            response.context.get('group').description,
            self.post.group.description
        )

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован c правильным контекстом."""
        response = self.client.get(
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            )
        )
        first_object = response.context['page_obj'][0]
        self.context_test_helper(first_object)
        self.assertEqual(
            response.context.get('author').username, self.post.author.username
        )

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован c правильным контекстом."""
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        first_object = response.context['post']
        self.context_test_helper(first_object)

    def test_create_post_pages_show_correct_context(self):
        """Шаблон post_create сформирован c правильным контекстом."""
        response = self.another_authorized_client.get(
            reverse('posts:post_create')
        )
        self.assertIsInstance(
            response.context['form'], forms.ModelForm
        )

    def test_edit_post_page_show_correct_context(self):
        """Проверяет, что шаблон post_edit cодержит форму
        редактирования поста.
        """
        response = self.another_authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertIsInstance(
            response.context['form'], forms.ModelForm
        )
        test_value = True
        self.assertTrue(response.context['is_edit'], test_value)
        self.assertEqual(response.context['post_id'], self.post.id)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug-group',
            description='Тестовое описание',
        )
        cls.author = User.objects.create_user(username='AlexAndreev')
        cls.many_posts = []
        for _ in range(
            settings.POSTS_ON_FIRST_PAGE
            + settings.POSTS_ON_SECOND_PAGE
        ):
            cls.many_posts.append(Post(
                author=cls.author,
                group=cls.group,
                text='Тестовый пост',
            ))
        Post.objects.bulk_create(cls.many_posts)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        cache.clear()

    def test_first_page_contains_ten_records(self):
        """Paginator выводит 10 постов на первой странице"""
        templates_pages_names = {
            reverse('posts:index'): settings.POSTS_ON_FIRST_PAGE,
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): settings.POSTS_ON_FIRST_PAGE,
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            ): settings.POSTS_ON_FIRST_PAGE,
        }
        for reverse_name, posts_count in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), posts_count
                )

    def test_second_page_contains_three_records(self):
        """Paginator выводит 3 поста на второй странице"""
        templates_pages_names = {
            reverse('posts:index') + '?page=2':
            settings.POSTS_ON_SECOND_PAGE,
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug-group'}
            ) + '?page=2': settings.POSTS_ON_SECOND_PAGE,
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            ) + '?page=2': settings.POSTS_ON_SECOND_PAGE,
        }
        for reverse_name, posts_count in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), posts_count
                )


class PostOnPagesViewsTest(TestCase):
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
            author=cls.author,
            text='Тестовый пост',
            group=cls.group
        )

        cls.another_post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост без группы',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)

    def test_post_on_all_pages(self):
        """Пост находится на всех нужных страницах"""
        another_post_with_group = Post.objects.create(
            author=self.author,
            text='Второй тестовый пост с группой',
            group=self.group
        )
        post_on_pages = {
            reverse('posts:index'): another_post_with_group,
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): another_post_with_group,
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            ): another_post_with_group,
        }
        for reverse_name, post in post_on_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    post,
                    response.context['page_obj'][0]
                )

    def test_post_not_on_all_pages(self):
        """Пост не попадает в неправильную группу"""
        post_on_pages = {
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): self.another_post,
        }
        for reverse_name, another_post in post_on_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertNotIn(another_post, response.context['page_obj'])


class CacheViewsTest(TestCase):
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
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)
        cache.clear()

    def test_index_cache_work(self):
        """
        Главная страница кэшируется и пока кэщ не очищен,
        content остается.
        """
        self.assertTrue(
            Post.objects.filter(
                author=self.author,
                text=self.post.text,
                group=self.group,
            ).exists()
        )
        response_one = self.authorized_client.get(
            reverse('posts:index')
        )
        result_one = response_one.content
        self.post.delete()
        response_two = self.authorized_client.get(
            reverse('posts:index')
        )
        result_two = response_two.content
        self.assertEqual(result_one, result_two)
        cache.clear()
        response_three = self.authorized_client.get(
            reverse('posts:index')
        )
        result_three = response_three.content
        self.assertNotEqual(result_two, result_three)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='auth')
        cls.not_follower = User.objects.create_user(username='unfollow')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug-group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Пост для подписчиков',
            author=cls.author,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)
        self.unfollower = Client()
        self.unfollower.force_login(self.not_follower)
        cache.clear()

    def test_follow(self):
        """Авторизованный пользователь может подписываться на других пользователей
        """
        follow_response = self.authorized_user.post(
            reverse('posts:profile_follow', args=[self.post.author])
        )
        self.assertEqual(follow_response.status_code, 302)
        self.assertEqual(Follow.objects.count(), 1)
        self.assertEqual(Follow.objects.first().author, self.post.author)
        self.assertEqual(Follow.objects.first().user, self.user)

    def test_unfollow(self):
        """Авторизованный пользователь может удалять пользователей из подписок
        """
        Follow.objects.create(user=self.user, author=self.author)
        self.assertEqual(Follow.objects.count(), 1)
        unfollow_response = self.authorized_user.post(
            reverse('posts:profile_unfollow', args=[self.post.author])
        )
        self.assertEqual(unfollow_response.status_code, 302)
        self.assertEqual(Follow.objects.count(), 0)
        self.assertIsNone(Follow.objects.first())

    def test_post_on_followers_page(self):
        """Новый пост появляется на главной странице подписчиков
        """
        Follow.objects.create(user=self.user, author=self.author)
        response = self.authorized_user.get(
            reverse('posts:follow_index')
        )
        self.assertIn(self.post, response.context['page_obj'])

        not_follower_response = self.unfollower.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(
            self.post,
            not_follower_response.context['page_obj']
        )
