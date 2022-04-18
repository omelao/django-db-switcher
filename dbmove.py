from django.apps import apps
from django.contrib.auth.management import _get_all_permissions
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand
from django.db import models
from contextlib import contextmanager

imported = []
m2m_models = []

db_origin = 'default'
db_destination = 'postgresql'

def db_migrate(model):

    # identify fks
    for field in model._meta.get_fields():
        if isinstance(field, models.ForeignKey) or isinstance(field, models.ManyToManyField):
            import_name =  importname( field.related_model )
            if import_name not in imported:
                db_migrate( field.related_model )

        if hasattr( field, 'm2m_column_name' ):
            m2m_model = getattr( model, field.name ).through if hasattr(field, 'm2m_column_name') else None
            import_name =  importname( m2m_model )
            if import_name not in imported:
                m2m_models.append( m2m_model )

    # import root model after fks
    import_name = importname( model )
    print( "'" + import_name + "'," )

    if import_name not in imported:

        imported.append( import_name )

        if model.objects.using( db_destination ).exists():
             model.objects.using( db_destination ).all().delete()

        items = model.objects.using( db_origin ).all()
        auto_now = []

        for root_field in model._meta.get_fields():
            if hasattr(root_field, 'auto_now_add') and root_field.auto_now_add == True or hasattr(root_field, 'auto_now') and root_field.auto_now == True:
                auto_now.append( root_field.name )

        for i in range(0, len(items), 1000):
            chunk_items = items[i:i+1000]
            if len( auto_now ) > 0:
                with suppress_auto_now(model, auto_now ):
                    model.objects.using( db_destination ).bulk_create(chunk_items)
            else:
                model.objects.using( db_destination ).bulk_create(chunk_items)


@contextmanager
def suppress_auto_now(model, field_names):
    fields_state = {}
    for field_name in field_names:
        field = model._meta.get_field(field_name)
        fields_state[field] = {'auto_now': field.auto_now, 'auto_now_add': field.auto_now_add}

    for field in fields_state:
        field.auto_now = False
        field.auto_now_add = False
    try:
        yield
    finally:
        for field, state in fields_state.items():
            field.auto_now = state['auto_now']
            field.auto_now_add = state['auto_now_add']

def importname( model ):
    return model._meta.app_label + '.' + model._meta.object_name

class Command(BaseCommand):
    def handle(self, *args, **options):
        from django.db import connection
        from django.db import connections

        tables = connection.introspection.table_names()
        seen_models = connection.introspection.installed_models(tables)

        for model in seen_models:
            import_name =  importname( model )
            if import_name not in imported:
                db_migrate( model )

        for m2m_model in m2m_models:
            try:
                import_name =  importname( m2m_model )
                if import_name not in imported:
                    db_migrate( m2m_model )

            except:
                continue

        for table in tables:
            with connections[ db_destination ].cursor() as cursor:
                try:
                    cursor.execute( "select setval('" + table + "_id_seq', max(id)) from " + table )
                except:
                    continue

        print( 'Importados:', len(imported), imported )
