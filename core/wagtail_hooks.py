from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from core.models import MinutesLabel, AbbreviationExplanation


class MinutesLabelAdmin(ModelAdmin):
    model = MinutesLabel
    add_to_settings_menu = True


class AbbreviationExplanationAdmin(ModelAdmin):
    model = AbbreviationExplanation
    add_to_settings_menu = True


modeladmin_register(MinutesLabelAdmin)
modeladmin_register(AbbreviationExplanationAdmin)
