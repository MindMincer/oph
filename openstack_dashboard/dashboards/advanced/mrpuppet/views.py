# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import tabs
from horizon import exceptions
from horizon import forms

from horizon.utils import memoized

from openstack_dashboard import api

from openstack_dashboard.dashboards.advanced.mrpuppet \
    import forms as project_forms

from openstack_dashboard.dashboards.advanced.mrpuppet \
    import tabs as advanced_tabs


class IndexView(tabs.TabbedTableView):
    tab_group_class = advanced_tabs.AdvancedTabs
    # A very simple class-based view...
    template_name = 'advanced/mrpuppet/index.html'

    def get_data(self, request, context, *args, **kwargs):
        # Add data to the context here...
        return context


class ApplyActionView(forms.ModalFormView):
    form_class = project_forms.ApplyAction
    template_name = 'advanced/mrpuppet/apply_action.html'
    success_url = reverse_lazy("horizon:advanced:mrpuppet:index")
    modal_id = "apply_action_modal"
    modal_header = _("Apply Action")
    submit_label = _("Apply Action")
    submit_url = "horizon:advanced:mrpuppet:apply_action"

    @memoized.memoized_method
    def get_object(self):
        try:
            return api.nova.server_get(self.request,
                                       self.kwargs["instance_id"])
        except Exception:
            exceptions.handle(self.request,
                              _("Unable to retrieve instance."))

    def get_initial(self):
        return {"instance_id": self.kwargs["instance_id"]}

    def get_context_data(self, **kwargs):
        context = super(ApplyActionView, self).get_context_data(**kwargs)
        instance_id = self.kwargs['instance_id']
        context['instance_id'] = instance_id
        context['instance'] = self.get_object()
        context['submit_url'] = reverse(self.submit_url, args=[instance_id])
        return context