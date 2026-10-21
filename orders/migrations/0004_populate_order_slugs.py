from django.db import migrations


def populate_slugs(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    for order in Order.objects.all().iterator():
        order.slug = f'order-{order.pk}'
        order.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_slug'),
    ]

    operations = [
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
    ]