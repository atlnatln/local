from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('credits', '0005_child_question_progress'),
    ]

    operations = [
        migrations.CreateModel(
            name='LevelSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField()),
                ('levels_json', models.JSONField(help_text='12 seviyeden oluşan set')),
                ('is_ai_generated', models.BooleanField(default=False)),
                ('credit_used', models.BooleanField(default=False, help_text='Bu set için kredi harcandı mı')),
                ('completed_level_ids', models.JSONField(blank=True, default=list, help_text='Tamamlanan seviye ID\'leri')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='level_sets', to='credits.childprofile')),
            ],
            options={
                'ordering': ['-version'],
                'unique_together': {('child', 'version')},
            },
        ),
    ]
