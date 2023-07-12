from django.contrib import admin
from .models import AddItem,Purchase,Sales,Unit

# Register your models here.
admin.site.register(AddItem)
admin.site.register(Purchase)
admin.site.register(Sales)
admin.site.register(Unit)