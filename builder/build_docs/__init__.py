
# Here is an example of how to use building of the documentation
# this uses sphinx to do the work. any of the sphinx packages
# that get used to build the documentation do not get installed into
# the users site-packages folder. They get placed in the same folder
# where this setup file resides. This is a nice feature because
# it doesn't install anything into the users python environment

import sys
import os
from build_framework import build_docs as _build_docs

from setup import (
    __VERSION__,
    __PACKAGE__,
    __AUTHOR__,
    __DESCRIPTION__
)


if 'build_docs' in sys.argv:
    setup_requires = [
        'Sphinx==1.8.0',
        'groundwork-sphinx-theme',
        'sphinx-sitemap>=1.0.2',
        'sphinxcontrib-blockdiag>=1.5.5',
        'sphinxcontrib-nwdiag>=0.9.5',
        'sphinxcontrib-actdiag>=0.8.5',
        'sphinxcontrib-seqdiag>=0.8.5',
        'sphinxcontrib-fulltoc>=1.2.0',
    ]

    dependency_links = [
        'https://github.com/kdschlosser/groundwork-sphinx-theme/tarball'
        '/sphinx_2.0_support#egg=groundwork_sphinx_theme'
    ]

else:
    setup_requires = []
    dependency_links = []


class build_docs(_build_docs.build_docs):

    def finalize_options(self):
        sphinx_conf = self.sphinx_conf = _build_docs.ConfigOptions()

        # -- GENERAL options ------------------------------------------------------
        sphinx_conf.suppress_warnings = ['image.nonlocal_uri']
        sphinx_conf.extensions = [
            'sphinx.ext.autodoc',
            'sphinx.ext.todo',
            'sphinx.ext.doctest',
            'sphinx.ext.viewcode',
            'sphinx.ext.autosummary',
            'sphinxcontrib.blockdiag',
            'sphinxcontrib.nwdiag',
            'sphinxcontrib.actdiag',
            'sphinxcontrib.seqdiag',
            'sphinxcontrib.fulltoc',
            'sphinx_sitemap',
            'sphinx.ext.graphviz',
            'sphinx.ext.inheritance_diagram'
        ]

        if sys.platform.startswith('win'):
            sphinx_conf.blockdiag_fontpath = os.path.join(
                os.path.expandvars('%WINDIR%'),
                'Fonts',
                'Arial.ttf'
            )
        else:
            sphinx_conf.blockdiag_fontpath = (
                '/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf'
            )
        sphinx_conf.templates_path = ['_templates']
        sphinx_conf.source_suffix = '.rst'
        sphinx_conf.master_doc = 'index'
        sphinx_conf.version = __VERSION__
        sphinx_conf.release = __VERSION__
        sphinx_conf.exclude_patterns = ['_build']
        sphinx_conf.add_function_parentheses = True
        sphinx_conf.show_authors = True
        sphinx_conf.pygments_style = 'sphinx'
        sphinx_conf.add_module_names = True

        # -- Options for HTML output ----------------------------------------------
        sphinx_conf.html_baseurl = '/docs/'
        sphinx_conf.html_theme = 'groundwork'
        sphinx_conf.html_theme_options = {
            "sidebar_width": '240px',
            "stickysidebar": True,
            "stickysidebarscrollable": True,
            "contribute": True,
            "github_fork": "pycurl/pycurl",
            "github_user": "pycurl",
        }
        sphinx_conf.html_theme_path = ["_themes"]
        sphinx_conf.html_title = __PACKAGE__
        sphinx_conf.html_logo = '_static/images/logo.png'
        sphinx_conf.html_static_path = ['_static']
        sphinx_conf.html_domain_indices = True
        sphinx_conf.html_use_index = True
        sphinx_conf.html_split_index = False
        sphinx_conf.html_show_sourcelink = True
        sphinx_conf.html_sourcelink_suffix = '.py'
        sphinx_conf.html_experimental_html5_writer = True
        sphinx_conf.html_show_sphinx = False
        sphinx_conf.html_copy_source = True
        sphinx_conf.html_show_copyright = True
        sphinx_conf.htmlhelp_basename = __PACKAGE__
        sphinx_conf.html_sidebars = {
            '**': [
                'globaltoc.html',
                'sourcelink.html',
                'searchbox.html'
            ],
            'using/windows': [
                'windowssidebar.html',
                'searchbox.html'
            ],
        }

        # -- Options for LATEX output ---------------------------------------------
        sphinx_conf.latex_elements = {}
        sphinx_conf.latex_documents = [
            ('index', __PACKAGE__ + '.tex', __PACKAGE__ + ' Documentation',
             __AUTHOR__, 'manual'),
        ]

        # -- Options for MAN PAGES output -----------------------------------------
        sphinx_conf.man_pages = [
            ('index', __PACKAGE__, __PACKAGE__ + ' Documentation',
             [__AUTHOR__], 1)
        ]

        # -- Options for TEXT INFO output -----------------------------------------
        sphinx_conf.texinfo_documents = [
            (
                'index',
                __PACKAGE__,
                __PACKAGE__ + ' Documentation',
                __AUTHOR__,
                __PACKAGE__,
                __DESCRIPTION__,
                'Miscellaneous'
            ),
        ]

        # sphinx_conf.additional_lines = sphinx_extra_lines
        if self.full_traceback is False:
            self.full_traceback = True

        _build_docs.build_docs.finalize_options(self)





