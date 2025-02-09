#  Copyright (C) 2022  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from enum import Enum
from typing import Dict, Type

from aas_editor.import_feature import import_util
from aas_editor.utils import util
from aas_editor.utils import util_classes
from aas_editor.utils import util_type

IMPORT_FILE = "Motor Daten aus EMSRDB.xlsx"


class PreObjectImport(util_classes.PreObject):
    EXAMPLE_ROW_VALUE = None

    def __init__(self, objType, args, kwargs: Dict[str, object]):
        super(PreObjectImport, self).__init__(objType, args, kwargs)
        self._fromPreObjs2KwargObjs()
        paramsToAttrs: Dict[str, str] = util_classes.ClassesInfo.params_to_attrs(objType)
        self.attrsToParams: Dict[str, str] = dict((v, k) for k, v in paramsToAttrs.items())

    @staticmethod
    def fromObject(obj, withIterParams=True):
        objType = type(obj)

        if isinstance(obj, PreObjectImport):
            return obj
        elif isinstance(obj, util_classes.PreObject):
            return PreObjectImport.fromPreObject(obj)

        if obj is None:
            return PreObjectImport.useExistingObject(obj)
        elif util_type.issubtype(objType, bool):
            return PreObjectImport(objType, (obj,), {})
        elif util_type.issubtype(objType, (str, int, float, bytes)):
            return PreObjectImport(objType, (str(obj),), {})
        elif util_type.issubtype(objType, Enum):
            return PreObjectImport(objType, (obj,), {})
        elif util_type.issubtype(objType, Type) or objType == type:
            return PreObjectImport.useExistingObject(obj)
        elif util_type.issubtype(objType, dict):
            listObj = []
            for item in obj:
                key = PreObjectImport.fromObject(item)
                value = PreObjectImport.fromObject(obj[item])
                listObj.append((key, value))
            return PreObjectImport(objType, (listObj,), {})
        elif util_type.isSimpleIterableType(objType):
            listObj = []
            for item in obj:
                item = PreObjectImport.fromObject(item)
                listObj.append(item)
            return PreObjectImport(objType, (listObj,), {})
        else:
            kwargs = {}
            params = list(util.getReqParams4init(objType, rmDefParams=False, delOptional=False).keys())
            iterParams = util_classes.ClassesInfo.iterAttrs(objType)
            [params.remove(i) for i in iterParams]
            paramsToAttrs = util_classes.ClassesInfo.params_to_attrs(objType)
            for param in params:
                attr = paramsToAttrs.get(param, param)
                val = getattr(obj, attr)
                val = PreObjectImport.fromObject(val)
                kwargs[param] = val
            if withIterParams:
                for iterParam in iterParams:
                    iterAttr = paramsToAttrs.get(iterParam, iterParam)
                    kwargs[iterParam] = getattr(obj, iterAttr)

            defaultParams2hide = dict(util_classes.ClassesInfo.default_params_to_hide(objType))
            kwargs.update(defaultParams2hide)
            return PreObjectImport(objType, [], kwargs)

    @staticmethod
    def fromPreObject(preObj: util_classes.PreObject):
        if preObj.existingObjUsed:
            return PreObjectImport.useExistingObject(preObj.existingObj)
        else:
            return PreObjectImport(preObj.objType, preObj.args, preObj.kwargs)

    def _fromPreObjs2KwargObjs(self):
        args = []
        for arg in self.args:
            if isinstance(arg, util_classes.PreObject):
                arg = PreObjectImport.fromPreObject(arg)
            elif arg and type(arg) in (list, tuple) and isinstance(arg[0], util_classes.PreObject):
                arg = [PreObjectImport.fromPreObject(i) for i in arg]
            args.append(arg)

        kwargs = {}
        for key in self.kwargs:
            value = self.kwargs[key]
            if isinstance(value, util_classes.PreObject):
                value = PreObjectImport.fromPreObject(value)
            if isinstance(key, util_classes.PreObject):
                key = PreObjectImport.fromPreObject(key)
            kwargs[key] = value

        self.args = args
        self.kwargs = kwargs

    def initWithImport(self, rowNum, sourceWB, sheetname, fromSavedExampleRow=False):
        funcKwargs = {
            "rowNum": rowNum,
            "sourceWB": sourceWB,
            "sheetname": sheetname,
            "fromSavedExampleRow": fromSavedExampleRow
        }
        if self.existingObjUsed:
            return PreObjectImport._initObjWithImport(self.existingObj, **funcKwargs)
        args = self._initWithImportArgs(**funcKwargs)
        kwargs = self._initWithImportKwargs(**funcKwargs)
        return self.objType(*args, **kwargs)

    @classmethod
    def _initObjWithImport(cls, obj, rowNum, sourceWB, sheetname, fromSavedExampleRow):
        if isinstance(obj, PreObjectImport):
            return obj.initWithImport(rowNum, sourceWB, sheetname, fromSavedExampleRow)
        elif isinstance(obj, str) and import_util.isValueToImport(obj):
            if fromSavedExampleRow:
                return import_util.importValueFromExampleRow(obj, row=PreObjectImport.EXAMPLE_ROW_VALUE)
            else:
                return import_util.importValueFromExcelWB(obj, workbook=sourceWB, row=rowNum, sheetname=sheetname)
        elif util_type.isSimpleIterable(obj):
            value = [PreObjectImport._initObjWithImport(i, rowNum, sourceWB, sheetname, fromSavedExampleRow) for i in obj]
            return value
        else:
            return obj

    def _initWithImportArgs(self, **funcKwargs):
        args = []
        if self.objType is dict:
            # args has following structure: ((key1,val1), (key2,val2) ...)
            for keyVal in self.args:
                if keyVal:
                    initKey = PreObjectImport._initObjWithImport(keyVal[0], **funcKwargs)
                    initVal = PreObjectImport._initObjWithImport(keyVal[1], **funcKwargs)
                    args.append((initKey, initVal))
        else:
            for val in self.args:
                initVal = PreObjectImport._initObjWithImport(val, **funcKwargs)
                args.append(initVal)
        return args

    def _initWithImportKwargs(self, **funcKwargs):
        kwargs = {}
        for key, val in self.kwargs.items():
            initVal = PreObjectImport._initObjWithImport(val, **funcKwargs)
            kwargs[key] = initVal
        return kwargs

    def initWithExampleRowImport(self):
        return self.initWithImport(rowNum=None, sourceWB=None, sheetname=None, fromSavedExampleRow=True)

    def __str__(self):
        if self.existingObjUsed:
            return str(self.existingObj)
        else:
            args = str(self.args).strip("[]")
            kwargs = ""
            for kwarg in self.kwargs:
                kwargs = f"{kwargs}, {kwarg}={self.kwargs[kwarg]}"
            if args and not kwargs:
                return f"{util_type.getTypeName(self.objType)}({args})"
            elif kwargs and not args:
                return f"{util_type.getTypeName(self.objType)}({kwargs})"
            else:
                return f"{util_type.getTypeName(self.objType)}({args}, {kwargs})"

    def __getattr__(self, item):
        param = self.attrsToParams.get(item, item)
        if param in self.kwargs:
            return self.kwargs[param]
        else:
            return object.__getattr__(util_classes.PreObject, item)

    def __iter__(self):
        if util_type.isIterableType(self.objType) and self.args:
            return iter(self.args[0])

    def items(self):
        if util_type.issubtype(self.objType, dict):
            return self.args
        else:
            raise AttributeError(f"{self.objType} has no attribute 'items'")

    def getMapping(self) -> Dict[str, str]:
        mapping = {}
        if self.existingObjUsed and isinstance(self.existingObj, str) and import_util.isValueToImport(self.existingObj):
            return str(self.existingObj)
        elif self.args:
            if len(self.args) > 1:
                raise NotImplementedError

            for i, value in enumerate(self.args):
                if isinstance(value, PreObjectImport):
                    return value.getMapping()
                elif isinstance(value, str) and import_util.isValueToImport(value):
                    return str(value)
                elif value and type(value) == list and isinstance(value[0], PreObjectImport):
                    for i, obj in enumerate(value):
                        mapping[i] = obj.getMapping()
        elif self.kwargs:
            for key, value in self.kwargs.items():
                if isinstance(value, PreObjectImport):
                    map = value.getMapping()
                    if map:
                        mapping[key] = map
                elif isinstance(value, str) and import_util.isValueToImport(value):
                    mapping[key] = str(value)
        return mapping

    def setMapping(self, mapping: Dict[str, str]):
        if mapping:
            if isinstance(mapping, dict):
                for attr in mapping:
                    if isinstance(attr, int) or (isinstance(attr, str) and attr.isdecimal()):
                        preObj = self.args[0][int(attr)]
                    else:
                        preObj = self.kwargs[attr]
                    preObj.setMapping(mapping[attr])
            else:
                self.args = [mapping]
