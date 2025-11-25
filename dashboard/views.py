from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import FactCheckHistory
from .serializers import (
    FactCheckHistorySerializer,
    FactCheckHistoryListSerializer,
    StatisticsSerializer
)


class FactCheckHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing fact check history
    Requires admin authentication
    """
    queryset = FactCheckHistory.objects.all()
    permission_classes = [AllowAny]
    pagination_class = None  # Disable pagination
    filterset_fields = ['case', 'created_at']
    search_fields = ['query', 'talk', 'ip_address']
    ordering_fields = ['created_at', 'case']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Use lighter serializer for list view"""
        if self.action == 'list':
            return FactCheckHistoryListSerializer
        return FactCheckHistorySerializer

    def get_queryset(self):
        """
        Filter queryset based on query parameters
        """
        queryset = super().get_queryset()

        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # Filter by case
        case = self.request.query_params.get('case', None)
        if case:
            queryset = queryset.filter(case=case)

        return queryset

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get comprehensive statistics
        Endpoint: /api/admin/fact-checks/statistics/
        """
        now = timezone.now()
        today = now.date()
        yesterday = today - timedelta(days=1)

        # Count checks
        total_checks = FactCheckHistory.objects.count()
        today_checks = FactCheckHistory.objects.filter(
            created_at__date=today
        ).count()
        yesterday_checks = FactCheckHistory.objects.filter(
            created_at__date=yesterday
        ).count()
        last_7_days = FactCheckHistory.objects.filter(
            created_at__gte=now - timedelta(days=7)
        ).count()
        last_30_days = FactCheckHistory.objects.filter(
            created_at__gte=now - timedelta(days=30)
        ).count()

        # Count by case
        stats = FactCheckHistory.objects.aggregate(
            true_count=Count('id', filter=Q(case='true')),
            false_count=Count('id', filter=Q(case='false')),
            mixed_count=Count('id', filter=Q(case='mixed')),
            unverified_count=Count('id', filter=Q(case='unverified')),
        )

        # Calculate percentages
        true_percentage = (stats['true_count'] / total_checks * 100) if total_checks > 0 else 0
        false_percentage = (stats['false_count'] / total_checks * 100) if total_checks > 0 else 0
        mixed_percentage = (stats['mixed_count'] / total_checks * 100) if total_checks > 0 else 0
        unverified_percentage = (stats['unverified_count'] / total_checks * 100) if total_checks > 0 else 0

        # Top queries (most recent 10)
        top_queries = FactCheckHistory.objects.values(
            'query', 'case', 'created_at'
        ).order_by('-created_at')[:10]

        # Recent checks (last 5)
        recent_checks = FactCheckHistory.objects.all().order_by('-created_at')[:5]

        data = {
            'total_checks': total_checks,
            'today_checks': today_checks,
            'yesterday_checks': yesterday_checks,
            'last_7_days': last_7_days,
            'last_30_days': last_30_days,
            'true_count': stats['true_count'],
            'false_count': stats['false_count'],
            'mixed_count': stats['mixed_count'],
            'unverified_count': stats['unverified_count'],
            'true_percentage': round(true_percentage, 2),
            'false_percentage': round(false_percentage, 2),
            'mixed_percentage': round(mixed_percentage, 2),
            'unverified_percentage': round(unverified_percentage, 2),
            'top_queries': list(top_queries),
            'recent_checks': FactCheckHistoryListSerializer(recent_checks, many=True).data,
        }

        serializer = StatisticsSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export fact checks to CSV
        Endpoint: /api/admin/fact-checks/export/
        """
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="fact_checks.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'النص', 'النتيجة', 'التحليل', 'عدد المصادر', 'IP', 'التاريخ'])

        queryset = self.get_queryset()
        for obj in queryset:
            writer.writerow([
                obj.id,
                obj.query,
                obj.get_case_display(),
                obj.talk[:200],  # First 200 chars of analysis
                obj.sources_count,
                obj.ip_address,
                obj.created_at.strftime('%Y-%m-%d %H:%M')
            ])

        return response

    @action(detail=True, methods=['patch'])
    def update_case(self, request, pk=None):
        """
        Update only the case field
        Endpoint: /api/admin/fact-checks/{id}/update_case/
        """
        fact_check = self.get_object()
        new_case = request.data.get('case')

        if new_case not in ['true', 'false', 'mixed', 'unverified']:
            return Response(
                {'error': 'Invalid case value'},
                status=status.HTTP_400_BAD_REQUEST
            )

        fact_check.case = new_case
        fact_check.save()

        serializer = self.get_serializer(fact_check)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        """
        Delete all fact check history records
        Endpoint: /api/admin/fact-checks/delete_all/
        """
        count = FactCheckHistory.objects.count()
        FactCheckHistory.objects.all().delete()

        return Response(
            {
                'message': f'Successfully deleted {count} fact check records',
                'deleted_count': count
            },
            status=status.HTTP_200_OK
        )
