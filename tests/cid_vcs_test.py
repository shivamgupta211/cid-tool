
from __future__ import print_function, absolute_import

from .citool_utbase import citool_UTBase
from futoin.cid.rmstool import RmsTool

import os
import subprocess
import glob

class cid_VCS_UTBase ( citool_UTBase ) :
    __test__ = False
    
    @classmethod
    def setUpClass( cls ):
        super(cid_VCS_UTBase, cls).setUpClass()
        
        test_tar = os.path.basename( cls.TEST_DIR )
        cmd = [
            '/bin/tar', 'xf',
            os.path.join(os.path.dirname(__file__), test_tar + '.tar'),
            '-C', cls.TEST_RUN_DIR
        ]
        subprocess.check_output( cmd, stdin=subprocess.PIPE )
    
    def test_10_tag( self ):
        self._call_citool( [
                'tag', 'branch_A',
                '--vcsRepo', self.VCS_REPO,
                '--wcDir', 'build_ver' ] )
        
    def test_20_tag_invalid_ver( self ):
        self._call_citool( [
            'tag', 'branch_A', 'v1.2.4',
            '--vcsRepo', self.VCS_REPO,
            '--wcDir', 'build_ver' ], returncode=1 )
        
    def test_21_tag_ver( self ):
        self._call_citool( [
            'tag', 'branch_A', '1.3.0',
            '--vcsRepo', self.VCS_REPO,
            '--wcDir', 'build_ver' ] )
        
    def test_30_prepare( self ):
        self._call_citool( [ 'prepare', 'branch_A', '--vcsRepo', self.VCS_REPO, '--wcDir', 'prep_dir' ] )
        self._goToBase()
        self._call_citool( [ 'prepare', 'v1.2.3', '--wcDir', 'prep_dir' ] )
        self._goToBase()
        os.chdir( 'prep_dir' )
        self._call_citool( [ 'prepare', 'branch_A' ] )
    
    def test_40_ci_build( self ):
        try:
            os.makedirs( 'rms_repo/Builds')
            os.makedirs( 'rms_repo/Verified')
            os.makedirs( 'rms_repo/Prod')
        except :
            pass
        
        rms_dir = os.path.realpath( 'rms_repo' )

        self._call_citool( [ 'ci_build', 'branch_A', 'Builds',
                            '--vcsRepo', self.VCS_REPO,
                            '--rmsRepo', 'scp:' + rms_dir ] )
        
        self._goToBase()
        os.chdir( 'ci_build' )
        package = subprocess.check_output( 'cd %s && ls Builds/*.txz | head -1' % rms_dir, shell=True )
        try:
            package = str(package, 'utf8').strip()
        except TypeError:
            package = str(package).strip()
            
        package_base = os.path.basename( package )
        pkg_hash = RmsTool.rmsCalcHash( package_base, 'sha512' )
        os.unlink( package_base )
        self._call_citool( [ 'promote', package, 'Verified',
                            '--rmsRepo', 'scp:' + rms_dir,
                            '--rmsHash', pkg_hash ] )
        
        self._goToBase()
        os.chdir( 'ci_build' )
        self._call_citool( [ 'promote', package, 'Prod',
                            '--rmsRepo', 'scp:' + rms_dir,
                            '--rmsHash', pkg_hash ] )
        
        self._goToBase()
        content = subprocess.check_output( 'tar tJf rms_repo/Prod/wc-CI-1.3.0-*.txz | /usr/bin/sort -f', shell=True )
        try:
            content = str(content, 'utf8')
        except TypeError:
            content = str(content)
        req_content=[
            '',
            './',
            './bower.json',
            './bower.json.gz',
            './BRANCH_A',
            './composer.json',
            './composer.json.gz',
            './Gruntfile.js',
            './Gruntfile.js.gz',
            './node_modules/',
            './.package.checksums',
            './package.json',
            './package.json.gz',
            './vendor/',
            './vendor/autoload.php',
            './vendor/composer/',
            './vendor/composer/autoload_classmap.php',
            './vendor/composer/autoload_namespaces.php',
            './vendor/composer/autoload_psr4.php',
            './vendor/composer/autoload_real.php',
            './vendor/composer/autoload_static.php',
            './vendor/composer/ClassLoader.php',
            './vendor/composer/LICENSE',
            './vendor/composer/installed.json',
            './vendor/composer/installed.json.gz',
        ]
        self.maxDiff = 1024
        content = sorted(content.split("\n"))
        req_content = sorted(req_content)
        self.assertEqual( content, req_content )
        
    def test_40_release_build( self ):
        rms_dir = os.path.realpath( 'rms_repo' )

        self._call_citool( [ 'ci_build', 'v1.2.3', 'Builds',
                            '--vcsRepo', self.VCS_REPO,
                            '--rmsRepo', 'scp:' + rms_dir ] )
        
    def test_50_rms_deploy( self ):
        rms_dir = os.path.realpath( 'rms_repo' )
        
        os.makedirs( 'test_deploy' )
        os.chdir( 'test_deploy' )
        self._call_citool( [ 'deploy', 'Prod',
                            '--rmsRepo', 'scp:' + rms_dir ] )

        self.assertTrue(glob.glob('wc-CI-1.3.0-*'))
        
    def test_51_rms_redeploy( self ):
        rms_dir = os.path.realpath( 'rms_repo' )
        
        os.chdir( 'test_deploy' )
        self._call_citool( [ 'deploy', 'Prod',
                            '--rmsRepo', 'scp:' + rms_dir,
                            '--redeploy'] )
        
        self.assertTrue(glob.glob('wc-CI-1.3.0-*'))
        
    def test_52_rms_deploy_package( self ):
        rms_dir = os.path.realpath( 'rms_repo' )
        
        os.chdir( 'test_deploy' )
        
        package = 'wc-1.2.3-*'

        self._call_citool( [ 'deploy', 'Builds', package,
                            '--rmsRepo', 'scp:' + rms_dir ] )
        
        self.assertTrue(glob.glob('wc-1.2.3-*'))
        
        self._call_citool( [ 'deploy', 'Builds', package,
                            '--rmsRepo', 'scp:' + rms_dir ],
                            returncode=1 )
        
        self.assertTrue(glob.glob('wc-1.2.3-*'))
        
        self._call_citool( [ 'deploy', 'Builds', package,
                            '--rmsRepo', 'scp:' + rms_dir,
                            '--redeploy' ] )
        
        self.assertTrue(glob.glob('wc-1.2.3-*'))

    def test_60_vcstag_deploy( self ):
        os.chdir( 'test_deploy' )
        
        self._call_citool( [ 'deploy', 'vcstag', '--vcsRepo', self.VCS_REPO ] )
        self.assertTrue(os.path.exists('v1.3.0'))
        
        self._call_citool( [ 'deploy', 'vcstag', '--vcsRepo', self.VCS_REPO ], returncode=1 )
        self.assertTrue(os.path.exists('v1.3.0'))
        
        self._call_citool( [ 'deploy', 'vcstag', '--vcsRepo', self.VCS_REPO, '--redeploy' ] )
        self.assertTrue(os.path.exists('v1.3.0'))
        
    def test_61_vcstag_deploy_ref( self ):
        os.chdir( 'test_deploy' )
        
        self._call_citool( [ 'deploy', 'vcstag', '--vcsRepo', self.VCS_REPO, 'v1.2.*' ] )
        self.assertTrue(os.path.exists('v1.2.4'))

        self._call_citool( [ 'deploy', 'vcstag', '--vcsRepo', self.VCS_REPO, 'v1.2.4' ], returncode=1 )
        self.assertTrue(os.path.exists('v1.2.4'))

        self._call_citool( [ 'deploy', 'vcstag', '--vcsRepo', self.VCS_REPO, 'v1.2.*', '--redeploy' ] )
        self.assertTrue(os.path.exists('v1.2.4'))
        
        self._call_citool( [ 'deploy', 'vcstag', '--vcsRepo', self.VCS_REPO, 'v1.2.3' ] )
        self.assertTrue(os.path.exists('v1.2.3'))
        
    def test_70_vcsref_deploy( self ):
        os.chdir( 'test_deploy' )
        
        self._call_citool( [ 'deploy', 'vcsref', 'branch_A', '--vcsRepo', self.VCS_REPO ] )
        self.assertTrue(glob.glob('branch_A_*'))
        
        self._call_citool( [ 'deploy', 'vcsref', 'branch_A', '--vcsRepo', self.VCS_REPO ], returncode=1 )
        self.assertTrue(glob.glob('branch_A_*'))
        
        self._call_citool( [ 'deploy', 'vcsref', 'branch_A', '--vcsRepo', self.VCS_REPO, '--redeploy' ] )
        self.assertTrue(glob.glob('branch_A_*'))
        

#=============================================================================        
class cid_git_Test ( cid_VCS_UTBase ) :
    __test__ = True
    TEST_DIR = os.path.join(cid_VCS_UTBase.TEST_RUN_DIR, 'test_git')
    VCS_REPO = 'git:' + os.path.join( TEST_DIR, 'repo' )
        
#=============================================================================
class cid_hg_Test ( cid_VCS_UTBase ) :
    __test__ = True
    TEST_DIR = os.path.join(cid_VCS_UTBase.TEST_RUN_DIR, 'test_hg')
    VCS_REPO = 'hg:' + os.path.join( TEST_DIR, 'repo' )

#=============================================================================
class cid_svn_Test ( cid_VCS_UTBase ) :
    __test__ = True
    TEST_DIR = os.path.join(cid_VCS_UTBase.TEST_RUN_DIR, 'test_svn')
    VCS_REPO = 'svn:file://' + os.path.join( TEST_DIR, 'repo' )