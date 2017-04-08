from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import datetime


class Category(models.Model):
    """
    Model of categories.
    """
    content = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.content

    def __repr__(self):
        return self.content


class Tag(models.Model):
    """
    Model of tags
    """
    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Blog(models.Model):
    """
    Model of blog articles.
    """
    author = models.ForeignKey(User)
    title = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)
    content = models.CharField(max_length=4096)
    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(to=Tag, related_name='blogs', related_query_name='blog', blank=True)
    pub_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    """
    Model of comments to blog articles.
    """
    author = models.ForeignKey(User)
    content = models.CharField(max_length=4096)
    topic = models.ForeignKey(Blog, related_name='comments')
    reply_to = models.ForeignKey('self', null=True, blank=True, related_name='replies')
    pub_date = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ['pub_date']

    @classmethod
    def list_per_blog(cls, blog_pk):
        """
        Return the comments related to a blog article with the given pk.
        The comments that reply other comments will be added with an additional attribute reply_to_author, 
        which is the author of the comment replied.
        :param blog_pk: the pk of the blog article
        :return: the list of comments related to the blog article
        """
        comments = Comment.objects.select_related('reply_to').filter(topic=blog_pk)
        for comment in comments:
            if comment.reply_to is not None:
                comment.reply_to_author = comment.reply_to.author
        return comments
