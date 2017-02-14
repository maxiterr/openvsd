from vsd_common import *


@vsdcli.command(name='license-list')
@click.pass_context
def license_list(ctx):
    """Show all license within the VSD"""
    from datetime import datetime
    result = ctx.obj['nc'].get("licenses")
    table = PrettyTable(["License id",
                         "Compagny",
                         "Max NICs",
                         "Max VMs",
                         "Version",
                         "Expiration"])
    for line in result:
        version = line['productVersion'] + 'R' + str(line['majorRelease']),
        table.add_row([line['ID'],
                       line['company'],
                       line['allowedNICsCount'],
                       line['allowedVMsCount'],
                       line['productVersion'] + 'R' + str(
                           line['majorRelease']),
                       datetime.fromtimestamp(
                           line['expirationDate'] /
                           1000).strftime('%Y-%m-%d %H:%M:%S')])
    print table


@vsdcli.command(name='license-show')
@click.argument('license-id', metavar='<license-id>', required=True)
@click.option('--verbose', count=True, help='Show license code in BASE64')
@click.pass_context
def license_show(ctx, license_id, verbose):
    """Show license detail for a given license id"""
    result = ctx.obj['nc'].get("licenses/%s" % license_id)[0]
    print_object(result, exclude=['license'], only=ctx.obj['show_only'])
    if verbose >= 1:
        print "License: " + result['license']


@vsdcli.command(name='license-create')
@click.argument('license', metavar='<license (Base64)>', required=True)
@click.pass_context
def license_create(ctx, license):
    """Add a license to the VSD"""
    result = ctx.obj['nc'].post("licenses", {"license": license})[0]
    print_object(result, exclude=['license'], only=ctx.obj['show_only'])


@vsdcli.command(name='license-delete')
@click.argument('license-id', metavar='<license ID>', required=True)
@click.confirmation_option(prompt='Are you sure ?')
@click.pass_context
def license_delete(ctx, license_id):
    """Delete a given license"""
    ctx.obj['nc'].delete("licenses/%s" % license_id)
