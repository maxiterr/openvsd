from open_vsdcli.vsd_common import *


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
def staticroute_list(ctx, filter, **ids):
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
    print(table)


@vsdcli.command(name='staticroute-show')
@click.argument('staticroute-id', metavar='<staticroute-id>',
                required=True)
@click.pass_context
def domaintemplate_show(ctx, staticroute_id):
    """Show information for a given static route id"""
    result = ctx.obj['nc'].get("staticroutes/%s" % staticroute_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='staticroute-create')
@click.option('--sharednetworkresource-id',
              metavar='<Shared network resource ID>')
@click.option('--domain-id', metavar='<Domain id>')
@click.option('--l2domain-id', metavar='<L2 Domain id>')
@click.option('--aggregateddomain-id', metavar='<Aggregated dommain id>')
@click.option('--address', metavar='<address IPv4 or IPv6>', required=True)
@click.option('--mask', metavar='<netmask or mask length>',
              help='Mask must be length for IPv6', required=True)
@click.option('--gateway', metavar='<gateway IPv4 or IPv6>', required=True)
@click.option('--ip-type', type=click.Choice(['IPV4',
                                             'IPV6']),
              default='IPV4', help='Default : IPV4')
@click.option('--bfd-enabled',  is_flag=True,
              help='Active BFD for this route')
@click.pass_context
def subnet_create(ctx, address, mask, gateway, ip_type, bfd_enabled, **ids):
    """Create route for domain, l2domain, shared network"""
    """or aggregate domain"""
    id_type, id = check_id(**ids)

    try:
        int(mask)
        mask_is_netmask = False
    except ValueError:
        mask_is_netmask = True

    if ip_type == 'IPV6':
        if mask_is_netmask:
            raise click.exceptions.UsageError(
                "For IPv6 mask must be a length")
        params = {'IPv6Address': address + '/' + mask,
                  'nextHopIp': gateway}
    else:
        if not mask_is_netmask:
            netmask = length_to_netmask(mask)
        else:
            netmask = mask
        params = {'address': address,
                  'netmask': netmask,
                  'nextHopIp': gateway}

    if bfd_enabled:
        params['BFDEnabled'] = True

    result = ctx.obj['nc'].post("%ss/%s/staticroutes?responseChoice=1"
                                % (id_type, id), params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='staticroute-update')
@click.argument('route-id', metavar='<Static route ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def subnet_update(ctx, route_id, key_value):
    """Update key/value for a given static route"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':', 1)
        params[key] = value
    ctx.obj['nc'].put("staticroutes/%s?responseChoice=1" % route_id, params)
    result = ctx.obj['nc'].get("staticroutes/%s" % route_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='staticroute-delete')
@click.argument('staticroute-id', metavar='<Static route ID>', required=True)
@click.pass_context
def subnet_delete(ctx, staticroute_id):
    """Delete a given static route"""
    ctx.obj['nc'].delete("staticroutes/%s?responseChoice=1" % staticroute_id)
