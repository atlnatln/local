from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('credits', '0006_levelset'),
    ]

    operations = [
        # ── 1. RenewalLock tablosu ──────────────────────────────────────────
        migrations.CreateModel(
            name='RenewalLock',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID',
                )),
                ('content_type', models.CharField(max_length=20)),
                ('expires_at', models.DateTimeField(
                    help_text='Bu süre geçince kilit geçersiz sayılır',
                )),
                ('created_at', models.DateTimeField(
                    default=django.utils.timezone.now,
                )),
                ('child', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='renewal_locks',
                    to='credits.childprofile',
                )),
            ],
            options={
                'indexes': [
                    models.Index(fields=['expires_at'], name='credits_renewallock_expires_idx'),
                ],
                'unique_together': {('child', 'content_type')},
            },
        ),

        # ── 2. Geçersiz education_period kayıtlarını düzelt ─────────────────
        # Eski profillerde beklenmedik bir değer varsa sinif_2'ye çek.
        migrations.RunSQL(
            sql="""
                UPDATE credits_childprofile
                SET education_period = 'sinif_2'
                WHERE education_period NOT IN (
                    'okul_oncesi', 'sinif_1', 'sinif_2', 'sinif_3', 'sinif_4'
                )
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
