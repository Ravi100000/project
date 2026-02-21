from django import template

register = template.Library()

@register.filter
def is_equal(value, arg):
    return str(value) == str(arg)

@register.filter
def is_in(value, arg):
    """Checks if value (as string) is in a comma-separated list of strings."""
    if not value or not arg:
        return False
    return str(value).strip() in [s.strip() for s in str(arg).split(',')]

@register.filter
def has_any_role(user, roles_str):
    """
    Checks if user has any of the roles in comma-separated roles_str.
    Also returns True if user is superuser.
    Usage: {% if user|has_any_role:"MANAGER,DISPATCHER" %}
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    roles = [r.strip() for r in roles_str.split(',')]
    return getattr(user, 'role', None) in roles
