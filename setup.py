from setuptools import find_packages, setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

# Call the setup function
if __name__ == '__main__':
    setup(
        name='scikit-sdr',
        version='0.3.dev0',
        description='Python 3 library that provides algorithms for building digital communication systems and for experimenting with DSP and SDR',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/dave-pi/scikit-sdr',
        author='David Pi',
        author_email='david.pinho@gmail.com',
        license='GPLv3+',
        project_urls={
            'Documentation': 'http://komm.readthedocs.io/',
            'Source': 'https://github.com/rwnobrega/komm/'},
        packages=find_packages(exclude=['gnuradio', 'docs', 'tests*']),
        test_suite='tests',
        setup_requires=['pytest-runner'],
        tests_require=['pytest'],
        python_requires='>=3.6',
        install_requires=['numpy>=1.19.1', 'scipy>=1.5.2', 'matplotlib>=3.2.1'],
        classifiers=[
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Intended Audience :: Science/Research',
            'Topic :: Scientific/Engineering'])
