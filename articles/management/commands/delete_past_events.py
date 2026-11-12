from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from articles.models import Event

class Command(BaseCommand):
    
    help = 'Delete events whose date and start time have already passed.'
    
    def handle(self, *args, **options):
        
        now = timezone.localtime()
        
        events = Event.objects.all()
        
        # Keep track of how many events were deleted
        deleted_count = 0
        
        for event in events:
            
            # If the event has no date, don't delete it.
            if not event.event_date:
                continue
            
            # If the event has no time, don't delete it.
            # don't delete it automatically.
            if not event.end_time:
                continue
            
            # combine event date and end time
            event_datetime = timezone.make_aware(
                datetime.combine(
                    event.event_date,
                    event.end_time
                )
            )
                
            # Delete only events that have completely passed.
            if event_datetime < now:
                
                self.stdout.write(
                    self.style.WARNING(
                        f'Deleting past event: {event.title}'
                    )
                )
                event.delete()
                
                deleted_count += 1
                
        self.stdout.write(
            self.style.SUCCESS(
                f'Done. Deleted {deleted_count} past event(s).'
            )
        )