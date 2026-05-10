from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse, Http404
from django.conf import settings
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from .models import StaffMember, Department, ContractorFile
from . import bucket_storage


def contractors(request):
    qs = StaffMember.objects.filter(
        employee_type='contractor'
    ).prefetch_related('assignments__project__client').order_by('first_name', 'last_name')

    business_names = StaffMember.objects.filter(
        employee_type='contractor',
        contractor_business_name__isnull=False
    ).exclude(contractor_business_name='').values_list('contractor_business_name', flat=True).distinct()

    departments = Department.objects.all().order_by('name')

    context = {
        'contractors': qs,
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


def add_contractor(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        dept_id = request.POST.get('rpr_department') or None
        dept = Department.objects.get(pk=dept_id) if dept_id else None
        contractor = StaffMember.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            personal_email=request.POST['personal_email'],
            phone_number=request.POST['phone_number'],
            street=request.POST['street'],
            city=request.POST['city'],
            state=request.POST['state'],
            zip_code=request.POST['zip_code'],
            title=request.POST.get('title') or None,
            status=request.POST.get('status', 'active'),
            employee_type='contractor',
            contractor_business_name=request.POST.get('contractor_business_name') or None,
            rpr_department=dept,
            date_of_joining=request.POST.get('date_of_joining') or None,
            contract_status=request.POST.get('contract_status', 'active'),
        )
        return JsonResponse({'success': True, 'id': contractor.staff_id})
    except IntegrityError:
        return JsonResponse({'success': False, 'error': 'A contractor with that email already exists.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def contractor_detail(request, staff_id):
    contractor = get_object_or_404(StaffMember, pk=staff_id)
    assignments = contractor.assignments.select_related('project__client').all()
    files = contractor.files.all()
    return render(request, 'contractor_detail.html', {
        'contractor': contractor,
        'assignments': assignments,
        'pay_rates': [],
        'files': files,
    })


def upload_contractor_file(request, staff_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    contractor = get_object_or_404(StaffMember, pk=staff_id)
    file_obj = request.FILES.get('file')
    if not file_obj:
        return JsonResponse({'success': False, 'error': 'No file provided.'}, status=400)
    try:
        object_key, mime_type = bucket_storage.upload_file(contractor, file_obj)
        doc = ContractorFile.objects.create(
            staff_member=contractor,
            original_name=file_obj.name,
            object_key=object_key,
            content_type=mime_type,
            file_size=file_obj.size,
        )
        return JsonResponse({'success': True, 'id': doc.id, 'name': doc.original_name})
    except ValidationError as e:
        return JsonResponse({'success': False, 'error': e.message}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def download_contractor_file(request, file_id):
    doc = get_object_or_404(ContractorFile, pk=file_id)
    try:
        body, content_type, content_length = bucket_storage.stream_download(doc.object_key)
    except Exception:
        raise Http404
    response = StreamingHttpResponse(body.iter_chunks(), content_type=content_type)
    response['Content-Length'] = content_length
    response['Content-Disposition'] = f'inline; filename="{doc.original_name}"'
    return response


@require_POST
def delete_contractor_file(request, file_id):
    doc = get_object_or_404(ContractorFile, pk=file_id)
    try:
        bucket_storage.delete_file(doc.object_key)
        doc.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
