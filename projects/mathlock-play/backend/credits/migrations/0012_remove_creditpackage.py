# Generated manually — CreditPackage model no longer used by any endpoint

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('credits', '0011_question_question_code'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CreditPackage',
        ),
    ]
