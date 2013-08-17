# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 VEXXHOST, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import jinja2

HOSTS = jinja2.Template("""127.0.0.1 localhost
::1 localhost ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

{%- for ip in ips %}
{{ ip }} {{ hostname }}
{% endfor %}""")

DEBIAN_INTERFACES = jinja2.Template("""auto lo
iface lo inet loopback
{% for dev in devices %}
auto {{ dev.name }}
iface {{ dev.name }} inet static
    address {{ dev.addr }}
    netmask {{ dev.netmask }}
{% if dev.gateway %}    gateway {{ dev.gateway }}{% endif %}
{% if dev.dns %}    dns-nameservers {{ dev.dns }}{% endif %}
{% for ip in dev.ips %}
auto {{ dev.name }}:{{ loop.index }}
iface {{ dev.name }}:{{ loop.index }} inet static
    address {{ ip.addr }}
    netmask {{ ip.netmask }}
{% endfor %}
{% endfor %}""")


REDHAT_SYSCONFIG = jinja2.Template("""NETWORKING=yes
NETWORKING_IPV6=yes
HOSTNAME={{ hostname }}
""")
