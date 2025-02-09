from django import template
# from template_library import custom_filters

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """Добавляет CSS-класс к полю формы."""
    return field.as_widget(attrs={"class": css_class})
