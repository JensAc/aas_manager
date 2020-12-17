from aas_editor.models import StandardItem
from aas_editor.settings.app_settings import PACKAGE_ROLE
from aas_editor.utils.util_type import isIterable
from aas_editor.package import Package


class PackTreeViewItem(StandardItem):
    def __init__(self, obj, parent, **kwargs):
        super().__init__(obj, parent=parent, **kwargs)
        if isinstance(obj, Package):
            self.typehint = Package
            self.package = obj
        else:
            self.package = parent.data(PACKAGE_ROLE)
        self.populate()

    def populate(self):
        kwargs = {
            "parent": self,
            "new": self.new,
        }
        if isinstance(self.obj, Package):
            for attr in Package.packViewAttrs():
                # set package objStore as obj, so that delete works
                packItem = PackTreeViewItem(getattr(self.obj, attr), name=attr, **kwargs)
                packItem.obj = self.obj.objStore
        elif isIterable(self.obj):
            self._populateIterable(self.obj, **kwargs)

    @staticmethod
    def _populateIterable(obj, **kwargs):
        for sub_item_obj in obj:
            PackTreeViewItem(sub_item_obj, **kwargs)
