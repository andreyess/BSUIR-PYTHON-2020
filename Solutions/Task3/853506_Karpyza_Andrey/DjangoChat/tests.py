import pytest

from django.contrib.auth import authenticate
from django.test import Client

from DjangoChat.forms import UserRegistrationForm
from DjangoChat.models import *
import ISP.settings

@pytest.fixture(scope="function")
def data_source(db):
    c = Client()
    c.post('/register/', {'username': 'test', 'first_name': 'Andrew', 'password': 'test',
                                     'password2': 'test', 'email': 'test@gmail.com'})
    user = User.objects.get(username='test')
    profile = user.profile
    post = Post.objects.create(title='TestPost', author=user, body='test body', slug='testpost', status='published')
    registration_msg = RegistrationMessage.objects.create(profile=profile, url='abcabc', sended = True)
    comment = Comment.objects.create(post=post, author=user, body='comment')
    news = News.objects.create(body='news body', title='news title')
    like = Like.objects.create(post=post, author=user)


def test_save(db, data_source):
    user = User.objects.get(username='test')
    post = Post.objects.get(title='TestPost')
    comment = Comment.objects.get(body='comment')
    news = News.objects.get(title='news title')
    like = Like.objects.get(author=user)
    assert post.body == 'test body'
    assert comment.author == user
    assert news.body == 'news body'
    assert like.post == post


def test_save_user(db, data_source):
    user = authenticate(username="test", password="test")
    assert user.email == "test@gmail.com"
    assert user.profile.verified == False
    assert user.password != 'test'


def test_save_comment(db, data_source):
    comment = Comment.objects.get(body='comment')
    assert comment.author.username == 'test'
    assert comment.body == 'comment'
    assert comment.post.title == 'TestPost'


def test_login_form(db, data_source):
    c = Client()
    response = c.get('/login/')
    assert response.status_code == 200
    response = c.post('/login/', {'username': 'default0', 'password': 'default'})
    assert response.status_code == 200
    response = c.post('/login/', {'username': 'test', 'password': 'test'})
    assert response.status_code == 302


@pytest.mark.parametrize("email,username,password,password2,error_field",
                         [('test@gmail.com', 'check', 'test', 'test', "email"),
                          ('Nonedefault@gmail.com', 'test', 'test', 'test', "username"),
                          ('Nonedefault@gmail.com', 'Nonedefault', 'Nonedefault', 'test', "password2"), ])
def test_registration_form(db, data_source, email, username, password, password2, error_field):
    form_data = {'username': username, 'password': password,
                                     'password2': password2, 'email': email}
    form = UserRegistrationForm(data=form_data)
    assert form.has_error(error_field)


def test_logout(db, data_source):
    c = Client()
    assert c.login(username='test', password='test')
    response = c.post('/logout/')
    assert response.status_code == 302


def test_main_url(db, data_source):
    c = Client()
    response = c.get("/")
    assert response.status_code == 200


def test_detail_get_url(db, data_source):
    c = Client()
    post = Post.objects.get(title='TestPost')
    data = (post.publish.year,
            post.publish.strftime('%m'),
            post.publish.strftime('%d'),
            post.slug)
    response = c.get("/1000/47/22/testpost/")
    assert response.status_code == 302
    response = c.get("/{}/{}/{}/{}/".format(*data[:-1], 'failure'))
    assert response.status_code == 302
    response = c.get("/{}/{}/{}/{}/".format(*data))
    assert response.status_code == 302
    assert c.login(username='test', password='test')
    response = c.get("/{}/{}/{}/{}/".format(*data))
    assert response.status_code == 200


def test_detail_post_url(db, data_source):
    c = Client()
    assert c.login(username='test', password='test')
    post = Post.objects.get(title='TestPost')
    data = (post.publish.year,
            post.publish.strftime('%m'),
            post.publish.strftime('%d'),
            post.slug)
    response = c.post("/{}/{}/{}/{}/".format(*data[:-1], 'failure'), {'body': 'TestCommentNumberTwo'})
    assert response.status_code == 404
    response = c.post("/{}/{}/{}/{}/".format(*data), {'body': 'TestCommentNumberTwo'})
    assert response.status_code == 200
    comments = Comment.objects.all()
    assert len(comments) == 2


def test_detail_like_url(db, data_source):
    c = Client()
    post = Post.objects.get(title='TestPost')
    data = (post.publish.year,
            post.publish.strftime('%m'),
            post.publish.strftime('%d'),
            post.slug)
    response = c.get("/{}/{}/{}/{}/like".format(*data))
    assert response.status_code == 302
    assert c.login(username='test', password='test')
    response = c.get("/{}/{}/{}/{}/like".format(*data))
    assert response.status_code == 200
    response = c.get("/{}/{}/{}/{}/like".format(*data))
    assert response.status_code == 200
    response = c.post("/{}/{}/{}/{}/like".format(*data), {'body': 'TestCommentNumberThree'})
    assert response.status_code == 200


def test_share_url(db, data_source):
    c = Client()
    post = Post.objects.get(title='TestPost')
    response = c.get("/{}/share/".format(post.id))
    assert response.status_code == 302
    assert c.login(username='test', password='test')
    response = c.get("/{}/share/".format(post.id))
    assert response.status_code == 200
    response = c.post("/{}/share/".format(post.id), {'to': 'andrey.karpyza@mail.ru', 'comments': 'check it'})
    assert response.status_code == 200


def test_register_get_url(db, data_source):
    c = Client()
    response = c.get('/register/')
    assert response.status_code == 200


@pytest.mark.parametrize("email,username,password,password2,result_code,acc_count",
                         [('test@gmail.com', 'check', 'test', 'test', 200, 1),
                          ('Nonedefault@gmail.com', 'test', 'test', 'test', 200, 1),
                          ('Nonedefault@gmail.com', 'USERNAME', 'Nonedefault', 'test', 200, 1),
                          ('Nonedefault@gmail.com', 'USERNAME', 'Nonedefault', 'Nonedefault', 200, 2)])
def test_register_post_url(db, data_source, email, username, password, password2, result_code, acc_count):
    c = Client()
    response = c.post('/register/', {'username': username, 'first_name': 'name', 'password': password,
                          'password2': password2, 'email': email})
    assert response.status_code == result_code
    users = User.objects.all()
    assert len(users) == acc_count


def test_password_confirmation_url(db, data_source):
    c = Client()
    profiles = Profile.objects.filter(verified=False)
    assert len(profiles) == 1
    response = c.get('/register/confirmation/{}'.format('false'))
    assert response.status_code == 404
    response = c.get('/register/confirmation/{}'.format('abcabc'))
    assert response.status_code == 200
    profiles = Profile.objects.filter(verified=False)
    assert len(profiles) == 0


def test_login_url(db, data_source):
    c = Client()
    response = c.post('/login/', {'username': 'abcabc', 'password': 'abcabc'})
    assert response.status_code == 200
    response = c.post('/login/', {'username': 'test', 'password': 'test'})
    assert response.status_code == 302
    assert response.url == '/login/'
    # confirm password and activate account
    response = c.get('/register/confirmation/{}'.format('abcabc'))
    assert response.status_code == 200
    response = c.post('/login/', {'username': 'test', 'password': 'test'})
    assert response.status_code == 302
    assert response.url == '/'


def test_password_reset_url(db, data_source):
    c = Client()
    response = c.post('/password-reset/', {'email': 'test@gmail.com'})
    assert response.status_code == 302
