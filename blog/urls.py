from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

app_name = 'blog'
urlpatterns = [
    url(r'^[index]?', views.list_blog, name='index'),
    url(r'^view/(?P<slug>[-\w]+)', views.view_blog, name='view_blog'),
    url(r'^category/(?P<category>[\w]+)', views.list_blog_per_category, name='list_per_category'),
    url(r'^search', views.search_blog, name='search'),
    url(r'^add', views.add_blog, name='add_blog'),
    url(r'^edit', views.edit_blog, name='edit_blog'),
    url(r'^delete', views.delete_blog, name='delete_blog'),
    url(r'^about', TemplateView.as_view(template_name='blog/about.html'), name='about'),
    url(r'^comment/delete', views.delete_comment, name='del_comment'),
    url(r'^comment/add', views.add_comment, name='add_comment'),
    url(r'^get-categories', views.get_category_links, name='get_categories'),
]
