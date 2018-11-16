from setuptools import find_packages, setup


with open('README.md', 'r') as f:
    long_description = f.read()


setup(
    name='montague-nlu',
    version='0.1.3',
    description='Natural language understanding system',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    author='Ian Fisher',
    author_email='iafisher@protonmail.com',
    entry_points={
        'console_scripts': [
            'montague = montague.montague:run_shell',
        ],
    },
    packages=find_packages(exclude=['tests']),
    package_data={'montague': ['resources/*json']},
    install_requires=[
        'lark-parser==0.6.4',
    ],
    project_urls={
        'Source': 'https://github.com/iafisher/montague',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)
