#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
    name='k8projectmanager',
    description='Behandlung von Kubernetes Projecten',
    long_description="""Dieses Program verwaltet Kubernetes Objecte. Funktionen:
    - Localisiert
    - Generirung und/oder von kompleten Kubernetes Projecten
    - Löschen von kompleten Kubernetes Projecten
    - Modular
    Existirenden Object Module:
    - Persistent Volume
    - Namespace
    - Claim
    - Secret für TLS
    - Deployment mit Template und Pods
    - Service
    - Ingress""",
    author='Juergen Ofner',
    author_email='xenon@ze.tum.de',
    version='0.46',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['k8projectgenerator=k8projectmanager.k8projectgenerator:start',
                            'k8projectdeleter=k8projectmanager.k8projectdeleter:start'],
    },
    platforms=["posix"],
    install_requires=['kubernetes>=10.0.0'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Natural Language :: German',
        'Operating System :: Unix',
        'Topic :: System :: Container'
    ]
)
