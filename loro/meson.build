configure_file(
  input: 'loro.py',
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
install_subdir('backend', install_dir: moduledir)
install_subdir('frontend', install_dir: moduledir)
