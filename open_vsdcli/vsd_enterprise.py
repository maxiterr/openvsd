from vsd_common import *


@vsdcli.command(name='enterprise-list')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, description, lastUpdatedDate, '
                   'creationDate, externalID')
@click.pass_context
def enterprise_list(ctx, filter):
    """Show all enterprise within the VSD"""
    result = ctx.obj['nc'].get("enterprises", filter=filter)
    table = PrettyTable(["Enterprise ID", "Name"])
    for line in result:
        table.add_row([line['ID'],
                       line['name']])
    print table


@vsdcli.command(name='enterprise-show')
@click.argument('enterprise-id', metavar='<enterprise-id>', required=True)
@click.pass_context
def enterprise_show(ctx, enterprise_id):
    """Show information for a given enterprise id"""
    result = ctx.obj['nc'].get("enterprises/%s" % enterprise_id)[0]
    print_object(result, exclude=['APIKey'], only=ctx.obj['show_only'])


@vsdcli.command(name='enterprise-create')
@click.argument('name', metavar='<name>', required=True)
@click.pass_context
def enterprise_create(ctx, name):
    """Add an enterprise to the VSD"""
    params = {}
    params['name'] = name
    result = ctx.obj['nc'].post("enterprises", params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='enterprise-delete')
@click.argument('enterprise-id', metavar='<enterprise ID>', required=True)
@click.confirmation_option(prompt='Are you sure ?')
@click.pass_context
def enterprise_delete(ctx, enterprise_id):
    """Delete a given enterprise"""
    ctx.obj['nc'].delete("enterprises/%s?responseChoice=1" % enterprise_id)


@vsdcli.command(name='enterprise-update')
@click.argument('enterprise-id', metavar='<enterprise ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def enterprise_update(ctx, enterprise_id, key_value):
    """Update key/value for a given enterprise"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':', 1)
        params[key] = value
    ctx.obj['nc'].put("enterprises/%s" % enterprise_id, params)
    result = ctx.obj['nc'].get("enterprises/%s" % enterprise_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='enterprisepermission-list')
@click.option('--redundancygroup-id', metavar='<id>')
@click.option('--gateway-id', metavar='<id>')
@click.option('--vlan-id', metavar='<id>')
@click.option('--service-id', metavar='<id>')
@click.option('--port-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, lastUpdatedDate, creationDate, '
                   'externalID')
@click.pass_context
def enterprisepermission_list(ctx, filter, **ids):
    """List all Enterprise Permission for a CSP entity"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/enterprisepermissions" % (id_type, id)
    if not filter:
        result = ctx.obj['nc'].get(request)
    else:
        result = ctx.obj['nc'].get(request, filter=filter)
    table = PrettyTable(["ID",
                         "Action",
                         "Entity ID",
                         "Entity type",
                         "Entity name"])
    for line in result:
        table.add_row([line['ID'],
                       line['permittedAction'],
                       line['permittedEntityID'],
                       line['permittedEntityType'],
                       line['permittedEntityName']])
    print table


@vsdcli.command(name='enterprisepermission-show')
@click.argument('enterprisepermission-id', metavar='<enterprisepermission-id>',
                required=True)
@click.pass_context
def enterprisepermission_show(ctx, permission_id):
    """Show information for a given enterprisepermission id"""
    result = ctx.obj['nc'].get("enterprisepermissions/%s" %
                               enterprisepermission_id)[0]
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
    ctx.obj['nc'].post("%ss/%s/enterprisepermissions" % (id_type, id), params)
