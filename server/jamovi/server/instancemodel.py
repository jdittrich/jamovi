
from .analyses import Analyses

from ..core import MeasureType


class InstanceModel:

    N_VIRTUAL_COLS = 5
    N_VIRTUAL_ROWS = 50

    def __init__(self):
        self._dataset = None
        self._analyses = Analyses()
        self._path = ''
        self._title = ''

        self._columns = [ ]
        self._next_id = 0

        self._virtual_start = -1

    def __getitem__(self, index_or_name):
        if type(index_or_name) is int:
            index = index_or_name
            return self._columns[index]
        else:
            name = index_or_name
            for column in self:
                if column.name == name:
                    return column
            else:
                raise KeyError()

    def __iter__(self):
        return self._columns.__iter__()

    def get_column_by_id(self, id):
        for column in self:
            if column.id == id:
                return column
        else:
            raise KeyError()

    @property
    def virtual_start(self):
        return self._virtual_start

    def append_column(self, name, import_name=None):
        return self._dataset.append_column(name, import_name)

    def set_row_count(self, count):
        self._dataset.set_row_count(count)

    def append_row(self):
        self._dataset.append_row()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def analyses(self):
        return self._analyses

    @property
    def has_dataset(self):
        return self._dataset is not None

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, dataset):
        self._dataset = dataset

    def refresh(self):

        self._columns = [ ]

        index = 0
        for child in self._dataset:
            column = Column(self, child)
            column.id = index
            column.index = index
            self._columns.append(column)
            index += 1

        self._virtual_start = index
        self._add_virtual_columns()

    def _add_virtual_columns(self):
        n_virtual = len(self._columns) - self._virtual_start
        for i in range(n_virtual, InstanceModel.N_VIRTUAL_COLS):
            index = self._virtual_start + i
            column = Column(self)
            column.id = index
            column.index = index
            self._columns.append(column)
            index += 1

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    @property
    def virtual_row_count(self):
        return self._dataset.row_count + InstanceModel.N_VIRTUAL_ROWS

    @property
    def row_count(self):
        return self._dataset.row_count

    @property
    def column_count(self):
        return len(self._columns)

    @property
    def is_edited(self):
        return self._dataset.is_edited

    @is_edited.setter
    def is_edited(self, edited):
        self._dataset.is_edited = edited

    @property
    def is_blank(self):
        return self._dataset.is_blank

    @is_blank.setter
    def is_blank(self, blank):
        self._dataset.blank = blank

    def _gen_column_name(self, index):
        name = ''
        while True:
            i = index % 26
            name = chr(i + 65) + name
            index -= i
            index = int(index / 26)
            index -= 1
            if index < 0:
                break

        i = 2
        try_name = name
        while True:
            for column in self._dataset:
                if column.name == try_name:
                    break  # not unique
            else:
                name = try_name
                break  # unique
            try_name = name + ' (' + str(i) + ')'
            i += 1
        return name

    def _realise_column(self, column):
        index = column.index
        for i in range(self._virtual_start, index + 1):
            name = self._gen_column_name(i)
            child = self._dataset.append_column(name)
            wrapper = self[i]
            wrapper._child = child
            wrapper.auto_measure = True
        self._virtual_start = index + 1
        self._add_virtual_columns()


class Column:

    def __init__(self, parent, child=None):
        self._parent = parent
        self._child = child
        self._id = -1
        self._index = -1

    def _create_child(self):
        if self._child is None:
            self._parent._realise_column(self)

    def __setitem__(self, index, value):
        if self._child is None:
            self._create_child()
        self._child[index] = value

    def __getitem__(self, index):
        if self._child is not None:
            if index < self._child.row_count:
                return self._child[index]
            elif self._child.measure_type is MeasureType.NOMINAL_TEXT:
                return ''
            elif self._child.measure_type is MeasureType.CONTINUOUS:
                return float('nan')
            else:
                return -2147483648
        return -2147483648

    @property
    def is_virtual(self):
        return self._child is None

    def realise(self):
        self._create_child()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index

    @property
    def name(self):
        if self._child is not None:
            return self._child.name
        return ''

    @name.setter
    def name(self, name):
        if self._child is None:
            self._create_child()
        self._child.name = name

    @property
    def import_name(self):
        if self._child is not None:
            return self._child.import_name
        return ''

    @property
    def measure_type(self):
        if self._child is not None:
            return self._child.measure_type
        return MeasureType.NONE

    @measure_type.setter
    def measure_type(self, measure_type):
        if self._child is None:
            self._create_child()
        self._child.measure_type = measure_type

    @property
    def auto_measure(self):
        if self._child is not None:
            return self._child.auto_measure
        return True

    @auto_measure.setter
    def auto_measure(self, auto):
        if self._child is None:
            self._create_child()
        self._child.auto_measure = auto

    @property
    def dps(self):
        if self._child is not None:
            return self._child.dps
        return 0

    @dps.setter
    def dps(self, dps):
        if self._child is None:
            self._create_child()
        self._child.dps = dps

    def determine_dps(self):
        if self._child is not None:
            self._child.determine_dps()

    def append(self, value):
        if self._child is None:
            self._create_child()
        self._child.append(value)

    def insert_level(self, raw, label):
        if self._child is None:
            self._create_child()
        self._child.insert_level(raw, label)

    def get_value_for_label(self, label):
        if self._child is not None:
            return self._child.get_value_for_label(label)
        else:
            return -2147483648

    def clear_levels(self):
        if self._child is None:
            self._create_child()
        self._child.clear_levels()

    @property
    def has_levels(self):
        if self._child is not None:
            return self._child.has_levels
        return False

    @property
    def level_count(self):
        if self._child is not None:
            return self._child.level_count
        return 0

    def has_level(self, index_or_name):
        if self._child is not None:
            return self._child.has_level(index_or_name)
        return False

    @property
    def levels(self):
        if self._child is not None:
            return self._child.levels
        return []

    @property
    def row_count(self):
        if self._child is not None:
            return self._child.row_count
        return 0

    @property
    def changes(self):
        if self._child is not None:
            return self._child.changes
        return False

    def clear_at(self, index):
        if self._child is None:
            self._create_child()
        self._child.clear_at(index)

    def __iter__(self):
        if self._child is None:
            self._create_child()
        return self._child.__iter__()

    def raw(self, index):
        if self._child is not None:
            return self._child.raw(index)
        return -2147483648

    def change(self, measure_type, name=None, levels=None, dps=None, auto_measure=None):
        if self._child is None:
            self._create_child()
        self._child.change(measure_type, name, levels, dps, auto_measure)
