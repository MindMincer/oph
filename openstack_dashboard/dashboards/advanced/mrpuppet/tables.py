from django.utils.translation import ugettext_lazy as _

from horizon import tables
from openstack_dashboard import api


def is_deleting(instance):
    task_state = getattr(instance, "OS-EXT-STS:task_state", None)
    if not task_state:
        return False
    return task_state.lower() == "deleting"

def has_metadata(instance):
    metadatas = api.nova.server_get(self.request, instance_id).to_dict()
    return metadatas


class UpdateMetadata(tables.LinkAction):
    name = "updatemetadata"
    verbose_name = _("Update Metadata")
    url = "horizon:advanced:mrpuppet:update_metadata"
    classes = ("ajax-modal",)
    icon = "camera"

    def allowed(self, request, instance=None):
        return instance.status in ("ACTIVE") \
            and not is_deleting(instance) \
            and has_metadata(instance)

class AddMetadata(tables.LinkAction):
    name = "addmetadata"
    verbose_name = _("Add Metadata")
    url = "horizon:advanced:mrpuppet:add_metadata"
    classes = ("ajax-modal",)
    icon = "camera"

    def allowed(self, request, instance=None):
        return instance.status in ("ACTIVE") \
            and not is_deleting(instance)


class MyFilterAction(tables.FilterAction):
    name = "myfilter"


class InstancesTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"))
    status = tables.Column("status", verbose_name=_("Status"))
    zone = tables.Column('availability_zone', verbose_name=_("Availability Zone"))
    image_name = tables.Column('image_name', verbose_name=_("Image Name"))

    class Meta:
        name = "instances"
        verbose_name = _("Instances")
        table_actions = (MyFilterAction,)
        row_actions = (AddMetadata, UpdateMetadata,)