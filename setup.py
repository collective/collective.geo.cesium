from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.geo.cesium',
      version=version,
      description="Cesium view for collective.geo",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: GIS",
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        ],
      keywords='GIS Cesium Globe WebGL',
      author='Christian Ledermann',
      author_email='christian.ledermann@gmail.com',
      url='http://plone.org/products/collective.geo.cesium',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.geo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'collective.geo.settings',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
