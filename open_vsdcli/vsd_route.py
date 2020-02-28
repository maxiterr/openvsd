from vsd_common import *


@vsdcli.command(name='staticroute-list')
@click.option('--containerinterface-id', metavar='<id>')
@click.option('--sharednetworkresource-id', metavar='<id>')
@click.option('--vminterface-id', metavar='<id>')
@click.option('--domain-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--hostinterface-id', metavar='<id>')
@click.option('--aggregateddomain-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for address, BFDEnabled, blackHoleEnabled, '
                   'externalID, IPType, IPv6Address, netmask, nextHopIP, '
                   'routeDistinguisher')
@click.pass_context
def l2domain_list(ctx, filter, **ids):
    """List statics route"""
    id_type, id = check_id(one_and_only_one=False, **ids)
    if id_type is None and id is None:
        uri = "staticroutes"
    else:
        uri = "%ss/%s/staticroutes" % (id_type, id)
    if not filter:
        result = ctx.obj['nc'].get(uri)
    else:
        result = ctx.obj['nc'].get(uri, filter=filter)
    table = PrettyTable(["ID", "Subnet", "Next hop"])
    for line in result:
        if line['IPType'] == 'IPV4':
            address = line['address'] + "/" + \
                    netmask_to_length(line['netmask'])
        else:
            address = line['IPv6Address']
        table.add_row([
            line['ID'],
            address,
            line['nextHopIp']
        ])
    print table


@vsdcli.command(name='staticroute-show')
@click.argument('staticroute-id', metavar='<staticroute-id>',
                required=True)
@click.pass_context
def domaintemplate_show(ctx, staticroute_id):
    """Show information for a given static route id"""
    result = ctx.obj['nc'].get("staticroutes/%s" % staticroute_id)[0]
    print_object(result, only=ctx.obj['show_only'])
