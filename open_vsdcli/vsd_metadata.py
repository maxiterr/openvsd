from vsd_common import *


@vsdcli.command(name='metadata-list')
@click.option('--entity', metavar='<name>', help="Can be any entity in VSD")
@click.option('--id', metavar='<ID>', help="ID of the entity")
@click.option('--global', 'is_global', is_flag=True,
              help="Show global metadata instead of local")
@click.option('--filter', metavar='<filter>',
              help='Filter for name, description, blob, global,'
                   ' networkNotificationDisabled, ID, externalID')
@click.pass_context
def metadata_list(ctx, filter, entity, id, is_global):
    """List all metadata associated to any entity"""
    if is_global:
        request = "%ss/%s/globalmetadatas" % (entity, id)
    else:
        request = "%ss/%s/metadatas" % (entity, id)
    result = ctx.obj['nc'].get(request, filter=filter)
    table = PrettyTable(["ID", "name", "description"])
    for line in result:
        table.add_row([line['ID'],
                       line['name'],
                       line['description']])
    print table


@vsdcli.command(name='metadata-show')
@click.argument('metadata-id', metavar='<Metadata ID>', required=True)
@click.option('--data', 'data', is_flag=True,
              help="Show data content only. Preemptive option on list-tag")
@click.option('--global', 'is_global', is_flag=True,
              help="Show global metadata instead of local")
@click.option('--list-tag', is_flag=True,
              help="List tag for this metadata")
@click.pass_context
def metadata_show(ctx, metadata_id, data, is_global, list_tag):
    """Show information for a given metadata id"""
    if is_global:
        request = "globalmetadatas/%s" % metadata_id
    else:
        request = "metadatas/%s" % metadata_id
    result = ctx.obj['nc'].get(request)[0]
    if data:
        print result['blob']
        return
    if not list_tag:
        print_object(result, only=ctx.obj['show_only'], exclude=['blob'])
        return
    tags = []
    for tag in result['metadataTagIDs']:
        tags.append(ctx.obj['nc'].get("metadatatags/%s" % tag)[0])
    table = PrettyTable(["ID", "name", "description"])
    for line in tags:
        table.add_row([line['ID'],
                       line['name'],
                       line['description']])
    print table


@vsdcli.command(name='metadata-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--entity', metavar='<name>', required=True,
              help="Can be any entity in VSD")
@click.option('--id', metavar='<ID>', required=True,
              help="ID of the entity")
@click.option('--tag', metavar='<ID>', multiple=True,
              help="tag's ID to add. Can be repeted")
@click.option('--data', required=True,
              help="Metadata that describes about the entity attached to it.")
@click.pass_context
def metadata_create(ctx, name, entity, id, tag, data):
    """Create a metadata for a given entity ID"""
    params = {'name': name,
              'blob': data}
    if tag:
        params['metadataTagIDs'] = []
        for t in tag:
            params['metadataTagIDs'].append(t)
    request = "%ss/%s/metadatas" % (entity, id)
    result = ctx.obj['nc'].post(request, params)[0]
    print_object(result, only=ctx.obj['show_only'], exclude=['blob'])


@vsdcli.command(name='metadata-update')
@click.argument('metadata-id', metavar='<metadata ID>',
                required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.option('--global', 'is_global', is_flag=True,
              help="Update global metadata instead of local")
@click.pass_context
def metadata_update(ctx, metadata_id, key_value, is_global):
    """Update key/value for a given metadata"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':', 1)
        params[key] = value
    if is_global:
        request = "globalmetadatas/%s" % metadata_id
    else:
        request = "metadatas/%s" % metadata_id
    ctx.obj['nc'].put(request, params)
    result = ctx.obj['nc'].get(request)[0]
    print_object(result, only=ctx.obj['show_only'], exclude=['blob'])


@vsdcli.command(name='metadata-add-tag')
@click.argument('metadata-id', metavar='<metadata ID>',
                required=True)
@click.option('--tag', metavar='<ID>', multiple=True, required=True,
              help="tag's ID to add. Can be repeted")
@click.option('--global', 'is_global', is_flag=True,
              help="Update global metadata instead of local")
@click.pass_context
def metadata_add_tag(ctx, metadata_id, is_global, tag):
    """Add single or multiple tag to an existing metadata"""
    if is_global:
        request = "globalmetadatas/%s" % metadata_id
    else:
        request = "metadatas/%s" % metadata_id
    params = {}
    params['metadataTagIDs'] = ctx.obj['nc'].get(request)[0]['metadataTagIDs']
    for t in tag:
        params['metadataTagIDs'].append(t)
    ctx.obj['nc'].put(request, params)
    result = ctx.obj['nc'].get(request)[0]
    print_object(result, only=ctx.obj['show_only'], exclude=['blob'])


@vsdcli.command(name='metadata-remove-tag')
@click.argument('metadata-id', metavar='<metadata ID>',
                required=True)
@click.option('--tag', metavar='<ID>', multiple=True, required=True,
              help="tag's ID to remove. Can be repeted")
@click.option('--global', 'is_global', is_flag=True,
              help="Update global metadata instead of local")
@click.pass_context
def metadata_remove_tag(ctx, metadata_id, is_global, tag):
    """remove single or multiple tag to an existing metadata"""
    if is_global:
        request = "globalmetadatas/%s" % metadata_id
    else:
        request = "metadatas/%s" % metadata_id
    existing_tag = ctx.obj['nc'].get(request)[0]['metadataTagIDs']
    if not len(existing_tag):
        print("Error: There is no tag for metadata %s" % metadata_id)
        exit(1)
    params = {'metadataTagIDs': []}
    change = False
    for t in existing_tag:
        if t not in tag:
            params['metadataTagIDs'].append(t)
        else:
            change = True
    if not change:
        print("Warning: none of given tag exists in metadata %s" % metadata_id)
        exit(1)
    ctx.obj['nc'].put(request, params)
    result = ctx.obj['nc'].get(request)[0]
    print_object(result, only=ctx.obj['show_only'], exclude=['blob'])


@vsdcli.command(name='metadata-delete')
@click.argument('metadata-id', metavar='<metadata ID>',
                required=True)
@click.pass_context
def metadata_delete(ctx, metadata_id):
    """Delete a given metadata"""
    ctx.obj['nc'].delete("metadatas/%s" % metadata_id)


@vsdcli.command(name='metadatatag-list')
@click.option('--enterprise-id', metavar='<ID>')
@click.option('--metadata-id', metavar='<ID>')
@click.option('--filter', metavar='<filter>',
              help="Filter for name, description, associatedExternalServiceID"
                   ", autoCreated, ID, externalID")
@click.pass_context
def metadatatag_list(ctx, enterprise_id, metadata_id, filter):
    """Show all metadata tags for a given enterprise or metadata.
       If nor enterprise or metadata is given, list all metadata tags
       associated to DC"""
    if enterprise_id:
        request = "enterprises/%s/metadatatags" % enterprise_id
    elif metadata_id:
        request = "metadatas/%s/metadatatags" % metadata_id
    else:
        request = "metadatatags"
    result = ctx.obj['nc'].get(request, filter=filter)
    table = PrettyTable(["ID", "name", "description"])
    for line in result:
        table.add_row([line['ID'],
                       line['name'],
                       line['description']])
    print table


@vsdcli.command(name='metadatatag-show')
@click.argument('metadatatag-id', metavar='<ID>', required=True)
@click.pass_context
def metadatatag_show(ctx, metadatatag_id):
    """Show information for a given metadata tag id"""
    result = ctx.obj['nc'].get("metadatatags/%s" % metadatatag_id)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='metadatatag-create')
@click.argument('name', metavar='<name>', required=True)
@click.option('--enterprise-id', metavar='<ID>')
@click.option('--description')
@click.pass_context
def metadatatag_create(ctx, name, enterprise_id, description):
    """Add an metadatatag to a given enterprise. CSPROOT can create DC
       associated tag if enterprise id is not specified"""
    if enterprise_id:
        request = "enterprises/%s/metadatatags" % enterprise_id
    else:
        request = "metadatatags"
    params = {'name': name,
              'description': description}
    result = ctx.obj['nc'].post(request, params)[0]
    print_object(result, only=ctx.obj['show_only'])


@vsdcli.command(name='metadatatag-delete')
@click.argument('metadatatag-id', metavar='<metadatatag ID>', required=True)
@click.pass_context
def metadatatag_delete(ctx, metadatatag_id):
    """Delete a given metadatatag"""
    ctx.obj['nc'].delete("metadatatags/%s" % metadatatag_id)


@vsdcli.command(name='metadatatag-update')
@click.argument('metadatatag-id', metavar='<metadatatag ID>', required=True)
@click.option('--key-value', metavar='<key:value>', multiple=True)
@click.pass_context
def metadatatag_update(ctx, metadatatag_id, key_value):
    """Update key/value for a given metadatatag"""
    params = {}
    for kv in key_value:
        key, value = kv.split(':', 1)
        params[key] = value
    ctx.obj['nc'].put("metadatatags/%s" % metadatatag_id, params)
    result = ctx.obj['nc'].get("metadatatags/%s" % metadatatag_id)[0]
    print_object(result, only=ctx.obj['show_only'])
