from prettytable import PrettyTable
import click
from open_vsdcli.vsd_client import VSDConnection


def print_object(obj, only=None, exclude=[]):
    def _format_multiple_values(values):
        """Format list in string to be printable as prettytable"""
        row_value = ""
        if len(values) > 0:
            last = values.pop()
            for o in values:
                row_value += "%s\n" % o
            row_value += last
        return row_value

    def _print_table(obj, exclude):
        from time import gmtime
        from time import strftime
        table = PrettyTable(["Field", "Value"])
        table.align["Field"] = "l"

        for key in obj.keys():
            if key not in exclude:
                if type(obj[key]) is list:
                    table.add_row([
                        key,
                        _format_multiple_values(obj[key])
                    ])
                else:
                    if key.endswith(('Date', 'Expiry')) and \
                       not obj[key] == 'null' and obj[key]:
                        value = strftime(
                            "%Y-%m-%d %H:%M:%S UTC",
                            gmtime(float(obj[key])/1000)
                        )
                    else:
                        value = obj[key]
                    table.add_row([key, value])
        print(table)
    if only:
        if only in obj:
            print(obj[only])
        else:
            print("No such key : %s" % only)
    else:
        _print_table(obj, exclude)


def check_id(one_and_only_one=True, **ids):
    # Remove '_id' at the end of key names
    new_ids = {}
    for k, v in ids.items():
        k = '_'.join(k.split('_')[0:-1])
        new_ids[k] = v
    ids = new_ids

    # Check one and only one id is specified
    nb_ids = 0
    for k, v in ids.items():
        if v is not None:
            nb_ids += 1
            good_k = k
    if nb_ids == 0 and one_and_only_one is False:
        return None, None
    elif nb_ids != 1:
        raise click.exceptions.UsageError(
            "You must specify one and only one id in %s" % ids.keys())
    return good_k, ids[good_k]


def netmask_to_length(netmask):
    tableSubnet = {
        '0':   0,
        '128': 1,
        '192': 2,
        '224': 3,
        '240': 4,
        '248': 5,
        '252': 6,
        '254': 7,
        '255': 8
    }
    netmask_splited = str(netmask).split('.')
    length = tableSubnet[netmask_splited[0]] + \
        tableSubnet[netmask_splited[1]] + \
        tableSubnet[netmask_splited[2]] + \
        tableSubnet[netmask_splited[3]]
    return str(length)


def length_to_netmask(length):
    octet = []
    for i in [3, 2, 1, 0]:
        octet.append(str((0xffffffff << (32 - int(length)) >> i*8) & 0xff))
    return '.'.join(octet)


def print_creds(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('export VSD_USERNAME=<username>')
    click.echo('export VSD_PASSWORD=<password>')
    click.echo('export VSD_ENTERPRISE=csp')
    click.echo('export VSD_API_VERSION=5_0')
    click.echo('export VSD_API_URL=https://<host>:<port>')
    ctx.exit()


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    import pbr.version
    version_info = pbr.version.VersionInfo('open-vsdcli')
    click.echo(version_info.version_string())
    ctx.exit()


def print_completion(ctx, param, value):
    from os import environ
    from click._bashcomplete import get_completion_script
    if not value or ctx.resilient_parsing:
        return

    try:
        env_shell = environ['SHELL'].lower()
    except:
        click.echo('Unable to detect shell. Missing "SHELL" env variable.')
        ctx.exit()

    shell = [el for el in ['bash', 'zsh', 'fish'] if el in env_shell]
    if not shell:
        click.echo('Shell "%s" not supported for completion.' % env_shell)
        click.echo('Supported shell: "bash", "zsh", "fish".')
        ctx.exit()

    shell = shell[0]
    click.echo('# vsd %s completion start' % shell)
    print(get_completion_script("vsd", "_VSD_COMPLETE", shell).strip())
    click.echo('# vsd %s completion end' % shell)
    ctx.exit()


@click.group()
@click.option('--creds', is_flag=True, callback=print_creds, is_eager=True,
              expose_value=False, help='Display creds example')
@click.option('--version', is_flag=True, callback=print_version, is_eager=True,
              expose_value=False, help='Display version and exit')
@click.option('--vsd-api-url', metavar='<url>', envvar='VSD_API_URL',
              required=True,
              help='VSD url http(s)://hostname:port/nuage/api'
              ' (Env: VSD_API_URL)')
@click.option('--vsd-username', metavar='<username>', envvar='VSD_USERNAME',
              required=True,
              help='VSD Authentication username (Env: VSD_USERNAME)')
@click.option('--vsd-password', metavar='<password>', envvar='VSD_PASSWORD',
              required=True,
              help='VSD Authentication password (Env: VSD_PASSWORD)')
@click.option('--vsd-enterprise', metavar='<enterprise>',
              envvar='VSD_ENTERPRISE',
              required=True,
              help='VSD Authentication enterprise (Env: VSD_ENTERPRISE)')
@click.option('--vsd-api-version', metavar='<api version>',
              envvar='VSD_API_VERSION',
              required=True,
              help='VSD Authentication organization (Env: VSD_API_VERSION)')
@click.option('--vsd-disable-proxy',
              envvar='VSD_DISABLE_PROXY',
              is_flag=True,
              help='Disable proxy if defined via env http(s)_proxy'
              ' (Env: VSD_DISABLE_PROXY)')
@click.option('--vsd-http-proxy',
              envvar='VSD_HTTP_PROXY', metavar='<127.0.0.1:3128>',
              help='Use this proxy to reach the vsd and override env'
              ' http(s)_proxy. (Env: VSD_HTTP_PROXY)')
@click.option('--vsd-https-proxy',
              envvar='VSD_HTTPS_PROXY', metavar='<127.0.0.1:3128>',
              help='Use this proxy to reach the vsd and override env'
              ' https_proxy. If ommited, https proxy will be set with the'
              ' given http-proxy (Env: VSD_HTTPS_PROXY)')
@click.option('--show-only', metavar='<key>',
              help='Show only the value for a given key'
                   ' (usable for show and create command)')
@click.option('--debug', is_flag=True,
              help='Active debug for request and response')
@click.option('--force-auth', is_flag=True,
              help='Do not use existing APIkey. Replay authentication')
@click.option('--completion', is_flag=True, callback=print_completion,
              is_eager=True, expose_value=False,
              help='Display script to enable completion')
@click.pass_context
def vsdcli(ctx, vsd_username, vsd_password, vsd_enterprise,
           vsd_api_version, vsd_api_url, show_only, vsd_disable_proxy,
           vsd_http_proxy, vsd_https_proxy, debug, force_auth):
    """Command-line interface to the VSD APIs"""
    if vsd_http_proxy and vsd_https_proxy:
        proxies = {
                "http": vsd_http_proxy,
                "https": vsd_https_proxy}
    elif vsd_http_proxy and not vsd_https_proxy:
        proxies = {
                "http": vsd_http_proxy,
                "https": vsd_http_proxy}
    elif not vsd_http_proxy and not vsd_https_proxy:
        proxies = {
                "http": None,
                "https": None}
    else:
        raise click.exceptions.UsageError(
                "https proxy can be ommited when http proxy is given, but not"
                " the oposite")
    nc = VSDConnection(
            vsd_username,
            vsd_password,
            vsd_enterprise,
            vsd_api_url,
            vsd_api_version,
            disable_proxy=vsd_disable_proxy,
            proxy=proxies,
            debug=debug,
            force_auth=force_auth
         )
    ctx.obj['nc'] = nc
    ctx.obj['show_only'] = show_only


@vsdcli.command(name='me-show')
@click.option('--verbose', count=True, help='Show APIKey')
@click.pass_context
def me_show(ctx, verbose):
    """Show my own user information"""
    result = ctx.obj['nc'].me()[0]
    if verbose >= 1:
        print_object(result)
    else:
        print_object(result, exclude=['APIKey'], only=ctx.obj['show_only'])


@vsdcli.command(name='free-api')
@click.argument('ressource', metavar='<ressource>', required=True)
@click.option('--verb',
              type=click.Choice(['PUT',
                                 'GET',
                                 'POST',
                                 'DELETE']),
              default='GET',
              help='Default : GET')
@click.option('--header', metavar='<name:value>', multiple=True,
              help='Add header to the request. Can be repeated.')
@click.option('--key-value', metavar='<key:value>', multiple=True,
              help='Specify body in key/value pair.'
                   ' Can be repeated. Incompatible with --body.')
@click.option('--body', metavar='<data json>',
              help='Specify body of the request in json format.'
                   ' Incompatible with --key-value.')
@click.pass_context
def free_api(ctx, ressource, verb, header, key_value, body):
    """build your own API call (with headers and data)"""
    import json
    if key_value and body:
        raise click.exceptions.UsageError(
            "Use body or key-value")
    if key_value:
        params = {}
        for kv in key_value:
            key, value = kv.split(':', 1)
            params[key] = value
    if body:
        try:
            params = json.loads(body)
        except ValueError:
            raise click.exceptions.UsageError(
                "Body could not be decoded as JSON")
    h = {}
    if header:
        for kv in header:
            key, value = kv.split(':', 1)
            h[key] = value
    if verb == 'GET':
        result = ctx.obj['nc'].get(ressource, headers=h)
    elif verb == 'PUT':
        result = ctx.obj['nc'].put(ressource, params, headers=h)
    elif verb == 'POST':
        result = ctx.obj['nc'].post(ressource, params, headers=h)
    elif verb == 'DELETE':
        result = ctx.obj['nc'].delete(ressource)
    print(json.dumps(result, indent=4))
