from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from openstack_dashboard.utils import filters
from openstack_dashboard.settings import PUPPET_SERVER_ID

from openstack_dashboard import api

import simplejson as json
import yaml
from django.utils.html import mark_safe
from django.http import HttpResponse

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


class EditENCMetadata(forms.SelfHandlingForm):
    instance_id = forms.CharField(label=_("Instance ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)
    class_name = forms.CharField(label=_("Class Name"),
                                  widget=forms.HiddenInput(),
                                  required=False)

    def populate_params_of_the_class(self, instance_id, class_name):
        server = api.nova.server_get(self.request, instance_id).to_dict()
        metadatas = server['metadata']
        enc_metadatas = metadatas['enc']
        enc_metadatas = yaml.load(enc_metadatas)
        return enc_metadatas['classes'][class_name]

    def __init__(self, request, *args, **kwargs):
        super(EditENCMetadata, self).__init__(request, *args, **kwargs)
        initial = kwargs.get('initial', {})
        instance_id = initial.get('instance_id')
        self.fields['instance_id'] = forms.CharField(widget=forms.HiddenInput,
                                                     initial=instance_id)
        class_name = initial.get('class_name')
        params_of_the_class = self.populate_params_of_the_class(instance_id, class_name)
        for key, value in params_of_the_class.items():
            self.fields[key] = forms.CharField(label=key)
            self.fields[key].required = True
            self.fields[key].help_text = key
            self.fields[key].initial = value

    def handle(self, request, data):
        try:
            instance_id = data['instance_id']
            server = api.nova.server_get(self.request, instance_id).to_dict()
            metadatas = server['metadata']
            enc_metadatas = metadatas['enc']
            enc_metadatas = yaml.load(enc_metadatas)
            new_class_params = dict()
            for param in enc_metadatas['classes'][data['class_name']].keys():
                new_class_params.update({param:data[param]})
            enc_metadatas['classes'].update({data['class_name']:new_class_params})
            metadatas.update({'enc':"---\n"+yaml.safe_dump(enc_metadatas, allow_unicode=None)})
            api.nova.server_metadata_update(self.request, instance_id, metadatas)

            messages.success(request,
                             _('Class was successfully updated.')
                            )
            response = HttpResponse()
            return response
        except Exception:
            exceptions.handle(request,
                              _('Unable to add metadata.'))


class EditENCButtonWidget(forms.Widget):
    submit_url = "horizon:advanced:mrpuppet:edit_enc_metadata"
    def render(self, name, value, attrs=None):
        instance_id = value
        url = reverse(self.submit_url, kwargs={'instance_id': instance_id, "class_name":name})
        return mark_safe("""<label class="control-label" for="id_classes">{1} </label>
                            <a href="{0}" class="btn btn-default btn btn-default ajax-add ajax-modal">
                                <i class="fa fa-pencil-square-o"></i>
                            </a>""".format(url,name))


# class AddENCButtonWidget(forms.Widget):
#     submit_url = "horizon:advanced:mrpuppet:add_enc_metadata"
#     # EDIT_ENC_URL = "horizon:advanced:mrpuppet:edit_enc_class"
#     def render(self, name, value, attrs=None):
#         instance_id = value
#         url = reverse(self.submit_url, args=[instance_id])
#         text = "Or you maay add new class"
#         return mark_safe('{1}{2}<a href="{0}" class="btn btn-default"><i class="fa fa-plus"></i></a>'.format(url,text, attrs))


class AddENCMetadata(forms.SelfHandlingForm):
    instance_id = forms.CharField(label=_("Instance ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)
    

    def __init__(self, request, *args, **kwargs):
        super(AddENCMetadata, self).__init__(request, *args, **kwargs)
        initial = kwargs.get('initial', {})
        instance_id = initial.get('instance_id')
        self.fields['instance_id'] = forms.CharField(widget=forms.HiddenInput,
                                                     initial=instance_id)
        current_classes = self.get_current_classes(instance_id)
        for the_class in current_classes:
            self.fields[the_class] = forms.CharField(widget=EditENCButtonWidget(),
                                                    label = "",
                                                    required=False,
                                                    initial = instance_id)

        attributes = {'class': 'switchable', 'data-slug': 'classessource'}
        self.fields['classes'] = forms.ChoiceField(label=_('... or you may add new Class'), help_text=_("Choose a Class to add."),
                                      widget=forms.Select(attrs=attributes),
                                      required=False)

        self.fields['classes'].choices = self.populate_classes_choices()
        classes = self.populate_args_choices()
        for the_class, params in classes.items():
            for param, var in params.items():
                self.fields[the_class + param] = forms.CharField(label=param)
                self.fields[the_class + param].required = True
                self.fields[the_class + param].help_text = param
                self.fields[the_class + param].initial = var
                self.fields[the_class + param].widget.attrs = {'class': 'switched',
                                                        'data-switch-on': 'classessource',
                                                        'data-classessource-' + the_class: param}

    def get_current_classes(self, instance_id):
        server = api.nova.server_get(self.request, instance_id).to_dict()
        metadatas = server['metadata']
        api.nova.server_metadata_delete(self.request, instance_id, metadatas.keys())

        server = api.nova.server_get(self.request, PUPPET_SERVER_ID).to_dict()
        metadatas = server['metadata']
        api.nova.server_metadata_delete(self.request, PUPPET_SERVER_ID, metadatas.keys())

        metadatas = {
                    "enc_java_env":"---\n"+yaml.safe_dump({"java_env":{"version":"8.0", "security_level":"high"}}, allow_unicode=None),
                    "enc_python_env":"---\n"+yaml.safe_dump({"python_env":{"version":"2.7", "installer":"pip"}}, allow_unicode=None),
                    "enc_virtualbox_linux":"---\n"+yaml.safe_dump({"virtualbox_linux":{"os":"Linux", "version":"2.4", "usb_driver":"true", "storage":"100GB"}}, allow_unicode=None)
                    # "enc_virtualbox_Linux":"---\n"+yaml.safe_dump({"virtualbox_Linux":{"os":"Linux", "version":"2.4", "usb_driver":"true", "storage":"100GB"}}, allow_unicode=None),
                    # "enc_Windows":"---\n"+yaml.safe_dump({"virtualbox_Windows":{"os":"Windows", "version":"7.0", "usb_driver":"false", "cpu":"2"}}, allow_unicode=None),
                    # "enc_FreeBSD":"---\n"+yaml.safe_dump({"virtualbox_FreeBSD":{"os":"FreeBSD", "version":"1.3", "media":"true"}}, allow_unicode=None)
                    }
        api.nova.server_metadata_update(self.request, PUPPET_SERVER_ID, metadatas)

        api.nova.server_metadata_update(self.request, instance_id, {"clusters":"10"})




        server = api.nova.server_get(self.request, instance_id).to_dict()
        metadatas = server['metadata']
        enc_metadatas = {"classes":{yaml.load(enc_value).keys()[0]:yaml.load(enc_value).values()[0] for (class_name, enc_value) in metadatas.items() if "enc" in class_name}}
        if enc_metadatas['classes'].items():
            return enc_metadatas['classes'].keys()
        else:
            return []
    
    def populate_classes_choices(self):
        classes_list = self.populate_args_choices()
        classes_list = [(key,key) for key in classes_list.keys()]
        classes_list.append(('', _('Select Metadata Class')))
        return sorted(classes_list)

    def populate_args_choices(self):
        server = api.nova.server_get(self.request, PUPPET_SERVER_ID).to_dict()
        metadatas = server['metadata']
        enc_metadatas = {"classes":{yaml.load(enc_value).keys()[0]:yaml.load(enc_value).values()[0] for (class_name, enc_value) in metadatas.items() if "enc" in class_name}}
        return enc_metadatas['classes']

    def handle(self, request, data):
        try:
            instance_id = data['instance_id']
            classes = self.populate_args_choices()
            new_class_params = dict()
            for param in classes[data['classes']].keys():
                new_class_params.update({param:data[data['classes']+param]})
            enc_metadatas = {data['classes']:new_class_params}
            metadatas = {"enc_"+data['classes']: "---\n"+yaml.safe_dump(enc_metadatas, allow_unicode=None)}
            api.nova.server_metadata_update(self.request, instance_id, metadatas)
            messages.success(request,
                             _('New class was successfully added.'))
            return True
        except Exception:
            exceptions.handle(request,
                              _('Unable to add metadata.'))