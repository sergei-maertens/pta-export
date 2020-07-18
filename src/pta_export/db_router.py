from typing import Optional

PTA_ALIAS = "ocpta"


class OCPTARouter:
    """
    Route OCPTA unmanaged models to the remote OCPTA database.
    """

    def db_for_read(self, model, **hints) -> str:
        if not model._meta.managed:
            return PTA_ALIAS
        return None

    def db_for_write(self, model, **hints) -> str:
        if not model._meta.managed:
            return PTA_ALIAS
        return None

    def allow_relation(self, obj1, obj2, **hints) -> bool:
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        return obj1._meta.managed == obj2._meta.managed

    def allow_migrate(self, db, app_label, model_name=None, **hints) -> Optional[bool]:
        """
        Make sure the auth and contenttypes apps only appear in the
        'auth_db' database.
        """
        if app_label == "core":
            return False
        return None
