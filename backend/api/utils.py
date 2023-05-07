from django.db.models import F, Sum


def create_shopping_cart_report(items):
    items = items.values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(
        name=F('ingredient__name'),
        units=F('ingredient__measurement_unit'),
        total=Sum('amount'),
    ).order_by('-total')

    text = '\n'.join([
        f"{item['name']} ({item['units']}) - {item['total']}"
        for item in items
    ])

    return text
