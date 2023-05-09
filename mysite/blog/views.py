from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import Post


def post_list(request):
    template = 'blog/post/list.html'
    postlist = Post.published.all()
    paginator = Paginator(postlist, 3)
    page_number = request.GET.get('page', 1)
    posts = paginator.page(page_number)
    context = {'posts': posts}
    return render(request, template, context)


def post_detail(request, year, month, day, post):
    template = 'blog/post/detail.html'
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day)
    context = {'post': post}
    return render(request, template, context)
