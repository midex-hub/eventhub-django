from django.core.management.base import BaseCommand
from bookings.models import QRCode


class Command(BaseCommand):
    help = 'Regenerate QR code images so they encode the full public ticket URL instead of the raw code string.'

    def handle(self, *args, **options):
        qrcodes = QRCode.objects.all()
        total = qrcodes.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('No QR codes found.'))
            return

        self.stdout.write(f'Regenerating {total} QR code(s)...')
        updated = 0
        for qr in qrcodes:
            try:
                # Delete the old image file and field value so _generate_qr_image() runs again
                if qr.image:
                    try:
                        qr.image.delete(save=False)
                    except Exception:
                        pass
                    qr.image = None

                qr._generate_qr_image()
                qr.save(update_fields=['image'])
                updated += 1
                self.stdout.write(f'  [OK] {qr.code}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  [ERROR] {qr.code}: {e}'))


        self.stdout.write(self.style.SUCCESS(f'\nDone — {updated}/{total} QR codes regenerated.'))
