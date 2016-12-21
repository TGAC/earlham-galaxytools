import logging

from galaxy.datatypes.binary import Binary, SQlite
from galaxy.datatypes.metadata import MetadataElement, MetadataParameter
from galaxy.util import sqlite

log = logging.getLogger(__name__)


class GAFASQLite(SQlite):
    """Class describing a GAFA SQLite database"""
    MetadataElement(name='gafa_schema_version', default='0.1.0', param=MetadataParameter, desc='GAFA schema version',
                    readonly=True, visible=True, no_value='0.1.0')
    file_ext = 'gafa.sqlite'

    def set_meta(self, dataset, overwrite=True, **kwd):
        super(GAFASQLite, self).set_meta(dataset, overwrite=overwrite, **kwd)
        try:
            conn = sqlite.connect(dataset.file_name)
            c = conn.cursor()
            version_query = 'SELECT version FROM meta'
            results = c.execute(version_query).fetchall()
            if len(results) == 0:
                raise Exception('version not found in meta table')
            elif len(results) > 1:
                raise Exception('Multiple versions found in meta table')
            dataset.metadata.gafa_schema_version = results[0][0]
        except Exception as e:
            log.warn("%s, set_meta Exception: %s", self, e)

    def sniff(self, filename):
        if super(GAFASQLite, self).sniff(filename):
            gafa_table_names = frozenset(['gene', 'gene_family', 'gene_family_member', 'meta', 'transcript'])
            conn = sqlite.connect(filename)
            c = conn.cursor()
            tables_query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            results = c.execute(tables_query).fetchall()
            found_table_names = frozenset(_[0] for _ in results)
            return gafa_table_names <= found_table_names
        return False


# Since Binary.register_sniffable_binary_format() ignores the sniff order declared in datatypes_conf.xml and put TS datatypes at the end, instead of simply doing:
# Binary.register_sniffable_binary_format("sqlite", "sqlite", SQlite)
# we need to register specialized SQLite datatypes before SQlite
for i, format_dict in enumerate(Binary.sniffable_binary_formats):
    if format_dict['class'] == SQlite:
        break
else:
    i += 1
Binary.sniffable_binary_formats.insert(i, {'type': 'gafa.sqlite', 'ext': 'gafa.sqlite', 'class': GAFASQLite})
