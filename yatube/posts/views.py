from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.conf import settings

from .forms import PostForm, CommentForm
from .models import Post, Group, Comment, Follow, User

@cache_page(20, key_prefix='index_page')
def index(request):
    posts = Post.objects.select_related(
        'group',
        'author',
    ).order_by(
        '-pub_date'
    )
    paginator = Paginator(posts, settings.POSTS_QUANTITY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all().order_by('-pub_date')
    paginator = Paginator(posts, settings.POSTS_QUANTITY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, settings.POSTS_QUANTITY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author).exists()
    template_name = 'posts/profile.html'
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template_name, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post)
    template_name = 'posts/post_detail.html'
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, template_name, context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    template_name = 'posts/create_post.html'
    return render(request, template_name, {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post.id)
    if request.method == "POST":
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:post_detail', post.id)
    form = PostForm(instance=post)
    return render(request, 'posts/create_post.html', {
        'post': post,
        'form': form,
        'post_id': post_id,
        'is_edit': True,
    })

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

@login_required
def follow_index(request):
    page_obj = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)

@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
            )
        return redirect('posts:follow_index')
    return redirect('posts:profile', username=author)

@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.filter(
            user=request.user,
            author=author
        ).delete()
        return redirect('posts:follow_index')
    return redirect('posts:profile', username=author)
 