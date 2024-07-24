from setuptools import setup

with open('README.md', 'r') as fp:
    long_description = fp.read()

setup(
    name='S.T.E.L.A.R',
    version='1.0',
    description='Tools for derive stellar parameters, focused on stellar mass.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    keywords=['stellar parameters: mass', 'isochrone fitting', 'machine learning', 'robust statistics'],
    author='João Paulo Matos Dias Gomes',
    author_email='jpmdgomes.bf@gmail.com',
    packages=['stelar'],
    # install_requires=[WRITE THEM],
    classifiers=[
        'Development Status :: 1 - Beta',
        'Topic :: Astronomy/Astrophysics',
        'License :: [WHEN I GOT]',
        'Programming Language :: Python :: 3'
    ]
)
