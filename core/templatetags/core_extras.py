from django import template

register = template.Library()


@register.filter
def menu_children(page):
    return page.get_children().in_menu()
