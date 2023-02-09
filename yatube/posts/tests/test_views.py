from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()

POSTS_ON_PAGE = 10
NUMBER_ONE = 1


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
        Post.objects.bulk_create(
            (
                Post(
                    author=cls.author1,
                    text='Test %s' % i,
                    group=cls.group
                ) for i in range(13)
            ), 13
        )
        Post.objects.bulk_create(
            (
                Post(
                    author=cls.author2,
                    text='Testos %s' % i,
                ) for i in range(13)
            ), 13
        )
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        cls.url_templates = (
            (reverse('posts:index'), 'posts/index.html'),
            (reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}
            ), 'posts/group_list.html'),
            (reverse(
                'posts:profile', kwargs={'username': cls.author1.username}
            ), 'posts/profile.html'),
            (reverse(
                'posts:post_detail', kwargs={'post_id': NUMBER_ONE}
            ), 'posts/post_detail.html'),
            (reverse('posts:post_create'), 'posts/create_post.html'),
            (reverse(
                'posts:post_edit', kwargs={'post_id': NUMBER_ONE}
            ), 'posts/create_post.html'),
        )
        cls.index = cls.url_templates[0][0]
        cls.group_list = cls.url_templates[1][0]
        cls.profile = cls.url_templates[2][0]
        cls.post_detail = cls.url_templates[3][0]
        cls.post_create = cls.url_templates[4][0]
        cls.post_edit = cls.url_templates[5][0]

    def setUp(self):
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(self.author1)

    def paginator_test(self, url, objs):
        for i in range(objs // POSTS_ON_PAGE + NUMBER_ONE):
            with self.subTest(i=i):
                response = self.client.get(url + f'?page={NUMBER_ONE + i}')
                if objs > POSTS_ON_PAGE:
                    pages = POSTS_ON_PAGE
                else:
                    pages = objs % POSTS_ON_PAGE
                self.assertEqual(len(response.context['page_obj']), pages)
                objs -= POSTS_ON_PAGE

    def test_pages_uses_correct_template_for_author(self):
        for url in self.url_templates:
            reverse_name, template = url
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        self.paginator_test(self.index, 26)

    def test_group_posts_show_correct_context(self):
        self.paginator_test(self.group_list, 13)
        response = self.client.get(self.group_list)
        for post in range(POSTS_ON_PAGE):
            group_title = response.context.get('page_obj')[post].group.title
            self.assertEqual(group_title, self.group.title)

    def test_profile_posts_show_correct_context(self):
        self.paginator_test(self.profile, 13)
        response = self.client.get(self.profile)
        for post in range(POSTS_ON_PAGE):
            author = response.context.get('page_obj')[post].author.username
            self.assertEqual(author, self.author1.username)

    def test_detail_page_show_correct_context(self):
        response = self.client.get(self.post_detail)
        post_number = response.context.get('post').id
        self.assertEqual(post_number, NUMBER_ONE)

    def test_post_create_page_show_correct_context(self):
        response = self.authorized_author_client.get(self.post_create)
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        response = self.authorized_author_client.get(self.post_edit)
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        form_fields_received = {
            'text': 'Test 0',
            'group': self.group.id,
        }
        for value, expected in form_fields_received.items():
            with self.subTest(value=value):
                form_field = response.context.get('form')[value].initial
                self.assertEqual(expected, form_field)

    def post_on_page(self, url, text):
        response = self.client.get(url)
        new_text = response.context.get('page_obj')[0].text
        self.assertEqual(new_text, text)

    def test_new_post_appears_on_index_group_profile_pages(self):
        new_group = Group.objects.create(
            title='Новая группа',
            slug='cats',
            description='Новое тестовое описание'
        )
        new_post = Post.objects.create(
            author=self.author2,
            text='Новый пост',
            group=new_group
        )
        self.post_on_page(self.index, new_post.text)
        self.post_on_page(
            reverse('posts:group_list', kwargs={'slug': new_group.slug}),
            new_post.text
        )
        self.post_on_page(
            reverse('posts:profile', kwargs={'username': self.author2}),
            new_post.text
        )
        response = self.client.get(self.group_list)
        new_text = response.context.get('page_obj')[0].text
        self.assertNotEqual(new_text, new_post.text)
