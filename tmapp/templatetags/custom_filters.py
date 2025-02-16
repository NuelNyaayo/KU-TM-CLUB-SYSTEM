from django import template

register = template.Library()

@register.filter
def leading_zeros(value, num_digits=3):
    """
    Pads the given integer with leading zeros up to the specified number of digits.
    """
    try:
        return f"{int(value):0{num_digits}d}"
    except (ValueError, TypeError):
        return value  # Return the original value if conversion fails