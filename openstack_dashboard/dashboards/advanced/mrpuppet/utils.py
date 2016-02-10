from openstack_dashboard.settings import PUPPET_SERVER_ID
from openstack_dashboard import api
import yaml


def get_metadata(request, instance_id):
	server = api.nova.server_get(request, instance_id).to_dict()
	return server['metadata']

def set_metadata(request, instance_id, metadata):
	api.nova.server_metadata_update(request, instance_id, metadata)

def get_enc_metadata(request, instance_id):
	server = api.nova.server_get(request, instance_id).to_dict()
	metadata = server['metadata']
	enc_values = [yaml.load(enc_value) for (class_name, enc_value) in metadata.items() if "enc" in class_name]
	return {enc_value.keys()[0]: enc_value.values()[0] for enc_val in enc_values}

def set_enc_metadata(request, instance_id, class_name, parameters):
    enc_metadata = {class_name: new_class_params}
    metadata = {"enc_"+class_name: "---\n"+yaml.safe_dump(enc_metadata, allow_unicode=None)}
    set_metadata_as_dict(request, instance_id, metadata)