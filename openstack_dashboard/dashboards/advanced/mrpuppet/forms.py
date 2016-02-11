from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from openstack_dashboard.utils import filters
from openstack_dashboard.settings import PUPPET_SERVER_ID

from django.utils.html import mark_safe
from django.http import HttpResponse

from openstack_dashboard.dashboards.advanced.mrpuppet import utils 

class UpdateMetadata(forms.SelfHandlingForm):
    instance_id = forms.CharField(label=_("Instance ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)

    def __init__(self, *args, **kwargs):
        super(UpdateMetadata, self).__init__(*args, **kwargs)
        instance_id = kwargs.get('initial', {}).get('instance_id')
        metadatas = utils.get_metadata(self.request, instance_id)
        for key, value in metadatas.items():
            if "enc" not in key:
                self.fields[key] = forms.CharField(label=key)
                self.fields[key].required = True
                self.fields[key].help_text = key
                self.fields[key].initial = value

    def handle(self, request, data):
        try:
            instance_id = data['instance_id']
            metadatas = utils.get_metadata(self.request, instance_id)
            for key, value in metadatas.items():
                if "enc" not in key:
                    metadatas.update({key:data[key]})
            utils.set_metadata(self.request, instance_id, metadatas)
            messages.success(request,_('Metadata was successfully updated.'))
            return True
        except Exception:
            exceptions.handle(request,_('Unable to update metadata.'))

class AddMetadata(forms.SelfHandlingForm):
    instance_id = forms.CharField(label=_("Instance ID"),
                                widget=forms.HiddenInput(),
                                required=False)
    name = forms.CharField(max_length=255,
                                label=_("Metadata Name"),
                                required=True)
    value = forms.CharField(max_length=255,
                                label=_("Metadata Value"),
                                required=True)

    def handle(self, request, data):
        try:
            instance_id = data['instance_id']
            metadatas = utils.get_metadata(self.request, instance_id)
            if data['name'] not in metadatas.keys():
                metadatas.update({data['name']:data['value']})
                utils.set_metadata(self.request, instance_id, metadatas)
                messages.success(request,_('Metadata was successfully added.'))
                return True
            else:
                messages.warning(request,_('Such metadata key already exists. Please, go to Update Metadata to change it.'))
        except Exception:
            exceptions.handle(request,_('Unable to add metadata.'))


class EditENCMetadata(forms.SelfHandlingForm):
    instance_id = forms.CharField(label=_("Instance ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)
    class_name = forms.CharField(label=_("Class Name"),
                                  widget=forms.HiddenInput(),
                                  required=False)

    def populate_params_of_the_class(self, instance_id, class_name):
        enc_metadatas = utils.get_enc_metadata(self.request, instance_id)
        return enc_metadatas[class_name]

    def __init__(self, request, *args, **kwargs):
        super(EditENCMetadata, self).__init__(request, *args, **kwargs)
        initial = kwargs.get('initial', {})
        instance_id = initial.get('instance_id')
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
            class_name = data['class_name']

            class_params = self.populate_params_of_the_class(instance_id, class_name)
            [class_params.update({param:data[param]}) for param in class_params.keys()]
            utils.set_enc_metadata(self.request, instance_id, class_name, class_params)
            messages.success(request,_('Class was successfully updated.'))
            response = HttpResponse()
            return response
        except Exception:
            exceptions.handle(request,_('Unable to add metadata.'))


class EditENCButtonWidget(forms.Widget):
    submit_url = "horizon:advanced:mrpuppet:edit_enc_metadata"
    def render(self, name, value, attrs=None):
        instance_id = value
        url = reverse(self.submit_url, kwargs={'instance_id': instance_id, "class_name": name})
        return mark_safe("""<label class="control-label" for="id_classes">{1} </label>
                            <a href="{0}" class="btn btn-default btn btn-default ajax-add ajax-modal">
                                <i class="fa fa-pencil-square-o"></i>
                            </a>""".format(url, name))


# class DeleteButtonWidget(forms.Widget):
#     submit_url = "horizon:advanced:mrpuppet:delete_metadata"
#     def render(self, name, value, attrs=None):
#         instance_id = value
#         url = reverse(self.submit_url, kwargs={'instance_id': instance_id, "class_name": name})
#         return mark_safe("""<label class="control-label" for="id_classes">{1} </label>
#                             <a href="{0}" class="btn btn-default btn btn-default ajax-add ajax-modal">
#                                 <i class="fa fa-trash-o"></i>
#                             </a>""".format(url, name))


class AddENCMetadata(forms.SelfHandlingForm):
    instance_id = forms.CharField(label=_("Instance ID"),
                                  widget=forms.HiddenInput(),
                                  required=False)
    

    def __init__(self, request, *args, **kwargs):
        super(AddENCMetadata, self).__init__(request, *args, **kwargs)
        initial = kwargs.get('initial', {})
        instance_id = initial.get('instance_id')
        current_classes = self.get_current_classes(instance_id)
        for the_class in current_classes:
            self.fields[the_class] = forms.CharField(widget=EditENCButtonWidget(),
                                                    label = "",
                                                    required=False,
                                                    initial = instance_id)

        attributes = {'class': 'switchable', 'data-slug': 'classessource'}
        self.fields['classes'] = forms.ChoiceField(label=_('... or you may add new Class'),
                                                    help_text=_("Choose a Class to add."),
                                                    widget=forms.Select(attrs=attributes),
                                                    required=False)

        self.fields['classes'].choices = self.populate_classes_choices(instance_id)
        classes = self.populate_args_choices()
        for class_name, params in classes.items():
            if class_name not in current_classes:
                for param, var in params.items():
                    self.fields[class_name + param] = forms.CharField(label=param)
                    self.fields[class_name + param].required = True
                    self.fields[class_name + param].help_text = param
                    self.fields[class_name + param].initial = var
                    self.fields[class_name + param].widget.attrs = {'class': 'switched',
                                                            'data-switch-on': 'classessource',
                                                            'data-classessource-' + class_name: param}

    def get_current_classes(self, instance_id):
        ### TODO: Delete this comment
        # from openstack_dashboard import api
        # import yaml
        # server = api.nova.server_get(self.request, instance_id).to_dict()
        # metadatas = server['metadata']
        # api.nova.server_metadata_delete(self.request, instance_id, metadatas.keys())

        # server = api.nova.server_get(self.request, PUPPET_SERVER_ID).to_dict()
        # metadatas = server['metadata']
        # api.nova.server_metadata_delete(self.request, PUPPET_SERVER_ID, metadatas.keys())

        # metadatas = {
        #             "enc_java_env":"---\n"+yaml.safe_dump({"java_env":{"version":"8.0", "security_level":"high"}}, allow_unicode=None),
        #             "enc_python_env":"---\n"+yaml.safe_dump({"python_env":{"version":"2.7", "installer":"pip"}}, allow_unicode=None),
        #             "enc_apache":"---\n"+yaml.safe_dump({"apache":{"default_vhost": "true", "service_ensure": "running"}}, allow_unicode=None),
        #             "enc_virtualbox_linux":"---\n"+yaml.safe_dump({"virtualbox_linux":{"os":"Linux", "version":"2.4", "usb_driver":"true", "storage":"100GB"}}, allow_unicode=None)
        #             }
        # api.nova.server_metadata_update(self.request, PUPPET_SERVER_ID, metadatas)

        # api.nova.server_metadata_update(self.request, instance_id, {"clusters":"10"})

        enc_metadatas = utils.get_enc_metadata(self.request, instance_id)
        return enc_metadatas.keys()
    
    def populate_classes_choices(self, instance_id):
        classes_list = self.populate_args_choices()
        current_classes = self.get_current_classes(instance_id)
        classes_list = [(class_name,class_name) for class_name in classes_list.keys() if class_name not in current_classes]
        classes_list.append(('', _('Select Metadata Class')))
        return sorted(classes_list)

    def populate_args_choices(self):
        enc_metadatas = utils.get_enc_metadata(self.request, PUPPET_SERVER_ID)
        return enc_metadatas

    def handle(self, request, data):
        try:
            instance_id = data['instance_id']
            class_name = data['classes']

            class_params = self.populate_args_choices()
            class_params = class_params[class_name]
            [class_params.update({param:data[class_name + param]}) for param in class_params.keys()]
            utils.set_enc_metadata(self.request, instance_id, class_name, class_params)
            messages.success(request, _('New class was successfully added.'))
            return True
        except Exception:
            exceptions.handle(request,_('Unable to add metadata.'))