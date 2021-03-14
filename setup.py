from distutils.core import setup
setup(
  name = 'serializer',
  packages = ['serializer'],
  version = '0.1',
  license='MIT',
  description = 'A Python module to help encode and decode network packets.',
  author = 'Alvin Lin',
  author_email = 'hungyeh.alvin.lin@gmail.com',
  url = 'https://github.com/bubblemans/network-serializer',
  download_url = 'https://github.com/bubblemans/network-serializer/archive/v0.1.tar.gz',
  keywords = ['network', 'serilize', 'serializer', 'encode', 'decode', 'packet'],
  install_requires=[],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)