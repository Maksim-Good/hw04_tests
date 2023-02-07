from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


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
            text='Тестовый пост длиннее 15 символов',
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(PostModelTest.post.text[:15], str(PostModelTest.post))
        group = PostModelTest.group
        self.assertEqual(group.title, str(self.group))

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)
        group = PostModelTest.group
        field_verboses = {
            'title': 'Имя группы',
            'slug': 'Тэг',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Здесь нужно ввести основной текст поста.',
            'author': 'Здесь нужно ввести имя автора поста.',
            'group': 'Здесь можно ввести имя группы.',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
        group = PostModelTest.group
        field_help_texts = {
            'title': 'Здесь нужно ввести имя группы.',
            'slug': 'Здесь нужно задать Тэг (уникальное имя).',
            'description': 'Здесь должно быть описание группы.'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)
