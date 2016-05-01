from vsd_common import *


@vsdcli.command(name='gateway-list')
@click.option('--enterprise-id', metavar='<ID>')
@click.option('--redundancygroup-id', metavar='<ID>')
@click.option('--filter', metavar='<filter>',
              help='Filter for pending, systemID, name, description, '
                   'personality, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def gateway_list_list(ctx, enterprise_id, redundancygroup_id, filter):
    """list gateways for a given enterprise or group id"""
    if enterprise_id:
        url_request = "enterprises/%s/gateways" % enterprise_id
    elif redundancygroup_id:
        url_request = "redundancygroups/%s/gateways" % redundancygroup_id
    else:
        url_request = "gateways"
    if not filter:
        result = ctx.obj['nc'].get(url_request)
    else:
        result = ctx.obj['nc'].get(url_request, filter=filter)
    table = PrettyTable(["ID",
                         "System ID",
                         "Name",
                         "Description",
                         "Pending",
                         "Redundancy Group ID",
                         "Personality"])
    for line in result:
        table.add_row([line['ID'],
                       line['systemID'],
                       line['name'],
                       line['description'],
                       line['pending'],
                       line['redundancyGroupID'],
                       line['personality']])
    print table


@vsdcli.command(name='gateway-show')
@click.argument('gateway-id', metavar='<gateway ID>', required=True)
@click.pass_context
def group_show(ctx, gateway_id):
    """Show information for a given gateway ID"""
    result = ctx.obj['nc'].get("gateways/%s" % gateway_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='gateway-update')
@click.argument('gateway-id', metavar='<gateway ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def gateway_update(ctx, gateway_id, key_value):
    """Update key/value for a given gateway"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':', 1)
        params[key] = value
    ctx.obj['nc'].put("gateways/%s" % gateway_id, params)
    result = ctx.obj['nc'].get("gateways/%s" % gateway_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='port-list')
@click.option('--redundancygroup-id', metavar='<id>')
@click.option('--gateway-id', metavar='<id>')
@click.option('--autodiscoveredgateway-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, physicalName, portType, userMnemonic, '
                   'useUserMnemonic, name, description, physicalName, '
                   'portType, VLANRange, lastUpdatedDate, creationDate, '
                   'externalID')
@click.pass_context
def port_list(ctx, filter, **ids):
    """List all port for a given redundancygroup, gateway or
       autodiscoveredgateway"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/ports" % (id_type, id)
    if not filter:
        result = ctx.obj['nc'].get(request)
    else:
        result = ctx.obj['nc'].get(request, filter=filter)
    table = PrettyTable(["ID", "name", "physicalName", "Type"])
    for line in result:
        table.add_row([line['ID'],
                       line['name'],
                       line['physicalName'],
                       line['portType']])
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
        key, value = kv.split(':', 1)
        params[key] = value
    ctx.obj['nc'].put("ports/%s" % port_id, params)
    result = ctx.obj['nc'].get("ports/%s" % port_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='vlan-list')
@click.option('--port-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for value, userMnemonic, useUserMnemonic, '
                   'description, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def vlan_list(ctx, filter, port_id):
    """List all port for a given port"""
    result = ctx.obj['nc'].get("ports/%s/vlans" % port_id, filter=filter)
    table = PrettyTable(["ID", "name", "value", "userMnemonic"])
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
    if mnemonic:
        params['userMnemonic'] = mnemonic
        params['useUserMnemonic'] = True
    if description:
        params['description'] = description
    # TODO: Check vlan is able to be converted.
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
        # TODO : check key_value is "str:str" in order to be parsable
        key, value = kv.split(':', 1)
        params[key] = value
    ctx.obj['nc'].put("vlans/%s" % vlan_id, params)
    result = ctx.obj['nc'].get("vlans/%s" % vlan_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='vlan-delete')
@click.argument('vlan-id', metavar='<vlan ID>', required=True)
@click.pass_context
def vlan_delete(ctx, vlan_id):
    """Delete a given vlan"""
    ctx.obj['nc'].delete("vlans/%s" % vlan_id)


@vsdcli.command(name='bridgeinterface-list')
@click.option('--domain-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--vport-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, type, lastUpdatedDate, creationDate, '
                   'externalID')
@click.pass_context
def bridgeinterface_list(ctx, filter, **ids):
    """List all bridge interface for a given domain, l2domain or vport"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/bridgeinterfaces" % (id_type, id)
    result = ctx.obj['nc'].get(request, filter=filter)
    table = PrettyTable(["ID", "name", "VPortID"])
    for line in result:
        table.add_row([line['ID'],
                       line['name'],
                       line['VPortID']])
    print table
