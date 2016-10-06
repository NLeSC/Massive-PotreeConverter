from distutils.core import setup
import subprocess, sys

# First we check PDAL in installed and in the PATH
(out,err) = subprocess.Popen('pdal -help', shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
if out.decode(sys.stdout.encoding).count('PDAL') == 0:
    print('Installation could not be done: PDAL could not be found.')
    sys.exit(1)

# Second we check PotreeConverter in installed and in the PATH
(out,err) = subprocess.Popen('PotreeConverter -h', shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
if out.decode(sys.stdout.encoding).count('usage: PotreeConverter') == 0:
    print('Installation could not be done: PotreeConverter could not be found.')
    sys.exit(1)

# Third we check LAStools in installed and in the PATH
(out,err) = subprocess.Popen('lasmerge -h', shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
if (out+err).decode(sys.stdout.encoding).count('LAStools') == 0:
    print('Installation could not be done: LAStools could not be found.')
    sys.exit(1)

# Fourth we see if pycoeman has been manually installed and is in PYTHONPATH
try:
    import pycoeman
except:
    print('Installation could not be done: pycoeman could not be found.')
    sys.exit(1)


setup(
    name='Massive-PotreeConverter',
    version='1.0.0',
    packages=['pympc', ],
    license='',
    long_description=open('README.md').read(),
    author='Oscar Martinez-Rubi',
    author_email='o.rubi@esciencecenter.nl',
    url='https://github.com/NLeSC/Massive-PotreeConverter',
    install_requires=[
          'lxml', 'pycoeman', 'numpy'],
    entry_points={
        'console_scripts': [
            'mpc-create-config-pycoeman=pympc.create_pycoeman_config_run_massive_potree_converter:main',
            'mpc-info=pympc.get_info:main',
            'mpc-tiling=pympc.generate_tiles:main',
            'mpc-merge=pympc.merge_potree:main',
            'mpc-merge-all=pympc.merge_potree_all:main',
            'mpc-wkt=pympc.get_wkt:main',
            'mpc-sort-index=pympc.sort_index:main',
            'mpc-db-extents=pympc.fill_db_extents:main',
            'mpc-db-extents-potree=pympc.fill_db_extents_potree:main',
        ],
    },
)
