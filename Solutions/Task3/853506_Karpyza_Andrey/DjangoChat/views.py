from django.shortcuts import render, get_object_or_404
from .models import Post, News, Like, RegistrationMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, UserRegistrationForm
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required


def post_list(request):
    object_list = Post.objects.filter(status='published')
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page') # получаем аттрибут page из запроса, указывающий на нужную страницу
    news = News.objects.all()
    news = news[len(news)-1]
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'DjangoChat/post/list.html',
                  {'page': page,
                   'posts': posts,
                   'news': news},)


@login_required
def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comment_objects = post.comments.filter(active=True)
    paginator = Paginator(comment_objects, 5)
    page = request.GET.get('page')
    likes = Like.objects.filter(post = post)
    is_liked = False
    for l in likes:
        if l.author == request.user:
            is_liked = True
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        comments = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        comments = paginator.page(paginator.num_pages)
    return render(request,
                  'DjangoChat/post/detail.html',
                  {'post': post,
                   'page': page,
                   'paginator': paginator,
                   'comments': comments,
                   'comment_form': comment_form,
                   })


@login_required
def post_like(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comment_objects = post.comments.filter(active=True)
    paginator = Paginator(comment_objects, 5)
    page = request.GET.get('page')
    if request.method == 'GET':
        likes = Like.objects.filter(post=post)
        is_liked = True
        for l in likes:
            if l.author == request.user:
                is_liked = False
                post.like_count-=1
                post.save()
                l.delete()
                break
        if is_liked:
            post.like_count += 1
            post.save()
            like = Like()
            like.author = request.user
            like.post = post
            like.save()
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        comments = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        comments = paginator.page(paginator.num_pages)

    return render(request,
                  'DjangoChat/post/detail.html',
                  {'post': post,
                   'page': page,
                   'paginator': paginator,
                   'comments': comments,
                   'comment_form': comment_form,
                   })


class PostListView(ListView):
    queryset = Post.objects.filter(status='published')
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'DjangoChat/post/list.html'


@login_required
def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(request.user.username, request.user.email, post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, request.user.email, cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'DjangoChat/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            return render(request, 'registration/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'user_form': user_form})


def register_confirm(request, key):
    print(key)
    message = get_object_or_404(RegistrationMessage, url=key)
    print('MSG: {}'.format(message))
    message.profile.verified = True
    message.profile.save()
    return render(request, 'registration/register_confirm.html')
