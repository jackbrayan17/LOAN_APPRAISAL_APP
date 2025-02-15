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


# Inline for BranchManager (used inside UserAdmin)
class BranchManagerInline(admin.StackedInline):
    model = BranchManager
    extra = 1
    autocomplete_fields = ['institution']


# Inline for LoanOfficer (used inside UserAdmin)
class LoanOfficerInline(admin.StackedInline):
    model = LoanOfficer
    extra = 1
    autocomplete_fields = ['institution']


# Custom UserAdmin to include roles and permissions in the admin panel
class UserAdmin(DefaultUserAdmin):
    add_form = UserCreationFormWithRoles
    form = UserChangeFormWithRoles

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': (
            'is_active', 'is_staff', 'is_superuser',
            'is_institution', 'is_branch_manager', 'is_loan_officer',
            'groups', 'user_permissions'
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

    inlines = [BranchManagerInline, LoanOfficerInline]

    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser',
                    'is_institution', 'is_branch_manager', 'is_loan_officer')
    search_fields = ('username', 'email')
    ordering = ('username',)

    def save_model(self, request, obj, form, change):
        """
        Automatically create an Institution when needed.
        """
        super().save_model(request, obj, form, change)

        # Auto-create Institution if the user is an institution
        if obj.is_institution:
            Institution.objects.get_or_create(user=obj, defaults={'name': f"Institution - {obj.username}"})


# Register the custom UserAdmin after it's fully defined
admin.site.register(User, UserAdmin)


# Register the other models with the admin
@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'contact', 'user')
    search_fields = ('name', 'address', 'user__username', 'user__email')


@admin.register(BranchManager)
class BranchManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution')
    list_filter = ('institution',)
    search_fields = ('user__username', 'user__email', 'institution__name')
    autocomplete_fields = ['institution']


@admin.register(LoanOfficer)
class LoanOfficerAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution')
    list_filter = ('institution',)
    search_fields = ('user__username', 'user__email', 'institution__name')
    autocomplete_fields = ['institution']
