pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
gnome = import('gnome')

blueprint = find_program('blueprint-compiler')
blueprints = custom_target('blueprints',
  input: files(
    'about.blp',
  ),
  output: '.',
  command: [blueprint, 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('loro',
  'loro.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints,
)
