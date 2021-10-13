from setuptools import setup

setup(
    name='cloud-radio-dsp',
    version="0.1",
    description='Cloud radio DSP',
    long_description="",
    license='MIT',
    author='Microsoft Corporation',
    url='https://github.com/bquantump/hackathon2021',
    zip_safe=False,
    classifiers=["Programming Language :: Python :: 3"],
    install_requires=[
        'scikit-commpy',
        'scipy',
        'numpy',
    ],
    packages=['dspcore'],
    include_package_data=True
)