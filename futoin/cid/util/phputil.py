
from ..mixins.ondemand import ext as _ext
from . import simple_memo as _simple_memo
from . import complex_memo as _complex_memo
from . import log as _log

_SYSTEM_VER = 'system'


@_simple_memo
def binaryVersions():
    detect = _ext.detect

    if detect.isDebian() or detect.isUbuntu():
        return ['5.6', '7.0', '7.1']

    if detect.isSCLSupported():
        return ['5.6', '7.0']

    if detect.isArchLinux():
        return ['5.6', '7.0', '7.1']

    if detect.isAlpineLinux():
        alpine_ver = detect.alpineLinuxVersion()

        if alpine_ver >= ['3', '6']:
            return ['5.6', '7.1']

        if alpine_ver >= ['3', '5']:
            return ['5.6', '7.0']

        return ['5.6']

    if detect.isMacOS():
        return ['5.6', '7.0', '7.1']

    return None


@_complex_memo
def basePackage(ver):
    detect = _ext.detect
    ver_nodot = ver.replace('.', '')

    if detect.isDebian() or detect.isUbuntu():
        if ver == _SYSTEM_VER:
            if detect.osCodeName() in ['jessie', 'trusty']:
                return 'php5'

            return 'php'

        return 'php{0}'.format(ver)

    if detect.isSCLSupported():
        return 'rh-php{0}'.format(ver_nodot)

    if detect.isArchLinux():
        if isArchLatest(ver):
            return 'php'

        return 'php{0}'.format(ver_nodot)

    if detect.isAlpineLinux():
        if isAlpineSplit():
            return 'php{0}'.format(ver.split('.')[0])

        return 'php'

    if detect.isMacOS():
        return 'homebrew/php/php{0}'.format(ver_nodot)

    if detect.isFedora():
        return 'php'

    if detect.isOpenSUSE():
        return 'php7'

    if detect.isSLES():
        return 'php5'

    return 'php'


def createBinDir(env, php_ver, src, bin_name):
    ospath = _ext.ospath
    os = _ext.os
    pathutil = _ext.pathutil

    php_dir = ospath.join(os.environ['HOME'], '.php', php_ver)
    php_dir = env.setdefault('phpDir', php_dir)

    php_bin_dir = ospath.join(php_dir, 'bin')
    php_bin = ospath.join(php_bin_dir, bin_name)

    if not ospath.exists(php_bin):
        os.makedirs(php_bin)

    dst = ospath.join(php_bin, bin_name)
    pathutil.rmTree(dst)
    _ext.pathutil.addBinPath(php_bin_dir, True)

    if ospath.exists(src):
        os.symlink(src, dst)


@_simple_memo
def isAlpineSplit():
    return _ext.detect.alpineLinuxVersion() >= ['3', '5']


def isArchLatest(ver):
    return ver == '7.1'

# do not cache


def extPackages(env):
    base_pkg = basePackage(env['phpVer'])
    pkg_prefix = '{0}-'.format(base_pkg)
    pkg_prefix2 = None
    detect = _ext.detect

    known = {k: None for k in knownExtensions()}
    update = {}
    pkg2key = {}
    found = None
    #---
    res = _ext.executil.callExternal(
        [env['phpBin'], '-m'],
        verbose=False)
    res = res.strip().split('\n')

    for r in res:
        r = r.lower().strip()

        if r == 'libxml':
            r = 'xml'
        elif r == 'Zend OPcache':
            r = 'opcache'

        if r in known:
            known[r] = True

    #---
    if detect.isDebian() or detect.isUbuntu():
        pkg2key = {
            'mysqlnd': 'mysql',
            'sqlite3': 'sqlite',
        }

        apt_cache = _ext.pathutil.which('apt-cache')
        found = _ext.executil.callExternal(
            [apt_cache, 'search', pkg_prefix],
            verbose=False)
        found = found.strip().split('\n')

    elif detect.isSCLSupported():
        pkg_prefix = '{0}-php-'.format(base_pkg)
        pkg_prefix2 = '{0}-php-pecl-'.format(base_pkg)
        pkg2key = {
            'mysqlnd': 'mysql',
            'process': 'pcntl',
        }

        yum = _ext.pathutil.which('yum')
        found = _ext.executil.callExternal(
            [yum, 'search', '-q', pkg_prefix],
            verbose=False).strip()
        found += _ext.executil.callExternal(
            [yum, 'search', '-q', pkg_prefix2],
            verbose=False).strip()
        found = found.split('\n')

    elif detect.isArchLinux():
        pass

    elif detect.isAlpineLinux():
        apk = '/sbin/apk'
        found = _ext.executil.callExternal(
            [apk, 'search', pkg_prefix],
            verbose=False)
        found = found.strip().split('\n')

    elif detect.isMacOS():
        found = _ext.install.brewSearch(pkg_prefix)
        pkg2key = {
            'pdo-pgsql': 'pgsql',
        }

    elif detect.isFedora():
        pkg_prefix2 = pkg_prefix + 'pecl-'
        pkg2key = {
            'mysqlnd': 'mysql',
            'process': 'pcntl',
        }

        dnf = _ext.pathutil.which('dnf')
        found = _ext.executil.callExternal(
            [dnf, 'search', '-q', pkg_prefix],
            verbose=False).strip()
        found += _ext.executil.callExternal(
            [dnf, 'search', '-q', pkg_prefix2],
            verbose=False).strip()
        found = found.split('\n')

    elif detect.isOpenSUSE() or detect.isSLES():
        zypper = _ext.pathutil.which('zypper')
        res = _ext.executil.callExternal(
            [zypper, 'search', '-t', 'package', pkg_prefix],
            verbose=False)

        found = []

        for f in found:
            f = f.split(' | ')

            if len(f) > 2:
                f = f[1].strip()
                found.append(f)

    #---
    if found:
        for r in res:
            r = r.split()

            if not r:
                continue

            p = r[0]
            k = p.replace(pkg_prefix, '')

            if pkg_prefix2:
                k = p.replace(pkg_prefix2, '')

            k = pkg2key.get(k, k)

            if k in known:
                update[k] = p

    #---
    for (k, v) in update.items():
        if k in known:
            if not known[k]:
                known[k] = v
        else:
            _log.errorExit('Unknown generic PHP ext "{0}"'.format(k))

    return res


def knownExtensions():
    return [
        'amqp',
        'apcu',
        'ast',
        'bcmath',
        'bz2',
        'blitz',
        'calendar',
        'ctype',
        'curl',
        'couchbase',
        'date',
        'ds',
        'ev',
        'enchant',
        'event',
        'exif',
        'fileinfo',
        'filter',
        'ftp',
        'gettext',
        'gd',
        'gearman',
        'geoip',
        'gmagick',
        'gmp',
        'gnupg',
        'grpc',
        'hash',
        'http',
        'iconv',
        'imagick',
        'imap',
        'intl',
        'json',
        'ldap',
        'kafka',
        'mailparse',
        'mbstring',
        'mysql',
        'mcrypt',
        'memcache',
        'memcached',
        'mongodb',
        'msgpack',
        'odbc',
        'opcache',
        'openssl',
        'pcntl',
        'pcre',
        'pdo',
        'pdo_mysql',
        'pdo_pgsql',
        'pdo_sqlite',
        'phar',
        'pgsql',
        'posix',
        'pspell',
        'readline',
        'recode',
        'redis',
        'session',
        'shmop',
        'snmp',
        'simplexml',
        'soap',
        'sockets',
        'spl',
        'sqlite',
        'ssh2',
        'sysvmsg',
        'sysvsem',
        'sysvshm',
        'tokenizer',
        'uv',
        'xdebug',
        'xml',
        'xmlreader',
        'xmlrpc',
        'xmlwriter',
        'xsl',
        'zlib',
        'zip',
        'zmq',
    ]


def installExtensions(env, exts, permissive=True):
    mapping = extPackages(env)
    install = _ext.install

    exts = _ext.configutil.listify(exts)

    for ext in exts:
        if ext in mapping:
            pkg = mapping[ext]

            if type(pkg) == type(''):
                install.deb(pkg)
                install.rpm(pkg)
                install.brew(pkg)
                install.apk(pkg)
                install.pacman(pkg)
                install.emerge(pkg)
            elif not pkg:
                msg = 'Not supported PHP extension: {0}'.format(ext)

                if permissive:
                    _log.warn(msg)
                else:
                    _log.errorExit(msg)
        else:
            _log.errorExit('Unknown PHP extension "{0}\nKnown: \n* {1}'.format(
                mapping, '\n*'.join(knownExtensions())))