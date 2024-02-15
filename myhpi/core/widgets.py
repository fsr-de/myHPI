from json import loads as parse_json

from django import forms
from wagtail.documents.models import Document


class AttachmentSelectWidget(forms.SelectMultiple):
    allow_multiple_selected = True
    current_user = None

    def __init__(self, attrs=None, choices=(), user=None):
        if user:
            self.current_user = user
        super().__init__(attrs, choices)

    def optgroups(self, name, value, attrs=None):
        """Return a list of optgroups for this widget."""
        groups = []
        has_selected = False

        attachments = []
        for option_value, option_label in self.choices:
            if not self.current_user:
                attachments.append((option_value, option_label))
            else:
                document = Document.objects.get(id=option_value.value)
                if document.is_editable_by_user(user=self.current_user):
                    attachments.append((option_value, option_label))

        for index, (option_value, option_label) in enumerate(attachments):
            if option_value is None:
                option_value = ""

            subgroup = []
            if isinstance(option_label, (list, tuple)):
                group_name = option_value
                subindex = 0
                choices = option_label
            else:
                group_name = None
                subindex = None
                choices = [(option_value, option_label)]
            groups.append((group_name, subgroup, index))

            for subvalue, sublabel in choices:
                selected = (not has_selected or self.allow_multiple_selected) and str(
                    subvalue
                ) in value
                has_selected |= selected
                subgroup.append(
                    self.create_option(
                        name,
                        subvalue,
                        sublabel,
                        selected,
                        index,
                        subindex=subindex,
                        attrs=attrs,
                    )
                )
                if subindex is not None:
                    subindex += 1
        return groups


class TextArrayWidget(forms.Widget):
    template_name = "core/text_array_widget.html"

    class Media:
        css = {"all": ["css/text_array_widget.css"]}
        js = ["js/admin/text_array_widget.js"]

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["strings"] = parse_json(context["widget"]["value"])
        return context
