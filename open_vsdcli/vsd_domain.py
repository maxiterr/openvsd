from open_vsdcli.vsd_common import *


@vsdcli.command(name='domaintemplate-list')
@click.option('--enterprise-id', metavar='<enterprise ID>', required=True)
@click.option('--filter', metavar='<filter>',
              help='Filter for NEED TO BE UPDATED')
@click.pass_context
def domaintemplate_list(ctx, enterprise_id, filter):
    """Show all domaintemplate for a given enterprise id"""
    result = ctx.obj['nc'].get("enterprises/%s/domaintemplates" %
                               enterprise_id, filter=filter)
    table = PrettyTable(["Domain Template ID", "Name"])
    for line in result:
        table.add_row([line['ID'],
                       line['name']])
    print(table)


@vsdcli.command(name='domaintemplate-show')
@click.argument('domaintemplate-id', metavar='<domaintemplate-id>',
                required=True)
@click.pass_context
def domaintemplate_show(ctx, domaintemplate_id):
    """Show information for a given domaintemplate id"""
    result = ctx.obj['nc'].get("domaintemplates/%s" % domaintemplate_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='domaintemplate-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--enterprise-id', metavar='<enterprise ID>', required=True)
@click.pass_context
def domaintemplate_create(ctx, name, enterprise_id):
    """Add an domaintemplate to the VSD for an given enterprise"""
    params = {'name': name}
    result = ctx.obj['nc'].post("enterprises/%s/domaintemplates" %
                                enterprise_id, params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='domaintemplate-delete')
@click.argument('domaintemplate-id', metavar='<domaintemplate ID>',
                required=True)
@click.pass_context
def domaintemplate_delete(ctx, domaintemplate_id):
    """Delete a given domaintemplate"""
    ctx.obj['nc'].delete("domaintemplates/%s" % domaintemplate_id)


@vsdcli.command(name='domaintemplate-update')
@click.argument('domaintemplate-id', metavar='<domaintemplate ID>',
                required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def domaintemplate_update(ctx, domaintemplate_id, key_value):
    """Update key/value for a given domaintemplate"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':', 1)
        params[key] = value
    ctx.obj['nc'].put("domaintemplates/%s" % domaintemplate_id, params)
    result = ctx.obj['nc'].get("domaintemplates/%s" % domaintemplate_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='domain-list')
@click.option('--domaintemplate-id', metavar='<id>')
@click.option('--enterprise-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for serviceID, name, description, customerID, '
                   'labelID, serviceID, lastUpdatedDate, creationDate, '
                   'externalID')
@click.pass_context
def domain_list(ctx, filter, **ids):
    """List domain for optionnal enterprise or domain id"""
    id_type, id = check_id(one_and_only_one=False, **ids)
    if id_type is None and id is None:
        query = "domains"
    else:
        query = "%ss/%s/domains" % (id_type, id)
    if not filter:
        result = ctx.obj['nc'].get(query)
    else:
        result = ctx.obj['nc'].get(query,
                                   filter=filter)
    table = PrettyTable(["Domain ID", "Name", "Description", "RT / RD"])
    for line in result:
        table.add_row([
            line['ID'],
            line['name'],
            line['description'],
            line['routeTarget'] + " / " + line['routeDistinguisher']])
    print(table)


@vsdcli.command(name='domain-show')
@click.argument('domain-id', metavar='<domain-id>', required=True)
@click.pass_context
def domain_show(ctx, domain_id):
    """Show information for a given domain id"""
    result = ctx.obj['nc'].get("domains/%s" % domain_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='domain-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--enterprise-id', metavar='<enterprise ID>', required=True)
@click.option('--template-id', metavar='<template ID>', required=True)
@click.option('--rd', metavar='<route distinguisher>')
@click.option('--rt', metavar='<route target>')
@click.pass_context
def domain_create(ctx, name, enterprise_id, template_id, rt, rd):
    """Add an domain to the VSD for an given enterprise"""
    params = {'name':       name,
              'templateID': template_id}
    if rt:
        params['routeTarget'] = rt
    if rd:
        params['routeDistinguisher'] = rd
    result = ctx.obj['nc'].post("enterprises/%s/domains" %
                                enterprise_id, params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='domain-delete')
@click.argument('domain-id', metavar='<domain ID>', required=True)
@click.pass_context
def domain_delete(ctx, domain_id):
    """Delete a given domain"""
    ctx.obj['nc'].delete("domains/%s" % domain_id)


@vsdcli.command(name='domain-update')
@click.argument('domain-id', metavar='<domain ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def domain_update(ctx, domain_id, key_value):
    """Update key/value for a given domain"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':', 1)
        params[key] = value
    ctx.obj['nc'].put("domains/%s" % domain_id, params)
    result = ctx.obj['nc'].get("domains/%s" % domain_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='zone-list')
@click.option('--domain-id', metavar='<domain ID>')
@click.option('--filter', metavar='<filter>',
              help='Filter for address, netmask, IPType, name, description, '
                   'numberOfHostsInSubnets, publicZone, address, netmask, '
                   'IPType, name, address, netmask, IPType, name, '
                   'lastUpdatedDate, creationDate, externalID')
@click.pass_context
def zone_list(ctx, domain_id, filter):
    """Show zone for optionnal domain id"""
    if domain_id is None:
        query = "zones"
    else:
        query = "domains/%s/zones" % domain_id
    if not filter:
        result = ctx.obj['nc'].get(query)
    else:
        result = ctx.obj['nc'].get(query,
                                   filter=filter)
    table = PrettyTable(["Zone ID", "Name"])
    for line in result:
        table.add_row([line['ID'],
                       line['name']])
    print(table)


@vsdcli.command(name='zone-show')
@click.argument('zone-id', metavar='<zone-id>', required=True)
@click.pass_context
def zone_show(ctx, zone_id):
    """Show information for a given zone id"""
    result = ctx.obj['nc'].get("zones/%s" % zone_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='zone-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--domain-id', metavar='<domain ID>', required=True)
@click.pass_context
def zone_create(ctx, name, domain_id):
    """Add a zone to the VSD for an given domain"""
    params = {'name': name}
    result = ctx.obj['nc'].post("domains/%s/zones" % domain_id, params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='zone-delete')
@click.argument('zone-id', metavar='<zone ID>', required=True)
@click.pass_context
def zone_delete(ctx, zone_id):
    """Delete a given zone"""
    ctx.obj['nc'].delete("zones/%s" % zone_id)
