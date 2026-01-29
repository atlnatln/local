
from django.core.management.base import BaseCommand
from apps.batches.models import Batch
from apps.batches.services import BatchProcessor
import logging

from apps.accounts.models import Organization

class Command(BaseCommand):
    help = 'Runs a test batch for İzmir Grid Search'

    def handle(self, *args, **options):
        self.stdout.write("Initializing Test Batch: İzmir / Şehir plancısı")
        
        # Ensure Org exists
        org, _ = Organization.objects.get_or_create(name="Test Org")
        
        # Cleanup previous tests
        Batch.objects.filter(city='İzmir', sector='Şehir plancısı').delete()
        
        # Create Batch
        batch = Batch.objects.create(
            organization=org,
            created_by="admin_test", 
            city='İzmir',
            sector='Şehir plancısı',
            record_count_estimate=50,
            status='CREATED'
        )
        
        self.stdout.write(f"Created Batch ID: {batch.id}")
        
        processor = BatchProcessor(batch.id)
        
        self.stdout.write("Starting Pipeline (Stage 1)...")
        self.stdout.write("Watch logs for Grid Search activation.")
        
        # Configure logging to show up in console for apps.providers.grid_search
        logger = logging.getLogger('apps.providers.grid_search')
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        
        # Also for batch services
        bs_logger = logging.getLogger('apps.batches.services')
        bs_logger.setLevel(logging.DEBUG)
        bs_logger.addHandler(handler)

        try:
            # We only want to run Stage 1 for this test, but run_pipeline does more.
            # safe to run_pipeline if it stops after stage 1 or we interrupt.
            # Actually run_pipeline runs everything. 
            # Let's just run _stage_collect_ids directly for the test to inspect results immediately.
            
            candidates = processor._stage_collect_ids()
            
            self.stdout.write(f"\n--- RESULTS ---")
            self.stdout.write(f"Found {len(candidates)} candidates.")
            for c in candidates[:10]:
                self.stdout.write(f" - {c['name']} ({c['id']})")
            if len(candidates) > 10:
                self.stdout.write(f"... and {len(candidates) - 10} more.")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            import traceback
            traceback.print_exc()

