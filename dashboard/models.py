from django.db import models
from django.utils import timezone
import uuid


class FactCheckHistory(models.Model):
    """
    Model to store all fact-check requests and their analysis results
    """

    # الحالات المختلفة للنتيجة
    CASE_CHOICES = [
        ('true', 'حقيقي'),
        ('false', 'كاذب'),
        ('mixed', 'غير مؤكد/مختلط'),
        ('unverified', 'غير موثق'),
    ]

    # Primary Key as UUID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # البيانات الأساسية
    query = models.TextField(
        verbose_name='النص/العنوان المُدخل',
        help_text='النص أو العنوان الذي تم فحصه'
    )

    case = models.CharField(
        max_length=20,
        choices=CASE_CHOICES,
        verbose_name='النتيجة',
        help_text='نتيجة الفحص: حقيقي، كاذب، مختلط، أو غير موثق'
    )

    talk = models.TextField(
        verbose_name='التحليل',
        help_text='التحليل الكامل للخبر'
    )

    sources = models.JSONField(
        default=list,
        blank=True,
        verbose_name='المصادر',
        help_text='قائمة المصادر المستخدمة في الفحص'
    )

    # بيانات إضافية
    news_article = models.TextField(
        blank=True,
        null=True,
        verbose_name='المقال الإخباري',
        help_text='المقال الإخباري المولد (إن وجد)'
    )

    x_tweet = models.TextField(
        blank=True,
        null=True,
        verbose_name='التغريدة',
        help_text='التغريدة المولدة (إن وجدت)'
    )

    # معلومات التتبع
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='عنوان IP',
        help_text='عنوان IP للمستخدم'
    )

    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name='User Agent',
        help_text='معلومات المتصفح والجهاز'
    )

    # التاريخ والوقت
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='تاريخ الإنشاء',
        db_index=True
    )

    class Meta:
        verbose_name = 'سجل فحص الحقائق'
        verbose_name_plural = 'سجلات فحص الحقائق'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['case']),
            models.Index(fields=['ip_address']),
        ]

    def __str__(self):
        return f"{self.query[:50]}... - {self.get_case_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def sources_count(self):
        """عدد المصادر"""
        return len(self.sources) if self.sources else 0

    @property
    def is_fake(self):
        """هل الخبر كاذب؟"""
        return self.case == 'false'

    @property
    def is_verified(self):
        """هل الخبر موثق؟"""
        return self.case in ['true', 'false', 'mixed']
