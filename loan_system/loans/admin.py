from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User, Institution, BranchManager, LoanOfficer

# Custom User form for creating users
class UserCreationFormWithRoles(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

# Custom User form for updating users
class UserChangeFormWithRoles(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

# Custom UserAdmin to include roles and permissions in the admin panel
class UserAdmin(DefaultUserAdmin):
    add_form = UserCreationFormWithRoles
    form = UserChangeFormWithRoles

    fieldsets = (
        (None, {'fields': ('username', 'password')}), 
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'is_institution', 
            'is_branch_manager', 'is_loan_officer', 'groups', 'user_permissions'
        )}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2', 'first_name', 'last_name', 'email', 
                'is_institution', 'is_branch_manager', 'is_loan_officer', 'is_active'
            )},
        ),
    )

    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 
                    'is_institution', 'is_branch_manager', 'is_loan_officer')
    search_fields = ('username', 'email')
    ordering = ('username',)

    def save_model(self, request, obj, form, change):
        """
        Override the save_model method to automatically assign roles and create related objects
        when creating or updating users.
        """
        super().save_model(request, obj, form, change)

        # Create the role-specific objects based on the roles assigned
        if obj.is_institution:
            institution, created = Institution.objects.get_or_create(user=obj)
            institution.name = "Institution Name"  # Placeholder, update as necessary
            institution.save()

        if obj.is_branch_manager:
            # Ensure an institution exists before creating a branch manager
            institution = Institution.objects.first()  # Replace with your logic to assign an institution
            if institution:
                branch_manager, created = BranchManager.objects.get_or_create(user=obj)
                branch_manager.institution = institution
                branch_manager.save()

        if obj.is_loan_officer:
            # Ensure an institution exists before creating a loan officer
            institution = Institution.objects.first()  # Replace with your logic to assign an institution
            if institution:
                loan_officer, created = LoanOfficer.objects.get_or_create(user=obj)
                loan_officer.institution = institution
                loan_officer.save()

# Register the custom UserAdmin after it's fully defined
admin.site.register(User, UserAdmin)

# Register the other models with the admin
@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'contact', 'user')

@admin.register(BranchManager)
class BranchManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution')

@admin.register(LoanOfficer)
class LoanOfficerAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution')
    list_filter = ('institution',)
    search_fields = ('user__username', 'user__email', 'institution__name')
