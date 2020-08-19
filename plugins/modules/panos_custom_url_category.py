#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Copyright 2018 Palo Alto Networks, Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: panos_custom_url_category
short_description: Create custom url category objects on PAN-OS devices.
description:
    - Create custom url category objects on PAN-OS devices.
author: "Borislav Varadinov (@bvaradinov-c)"
version_added: "1.2.0"
requirements:
    - pan-python can be obtained from PyPI U(https://pypi.python.org/pypi/pan-python)
    - pandevice can be obtained from PyPI U(https://pypi.python.org/pypi/pandevice)
notes:
    - Panorama is supported.
    - Check mode is supported.
extends_documentation_fragment:
    - paloaltonetworks.panos.fragments.transitional_provider
    - paloaltonetworks.panos.fragments.vsys
    - paloaltonetworks.panos.fragments.device_group
    - paloaltonetworks.panos.fragments.state
options:
    name:
        description:
            - Name of the tag.
        required: true
    url_value:
        description:
            - List with urls
    type:
        description:
            - type of the category - URL List or Category Match
    commit:
        description:
            - Commit changes after creating object.  If I(ip_address) is a Panorama device, and I(device_group) is
              also set, perform a commit to Panorama and a commit-all to the device group.
        required: false
        type: bool
        default: false
'''

EXAMPLES = '''
- name: Create Custom Url Category 'Internet Access List'
  panos_custom_url_category:
    provider: '{{ provider }}'
    name: 'Internet Access List'
    url_value:
        - microsoft.com
        - redhat.com
    type: "URL List"
'''

RETURN = '''
# Default return values
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.paloaltonetworks.panos.plugins.module_utils.panos import get_connection

try:
    from pandevice.objects import VersionedPanObject, VersionedParamPath, Root, ENTRY
    from pandevice.errors import PanDeviceError
except ImportError:
    pass


# TODO: Remove this class when migrate to pan-os-python.
# CustomUrlCategory class definition in pandevice is not complete.
# This bug has been fixed in pan-os-python.
class CustomUrlCategory(VersionedPanObject):
    """Custom url category group

    Args:
        name (str): The name
        url_value (list): Values to include in custom URL category object
        description (str): Description of this object
        type (str): Custom Url Category Type

    """

    ROOT = Root.VSYS
    SUFFIX = ENTRY

    def _setup(self):
        # xpaths
        self._xpaths.add_profile(value='/profiles/custom-url-category')

        # params
        params = []

        params.append(VersionedParamPath(
            'url_value', path='list', vartype='member'))
        params.append(VersionedParamPath(
            'description', path='description'))
        params.append(VersionedParamPath('type'))

        self._params = tuple(params)


def main():
    helper = get_connection(
        vsys=True,
        device_group=True,
        with_classic_provider_spec=True,
        with_state=True,
        argument_spec=dict(
            name=dict(type='str', required=True),
            url_value=dict(type='list', required=True),
            type=dict(type='str', default="URL List"),
            commit=dict(type='bool', default=False)
        )
    )

    module = AnsibleModule(
        argument_spec=helper.argument_spec,
        required_one_of=helper.required_one_of,
        supports_check_mode=True
    )

    parent = helper.get_pandevice_parent(module)

    spec = {
        'name': module.params['name'],
        'url_value': module.params['url_value'],
        'type': module.params['type']
    }

    commit = module.params['commit']

    try:
        listing = CustomUrlCategory.refreshall(parent, add=False)
    except PanDeviceError as e:
        module.fail_json(msg='Failed refresh: {0}'.format(e))

    obj = CustomUrlCategory(**spec)
    parent.add(obj)

    changed, diff = helper.apply_state(obj, listing, module)

    if commit and changed:
        helper.commit(module)

    module.exit_json(changed=changed, diff=diff)


if __name__ == '__main__':
    main()
