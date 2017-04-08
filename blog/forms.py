from django.forms import ModelForm, CharField
from django.forms.widgets import Textarea, HiddenInput

from .models import Comment, Blog


class CommentForm(ModelForm):
    def __init__(self, data=None, instance=None):
        if instance is not None:
            if instance.reply_to is not None:
                self.reply_to_author = Comment.objects.get(pk=instance.reply_to).author
        super(CommentForm, self).__init__(data=data, instance=instance)

    reply_to_author = CharField(max_length=50, required=False, widget=HiddenInput())

    class Meta:
        model = Comment
        fields = ['content', 'topic', 'reply_to', 'reply_to_author']
        widgets = {
            'content': Textarea(attrs={'cols': 60, 'rows': 5, 'class': 'form-control', 'style': "width: 60%"}),
            'topic': HiddenInput(), 'reply_to': HiddenInput(attrs={'required': False})}
        labels = {'content': 'Leave a comment'}


class BlogForm(ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content', "category"]
        widgets = {'content': Textarea({'cols': 80, 'rows': 15})}
