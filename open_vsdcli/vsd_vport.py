from vsd_common import *


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
    request = "%ss/%s/vporttags" % (id_type, id)
    if not filter:
        result = ctx.obj['nc'].get(request)
    else:
        result = ctx.obj['nc'].get(request, filter=filter)
    table = PrettyTable(["ID", "Description", "Name", "endPoint Type"])
    for line in result:
        table.add_row([line['ID'],
                       line['description'],
                       line['name'],
                       line['endPointType']])
    print table


@vsdcli.command(name='vport-list')
@click.option('--domain-id', metavar='<id>')
@click.option('--floatingip-id', metavar='<id>')
@click.option('--vrs-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--vporttag-id', metavar='<id>')
@click.option('--subnet-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, type, lastUpdatedDate, creationDate, '
                   'externalID')
@click.pass_context
def vport_list(ctx, filter, **ids):
    """List all ingress acl template for a given domain, l2domain, floatingip,
       vrs or vporttag"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/vports" % (id_type, id)
    result = ctx.obj['nc'].get(request, filter=filter)
    table = PrettyTable(["ID", "name", "active", "type"])
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
        key, value = kv.split(':', 1)
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
@click.option('--vlan-id', metavar='<id>',
              help='Required for BRIDGE and HOST creation')
@click.option('--subnet-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.pass_context
def vport_create(ctx, name, type, active, address_spoofing, vlan_id, **ids):
    """Add an vport to a given subnet or l2domain"""
    id_type, id = check_id(**ids)
    params = {'name':            name,
              'type':            type,
              'active':          active,
              'addressSpoofing': address_spoofing}
    if vlan_id:
        params['VLANID'] = vlan_id
    result = ctx.obj['nc'].post("%ss/%s/vports" % (id_type, id), params)[0]
    print_object(result, only=ctx.obj['show_only'])


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
        key, value = kv.split(':', 1)
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
    params = {'name': name}
    result = ctx.obj['nc'].post("vports/%s/bridgeinterfaces" % vport_id,
                                params)[0]
    print_object(result, only=ctx.obj['show_only'])
