from collections import OrderedDict
from operator import itemgetter
from allauth.account.admin import EmailAddressAdmin
from allauth.account.models import EmailAddress
from allauth.socialaccount.admin import (
    SocialAccountAdmin,
    SocialAppAdmin,
    SocialTokenAdmin,
)
from allauth.socialaccount.models import (
    SocialAccount,
    SocialApp,
    SocialToken,
)
from constance import settings as django_constance_settings
from constance.admin import Config, ConstanceAdmin
from constance.utils import get_values
from django_celery_beat.models import (
    ClockedSchedule,
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    SolarSchedule,
)
from django_celery_beat.admin import ClockedScheduleAdmin as BaseClockedScheduleAdmin
from django_celery_beat.admin import CrontabScheduleAdmin as BaseCrontabScheduleAdmin
from django_celery_beat.admin import PeriodicTaskAdmin as BasePeriodicTaskAdmin
from django_celery_beat.admin import PeriodicTaskForm, TaskSelectWidget
from django_celery_results.admin import GroupResultAdmin, TaskResultAdmin
from django_celery_results.models import GroupResult, TaskResult
from oauth2_provider.admin import (
    AccessTokenAdmin,
    ApplicationAdmin,
    GrantAdmin,
    IDTokenAdmin,
    RefreshTokenAdmin,
)
from oauth2_provider.models import (
    AccessToken,
    Application,
    Grant,
    IDToken,
    RefreshToken,
)
from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authtoken.models import TokenProxy
from rest_framework_simplejwt.token_blacklist.admin import (
    BlacklistedTokenAdmin,
    OutstandingTokenAdmin,
)
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from unfold.admin import ModelAdmin
from unfold.widgets import (
    UnfoldAdminSelectWidget,
    UnfoldAdminSplitDateTimeWidget,
    UnfoldAdminTextInputWidget,
    UnfoldBooleanWidget,
)

from django import get_version
from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from django.contrib.sites.models import Site
from django.contrib.sites.admin import SiteAdmin
from django.contrib.admin.options import csrf_protect_m
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
class UnfoldTaskSelectWidget(UnfoldAdminSelectWidget, TaskSelectWidget):
    pass

class UnfoldTokenAdmin(TokenAdmin, ModelAdmin):
    pass

class UnfoldPeriodicTaskForm(PeriodicTaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["task"].widget = UnfoldAdminTextInputWidget()
        self.fields["regtask"].widget = UnfoldTaskSelectWidget()

class CustomConstanceAdmin(ConstanceAdmin):
    @csrf_protect_m
    def changelist_view(self, request, context=None):
        # copied code from constance admin
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied
        initial = get_values()
        form_cls = self.get_changelist_form(request)
        form = form_cls(initial=initial, request=request)
        if request.method == "POST" and request.user.has_perm(
            "constance.change_config"
        ):
            form = form_cls(
                data=request.POST, files=request.FILES, initial=initial, request=request
            )
            if form.is_valid():
                form.save()
                messages.add_message(
                    request, messages.SUCCESS, _("Live settings updated successfully.")
                )
                return HttpResponseRedirect(".")
            messages.add_message(
                request, messages.ERROR, _("Failed to update live settings.")
            )
        context = dict(
            self.admin_site.each_context(request),
            config_values=[],
            title=self.model._meta.app_config.verbose_name,
            app_label="constance",
            opts=self.model._meta,
            form=form,
            media=self.media + form.media,
            icon_type="svg",
            django_version=get_version(),
        )
        for name, options in django_constance_settings.CONFIG.items():
            context["config_values"].append(
                self.get_config_value(name, options, form, initial)
            )

        if django_constance_settings.CONFIG_FIELDSETS:
            if isinstance(django_constance_settings.CONFIG_FIELDSETS, dict):
                fieldset_items = django_constance_settings.CONFIG_FIELDSETS.items()
            else:
                fieldset_items = django_constance_settings.CONFIG_FIELDSETS

            context["fieldsets"] = []
            for fieldset_title, fieldset_data in fieldset_items:
                if isinstance(fieldset_data, dict):
                    fields_list = fieldset_data["fields"]
                    collapse = fieldset_data.get("collapse", False)
                else:
                    fields_list = fieldset_data
                    collapse = False

                absent_fields = [
                    field
                    for field in fields_list
                    if field not in django_constance_settings.CONFIG
                ]
                if any(absent_fields):
                    raise ValueError(
                        "CONSTANCE_CONFIG_FIELDSETS contains field(s) that does not exist(s): {}".format(
                            ", ".join(absent_fields)
                        )
                    )

                config_values = []

                for name in fields_list:
                    options = django_constance_settings.CONFIG.get(name)
                    if options:
                        config_values.append(
                            self.get_config_value(name, options, form, initial)
                        )
                fieldset_context = {
                    "title": fieldset_title,
                    "config_values": config_values,
                }

                if collapse:
                    fieldset_context["collapse"] = True
                context["fieldsets"].append(fieldset_context)
            if not isinstance(
                django_constance_settings.CONFIG_FIELDSETS, (OrderedDict, tuple)
            ):
                context["fieldsets"].sort(key=itemgetter("title"))

        if not isinstance(django_constance_settings.CONFIG, OrderedDict):
            context["config_values"].sort(key=itemgetter("name"))
        request.current_app = self.admin_site.name

        # Custom code - update form field widgets based on configuration options.
        for config_value in context.get("config_values"):
            if config_value.get("is_checkbox"):
                config_value.get("form_field").field.widget = UnfoldBooleanWidget()
            elif config_value.get("is_datetime"):
                config_value.get("form_field").field.widget = (
                    UnfoldAdminSplitDateTimeWidget()
                )
            else:
                config_value.get("form_field").field.widget = (
                    UnfoldAdminTextInputWidget()
                )

        return TemplateResponse(request, self.change_list_template, context)

MODELS_TO_UNREGISTER = {
    "base": [[Config], Group, Site],
    "drf": [SocialAccount, SocialToken, SocialApp],
    "drf_auth_token": [TokenProxy],
    "simplejwt": [BlacklistedToken, OutstandingToken],
    "celery": [
        PeriodicTask,
        IntervalSchedule,
        CrontabSchedule,
        SolarSchedule,
        ClockedSchedule,
    ],
    "celery_results": [TaskResult, GroupResult],
    "oauth": [Application, AccessToken, RefreshToken, Grant, IDToken],
    "accounts": [EmailAddress],
}

MODEL_ADMIN_MAPPING = {
    "base": {
        Group: GroupAdmin,
        Site: SiteAdmin,
        "config": (Config, CustomConstanceAdmin),
    },
    "drf": {
        SocialAccount: SocialAccountAdmin,
        SocialToken: SocialTokenAdmin,
        SocialApp: SocialAppAdmin,
    },
     "simplejwt": {
        BlacklistedToken: (BlacklistedTokenAdmin, ModelAdmin),
        OutstandingToken: (OutstandingTokenAdmin, ModelAdmin),
    },
    "celery": {
        PeriodicTask: (
            BasePeriodicTaskAdmin,
            ModelAdmin,
            {"form": UnfoldPeriodicTaskForm},
        ),
        TokenProxy: UnfoldTokenAdmin,
        IntervalSchedule: (ModelAdmin, None),
        CrontabSchedule: (BaseCrontabScheduleAdmin, ModelAdmin),
        SolarSchedule: (ModelAdmin, None),
        ClockedSchedule: (BaseClockedScheduleAdmin, ModelAdmin),
    },
    "celery_results": {
        TaskResult: (TaskResultAdmin, ModelAdmin),
        GroupResult: (GroupResultAdmin, ModelAdmin),
    },
    "oauth": {
        Application: (ApplicationAdmin, ModelAdmin),
        AccessToken: (AccessTokenAdmin, ModelAdmin),
        RefreshToken: (RefreshTokenAdmin, ModelAdmin),
        Grant: (GrantAdmin, ModelAdmin),
        IDToken: (IDTokenAdmin, ModelAdmin),
    },
    "accounts": {
        EmailAddress: (EmailAddressAdmin, ModelAdmin),
    },
}

def register_with_unfold():
    # Initially unregister all 3rd party models
    for category, models in MODELS_TO_UNREGISTER.items():
        for model in models:
            # Handle both list and non-list models
            if isinstance(model, list):
                admin.site.unregister(model)
            else:
                admin.site.unregister([model])

    for category, mappings in MODEL_ADMIN_MAPPING.items():
        for model, config in mappings.items():
            if model == "config":
                admin.site.register([config[0]], config[1])
            elif isinstance(config, tuple):
                base_admin, unfold_admin, extra_attrs = (
                    config + (None,) if len(config) == 2 else config
                )
                attrs = extra_attrs or {}
                admin_class = type(
                    f"Unfold{model.__name__}Admin",
                    (base_admin, unfold_admin) if unfold_admin else (base_admin,),
                    attrs,
                )
                admin.site.register(model, admin_class)
            else:
                admin_class = type(
                    f"Unfold{model.__name__}Admin", (config, ModelAdmin), {}
                )
                admin.site.register(model, admin_class)


register_with_unfold()
