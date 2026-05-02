from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.conf import settings
from .models import StaffMember, Department


def contractors(request):
    qs = StaffMember.objects.filter(
        employee_type='contractor'
    ).prefetch_related('assignments__project__client').order_by('first_name', 'last_name')

    paginator = Paginator(qs, 50)
    page = paginator.get_page(request.GET.get('page'))

    business_names = StaffMember.objects.filter(
        employee_type='contractor',
        contractor_business_name__isnull=False
    ).exclude(contractor_business_name='').values_list('contractor_business_name', flat=True).distinct()

    departments = Department.objects.all().values_list('name', flat=True).order_by('name')

    context = {
        'contractors': page,
        'business_names': business_names,
        'departments': departments,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    return render(request, 'contractors.html', context)


def contractor_map_data(request):
    status_display = dict(StaffMember._meta.get_field('status').choices)
    contractors = StaffMember.objects.filter(
        employee_type='contractor',
        latitude__isnull=False,
        longitude__isnull=False,
    ).values(
        'staff_id', 'first_name', 'last_name', 'status',
        'street', 'city', 'state', 'zip_code',
        'rpr_department__name', 'latitude', 'longitude',
    )
    data = [
        {
            'id': c['staff_id'],
            'name': f"{c['first_name']} {c['last_name']}",
            'status': c['status'],
            'status_display': status_display.get(c['status'], c['status']),
            'address': f"{c['street']}, {c['city']}, {c['state']} {c['zip_code']}",
            'city': c['city'],
            'state': c['state'],
            'department': c['rpr_department__name'] or '',
            'lat': c['latitude'],
            'lng': c['longitude'],
            'detail_url': f"/contractors/{c['staff_id']}/",
        }
        for c in contractors
    ]
    return JsonResponse({'contractors': data})
