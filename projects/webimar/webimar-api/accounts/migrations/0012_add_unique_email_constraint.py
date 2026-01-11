"""Add unique constraint (index) to auth_user.email without custom user model.

Bu migration önceki hatalı denemeyi (accounts.User modelini varmış gibi AlterField) düzeltir.
Default Django User modeli (auth_user) üzerinde email alanı nullable olabilir; mevcut
verilerde duplicate email veya boş email varsa unique index eklenemez. Bu nedenle:

1. Boş stringleri NULL'a çeviriyoruz (standartlaştırma)
2. Email'i lower() yaparak case-insensitive tutarlılık sağlıyoruz
3. Duplicate kayıt varsa migration hata verecek; kullanıcıya müdahale imkanı için
   TRY/CATCH kullanmıyoruz — CI'da fark edilmesi önemli.
4. Unique partial index kullanıyoruz: yalnızca email IS NOT NULL olan kayıtlar için
   benzersizlik sağlanır (PostgreSQL varsayımı).

Rollback (reverse_sql) indexi düşürür.
"""

from django.db import migrations, connection


def add_unique_email_index(apps, schema_editor):
    vendor = connection.vendor
    with connection.cursor() as cursor:
        # Normalize blanks to NULL and lowercase
        if vendor in ('postgresql', 'sqlite'):
            cursor.execute("UPDATE auth_user SET email = NULL WHERE email = ''")
            cursor.execute("UPDATE auth_user SET email = LOWER(email) WHERE email IS NOT NULL")

            # Check duplicates (case-insensitive) before creating index
            cursor.execute("""
                SELECT lower(email) AS e, COUNT(*) c
                FROM auth_user
                WHERE email IS NOT NULL
                GROUP BY lower(email)
                HAVING COUNT(*) > 1
            """)
            dups = cursor.fetchall()
            if dups:
                # Fail clearly so admin temizleyebilir
                sample = ', '.join([row[0] for row in dups[:5]])
                raise RuntimeError(f"email alanında mükerrer kayıtlar var, index oluşturulamadı. Örnekler: {sample}")

            if vendor == 'postgresql':
                cursor.execute("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'auth_user_email_unique_idx'
                        ) THEN
                            EXECUTE 'CREATE UNIQUE INDEX auth_user_email_unique_idx ON auth_user (LOWER(email)) WHERE email IS NOT NULL';
                        END IF;
                    END$$;
                """)
            elif vendor == 'sqlite':
                # SQLite expression + partial index (3.8+)
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS auth_user_email_unique_idx ON auth_user(lower(email)) WHERE email IS NOT NULL")
        else:
            # Diğer veritabanları için şimdilik sadece uyarı
            print(f"[accounts 0012] Unique email index atlandı (desteklenmeyen DB vendor: {vendor})")


def remove_unique_email_index(apps, schema_editor):
    vendor = connection.vendor
    with connection.cursor() as cursor:
        try:
            if vendor == 'postgresql':
                cursor.execute("DROP INDEX IF EXISTS auth_user_email_unique_idx")
            elif vendor == 'sqlite':
                cursor.execute("DROP INDEX IF EXISTS auth_user_email_unique_idx")
        except Exception as e:
            print(f"[accounts 0012] Index silinirken hata: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_alter_securityevent_user_alter_useractivity_user_and_more'),
    ]

    operations = [
        migrations.RunPython(add_unique_email_index, remove_unique_email_index),
    ]
