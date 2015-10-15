# Copyright 2015 Maxime Terras <maxime.terras@numergy.com>
# Copyright 2015 Pierre Padrixe <pierre.padrixe@gmail.com>
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


import click
from vsd_client import VSDConnection
from prettytable import PrettyTable

def print_object(obj, only=None, exclude=[]):
    def _format_multiple_values(values):
        """Format list in string to be printable as prettytable"""
        row_value = ""
        if len(values) > 0:
            last = values.pop()
            for o in values:
                row_value += "%s\n" % o
            row_value += last
        return row_value
            

    def _print_table(obj, exclude):
        table = PrettyTable(["Field", "Value"])
        table.align["Field"] = "l"

        for key in obj.keys():
            if key not in exclude:
                if type(obj[key]) is list:
                    table.add_row([key, _format_multiple_values(obj[key])])
                else:
                    table.add_row([key, obj[key]])
        print table

    if only:
        if only in obj:
            print obj[only]
        else:
            print "No such key : %s" %only
    else:
        _print_table(obj, exclude)
            

def netmask_to_length(netmask):
    tableSubnet={
        '0'   : 0,
        '128' : 1,
        '192' : 2,
        '224' : 3,
        '240' : 4,
        '248' : 5,
        '252' : 6,
        '254' : 7,
        '255' : 8,
    }
    netmask_splited = str(netmask).split('.')
    length = tableSubnet[ netmask_splited[0] ] + tableSubnet[ netmask_splited[1] ] + \
                tableSubnet[ netmask_splited[2] ] + tableSubnet[ netmask_splited[3] ]
    return str(length)

def check_id(**ids):
    # Remove '_id' at the end of key names
    new_ids = {}
    for k, v in ids.items():
        k = '_'.join(k.split('_')[0:-1])
        new_ids[k] = v
    ids = new_ids

    # Check one and only one id is specified
    nb_ids = 0
    for k, v in ids.items():
        if v is not None:
            nb_ids += 1
            good_k = k
    if nb_ids != 1:
        raise click.exceptions.UsageError(
            "You must specify only one id in %s" % ids.keys())

    return good_k, ids[good_k]

@click.group()
@click.option('--vsd-url', metavar='<url>', envvar='VSD_URL',
              help='VSD url http(s)://hostname:port/nuage/api_v1_0 (Env: VSD_URL)', required=True)
@click.option('--vsd-username',metavar='<username>', envvar='VSD_USERNAME',
              help='VSD Authentication username (Env: VSD_USERNAME)', required=True )
@click.option('--vsd-password',metavar='<password>', envvar='VSD_PASSWORD',
              help='VSD Authentication password (Env: VSD_PASSWORD)', required=True )
@click.option('--vsd-enterprise',metavar='<enterprise>', envvar='VSD_ENTERPRISE',
              help='VSD Authentication enterprise (Env: VSD_ENTERPRISE)', required=True )
@click.option('--show-only',metavar='<key>',
              help='Show only the value for a given key (usable for show and create command)' )
@click.option('--debug', is_flag=True, help='Active debug for request and response')
@click.option('--force-auth', is_flag=True, help='Do not use existing APIkey. Replay authentication')
@click.pass_context
def vsdcli(ctx, vsd_username, vsd_password, vsd_enterprise, vsd_url, show_only, debug, force_auth):
    """Command-line interface to the VSD APIs"""
    nc = VSDConnection(
            vsd_username,
            vsd_password,
            vsd_enterprise,
            vsd_url,
            debug=debug,
            force_auth=force_auth
         )
    ctx.obj['nc'] = nc
    ctx.obj['show_only'] = show_only

@vsdcli.command(name='me-show')
@click.option('--verbose', count=True, help='Show APIKey')
@click.pass_context
def me_show(ctx, verbose):
    """Show my own user information"""
    result = ctx.obj['nc'].me()[0]
    if verbose >= 1:
        print_object( result )
    else:
        print_object( result, exclude=['APIKey'], only=ctx.obj['show_only'] )


@vsdcli.command(name='license-list')
@click.pass_context
def license_list(ctx):
    """Show all license within the VSD"""
    from datetime import datetime
    result = ctx.obj['nc'].get("licenses")
    table=PrettyTable(["License id", "Compagny", "Max NICs", "Max VMs", "Version", "Expiration"])
    for line in result:
        table.add_row( [ line['ID'],
                          line['company'],
                          line['allowedNICsCount'],
                          line['allowedVMsCount'],
                          line['productVersion'] + 'R' + str(line['majorRelease']),
                          datetime.fromtimestamp( line['expirationDate']/1000 ).strftime('%Y-%m-%d %H:%M:%S') ] )
    print table

@vsdcli.command(name='license-show')
@click.argument('license-id', metavar='<license-id>', required=True)
@click.option('--verbose', count=True, help='Show license code in BASE64')
@click.pass_context
def license_show(ctx, license_id, verbose):
    """Show license detail for a given license id"""
    result = ctx.obj['nc'].get("licenses/%s" %license_id)[0]
    print_object( result, exclude=['license'], only=ctx.obj['show_only'] )
    if verbose >= 1:
        print "License: " + result['license']

@vsdcli.command(name='license-create')
@click.argument('license', metavar='<license (Base64)>', required=True)
@click.pass_context
def license_create(ctx, license):
    """Add a license to the VSD"""
    result = ctx.obj['nc'].post("licenses" , { "license": license })[0]
    print_object( result, exclude=['license'], only=ctx.obj['show_only'] )

@vsdcli.command(name='license-delete')
@click.argument('license-id', metavar='<license ID>', required=True)
@click.confirmation_option(prompt='Are you sure ?')
@click.pass_context
def license_delete(ctx, license_id):
    """Delete a given license"""
    ctx.obj['nc'].delete("licenses/%s" %license_id)

@vsdcli.command(name='enterprise-list')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, description, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def enterprise_list(ctx, filter):
    """Show all enterprise within the VSD"""
    result = ctx.obj['nc'].get("enterprises", filter=filter)
    table=PrettyTable(["Enterprise ID", "Name"])
    for line in result:
        table.add_row( [ line['ID'],
                        line['name'] ] )
    print table

@vsdcli.command(name='enterprise-show')
@click.argument('enterprise-id', metavar='<enterprise-id>', required=True)
@click.pass_context
def enterprise_show(ctx, enterprise_id):
    """Show information for a given enterprise id"""
    result = ctx.obj['nc'].get("enterprises/%s" %enterprise_id)[0]
    print_object( result, exclude=['APIKey'], only=ctx.obj['show_only'] )

@vsdcli.command(name='enterprise-create')
@click.argument('name', metavar='<name>', required=True)
@click.pass_context
def enterprise_create(ctx, name):
    """Add an enterprise to the VSD"""
    params = {}
    params['name'] = name
    result = ctx.obj['nc'].post("enterprises" , params)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='enterprise-delete')
@click.argument('enterprise-id', metavar='<enterprise ID>', required=True)
@click.confirmation_option(prompt='Are you sure ?')
@click.pass_context
def enterprise_delete(ctx, enterprise_id):
    """Delete a given enterprise"""
    ctx.obj['nc'].delete("enterprises/%s?responseChoice=1" %enterprise_id)

@vsdcli.command(name='enterprise-update')
@click.argument('enterprise-id', metavar='<enterprise ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def enterprise_update(ctx, enterprise_id, key_value):
    """Update key/value for a given enterprise"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':',1)
        params[key] = value
    ctx.obj['nc'].put("enterprises/%s" %enterprise_id, params)
    result = ctx.obj['nc'].get("enterprises/%s" %enterprise_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='domaintemplate-list')
@click.option('--enterprise-id', metavar='<enterprise ID>', required=True)
@click.option('--filter', metavar='<filter>',
              help='Filter for NEED TO BE UPDATED')
@click.pass_context
def domaintemplate_list(ctx, enterprise_id, filter):
    """Show all domaintemplate for a given enterprise id"""
    result = ctx.obj['nc'].get("enterprises/%s/domaintemplates" %enterprise_id, filter=filter)
    table=PrettyTable(["Domain Template ID", "Name"])
    for line in result:
        table.add_row( [ line['ID'],
                        line['name'] ] )
    print table

@vsdcli.command(name='domaintemplate-show')
@click.argument('domaintemplate-id', metavar='<domaintemplate-id>', required=True)
@click.pass_context
def domaintemplate_show(ctx, domaintemplate_id):
    """Show information for a given domaintemplate id"""
    result = ctx.obj['nc'].get("domaintemplates/%s" %domaintemplate_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='domaintemplate-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--enterprise-id', metavar='<enterprise ID>', required=True)
@click.pass_context
def domaintemplate_create(ctx, name, enterprise_id):
    """Add an domaintemplate to the VSD for an given enterprise"""
    params = {'name' : name }
    result = ctx.obj['nc'].post("enterprises/%s/domaintemplates" %enterprise_id, params)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='domaintemplate-delete')
@click.argument('domaintemplate-id', metavar='<domaintemplate ID>', required=True)
@click.pass_context
def domaintemplate_delete(ctx, domaintemplate_id):
    """Delete a given domaintemplate"""
    ctx.obj['nc'].delete("domaintemplates/%s" %domaintemplate_id)

@vsdcli.command(name='domaintemplate-update')
@click.argument('domaintemplate-id', metavar='<domaintemplate ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def domaintemplate_update(ctx, domaintemplate_id, key_value):
    """Update key/value for a given domaintemplate"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':',1)
        params[key] = value
    ctx.obj['nc'].put("domaintemplates/%s" %domaintemplate_id, params)
    result = ctx.obj['nc'].get("domaintemplates/%s" %domaintemplate_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='domain-list')
@click.option('--domaintemplate-id', metavar='<id>')
@click.option('--enterprise-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for serviceID, name, description, customerID, labelID, serviceID, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def domain_list(ctx, filter, **ids):
    """Show domain for a given enterprise or domain id"""
    id_type, id = check_id(**ids)
    if filter == None:
        result = ctx.obj['nc'].get("%ss/%s/domains" %(id_type, id))
    else :
        result = ctx.obj['nc'].get("%ss/%s/domains" %(id_type, id), filter=filter)
    table=PrettyTable(["Domain ID", "Name", "Description", "RT / RD"])
    for line in result:
        table.add_row( [ line['ID'],
                        line['name'],
                        line['description'],
                        line['routeTarget'] + " / " + line['routeDistinguisher'] ] )
    print table

@vsdcli.command(name='domain-show')
@click.argument('domain-id', metavar='<domain-id>', required=True)
@click.pass_context
def domain_show(ctx, domain_id):
    """Show information for a given domain id"""
    result = ctx.obj['nc'].get("domains/%s" %domain_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='domain-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--enterprise-id', metavar='<enterprise ID>', required=True)
@click.option('--template-id', metavar='<template ID>', required=True)
@click.option('--rd', metavar='<route distinguisher>')
@click.option('--rt', metavar='<route target>')
@click.pass_context
def domain_create(ctx, name, enterprise_id, template_id, rt, rd):
    """Add an domain to the VSD for an given enterprise"""
    params = {'name' : name,
        'templateID' : template_id }
    if rt != None :
        params['routeTarget'] = rt
    if rd != None :
        params['routeDistinguisher'] = rd
    result = ctx.obj['nc'].post("enterprises/%s/domains" %enterprise_id, params)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='domain-delete')
@click.argument('domain-id', metavar='<domain ID>', required=True)
@click.pass_context
def domain_delete(ctx, domain_id):
    """Delete a given domain"""
    ctx.obj['nc'].delete("domains/%s" %domain_id)

@vsdcli.command(name='domain-update')
@click.argument('domain-id', metavar='<domain ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def domain_update(ctx, domain_id, key_value):
    """Update key/value for a given domain"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':',1)
        params[key] = value
    ctx.obj['nc'].put("domains/%s" %domain_id, params)
    result = ctx.obj['nc'].get("domains/%s" %domain_id)[0]
    print_object( result, only=ctx.obj['show_only'] )


@vsdcli.command(name='zone-list')
@click.option('--domain-id', metavar='<domain ID>', required=True)
@click.option('--filter', metavar='<filter>',
              help='Filter for address, netmask, IPType, name, description, numberOfHostsInSubnets, publicZone, address, netmask, IPType, name, address, netmask, IPType, name, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def zone_list(ctx, domain_id, filter):
    """Show zone for a given domain id"""
    if filter == None:
        result = ctx.obj['nc'].get("domains/%s/zones" %domain_id)
    else :
        result = ctx.obj['nc'].get("domains/%s/zones" %domain_id, filter=filter)
    table=PrettyTable(["Zone ID", "Name" ])
    for line in result:
        table.add_row( [ line['ID'],
                         line['name'] ] )
    print table

@vsdcli.command(name='zone-show')
@click.argument('zone-id', metavar='<zone-id>', required=True)
@click.pass_context
def zone_show(ctx, zone_id):
    """Show information for a given zone id"""
    result = ctx.obj['nc'].get("zones/%s" %zone_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='zone-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--domain-id', metavar='<domain ID>', required=True)
@click.pass_context
def zone_create(ctx, name, domain_id ):
    """Add a zone to the VSD for an given domain"""
    params = {'name' : name }
    result = ctx.obj['nc'].post("domains/%s/zones" %domain_id, params)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='zone-delete')
@click.argument('zone-id', metavar='<zone ID>', required=True)
@click.pass_context
def zone_delete(ctx, zone_id):
    """Delete a given zone"""
    ctx.obj['nc'].delete("zones/%s" %zone_id)


@vsdcli.command(name='subnet-list')
@click.option('--zone-id', metavar='<id>')
@click.option('--domain-id', metavar='<id>')
@click.option('--app-id', metavar='<id>')
@click.option('--subnettemplate-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for address, netmask, IPType, name, gateway, description, serviceID, address, netmask, IPType, name, gateway, description, splitSubnet, proxyARP, address, netmask, IPType, name, gateway, description, address, netmask, IPType, name, address, netmask, IPType, name, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def subnet_list(ctx, filter, **ids):
    """List subnets for a given zone, app, subnettemplate, or domain id"""
    id_type, id = check_id(**ids)
    if filter == None:
        result = ctx.obj['nc'].get("%ss/%s/subnets" %(id_type, id))
    else :
        result = ctx.obj['nc'].get("%ss/%s/subnets" %(id_type, id), filter=filter)
    table=PrettyTable(["Subnet ID", "Name", "Address", "Gateway", "RT / RD", "External ID"])

    for line in result:
        if line['address'] != None:
            address = line['address'] + "/" + netmask_to_length( line['netmask'] )
        else:
            address = "None"

        table.add_row( [ line['ID'],
                        line['name'],
                        address,
                        line['gateway'],
                        line['routeTarget'] + " / " + line['routeDistinguisher'],
                        line['externalID']
                        ] )
    print table

@vsdcli.command(name='subnet-show')
@click.argument('subnet-id', metavar='<subnet-id>', required=True)
@click.pass_context
def subnet_show(ctx, subnet_id):
    """Show information for a given subnet id"""
    result = ctx.obj['nc'].get("subnets/%s" %subnet_id)[0]
    print_object( result, only=ctx.obj['show_only'] )


@vsdcli.command(name='subnet-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--zone-id', metavar='<zone ID>', required=True)
@click.option('--address', metavar='<address>', required=True)
@click.option('--netmask', metavar='<netmask>', required=True)
@click.option('--gateway', metavar='<gateway>')
@click.option('--rd', metavar='<route distinguisher>')
@click.option('--rt', metavar='<route target>')
@click.pass_context
def subnet_create(ctx, name, zone_id, address, gateway, netmask, rt, rd ):
    """Add a subnet to the VSD for an given zone"""

    # Define mandotory values
    params = {'name' : name,
        'address' : address,
        'netmask' : netmask }
    # Define optionnal values
    if gateway != None :
        params['gateway'] = gateway
    if rt != None :
        params['routeTarget'] = rt
    if rd != None :
        params['routeDistinguisher'] = rd

    result = ctx.obj['nc'].post("zones/%s/subnets" %zone_id, params)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='subnet-update')
@click.argument('subnet-id', metavar='<subnet ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def subnet_update(ctx, subnet_id, key_value):
    """Update key/value for a given subnet"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':',1)
        params[key] = value
    ctx.obj['nc'].put("subnets/%s" %subnet_id, params)
    result = ctx.obj['nc'].get("subnets/%s" %subnet_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='subnet-delete')
@click.argument('subnet-id', metavar='<subnet ID>', required=True)
@click.pass_context
def subnet_delete(ctx, subnet_id):
    """Delete a given subnet"""
    ctx.obj['nc'].delete("subnets/%s" %subnet_id)

@vsdcli.command(name='user-list')
@click.option('--enterprise-id', metavar='<id>')
@click.option('--group-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for firstName, lastName, userName, email, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def user_list_list(ctx, filter, **ids):
    """list users for a given enterprise or group id"""
    id_type, id = check_id(**ids)
    if filter == None:
        result = ctx.obj['nc'].get("%ss/%s/users" %(id_type, id))
    else :
        result = ctx.obj['nc'].get("%ss/%s/users" %(id_type, id), filter=filter)
    table=PrettyTable(["ID", "User name", "First name", "Last name", "Email"])
    for line in result:
        table.add_row( [ line['ID'],
                        line['userName'],
                        line['firstName'],
                        line['lastName'],
                        line['email'] ] )
    print table

@vsdcli.command(name='user-show')
@click.argument('user-id', metavar='<user-id>', required=True)
@click.pass_context
def user_show(ctx, user_id):
    """Show information for a given user id"""
    result = ctx.obj['nc'].get("users/%s" %user_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='user-create')
@click.argument('username', metavar='<username>', required=True)
@click.option('--lastname', metavar='<lastname>', required=True)
@click.option('--firstname', metavar='<firstname>', required=True)
@click.option('--email', metavar='<email>', required=True)
@click.option('--password', metavar='<password>', required=True)
@click.option('--enterprise-id', metavar='<enterprise ID>', required=True)
@click.pass_context
def user_create(ctx, username, firstname, lastname, email, password, enterprise_id ):
    """Add a user to the VSD"""
    
    import hashlib
    
    # Define mandotory values
    params = {'userName' : username,
        'firstName' : firstname,
        'lastName'  : lastname,
        'email'     : email,
        'password'  : hashlib.sha1(password).hexdigest() }
    
    result = ctx.obj['nc'].post("enterprises/%s/users" %enterprise_id, params)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='user-delete')
@click.argument('user-id', metavar='<user ID>', required=True)
@click.pass_context
def user_delete(ctx, user_id):
    """Delete a given user"""
    ctx.obj['nc'].delete("users/%s" %user_id)

@vsdcli.command(name='user-update')
@click.argument('user-id', metavar='<user ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def user_update(ctx, user_id, key_value):
    """Update key/value for a given user"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':',1)
        params[key] = value
    ctx.obj['nc'].put("users/%s" %user_id, params)
    result = ctx.obj['nc'].get("users/%s" %user_id)[0]
    print_object( result, only=ctx.obj['show_only'] )



@vsdcli.command(name='group-list')
@click.option('--enterprise-id', metavar='<id>')
@click.option('--user-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, description, role, private, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def group_list(ctx, filter, **ids):
    """list groups for a given enterprise id or that an user belongs to"""
    id_type, id = check_id(**ids)
    if filter == None:
        result = ctx.obj['nc'].get("%ss/%s/groups" %(id_type, id))
    else :
        result = ctx.obj['nc'].get("%ss/%s/groups" %(id_type, id), filter=filter)
    table=PrettyTable(["ID", "Name", "Description", "Role", "Private"])
    table.max_width['Description'] = 40
    for line in result:
        table.add_row( [ line['ID'],
                        line['name'],
                        line['description'],
                        line['role'],
                        line['private'] ] )
    print table

@vsdcli.command(name='group-show')
@click.argument('group-id', metavar='<group-id>', required=True)
@click.pass_context
def group_show(ctx, group_id):
    """Show information for a given group id"""
    result = ctx.obj['nc'].get("groups/%s" %group_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='group-create')
@click.argument('name', metavar='<Group name>', required=True)
@click.option('--enterprise-id', metavar='<enterprise ID>', required=True)
@click.option('--description', metavar='<descrition>')
@click.option('--private', metavar='<email>', count=True)
@click.pass_context
def group_create(ctx, name, enterprise_id , description, private ):
    """Add a group to the VSD"""
    
    # Define mandotory values
    params = {'name' : name }
    # Define optional values
    if description != None:
        params['description'] = description
    if private >= 1:
        params['private'] = True
    result = ctx.obj['nc'].post("enterprises/%s/groups" %enterprise_id, params)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='group-update')
@click.argument('group-id', metavar='<group ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def group_update(ctx, group_id, key_value):
    """Update key/value for a given group"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':',1)
        params[key] = value
    ctx.obj['nc'].put("groups/%s" %group_id, params)
    result = ctx.obj['nc'].get("groups/%s" %group_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='group-delete')
@click.argument('group-id', metavar='<group ID>', required=True)
@click.pass_context
def group_delete(ctx, group_id):
    """Delete a given group"""
    ctx.obj['nc'].delete("groups/%s" %group_id)

@vsdcli.command(name='group-add-user')
@click.argument('group-id', metavar='<group ID>', required=True)
@click.option('--user-id', metavar='<user ID>', required=True)
@click.pass_context
def group_add_user(ctx, group_id, user_id):
    """Add a user to a given group"""
    # Get all user for this group
    userList = ctx.obj['nc'].get("groups/%s/users" %group_id )
    user_ids = [u['ID'] for u in userList]
    user_ids.append( user_id )
    ctx.obj['nc'].put("groups/%s/users" %group_id, user_ids )

@vsdcli.command(name='group-del-user')
@click.argument('group-id', metavar='<group ID>', required=True)
@click.option('--user-id', metavar='<user ID>', required=True)
@click.pass_context
def group_del_user(ctx, group_id, user_id):
    """delete a user from a given group"""
    # Get all user for this group
    user_list = ctx.obj['nc'].get("groups/%s/users" % group_id)
    user_ids = [elt.get('ID') for elt in user_list if elt.get('ID') != user_id]
    if len(user_ids) == len(user_list):
        print "User not present in the group"
    else:
        ctx.obj['nc'].put("groups/%s/users" % group_id, user_ids)

@vsdcli.command(name='gateway-list')
@click.option('--enterprise-id', metavar='<ID>')
@click.option('--redundancygroup-id', metavar='<ID>')
@click.option('--filter', metavar='<filter>',
              help='Filter for pending, systemID, name, description, personality, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def gateway_list_list(ctx, enterprise_id, redundancygroup_id, filter):
    """list gateways for a given enterprise or group id"""
    if enterprise_id != None:
        url_request = "enterprises/%s/gateways" %enterprise_id
    elif redundancygroup_id != None:
        url_request = "redundancygroups/%s/gateways" %redundancygroup_id
    else:
        url_request = "gateways"

    if filter == None:
        result = ctx.obj['nc'].get( url_request )
    else :
        result = ctx.obj['nc'].get( url_request , filter=filter)
    table=PrettyTable(["ID", "System ID", "Name", "Description", "Pending", "Redundancy Group ID", "Personality"])
    for line in result:
        table.add_row( [ line['ID'],
                        line['systemID'],
                        line['name'],
                        line['description'],
                        line['pending'],
                        line['redundancyGroupID'],
                        line['personality'] ] )
    print table

@vsdcli.command(name='gateway-show')
@click.argument('gateway-id', metavar='<gateway ID>', required=True)
@click.pass_context
def group_show(ctx, gateway_id):
    """Show information for a given gateway ID"""
    result = ctx.obj['nc'].get("gateways/%s" %gateway_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='gateway-update')
@click.argument('gateway-id', metavar='<gateway ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def gateway_update(ctx, gateway_id, key_value):
    """Update key/value for a given gateway"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':',1)
        params[key] = value
    ctx.obj['nc'].put("gateways/%s" %gateway_id, params)
    result = ctx.obj['nc'].get("gateways/%s" %gateway_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='vsp-list')
@click.option('--filter', metavar='<filter>',
              help='Filter for productVersion, name, description, location, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def vsp_list(ctx, filter):
    """list all vsp"""
    if filter == None:
        result = ctx.obj['nc'].get("vsps/")
    else :
        result = ctx.obj['nc'].get("vsps/", filter=filter)
    table=PrettyTable(["ID", "Name", "Description", "Version"])
    for line in result:
        table.add_row( [ line['ID'],
                        line['name'],
                        line['description'],
                        line['productVersion'] ] )
    print table

@vsdcli.command(name='vsp-show')
@click.argument('vsp-id', metavar='<vsp ID>', required=True)
@click.pass_context
def vsp_show(ctx, vsp_id):
    """Show information for a given vsp ID"""
    result = ctx.obj['nc'].get("vsps/%s" %vsp_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='vsd-list')
@click.argument('vsp-id', metavar='<vsp ID>', required=True)
@click.option('--filter', metavar='<filter>',
              help='Filter for address, managementIP, name, location, description, productVersion, status, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def vsd_list(ctx, vsp_id, filter):
    """List all vsd for a given vsp"""
    if filter == None:
        result = ctx.obj['nc'].get("vsps/%s/vsds" %vsp_id)
    else :
        result = ctx.obj['nc'].get("vsps/%s/vsds" %vsp_id, filter=filter)
    table=PrettyTable(["ID", "Name", "Description", "Status", "Mode"])
    for line in result:
        table.add_row( [ line['ID'],
                        line['name'],
                        line['description'],
                        line['status'],
                        line['mode'] ] )
    print table

@vsdcli.command(name='vsd-show')
@click.argument('vsd-id', metavar='<vsd ID>', required=True)
@click.option('--verbose', count=True, help='Show disk informations')
@click.pass_context
def vsd_show(ctx, vsd_id, verbose):
    """Show information for a given VSD ID"""
    result = ctx.obj['nc'].get("vsds/%s" %vsd_id)[0]
    print_object( result, only=ctx.obj['show_only'], exclude=['disks'] )
    if verbose >= 1:
        print "Disks :"
        print result['disks']


@vsdcli.command(name='vsd-componant-list')
@click.argument('vsd-id', metavar='<vsd ID>', required=True)
@click.pass_context
def vsd_componant_list(ctx, vsd_id):
    """List componant for a given VSD ID"""
    result = ctx.obj['nc'].get("vsds/%s/components" %vsd_id)
    table=PrettyTable(["ID", "Name", "Description", "Status", "Address", "Version", "type"])
    for line in result:
        table.add_row( [ line['ID'],
                        line['name'],
                        line['description'],
                        line['status'],
                        line['address'],
                        line['productVersion'],
                        line['type'] ] )
    print table



@vsdcli.command(name='vm-list')
@click.option('--egressacltemplate-id', metavar='<id>')
@click.option('--enterprise-id', metavar='<id>')
@click.option('--ingressacltemplate-id', metavar='<id>')
@click.option('--vrs-id', metavar='<id>')
@click.option('--vport-id', metavar='<id>')
@click.option('--zone-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--app-id', metavar='<id>')
@click.option('--domain-id', metavar='<id>')
@click.option('--user-id', metavar='<id>')
@click.option('--subnet-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for UUID, name, status, reasonType, hypervisorIP, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def vm_list(ctx, filter, **ids):
    """List all VMs"""
    id_type, id = check_id(**ids)
    request = "vms"
    if id != None :
        if id_type != None :
            request = "%ss/%s/vms" %(id_type, id)
    if filter == None :
        result = ctx.obj['nc'].get(request)
    else :
        result = ctx.obj['nc'].get(request, filter=filter)
    table=PrettyTable(["ID", "Vm UUID", "Name", "Status", "Hypervisor IP", "Reason Type"])
    for line in result:
        table.add_row( [ line['ID'],
                        line['UUID'],
                        line['name'],
                        line['status'],
                        line['hypervisorIP'],
                        line['reasonType'] ] )
    print table

@vsdcli.command(name='vm-show')
@click.argument('vm-id', metavar='<vm ID>', required=True)
@click.pass_context
def vm_show(ctx, vm_id):
    """Show information for a given VM ID"""
    result = ctx.obj['nc'].get("vms/%s" %vm_id)[0]
    print_object( result,exclude=['interfaces','resyncInfo'], only=ctx.obj['show_only'] )

@vsdcli.command(name='vm-delete')
@click.argument('vm-id', metavar='<vm ID>', required=True)
@click.pass_context
def vm_delete(ctx, vm_id):
    """Delete VM for a given ID"""
    result = ctx.obj['nc'].delete("vms/%s" %vm_id)



@vsdcli.command(name='vminterface-list')
@click.option('--subnet-id', metavar='<id>')
@click.option('--zone-id', metavar='<id>')
@click.option('--vm-id', metavar='<id>')
@click.option('--vport-id', metavar='<id>')
@click.option('--domain-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, IPAddress, MAC, name, IPAddress, name, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def vminterfaces_list(ctx, filter, **ids):
    """List VM interfaces"""
    id_type, id = check_id(**ids)
    if (id != None and id_type == None) or (id == None and id_type != None):
        raise Exception("Set id and id-type")

    if id_type != None:
        request = "%ss/%s/vminterfaces" %(id_type, id)
    else:
        request = "vminterfaces" 
    if filter == None:
        result = ctx.obj['nc'].get(request)
    else :
        result = ctx.obj['nc'].get(request, filter=filter)
    table=PrettyTable(["ID", "VM UUID", "IP Address", "Netmask" , "Floating IP", "MAC" ])
    for line in result:
        table.add_row( [ line['ID'],
                        line['VMUUID'],
                        line['IPAddress'],
                        line['netmask'],
                        line['associatedFloatingIPAddress'],
                        line['MAC'] ] )
    print table

@vsdcli.command(name='vminterface-show')
@click.argument('vminterface-id', metavar='<vminterface ID>', required=True)
@click.pass_context
def vminterface_show(ctx, vminterface_id):
    """Show information for a given VM interface ID"""
    result = ctx.obj['nc'].get("vminterfaces/%s" %vminterface_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='shared-network-list')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, description, address, netmask, gateway, type, domainRouteDistinguisher, domainRouteTarget, externalID')
@click.pass_context
def shared_network_list(ctx, filter):
    """List all shared network ressource"""
    if filter == None :
        result = ctx.obj['nc'].get("sharednetworkresources")
    else :
        result = ctx.obj['nc'].get("sharednetworkresources", filter=filter)
    print netmask_to_length( "255.255.255.0" )
    table=PrettyTable(["ID", "Name", "Description", "Type", "Address", "Gateway", "RT / RD" ])
    for line in result:
        table.add_row( [ line['ID'],
                        line['name'],
                        line['description'],
                        line['type'],
                        line['address'] + "/" + netmask_to_length( line['netmask'] ),
                        line['gateway'],
                        line['domainRouteTarget'] + " / " + line['domainRouteDistinguisher']
                       ] )
    print table

@vsdcli.command(name='vminterface-update')
@click.argument('vminterface-id', metavar='<vminterface ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def vminterface_update(ctx, vminterface_id, key_value):
    """Update key/value for a given vminterface"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':',1)
        params[key] = value
    ctx.obj['nc'].put("vminterfaces/%s" %vminterface_id, params)
    result = ctx.obj['nc'].get("vminterfaces/%s" %vminterface_id)[0]
    print_object( result, only=ctx.obj['show_only'] )




@vsdcli.command(name='shared-network-show')
@click.argument('shared-network-id', metavar='<shared-network ID>', required=True)
@click.pass_context
def shared_network_show(ctx, shared_network_id):
    """Show information for a given shared-network ID"""
    result = ctx.obj['nc'].get("sharednetworkresources/%s" %shared_network_id)[0]
    print_object( result, only=ctx.obj['show_only'] )


@vsdcli.command(name='vporttag-list')
@click.option('--bridgeinterface-id', metavar='<id>')
@click.option('--hostinterface-id', metavar='<id>')
@click.option('--vport-id', metavar='<id>')
@click.option('--domain-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--vminterface-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for lastUpdatedDate, creationDate, externalID')
@click.pass_context
def vporttag_list(ctx, filter, **ids):
    """List all vPort tag"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/vporttags" %(id_type, id)
    if filter == None :
        result = ctx.obj['nc'].get(request)
    else :
        result = ctx.obj['nc'].get(request, filter=filter)
    table=PrettyTable(["ID", "Description", "Name", "endPoint Type" ])
    for line in result:
        table.add_row( [ line['ID'],
                        line['description'],
                        line['name'],
                        line['endPointType'] ] )
    print table

@vsdcli.command(name='l2domain-list')
@click.option('--l2domaintemplate-id', metavar='<id>')
@click.option('--enterprise-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for description, name, serviceID, description, name, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def l2domain_list(ctx, filter, **ids):
    """List L2 domain for a given enterprise or l2 domain template"""
    id_type, id = check_id(**ids)
    if filter == None:
        result = ctx.obj['nc'].get("%ss/%s/l2domains" %(id_type, id))
    else :
        result = ctx.obj['nc'].get("%ss/%s/l2domains" %(id_type, id), filter=filter)
    table=PrettyTable(["L2 Domain ID", "Name", "Description", "RT / RD"])
    for line in result:
        table.add_row( [ line['ID'],
                        line['name'],
                        line['description'],
                        line['routeTarget'] + " / " + line['routeDistinguisher'] ] )
    print table


@vsdcli.command(name='l2domain-show')
@click.argument('l2domain-id', metavar='<l2domain-id>', required=True)
@click.pass_context
def l2domain_show(ctx, l2domain_id):
    """Show information for a given l2 domain id"""
    result = ctx.obj['nc'].get("l2domains/%s" %l2domain_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='l2domain-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--enterprise-id', metavar='<enterprise ID>', required=True)
@click.option('--template-id', metavar='<template ID>', required=True)
@click.option('--rd', metavar='<route distinguisher>')
@click.option('--rt', metavar='<route target>')
@click.pass_context
def l2domain_create(ctx, name, enterprise_id, template_id, rt, rd):
    """Add an l2 domain to the VSD for an given enterprise"""
    params = {'name' : name,
        'templateID' : template_id }
    if rt != None :
        params['routeTarget'] = rt
    if rd != None :
        params['routeDistinguisher'] = rd
    result = ctx.obj['nc'].post("enterprises/%s/l2domains" %enterprise_id, params)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='l2domain-delete')
@click.argument('l2domain-id', metavar='<l2domain ID>', required=True)
@click.pass_context
def l2domain_delete(ctx, domain_id):
    """Delete a given l2 domain"""
    ctx.obj['nc'].delete("l2domains/%s" %domain_id)

@vsdcli.command(name='l2domain-update')
@click.argument('l2domain-id', metavar='<domain ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def l2domain_update(ctx, l2domain_id, key_value):
    """Update key/value for a given l2 domain"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':',1)
        params[key] = value
    ctx.obj['nc'].put("l2domains/%s" %l2domain_id, params)
    result = ctx.obj['nc'].get("l2domains/%s" %l2domain_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='floatingip-list')
@click.argument('id', metavar='<domain ID>', required=True)
@click.option('--filter', metavar='<filter>',
              help='Filter for assigned, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def floatingip_list(ctx, id, filter):
    """List floating IP for a given domain ID"""
    if filter == None:
        result = ctx.obj['nc'].get("domains/%s/floatingips" %id)
    else :
        result = ctx.obj['nc'].get("domains/%s/floatingips" %id, filter=filter)
    table=PrettyTable(["ID", "address", "assigned", "externalID"])
    for line in result:
        table.add_row( [ line['ID'],
                        line['address'],
                        line['assigned'],
                        line['externalID'] ] )
    print table

@vsdcli.command(name='floatingip-show')
@click.argument('floatingip-id', metavar='<floatingip-id>', required=True)
@click.pass_context
def floatingip_show(ctx, floatingip_id):
    """Show information for a given floating IP id"""
    result = ctx.obj['nc'].get("floatingips/%s" %floatingip_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='permission-list')
@click.option('--zone-id', metavar='<id>')
@click.option('--domaintemplate-id', metavar='<id>')
@click.option('--redundancygroup-id', metavar='<id>')
@click.option('--gateway-id', metavar='<id>')
@click.option('--vlan-id', metavar='<id>')
@click.option('--domain-id', metavar='<id>')
@click.option('--service-id', metavar='<id>')
@click.option('--port-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--l2domaintemplate-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def permission_list(ctx, filter, **ids):
    """List all permissions"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/permissions" %(id_type, id)
    if filter == None :
        result = ctx.obj['nc'].get(request)
    else :
        result = ctx.obj['nc'].get(request, filter=filter)
    table=PrettyTable(["ID", "Action", "Entity ID", "Entity type", "Entity name"])
    for line in result:
        table.add_row([line['ID'],
                       line['permittedAction'],
                       line['permittedEntityID'],
                       line['permittedEntityType'],
                       line['permittedEntityName'] ] )
    print table

@vsdcli.command(name='permission-show')
@click.argument('permission-id', metavar='<permission-id>', required=True)
@click.pass_context
def permission_show(ctx, permission_id):
    """Show information for a given permission id"""
    result = ctx.obj['nc'].get("permissions/%s" %permission_id)[0]
    print_object( result, only=ctx.obj['show_only'] )

@vsdcli.command(name='add-permission')
@click.argument('entity-id', metavar='<group or user ID>', required=True)
@click.option('--action', type=click.Choice(['USE',
                                             'EXTEND',
                                             'READ',
                                             'INSTANTIATE']),
              default='USE', help='Default : USE')
@click.option('--zone-id', metavar='<id>')
@click.option('--domaintemplate-id', metavar='<id>')
@click.option('--redundancygroup-id', metavar='<id>')
@click.option('--gateway-id', metavar='<id>')
@click.option('--vlan-id', metavar='<id>')
@click.option('--domain-id', metavar='<id>')
@click.option('--service-id', metavar='<id>')
@click.option('--port-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--l2domaintemplate-id', metavar='<id>')
@click.option('--zone-id', metavar='<id>')
@click.pass_context
def add_permission(ctx, entity_id, action, **ids):
    """Add permission for a given element (Domain, Zone, L2Domain, etc...)"""
    id_type, id = check_id(**ids)
    params = {}
    params['permittedEntityID'] = entity_id
    params['permittedAction'] = action
    ctx.obj['nc'].post("%ss/%s/permissions" %(id_type, id), params)


@vsdcli.command(name='enterprisepermission-list')
@click.option('--redundancygroup-id', metavar='<id>')
@click.option('--gateway-id', metavar='<id>')
@click.option('--vlan-id', metavar='<id>')
@click.option('--service-id', metavar='<id>')
@click.option('--port-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def enterprisepermission_list(ctx, filter, **ids):
    """List all Enterprise Permission for a CSP entity"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/enterprisepermissions" %(id_type, id)
    if filter == None :
        result = ctx.obj['nc'].get(request)
    else :
        result = ctx.obj['nc'].get(request, filter=filter)
    table=PrettyTable(["ID", "Action", "Entity ID", "Entity type", "Entity name"])
    for line in result:
        table.add_row([line['ID'],
                       line['permittedAction'],
                       line['permittedEntityID'],
                       line['permittedEntityType'],
                       line['permittedEntityName'] ])
    print table


@vsdcli.command(name='enterprisepermission-show')
@click.argument('enterprisepermission-id', metavar='<enterprisepermission-id>', required=True)
@click.pass_context
def enterprisepermission_show(ctx, permission_id):
    """Show information for a given enterprisepermission id"""
    result = ctx.obj['nc'].get("enterprisepermissions/%s" %enterprisepermission_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='enterprisepermission-create')
@click.argument('entity-id', metavar='<group or user ID>', required=True)
@click.option('--action', type=click.Choice(['USE',
                                             'EXTEND',
                                             'READ',
                                             'INSTANTIATE']),
              default='USE', help='Default : USE')
@click.option('--redundancygroup-id', metavar='<id>')
@click.option('--gateway-id', metavar='<id>')
@click.option('--vlan-id', metavar='<id>')
@click.option('--service-id', metavar='<id>')
@click.option('--port-id', metavar='<id>')
@click.pass_context
def enterprisepermission_create(ctx, entity_id, action, **ids):
    """Add permission for a given element (gateway, vlan, etc...)"""
    id_type, id = check_id(**ids)
    params = {}
    params['permittedEntityID'] = entity_id
    params['permittedAction'] = action
    ctx.obj['nc'].post("%ss/%s/enterprisepermissions" %(id_type, id), params)


@vsdcli.command(name='port-list')
@click.option('--redundancygroup-id', metavar='<id>')
@click.option('--gateway-id', metavar='<id>')
@click.option('--autodiscoveredgateway-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, physicalName, portType, userMnemonic, useUserMnemonic, name, description, physicalName, portType, VLANRange, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def port_list(ctx, filter, **ids):
    """List all port for a given redundancygroup, gateway or autodiscoveredgateway"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/ports" %(id_type, id)
    if filter == None :
        result = ctx.obj['nc'].get(request)
    else :
        result = ctx.obj['nc'].get(request, filter=filter)
    table=PrettyTable(["ID", "name", "physicalName"])
    for line in result:
        table.add_row([line['ID'],
                       line['name'],
                       line['physicalName'] ])
    print table


@vsdcli.command(name='port-show')
@click.argument('port-id', metavar='<port-id>', required=True)
@click.pass_context
def port_show(ctx, port_id):
    """Show information for a given port id"""
    result = ctx.obj['nc'].get("ports/%s" % port_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='port-update')
@click.argument('port-id', metavar='<port ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def port_update(ctx, port_id, key_value):
    """Update key/value for a given port"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':',1)
        params[key] = value
    ctx.obj['nc'].put("ports/%s" %port_id, params)
    result = ctx.obj['nc'].get("ports/%s" %port_id)[0]
    print_object( result, only=ctx.obj['show_only'] )


@vsdcli.command(name='vlan-list')
@click.option('--port-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for value, userMnemonic, useUserMnemonic, description, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def vlan_list(ctx, filter, port_id):
    """List all port for a given port"""
    result = ctx.obj['nc'].get("ports/%s/vlans" % port_id, filter=filter)
    table=PrettyTable(["ID", "name", "value", "userMnemonic"])
    for line in result:
        table.add_row([line['ID'],
                       line['description'],
                       line['value'],
                       line['userMnemonic']])
    print table


@vsdcli.command(name='vlan-show')
@click.argument('vlan-id', metavar='<vlan-id>', required=True)
@click.pass_context
def vlan_show(ctx, vlan_id):
    """Show information for a given vlan id"""
    result = ctx.obj['nc'].get("vlans/%s" % vlan_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='vlan-create')
@click.option('--port-id', metavar='<id>', required=True)
@click.option('--vlan', metavar='<vlan number>', required=True)
@click.option('--mnemonic', metavar='<user Mnemonic>')
@click.option('--description', metavar='<description>')
@click.pass_context
def vlan_create(ctx, port_id, vlan, mnemonic, description):
    """Add vlan for a given port"""
    params = {}
    if mnemonic is not None:
        params['userMnemonic'] = mnemonic
        params['useUserMnemonic'] = True
    if description is not None:
        params['description'] = description
    #TODO: Check vlan is able to be converted.
    params['value'] = int(vlan)
    result = ctx.obj['nc'].post("ports/%s/vlans" % port_id, params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='vlan-update')
@click.argument('vlan-id', metavar='<vlan ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def vlan_update(ctx, vlan_id, key_value):
    """Update key/value for a given vlan"""
    params = {}
    for kv in key_value:
        #TODO : check key_value is "str:str" in order to be parsable
        key, value = kv.split(':',1)
        params[key] = value
    ctx.obj['nc'].put("vlans/%s" %vlan_id, params)
    result = ctx.obj['nc'].get("vlans/%s" % vlan_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='vlan-delete')
@click.argument('vlan-id', metavar='<vlan ID>', required=True)
@click.pass_context
def vlan_delete(ctx, vlan_id):
    """Delete a given vlan"""
    ctx.obj['nc'].delete("vlans/%s" %vlan_id)


@vsdcli.command(name='egressacltemplate-list')
@click.option('--l2domaintemplate-id', metavar='<id>')
@click.option('--domaintemplate-id', metavar='<id>')
@click.option('--domain-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, physicalName, portType, userMnemonic, useUserMnemonic, name, description, physicalName, portType, VLANRange, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def egressacltemplate_list(ctx, filter, **ids):
    """List all egress acl template for a given l2domaintemplate, domaintemplate, domain or l2domain"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/egressacltemplates" %(id_type, id)
    result = ctx.obj['nc'].get(request, filter=filter)
    table=PrettyTable(["ID", "name", "active", "defaultAllowIP", "defaultAllowNonIP"])
    for line in result:
        table.add_row([line['ID'],
                       line['name'],
                       line['active'],
                       line['defaultAllowIP'],
                       line['defaultAllowNonIP'] ])
    print table


@vsdcli.command(name='egressacltemplate-show')
@click.argument('egressacltemplate-id', metavar='<port-id>', required=True)
@click.pass_context
def egressacltemplate_show(ctx, egressacltemplate_id):
    """Show information for a given egressacltemplate id"""
    result = ctx.obj['nc'].get("egressacltemplates/%s" % egressacltemplate_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='egressacltemplate-update')
@click.argument('egressacltemplate-id', metavar='<egressacltemplate ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def egressacltemplate_update(ctx, egressacltemplate_id, key_value):
    """Update key/value for a given egressacltemplate"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':',1)
        params[key] = value
    ctx.obj['nc'].put("egressacltemplates/%s?responseChoice=1" % egressacltemplate_id, params)
    result = ctx.obj['nc'].get("egressacltemplates/%s" % egressacltemplate_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='egressacltemplate-delete')
@click.argument('egressacltemplate-id', metavar='<egressacltemplate ID>', required=True)
@click.pass_context
def egressacltemplate_delete(ctx, egressacltemplate_id):
    """Delete a given egressacltemplate"""
    ctx.obj['nc'].delete("egressacltemplates/%s?responseChoice=1" % egressacltemplate_id)


@vsdcli.command(name='egressacltemplate-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--domain-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--domaintemplate-id', metavar='<id>')
@click.option('--l2domaintemplate-id', metavar='<id>')
@click.pass_context
def egressacltemplate_create(ctx, name, **ids):
    """Add an Egress ACL template to a given domain, l2domain, domaintemplate or l2domaintemplate"""
    id_type, id = check_id(**ids)
    params = {'name' : name}
    result = ctx.obj['nc'].post("%ss/%s/egressacltemplates" % (id_type, id), params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='ingressacltemplate-list')
@click.option('--l2domaintemplate-id', metavar='<id>')
@click.option('--domaintemplate-id', metavar='<id>')
@click.option('--domain-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for allowL2AddressSpoof, defaultAllowIP, defaultAllowNonIP, name, description, active, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def ingressacltemplate_list(ctx, filter, **ids):
    """List all ingress acl template for a given l2domaintemplate, domaintemplate, domain or l2domain"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/ingressacltemplates" %(id_type, id)
    result = ctx.obj['nc'].get(request, filter=filter)
    table=PrettyTable(["ID", "name", "active", "defaultAllowIP", "defaultAllowNonIP", "allowL2AddressSpoof"])
    for line in result:
        table.add_row([line['ID'],
                       line['name'],
                       line['active'],
                       line['defaultAllowIP'],
                       line['defaultAllowNonIP'],
                       line['allowL2AddressSpoof']])
    print table


@vsdcli.command(name='ingressacltemplate-show')
@click.argument('ingressacltemplate-id', metavar='<id>', required=True)
@click.pass_context
def ingressacltemplate_show(ctx, ingressacltemplate_id):
    """Show information for a given ingressacltemplate id"""
    result = ctx.obj['nc'].get("ingressacltemplates/%s" % ingressacltemplate_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='ingressacltemplate-update')
@click.argument('ingressacltemplate-id', metavar='<ingressacltemplate ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def ingressacltemplate_update(ctx, ingressacltemplate_id, key_value):
    """Update key/value for a given ingressacltemplate"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':',1)
        params[key] = value
    ctx.obj['nc'].put("ingressacltemplates/%s?responseChoice=1" % ingressacltemplate_id, params)
    result = ctx.obj['nc'].get("ingressacltemplates/%s" % ingressacltemplate_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='ingressacltemplate-delete')
@click.argument('ingressacltemplate-id', metavar='<ingressacltemplate ID>', required=True)
@click.pass_context
def ingressacltemplate_delete(ctx, ingressacltemplate_id):
    """Delete a given ingressacltemplate"""
    ctx.obj['nc'].delete("ingressacltemplates/%s?responseChoice=1" % ingressacltemplate_id)


@vsdcli.command(name='ingressacltemplate-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--domain-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--domaintemplate-id', metavar='<id>')
@click.option('--l2domaintemplate-id', metavar='<id>')
@click.pass_context
def ingressacltemplate_create(ctx, name, **ids):
    """Add an Ingress ACL template to a given domain, l2domain, domaintemplate or l2domaintemplate"""
    id_type, id = check_id(**ids)
    params = {'name' : name}
    result = ctx.obj['nc'].post("%ss/%s/ingressacltemplates" % (id_type, id), params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='vport-list')
@click.option('--domain-id', metavar='<id>')
@click.option('--floatingip-id', metavar='<id>')
@click.option('--vrs-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--vporttag-id', metavar='<id>')
@click.option('--subnet-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, type, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def vport_list(ctx, filter, **ids):
    """List all ingress acl template for a given domain, l2domain, floatingip, vrs or vporttag"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/vports" %(id_type, id)
    result = ctx.obj['nc'].get(request, filter=filter)
    table=PrettyTable(["ID", "name", "active", "type"])
    for line in result:
        table.add_row([line['ID'],
                       line['name'],
                       line['active'],
                       line['type']])
    print table


@vsdcli.command(name='vport-show')
@click.argument('vport-id', metavar='<id>', required=True)
@click.pass_context
def vport_show(ctx, vport_id):
    """Show information for a given vport id"""
    result = ctx.obj['nc'].get("vports/%s" % vport_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='vport-update')
@click.argument('vport-id', metavar='<ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def vport_update(ctx, vport_id, key_value):
    """Update key/value for a given vport"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':',1)
        params[key] = value
    ctx.obj['nc'].put("vports/%s" % vport_id, params)
    result = ctx.obj['nc'].get("vports/%s" % vport_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='vport-delete')
@click.argument('vport-id', metavar='<ID>', required=True)
@click.pass_context
def vport_delete(ctx, vport_id):
    """Delete a given vport"""
    ctx.obj['nc'].delete("vports/%s" % vport_id)


@vsdcli.command(name='vport-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--type',
              type=click.Choice(['VM',
                                 'HOST',
                                 'BRIDGE']),
              required=True)
@click.option('--active/--no-active', required=True)
@click.option('--address-spoofing',
              type=click.Choice(['ENABLED',
                                 'DISABLED',
                                 'INHERITED']),
              required=True)
@click.option('--subnet-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.pass_context
def vport_create(ctx, name, type, active, address_spoofing, **ids):
    """Add an vport to a given subnet or l2domain"""
    id_type, id = check_id(**ids)
    params = {'name' : name,
              'type': type,
              'active': active,
              'addressSpoofing': address_spoofing}
    result = ctx.obj['nc'].post("%ss/%s/vports" % (id_type, id), params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='bridgeinterface-list')
@click.option('--domain-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--vport-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, type, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def bridgeinterface_list(ctx, filter, **ids):
    """List all bridge interface for a given domain, l2domain or vport"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/bridgeinterfaces" %(id_type, id)
    result = ctx.obj['nc'].get(request, filter=filter)
    table=PrettyTable(["ID", "name", "VPortID"])
    for line in result:
        table.add_row([line['ID'],
                       line['name'],
                       line['VPortID']])
    print table


@vsdcli.command(name='bridgeinterface-show')
@click.argument('bridgeinterface-id', metavar='<id>', required=True)
@click.pass_context
def bridgeinterface_show(ctx, bridgeinterface_id):
    """Show information for a given bridgeinterface id"""
    result = ctx.obj['nc'].get("bridgeinterfaces/%s" % bridgeinterface_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='bridgeinterface-update')
@click.argument('bridgeinterface-id', metavar='<ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def bridgeinterface_update(ctx, bridgeinterface_id, key_value):
    """Update key/value for a given bridgeinterface"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':',1)
        params[key] = value
    ctx.obj['nc'].put("bridgeinterfaces/%s" % bridgeinterface_id, params)
    result = ctx.obj['nc'].get("bridgeinterfaces/%s" % bridgeinterface_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='bridgeinterface-delete')
@click.argument('bridgeinterface-id', metavar='<ID>', required=True)
@click.pass_context
def bridgeinterface_delete(ctx, bridgeinterface_id):
    """Delete a given bridgeinterface"""
    ctx.obj['nc'].delete("bridgeinterfaces/%s" % bridgeinterface_id)


@vsdcli.command(name='bridgeinterface-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--vport-id', metavar='<ID>', required=True)
@click.pass_context
def bridgeinterface_create(ctx, name, vport_id):
    """Add an bridge interface to a given vport"""
    params = {'name' : name}
    result = ctx.obj['nc'].post("vports/%s/bridgeinterfaces" % vport_id, params)[0]
    print_object(result, only=ctx.obj['show_only'])


def main():
    vsdcli(obj={})

if __name__ == '__main__':
    main()
