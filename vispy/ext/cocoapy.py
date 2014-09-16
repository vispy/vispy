# -*- coding: utf-8 -*-

from ctypes import (cdll, util, Structure, cast, byref, POINTER, CFUNCTYPE,
                    c_int, c_long, c_ulong, c_ushort, c_wchar, c_uint32,
                    c_double, c_uint, c_float, c_void_p, c_char_p, c_bool,
                    c_buffer, c_ubyte, c_byte, c_int8, c_int16, c_int32,
                    c_int64, c_short, c_longlong, c_size_t, sizeof,
                    c_uint8, c_longdouble, c_char, c_ulonglong, py_object,
                    alignment, ArgumentError)

import platform
import struct
import sys

if sys.version_info[0] >= 3:
    string_types = str,
else:
    string_types = basestring,  # noqa

# Based on Pyglet code

##############################################################################
# cocoatypes.py

__LP64__ = (8 * struct.calcsize("P") == 64)
__i386__ = (platform.machine() == 'i386')

PyObjectEncoding = b'{PyObject=@}'


def encoding_for_ctype(vartype):
    typecodes = {c_char: b'c', c_int: b'i', c_short: b's', c_long: b'l',
                 c_longlong: b'q', c_ubyte: b'C', c_uint: b'I', c_ushort: b'S',
                 c_ulong: b'L', c_ulonglong: b'Q', c_float: b'f',
                 c_double: b'd', c_bool: b'B', c_char_p: b'*', c_void_p: b'@',
                 py_object: PyObjectEncoding}
    return typecodes.get(vartype, b'?')

if __LP64__:
    NSInteger = c_long
    NSUInteger = c_ulong
    CGFloat = c_double
    NSPointEncoding = b'{CGPoint=dd}'
    NSSizeEncoding = b'{CGSize=dd}'
    NSRectEncoding = b'{CGRect={CGPoint=dd}{CGSize=dd}}'
    NSRangeEncoding = b'{_NSRange=QQ}'
else:
    NSInteger = c_int
    NSUInteger = c_uint
    CGFloat = c_float
    NSPointEncoding = b'{_NSPoint=ff}'
    NSSizeEncoding = b'{_NSSize=ff}'
    NSRectEncoding = b'{_NSRect={_NSPoint=ff}{_NSSize=ff}}'
    NSRangeEncoding = b'{_NSRange=II}'

NSIntegerEncoding = encoding_for_ctype(NSInteger)
NSUIntegerEncoding = encoding_for_ctype(NSUInteger)
CGFloatEncoding = encoding_for_ctype(CGFloat)

CGImageEncoding = b'{CGImage=}'
NSZoneEncoding = b'{_NSZone=}'


class NSPoint(Structure):
    _fields_ = [("x", CGFloat), ("y", CGFloat)]
CGPoint = NSPoint


class NSSize(Structure):
    _fields_ = [("width", CGFloat), ("height", CGFloat)]
CGSize = NSSize


class NSRect(Structure):
    _fields_ = [("origin", NSPoint), ("size", NSSize)]
CGRect = NSRect


NSTimeInterval = c_double
CFIndex = c_long
UniChar = c_ushort
unichar = c_wchar
CGGlyph = c_ushort


class CFRange(Structure):
    _fields_ = [("location", CFIndex), ("length", CFIndex)]


class NSRange(Structure):
    _fields_ = [("location", NSUInteger), ("length", NSUInteger)]


CFTypeID = c_ulong
CFNumberType = c_uint32


##############################################################################
# runtime.py

__LP64__ = (8*struct.calcsize("P") == 64)
__i386__ = (platform.machine() == 'i386')

if sizeof(c_void_p) == 4:
    c_ptrdiff_t = c_int32
elif sizeof(c_void_p) == 8:
    c_ptrdiff_t = c_int64

objc = cdll.LoadLibrary(util.find_library('objc'))

objc.class_addIvar.restype = c_bool
objc.class_addIvar.argtypes = [c_void_p, c_char_p, c_size_t, c_uint8, c_char_p]

objc.class_addMethod.restype = c_bool

objc.class_addProtocol.restype = c_bool
objc.class_addProtocol.argtypes = [c_void_p, c_void_p]

objc.class_conformsToProtocol.restype = c_bool
objc.class_conformsToProtocol.argtypes = [c_void_p, c_void_p]

objc.class_copyIvarList.restype = POINTER(c_void_p)
objc.class_copyIvarList.argtypes = [c_void_p, POINTER(c_uint)]

objc.class_copyMethodList.restype = POINTER(c_void_p)
objc.class_copyMethodList.argtypes = [c_void_p, POINTER(c_uint)]

objc.class_copyPropertyList.restype = POINTER(c_void_p)
objc.class_copyPropertyList.argtypes = [c_void_p, POINTER(c_uint)]

objc.class_copyProtocolList.restype = POINTER(c_void_p)
objc.class_copyProtocolList.argtypes = [c_void_p, POINTER(c_uint)]

objc.class_createInstance.restype = c_void_p
objc.class_createInstance.argtypes = [c_void_p, c_size_t]

objc.class_getClassMethod.restype = c_void_p
objc.class_getClassMethod.argtypes = [c_void_p, c_void_p]

objc.class_getClassVariable.restype = c_void_p
objc.class_getClassVariable.argtypes = [c_void_p, c_char_p]

objc.class_getInstanceMethod.restype = c_void_p
objc.class_getInstanceMethod.argtypes = [c_void_p, c_void_p]

objc.class_getInstanceSize.restype = c_size_t
objc.class_getInstanceSize.argtypes = [c_void_p]

objc.class_getInstanceVariable.restype = c_void_p
objc.class_getInstanceVariable.argtypes = [c_void_p, c_char_p]

objc.class_getIvarLayout.restype = c_char_p
objc.class_getIvarLayout.argtypes = [c_void_p]

objc.class_getMethodImplementation.restype = c_void_p
objc.class_getMethodImplementation.argtypes = [c_void_p, c_void_p]

objc.class_getMethodImplementation_stret.restype = c_void_p
objc.class_getMethodImplementation_stret.argtypes = [c_void_p, c_void_p]

objc.class_getName.restype = c_char_p
objc.class_getName.argtypes = [c_void_p]

objc.class_getProperty.restype = c_void_p
objc.class_getProperty.argtypes = [c_void_p, c_char_p]

objc.class_getSuperclass.restype = c_void_p
objc.class_getSuperclass.argtypes = [c_void_p]

objc.class_getVersion.restype = c_int
objc.class_getVersion.argtypes = [c_void_p]

objc.class_getWeakIvarLayout.restype = c_char_p
objc.class_getWeakIvarLayout.argtypes = [c_void_p]

objc.class_isMetaClass.restype = c_bool
objc.class_isMetaClass.argtypes = [c_void_p]

objc.class_replaceMethod.restype = c_void_p
objc.class_replaceMethod.argtypes = [c_void_p, c_void_p, c_void_p, c_char_p]

objc.class_respondsToSelector.restype = c_bool
objc.class_respondsToSelector.argtypes = [c_void_p, c_void_p]

objc.class_setIvarLayout.restype = None
objc.class_setIvarLayout.argtypes = [c_void_p, c_char_p]

objc.class_setSuperclass.restype = c_void_p
objc.class_setSuperclass.argtypes = [c_void_p, c_void_p]

objc.class_setVersion.restype = None
objc.class_setVersion.argtypes = [c_void_p, c_int]

objc.class_setWeakIvarLayout.restype = None
objc.class_setWeakIvarLayout.argtypes = [c_void_p, c_char_p]

objc.ivar_getName.restype = c_char_p
objc.ivar_getName.argtypes = [c_void_p]

objc.ivar_getOffset.restype = c_ptrdiff_t
objc.ivar_getOffset.argtypes = [c_void_p]

objc.ivar_getTypeEncoding.restype = c_char_p
objc.ivar_getTypeEncoding.argtypes = [c_void_p]

objc.method_copyArgumentType.restype = c_char_p
objc.method_copyArgumentType.argtypes = [c_void_p, c_uint]

objc.method_copyReturnType.restype = c_char_p
objc.method_copyReturnType.argtypes = [c_void_p]

objc.method_exchangeImplementations.restype = None
objc.method_exchangeImplementations.argtypes = [c_void_p, c_void_p]

objc.method_getArgumentType.restype = None
objc.method_getArgumentType.argtypes = [c_void_p, c_uint, c_char_p, c_size_t]

objc.method_getImplementation.restype = c_void_p
objc.method_getImplementation.argtypes = [c_void_p]

objc.method_getName.restype = c_void_p
objc.method_getName.argtypes = [c_void_p]

objc.method_getNumberOfArguments.restype = c_uint
objc.method_getNumberOfArguments.argtypes = [c_void_p]

objc.method_getReturnType.restype = None
objc.method_getReturnType.argtypes = [c_void_p, c_char_p, c_size_t]

objc.method_getTypeEncoding.restype = c_char_p
objc.method_getTypeEncoding.argtypes = [c_void_p]

objc.method_setImplementation.restype = c_void_p
objc.method_setImplementation.argtypes = [c_void_p, c_void_p]

objc.objc_allocateClassPair.restype = c_void_p
objc.objc_allocateClassPair.argtypes = [c_void_p, c_char_p, c_size_t]

objc.objc_copyProtocolList.restype = POINTER(c_void_p)
objc.objc_copyProtocolList.argtypes = [POINTER(c_int)]

objc.objc_getAssociatedObject.restype = c_void_p
objc.objc_getAssociatedObject.argtypes = [c_void_p, c_void_p]

objc.objc_getClass.restype = c_void_p
objc.objc_getClass.argtypes = [c_char_p]

objc.objc_getClassList.restype = c_int
objc.objc_getClassList.argtypes = [c_void_p, c_int]

objc.objc_getMetaClass.restype = c_void_p
objc.objc_getMetaClass.argtypes = [c_char_p]

objc.objc_getProtocol.restype = c_void_p
objc.objc_getProtocol.argtypes = [c_char_p]

objc.objc_msgSendSuper_stret.restype = None

objc.objc_msgSend_stret.restype = None

objc.objc_registerClassPair.restype = None
objc.objc_registerClassPair.argtypes = [c_void_p]

objc.objc_removeAssociatedObjects.restype = None
objc.objc_removeAssociatedObjects.argtypes = [c_void_p]

objc.objc_setAssociatedObject.restype = None
objc.objc_setAssociatedObject.argtypes = [c_void_p, c_void_p, c_void_p, c_int]

objc.object_copy.restype = c_void_p
objc.object_copy.argtypes = [c_void_p, c_size_t]

objc.object_dispose.restype = c_void_p
objc.object_dispose.argtypes = [c_void_p]

objc.object_getClass.restype = c_void_p
objc.object_getClass.argtypes = [c_void_p]

objc.object_getClassName.restype = c_char_p
objc.object_getClassName.argtypes = [c_void_p]

objc.object_getInstanceVariable.restype = c_void_p
objc.object_getInstanceVariable.argtypes = [c_void_p, c_char_p, c_void_p]

objc.object_getIvar.restype = c_void_p
objc.object_getIvar.argtypes = [c_void_p, c_void_p]

objc.object_setClass.restype = c_void_p
objc.object_setClass.argtypes = [c_void_p, c_void_p]

objc.object_setInstanceVariable.restype = c_void_p

objc.object_setIvar.restype = None
objc.object_setIvar.argtypes = [c_void_p, c_void_p, c_void_p]

objc.property_getAttributes.restype = c_char_p
objc.property_getAttributes.argtypes = [c_void_p]

objc.property_getName.restype = c_char_p
objc.property_getName.argtypes = [c_void_p]

objc.protocol_conformsToProtocol.restype = c_bool
objc.protocol_conformsToProtocol.argtypes = [c_void_p, c_void_p]


class OBJC_METHOD_DESCRIPTION(Structure):
    _fields_ = [("name", c_void_p), ("types", c_char_p)]


objc.protocol_copyMethodDescriptionList.restype = \
    POINTER(OBJC_METHOD_DESCRIPTION)
objc.protocol_copyMethodDescriptionList.argtypes = [c_void_p, c_bool,
                                                    c_bool, POINTER(c_uint)]

objc.protocol_copyPropertyList.restype = c_void_p
objc.protocol_copyPropertyList.argtypes = [c_void_p, POINTER(c_uint)]

objc.protocol_copyProtocolList = POINTER(c_void_p)
objc.protocol_copyProtocolList.argtypes = [c_void_p, POINTER(c_uint)]

objc.protocol_getMethodDescription.restype = OBJC_METHOD_DESCRIPTION
objc.protocol_getMethodDescription.argtypes = [c_void_p, c_void_p,
                                               c_bool, c_bool]

objc.protocol_getName.restype = c_char_p
objc.protocol_getName.argtypes = [c_void_p]

objc.sel_getName.restype = c_char_p
objc.sel_getName.argtypes = [c_void_p]

objc.sel_isEqual.restype = c_bool
objc.sel_isEqual.argtypes = [c_void_p, c_void_p]

objc.sel_registerName.restype = c_void_p
objc.sel_registerName.argtypes = [c_char_p]


def ensure_bytes(x):
    if isinstance(x, bytes):
        return x
    return x.encode('ascii')


def get_selector(name):
    return c_void_p(objc.sel_registerName(ensure_bytes(name)))


def get_class(name):
    return c_void_p(objc.objc_getClass(ensure_bytes(name)))


def get_object_class(obj):
    return c_void_p(objc.object_getClass(obj))


def get_metaclass(name):
    return c_void_p(objc.objc_getMetaClass(ensure_bytes(name)))


def get_superclass_of_object(obj):
    cls = c_void_p(objc.object_getClass(obj))
    return c_void_p(objc.class_getSuperclass(cls))


def x86_should_use_stret(restype):
    if type(restype) != type(Structure):
        return False
    if not __LP64__ and sizeof(restype) <= 8:
        return False
    if __LP64__ and sizeof(restype) <= 16:  # maybe? I don't know?
        return False
    return True


def should_use_fpret(restype):
    if not __i386__:
        return False
    if __LP64__ and restype == c_longdouble:
        return True
    if not __LP64__ and restype in (c_float, c_double, c_longdouble):
        return True
    return False


def send_message(receiver, selName, *args, **kwargs):
    if isinstance(receiver, string_types):
        receiver = get_class(receiver)
    selector = get_selector(selName)
    restype = kwargs.get('restype', c_void_p)
    argtypes = kwargs.get('argtypes', [])
    if should_use_fpret(restype):
        objc.objc_msgSend_fpret.restype = restype
        objc.objc_msgSend_fpret.argtypes = [c_void_p, c_void_p] + argtypes
        result = objc.objc_msgSend_fpret(receiver, selector, *args)
    elif x86_should_use_stret(restype):
        objc.objc_msgSend_stret.argtypes = [POINTER(restype), c_void_p,
                                            c_void_p] + argtypes
        result = restype()
        objc.objc_msgSend_stret(byref(result), receiver, selector, *args)
    else:
        objc.objc_msgSend.restype = restype
        objc.objc_msgSend.argtypes = [c_void_p, c_void_p] + argtypes
        result = objc.objc_msgSend(receiver, selector, *args)
        if restype == c_void_p:
            result = c_void_p(result)
    return result


class OBJC_SUPER(Structure):
    _fields_ = [('receiver', c_void_p), ('class', c_void_p)]

OBJC_SUPER_PTR = POINTER(OBJC_SUPER)


def send_super(receiver, selName, *args, **kwargs):
    if hasattr(receiver, '_as_parameter_'):
        receiver = receiver._as_parameter_
    superclass = get_superclass_of_object(receiver)
    super_struct = OBJC_SUPER(receiver, superclass)
    selector = get_selector(selName)
    restype = kwargs.get('restype', c_void_p)
    argtypes = kwargs.get('argtypes', None)
    objc.objc_msgSendSuper.restype = restype
    if argtypes:
        objc.objc_msgSendSuper.argtypes = [OBJC_SUPER_PTR, c_void_p] + argtypes
    else:
        objc.objc_msgSendSuper.argtypes = None
    result = objc.objc_msgSendSuper(byref(super_struct), selector, *args)
    if restype == c_void_p:
        result = c_void_p(result)
    return result


cfunctype_table = {}


def parse_type_encoding(encoding):
    type_encodings = []
    brace_count = 0    # number of unclosed curly braces
    bracket_count = 0  # number of unclosed square brackets
    typecode = b''
    for c in encoding:
        if isinstance(c, int):
            c = bytes([c])

        if c == b'{':
            if typecode and typecode[-1:] != b'^' and brace_count == 0 and \
                    bracket_count == 0:
                type_encodings.append(typecode)
                typecode = b''
            typecode += c
            brace_count += 1
        elif c == b'}':
            typecode += c
            brace_count -= 1
            assert(brace_count >= 0)
        elif c == b'[':
            if typecode and typecode[-1:] != b'^' and brace_count == 0 and \
                    bracket_count == 0:
                type_encodings.append(typecode)
                typecode = b''
            typecode += c
            bracket_count += 1
        elif c == b']':
            typecode += c
            bracket_count -= 1
            assert(bracket_count >= 0)
        elif brace_count or bracket_count:
            typecode += c
        elif c in b'0123456789':
            pass
        elif c in b'rnNoORV':
            pass
        elif c in b'^cislqCISLQfdBv*@#:b?':
            if typecode and typecode[-1:] == b'^':
                typecode += c
            else:
                if typecode:
                    type_encodings.append(typecode)
                typecode = c

    if typecode:
        type_encodings.append(typecode)

    return type_encodings


def cfunctype_for_encoding(encoding):
    if encoding in cfunctype_table:
        return cfunctype_table[encoding]
    typecodes = {b'c': c_char, b'i': c_int, b's': c_short, b'l': c_long,
                 b'q': c_longlong, b'C': c_ubyte, b'I': c_uint, b'S': c_ushort,
                 b'L': c_ulong, b'Q': c_ulonglong, b'f': c_float,
                 b'd': c_double, b'B': c_bool, b'v': None, b'*': c_char_p,
                 b'@': c_void_p, b'#': c_void_p, b':': c_void_p,
                 NSPointEncoding: NSPoint, NSSizeEncoding: NSSize,
                 NSRectEncoding: NSRect, NSRangeEncoding: NSRange,
                 PyObjectEncoding: py_object}
    argtypes = []
    for code in parse_type_encoding(encoding):
        if code in typecodes:
            argtypes.append(typecodes[code])
        elif code[0:1] == b'^' and code[1:] in typecodes:
            argtypes.append(POINTER(typecodes[code[1:]]))
        else:
            raise Exception('unknown type encoding: ' + code)

    cfunctype = CFUNCTYPE(*argtypes)
    cfunctype_table[encoding] = cfunctype
    return cfunctype


def create_subclass(superclass, name):
    if isinstance(superclass, string_types):
        superclass = get_class(superclass)
    return c_void_p(objc.objc_allocateClassPair(superclass,
                                                ensure_bytes(name), 0))


def register_subclass(subclass):
    objc.objc_registerClassPair(subclass)


def add_method(cls, selName, method, types):
    type_encodings = parse_type_encoding(types)
    assert(type_encodings[1] == b'@')  # ensure id self typecode
    assert(type_encodings[2] == b':')  # ensure SEL cmd typecode
    selector = get_selector(selName)
    cfunctype = cfunctype_for_encoding(types)
    imp = cfunctype(method)
    objc.class_addMethod.argtypes = [c_void_p, c_void_p, cfunctype, c_char_p]
    objc.class_addMethod(cls, selector, imp, types)
    return imp


def add_ivar(cls, name, vartype):
    return objc.class_addIvar(cls, ensure_bytes(name), sizeof(vartype),
                              alignment(vartype), encoding_for_ctype(vartype))


def set_instance_variable(obj, varname, value, vartype):
    objc.object_setInstanceVariable.argtypes = [c_void_p, c_char_p, vartype]
    objc.object_setInstanceVariable(obj, ensure_bytes(varname), value)


def get_instance_variable(obj, varname, vartype):
    variable = vartype()
    objc.object_getInstanceVariable(obj, ensure_bytes(varname),
                                    byref(variable))
    return variable.value


class ObjCMethod(object):
    """This represents an unbound Objective-C method (really an IMP)."""
    typecodes = {b'c': c_byte, b'i': c_int, b's': c_short, b'l': c_long,
                 b'q': c_longlong, b'C': c_ubyte, b'I': c_uint, b'S': c_ushort,
                 b'L': c_ulong, b'Q': c_ulonglong, b'f': c_float,
                 b'd': c_double, b'B': c_bool, b'v': None, b'Vv': None,
                 b'*': c_char_p, b'@': c_void_p, b'#': c_void_p,
                 b':': c_void_p, b'^v': c_void_p, b'?': c_void_p,
                 NSPointEncoding: NSPoint, NSSizeEncoding: NSSize,
                 NSRectEncoding: NSRect, NSRangeEncoding: NSRange,
                 PyObjectEncoding: py_object}
    cfunctype_table = {}

    def __init__(self, method):
        self.selector = c_void_p(objc.method_getName(method))
        self.name = objc.sel_getName(self.selector)
        self.pyname = self.name.replace(b':', b'_')
        self.encoding = objc.method_getTypeEncoding(method)
        self.return_type = objc.method_copyReturnType(method)
        self.nargs = objc.method_getNumberOfArguments(method)
        self.imp = c_void_p(objc.method_getImplementation(method))
        self.argument_types = []
        for i in range(self.nargs):
            buffer = c_buffer(512)
            objc.method_getArgumentType(method, i, buffer, len(buffer))
            self.argument_types.append(buffer.value)
        try:
            self.argtypes = [self.ctype_for_encoding(t)
                             for t in self.argument_types]
        except:
            self.argtypes = None
        try:
            if self.return_type == b'@':
                self.restype = ObjCInstance
            elif self.return_type == b'#':
                self.restype = ObjCClass
            else:
                self.restype = self.ctype_for_encoding(self.return_type)
        except:
            self.restype = None
        self.func = None

    def ctype_for_encoding(self, encoding):
        """Return ctypes type for an encoded Objective-C type."""
        if encoding in self.typecodes:
            return self.typecodes[encoding]
        elif encoding[0:1] == b'^' and encoding[1:] in self.typecodes:
            return POINTER(self.typecodes[encoding[1:]])
        elif encoding[0:1] == b'^' and encoding[1:] in [CGImageEncoding,
                                                        NSZoneEncoding]:
            return c_void_p
        elif encoding[0:1] == b'r' and encoding[1:] in self.typecodes:
            return self.typecodes[encoding[1:]]
        elif encoding[0:2] == b'r^' and encoding[2:] in self.typecodes:
            return POINTER(self.typecodes[encoding[2:]])
        else:
            raise Exception('unknown encoding for %s: %s'
                            % (self.name, encoding))

    def get_prototype(self):
        if self.restype == ObjCInstance or self.restype == ObjCClass:
            self.prototype = CFUNCTYPE(c_void_p, *self.argtypes)
        else:
            self.prototype = CFUNCTYPE(self.restype, *self.argtypes)
        return self.prototype

    def __repr__(self):
        return "<ObjCMethod: %s %s>" % (self.name, self.encoding)

    def get_callable(self):
        if not self.func:
            prototype = self.get_prototype()
            self.func = cast(self.imp, prototype)
            if self.restype == ObjCInstance or self.restype == ObjCClass:
                self.func.restype = c_void_p
            else:
                self.func.restype = self.restype
            self.func.argtypes = self.argtypes
        return self.func

    def __call__(self, objc_id, *args):
        f = self.get_callable()
        try:
            result = f(objc_id, self.selector, *args)
            if self.restype == ObjCInstance:
                result = ObjCInstance(result)
            elif self.restype == ObjCClass:
                result = ObjCClass(result)
            return result
        except ArgumentError as error:
            error.args += ('selector = ' + self.name,
                           'argtypes =' + str(self.argtypes),
                           'encoding = ' + self.encoding)
            raise


class ObjCBoundMethod(object):
    def __init__(self, method, objc_id):
        self.method = method
        self.objc_id = objc_id

    def __repr__(self):
        return '<ObjCBoundMethod %s (%s)>' % (self.method.name, self.objc_id)

    def __call__(self, *args):
        return self.method(self.objc_id, *args)


class ObjCClass(object):
    _registered_classes = {}

    def __new__(cls, class_name_or_ptr):
        if isinstance(class_name_or_ptr, string_types):
            name = class_name_or_ptr
            ptr = get_class(name)
        else:
            ptr = class_name_or_ptr
            if not isinstance(ptr, c_void_p):
                ptr = c_void_p(ptr)
            name = objc.class_getName(ptr)

        if name in cls._registered_classes:
            return cls._registered_classes[name]

        objc_class = super(ObjCClass, cls).__new__(cls)
        objc_class.ptr = ptr
        objc_class.name = name
        objc_class.instance_methods = {}   # mapping of name -> instance method
        objc_class.class_methods = {}      # mapping of name -> class method
        objc_class._as_parameter_ = ptr    # for ctypes argument passing

        cls._registered_classes[name] = objc_class
        objc_class.cache_instance_methods()
        objc_class.cache_class_methods()
        return objc_class

    def __repr__(self):
        return "<ObjCClass: %s at %s>" % (self.name, str(self.ptr.value))

    def cache_instance_methods(self):
        count = c_uint()
        method_array = objc.class_copyMethodList(self.ptr, byref(count))
        for i in range(count.value):
            method = c_void_p(method_array[i])
            objc_method = ObjCMethod(method)
            self.instance_methods[objc_method.pyname] = objc_method

    def cache_class_methods(self):
        count = c_uint()
        args = [objc.object_getClass(self.ptr), byref(count)]
        method_array = objc.class_copyMethodList(*args)
        for i in range(count.value):
            method = c_void_p(method_array[i])
            objc_method = ObjCMethod(method)
            self.class_methods[objc_method.pyname] = objc_method

    def get_instance_method(self, name):
        if name in self.instance_methods:
            return self.instance_methods[name]
        else:
            selector = get_selector(name.replace(b'_', b':'))
            method = c_void_p(objc.class_getInstanceMethod(self.ptr, selector))
            if method.value:
                objc_method = ObjCMethod(method)
                self.instance_methods[name] = objc_method
                return objc_method
        return None

    def get_class_method(self, name):
        if name in self.class_methods:
            return self.class_methods[name]
        else:
            selector = get_selector(name.replace(b'_', b':'))
            method = c_void_p(objc.class_getClassMethod(self.ptr, selector))
            if method.value:
                objc_method = ObjCMethod(method)
                self.class_methods[name] = objc_method
                return objc_method
        return None

    def __getattr__(self, name):
        name = ensure_bytes(name)
        method = self.get_class_method(name)
        if method:
            return ObjCBoundMethod(method, self.ptr)
        method = self.get_instance_method(name)
        if method:
            return method
        raise AttributeError('ObjCClass %s has no attribute %s'
                             % (self.name, name))


class ObjCInstance(object):
    _cached_objects = {}

    def __new__(cls, object_ptr):
        if not isinstance(object_ptr, c_void_p):
            object_ptr = c_void_p(object_ptr)
        if not object_ptr.value:
            return None
        if object_ptr.value in cls._cached_objects:
            return cls._cached_objects[object_ptr.value]

        objc_instance = super(ObjCInstance, cls).__new__(cls)
        objc_instance.ptr = object_ptr
        objc_instance._as_parameter_ = object_ptr
        class_ptr = c_void_p(objc.object_getClass(object_ptr))
        objc_instance.objc_class = ObjCClass(class_ptr)

        cls._cached_objects[object_ptr.value] = objc_instance
        observer = send_message(send_message('DeallocationObserver', 'alloc'),
                                'initWithObject:', objc_instance)
        objc.objc_setAssociatedObject(objc_instance, observer, observer, 0x301)
        send_message(observer, 'release')
        return objc_instance

    def __repr__(self):
        if self.objc_class.name == b'NSCFString':
            from .cocoalibs import cfstring_to_string
            string = cfstring_to_string(self)
            return ("<ObjCInstance %#x: %s (%s) at %s>"
                    % (id(self), self.objc_class.name, string,
                       str(self.ptr.value)))
        return ("<ObjCInstance %#x: %s at %s>"
                % (id(self), self.objc_class.name, str(self.ptr.value)))

    def __getattr__(self, name):
        name = ensure_bytes(name)
        method = self.objc_class.get_instance_method(name)
        if method:
            return ObjCBoundMethod(method, self)
        method = self.objc_class.get_class_method(name)
        if method:
            return ObjCBoundMethod(method, self.objc_class.ptr)
        keys = list(self.objc_class.instance_methods.keys())
        raise AttributeError('ObjCInstance %s has no attribute %s, only:\n%s'
                             % (self.objc_class.name, name, keys))


def convert_method_arguments(encoding, args):
    new_args = []
    arg_encodings = parse_type_encoding(encoding)[3:]
    for e, a in zip(arg_encodings, args):
        if e == b'@':
            new_args.append(ObjCInstance(a))
        elif e == b'#':
            new_args.append(ObjCClass(a))
        else:
            new_args.append(a)
    return new_args


class ObjCSubclass(object):

    def __init__(self, superclass, name, register=True):
        self._imp_table = {}
        self.name = name
        self.objc_cls = create_subclass(superclass, name)
        self._as_parameter_ = self.objc_cls
        if register:
            self.register()

    def register(self):
        objc.objc_registerClassPair(self.objc_cls)
        self.objc_metaclass = get_metaclass(self.name)

    def add_ivar(self, varname, vartype):
        return add_ivar(self.objc_cls, varname, vartype)

    def add_method(self, method, name, encoding):
        imp = add_method(self.objc_cls, name, method, encoding)
        self._imp_table[name] = imp

    def add_class_method(self, method, name, encoding):
        imp = add_method(self.objc_metaclass, name, method, encoding)
        self._imp_table[name] = imp

    def rawmethod(self, encoding):
        encoding = ensure_bytes(encoding)
        typecodes = parse_type_encoding(encoding)
        typecodes.insert(1, b'@:')
        encoding = b''.join(typecodes)

        def decorator(f):
            name = f.__name__.replace('_', ':')
            self.add_method(f, name, encoding)
            return f
        return decorator

    def method(self, encoding):
        encoding = ensure_bytes(encoding)
        typecodes = parse_type_encoding(encoding)
        typecodes.insert(1, b'@:')
        encoding = b''.join(typecodes)

        def decorator(f):
            def objc_method(objc_self, objc_cmd, *args):
                py_self = ObjCInstance(objc_self)
                py_self.objc_cmd = objc_cmd
                args = convert_method_arguments(encoding, args)
                result = f(py_self, *args)
                if isinstance(result, ObjCClass):
                    result = result.ptr.value
                elif isinstance(result, ObjCInstance):
                    result = result.ptr.value
                return result
            name = f.__name__.replace('_', ':')
            self.add_method(objc_method, name, encoding)
            return objc_method
        return decorator

    def classmethod(self, encoding):
        """Function decorator for class methods."""
        # Add encodings for hidden self and cmd arguments.
        encoding = ensure_bytes(encoding)
        typecodes = parse_type_encoding(encoding)
        typecodes.insert(1, b'@:')
        encoding = b''.join(typecodes)

        def decorator(f):
            def objc_class_method(objc_cls, objc_cmd, *args):
                py_cls = ObjCClass(objc_cls)
                py_cls.objc_cmd = objc_cmd
                args = convert_method_arguments(encoding, args)
                result = f(py_cls, *args)
                if isinstance(result, ObjCClass):
                    result = result.ptr.value
                elif isinstance(result, ObjCInstance):
                    result = result.ptr.value
                return result
            name = f.__name__.replace('_', ':')
            self.add_class_method(objc_class_method, name, encoding)
            return objc_class_method
        return decorator


# XXX This causes segfaults in all backends (yikes!), and makes it so that
# pyglet can't even be loaded. We'll just have to live with leaks for now,
# which is probably alright since we only use the
# NSFontManager.sharedFontManager class currently.

# class DeallocationObserver_Implementation(object):
#    DeallocationObserver = ObjCSubclass('NSObject', 'DeallocationObserver',
#                                        register=False)
#    DeallocationObserver.add_ivar('observed_object', c_void_p)
#    DeallocationObserver.register()
#
#    @DeallocationObserver.rawmethod('@@')
#    def initWithObject_(self, cmd, anObject):
#        self = send_super(self, 'init')
#        self = self.value
#        set_instance_variable(self, 'observed_object', anObject, c_void_p)
#        return self
#
#    @DeallocationObserver.rawmethod('v')
#    def dealloc(self, cmd):
#        anObject = get_instance_variable(self, 'observed_object', c_void_p)
#        ObjCInstance._cached_objects.pop(anObject, None)
#        send_super(self, 'dealloc')
#
#    @DeallocationObserver.rawmethod('v')
#    def finalize(self, cmd):
#        anObject = get_instance_variable(self, 'observed_object', c_void_p)
#        ObjCInstance._cached_objects.pop(anObject, None)
#        send_super(self, 'finalize')


##############################################################################
# cocoalibs.py

cf = cdll.LoadLibrary(util.find_library('CoreFoundation'))

kCFStringEncodingUTF8 = 0x08000100

CFAllocatorRef = c_void_p
CFStringEncoding = c_uint32

cf.CFStringCreateWithCString.restype = c_void_p
cf.CFStringCreateWithCString.argtypes = [CFAllocatorRef, c_void_p,
                                         CFStringEncoding]

cf.CFRelease.restype = c_void_p
cf.CFRelease.argtypes = [c_void_p]

cf.CFStringGetLength.restype = CFIndex
cf.CFStringGetLength.argtypes = [c_void_p]

cf.CFStringGetMaximumSizeForEncoding.restype = CFIndex
cf.CFStringGetMaximumSizeForEncoding.argtypes = [CFIndex, CFStringEncoding]

cf.CFStringGetCString.restype = c_bool
cf.CFStringGetCString.argtypes = [c_void_p, c_char_p, CFIndex,
                                  CFStringEncoding]

cf.CFStringGetTypeID.restype = CFTypeID
cf.CFStringGetTypeID.argtypes = []

cf.CFAttributedStringCreate.restype = c_void_p
cf.CFAttributedStringCreate.argtypes = [CFAllocatorRef, c_void_p, c_void_p]

cf.CFURLCreateWithFileSystemPath.restype = c_void_p
cf.CFURLCreateWithFileSystemPath.argtypes = [CFAllocatorRef, c_void_p,
                                             CFIndex, c_bool]


def CFSTR(string):
    args = [None, string.encode('utf8'), kCFStringEncodingUTF8]
    return ObjCInstance(c_void_p(cf.CFStringCreateWithCString(*args)))


def get_NSString(string):
    """Autoreleased version of CFSTR"""
    return CFSTR(string).autorelease()


def cfstring_to_string(cfstring):
    length = cf.CFStringGetLength(cfstring)
    size = cf.CFStringGetMaximumSizeForEncoding(length, kCFStringEncodingUTF8)
    buffer = c_buffer(size + 1)
    result = cf.CFStringGetCString(cfstring, buffer, len(buffer),
                                   kCFStringEncodingUTF8)
    if result:
        return buffer.value.decode('utf8')


cf.CFDataCreate.restype = c_void_p
cf.CFDataCreate.argtypes = [c_void_p, c_void_p, CFIndex]

cf.CFDataGetBytes.restype = None
cf.CFDataGetBytes.argtypes = [c_void_p, CFRange, c_void_p]

cf.CFDataGetLength.restype = CFIndex
cf.CFDataGetLength.argtypes = [c_void_p]

cf.CFDictionaryGetValue.restype = c_void_p
cf.CFDictionaryGetValue.argtypes = [c_void_p, c_void_p]

cf.CFDictionaryAddValue.restype = None
cf.CFDictionaryAddValue.argtypes = [c_void_p, c_void_p, c_void_p]

cf.CFDictionaryCreateMutable.restype = c_void_p
cf.CFDictionaryCreateMutable.argtypes = [CFAllocatorRef, CFIndex,
                                         c_void_p, c_void_p]

cf.CFNumberCreate.restype = c_void_p
cf.CFNumberCreate.argtypes = [CFAllocatorRef, CFNumberType, c_void_p]

cf.CFNumberGetType.restype = CFNumberType
cf.CFNumberGetType.argtypes = [c_void_p]

cf.CFNumberGetValue.restype = c_ubyte
cf.CFNumberGetValue.argtypes = [c_void_p, CFNumberType, c_void_p]

cf.CFNumberGetTypeID.restype = CFTypeID
cf.CFNumberGetTypeID.argtypes = []

cf.CFGetTypeID.restype = CFTypeID
cf.CFGetTypeID.argtypes = [c_void_p]

# CFNumber.h
kCFNumberSInt8Type = 1
kCFNumberSInt16Type = 2
kCFNumberSInt32Type = 3
kCFNumberSInt64Type = 4
kCFNumberFloat32Type = 5
kCFNumberFloat64Type = 6
kCFNumberCharType = 7
kCFNumberShortType = 8
kCFNumberIntType = 9
kCFNumberLongType = 10
kCFNumberLongLongType = 11
kCFNumberFloatType = 12
kCFNumberDoubleType = 13
kCFNumberCFIndexType = 14
kCFNumberNSIntegerType = 15
kCFNumberCGFloatType = 16
kCFNumberMaxType = 16


def cfnumber_to_number(cfnumber):
    """Convert CFNumber to python int or float."""
    numeric_type = cf.CFNumberGetType(cfnumber)
    cfnum_to_ctype = {kCFNumberSInt8Type: c_int8, kCFNumberSInt16Type: c_int16,
                      kCFNumberSInt32Type: c_int32,
                      kCFNumberSInt64Type: c_int64,
                      kCFNumberFloat32Type: c_float,
                      kCFNumberFloat64Type: c_double,
                      kCFNumberCharType: c_byte, kCFNumberShortType: c_short,
                      kCFNumberIntType: c_int, kCFNumberLongType: c_long,
                      kCFNumberLongLongType: c_longlong,
                      kCFNumberFloatType: c_float,
                      kCFNumberDoubleType: c_double,
                      kCFNumberCFIndexType: CFIndex,
                      kCFNumberCGFloatType: CGFloat}

    if numeric_type in cfnum_to_ctype:
        t = cfnum_to_ctype[numeric_type]
        result = t()
        if cf.CFNumberGetValue(cfnumber, numeric_type, byref(result)):
            return result.value
    else:
        raise Exception(
            'cfnumber_to_number: unhandled CFNumber type %d' % numeric_type)

# Dictionary of cftypes matched to the method converting them to python values.
known_cftypes = {cf.CFStringGetTypeID(): cfstring_to_string,
                 cf.CFNumberGetTypeID(): cfnumber_to_number}


def cftype_to_value(cftype):
    """Convert a CFType into an equivalent python type.
    The convertible CFTypes are taken from the known_cftypes
    dictionary, which may be added to if another library implements
    its own conversion methods."""
    if not cftype:
        return None
    typeID = cf.CFGetTypeID(cftype)
    if typeID in known_cftypes:
        convert_function = known_cftypes[typeID]
        return convert_function(cftype)
    else:
        return cftype

cf.CFSetGetCount.restype = CFIndex
cf.CFSetGetCount.argtypes = [c_void_p]

cf.CFSetGetValues.restype = None
# PyPy 1.7 is fine with 2nd arg as POINTER(c_void_p),
# but CPython ctypes 1.1.0 complains, so just use c_void_p.
cf.CFSetGetValues.argtypes = [c_void_p, c_void_p]


def cfset_to_set(cfset):
    """Convert CFSet to python set."""
    count = cf.CFSetGetCount(cfset)
    buffer = (c_void_p * count)()
    cf.CFSetGetValues(cfset, byref(buffer))
    return set([cftype_to_value(c_void_p(buffer[i])) for i in range(count)])

cf.CFArrayGetCount.restype = CFIndex
cf.CFArrayGetCount.argtypes = [c_void_p]

cf.CFArrayGetValueAtIndex.restype = c_void_p
cf.CFArrayGetValueAtIndex.argtypes = [c_void_p, CFIndex]


def cfarray_to_list(cfarray):
    """Convert CFArray to python list."""
    count = cf.CFArrayGetCount(cfarray)
    return [cftype_to_value(c_void_p(cf.CFArrayGetValueAtIndex(cfarray, i)))
            for i in range(count)]


kCFRunLoopDefaultMode = c_void_p.in_dll(cf, 'kCFRunLoopDefaultMode')

cf.CFRunLoopGetCurrent.restype = c_void_p
cf.CFRunLoopGetCurrent.argtypes = []

cf.CFRunLoopGetMain.restype = c_void_p
cf.CFRunLoopGetMain.argtypes = []

cf.CFShow.restype = None
cf.CFShow.argtypes = [c_void_p]

######################################################################

# APPLICATION KIT

# Even though we don't use this directly, it must be loaded so that
# we can find the NSApplication, NSWindow, and NSView classes.
appkit = cdll.LoadLibrary(util.find_library('AppKit'))

NSDefaultRunLoopMode = c_void_p.in_dll(appkit, 'NSDefaultRunLoopMode')
NSEventTrackingRunLoopMode = c_void_p.in_dll(
    appkit, 'NSEventTrackingRunLoopMode')
NSApplicationDidHideNotification = c_void_p.in_dll(
    appkit, 'NSApplicationDidHideNotification')
NSApplicationDidUnhideNotification = c_void_p.in_dll(
    appkit, 'NSApplicationDidUnhideNotification')

# /System/Library/Frameworks/AppKit.framework/Headers/NSEvent.h
# NSAnyEventMask = 0xFFFFFFFFL     # NSUIntegerMax
# Commented out b/c not Py3k compatible

NSKeyDown = 10
NSKeyUp = 11
NSFlagsChanged = 12
NSApplicationDefined = 15

NSAlphaShiftKeyMask = 1 << 16
NSShiftKeyMask = 1 << 17
NSControlKeyMask = 1 << 18
NSAlternateKeyMask = 1 << 19
NSCommandKeyMask = 1 << 20
NSNumericPadKeyMask = 1 << 21
NSHelpKeyMask = 1 << 22
NSFunctionKeyMask = 1 << 23

NSInsertFunctionKey = 0xF727
NSDeleteFunctionKey = 0xF728
NSHomeFunctionKey = 0xF729
NSBeginFunctionKey = 0xF72A
NSEndFunctionKey = 0xF72B
NSPageUpFunctionKey = 0xF72C
NSPageDownFunctionKey = 0xF72D

# /System/Library/Frameworks/AppKit.framework/Headers/NSWindow.h
NSBorderlessWindowMask = 0
NSTitledWindowMask = 1 << 0
NSClosableWindowMask = 1 << 1
NSMiniaturizableWindowMask = 1 << 2
NSResizableWindowMask = 1 << 3

# /System/Library/Frameworks/AppKit.framework/Headers/NSPanel.h
NSUtilityWindowMask = 1 << 4

# /System/Library/Frameworks/AppKit.framework/Headers/NSGraphics.h
NSBackingStoreRetained = 0
NSBackingStoreNonretained = 1
NSBackingStoreBuffered = 2

# /System/Library/Frameworks/AppKit.framework/Headers/NSTrackingArea.h
NSTrackingMouseEnteredAndExited = 0x01
NSTrackingMouseMoved = 0x02
NSTrackingCursorUpdate = 0x04
NSTrackingActiveInActiveApp = 0x40

# /System/Library/Frameworks/AppKit.framework/Headers/NSOpenGL.h
NSOpenGLPFAAllRenderers = 1   # choose from all available renderers
NSOpenGLPFADoubleBuffer = 5   # choose a double buffered pixel format
NSOpenGLPFAStereo = 6   # stereo buffering supported
NSOpenGLPFAAuxBuffers = 7   # number of aux buffers
NSOpenGLPFAColorSize = 8   # number of color buffer bits
NSOpenGLPFAAlphaSize = 11   # number of alpha component bits
NSOpenGLPFADepthSize = 12   # number of depth buffer bits
NSOpenGLPFAStencilSize = 13   # number of stencil buffer bits
NSOpenGLPFAAccumSize = 14   # number of accum buffer bits
NSOpenGLPFAMinimumPolicy = 51   # never choose smaller buffers than requested
NSOpenGLPFAMaximumPolicy = 52   # choose largest buffers of type requested
NSOpenGLPFAOffScreen = 53   # choose an off-screen capable renderer
NSOpenGLPFAFullScreen = 54   # choose a full-screen capable renderer
NSOpenGLPFASampleBuffers = 55   # number of multi sample buffers
NSOpenGLPFASamples = 56   # number of samples per multi sample buffer
NSOpenGLPFAAuxDepthStencil = 57   # each aux buffer has its own depth stencil
NSOpenGLPFAColorFloat = 58   # color buffers store floating point pixels
NSOpenGLPFAMultisample = 59   # choose multisampling
NSOpenGLPFASupersample = 60   # choose supersampling
NSOpenGLPFASampleAlpha = 61   # request alpha filtering
NSOpenGLPFARendererID = 70   # request renderer by ID
NSOpenGLPFASingleRenderer = 71   # choose a single renderer for all screens
NSOpenGLPFANoRecovery = 72   # disable all failure recovery systems
NSOpenGLPFAAccelerated = 73   # choose a hardware accelerated renderer
NSOpenGLPFAClosestPolicy = 74   # choose the closest color buffer to request
NSOpenGLPFARobust = 75   # renderer does not need failure recovery
NSOpenGLPFABackingStore = 76   # back buffer contents are valid after swap
NSOpenGLPFAMPSafe = 78   # renderer is multi-processor safe
NSOpenGLPFAWindow = 80   # can be used to render to an onscreen window
NSOpenGLPFAMultiScreen = 81   # single window can span multiple screens
NSOpenGLPFACompliant = 83   # renderer is opengl compliant
NSOpenGLPFAScreenMask = 84   # bit mask of supported physical screens
NSOpenGLPFAPixelBuffer = 90   # can be used to render to a pbuffer
# can be used to render offline to a pbuffer
NSOpenGLPFARemotePixelBuffer = 91
NSOpenGLPFAAllowOfflineRenderers = 96  # allow use of offline renderers
# choose a hardware accelerated compute device
NSOpenGLPFAAcceleratedCompute = 97
# number of virtual screens in this format
NSOpenGLPFAVirtualScreenCount = 128

NSOpenGLCPSwapInterval = 222


# /System/Library/Frameworks/ApplicationServices.framework/Frameworks/...
#     CoreGraphics.framework/Headers/CGImage.h
kCGImageAlphaNone = 0
kCGImageAlphaPremultipliedLast = 1
kCGImageAlphaPremultipliedFirst = 2
kCGImageAlphaLast = 3
kCGImageAlphaFirst = 4
kCGImageAlphaNoneSkipLast = 5
kCGImageAlphaNoneSkipFirst = 6
kCGImageAlphaOnly = 7

kCGImageAlphaPremultipliedLast = 1

kCGBitmapAlphaInfoMask = 0x1F
kCGBitmapFloatComponents = 1 << 8

kCGBitmapByteOrderMask = 0x7000
kCGBitmapByteOrderDefault = 0 << 12
kCGBitmapByteOrder16Little = 1 << 12
kCGBitmapByteOrder32Little = 2 << 12
kCGBitmapByteOrder16Big = 3 << 12
kCGBitmapByteOrder32Big = 4 << 12

# NSApplication.h
NSApplicationPresentationDefault = 0
NSApplicationPresentationHideDock = 1 << 1
NSApplicationPresentationHideMenuBar = 1 << 3
NSApplicationPresentationDisableProcessSwitching = 1 << 5
NSApplicationPresentationDisableHideApplication = 1 << 8

# NSRunningApplication.h
NSApplicationActivationPolicyRegular = 0
NSApplicationActivationPolicyAccessory = 1
NSApplicationActivationPolicyProhibited = 2

######################################################################

# QUARTZ / COREGRAPHICS

quartz = cdll.LoadLibrary(util.find_library('quartz'))

CGDirectDisplayID = c_uint32     # CGDirectDisplay.h
CGError = c_int32                # CGError.h
CGBitmapInfo = c_uint32          # CGImage.h

# /System/Library/Frameworks/ApplicationServices.framework/Frameworks/...
#     ImageIO.framework/Headers/CGImageProperties.h
kCGImagePropertyGIFDictionary = c_void_p.in_dll(
    quartz, 'kCGImagePropertyGIFDictionary')
kCGImagePropertyGIFDelayTime = c_void_p.in_dll(
    quartz, 'kCGImagePropertyGIFDelayTime')

# /System/Library/Frameworks/ApplicationServices.framework/Frameworks/...
#     CoreGraphics.framework/Headers/CGColorSpace.h
kCGRenderingIntentDefault = 0

quartz.CGDisplayIDToOpenGLDisplayMask.restype = c_uint32
quartz.CGDisplayIDToOpenGLDisplayMask.argtypes = [c_uint32]

quartz.CGMainDisplayID.restype = CGDirectDisplayID
quartz.CGMainDisplayID.argtypes = []

quartz.CGShieldingWindowLevel.restype = c_int32
quartz.CGShieldingWindowLevel.argtypes = []

quartz.CGCursorIsVisible.restype = c_bool

quartz.CGDisplayCopyAllDisplayModes.restype = c_void_p
quartz.CGDisplayCopyAllDisplayModes.argtypes = [CGDirectDisplayID, c_void_p]

quartz.CGDisplaySetDisplayMode.restype = CGError
quartz.CGDisplaySetDisplayMode.argtypes = [
    CGDirectDisplayID, c_void_p, c_void_p]

quartz.CGDisplayCapture.restype = CGError
quartz.CGDisplayCapture.argtypes = [CGDirectDisplayID]

quartz.CGDisplayRelease.restype = CGError
quartz.CGDisplayRelease.argtypes = [CGDirectDisplayID]

quartz.CGDisplayCopyDisplayMode.restype = c_void_p
quartz.CGDisplayCopyDisplayMode.argtypes = [CGDirectDisplayID]

quartz.CGDisplayModeGetRefreshRate.restype = c_double
quartz.CGDisplayModeGetRefreshRate.argtypes = [c_void_p]

quartz.CGDisplayModeRetain.restype = c_void_p
quartz.CGDisplayModeRetain.argtypes = [c_void_p]

quartz.CGDisplayModeRelease.restype = None
quartz.CGDisplayModeRelease.argtypes = [c_void_p]

quartz.CGDisplayModeGetWidth.restype = c_size_t
quartz.CGDisplayModeGetWidth.argtypes = [c_void_p]

quartz.CGDisplayModeGetHeight.restype = c_size_t
quartz.CGDisplayModeGetHeight.argtypes = [c_void_p]

quartz.CGDisplayModeCopyPixelEncoding.restype = c_void_p
quartz.CGDisplayModeCopyPixelEncoding.argtypes = [c_void_p]

quartz.CGGetActiveDisplayList.restype = CGError
quartz.CGGetActiveDisplayList.argtypes = [
    c_uint32, POINTER(CGDirectDisplayID), POINTER(c_uint32)]

quartz.CGDisplayBounds.restype = CGRect
quartz.CGDisplayBounds.argtypes = [CGDirectDisplayID]

quartz.CGImageSourceCreateWithData.restype = c_void_p
quartz.CGImageSourceCreateWithData.argtypes = [c_void_p, c_void_p]

quartz.CGImageSourceCreateImageAtIndex.restype = c_void_p
quartz.CGImageSourceCreateImageAtIndex.argtypes = [
    c_void_p, c_size_t, c_void_p]

quartz.CGImageSourceCopyPropertiesAtIndex.restype = c_void_p
quartz.CGImageSourceCopyPropertiesAtIndex.argtypes = [
    c_void_p, c_size_t, c_void_p]

quartz.CGImageGetDataProvider.restype = c_void_p
quartz.CGImageGetDataProvider.argtypes = [c_void_p]

quartz.CGDataProviderCopyData.restype = c_void_p
quartz.CGDataProviderCopyData.argtypes = [c_void_p]

quartz.CGDataProviderCreateWithCFData.restype = c_void_p
quartz.CGDataProviderCreateWithCFData.argtypes = [c_void_p]

quartz.CGImageCreate.restype = c_void_p
quartz.CGImageCreate.argtypes = [c_size_t, c_size_t, c_size_t, c_size_t,
                                 c_size_t, c_void_p, c_uint32, c_void_p,
                                 c_void_p, c_bool, c_int]

quartz.CGImageRelease.restype = None
quartz.CGImageRelease.argtypes = [c_void_p]

quartz.CGImageGetBytesPerRow.restype = c_size_t
quartz.CGImageGetBytesPerRow.argtypes = [c_void_p]

quartz.CGImageGetWidth.restype = c_size_t
quartz.CGImageGetWidth.argtypes = [c_void_p]

quartz.CGImageGetHeight.restype = c_size_t
quartz.CGImageGetHeight.argtypes = [c_void_p]

quartz.CGImageGetBitsPerPixel.restype = c_size_t
quartz.CGImageGetBitsPerPixel.argtypes = [c_void_p]

quartz.CGImageGetBitmapInfo.restype = CGBitmapInfo
quartz.CGImageGetBitmapInfo.argtypes = [c_void_p]

quartz.CGColorSpaceCreateDeviceRGB.restype = c_void_p
quartz.CGColorSpaceCreateDeviceRGB.argtypes = []

quartz.CGDataProviderRelease.restype = None
quartz.CGDataProviderRelease.argtypes = [c_void_p]

quartz.CGColorSpaceRelease.restype = None
quartz.CGColorSpaceRelease.argtypes = [c_void_p]

quartz.CGWarpMouseCursorPosition.restype = CGError
quartz.CGWarpMouseCursorPosition.argtypes = [CGPoint]

quartz.CGDisplayMoveCursorToPoint.restype = CGError
quartz.CGDisplayMoveCursorToPoint.argtypes = [CGDirectDisplayID, CGPoint]

quartz.CGAssociateMouseAndMouseCursorPosition.restype = CGError
quartz.CGAssociateMouseAndMouseCursorPosition.argtypes = [c_bool]

quartz.CGBitmapContextCreate.restype = c_void_p
quartz.CGBitmapContextCreate.argtypes = [
    c_void_p, c_size_t, c_size_t, c_size_t, c_size_t, c_void_p, CGBitmapInfo]

quartz.CGBitmapContextCreateImage.restype = c_void_p
quartz.CGBitmapContextCreateImage.argtypes = [c_void_p]

quartz.CGFontCreateWithDataProvider.restype = c_void_p
quartz.CGFontCreateWithDataProvider.argtypes = [c_void_p]

quartz.CGFontCreateWithFontName.restype = c_void_p
quartz.CGFontCreateWithFontName.argtypes = [c_void_p]

quartz.CGContextDrawImage.restype = None
quartz.CGContextDrawImage.argtypes = [c_void_p, CGRect, c_void_p]

quartz.CGContextRelease.restype = None
quartz.CGContextRelease.argtypes = [c_void_p]

quartz.CGContextSetTextPosition.restype = None
quartz.CGContextSetTextPosition.argtypes = [c_void_p, CGFloat, CGFloat]

quartz.CGContextSetShouldAntialias.restype = None
quartz.CGContextSetShouldAntialias.argtypes = [c_void_p, c_bool]

quartz.CGDataProviderCreateWithURL.restype = c_void_p
quartz.CGDataProviderCreateWithURL.argtypes = [c_void_p]

quartz.CGFontCreateWithDataProvider.restype = c_void_p
quartz.CGFontCreateWithDataProvider.argtypes = [c_void_p]

quartz.CGDisplayScreenSize.argtypes = [CGDirectDisplayID]
quartz.CGDisplayScreenSize.restype = CGSize

quartz.CGDisplayBounds.argtypes = [CGDirectDisplayID]
quartz.CGDisplayBounds.restype = CGRect

######################################################################

# CORETEXT
ct = cdll.LoadLibrary(util.find_library('CoreText'))

# Types
CTFontOrientation = c_uint32      # CTFontDescriptor.h
CTFontSymbolicTraits = c_uint32   # CTFontTraits.h

# CoreText constants
kCTFontAttributeName = c_void_p.in_dll(ct, 'kCTFontAttributeName')
kCTFontFamilyNameAttribute = c_void_p.in_dll(ct, 'kCTFontFamilyNameAttribute')
kCTFontSymbolicTrait = c_void_p.in_dll(ct, 'kCTFontSymbolicTrait')
kCTFontWeightTrait = c_void_p.in_dll(ct, 'kCTFontWeightTrait')
kCTFontTraitsAttribute = c_void_p.in_dll(ct, 'kCTFontTraitsAttribute')

# constants from CTFontTraits.h
kCTFontItalicTrait = (1 << 0)
kCTFontBoldTrait = (1 << 1)

ct.CTLineCreateWithAttributedString.restype = c_void_p
ct.CTLineCreateWithAttributedString.argtypes = [c_void_p]

ct.CTLineDraw.restype = None
ct.CTLineDraw.argtypes = [c_void_p, c_void_p]

ct.CTFontGetBoundingRectsForGlyphs.restype = CGRect
ct.CTFontGetBoundingRectsForGlyphs.argtypes = [
    c_void_p, CTFontOrientation, POINTER(CGGlyph), POINTER(CGRect), CFIndex]

ct.CTFontGetAdvancesForGlyphs.restype = c_double
ct.CTFontGetAdvancesForGlyphs.argtypes = [
    c_void_p, CTFontOrientation, POINTER(CGGlyph), POINTER(CGSize), CFIndex]

ct.CTFontGetAscent.restype = CGFloat
ct.CTFontGetAscent.argtypes = [c_void_p]

ct.CTFontGetDescent.restype = CGFloat
ct.CTFontGetDescent.argtypes = [c_void_p]

ct.CTFontGetSymbolicTraits.restype = CTFontSymbolicTraits
ct.CTFontGetSymbolicTraits.argtypes = [c_void_p]

ct.CTFontGetGlyphsForCharacters.restype = c_bool
ct.CTFontGetGlyphsForCharacters.argtypes = [
    c_void_p, POINTER(UniChar), POINTER(CGGlyph), CFIndex]

ct.CTFontCreateWithGraphicsFont.restype = c_void_p
ct.CTFontCreateWithGraphicsFont.argtypes = [c_void_p, CGFloat, c_void_p,
                                            c_void_p]

ct.CTFontCopyFamilyName.restype = c_void_p
ct.CTFontCopyFamilyName.argtypes = [c_void_p]

ct.CTFontCopyFullName.restype = c_void_p
ct.CTFontCopyFullName.argtypes = [c_void_p]

ct.CTFontCreateWithFontDescriptor.restype = c_void_p
ct.CTFontCreateWithFontDescriptor.argtypes = [c_void_p, CGFloat, c_void_p]

ct.CTFontCreateCopyWithAttributes.restype = c_void_p
ct.CTFontCreateCopyWithAttributes.argtypes = [c_void_p, CGFloat, c_void_p,
                                              c_void_p]

ct.CTFontDescriptorCreateWithAttributes.restype = c_void_p
ct.CTFontDescriptorCreateWithAttributes.argtypes = [c_void_p]

ct.CTTypesetterCreateWithAttributedString.restype = c_void_p
ct.CTTypesetterCreateWithAttributedString.argtypes = [c_void_p]

ct.CTTypesetterCreateLine.restype = c_void_p
ct.CTTypesetterCreateLine.argtypes = [c_void_p, CFRange]

ct.CTLineGetOffsetForStringIndex.restype = CGFloat
ct.CTLineGetOffsetForStringIndex.argtypes = [c_void_p, CFIndex,
                                             POINTER(CGFloat)]

ct.CTFontManagerCreateFontDescriptorsFromURL.restype = c_void_p
ct.CTFontManagerCreateFontDescriptorsFromURL.argtypes = [c_void_p]

######################################################################

# FOUNDATION

# foundation = cdll.LoadLibrary(util.find_library('Foundation'))

# foundation.NSMouseInRect.restype = c_bool
# foundation.NSMouseInRect.argtypes = [NSPoint, NSRect, c_bool]
