from django import template

register = template.Library()


@register.filter()
def chinese_name(user):
    if user.first_name and user.last_name:
        return user.last_name + user.first_name
    else:
        return user.username
