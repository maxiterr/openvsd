from vsd_common import *


@vsdcli.command(name='subnet-list')
@click.option('--zone-id', metavar='<id>')
@click.option('--domain-id', metavar='<id>')
@click.option('--app-id', metavar='<id>')
@click.option('--subnettemplate-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for address, netmask, IPType, name, gateway, '
                   'description, serviceID, assocApplicationObjectType, '
                   'splitSubnet, proxyARP, enableMulticast, externalID')
@click.pass_context
def subnet_list(ctx, filter, **ids):
    """List subnets for a given zone, app, subnettemplate, or domain id"""
    id_type, id = check_id(**ids)
    if not filter:
        result = ctx.obj['nc'].get("%ss/%s/subnets" % (id_type, id))
    else:
        result = ctx.obj['nc'].get("%ss/%s/subnets" % (id_type, id),
                                   filter=filter)
    table = PrettyTable(["Subnet ID",
                         "Name",
                         "Address",
                         "Gateway",
                         "RT / RD",
                         "External ID"])
    for line in result:
        if line['address']:
            address = line['address'] + "/" + \
                netmask_to_length(line['netmask'])
        else:
            address = "None"
        rt_rd = line['routeTarget'] + " / " + line['routeDistinguisher']
        table.add_row([line['ID'],
                       line['name'],
                       address,
                       line['gateway'],
                       rt_rd,
                       line['externalID']])
    print table


@vsdcli.command(name='subnet-show')
@click.argument('subnet-id', metavar='<subnet-id>', required=True)
@click.pass_context
def subnet_show(ctx, subnet_id):
    """Show information for a given subnet id"""
    result = ctx.obj['nc'].get("subnets/%s" % subnet_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='subnet-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--zone-id', metavar='<zone ID>', required=True)
@click.option('--address', metavar='<address>', required=True)
@click.option('--netmask', metavar='<netmask>', required=True)
@click.option('--gateway', metavar='<gateway>')
@click.option('--rd', metavar='<route distinguisher>')
@click.option('--rt', metavar='<route target>')
@click.pass_context
def subnet_create(ctx, name, zone_id, address, gateway, netmask, rt, rd):
    """Add a subnet to the VSD for an given zone"""
    # Define mandotory values
    params = {'name':    name,
              'address': address,
              'netmask': netmask}
    # Define optionnal values
    if gateway:
        params['gateway'] = gateway
    if rt:
        params['routeTarget'] = rt
    if rd:
        params['routeDistinguisher'] = rd
    result = ctx.obj['nc'].post("zones/%s/subnets" % zone_id, params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='subnet-update')
@click.argument('subnet-id', metavar='<subnet ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def subnet_update(ctx, subnet_id, key_value):
    """Update key/value for a given subnet"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':', 1)
        params[key] = value
    ctx.obj['nc'].put("subnets/%s" % subnet_id, params)
    result = ctx.obj['nc'].get("subnets/%s" % subnet_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='subnet-delete')
@click.argument('subnet-id', metavar='<subnet ID>', required=True)
@click.pass_context
def subnet_delete(ctx, subnet_id):
    """Delete a given subnet"""
    ctx.obj['nc'].delete("subnets/%s" % subnet_id)


@vsdcli.command(name='shared-network-list')
@click.option(
    '--filter', metavar='<filter>',
    help='Filter for name, description, address, netmask, gateway, '
         'type, domainRouteDistinguisher, domainRouteTarget, externalID'
)
@click.pass_context
def shared_network_list(ctx, filter):
    """List all shared network ressource"""
    if not filter:
        result = ctx.obj['nc'].get("sharednetworkresources")
    else:
        result = ctx.obj['nc'].get("sharednetworkresources", filter=filter)
    table = PrettyTable(["ID",
                         "Name",
                         "Description",
                         "Type",
                         "Address",
                         "Gateway",
                         "RT / RD"])
    for line in result:
        table.add_row([
            line['ID'],
            line['name'],
            line['description'],
            line['type'],
            line['address'] + "/" + netmask_to_length(line['netmask']),
            line['gateway'],
            ' / '.join([
                line['domainRouteTarget'],
                line['domainRouteDistinguisher']])
        ])
    print table


@vsdcli.command(name='shared-network-show')
@click.argument('shared-network-id', metavar='<shared-network ID>',
                required=True)
@click.pass_context
def shared_network_show(ctx, shared_network_id):
    """Show information for a given shared-network ID"""
    result = ctx.obj['nc'].get("sharednetworkresources/%s" %
                               shared_network_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='l2domain-list')
@click.option('--l2domaintemplate-id', metavar='<id>')
@click.option('--enterprise-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for description, name, serviceID, description, '
                   'name, lastUpdatedDate, creationDate, externalID')
@click.pass_context
def l2domain_list(ctx, filter, **ids):
    """List L2 domain for a given enterprise or l2 domain template"""
    id_type, id = check_id(**ids)
    if not filter:
        result = ctx.obj['nc'].get("%ss/%s/l2domains" % (id_type, id))
    else:
        result = ctx.obj['nc'].get("%ss/%s/l2domains" % (id_type, id),
                                   filter=filter)
    table = PrettyTable(["L2 Domain ID", "Name", "Description", "RT / RD"])
    for line in result:
        table.add_row([
            line['ID'],
            line['name'],
            line['description'],
            line['routeTarget'] + " / " + line['routeDistinguisher']
        ])
    print table


@vsdcli.command(name='l2domain-show')
@click.argument('l2domain-id', metavar='<l2domain-id>', required=True)
@click.pass_context
def l2domain_show(ctx, l2domain_id):
    """Show information for a given l2 domain id"""
    result = ctx.obj['nc'].get("l2domains/%s" % l2domain_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='l2domain-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--enterprise-id', metavar='<enterprise ID>', required=True)
@click.option('--template-id', metavar='<template ID>', required=True)
@click.option('--rd', metavar='<route distinguisher>')
@click.option('--rt', metavar='<route target>')
@click.pass_context
def l2domain_create(ctx, name, enterprise_id, template_id, rt, rd):
    """Add an l2 domain to the VSD for an given enterprise"""
    params = {'name':       name,
              'templateID': template_id}
    if rt:
        params['routeTarget'] = rt
    if rd:
        params['routeDistinguisher'] = rd
    result = ctx.obj['nc'].post("enterprises/%s/l2domains" %
                                enterprise_id, params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='l2domain-delete')
@click.argument('l2domain-id', metavar='<l2domain ID>', required=True)
@click.pass_context
def l2domain_delete(ctx, domain_id):
    """Delete a given l2 domain"""
    ctx.obj['nc'].delete("l2domains/%s" % domain_id)


@vsdcli.command(name='l2domain-update')
@click.argument('l2domain-id', metavar='<domain ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def l2domain_update(ctx, l2domain_id, key_value):
    """Update key/value for a given l2 domain"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':', 1)
        params[key] = value
    ctx.obj['nc'].put("l2domains/%s" % l2domain_id, params)
    result = ctx.obj['nc'].get("l2domains/%s" % l2domain_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='floatingip-list')
@click.argument('id', metavar='<domain ID>', required=True)
@click.option('--filter', metavar='<filter>',
              help='Filter for assigned, lastUpdatedDate, creationDate, '
                   'externalID')
@click.pass_context
def floatingip_list(ctx, id, filter):
    """List floating IP for a given domain ID"""
    if not filter:
        result = ctx.obj['nc'].get("domains/%s/floatingips" % id)
    else:
        result = ctx.obj['nc'].get("domains/%s/floatingips" % id,
                                   filter=filter)
    table = PrettyTable(["ID", "address", "assigned", "externalID"])
    for line in result:
        table.add_row([line['ID'],
                       line['address'],
                       line['assigned'],
                       line['externalID']])
    print table


@vsdcli.command(name='floatingip-show')
@click.argument('floatingip-id', metavar='<floatingip-id>', required=True)
@click.pass_context
def floatingip_show(ctx, floatingip_id):
    """Show information for a given floating IP id"""
    result = ctx.obj['nc'].get("floatingips/%s" % floatingip_id)[0]
    print_object(result, only=ctx.obj['show_only'])
