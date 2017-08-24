from setuptools import setup, find_packages

setup(
    name='f2e',
    # version='0.0.5',
    version='0.0.0',
    # version_format='{tag}.dev{commitcount}',
    # setup_requires=['setuptools-git-version'],
    description='Fax to email gateway (Sendgrid/Twilio)',
    long_description='Some restructured text maybe',
    classifiers=[
        "Programming Language :: Python",
    ],
    author='Rick Copeland',
    author_email='rick@ehtcares.com',
    url='',
    keywords='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    tests_require=[],
    entry_points="""
    [console_scripts]
    f2e = f2e.commands:main
    safer-wkhtmltopdf = f2e.commands:safer.wkhtmltopdf
    safer-wkhtmltopdf-pack = f2e.commands:safer.wkhtmltopdf_pack

    [f2e.commands]
    shell = f2e.commands.shell:Shell
    serve = f2e.commands.serve:Serve
    """)
