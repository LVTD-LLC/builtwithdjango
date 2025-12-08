from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = "Get or create an API token for a user"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="Username to get/create token for. If not provided, uses first superuser.",
        )

    def handle(self, *args, **options):
        User = get_user_model()

        if options["username"]:
            try:
                user = User.objects.get(username=options["username"])
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User '{options['username']}' not found"))
                return
        else:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                self.stdout.write(self.style.ERROR("No superuser found. Please create one first."))
                return

        if not user.is_superuser:
            self.stdout.write(
                self.style.WARNING(f"Warning: User '{user.username}' is not a superuser. API will reject requests.")
            )

        token, created = Token.objects.get_or_create(user=user)

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created new token for user '{user.username}'"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Retrieved existing token for user '{user.username}'"))

        self.stdout.write(self.style.SUCCESS(f"\nAPI Token: {token.key}"))
        self.stdout.write(
            self.style.SUCCESS(f"\nUse this in your API requests:\ncurl -H 'Authorization: Token {token.key}' ...")
        )
