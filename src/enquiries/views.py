from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from counter.services import is_owner_visit, is_same_origin, today_in_da_nang
from enquiries.forms import EnquiryForm
from enquiries.services import Outcome, is_trapped, store_enquiry
from pages import language
from pages.views import render_home


class SeeOther(HttpResponseRedirect):
    """303: the browser follows it with a GET (Django 5.2 has no HttpResponseSeeOther)."""

    status_code = 303


def _sent(lang: str) -> HttpResponse:
    return SeeOther(language.home_path(lang) + "?enquiry=sent#enquiry")


# The visitor has no cookie and no token: the Origin check replaces CSRF, as for /count/.
@csrf_exempt
@require_POST
def enquiry(request: HttpRequest) -> HttpResponse:
    if not is_same_origin(request):
        return HttpResponse(status=403)
    lang = language.of_request(request)
    form = EnquiryForm(request.POST, language=lang, today=today_in_da_nang())
    valid = form.is_valid()
    if is_trapped(form):
        return _sent(lang)
    if not valid:
        return render_home(request, enquiry_form=form, enquiry_state="errors", status=400)
    outcome = store_enquiry(
        form, language=lang, from_owner=is_owner_visit(request), now=timezone.now()
    )
    if outcome is Outcome.PAUSED:
        return render_home(request, enquiry_state="paused", status=429)
    return _sent(lang)
