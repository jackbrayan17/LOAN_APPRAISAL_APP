from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import BranchManager, Institution  # Adjust based on your app structure

User = get_user_model()

@receiver(post_save, sender=User)
def create_branch_manager(sender, instance, created, **kwargs):
    if created and instance.is_branch_manager:  # Assuming you have this field to check
        institution = Institution.objects.first()  # Example: Assign the first institution (change this logic as needed)
        BranchManager.objects.create(user=instance, institution=institution)
