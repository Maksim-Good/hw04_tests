from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author1 = User.objects.create_user(username='Test_name_author1')
        cls.author2 = User.objects.create_user(username='Test_name_author2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        for i in range(13):
            Post.objects.create(
                author=cls.author1,
                text='Тестовый пост',
                group=cls.group
            )
            Post.objects.create(
                author=cls.author2,
                text='Тестовый пост2'
            )

    def setUp(self):
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(self.author1)

    def test_pages_uses_correct_template_for_author(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'test_slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'Test_name_author1'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': 1}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': 1}
            ): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:index') + '?page=3')
        self.assertEqual(len(response.context['page_obj']), 6)

    def test_group_posts_show_correct_context(self):
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)
        for post in range(10):
            group_title = response.context.get('page_obj')[post].group.title
            self.assertEqual(group_title, 'Тестовая группа')
        response = self.client.get(
            reverse(
                'posts:group_list', kwargs={'slug': 'test_slug'}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
        for post in range(3):
            group_title = response.context.get('page_obj')[post].group.title
            self.assertEqual(group_title, 'Тестовая группа')

    def test_profile_posts_show_correct_context(self):
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.author1})
        )
        self.assertEqual(len(response.context['page_obj']), 10)
        for post in range(10):
            author = response.context.get('page_obj')[post].author.username
            self.assertEqual(author, 'Test_name_author1')
        response = self.client.get(
            reverse(
                'posts:profile', kwargs={'username': self.author1}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
        for post in range(3):
            author = response.context.get('page_obj')[post].author.username
            self.assertEqual(author, 'Test_name_author1')

    def test_detail_page_show_correct_context(self):
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        post_number = response.context.get('post').id
        self.assertEqual(post_number, 1)

    def test_post_create_page_show_correct_context(self):
        response = self.authorized_author_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        response = self.authorized_author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        form_fields_received = {
            'text': 'Тестовый пост',
            'group': self.group.id,
        }
        for value, expected in form_fields_received.items():
            with self.subTest(value=value):
                form_field = response.context.get('form')[value].initial
                self.assertEqual(expected, form_field)

    def test_new_post_appears_on_index_group_profile_pages(self):
        new_group = Group.objects.create(
            title='Новая группа',
            slug='cats',
            description='Новое тестовое описание'
        )
        Post.objects.create(
            author=self.author2,
            text='Новый пост',
            group=new_group
        )
        response = self.client.get(reverse('posts:index'))
        new_text = response.context.get('page_obj')[0].text
        self.assertEqual(new_text, 'Новый пост')
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'cats'})
        )
        new_text = response.context.get('page_obj')[0].text
        self.assertEqual(new_text, 'Новый пост')
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.author2})
        )
        new_text = response.context.get('page_obj')[0].text
        self.assertEqual(new_text, 'Новый пост')
