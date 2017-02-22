
from .citool_utbase import citool_UTBase
import os

class citool_Tool_UTBase ( citool_UTBase ) :
    __test__ = False
    TOOL_NAME = 'invalid'
    TOOL_MANAGED = True
    TOOL_ENV = {}
    _env_backup = None

    @classmethod
    def setUpClass( cls ):
        cls._env_backup = {}
        cls.TEST_DIR = os.path.join(cls.TEST_RUN_DIR, 'tool_'+cls.TOOL_NAME)
        super(citool_Tool_UTBase, cls).setUpClass()
        os.mkdir( cls.TEST_DIR )
        os.chdir( cls.TEST_DIR )
        
        for k, v in cls.TOOL_ENV.items():
            cls._env_backup[k] = os.environ.get(k, None)
            os.environ[k] = v
            
    @classmethod
    def tearDownClass( cls ):
        for k, v in cls._env_backup.items():
            if v:
                os.environ[k] = v
            else:
                del os.environ[k]
        
    def test_10_tool_uninstall( self ):
        if self.TOOL_MANAGED:
            self._call_citool( [ 'tool', 'uninstall', self.TOOL_NAME ] )
        
    def test_20_tool_test( self ):
        if self.TOOL_MANAGED:
            try:
                self._call_citool( [ 'tool', 'test', self.TOOL_NAME ] )
            except:
                return
            raise RuntimeError('Tool must not be present')

    def test_30_tool_install( self ):
        if self.TOOL_MANAGED:
            self._call_citool( [ 'tool', 'install', self.TOOL_NAME ] )

    def test_40_tool_test( self ):
        self._call_citool( [ 'tool', 'test', self.TOOL_NAME ] )

    def test_50_tool_update( self ):
        if self.TOOL_MANAGED:
            self._call_citool( [ 'tool', 'update', self.TOOL_NAME ] )
        

# 10
#-----
for t in ['bash', 'curl', 'git', 'hg', 'svn', 'gpg', 'scp', 'ssh']:
    cls = 'citool_Tool_10_' + t
    globals()[cls] = type(cls, (citool_Tool_UTBase, ), {
        '__test__' : True,
        'TOOL_NAME' : t,
        'TOOL_MANAGED' : False,
    })
    
# 20
#-----
for t in ['nvm', 'rvm', 'phpbuild']: # virtualenv
    cls = 'citool_Tool_20_' + t
    globals()[cls] = type(cls, (citool_Tool_UTBase, ), {
        '__test__' : True,
        'TOOL_NAME' : t,
    })

# 30
#-----
os.environ['rubyVer'] = 'ruby-2.3.3' # use available pre-built binary

for t in ['node', 'ruby']: # python
    cls = 'citool_Tool_30_' + t
    globals()[cls] = type(cls, (citool_Tool_UTBase, ), {
        '__test__' : True,
        'TOOL_NAME' : t,
    })
    
cls = 'citool_Tool_30_php'
globals()[cls] = type(cls, (citool_Tool_UTBase, ), {
    '__test__' : True,
    'TOOL_NAME' : t,
    'TOOL_ENV': {
        'phpVer' : '7',
    },
})
#--
cls = 'citool_Tool_30_php_system'
globals()[cls] = type(cls, (citool_Tool_UTBase, ), {
    '__test__' : True,
    'TOOL_NAME' : t,
    'TOOL_MANAGED' : False,
})

# 40
#-----
for t in ['npm', 'gem']: # pip
    cls = 'citool_Tool_40_' + t
    globals()[cls] = type(cls, (citool_Tool_UTBase, ), {
        '__test__' : True,
        'TOOL_NAME' : t,
        'TOOL_MANAGED' : False,
    })


# 50
#-----
for t in ['composer']:
    cls = 'citool_Tool_50_' + t
    globals()[cls] = type(cls, (citool_Tool_UTBase, ), {
        '__test__' : True,
        'TOOL_NAME' : t,
    })
