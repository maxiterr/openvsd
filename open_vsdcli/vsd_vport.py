from open_vsdcli.vsd_common import *


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
    print(table)


@vsdcli.command(name='vport-list')
@click.option('--domain-id', metavar='<id>')
@click.option('--floatingip-id', metavar='<id>')
@click.option('--vrs-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--vporttag-id', metavar='<id>')
@click.option('--subnet-id', metavar='<id>')
@click.option('--trunk-id', metavar='<id>')
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
    if id_type == "trunk":
        table = PrettyTable(["ID",
                             "name",
                             "active",
                             "type",
                             "Trunk role",
                             "Vlan"])
        for line in result:
            table.add_row([line['ID'],
                           line['name'],
                           line['active'],
                           line['type'],
                           line['trunkRole'],
                           line['segmentationID']])
    else:
        table = PrettyTable(["ID", "name", "active", "type"])
        for line in result:
            table.add_row([line['ID'],
                           line['name'],
                           line['active'],
                           line['type']])
    print(table)


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


@vsdcli.command(name='trunk-list')
@click.option('--enterprise-id', metavar='<id>')
@click.option('--vport-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for name or externalID')
@click.pass_context
def trunk_list(ctx, filter, **ids):
    """List all trunk in enterprise or attach to a vport"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/trunks" % (id_type, id)
    result = ctx.obj['nc'].get(request, filter=filter)

    table = PrettyTable(["ID", "name", "associatedVPortID"])
    for line in result:
        table.add_row([line['ID'],
                       line['name'],
                       line['associatedVPortID']])
    print(table)


@vsdcli.command(name='trunk-show')
@click.argument('trunk-id', metavar='<id>', required=True)
@click.pass_context
def trunk_show(ctx, trunk_id):
    """Show information for a given trunk id"""
    result = ctx.obj['nc'].get("trunks/%s" % trunk_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='trunk-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--vport-id', metavar='<ID>', required=True)
@click.option('--enterprise-id', metavar='<ID>',
              help='if ommited, try to extracted from vport parent')
@click.pass_context
def trunk_create(ctx, name, vport_id, enterprise_id):
    """Add an bridge interface to a given vport"""
    if not enterprise_id:
        result = ctx.obj['nc'].get("vports/%s" % vport_id)[0]
        if result['parentType'] == 'subnet':
            parent_id = result['domainID']
            parent_type = 'domain'
        else:
            parent_id = result['parentID']
            parent_type = 'l2domain'
        enterprise_id = result = ctx.obj['nc'].get(
                "%ss/%s" % (parent_type, parent_id))[0]['parentID']
    params = {'name': name,
              'associatedVPortID': vport_id}
    result = ctx.obj['nc'].post("enterprises/%s/trunks" % enterprise_id,
                                params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='trunk-delete')
@click.argument('trunk-id', metavar='<ID>', required=True)
@click.option('--force',  is_flag=True,
              help='Force deletion even there is sub-vport')
@click.pass_context
def trunk_delete(ctx, trunk_id, force):
    """Delete a given trunk"""
    request = "trunks/%s" % trunk_id
    if force:
        result = ctx.obj['nc'].delete(request + "?responseChoice=1")
    else:
        # Check if there is more than 1 vport
        result = ctx.obj['nc'].get("trunks/%s/vports" % trunk_id)
        sub_port_count = sum(map(lambda x: x['trunkRole'] == 'SUB_PORT',
                                 result))
        if sub_port_count > 0:
            print("Error: There is %s sub-port attached. "
                  "Use --force to delete" % sub_port_count)
            exit(1)
        else:
            result = ctx.obj['nc'].delete(request)


@vsdcli.command(name='virtualip-list')
@click.option('--redirectiontargets-id', metavar='<id>')
@click.option('--vport-id', metavar='<id>')
@click.option('--subnet-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for Virtual IP, externalID or IP type (IPV4 or 6)')
@click.pass_context
def virtualip_list(ctx, filter, **ids):
    """List all virtual IP associated to a vport, a redirection target"""
    """or a subnet"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/virtualips" % (id_type, id)
    result = ctx.obj['nc'].get(request, filter=filter)

    table = PrettyTable(['ID',
                         'Virtual IP',
                         'MAC',
                         'Parent type',
                         'Parent ID'])
    for line in result:
        table.add_row([line['ID'],
                       line['virtualIP'],
                       line['MAC'],
                       line['parentType'],
                       line['parentID']])
    print(table)


@vsdcli.command(name='virtualip-show')
@click.argument('virtualip-id', metavar='<id>', required=True)
@click.pass_context
def virtualip_show(ctx, virtualip_id):
    """Show information for a given virtual ip id"""
    result = ctx.obj['nc'].get("virtualips/%s" % virtualip_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='virtualip-delete')
@click.argument('virtualip-id', metavar='<ID>', required=True)
@click.pass_context
def virtualip_delete(ctx, virtualip_id):
    """Delete a given virtual ip"""
    ctx.obj['nc'].delete("virtualips/%s" % virtualip_id)


@vsdcli.command(name='virtualip-create')
@click.option('--vport-id', metavar='<ID>', required=True)
@click.option('--virtualip', metavar='<IP>', required=True)
@click.option('--mac-from-vm', is_flag=True,
              help='Get the MAC address from the VM interface belong'
              ' to this vport')
@click.option('--mac', metavar='<mac>', help='Incompatible with same-as-vm')
@click.pass_context
def virtualip_create(ctx, virtualip, vport_id, mac_from_vm, mac):
    """Add a virtual ip to a given vport"""
    params = {'virtualIP': virtualip}
    if mac_from_vm:
        if mac:
            raise click.exceptions.UsageError(
                "When you activate mac-from-vm, do not use the mac option")
        result = ctx.obj['nc'].get("vports/%s/vminterfaces" % vport_id)[0]
        if result['MAC']:
            params['MAC'] = result['MAC']
    if mac:
        params['MAC'] = mac
    result = ctx.obj['nc'].post("vports/%s/virtualips" % vport_id,
                                params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='virtualip-update')
@click.argument('virtualip-id', metavar='<ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def virtualip_update(ctx, virtualip_id, key_value):
    """Update key/value for a given virtualip"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':', 1)
        params[key] = value
    ctx.obj['nc'].put("virtualips/%s" % virtualip_id, params)
    result = ctx.obj['nc'].get("virtualips/%s" % virtualip_id)[0]
    print_object(result, only=ctx.obj['show_only'])
