from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Check and fix admin user permissions'

    def handle(self, *args, **options):
        try:
            # Find admin user
            admin_user = User.objects.get(username='admin')
            
            self.stdout.write(f"Found admin user: {admin_user.email}")
            self.stdout.write(f"is_staff: {admin_user.is_staff}")
            self.stdout.write(f"is_superuser: {admin_user.is_superuser}")
            self.stdout.write(f"is_active: {admin_user.is_active}")
            
            # Fix admin permissions if needed
            if not admin_user.is_staff or not admin_user.is_superuser:
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.save()
                self.stdout.write(self.style.SUCCESS("✅ Admin permissions fixed!"))
            else:
                self.stdout.write(self.style.SUCCESS("✅ Admin permissions are correct"))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Admin user not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}")) 