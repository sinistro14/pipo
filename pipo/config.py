import os

from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    root_path=os.path.dirname(os.path.realpath(__file__)),
    envvar_prefix="PIPO",
    environments=True,
    validate_on_update=True,
    settings_files=["settings.yaml", ".secrets.yaml"],
    validators=[
        Validator("app", "channel", "voice_channel", "token", must_exist=True),
    ],
)

# `envvar_prefix` = export envvars with `export PIPO_FOO=bar`
# `settings_files` = load these files in the order

# lazy evaluation, check on usage only
settings.validators.register(
    validators=[
        Validator("app", "channel", "voice_channel", "token", neq=""),
    ],
)
