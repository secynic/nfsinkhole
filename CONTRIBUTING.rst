============
Contributing
============

****************
Issue submission
****************

| Issues are tracked on GitHub:
| https://github.com/secynic/nfsinkhole/issues


Follow the guidelines detailed in the appropriate section below. As a general
rule of thumb, provide as much information as possible when submitting issues.

Bug reports
===========

- Title should be a short, descriptive summary of the bug
- Include the OS, Python, and nfsinkhole versions affected
- Provide a context (with code example) in the description of your issue. What
  are you attempting to do?
- Include the full obfuscated output. Make sure to set DEBUG logging:
  ::

    import logging
    LOG_FORMAT = ('[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] '
       '[%(funcName)s()] %(message)s')
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
- Include sources of information with links or screenshots
- Do you have a suggestion on how to fix the bug?

Feature Requests
================

- Title should be a short, descriptive summary of the feature requested
- Provide use case examples
- Include sources of information with links or screenshots
- Do you have a suggestion on how to implement the feature?

.. _contrib-testing:

Testing
=======

Testing code and infrastructure is in progress.

Questions
=========

I am happy to answer any questions and provide assistance where possible.
Please be clear and concise. Provide examples when possible. Check the
nfsinkhole `documentation <https://nfsinkhole.readthedocs.io/en/latest>`_ and the
`issue tracker <https://github.com/secynic/nfsinkhole/issues>`_ before asking a
question.

*************
Pull Requests
*************

What to include
===============

Aside from the core code changes, it is helpful to provide the following
(where applicable):

- Unit tests
- Examples
- Sphinx configuration changes in /docs
- Requirements (python2.6.txt, etc)

Guidelines
==========

- Title should be a short, descriptive summary of the changes
- Follow `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_ where possible.
- Follow the `Google docstring style guide
  <https://google.github.io/styleguide/pyguide.html#Comments>`_ for
  comments
- Must be compatible with Python 2.6, 2.7, and 3+
- Must not break OS compatibility for RHEL 6/7, CentOS 6/7
- Break out reusable code to functions
- Make your code easy to read and comment where necessary
- Reference the GitHub issue number in the description (e.g., Issue #01)
- When running nosetests, make sure to follow :ref:`contrib-testing`
