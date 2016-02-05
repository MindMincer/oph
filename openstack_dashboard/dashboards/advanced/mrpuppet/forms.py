from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms

from openstack_dashboard import api


class UpdateMetadata(forms.SelfHandlingForm):
    instance_id = forms.CharField(label=_("Instance ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)

    def __init__(self, *args, **kwargs):
        super(UpdateMetadata, self).__init__(*args, **kwargs)
        instance_id = kwargs.get('initial', {}).get('instance_id')
        # self.fields['instance_id'].initial = instance_id
        metadatas = api.nova.server_get(self.request, instance_id).to_dict()
        for key, value in metadatas['metadata'].items():
            self.fields[key] = forms.CharField(label=key)
            self.fields[key].required = True
            self.fields[key].help_text = key
            self.fields[key].initial = value

    def handle(self, request, data):
        try:
            instance_id = data['instance_id']
            server = api.nova.server_get(self.request, instance_id).to_dict()
            metadatas = server['metadata']
            for key, value in metadatas.items():
                metadatas.update({key:data[key]})
            api.nova.server_metadata_update(self.request, instance_id, metadatas)
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
            ### TODO : check if exist
            instance_id = data['instance_id']
            server = api.nova.server_get(self.request, instance_id).to_dict()
            metadatas = server['metadata']
            metadatas.update({data['name']:data['value']})
            api.nova.server_metadata_update(self.request, instance_id, metadatas)
            return True
        except Exception:
            exceptions.handle(request,
                              _('Unable to add metadata.'))


class AddENCMetadata(forms.SelfHandlingForm):
    instance_id = forms.CharField(label=_("Instance ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)
    attributes = {'class': 'switchable', 'data-slug': 'classessource'}
    classes = forms.ChoiceField(label=_('New Class'), help_text=_("Choose a Class to add."),
                                      widget=forms.Select(attrs=attributes),
                                      required=False)

    def __init__(self, request, *args, **kwargs):
        super(AddENCMetadata, self).__init__(request, *args, **kwargs)
        initial = kwargs.get('initial', {})
        instance_id = initial.get('instance_id')
        self.fields['instance_id'] = forms.CharField(widget=forms.HiddenInput,
                                                     initial=instance_id)
        self.fields['classes'].choices = self.populate_classes_choices()

        classes = self.populate_args_choices()#{"class1":4, "class2":6, "class3":2}
        for the_class, count in classes.items():
            for i in xrange(count):
                self.fields[the_class+"{}".format(i)] = forms.CharField(label=the_class)
                self.fields[the_class+"{}".format(i)].required = True
                self.fields[the_class+"{}".format(i)].help_text = the_class
                self.fields[the_class+"{}".format(i)].initial = the_class + "param" + "{}".format(i)
                self.fields[the_class+"{}".format(i)].widget.attrs = {'class': 'switched',
                                                        'data-switch-on': 'classessource',
                                                        'data-classessource-' + the_class: _('Classes Data')}

    def populate_classes_choices(self):
        classes_list = ['', _('Select Metadata Class'), ("class1","meta class 1"), ("class2","meta class 2"), ("class3","meta class 3")]
        return sorted(classes_list)

    def populate_args_choices(self):
        args_choices = {"class1":{""}},
                        "class2":6,
                        "class3":2}
        return args_choices

    def handle(self, request, data):
        try:
            ### TODO : check if exist
            # instance_id = data['instance_id']
            # server = api.nova.server_get(self.request, instance_id).to_dict()
            # metadatas = server['metadata']
            # metadatas.update({data['name']:data['value']})
            # api.nova.server_metadata_update(self.request, instance_id, metadatas)
            return True
        except Exception:
            exceptions.handle(request,
                              _('Unable to add metadata.'))