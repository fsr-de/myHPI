from django.core.exceptions import ValidationError
from django.forms import Form, ChoiceField


class RankedChoiceBallotForm(Form):
    def __init__(self, *args, options=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = options
        for option in self.options:
            self.fields[f"option_{option.pk}"] = ChoiceField(
                choices=[("unranked", "unranked")] + [(i, i) for i in range(1, len(self.options) + 1)],
                label=option.name, help_text=option.description)

    def clean(self):
        cleaned_data = super().clean()
        unranked = []
        ranks = []
        for key, rank in cleaned_data.items():
            if rank == "unranked":
                unranked.append(key)
            elif int(rank) not in range(1, len(self.options) + 1):
                raise ValidationError("Invalid rank.")
            else:
                ranks.append(rank)
        if len(ranks) != len(set(ranks)):
            raise ValidationError("All ranks must be unique.")
        for key in unranked:
            del cleaned_data[key]
        return cleaned_data
