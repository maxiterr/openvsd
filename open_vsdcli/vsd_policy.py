from vsd_common import *


@vsdcli.command(name='egressacltemplate-list')
@click.option('--l2domaintemplate-id', metavar='<id>')
@click.option('--domaintemplate-id', metavar='<id>')
@click.option('--domain-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, physicalName, portType, userMnemonic, '
                   'useUserMnemonic, name, description, physicalName, '
                   'portType, VLANRange, lastUpdatedDate, creationDate, '
                   'externalID')
@click.pass_context
def egressacltemplate_list(ctx, filter, **ids):
    """List all egress acl template for a given l2domaintemplate,
       domaintemplate, domain or l2domain"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/egressacltemplates" % (id_type, id)
    result = ctx.obj['nc'].get(request, filter=filter)
    table = PrettyTable(["ID",
                         "name",
                         "active",
                         "defaultAllowIP",
                         "defaultAllowNonIP"])
    for line in result:
        table.add_row([line['ID'],
                       line['name'],
                       line['active'],
                       line['defaultAllowIP'],
                       line['defaultAllowNonIP']])
    print table


@vsdcli.command(name='egressacltemplate-show')
@click.argument('egressacltemplate-id', metavar='<port-id>', required=True)
@click.pass_context
def egressacltemplate_show(ctx, egressacltemplate_id):
    """Show information for a given egressacltemplate id"""
    result = ctx.obj['nc'].get("egressacltemplates/%s" %
                               egressacltemplate_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='egressacltemplate-update')
@click.argument('egressacltemplate-id', metavar='<egressacltemplate ID>',
                required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def egressacltemplate_update(ctx, egressacltemplate_id, key_value):
    """Update key/value for a given egressacltemplate"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':', 1)
        params[key] = value
    ctx.obj['nc'].put("egressacltemplates/%s?responseChoice=1" %
                      egressacltemplate_id, params)
    result = ctx.obj['nc'].get("egressacltemplates/%s" %
                               egressacltemplate_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='egressacltemplate-delete')
@click.argument('egressacltemplate-id', metavar='<egressacltemplate ID>',
                required=True)
@click.pass_context
def egressacltemplate_delete(ctx, egressacltemplate_id):
    """Delete a given egressacltemplate"""
    ctx.obj['nc'].delete("egressacltemplates/%s?responseChoice=1" %
                         egressacltemplate_id)


@vsdcli.command(name='egressacltemplate-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--domain-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--domaintemplate-id', metavar='<id>')
@click.option('--l2domaintemplate-id', metavar='<id>')
@click.pass_context
def egressacltemplate_create(ctx, name, **ids):
    """Add an Egress ACL template to a given domain, l2domain, domaintemplate
       or l2domaintemplate"""
    id_type, id = check_id(**ids)
    params = {'name': name}
    result = ctx.obj['nc'].post("%ss/%s/egressacltemplates" % (id_type, id),
                                params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='ingressacltemplate-list')
@click.option('--l2domaintemplate-id', metavar='<id>')
@click.option('--domaintemplate-id', metavar='<id>')
@click.option('--domain-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for allowL2AddressSpoof, defaultAllowIP, '
                   'defaultAllowNonIP, name, description, active, '
                   'lastUpdatedDate, creationDate, externalID')
@click.pass_context
def ingressacltemplate_list(ctx, filter, **ids):
    """List all ingress acl template for a given l2domaintemplate,
       domaintemplate, domain or l2domain"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/ingressacltemplates" % (id_type, id)
    result = ctx.obj['nc'].get(request, filter=filter)
    table = PrettyTable(["ID",
                         "name",
                         "active",
                         "defaultAllowIP",
                         "defaultAllowNonIP",
                         "allowL2AddressSpoof"])
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
    result = ctx.obj['nc'].get("ingressacltemplates/%s" %
                               ingressacltemplate_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='ingressacltemplate-update')
@click.argument('ingressacltemplate-id', metavar='<ingressacltemplate ID>',
                required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def ingressacltemplate_update(ctx, ingressacltemplate_id, key_value):
    """Update key/value for a given ingressacltemplate"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':', 1)
        params[key] = value
    ctx.obj['nc'].put("ingressacltemplates/%s?responseChoice=1" %
                      ingressacltemplate_id, params)
    result = ctx.obj['nc'].get("ingressacltemplates/%s" %
                               ingressacltemplate_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='ingressacltemplate-delete')
@click.argument('ingressacltemplate-id', metavar='<ingressacltemplate ID>',
                required=True)
@click.pass_context
def ingressacltemplate_delete(ctx, ingressacltemplate_id):
    """Delete a given ingressacltemplate"""
    ctx.obj['nc'].delete("ingressacltemplates/%s?responseChoice=1" %
                         ingressacltemplate_id)


@vsdcli.command(name='ingressacltemplate-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--domain-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--domaintemplate-id', metavar='<id>')
@click.option('--l2domaintemplate-id', metavar='<id>')
@click.pass_context
def ingressacltemplate_create(ctx, name, **ids):
    """Add an Ingress ACL template to a given domain, l2domain, domaintemplate
       or l2domaintemplate"""
    id_type, id = check_id(**ids)
    params = {'name': name}
    result = ctx.obj['nc'].post("%ss/%s/ingressacltemplates" % (id_type, id),
                                params)[0]
    print_object(result, only=ctx.obj['show_only'])
