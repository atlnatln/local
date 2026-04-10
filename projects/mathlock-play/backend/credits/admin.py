from django.contrib import admin
from .models import (ChildProfile, CreditBalance, CreditPackage,
                     Device, PurchaseRecord, Question, QuestionSet, UserQuestionProgress)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('installation_id', 'device_token', 'email', 'created_at', 'last_seen')
    search_fields = ('installation_id', 'email')
    readonly_fields = ('device_token', 'created_at', 'last_seen')


@admin.register(ChildProfile)
class ChildProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'device', 'total_correct', 'total_shown', 'current_difficulty', 'updated_at')
    list_filter = ('current_difficulty',)


@admin.register(CreditBalance)
class CreditBalanceAdmin(admin.ModelAdmin):
    list_display = ('device', 'balance', 'total_purchased', 'total_used', 'free_set_used')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PurchaseRecord)
class PurchaseRecordAdmin(admin.ModelAdmin):
    list_display = ('device', 'product_id', 'credits_added', 'verified', 'consumed', 'created_at')
    list_filter = ('verified', 'consumed', 'product_id')
    readonly_fields = ('purchase_token', 'verification_response', 'created_at')


@admin.register(QuestionSet)
class QuestionSetAdmin(admin.ModelAdmin):
    list_display = ('child', 'version', 'is_ai_generated', 'credit_used', 'created_at')
    list_filter = ('is_ai_generated', 'credit_used')


@admin.register(CreditPackage)
class CreditPackageAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'display_name', 'credits', 'questions_count', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    list_editable = ('is_active', 'sort_order')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_id', 'text', 'answer', 'question_type', 'difficulty', 'batch_number')
    list_filter = ('question_type', 'difficulty', 'batch_number')
    search_fields = ('text',)


@admin.register(UserQuestionProgress)
class UserQuestionProgressAdmin(admin.ModelAdmin):
    list_display = ('device', 'question', 'solved', 'solve_count', 'last_attempt_at')
    list_filter = ('solved',)
    raw_id_fields = ('device', 'question')
