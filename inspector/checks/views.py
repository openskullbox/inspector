from bootstrap_modal_forms.mixins import PassRequestMixin, DeleteAjaxMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, FormView
from django_filters.views import BaseFilterView

from inspector.taskapp.tasks import execute_check
from .constants import STATUSES
from .filters import CheckRunFilter
from .forms import DatacheckRunForm, CheckGroupForm, DatacheckForm, CheckGroupRunForm
from .models import Datacheck, CheckGroup, CheckRun, EnvironmentStatus
from .service import CheckRunService


class CheckListView(ListView):
    model = Datacheck
    slug_field = "code"
    slug_url_kwarg = "code"


check_list_view = CheckListView.as_view()


class DatacheckDetailView(DetailView):
    model = Datacheck
    template_name = 'checks/datacheck_detail.html'


check_detail_view = DatacheckDetailView.as_view()


class DatacheckRunView(PassRequestMixin, SuccessMessageMixin,
                       CreateView):
    template_name = 'components/modals_run.html'
    form_class = DatacheckRunForm
    success_message = 'Success: Check was triggered.'
    success_url = reverse_lazy('checks_datacheck_list')

    def form_valid(self, form):
        form.instance.datacheck_id = self.kwargs['pk']
        form.instance.user = self.request.user
        form.instance.status = STATUSES.NEW
        # TODO - check if system is available in environment

        return super().form_valid(form)

    def get_success_url(self):
        if not self.request.is_ajax():
            execute_check.delay(self.object.id)
        return super().get_success_url()


datacheck_run_view = DatacheckRunView.as_view()


class CheckGroupRunView(PassRequestMixin, SuccessMessageMixin, FormView):
    template_name = 'components/modals_run.html'
    form_class = CheckGroupRunForm
    success_message = 'Success: Check group was triggered.'
    success_url = reverse_lazy('checks_checkgroup_list')

    def form_valid(self, form):
        if not self.request.is_ajax():
            CheckRunService.run_check_group(
                self.kwargs['pk'],
                form.instance.environment,
                self.request.user)

        return super().form_valid(form)


class DatacheckDeleteView(DeleteAjaxMixin, DeleteView):
    model = Datacheck
    template_name = 'components/modals_delete.html'
    success_message = 'Success: Check was deleted.'
    success_url = reverse_lazy('checks_datacheck_list')


check_delete_view = DatacheckDeleteView.as_view()


class CheckGroupListView(ListView):
    model = CheckGroup


class CheckGroupCreateView(CreateView):
    model = CheckGroup
    form_class = CheckGroupForm

    def get_success_url(self):
        return reverse('checks_checkgroup_list')


class CheckGroupUpdateView(UpdateView):
    model = CheckGroup
    form_class = CheckGroupForm

    def get_success_url(self):
        return reverse('checks_checkgroup_list')


class CheckRunListView(BaseFilterView, ListView):
    model = CheckRun
    paginate_by = 50
    filterset_class = CheckRunFilter

    def get_paginate_by(self, queryset):
        """
        Paginate by specified value in querystring, or use default class property value.
        """
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_queryset(self):
        qs = CheckRun.objects.select_related()
        qs_filtered_list = CheckRunFilter(self.request.GET, queryset=qs)

        return qs_filtered_list.qs


class CheckRunDetailView(DetailView):
    model = CheckRun


class DatacheckCreateView(CreateView):
    model = Datacheck
    form_class = DatacheckForm

    def get_success_url(self):
        return reverse('checks_datacheck_list')


class DatacheckUpdateView(UpdateView):
    model = Datacheck
    form_class = DatacheckForm

    def get_success_url(self):
        return reverse('checks_datacheck_list')


class EnvironmentStatusListView(ListView):
    model = EnvironmentStatus


class CheckGroupDeleteView(DeleteAjaxMixin, DeleteView):
    model = CheckGroup
    template_name = 'components/modals_delete.html'
    success_message = 'Success: Check group was deleted.'
    success_url = reverse_lazy('checks_checkgroup_list')


class DatacheckInfoView(DetailView):
    model = Datacheck
    template_name = 'checks/datacheck_info.html'