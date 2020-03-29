# -*- coding: utf-8 -*-

import setuptools
import os
import sys
import traceback
import imp


class build_docs(setuptools.Command):
    description = 'Build Documentation.'

    user_options = [
        (
            'builder-name=',
            'b',
            "compiler to use. Can be one of the following - html, dirhtml, "
            "singlehtml, htmlhelp, qthelp, devhelp, epub, applehelp, latex, "
            "man, texinfo, text, gettext, doctest, linkcheck, xml, pseudoxml\n"
            "the following builders are only available if make mode is being "
            "used - latexpdf, info\n default is html"
        ),
        (
            'make-mode',
            'M',
            "Uses the Sphinx make_mode module, which provides the same build "
            "functionality as a default Makefile or Make.bat. In addition to "
            "all Sphinx Builders, the following build pipelines are "
            "available: latexpdf, info"
        ),
        (
            'all-output',
            'a',
            "If given, always write all output files. The default is to only "
            "write output files for new and changed source files. (This may "
            "not apply to all builders."
        ),
        (
            'no-saved-environment',
            'E',
            "Don’t use a saved environment (the structure caching all "
            "cross-references), but rebuild it completely. The default is to "
            "only read and parse source files that are new or have changed "
            "since the last run."
        ),
        (
            'tag=',
            't',
            "Define the tag tag. This is relevant for only directives that "
            "only include their content if this tag is set."
        ),
        (
            'doctree-path=',
            'd',
            "Since Sphinx has to read and parse all source files before it "
            "can write an output file, the parsed source files are cached as "
            "'doctree pickles'. Normally, these files are put in a directory "
            "called .doctrees under the build directory; with this option you "
            "can select a different cache directory (the doctrees can be "
            "shared between all builders)."
        ),
        (
            'num-processes',
            'j',
            "Distribute the build over N processes in parallel, to make "
            "building on multiprocessor machines more effective. Note that "
            "not all parts and not all builders of Sphinx can be "
            "parallelized. If auto argument is given, Sphinx uses the number "
            "of CPU cores. default is auto"
        ),
        (
            'config-path=',
            'c',
            "Don’t look for the conf.py in the source directory, but use the "
            "given configuration directory instead. Note that various other "
            "files and paths given by configuration values are expected to be "
            "relative to the configuration directory, so they will have to be "
            "present at this location too."
        ),
        (
            'no-config',
            'C',
            "Don’t look for a configuration file; only take options via "
            "the -D option."
        ),
        (
            'nit-picky',
            'n',
            "Run in nit-picky mode. Currently, this generates warnings for "
            "all missing references. See the config value nitpick_ignore for "
            "a way to exclude some references as 'known missing'."
        ),
        (
            'no-color',
            'N',
            "Do not emit colored output."
        ),
        (
            'quiet',
            'q',
            "Do not output anything on standard output, only write warnings "
            "and errors to standard error."
        ),
        (
            'only-errors',
            'Q',
            "Do not output anything on standard output, also suppress "
            "warnings. Only errors are written to standard error."
        ),
        (
            'error-log=',
            'w',
            "Write warnings (and errors) to the given file, in addition to "
            "standard error."
        ),
        (
            'warnings-are-errors',
            'W',
            "Turn warnings into errors. This means that the build stops at "
            "the first warning and sphinx-build exits with exit status 1."
        ),
        (
            'keep-going',
            None,
            "With -W option, keep going processing when getting warnings to "
            "the end of build, and sphinx-build exits with exit status 1."
        ),
        (
            'full-traceback',
            'T',
            "Display the full traceback when an unhandled exception occurs. "
            "Otherwise, only a summary is displayed and the traceback "
            "information is saved to a file for further analysis."
        ),
        (
            'output-path=',
            None,
            'Output path. defaults to {source path}/_build'
        ),
        (
            'source-path=',
            None,
            'Path to the source files. defaults to {current path}/docs'
        ),
        (
            'config-overrides=',
            'D',
            'Override a configuration value set in the conf.py file.\n'
            'The value must be a number, string, list or dictionary value.\n'
            'We are not able to directly duplicate the command line syntax '
            'from Sphinx. There are some changes needed to be made in order '
            'to get this parameter to work properly.\n'
            'each entry will be setting=value separated by a semicolon\n'
            'setting=value;setting=value;setting=value\n'
            'For lists, html_theme_path=path1,path2.\n'
            'For dictionary values, supply the setting name and key like '
            'this: latex_elements.docclass=scrartcl.\n'
            'For boolean values, use 0 or 1 as the value.'
        ),
        (
            'html-values=',
            'A',
            'Make the name assigned to value in the HTML templates.\n'
            'We are not able to directly duplicate the command line syntax '
            'from Sphinx. There are some changes needed to be made in order '
            'to get this parameter to work properly.\n'
            'each entry will be setting=value separated by a semicolon\n'
            'setting=value;setting=value;setting=value\n'
        ),
        (
            'debug',
            None,
            'Debugging output'
        )
    ]

    boolean_options = [
        'dev',
        'full-traceback',
        'keep-going',
        'warnings-are-errors',
        'only-errors',
        'quiet',
        'no-color',
        'nit-picky',
        'no-config',
        'no-saved-environment',
        'all-output',
        'make-mode',
        'debug'
    ]

    sphinx_conf = None

    def initialize_options(self):
        self.html_values = ''
        self.config_overrides = ''
        self.source_path = '/docs'
        self.output_path = None
        self.full_traceback = False
        self.builder_name = 'html'
        self.make_mode = False
        self.all_output = False
        self.no_saved_environment = False
        self.tag = None
        self.doctree_path = None
        self.num_processes = 'auto'
        self.config_path = None
        self.no_config = False
        self.keep_going = False
        self.warnings_are_errors = False
        self.error_log = None
        self.only_errors = False
        self.quiet = False
        self.no_color = False
        self.nit_picky = False
        self.config_backup = None
        self.debug = False
        self.dev = False

    def finalize_options(self):
        flatten = lambda l: [item for sublist in l for item in sublist]

        if self.html_values:
            self.html_values = flatten(
                ['-A', item] for item in self.html_values.split(';')
            )
        else:
            self.html_values = []

        if self.config_overrides:
            self.config_overrides = flatten(
                ['-D', item] for item in self.config_overrides.split(';')
            )
        else:
            self.config_overrides = []

        if self.full_traceback:
            self.full_traceback = ['-T']
        else:
            self.full_traceback = []

        if self.make_mode:
            self.builder_name = ['-M', self.builder_name]

        else:
            self.builder_name = ['-b', self.builder_name]

        if self.all_output:
            self.all_output = ['-a']
        else:
            self.all_output = []

        if self.no_saved_environment:
            self.no_saved_environment = ['-E']
        else:
            self.no_saved_environment = []

        if self.tag is None:
            self.tag = []
        else:
            self.tag = ['-t', self.tag]

        if self.doctree_path is None:
            self.doctree_path = []
        else:
            self.doctree_path = ['-d', self.doctree_path]

        self.num_processes = ['-j', self.num_processes]

        if self.config_path is None:
            self.config_path = []
        else:
            self.config_path = ['-c', self.config_path]

        if self.no_config:
            self.no_config = ['-C']
        else:
            self.no_config = []

        if self.no_config:
            self.no_config = ['-C']
        else:
            self.no_config = []

        if self.keep_going:
            self.keep_going = ['--keep_going']
        else:
            self.keep_going = []

        if self.warnings_are_errors:
            self.warnings_are_errors = ['-W']
        else:
            self.warnings_are_errors = []

        if self.error_log is None:
            self.error_log = []
        else:
            self.error_log = ['-w', self.error_log]

        if self.only_errors:
            self.only_errors = ['-Q']
        else:
            self.only_errors = []

        if self.quiet:
            self.quiet = ['-q']
        else:
            self.quiet = []

        if self.no_color:
            self.no_color = ['-N']
        else:
            self.no_color = []

        if self.nit_picky:
            self.nit_picky = ['-n']
        else:
            self.nit_picky = []

        if self.distribution.verbose:
            self.verbose = ['-' + ('v' * self.distribution.verbose)]
        else:
            self.verbose = []

        if self.debug:
            self.verbose = ['-vvvv']

        if self.sphinx_conf is not None:
            if self.no_config:
                raise RuntimeError(
                    'Cannot have an options object and also '
                    'have no config specified'
                )

            if self.config_path:
                config_path = self.config_path[:-1]
            else:
                config_path = self.source_path

            if not config_path.endswith('conf.py'):
                config_path = os.path.join(config_path, 'conf.py')

            if os.path.exists(config_path + '.backup'):
                if os.path.exists(config_path):
                    os.remove(config_path)

                os.rename(config_path + '.backup', config_path)

            if os.path.exists(config_path):
                os.rename(config_path, config_path + '.backup')
                self.config_backup = config_path + '.backup'

            if self.sphinx_conf.project is None:
                self.sphinx_conf.project = self.distribution.get_name()

            if self.sphinx_conf.version is None:
                self.sphinx_conf.version = self.distribution.get_version()

            if self.sphinx_conf.author is None:
                self.sphinx_conf.author = self.distribution.get_author()

            if self.sphinx_conf.copyright is None:
                from time import strftime

                self.sphinx_conf.copyright = strftime(
                    '%Y ' + self.sphinx_conf.project
                )

            self.conf_path = config_path

        else:
            self.conf_path = None

        builder = self.distribution.get_command_obj('build')
        builder.dev = self.dev
        builder.ensure_finalized()

        self.build_lib = builder.build_lib

    def run(self):

        # *********************************************************************
        # This code block is to be able to build the documentation if
        # the module is installed into the python that is running the
        # setup program. What happens is for some reason both module.pyd
        # files try to load and this causes them to bump heads and the ugly
        # things start happening. so we want to make sure that we load the one
        # that was just compiled and also remove any module
        # references in sys.path. this ensures the proper one gets loaded

        build_ext = self.distribution.get_command_obj('build_ext')
        build_ext.ensure_finalized()
        extension = self.distribution.ext_modules[0]
        ext_path = build_ext.get_ext_fullpath(extension.name)

        mod = imp.load_dynamic(
            '',
            ext_path
        )

        sys.modules[''] = mod

        for path in sys.path[:]:
            if '' in path:
                sys.path.remove(path)

        sys.path.insert(0, os.path.abspath(self.build_lib))
        # *********************************************************************

        if self.sphinx_conf is not None:
            self.sphinx_conf.additional_lines = (
                'import sys\n'
                'sys.path.insert(0, r\'{path}\')\n\n'.format(
                    path=os.path.abspath(self.build_lib)
                )
            ) + self.sphinx_conf.additional_lines

            with open(self.conf_path, 'w') as f:
                f.write(str(self.sphinx_conf))

        try:
            if self.output_path is None:
                self.output_path = os.path.join(self.build_lib, 'docs')

            self.run_command('egg')

            sys.path.insert(0, os.path.abspath(self.build_lib))

            from sphinx.cmd.build import build_main

            options = (
                self.builder_name +
                self.html_values +
                self.config_overrides +
                self.full_traceback +
                self.all_output +
                self.no_saved_environment +
                self.tag +
                self.doctree_path +
                self.num_processes +
                self.config_path +
                self.no_config +
                self.keep_going +
                self.warnings_are_errors +
                self.error_log +
                self.only_errors +
                self.quiet +
                self.no_color +
                self.nit_picky +
                self.verbose +
                [self.source_path, self.output_path]
            )

            build_main(options)
        except:
            traceback.print_exc()
            sys.exit(1)

        if self.config_backup is not None:
            config_file = self.config_backup.replace('.backup', '')

            os.remove(config_file)
            os.rename(self.config_backup, config_file)


def create_property(func):
    func_name = func.__name__

    try:
        res = func(None)
    except:
        res = None

    doc = 'Default = ' + str(res)

    def fget(self):
        if func_name in self._config_options:
            return self._config_options[func_name]

        return func(self)

    def fset(self, value):
        self._config_options[func_name] = value

    def fdel(self):
        if func_name in self._config_options:
            del self._config_options[func_name]

    return property(fget=fget, fset=fset, fdel=fdel, doc=doc)


class ConfigOptions(object):

    def __init__(self):
        self._config_options = {}
        self._additional_lines = ''

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        if item in ConfigOptions.__dict__:
            prop = ConfigOptions.__dict__[item]
            return prop.fget(self)

        if item in self._config_options:
            return self._config_options[item]

        raise AttributeError(item)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            object.__setattr__(self, key, value)
            return

        if key in ConfigOptions.__dict__:
            prop = ConfigOptions.__dict__[key]
            prop.fset(self, value)
            return

        self._config_options[key] = value

    def __delattr__(self, item):
        if item in ConfigOptions.__dict__:
            prop = ConfigOptions.__dict__[item]
            prop.fdel(self)

        elif item in self._config_options:
            del self._config_options[item]

    @create_property
    def project(self):
        pass

    @create_property
    def author(self):
        pass

    @create_property
    def copyright(self):
        pass

    @create_property
    def version(self):
        pass

    @create_property
    def release(self):
        pass

    @create_property
    def extensions(self):
        pass

    @create_property
    def source_suffix(self):
        return {'.rst': 'restructuredtext'}

    @create_property
    def source_encoding(self):
        return 'utf-8-sig'

    @create_property
    def source_parsers(self):
        pass

    @create_property
    def master_doc(self):
        return 'index'

    @create_property
    def exclude_patterns(self):
        pass

    @create_property
    def templates_path(self):
        pass

    @create_property
    def template_bridge(self):
        pass

    @create_property
    def rst_epilog(self):
        pass

    @create_property
    def rst_prolog(self):
        pass

    @create_property
    def primary_domain(self):
        return 'py'

    @create_property
    def default_role(self):
        pass

    @create_property
    def keep_warnings(self):
        return False

    @create_property
    def suppress_warnings(self):
        pass

    @create_property
    def needs_sphinx(self):
        pass

    @create_property
    def needs_extensions(self):
        pass

    @create_property
    def manpages_url(self):
        pass

    @create_property
    def nitpicky(self):
        return False

    @create_property
    def nitpick_ignore(self):
        return ()

    @create_property
    def numfig(self):
        return False

    @create_property
    def numfig_format(self):
        return {
            'figure':     'Fig. %s',
            'table':      'Table %s',
            'code-block': 'Listing %s',
            'section':    'Section'
        }

    @create_property
    def numfig_secnum_depth(self):
        return 1

    @create_property
    def smartquotes(self):
        return True

    @create_property
    def smartquotes_action(self):
        return 'qDe'

    @create_property
    def smartquotes_excludes(self):
        return {'languages': ['ja'], 'builders': ['man', 'text']}

    @create_property
    def tls_verify(self):
        return True

    @create_property
    def tls_cacerts(self):
        pass

    @create_property
    def today(self):
        pass

    @create_property
    def today_fmt(self):
        pass

    @create_property
    def highlight_language(self):
        return 'default'

    @create_property
    def highlight_options(self):
        pass

    @create_property
    def pygments_style(self):
        pass

    @create_property
    def add_function_parentheses(self):
        return True

    @create_property
    def add_module_names(self):
        return True

    @create_property
    def show_authors(self):
        return False

    @create_property
    def modindex_common_prefix(self):
        return []

    @create_property
    def trim_footnote_reference_space(self):
        pass

    @create_property
    def trim_doctest_flags(self):
        return True

    @create_property
    def language(self):
        pass

    @create_property
    def locale_dirs(self):
        return ['locales']

    @create_property
    def gettext_compact(self):
        return False

    @create_property
    def gettext_uuid(self):
        return False

    @create_property
    def gettext_location(self):
        return True

    @create_property
    def gettext_auto_build(self):
        return True

    @create_property
    def gettext_additional_targets(self):
        return []

    @create_property
    def figure_language_filename(self):
        return '{root}.{language}{ext}'

    @create_property
    def math_number_all(self):
        return False

    @create_property
    def math_eqref_format(self):
        pass

    @create_property
    def math_numfig(self):
        return True

    @create_property
    def html_theme(self):
        return 'alabaster'

    @create_property
    def html_theme_options(self):
        pass

    @create_property
    def html_theme_path(self):
        pass

    @create_property
    def html_style(self):
        pass

    @create_property
    def html_title(self):
        return str(self.project) + ' v' + str(self.version) + 'documentation'

    @create_property
    def html_short_title(self):
        return self.html_title

    @create_property
    def html_baseurl(self):
        pass

    @create_property
    def html_context(self):
        pass

    @create_property
    def html_logo(self):
        pass

    @create_property
    def html_favicon(self):
        pass

    @create_property
    def html_css_files(self):
        return []

    @create_property
    def html_js_files(self):
        return []

    @create_property
    def html_static_path(self):
        pass

    @create_property
    def html_extra_path(self):
        pass

    @create_property
    def html_last_updated_fmt(self):
        pass

    @create_property
    def html_use_smartypants(self):
        return True

    @create_property
    def html_add_permalinks(self):
        return True

    @create_property
    def html_sidebars(self):
        pass

    @create_property
    def html_additional_pages(self):
        pass

    @create_property
    def html_domain_indices(self):
        return True

    @create_property
    def html_use_index(self):
        return True

    @create_property
    def html_split_index(self):
        return False

    @create_property
    def html_copy_source(self):
        return True

    @create_property
    def html_show_sourcelink(self):
        return True

    @create_property
    def html_sourcelink_suffix(self):
        return '.txt'

    @create_property
    def html_use_opensearch(self):
        return ''

    @create_property
    def html_file_suffix(self):
        return ".html"

    @create_property
    def html_link_suffix(self):
        return self.html_file_suffix

    @create_property
    def html_show_copyright(self):
        return True

    @create_property
    def html_show_sphinx(self):
        return True

    @create_property
    def html_output_encoding(self):
        return 'utf-8'

    @create_property
    def html_compact_lists(self):
        return True

    @create_property
    def html_secnumber_suffix(self):
        return ". "

    @create_property
    def html_search_language(self):
        lang = self.language
        if lang is None:
            lang = "en"
        return lang

    @create_property
    def html_search_options(self):
        pass

    @create_property
    def html_search_scorer(self):
        return ''

    @create_property
    def html_scaled_image_link(self):
        return True

    @create_property
    def html_math_renderer(self):
        return 'mathjax'

    @create_property
    def html_experimental_html5_writer(self):
        return False

    @create_property
    def html4_writer(self):
        return False

    @create_property
    def singlehtml_sidebars(self):
        return self.html_sidebars

    @create_property
    def htmlhelp_basename(self):
        return 'pydoc'

    @create_property
    def htmlhelp_file_suffix(self):
        return ".html"

    @create_property
    def htmlhelp_link_suffix(self):
        return ".html"

    @create_property
    def applehelp_bundle_name(self):
        return self.project

    @create_property
    def applehelp_bundle_id(self):
        pass

    @create_property
    def applehelp_dev_region(self):
        return 'en-us'

    @create_property
    def applehelp_bundle_version(self):
        return '1'

    @create_property
    def applehelp_icon(self):
        pass

    @create_property
    def applehelp_kb_product(self):
        return str(self.project) + '-' + str(self.release)

    @create_property
    def applehelp_kb_url(self):
        pass

    @create_property
    def applehelp_remote_url(self):
        pass

    @create_property
    def applehelp_index_anchors(self):
        pass

    @create_property
    def applehelp_min_term_length(self):
        pass

    @create_property
    def applehelp_stopwords(self):
        lang = self.language
        if lang is None:
            lang = "en"
        return lang

    @create_property
    def applehelp_locale(self):
        lang = self.language
        if lang is None:
            lang = "en"
        return lang

    @create_property
    def applehelp_title(self):
        return str(self.project) + ' Help'

    @create_property
    def applehelp_codesign_identity(self):
        pass

    @create_property
    def applehelp_codesign_flags(self):
        pass

    @create_property
    def applehelp_indexer_path(self):
        return '/usr/bin/hiutil'

    @create_property
    def applehelp_codesign_path(self):
        return '/usr/bin/codesign'

    @create_property
    def applehelp_disable_external_tools(self):
        return False

    @create_property
    def epub_basename(self):
        return self.project

    @create_property
    def epub_theme(self):
        return 'epub'

    @create_property
    def epub_theme_options(self):
        pass

    @create_property
    def epub_title(self):
        return self.project

    @create_property
    def epub_description(self):
        return 'unknown'

    @create_property
    def epub_author(self):
        return self.author

    @create_property
    def epub_contributor(self):
        return 'unknown'

    @create_property
    def epub_language(self):
        lang = self.language

        if lang is None:
            lang = "en"
        return lang

    @create_property
    def epub_publisher(self):
        return self.author

    @create_property
    def epub_copyright(self):
        return self.copyright

    @create_property
    def epub_identifier(self):
        return 'unknown'

    @create_property
    def epub_scheme(self):
        return 'unknown'

    @create_property
    def epub_uid(self):
        return 'unknown'

    @create_property
    def epub_cover(self):
        return ()

    @create_property
    def epub_css_files(self):
        pass

    @create_property
    def epub_guide(self):
        return ()

    @create_property
    def epub_pre_files(self):
        return []

    @create_property
    def epub_post_files(self):
        return []

    @create_property
    def epub_exclude_files(self):
        return []

    @create_property
    def epub_tocdepth(self):
        return 3

    @create_property
    def epub_tocdup(self):
        return True

    @create_property
    def epub_tocscope(self):
        return 'default'

    @create_property
    def epub_fix_images(self):
        return False

    @create_property
    def epub_max_image_width(self):
        return 0

    @create_property
    def epub_show_urls(self):
        return 'inline'

    @create_property
    def epub_use_index(self):
        return self.html_use_index

    @create_property
    def epub_writing_mode(self):
        return 'horizontal'

    @create_property
    def latex_engine(self):
        return 'pdflatex'

    @create_property
    def latex_documents(self):
        pass

    @create_property
    def latex_logo(self):
        pass

    @create_property
    def latex_toplevel_sectioning(self):
        pass

    @create_property
    def latex_appendices(self):
        pass

    @create_property
    def latex_domain_indices(self):
        return True

    @create_property
    def latex_show_pagerefs(self):
        return False

    @create_property
    def latex_show_urls(self):
        return 'no'

    @create_property
    def latex_use_latex_multicolumn(self):
        return False

    @create_property
    def latex_use_xindy(self):
        pass

    @create_property
    def latex_elements(self):
        pass

    @create_property
    def latex_docclass(self):
        return {'howto': 'article', 'manual': 'report'}

    @create_property
    def latex_additional_files(self):
        pass

    @create_property
    def text_newlines(self):
        return 'unix'

    @create_property
    def text_sectionchars(self):
        return '*=-~"+`'

    @create_property
    def text_add_secnumbers(self):
        return True

    @create_property
    def text_secnumber_suffix(self):
        return ". "

    @create_property
    def man_pages(self):
        pass

    @create_property
    def man_show_urls(self):
        return False

    @create_property
    def texinfo_documents(self):
        pass

    @create_property
    def texinfo_appendices(self):
        pass

    @create_property
    def texinfo_domain_indices(self):
        return True

    @create_property
    def texinfo_show_urls(self):
        return 'footnote'

    @create_property
    def texinfo_no_detailmenu(self):
        return False

    @create_property
    def texinfo_elements(self):
        pass

    @create_property
    def qthelp_basename(self):
        return self.project

    @create_property
    def qthelp_namespace(self):
        return 'org.sphinx.' + str(self.project) + '.' + str(self.version)

    @create_property
    def qthelp_theme(self):
        return 'nonav'

    @create_property
    def qthelp_theme_options(self):
        pass

    @create_property
    def linkcheck_ignore(self):
        pass

    @create_property
    def linkcheck_retries(self):
        return 1

    @create_property
    def linkcheck_timeout(self):
        pass

    @create_property
    def linkcheck_workers(self):
        return 5

    @create_property
    def linkcheck_anchors(self):
        return True

    @create_property
    def linkcheck_anchors_ignore(self):
        return ["^!"]

    @create_property
    def xml_pretty(self):
        return True

    @create_property
    def Footnotes(self):
        pass

    @create_property
    def cpp_index_common_prefix(self):
        pass

    @create_property
    def cpp_id_attributes(self):
        pass

    @create_property
    def cpp_paren_attributes(self):
        pass

    @property
    def additional_lines(self):
        return self._additional_lines

    @additional_lines.setter
    def additional_lines(self, lines):
        self._additional_lines = lines

    def __str__(self):
        output = ''
        for key, value in self._config_options.items():
            output += key + ' = ' + repr(value) + '\n'

        output += '\n'
        if self._additional_lines:
            output += '\n' + self._additional_lines

        return '# -*- coding: utf-8 -*-\n\n' + output + '\n'
