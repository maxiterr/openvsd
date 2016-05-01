from vsd_common import *


@vsdcli.command(name='dhcp-option-list')
@click.option('--vminterface-id', metavar='<id>')
@click.option('--hostinterface-id', metavar='<id>')
@click.option('--bridgeinterface-id', metavar='<id>')
@click.option('--sharednetworkresource-id', metavar='<id>')
@click.option('--subnet-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--domain-id', metavar='<id>')
@click.option('--zone-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for type, length, value, lastUpdatedDate,'
                   ' creationDate, externalID')
@click.pass_context
def dhcp_option_list(ctx, filter, **ids):
    """List all dhcp option for a given vminterface, hostinterface,
    hostinterface, bridgeinterface, sharednetworkresource,
    subnet, l2domain, domain, zone"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/dhcpoptions" % (id_type, id)
    result = ctx.obj['nc'].get(request, filter=filter)
    table = PrettyTable(["ID", "Type", "Value", "Length"])
    for line in result:
        table.add_row([line['ID'],
                       line['type'],
                       line['value'],
                       line['length']])
    print table


@vsdcli.command(name='dhcp-option-show')
@click.argument('dhcpoption-id', metavar='<dhcp-option-id>', required=True)
@click.pass_context
def dhcp_option_show(ctx, dhcpoption_id):
    """Show information for a given dhcp option id"""
    result = ctx.obj['nc'].get("dhcpoptions/%s" % dhcpoption_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='dhcp-option-delete')
@click.argument('dhcpoption-id', metavar='<dhcp-option-id>', required=True)
@click.pass_context
def dhcp_option_delete(ctx, dhcpoption_id):
    """Delete a given dhcp option ID"""
    ctx.obj['nc'].delete("dhcpoptions/%s" % dhcpoption_id)


@vsdcli.command(name='dhcp-option-add')
@click.option('--sharednetworkresource-id', metavar='<id>')
@click.option('--subnet-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--domain-id', metavar='<id>')
@click.option('--zone-id', metavar='<id>')
@click.option('--value', metavar='<dhcp value>', required=True)
@click.option('--type', metavar='<dhcp type>', required=True)
@click.option('--length', metavar='<dhcp length>', required=True)
@click.pass_context
def dhcp_option_add(ctx, value, type, length,  **ids):
    """Add a dhcpoption (type, value, length) for a given sharednetworkresource,
    subnet, l2domain, domain, zone"""
    id_type, id = check_id(**ids)
    params = {}
    params['value'] = value
    params['type'] = type
    params['length'] = length
    result = ctx.obj['nc'].post("%ss/%s/dhcpoptions" % (id_type, id),
                                params)[0]
    print_object(result, only=ctx.obj['show_only'])


def decode_ip(data):
    """Decode IP address. Fulfill with 0 at the end if needed"""
    ip = ''  # IP in text fomat
    octet_count = 0  # count octet in IP
    while len(data) > 0:  # Decode octet per octet
        ip = ip + str(int(data[:2], 16))
        data = data[2:]
        octet_count += 1
        if len(data) > 0:
            ip += '.'
    while octet_count < 4:  # Fulfill with 0
        ip += '.0'
        octet_count += 1
    return ip


def encode_ip(ip, mask=None):
    """Encode IP address into string accordinaly with RFC3442,
       if mask is given, add it at the begining"""
    if mask == 0:
        return '00'  # As Define in RFC
    data = ''
    if mask:
        byte_count = (mask-1)/8+1
        data = hex(mask)[2:].zfill(2)
    else:
        byte_count = 4
    ip = ip.split('.')
    while byte_count > 0:
        data += hex(int(ip.pop(0)))[2:].zfill(2)
        byte_count -= 1
    return data


def decode_route(data):
    """Extract all mask/ip from data. Data is a string encoded
    accordinaly with RFC3442"""
    route = []
    while len(data) > 0:
        mask = int(data[:2], 16)
        data = data[2:]
        if mask == 0:
            byte = 0
            subnet = '0.0.0.0'
        else:
            byte = (mask-1)/8+1
            subnet = decode_ip(data[:2*byte])
            data = data[2*byte:]
        gateway = decode_ip(data[:8])
        data = data[8:]
        route.append({'mask':    str(mask),
                      'subnet':  subnet,
                      'gateway': gateway})
    return route


def encode_route(route):
    """Encode a list of route (a route is a dict with subnet, mask and gateway)
       into string accordinaly with RFC3442"""
    data = ''
    while len(route) > 0:
        r = route.pop()
        data += encode_ip(r['subnet'], int(r['mask']))
        data += encode_ip(r['gateway'])
    return data


def decode_dhcp_data(data):
    """data is the raw result from the API. Return a list of dict,
       with dict contains (subnet, mask, gateway, option)
       for each route"""
    data_f9 = [item for item in data if item['type'] == 'f9']
    data_79 = [item for item in data if item['type'] == '79']
    if len(data_f9) > 1 and len(data_79) > 1:
        raise Exception("Abnormal count of DHCP option")
    route = []
    route_f9 = []  # List with route for dhcp option 79
    route_79 = []  # List with route for dhcp option f9
    if len(data_f9) != 0:
        route_f9 = decode_route(data_f9[0]['value'])
    if len(data_79) != 0:
        route_79 = decode_route(data_79[0]['value'])
    route = [dict(t) for t in set([tuple(d.items())
                                  for d in route_79 + route_f9])]
    route_w_option = []
    for r in route:
        option = []
        if r in route_f9:
            option.append('f9')
        if r in route_79:
            option.append('79')
        r.update({'option': option})
        route_w_option.append(r)
    return route_w_option


@vsdcli.command(name='dhcp-route-list')
@click.option('--vminterface-id', metavar='<id>')
@click.option('--hostinterface-id', metavar='<id>')
@click.option('--bridgeinterface-id', metavar='<id>')
@click.option('--sharednetworkresource-id', metavar='<id>')
@click.option('--subnet-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for type, length, value, lastUpdatedDate, '
                   'creationDate, externalID')
@click.pass_context
def dhcp_route_list(ctx, filter, **ids):
    """List all routes in dhcp option for a given vminterface, hostinterface
       hostinterface, bridgeinterface, sharednetworkresource, subnet,
       l2domain"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/dhcpoptions" % (id_type, id)
    result = ctx.obj['nc'].get(request, filter=filter)

    route = decode_dhcp_data(result)

    table = PrettyTable(["Subnet", "Gateway", "option"])
    for line in route:
        table.add_row([line['subnet'] + '/' + line['mask'],
                       line['gateway'],
                       line['option']])
    print table


@vsdcli.command(name='dhcp-route-add')
@click.option('--vminterface-id', metavar='<id>')
@click.option('--hostinterface-id', metavar='<id>')
@click.option('--bridgeinterface-id', metavar='<id>')
@click.option('--sharednetworkresource-id', metavar='<id>')
@click.option('--subnet-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--subnet', required=True)
@click.option('--mask', required=True)
@click.option('--gateway', required=True)
@click.pass_context
def dhcp_route_add(ctx, subnet, mask, gateway, **ids):
    """Add route in dhcp option for a given vminterface, hostinterface,
       hostinterface, bridgeinterface, sharednetworkresource, subnet, l2domain
    """
    id_type, id = check_id(**ids)
    result = ctx.obj['nc'].get("%ss/%s/dhcpoptions" % (id_type, id))
    route = decode_dhcp_data(result)

    # TODO: Check if subnet and gateway are valid IP
    # TODO: Check mask is acceptable
    # TODO Check if route already exist, then raise execption
    route.append({'subnet':  subnet,
                  'mask':    mask,
                  'gateway': gateway,
                  'option':  ['f9', '79']})
    encoded_route = encode_route(route)

    params = {}
    params['value'] = encoded_route
    params['length'] = hex(len(encoded_route)/2)[2:].zfill(2)
    type_updated = []
    for option in result:
        if option['type'] in ['79', 'f9']:
            type_updated.append(option['type'])
            ctx.obj['nc'].put("dhcpoptions/%s" % option['ID'], params)
    if '79' not in type_updated:
        params['type'] = '79'
        ctx.obj['nc'].post("%ss/%s/dhcpoptions" % (id_type, id), params)
    if 'f9' not in type_updated:
        params['type'] = 'f9'
        ctx.obj['nc'].post("%ss/%s/dhcpoptions" % (id_type, id), params)


@vsdcli.command(name='dhcp-route-delete')
@click.option('--vminterface-id', metavar='<id>')
@click.option('--hostinterface-id', metavar='<id>')
@click.option('--bridgeinterface-id', metavar='<id>')
@click.option('--sharednetworkresource-id', metavar='<id>')
@click.option('--subnet-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--subnet', required=True)
@click.option('--mask', required=True)
@click.option('--gateway', required=True)
@click.pass_context
def dhcp_route_delete(ctx, subnet, mask, gateway, **ids):
    """Remove route in dhcp option for a given vminterface, hostinterface,
       hostinterface, bridgeinterface, sharednetworkresource, subnet, l2domain
    """
    id_type, id = check_id(**ids)
    result = ctx.obj['nc'].get("%ss/%s/dhcpoptions" % (id_type, id))
    route_list = decode_dhcp_data(result)
    if not len(route_list):
        raise Exception("No route to delete")
    # TODO: Check if subnet and gateway are valid IP
    # TODO: Check mask is acceptable
    route_to_remove = {'subnet':  subnet,
                       'mask':    mask,
                       'gateway': gateway}
    new_route_list = []
    change = 0
    for route in route_list:
        route.pop('option')
        if route == route_to_remove:
            change = 1
        else:
            new_route_list.append(route)
    if change == 0:
        raise Exception('Route not present: unable to remove it')
    if len(new_route_list) == 0:
        # Remove dhcp option because no more route
        for option in result:
            if option['type'] == '79' or option['type'] == 'f9':
                ctx.obj['nc'].delete("dhcpoptions/%s" % option['ID'])
    else:
        encoded_route = encode_route(new_route_list)
        params = {}
        params['value'] = encoded_route
        params['length'] = hex(len(encoded_route)/2)[2:].zfill(2)
        for option in result:
            if option['type'] == '79' or option['type'] == 'f9':
                ctx.obj['nc'].put("dhcpoptions/%s" % option['ID'], params)


@vsdcli.command(name='dhcp-gateway-show')
@click.option('--vminterface-id', metavar='<id>')
@click.option('--hostinterface-id', metavar='<id>')
@click.option('--bridgeinterface-id', metavar='<id>')
@click.option('--sharednetworkresource-id', metavar='<id>')
@click.option('--subnet-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for type, length, value, lastUpdatedDate,'
                   ' creationDate, externalID')
@click.pass_context
def dhcp_gateway_show(ctx, filter, **ids):
    """Show gateway in dhcp option for a given vminterface, hostinterface,
       hostinterface, bridgeinterface, sharednetworkresource, subnet, l2domain
    """
    id_type, id = check_id(**ids)
    request = "%ss/%s/dhcpoptions" % (id_type, id)
    result = ctx.obj['nc'].get(request, filter=filter)

    gateway = 'None'
    for option in result:
        if option['type'] == '03':
            gateway = decode_ip(option['value'])
    table = PrettyTable(["Gateway"])
    table.add_row([gateway])
    print table
