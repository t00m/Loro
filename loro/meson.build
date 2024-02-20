configure_file(
  input: 'loro.in',
  output: 'loro',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr--r--'
)

# Python sources
sources = [
  'main.py',
  'workflow.py',
  'dictionary.py'
]

install_data(sources, install_dir: moduledir)

# Subpackages
install_subdir('core', install_dir: moduledir)
install_subdir('extractors', install_dir: moduledir)
install_subdir('services', install_dir: moduledir)
install_subdir('builders', install_dir: moduledir)
