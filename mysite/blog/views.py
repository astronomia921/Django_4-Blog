from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# from django.views.generic import ListView
from django.views.decorators.http import require_POST
from django.core.mail import send_mail

from taggit.models import Tag

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


def post_list(request,  tag_slug=None):
    template = 'blog/post/list.html'
    num_post = 3
    page_one = 1

    postlist = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        postlist = postlist.filter(tags__in=[tag])

    paginator = Paginator(postlist, num_post)
    page_number = request.GET.get('page', page_one)

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(page_one)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts,
        'tag': tag
        }
    return render(request, template, context)

# class PostListView(ListView):
#     """
#     Альтернативное представление списка постов
#     """
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    template = 'blog/post/detail.html'
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day)
    comments = post.comments.filter(active=True)

    form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = (Post.published
                     .filter(tags__in=post_tags_ids)
                     .exclude(id=post.id))
    similar_posts = (similar_posts
                     .annotate(same_tags=Count('tags'))
                     .order_by('-same_tags', '-publish')[:4])
    context = {
        'post': post,
        'form': form,
        'comments': comments,
        'similar_posts': similar_posts,
        }
    return render(request, template, context)


def post_share(request, post_id):
    template = 'blog/post/share.html'
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    sent = False
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read "f"{post.title}"
            message = (f"Read {post.title} at {post_url}\n\n"
                       f"{cd['name']}\'s comments: {cd['comments']}")
            send_mail(subject, message,
                      'danil.mustafin921@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    context = {
        'post': post,
        'form': form,
        'sent': sent}
    return render(request, template, context)


@require_POST
def post_comment(request, post_id):
    template = 'blog/post/comment.html'
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    context = {
        'post': post,
        'form': form,
        'comment': comment,
    }
    return render(request, template, context)
