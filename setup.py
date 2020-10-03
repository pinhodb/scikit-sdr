from setuptools import setup

import sksdr

with open('README.md', 'r') as fh:
    long_description = fh.read()

DISTNAME         = 'scikit-sdr'
DESCRIPTION      = 'SDR scikit package'
LONG_DESCRIPTION = long_description
AUTHOR           = 'David Pi'
AUTHOR_EMAIL     = 'davidpinho@gmail.com'
MAINTAINER       = 'David Pi'
MAINTAINER_EMAIL = 'davidpinho@gmail.com'
URL              = 'http://projects.scipy.org/scipy/scikits'
LICENSE          = 'MIT'
DOWNLOAD_URL     = URL
PACKAGE_NAME     = 'sksdr'
EXTRA_INFO       = dict(
    python_requires='>=3.6',
    install_requires=['matplotlib', 'numpy', 'scipy'],
    classifiers=['Development Status :: 1 - Planning',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: BSD License',
                 'Topic :: Scientific/Engineering']
)

VERSION = sksdr.__version__

# Call the setup function
if __name__ == '__main__':
    setup(name=DISTNAME,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          url=URL,
          download_url=DOWNLOAD_URL,
          long_description=LONG_DESCRIPTION,
          long_description_content_type='text/markdown',
          include_package_data=True,
          test_suite='tests',
          setup_requires=['pytest-runner'],
          tests_require=['pytest'],
          version=VERSION,
          **EXTRA_INFO)
