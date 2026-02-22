from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("batches", "0002_batch_aborted_reason_batch_contacts_enriched_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="batch",
            name="emails_enriched",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
