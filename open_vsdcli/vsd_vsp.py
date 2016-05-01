from vsd_common import *


@vsdcli.command(name='vsp-list')
@click.option('--filter', metavar='<filter>',
              help='Filter for productVersion, name, description, location, '
                   'lastUpdatedDate, creationDate, externalID')
@click.pass_context
def vsp_list(ctx, filter):
    """list all vsp"""
    if not filter:
        result = ctx.obj['nc'].get("vsps/")
    else:
        result = ctx.obj['nc'].get("vsps/", filter=filter)
    table = PrettyTable(["ID", "Name", "Description", "Version"])
    for line in result:
        table.add_row([line['ID'],
                       line['name'],
                       line['description'],
                       line['productVersion']])
    print table


@vsdcli.command(name='vsp-show')
@click.argument('vsp-id', metavar='<vsp ID>', required=True)
@click.pass_context
def vsp_show(ctx, vsp_id):
    """Show information for a given vsp ID"""
    result = ctx.obj['nc'].get("vsps/%s" % vsp_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='vsd-list')
@click.argument('vsp-id', metavar='<vsp ID>', required=True)
@click.option('--filter', metavar='<filter>',
              help='Filter for address, managementIP, name, location, '
                   'description, productVersion, status, lastUpdatedDate, '
                   'creationDate, externalID')
@click.pass_context
def vsd_list(ctx, vsp_id, filter):
    """List all vsd for a given vsp"""
    if not filter:
        result = ctx.obj['nc'].get("vsps/%s/vsds" % vsp_id)
    else:
        result = ctx.obj['nc'].get("vsps/%s/vsds" % vsp_id, filter=filter)
    table = PrettyTable(["ID", "Name", "Description", "Status", "Mode"])
    for line in result:
        table.add_row([line['ID'],
                       line['name'],
                       line['description'],
                       line['status'],
                       line['mode']])
    print table


@vsdcli.command(name='vsd-show')
@click.argument('vsd-id', metavar='<vsd ID>', required=True)
@click.option('--verbose', count=True, help='Show disk informations')
@click.pass_context
def vsd_show(ctx, vsd_id, verbose):
    """Show information for a given VSD ID"""
    result = ctx.obj['nc'].get("vsds/%s" % vsd_id)[0]
    print_object(result, only=ctx.obj['show_only'], exclude=['disks'])
    if verbose >= 1:
        print "Disks :"
        print result['disks']


@vsdcli.command(name='vsd-componant-list')
@click.argument('vsd-id', metavar='<vsd ID>', required=True)
@click.pass_context
def vsd_componant_list(ctx, vsd_id):
    """List componant for a given VSD ID"""
    result = ctx.obj['nc'].get("vsds/%s/components" % vsd_id)
    table = PrettyTable(["ID",
                         "Name",
                         "Description",
                         "Status",
                         "Address",
                         "Version",
                         "type"])
    for line in result:
        table.add_row([line['ID'],
                       line['name'],
                       line['description'],
                       line['status'],
                       line['address'],
                       line['productVersion'],
                       line['type']])
    print table
