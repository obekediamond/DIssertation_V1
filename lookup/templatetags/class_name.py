from django import template

register = template.Library()

@register.filter()
def class_name(value):
    print(f"Value: {value}")  # Add this line for debugging
    return value.__class__.__name__
