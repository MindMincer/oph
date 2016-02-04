from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms

from openstack_dashboard import api


class ApplyAction(forms.SelfHandlingForm):
    # instance_id = forms.CharField(label=_("Instance ID"),
    #                               widget=forms.HiddenInput(),
    #                               required=False)
    # name = forms.CharField(max_length=255, label=_("Custom action"))


    def __init__(self, *args, **kwargs):
        super(ApplyAction, self).__init__(*args, **kwargs)
        instance_id = kwargs.get('initial', {}).get('instance_id')
        # self.fields['instance_id'].initial = instance_id
        metadatas = api.nova.server_get(self.request, instance_id).to_dict()
        for key, value in metadatas['metadata']:
            self.fields[key] = forms.CharField(label=key)
            self.fields[key].required = True
            self.fields[key].help_text = key
            self.fields[key].initial = value

    def handle(self, request, data):
        try:
            snapshot = api.nova.snapshot_create(request,
                                                data['instance_id'],
                                                data['name'])
            return snapshot
        except Exception:
            exceptions.handle(request,
                              _('Unable to create snapshot.'))