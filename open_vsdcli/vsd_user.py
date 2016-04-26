from vsd_common import *


@vsdcli.command(name='user-list')
@click.option('--enterprise-id', metavar='<id>')
@click.option('--group-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for firstName, lastName, userName, email, '
                   'lastUpdatedDate, creationDate, externalID')
@click.pass_context
def user_list_list(ctx, filter, **ids):
    """list users for a given enterprise or group id"""
    id_type, id = check_id(**ids)
    if not filter:
        result = ctx.obj['nc'].get("%ss/%s/users" % (id_type, id))
    else:
        result = ctx.obj['nc'].get("%ss/%s/users" % (id_type, id),
                                   filter=filter)
    table = PrettyTable(["ID",
                         "User name",
                         "First name",
                         "Last name",
                         "Email"])
    for line in result:
        table.add_row([line['ID'],
                       line['userName'],
                       line['firstName'],
                       line['lastName'],
                       line['email']])
    print table


@vsdcli.command(name='user-show')
@click.argument('user-id', metavar='<user-id>', required=True)
@click.pass_context
def user_show(ctx, user_id):
    """Show information for a given user id"""
    result = ctx.obj['nc'].get("users/%s" % user_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='user-create')
@click.argument('username', metavar='<username>', required=True)
@click.option('--lastname', metavar='<lastname>', required=True)
@click.option('--firstname', metavar='<firstname>', required=True)
@click.option('--email', metavar='<email>', required=True)
@click.option('--password', metavar='<password>', required=True)
@click.option('--enterprise-id', metavar='<enterprise ID>', required=True)
@click.pass_context
def user_create(ctx, username, firstname, lastname, email, password,
                enterprise_id):
    """Add a user to the VSD"""
    import hashlib
    # Define mandotory values
    params = {'userName':  username,
              'firstName': firstname,
              'lastName':  lastname,
              'email':     email,
              'password':  hashlib.sha1(password).hexdigest()}
    result = ctx.obj['nc'].post("enterprises/%s/users" %
                                enterprise_id, params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='user-delete')
@click.argument('user-id', metavar='<user ID>', required=True)
@click.pass_context
def user_delete(ctx, user_id):
    """Delete a given user"""
    ctx.obj['nc'].delete("users/%s" % user_id)


@vsdcli.command(name='user-update')
@click.argument('user-id', metavar='<user ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def user_update(ctx, user_id, key_value):
    """Update key/value for a given user"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':', 1)
        params[key] = value
    ctx.obj['nc'].put("users/%s" % user_id, params)
    result = ctx.obj['nc'].get("users/%s" % user_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='group-list')
@click.option('--enterprise-id', metavar='<id>')
@click.option('--user-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, description, role, private, '
                   'lastUpdatedDate, creationDate, externalID')
@click.pass_context
def group_list(ctx, filter, **ids):
    """list groups for a given enterprise id or that an user belongs to"""
    id_type, id = check_id(**ids)
    if not filter:
        result = ctx.obj['nc'].get("%ss/%s/groups" % (id_type, id))
    else:
        result = ctx.obj['nc'].get("%ss/%s/groups" % (id_type, id),
                                   filter=filter)
    table = PrettyTable(["ID", "Name", "Description", "Role", "Private"])
    table.max_width['Description'] = 40
    for line in result:
        table.add_row([line['ID'],
                       line['name'],
                       line['description'],
                       line['role'],
                       line['private']])
    print table


@vsdcli.command(name='group-show')
@click.argument('group-id', metavar='<group-id>', required=True)
@click.pass_context
def group_show(ctx, group_id):
    """Show information for a given group id"""
    result = ctx.obj['nc'].get("groups/%s" % group_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='group-create')
@click.argument('name', metavar='<Group name>', required=True)
@click.option('--enterprise-id', metavar='<enterprise ID>', required=True)
@click.option('--description', metavar='<descrition>')
@click.option('--private', metavar='<email>', count=True)
@click.pass_context
def group_create(ctx, name, enterprise_id, description, private):
    """Add a group to the VSD"""
    # Define mandotory values
    params = {'name': name}
    # Define optional values
    if description:
        params['description'] = description
    if private >= 1:
        params['private'] = True
    result = ctx.obj['nc'].post("enterprises/%s/groups" % enterprise_id,
                                params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='group-update')
@click.argument('group-id', metavar='<group ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def group_update(ctx, group_id, key_value):
    """Update key/value for a given group"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':', 1)
        params[key] = value
    ctx.obj['nc'].put("groups/%s" % group_id, params)
    result = ctx.obj['nc'].get("groups/%s" % group_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='group-delete')
@click.argument('group-id', metavar='<group ID>', required=True)
@click.pass_context
def group_delete(ctx, group_id):
    """Delete a given group"""
    ctx.obj['nc'].delete("groups/%s" % group_id)


@vsdcli.command(name='group-add-user')
@click.argument('group-id', metavar='<group ID>', required=True)
@click.option('--user-id', metavar='<user ID>', required=True)
@click.pass_context
def group_add_user(ctx, group_id, user_id):
    """Add a user to a given group"""
    # Get all user for this group
    userList = ctx.obj['nc'].get("groups/%s/users" % group_id)
    user_ids = [u['ID'] for u in userList]
    user_ids.append(user_id)
    ctx.obj['nc'].put("groups/%s/users" % group_id, user_ids)


@vsdcli.command(name='group-del-user')
@click.argument('group-id', metavar='<group ID>', required=True)
@click.option('--user-id', metavar='<user ID>', required=True)
@click.pass_context
def group_del_user(ctx, group_id, user_id):
    """delete a user from a given group"""
    # Get all user for this group
    user_list = ctx.obj['nc'].get("groups/%s/users" % group_id)
    user_ids = [elt.get('ID') for elt in user_list if elt.get('ID') != user_id]
    if len(user_ids) == len(user_list):
        print "User not present in the group"
    else:
        ctx.obj['nc'].put("groups/%s/users" % group_id, user_ids)


@vsdcli.command(name='permission-list')
@click.option('--zone-id', metavar='<id>')
@click.option('--domaintemplate-id', metavar='<id>')
@click.option('--redundancygroup-id', metavar='<id>')
@click.option('--gateway-id', metavar='<id>')
@click.option('--vlan-id', metavar='<id>')
@click.option('--domain-id', metavar='<id>')
@click.option('--service-id', metavar='<id>')
@click.option('--port-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--l2domaintemplate-id', metavar='<id>')
@click.option('--filter', metavar='<filter>',
              help='Filter for name, lastUpdatedDate, creationDate, '
                   'externalID')
@click.pass_context
def permission_list(ctx, filter, **ids):
    """List all permissions"""
    id_type, id = check_id(**ids)
    request = "%ss/%s/permissions" % (id_type, id)
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


@vsdcli.command(name='permission-show')
@click.argument('permission-id', metavar='<permission-id>', required=True)
@click.pass_context
def permission_show(ctx, permission_id):
    """Show information for a given permission id"""
    result = ctx.obj['nc'].get("permissions/%s" % permission_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='add-permission')
@click.argument('entity-id', metavar='<group or user ID>', required=True)
@click.option('--action', default='USE', help='Default : USE',
              type=click.Choice(['USE',
                                 'EXTEND',
                                 'READ',
                                 'INSTANTIATE']))
@click.option('--zone-id', metavar='<id>')
@click.option('--domaintemplate-id', metavar='<id>')
@click.option('--redundancygroup-id', metavar='<id>')
@click.option('--gateway-id', metavar='<id>')
@click.option('--vlan-id', metavar='<id>')
@click.option('--domain-id', metavar='<id>')
@click.option('--service-id', metavar='<id>')
@click.option('--port-id', metavar='<id>')
@click.option('--l2domain-id', metavar='<id>')
@click.option('--l2domaintemplate-id', metavar='<id>')
@click.option('--zone-id', metavar='<id>')
@click.pass_context
def add_permission(ctx, entity_id, action, **ids):
    """Add permission for a given element (Domain, Zone, L2Domain, etc...)"""
    id_type, id = check_id(**ids)
    params = {}
    params['permittedEntityID'] = entity_id
    params['permittedAction'] = action
    ctx.obj['nc'].post("%ss/%s/permissions" % (id_type, id), params)
