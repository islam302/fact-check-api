from rest_framework import serializers
from .models import FactCheckHistory


class FactCheckHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for FactCheckHistory model
    """
    case_display = serializers.CharField(source='get_case_display', read_only=True)
    sources_count = serializers.IntegerField(read_only=True)
    is_fake = serializers.BooleanField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = FactCheckHistory
        fields = [
            'id',
            'query',
            'case',
            'case_display',
            'talk',
            'sources',
            'sources_count',
            'news_article',
            'x_tweet',
            'ip_address',
            'user_agent',
            'created_at',
            'is_fake',
            'is_verified',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'case_display',
            'sources_count',
            'is_fake',
            'is_verified',
        ]


class FactCheckHistoryListSerializer(serializers.ModelSerializer):
    """
    Lighter serializer for list views
    """
    query_preview = serializers.SerializerMethodField()

    class Meta:
        model = FactCheckHistory
        fields = [
            'id',
            'query_preview',
            'case',
            'talk',
        ]

    def get_query_preview(self, obj):
        """Return first 100 characters of query"""
        if len(obj.query) > 100:
            return f"{obj.query[:100]}..."
        return obj.query


class StatisticsSerializer(serializers.Serializer):
    """
    Serializer for dashboard statistics
    """
    total_checks = serializers.IntegerField()
    today_checks = serializers.IntegerField()
    yesterday_checks = serializers.IntegerField()
    last_7_days = serializers.IntegerField()
    last_30_days = serializers.IntegerField()

    true_count = serializers.IntegerField()
    false_count = serializers.IntegerField()
    mixed_count = serializers.IntegerField()
    unverified_count = serializers.IntegerField()

    true_percentage = serializers.FloatField()
    false_percentage = serializers.FloatField()
    mixed_percentage = serializers.FloatField()
    unverified_percentage = serializers.FloatField()

    top_queries = serializers.ListField()
    recent_checks = FactCheckHistoryListSerializer(many=True)
