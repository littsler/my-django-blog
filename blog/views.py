import logging
import itertools
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.utils.text import slugify
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q
from django.http.response import JsonResponse

from .forms import CommentForm, BlogForm
from .models import Blog, Comment, Tag, Category
from .settings import BLOGS_PER_PAGE

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def list_blog(request):
    blog_list = Blog.objects.all()
    return _render_paged_blog_list(request, blog_list, 'Blogs')


def list_blog_per_category(request, category):
    blog_list = Blog.objects.filter(category=category)
    return _render_paged_blog_list(request, blog_list, 'Blogs of Category \'' + category + '\'')


def view_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    comment_list = Comment.list_per_blog(blog.pk)
    return render(request, 'blog/view.html',
                  context={'blog': blog, 'comments': comment_list, 'comment_form': CommentForm()})


@login_required()
def add_blog(request):
    if not request.user.groups.filter(name='authors'):
        return render(request, 'blog/error.html', {'error': _('Insufficient privilege!'), 'message': _(
            'Insufficient privilege! Please contact administrator!')})
    if request.method == 'POST':
        parameters = request.POST
        log.debug(parameters)
        tags = parameters['tags'].split(',')
        tag_instances = []
        for tag in tags:
            try:
                tag_instances.append(Tag.objects.get(name=tag))
            except Tag.DoesNotExist:
                instance = Tag(name=tag)
                instance.save()
                tag_instances.append(instance)
        blog_form = BlogForm(parameters)
        if blog_form.is_valid():
            blog = blog_form.save(commit=False)
            blog.author = request.user
            slug_prefix = slugify(blog.title)
            slug = slug_prefix
            for i in itertools.count(1):
                if not Blog.objects.filter(slug=slug).exists():
                    break
                slug = "%s-%d" % (slug_prefix, i)
            blog.slug = slug
            blog.save()
            blog.tags.add(*tag_instances)
            blog.save()
            return redirect('blog:view_blog', slug=slug)
    else:
        return render(request, 'blog/add.html', {'categories': Category.objects.all()})


@login_required
@permission_required('blog.change_blog')
def edit_blog(request):
    if request.method == 'POST':
        parameters = request.POST
        blog = Blog.objects.get(pk=parameters.get('blog_id'))
        if request.user != blog.author:
            return render(request, 'blog/error.html', {'error': _('Insufficient privilege!'), 'message': _(
                'Insufficient privilege! Please contact administrator!')})
        tags = parameters['tags'].split(',')
        tag_instances = []
        for tag in tags:
            try:
                tag_instances.append(Tag.objects.get(name=tag))
            except Tag.DoesNotExist:
                instance = Tag(name=tag)
                instance.save()
                tag_instances.append(instance)
        blog_form = BlogForm(parameters, instance=blog)
        if blog_form.is_valid():
            blog_modified = blog_form.save(commit=False)
            slug_prefix = slugify(blog.title)
            slug = slug_prefix
            for i in itertools.count(1):
                if not Blog.objects.filter(slug=slug).exists():
                    break
                slug = "%s-%d" % (slug_prefix, i)
            blog_modified.slug = slug
            blog_modified.tags.add(*tag_instances)
            blog_modified.save()
            return redirect(reverse('blog:view_blog', args=(blog_modified.slug,)))
    else:
        blog = Blog.objects.get(pk=request.GET.get('blog_id'))
        blog_form = BlogForm(instance=blog)
        tag_str = ','.join(tag.name for tag in blog.tags.all())
        return render(request, 'blog/add.html',
                      {'blog_form': blog_form, 'categories': Category.objects.all(), 'blog_id': blog.pk,
                       'tags': tag_str})


@login_required
@permission_required('blog.delete_blog')
def delete_blog(request):
    if request.method == 'post':
        blog_id = request.POST.get('blog_id')
    else:
        blog_id = request.GET.get('blog_id')
    if blog_id is None or not Blog.objects.filter(pk=blog_id).exists():
        return redirect(reverse('blog:error', kwargs={'error': _('The required blog does not exist'),
                                                      'message': _(
                                                          'The required blog does not exist! Please perform the operation through the valid pages')}))
    blog = Blog.objects.get(pk=blog_id)
    if request.user != blog.author:
        return redirect(reverse('blog:error', kwargs={'error': _('Insufficient Previlige'),
                                                      'message': _(
                                                          'You are not the author of the blog to delete. Cannot perform the deletion!')}))
    blog.delete()
    return redirect(reverse('blog:index'))


@require_GET
def search_blog(request):
    parameters = request.GET
    q_chain = Q()
    for key in parameters.keys():
        if key == 'keyword':
            q_chain &= Q(title__icontains=parameters['keyword']) | Q(tags=parameters['keyword'])
        elif key == 'author':
            q_chain &= Q(author__username=parameters['author'])
        else:
            q_chain &= Q(**{key: parameters[key]})
    blog_list = Blog.objects.filter(q_chain).distinct()
    return render(request, 'blog/index.html', {'blog_list': blog_list, 'title': 'Search Results'})


@require_GET
@permission_required('blog.delete_comment')
def delete_comment(request):
    Comment.objects.get(pk=request.GET.get('comment')).delete()
    return redirect(request.GET.get('next'))


@require_POST
@permission_required('blog.add_comment')
def add_comment(request):
    comment_form = CommentForm(request.POST)
    author = request.user
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.author = author
        comment.save()
        return redirect(request.META['HTTP_REFERER'])
    else:
        raise Exception(comment_form.errors)


def get_category_links(request):
    data = {}
    for c in Category.objects.all():
        data[c.content] = reverse('blog:list_per_category', args=[c.content])
    return JsonResponse(data)


def _render_paged_blog_list(request, blog_list, title):
    paginator = Paginator(blog_list, BLOGS_PER_PAGE)
    page = request.GET.get('page')
    try:
        blogs = paginator.page(page)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages)
    return render(request, 'blog/index.html',
                  context={'blog_list': blogs, 'title': title})
