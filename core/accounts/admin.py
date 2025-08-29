from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

# Register your models here.

class CustomUserCreationForm(UserCreationForm):
    """Formulario personalizado para crear usuarios"""
    class Meta:
        model = User
        fields = ('email', 'username')

class CustomUserChangeForm(UserChangeForm):
    """Formulario personalizado para editar usuarios"""
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff')

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Configuración del admin para User personalizado"""
    
    # Formularios personalizados
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    
    # Campos mostrados en la lista
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    
    # Campos de búsqueda
    search_fields = ('email', 'username', 'first_name', 'last_name')
    
    # Ordenamiento
    ordering = ('email',)
    
    # Campos en el formulario de detalle
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Información Personal', {
            'fields': ('username', 'first_name', 'last_name')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # Campos para agregar usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
        ('Información Personal', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name'),
        }),
        ('Permisos', {
            'classes': ('wide',),
            'fields': ('is_staff', 'is_active'),
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ('date_joined', 'last_login')
    
    # Configuración de filtros
    filter_horizontal = ('groups', 'user_permissions')
    
    def get_queryset(self, request):
        """Optimizar queries con select_related"""
        qs = super().get_queryset(request)
        return qs.select_related().prefetch_related('groups')
    
    def save_model(self, request, obj, form, change):
        """Personalizar guardado si es necesario"""
        super().save_model(request, obj, form, change)
