from setuptools import setup

setup(name='ushapy',
      version='0.1',
      description='Ushahidi platform API tools',
      long_description='The Ushahidi platform from www.ushahidi.com is a tool used to map and classify crowdsourced inputs. This library uses the Ushahidi platform API to access data on any Ushahidi site with its API enabled.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing',
      ],
      keywords='Ushahidi crowdsource',
      url='http://github.com/bodacea/ushapy',
      author='Sara-Jayne Terp',
      author_email='sarajterp@gmail.com',
      license='MIT',
      packages=['ushapy'],
      install_requires=[
          'requests','time','json','datetime','requests.auth',
      ],
      include_package_data=True,
      zip_safe=False)