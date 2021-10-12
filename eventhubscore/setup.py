from setuptools import setup

setup(
    name='cloud-radio',
    version="0.1",
    description='Cloud radio',
    long_description="",
    license='MIT',
    author='Microsoft Corporation',
    url='https://github.com/bquantump/hackathon2021',
    zip_safe=False,
    classifiers=["Programming Language :: Python :: 3"],
    install_requires=[
        'azure-eventhub==5.6.0',
        'azure.schemaregistry==1.0.0b2',
        'azure-schemaregistry-avroserializer==1.0.0b2',
        'azure-identity',
        'dataclasses-avroschema'
    ],
    include_package_data=True
)