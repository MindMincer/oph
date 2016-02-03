from django.utils.translation import ugettext_lazy as _

from horizon import tables


def is_deleting(instance):
    task_state = getattr(instance, "OS-EXT-STS:task_state", None)
    if not task_state:
        return False
    return task_state.lower() == "deleting"


class ApplyAction(tables.LinkAction):
    name = "applyaction"
    verbose_name = _("Apply Action")
    url = "horizon:advanced:mrpappuet:apply_action"
    classes = ("ajax-modal",)
    icon = "camera"

    def allowed(self, request, instance=None):
        return instance.status in ("ACTIVE") \
            and not is_deleting(instance)

    def get_link_url(self, datum=None):
        obj_id = self.table.get_object_id(datum)
        return "/horizon/advanced/mrpuppet/{0}/apply_action".format(obj_id)


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
        row_actions = (ApplyAction,)