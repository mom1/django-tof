# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, JsonResponse


@login_required
def get_generickey_json(request):
    pk = request.GET.get('id', None)
    if not pk:
        raise Http404('id GET parameter')
    model_type = ContentType.objects.get_for_id(pk)
    data = model_type.get_all_objects_for_this_type()
    return JsonResponse([{'pk': d.pk, 'text': str(d)} for d in data], safe=False, content_type='application/json')
