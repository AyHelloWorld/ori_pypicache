# ori_pypicache
A powerful PyPI-compatible Cache Server

Background: 
    PyPI - the Python Package Index ( https://pypi.python.org/pypi ), It is a repository of software for the Python programming language recommended by the Python community. All people can download third-party toolkit from it or upload their own libraries to PyPI.But for the reason of unstable network or some else, it’s hard to access to foreign websites, especially PyPI, at a slower speed, packet loss happen frequently, or perhaps not be accessible at all.
    To solve this problem, Setup a local self-updating pypi.python.org caching mirror is a good idea.

Program Details:
    A powerful PyPI-compatible Cache Server ( hereafter referred to as Pypicache), Pypicache aims to solve some problems developers and teams encounter when using python packages: 
    1. Many python package installation tools will check all associated links for a python project on PyPI, which can be problematic when the project’s server is down. Doubly so if the download link is on that server. 
    2. Commercial development of python projects might involve local patches to packages or completely private packages. It’s useful to host these internally. 
    3. Hosting an internal proxy can save quite a bit of bandwidth, which might be an issue for some teams.
    4. Installation of a larger project can be noticeably faster from an internal server. 
    5. Continuous integration tools can potentially install large sets of packages again and again, which can consume upstream bandwidth and slow down builds. 

Pypicache can be used in the following ways: 
    1. As a straight proxy to PyPI, caching package downloads wherever possible. 
    2. As a completely standalone PyPI server, useful for deploying from. 
    3. As an internal server for hosting custom packages. A possible day to day workflow could involve a pypicache server running on developer’s machines or in an office.

    Developers would install packages via this server. This server can also be shared by a deployment build tool which would install from the completely local copy of packages. This allows for repeatable builds.
