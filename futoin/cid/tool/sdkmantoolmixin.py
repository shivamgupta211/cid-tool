#
# Copyright 2015-2017 (c) Andrey Galkin
#



from .bashtoolmixin import BashToolMixIn
from .javatoolmixin import JavaToolMixIn


class SdkmanToolMixIn(BashToolMixIn, JavaToolMixIn):
    __slots__ = ()

    def _needJDK(self):
        return True

    def getDeps(self):
        return (
            super(SdkmanToolMixIn, self).getDeps() +
            ['sdkman', 'java'] +
            (self._needJDK() and ['jdk'] or [])
        )

    def _sdkName(self):
        return self._name

    def _binName(self):
        return self._name

    def _setAutoAnswer(self, env):
        self._callBash(env,
                       'grep -q "sdkman_auto_answer=true" {0} || echo "sdkman_auto_answer=true" >> {0}'
                       .format(self._ospath.join(env['sdkmanDir'], 'etc', 'config')),
                       verbose=False
                       )

    def _callSdkman(self, env, cmd, verbose=True):
        return self._callBash(env,
                              'source {0} >/dev/null && sdk {1}'.format(
                                  env['sdkmanInit'],
                                  cmd
                              ),
                              verbose=verbose
                              )

    def _javaVersion(self, env):
        if not env.get('javaBin', None):
            return 0

        java_ver = self._callBash(
            env, '{0} -version 2>&1'.format(env['javaBin']), verbose=False)
        return int(self._ext.re.search('version "1\.([0-9]+)\.', java_ver).group(1))

    def _installTool(self, env):
        self._setAutoAnswer(env)
        self._callSdkman(env,
                         'install {0} {1}'.format(
                             self._sdkName(),
                             env.get(self._name + 'Ver', '')
                         )
                         )

    def _updateTool(self, env):
        self._setAutoAnswer(env)
        self._callSdkman(env,
                         'upgrade {0}'.format(
                             self._sdkName()
                         )
                         )

    def uninstallTool(self, env):
        ospath = self._ospath
        tool_dir = ospath.join(
            env['sdkmanDir'], 'candidates', self._sdkName())
        self._pathutil.rmTree(tool_dir)

    def initEnv(self, env):
        ospath = self._ospath
        if not env.get('sdkmanDir', None):
            return

        tool_dir = ospath.join(
            env['sdkmanDir'], 'candidates', self._sdkName(), 'current')

        if not ospath.exists(tool_dir):
            return

        try:
            env_to_set = self._callSdkman(env,
                                          'use {0} {1} >/dev/null && env | grep -i {0}'
                                          .format(self._sdkName(), env.get(self._name + 'Ver', '')),
                                          verbose=False
                                          )
        except:
            return

        if env_to_set:
            self._pathutil.updateEnvFromOutput(env_to_set)
            super(SdkmanToolMixIn, self).initEnv(env, self._binName())
