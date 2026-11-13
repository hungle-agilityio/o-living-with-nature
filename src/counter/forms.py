"""The fields of one count, checked before anything is stored."""

from typing import Any

from django import forms

from counter.models import DailyCount


class CountForm(forms.Form):
    kind = forms.ChoiceField(choices=DailyCount.Kind.choices)
    channel = forms.ChoiceField(choices=DailyCount.Channel.choices, required=False)
    place = forms.ChoiceField(choices=DailyCount.Place.choices, required=False)

    def clean(self) -> dict[str, Any]:
        cleaned = super().clean() or {}
        kind = cleaned.get("kind")
        channel = cleaned.get("channel", "")
        place = cleaned.get("place", "")
        if kind == DailyCount.Kind.VIEW and (channel or place):
            raise forms.ValidationError("A view has no channel and no place.")
        if kind == DailyCount.Kind.CLICK and not (channel and place):
            raise forms.ValidationError("A click needs a channel and a place.")
        return cleaned
