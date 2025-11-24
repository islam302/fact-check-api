# Generated manually to convert id from integer to UUID

from django.db import migrations, models
from django.utils import timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        # Drop the old table using IF EXISTS
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS dashboard_factcheckhistory CASCADE;',
            reverse_sql='',
        ),

        # Create the new model with UUID (no need to delete since we dropped the table)
        migrations.CreateModel(
            name='FactCheckHistory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('query', models.TextField(help_text='النص أو العنوان الذي تم فحصه', verbose_name='النص/العنوان المُدخل')),
                ('case', models.CharField(choices=[('true', 'حقيقي'), ('false', 'كاذب'), ('mixed', 'غير مؤكد/مختلط'), ('unverified', 'غير موثق')], help_text='نتيجة الفحص: حقيقي، كاذب، مختلط، أو غير موثق', max_length=20, verbose_name='النتيجة')),
                ('talk', models.TextField(help_text='التحليل الكامل للخبر', verbose_name='التحليل')),
                ('sources', models.JSONField(blank=True, default=list, help_text='قائمة المصادر المستخدمة في الفحص', verbose_name='المصادر')),
                ('news_article', models.TextField(blank=True, help_text='المقال الإخباري المولد (إن وجد)', null=True, verbose_name='المقال الإخباري')),
                ('x_tweet', models.TextField(blank=True, help_text='التغريدة المولدة (إن وجدت)', null=True, verbose_name='التغريدة')),
                ('ip_address', models.GenericIPAddressField(blank=True, help_text='عنوان IP للمستخدم', null=True, verbose_name='عنوان IP')),
                ('user_agent', models.TextField(blank=True, help_text='معلومات المتصفح والجهاز', null=True, verbose_name='User Agent')),
                ('created_at', models.DateTimeField(db_index=True, default=timezone.now, verbose_name='تاريخ الإنشاء')),
            ],
            options={
                'verbose_name': 'سجل فحص الحقائق',
                'verbose_name_plural': 'سجلات فحص الحقائق',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['-created_at'], name='dashboard_f_created_538c3e_idx'),
                    models.Index(fields=['case'], name='dashboard_f_case_f87e29_idx'),
                    models.Index(fields=['ip_address'], name='dashboard_f_ip_addr_b8e0b5_idx'),
                ],
            },
        ),
    ]
