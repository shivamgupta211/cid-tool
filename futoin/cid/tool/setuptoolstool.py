
from ..buildtool import BuildTool
from ..testtool import TestTool
from .piptoolmixin import PipToolMixIn


class setuptoolsTool(PipToolMixIn, BuildTool, TestTool):
    """Easily download, build, install, upgrade, and uninstall Python packages.

Home: https://pypi.python.org/pypi/setuptools

Not assumed to be used directly.

Build targets:
    prepare -> {removes build & dist folders}
    build -> ['sdist', 'bdist_wheel']
    package -> {uses result of build in dist/}
Override targets with .config.toolTune.    

"""
    __slots__ = ()

    def autoDetectFiles(self):
        return 'setup.py'

    def uninstallTool(self, env):
        pass

    def initEnv(self, env):
        ospath = self._ospath
        virtualenv_dir = env['virtualenvDir']
        self._have_tool = ospath.exists(
            ospath.join(virtualenv_dir, 'bin', 'easy_install'))

    def onPrepare(self, config):
        targets = self._getTune(config, 'prepare', ['build', 'dist'])
        targets = self._configutil.listify(targets)

        for d in targets:
            self._pathutil.rmTree(d)

    def onBuild(self, config):
        env = config['env']
        self._requirePip(env, 'wheel')

        targets = self._getTune(config, 'build', ['sdist', 'bdist_wheel'])
        targets = self._configutil.listify(targets)

        self._executil.callExternal([env['pythonBin'], 'setup.py'] + targets)

    def onPackage(self, config):
        target = self._getTune(config, 'package', 'dist')
        self._pathutil.addPackageFiles(config, self._ospath.join(target, '*'))

    def onCheck(self, config):
        env = config['env']
        self._requirePip(env, 'docutils')
        self._requirePip(env, 'readme')
        self._executil.callExternal(
            [env['pythonBin'], 'setup.py', 'check', '-mrs'])
