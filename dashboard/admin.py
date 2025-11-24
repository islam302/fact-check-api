from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import FactCheckHistory


@admin.register(FactCheckHistory)
class FactCheckHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for FactCheckHistory with advanced features
    """

    list_display = [
        'id',
        'query_preview',
        'case_badge',
        'sources_count_display',
        'ip_address',
        'created_at',
    ]

    list_filter = [
        'case',
        'created_at',
        ('news_article', admin.EmptyFieldListFilter),
        ('x_tweet', admin.EmptyFieldListFilter),
    ]

    search_fields = [
        'query',
        'talk',
        'ip_address',
    ]

    readonly_fields = [
        'created_at',
        'sources_display',
        'news_article_preview',
        'tweet_preview',
    ]

    fieldsets = (
        ('معلومات الفحص', {
            'fields': ('query', 'case', 'talk')
        }),
        ('المصادر', {
            'fields': ('sources_display',),
            'classes': ('collapse',)
        }),
        ('محتوى مولّد', {
            'fields': ('news_article_preview', 'tweet_preview'),
            'classes': ('collapse',)
        }),
        ('معلومات التتبع', {
            'fields': ('ip_address', 'user_agent', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    list_per_page = 50
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    actions = ['mark_as_true', 'mark_as_false', 'export_selected']

    def query_preview(self, obj):
        """عرض أول 100 حرف من النص"""
        if len(obj.query) > 100:
            return f"{obj.query[:100]}..."
        return obj.query
    query_preview.short_description = 'النص'

    def case_badge(self, obj):
        """عرض النتيجة بألوان"""
        colors = {
            'true': '#28a745',
            'false': '#dc3545',
            'mixed': '#ffc107',
            'unverified': '#6c757d',
        }
        color = colors.get(obj.case, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_case_display()
        )
    case_badge.short_description = 'النتيجة'

    def sources_count_display(self, obj):
        """عرض عدد المصادر"""
        count = obj.sources_count
        return format_html(
            '<span style="font-weight: bold;">{}</span> مصدر',
            count
        )
    sources_count_display.short_description = 'المصادر'

    def sources_display(self, obj):
        """عرض المصادر بشكل منسق"""
        if not obj.sources:
            return "لا توجد مصادر"

        html = '<ol style="margin: 0; padding-left: 20px;">'
        for source in obj.sources:
            title = source.get('title', 'بدون عنوان')
            url = source.get('url', '#')
            html += f'<li><a href="{url}" target="_blank">{title}</a></li>'
        html += '</ol>'
        return format_html(html)
    sources_display.short_description = 'المصادر'

    def news_article_preview(self, obj):
        """عرض المقال الإخباري"""
        if not obj.news_article:
            return "لم يتم توليد مقال إخباري"
        return format_html(
            '<div style="background: #f5f5f5; padding: 10px; border-radius: 5px; max-height: 200px; overflow-y: auto;">{}</div>',
            obj.news_article.replace('\n', '<br>')
        )
    news_article_preview.short_description = 'المقال الإخباري'

    def tweet_preview(self, obj):
        """عرض التغريدة"""
        if not obj.x_tweet:
            return "لم يتم توليد تغريدة"
        return format_html(
            '<div style="background: #e8f4f8; padding: 10px; border-radius: 5px; border-left: 3px solid #1da1f2;">{}</div>',
            obj.x_tweet.replace('\n', '<br>')
        )
    tweet_preview.short_description = 'التغريدة'

    # Custom Actions
    def mark_as_true(self, request, queryset):
        """تحديد كـ حقيقي"""
        updated = queryset.update(case='true')
        self.message_user(request, f'تم تحديث {updated} سجل كـ حقيقي')
    mark_as_true.short_description = 'تحديد كـ حقيقي'

    def mark_as_false(self, request, queryset):
        """تحديد كـ كاذب"""
        updated = queryset.update(case='false')
        self.message_user(request, f'تم تحديث {updated} سجل كـ كاذب')
    mark_as_false.short_description = 'تحديد كـ كاذب'

    def export_selected(self, request, queryset):
        """تصدير السجلات المحددة (مثال بسيط)"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="fact_checks.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'النص', 'النتيجة', 'التحليل', 'عدد المصادر', 'التاريخ'])

        for obj in queryset:
            writer.writerow([
                obj.id,
                obj.query,
                obj.get_case_display(),
                obj.talk,
                obj.sources_count,
                obj.created_at.strftime('%Y-%m-%d %H:%M')
            ])

        return response
    export_selected.short_description = 'تصدير السجلات المحددة'

    def changelist_view(self, request, extra_context=None):
        """إضافة إحصائيات في أعلى الصفحة"""
        extra_context = extra_context or {}

        # إحصائيات عامة
        total = FactCheckHistory.objects.count()
        today = FactCheckHistory.objects.filter(
            created_at__date=timezone.now().date()
        ).count()
        last_7_days = FactCheckHistory.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()

        # إحصائيات حسب النتيجة
        stats = FactCheckHistory.objects.aggregate(
            true_count=Count('id', filter=Q(case='true')),
            false_count=Count('id', filter=Q(case='false')),
            mixed_count=Count('id', filter=Q(case='mixed')),
            unverified_count=Count('id', filter=Q(case='unverified')),
        )

        extra_context['total_checks'] = total
        extra_context['today_checks'] = today
        extra_context['last_7_days_checks'] = last_7_days
        extra_context['stats'] = stats

        return super().changelist_view(request, extra_context=extra_context)
