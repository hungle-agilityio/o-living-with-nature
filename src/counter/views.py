from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from counter.forms import CountForm
from counter.services import is_owner_visit, is_same_origin, record_count


# The visitor has no cookie and no token: the Origin check replaces CSRF.
@csrf_exempt
@require_POST
def count(request: HttpRequest) -> HttpResponse:
    if not is_same_origin(request):
        return HttpResponse(status=403)
    form = CountForm(request.POST)
    if not form.is_valid():
        return HttpResponse(status=400)
    if not is_owner_visit(request):
        record_count(
            kind=form.cleaned_data["kind"],
            channel=form.cleaned_data["channel"],
            place=form.cleaned_data["place"],
        )
    return HttpResponse(status=204)
