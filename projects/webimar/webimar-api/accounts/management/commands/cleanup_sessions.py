from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.utils import cleanup_expired_sessions

class Command(BaseCommand):
    help = 'Süresi dolmuş kullanıcı oturumlarını temizler'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Bu saatten eski oturumları pasifleştir (varsayılan: 24)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Gerçek temizlik yapmadan sadece sayıyı göster'
        )

    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']
        
        if dry_run:
            from datetime import timedelta
            from accounts.models import UserSession
            
            expired_time = timezone.now() - timedelta(hours=hours)
            count = UserSession.objects.filter(
                is_active=True,
                last_activity__lt=expired_time
            ).count()
            
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: {count} adet süresi dolmuş oturum bulundu (>{hours} saat)'
                )
            )
        else:
            count = cleanup_expired_sessions()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ {count} adet süresi dolmuş oturum pasifleştirildi'
                )
            )
