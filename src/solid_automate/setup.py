from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine-tuning.
build_options = {
    'packages': [

    ],
    'excludes': [
        'Dokumentacja'
    ],
    'zip_includes': [
    ],
    'no_compress': True
}

base = 'gui'

executables = [
    Executable('src/solid_automate/main.py', base=base,icon='assets/icon.ico')
]

setup(name='SolidAutomate',
      version='0.1',
      description='Automate for Solidworks',
      options={'build_exe': build_options},
      executables=executables)
