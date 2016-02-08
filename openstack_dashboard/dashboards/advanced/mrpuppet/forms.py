from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from openstack_dashboard.utils import filters

from openstack_dashboard import api

import simplejson as json
# import pyyaml
from django.utils.html import escape, mark_safe

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


# class UpdateENCMetadata(forms.SelfHandlingForm):
#     instance_id = forms.CharField(label=_("Instance ID"),
#                                   widget=forms.HiddenInput(),
#                                   required=False)

    

#     def populate_params_of_the_class(self, class_name):
#         classes = AddENCMetadata.populate_args_choices(self, self.instance_id)
#         return classes[class_name]

#     def __init__(self, request, *args, **kwargs):
#         super(UpdateENCMetadata, self).__init__(request, *args, **kwargs)
#         initial = kwargs.get('initial', {})
#         instance_id = initial.get('instance_id')
#         self.fields['instance_id'] = forms.CharField(widget=forms.HiddenInput,
#                                                      initial=instance_id)
#         class_name = "class1"
#         params_of_the_class = self.populate_params_of_the_class(class_name)
#         for key, value in params_of_the_class.items():
#             self.fields[key] = forms.CharField(label=key)
#             self.fields[key].required = True
#             self.fields[key].help_text = key
#             self.fields[key].initial = value

#     def handle(self, request, data):
#         try:
#             return True
#         except Exception:
#             exceptions.handle(request,
#                               _('Unable to add metadata.'))


class EditENCButtonWidget(forms.Widget):
    # EDIT_ENC_URL = "horizon:advanced:mrpuppet:edit_enc_class"
    def render(self, name, value, attrs=None):
        url = "/horizon/advanced/"
        return mark_safe('{1}<a href="{0}" class="btn btn-default"><i class="fa fa-pencil-square-o"></i></a>'.format(url,name))


class AddENCButtonWidget(forms.Widget):
    submit_url = "horizon:advanced:mrpuppet:add_enc_metadata"
    # EDIT_ENC_URL = "horizon:advanced:mrpuppet:edit_enc_class"
    def render(self, name, value, attrs=None):
        instance_id = value
        url = reverse(self.submit_url, args=[instance_id])
        text = "Or you maay add new class"
        return mark_safe('{1}<a href="{0}" class="btn btn-default"><i class="fa fa-plus"></i></a>'.format(url,text))


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
        current_classes = self.get_current_classes()
        for the_class in current_classes:
            self.fields[the_class] = forms.CharField(widget=EditENCButtonWidget(),
                                                    label = "",
                                                    required=False)

        self.fields["add_new"] = forms.CharField(widget=AddENCButtonWidget(),
                                                    label = "",
                                                    required=False,
                                                    initial = "instance_id")

        # self.fields['classes'].choices = self.populate_classes_choices()
        # classes = self.populate_args_choices()
        # for the_class, params in classes.items():
        #     for param, var in params.items():
        #         self.fields[the_class + param] = forms.CharField(label=param)
        #         self.fields[the_class + param].required = True
        #         self.fields[the_class + param].help_text = param
        #         self.fields[the_class + param].initial = var
        #         self.fields[the_class + param].widget.attrs = {'class': 'switched',
        #                                                 'data-switch-on': 'classessource',
        #                                                 'data-classessource-' + the_class: param}

    def get_current_classes(self):
        # instance_id = self.instance_id
        # server = api.nova.server_get(self.request, instance_id).to_dict()
        # enc_metadatas = server['metadata']['enc']
        # return enc_metadatas.keys()
        return ["class1","class2"]
    
    def populate_classes_choices(self):
        classes_list = [('', _('Select Metadata Class')), ("class1","class1"), ("class2","class2"), ("class3","class3")]
        return sorted(classes_list)

    def populate_args_choices(self):
        args_choices = {"class1": {"Param11":"param 1 var for class 1", "Param12":"param 2 var for class 1", "Param13":"param 3 var for class 1", "Param14":"param 4 var for class 1"},
                        "class2": {"Param21":"param 1 var for class 2", "Param22":"param 2 var for class 2", "Param23":"param 3 var for class 2", "Param24":"param 4 var for class 2", "Param25":"param 5 var for class 2", "Param26":"param 6 var for class 2"},
                        "class3": {"Param31":"param 1 var for class 3", "Param32":"param 2 var for class 3"}}
        return args_choices

    def handle(self, request, data):
        try:
            ### TODO : check if exist
            # instance_id = data['instance_id']
            # server = api.nova.server_get(self.request, instance_id).to_dict()
            # metadatas = server['metadata']
            # metadatas.update({data['name']:data['value']})
            # api.nova.server_metadata_update(self.request, instance_id, metadatas)

            # yaml.dump(data, ff, allow_unicode=True)
            return True
        except Exception:
            exceptions.handle(request,
                              _('Unable to add metadata.'))