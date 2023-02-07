from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Test_name')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(self.author)

    def test_create_post(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст2',
            'group': self.group.id,
        }
        response = self.authorized_author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': 'Test_name'}
            )
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст2',
            ).exists()
        )

    def test_edit_post(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
        }
        response = self.authorized_author_client.post(
            reverse('posts:post_edit', args=(1,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', args=(1,)
            )
        )
        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Post.objects.filter(
                text='Измененный текст',
            ).exists()
        )
