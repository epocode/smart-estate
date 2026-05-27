from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Avg, Q

from web.apps.house.models import City, District, PricePrediction, House


def prediction_index(request):
    """房价预测首页"""
    cities = City.objects.all()
    context = {'cities': cities}
    return render(request, 'prediction/index.html', context)


def api_prediction_data(request):
    """获取预测数据 (API)"""
    city_name = request.GET.get('city', '北京')
    district_id = request.GET.get('district', '')

    queryset = PricePrediction.objects.select_related('district__city')

    if city_name:
        queryset = queryset.filter(district__city__name=city_name)
    if district_id:
        queryset = queryset.filter(district_id=district_id)

    predictions = queryset.order_by('predict_date').values(
        'district__name', 'predict_date', 'avg_price', 'trend', 'change_rate', 'confidence'
    )

    return JsonResponse({'data': list(predictions)})


def api_district_trend(request):
    """获取区域历史价格趋势 (API)"""
    district_id = request.GET.get('district', '')

    if not district_id:
        return JsonResponse({'data': []})

    # 获取预测数据作为趋势
    predictions = PricePrediction.objects.filter(
        district_id=district_id
    ).order_by('predict_date').values('predict_date', 'avg_price', 'trend')

    # 获取当前实际均价
    current_avg = House.objects.filter(
        community__district_id=district_id, status=1
    ).aggregate(avg=Avg('unit_price'))['avg']

    return JsonResponse({
        'predictions': list(predictions),
        'current_avg_price': current_avg,
    })
