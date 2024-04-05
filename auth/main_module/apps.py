import django
from django.apps import AppConfig

class MainModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main_module'

    def ready(self):
        try:
            import main_module.signals
        except ImportError:
            # Обработка ошибки, если не удается импортировать сигналы
            pass