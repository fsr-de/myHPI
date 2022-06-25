from django import template

register = template.Library()


@register.inclusion_tag("menu_level.html")
def build_menu_level(sub_pages_by_level_and_id, level):
    return {"sub_pages_by_id": sub_pages_by_level_and_id.get(level, {}), "level": level}


@register.filter
def get(dict, key):
    return dict[key]


@register.filter
def sub_menu_pages(page):
    return page.menu_children


@register.filter
def all_sub_menu_pages_by_id(pages):
    all_sub_pages_by_id = {}
    for page in pages:
        traverse_page_tree(page, [], all_sub_pages_by_id)
    return all_sub_pages_by_id


def traverse_page_tree(curr_page, id_history, all_sub_pages):
    id = format_id_history(id_history)
    level_id = len(id_history)
    same_level_sub_pages = all_sub_pages.get(level_id, {})
    same_level_sub_pages[id] = same_level_sub_pages.get(id, []) + [curr_page]
    all_sub_pages[level_id] = same_level_sub_pages
    sub_pages = sub_menu_pages(curr_page)
    for sub_page in sub_pages:
        traverse_page_tree(sub_page, id_history + [curr_page.id], all_sub_pages)


def format_id_history(id_history):
    if not id_history:
        return "root"
    return str(id_history[-1])
