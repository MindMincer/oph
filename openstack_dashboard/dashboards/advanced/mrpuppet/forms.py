from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms

from openstack_dashboard import api


class UpdateMetadata(forms.SelfHandlingForm):
    # instance_id = forms.CharField(label=_("Instance ID"),
    #                               widget=forms.HiddenInput(),
    #                               required=False)
    # name = forms.CharField(max_length=255, label=_("Custom action"))


    def __init__(self, *args, **kwargs):
        super(UpdateMetadata, self).__init__(*args, **kwargs)
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
            return True
        except Exception:
            exceptions.handle(request,
                              _('Unable to update metadata.'))

class AddMetadata(forms.SelfHandlingForm):
    instance_id = forms.CharField(label=_("Instance ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)
    name = forms.CharField(max_length=255, label=_("Metadata Name"),
                                  required=True)
    value = forms.CharField(max_length=255, label=_("Metadata Value"),
                                  required=True)

    def handle(self, request, data):
        try:
            instance_id = data['instance_id']
            server = api.nova.server_get(self.request, instance_id).to_dict()
            metadatas = server['metadata']
            metadatas.update({data['name']:data['value']})
            api.nova.server_metadata_update(self.request, instance_id, metadatas)
            return True
        except Exception:
            exceptions.handle(request,
                              _('Unable to add metadata.'))