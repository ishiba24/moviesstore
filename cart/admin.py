# cart/admin.py
from django.contrib import admin
from .models import Order, Item, CheckoutFeedback

admin.site.register(Order)
admin.site.register(Item)

@admin.register(CheckoutFeedback)
class CheckoutFeedbackAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'feedback_text_short', 'date_submitted', 'order']
    list_filter = ['date_submitted']
    search_fields = ['name', 'feedback_text']
    readonly_fields = ['date_submitted']
    
    def feedback_text_short(self, obj):
        return obj.feedback_text[:50] + "..." if len(obj.feedback_text) > 50 else obj.feedback_text
    feedback_text_short.short_description = 'Feedback'