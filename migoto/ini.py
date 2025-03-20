"""Generates an ini file from a template file using Jinja2."""
import os
import addon_utils
from .. import bl_info
class Fatal(Exception): pass
try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    def generate_ini(character_name:str, char_hash: dict, offsets: list, texture_hashes_written: dict,
                    credit: str, game, operator, user_paths: list[str] = None, template_name: str|None  = "default.ini"):
        return False
else:
    def generate_ini(character_name:str, char_hash: dict, offsets: list, texture_hashes_written: dict, credit: str,
                    game, operator, user_paths: list[str] = None, template_name: str|None = "default.ini"):
        """Generates an ini file from a template file using Jinja2.
        Trailing spaces are removed from the template file."""

        if template_name is None or template_name == "":
            template_name = "default.ini"
        addon_path = None
        for mod in addon_utils.modules():
            if mod.bl_info['name'] == 'XXMI_Tools':
                addon_path = os.path.dirname(mod.__file__)
                break
        templates_paths = [os.path.join(addon_path, "templates")]
        if user_paths:
            # prefer user paths to overwrite original inis
            user_paths.extend(templates_paths)
            templates_paths = user_paths
        env = Environment(loader=FileSystemLoader(searchpath=templates_paths),
                        trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(template_name)

        return template.render(
            version=bl_info['version'],
            char_hash=char_hash,
            offsets=offsets,
            texture_hashes_written=texture_hashes_written,
            credit=credit,
            game=game,
            character_name=character_name,
            operator=operator
            )
