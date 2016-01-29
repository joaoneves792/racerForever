# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.8
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_ms3d', [dirname(__file__)])
        except ImportError:
            import _ms3d
            return _ms3d
        if fp is not None:
            try:
                _mod = imp.load_module('_ms3d', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _ms3d = swig_import_helper()
    del swig_import_helper
else:
    import _ms3d
del version_info
try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.


def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if (name == "thisown"):
        return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if (not static):
        if _newclass:
            object.__setattr__(self, name, value)
        else:
            self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr_nondynamic(self, class_type, name, static=1):
    if (name == "thisown"):
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    if (not static):
        return object.__getattr__(self, name)
    else:
        raise AttributeError(name)

def _swig_getattr(self, class_type, name):
    return _swig_getattr_nondynamic(self, class_type, name, 0)


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except AttributeError:
    class _object:
        pass
    _newclass = 0


class shader(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, shader, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, shader, name)
    __repr__ = _swig_repr

    def __init__(self, vertShader, fragShader):
        this = _ms3d.new_shader(vertShader, fragShader)
        try:
            self.this.append(this)
        except Exception:
            self.this = this
    __swig_destroy__ = _ms3d.delete_shader
    __del__ = lambda self: None

    def getShader(self):
        return _ms3d.shader_getShader(self)

    def use(self):
        return _ms3d.shader_use(self)
shader_swigregister = _ms3d.shader_swigregister
shader_swigregister(shader)

class ms3d(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, ms3d, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, ms3d, name)
    __repr__ = _swig_repr

    def __init__(self, *args):
        this = _ms3d.new_ms3d(*args)
        try:
            self.this.append(this)
        except Exception:
            self.this = this
    __swig_destroy__ = _ms3d.delete_ms3d
    __del__ = lambda self: None

    def draw(self):
        return _ms3d.ms3d_draw(self)

    def drawGL3(self):
        return _ms3d.ms3d_drawGL3(self)

    def createRectangle(self, width, height, texture):
        return _ms3d.ms3d_createRectangle(self, width, height, texture)

    def changeRectangleTexture(self, texture):
        return _ms3d.ms3d_changeRectangleTexture(self, texture)

    def prepare(self, shader):
        return _ms3d.ms3d_prepare(self, shader)

    def getJointPosition(self, jointName):
        return _ms3d.ms3d_getJointPosition(self, jointName)

    def changeTexture(self, groupName, textureFile):
        return _ms3d.ms3d_changeTexture(self, groupName, textureFile)
    __swig_getmethods__["initGlew"] = lambda x: _ms3d.ms3d_initGlew
    if _newclass:
        initGlew = staticmethod(_ms3d.ms3d_initGlew)
ms3d_swigregister = _ms3d.ms3d_swigregister
ms3d_swigregister(ms3d)

def ms3d_initGlew():
    return _ms3d.ms3d_initGlew()
ms3d_initGlew = _ms3d.ms3d_initGlew

class Tex(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Tex, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Tex, name)
    __repr__ = _swig_repr

    def __init__(self, filename):
        this = _ms3d.new_Tex(filename)
        try:
            self.this.append(this)
        except Exception:
            self.this = this

    def getTexture(self):
        return _ms3d.Tex_getTexture(self)
    __swig_destroy__ = _ms3d.delete_Tex
    __del__ = lambda self: None
Tex_swigregister = _ms3d.Tex_swigregister
Tex_swigregister(Tex)


_ms3d.MODEL_swigconstant(_ms3d)
MODEL = _ms3d.MODEL

_ms3d.VIEW_swigconstant(_ms3d)
VIEW = _ms3d.VIEW

_ms3d.PROJECTION_swigconstant(_ms3d)
PROJECTION = _ms3d.PROJECTION
class GLM(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, GLM, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, GLM, name)
    __repr__ = _swig_repr

    def __init__(self, shader):
        this = _ms3d.new_GLM(shader)
        try:
            self.this.append(this)
        except Exception:
            self.this = this
    __swig_destroy__ = _ms3d.delete_GLM
    __del__ = lambda self: None

    def selectMatrix(self, Matrix):
        return _ms3d.GLM_selectMatrix(self, Matrix)

    def perspective(self, fov_degrees, aspect_ratio, near, far):
        return _ms3d.GLM_perspective(self, fov_degrees, aspect_ratio, near, far)

    def otho(self, left, right, bottom, top, near, far):
        return _ms3d.GLM_otho(self, left, right, bottom, top, near, far)

    def lookAt(self, eyeX, eyeY, eyeZ, centerX, centerY, centerZ, upX, upY, upZ):
        return _ms3d.GLM_lookAt(self, eyeX, eyeY, eyeZ, centerX, centerY, centerZ, upX, upY, upZ)

    def loadIdentity(self):
        return _ms3d.GLM_loadIdentity(self)

    def translate(self, x, y, z):
        return _ms3d.GLM_translate(self, x, y, z)

    def rotate(self, angle, x, y, z):
        return _ms3d.GLM_rotate(self, angle, x, y, z)

    def scale(self, x, y, z):
        return _ms3d.GLM_scale(self, x, y, z)

    def pushMatrix(self):
        return _ms3d.GLM_pushMatrix(self)

    def popMatrix(self):
        return _ms3d.GLM_popMatrix(self)

    def changeShader(self, newShader):
        return _ms3d.GLM_changeShader(self, newShader)

    def getMVP(self):
        return _ms3d.GLM_getMVP(self)
GLM_swigregister = _ms3d.GLM_swigregister
GLM_swigregister(GLM)


_ms3d.MAX_LIGHTS_swigconstant(_ms3d)
MAX_LIGHTS = _ms3d.MAX_LIGHTS
class Lights(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Lights, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Lights, name)
    __repr__ = _swig_repr

    def __init__(self, shader):
        this = _ms3d.new_Lights(shader)
        try:
            self.this.append(this)
        except Exception:
            self.this = this
    __swig_destroy__ = _ms3d.delete_Lights
    __del__ = lambda self: None

    def enableLighting(self):
        return _ms3d.Lights_enableLighting(self)

    def disableLighting(self):
        return _ms3d.Lights_disableLighting(self)

    def enable(self, light):
        return _ms3d.Lights_enable(self, light)

    def disable(self, light):
        return _ms3d.Lights_disable(self, light)

    def setColor(self, light, red, green, blue, intensity):
        return _ms3d.Lights_setColor(self, light, red, green, blue, intensity)

    def setPosition(self, light, x, y, z):
        return _ms3d.Lights_setPosition(self, light, x, y, z)

    def setCone(self, light, direction_x, direction_y, direction_z, angle):
        return _ms3d.Lights_setCone(self, light, direction_x, direction_y, direction_z, angle)
Lights_swigregister = _ms3d.Lights_swigregister
Lights_swigregister(Lights)


_ms3d.SHADOW_MAP_SIZE_swigconstant(_ms3d)
SHADOW_MAP_SIZE = _ms3d.SHADOW_MAP_SIZE
class Shadows(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Shadows, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Shadows, name)
    __repr__ = _swig_repr

    def __init__(self, glm, normalShader, shadowMapShader, window_width, window_height, shadow_map_width, shadow_map_height):
        this = _ms3d.new_Shadows(glm, normalShader, shadowMapShader, window_width, window_height, shadow_map_width, shadow_map_height)
        try:
            self.this.append(this)
        except Exception:
            self.this = this
    __swig_destroy__ = _ms3d.delete_Shadows
    __del__ = lambda self: None

    def prepareToMapDepth(self, lightPosX, lightPosY, lightPosZ):
        return _ms3d.Shadows_prepareToMapDepth(self, lightPosX, lightPosY, lightPosZ)

    def changeOrthoBox(self, left, right, bottom, top, near, far):
        return _ms3d.Shadows_changeOrthoBox(self, left, right, bottom, top, near, far)

    def returnToNormalDrawing(self):
        return _ms3d.Shadows_returnToNormalDrawing(self)

    def getShadowTexture(self):
        return _ms3d.Shadows_getShadowTexture(self)
Shadows_swigregister = _ms3d.Shadows_swigregister
Shadows_swigregister(Shadows)

# This file is compatible with both classic and new-style classes.



class MATRIX:
    MODEL = 1
    VIEW = 2
    PROJECTION = 3

class LIGHTS:
    LIGHT_0 = 0
    LIGHT_1 = 1
    LIGHT_2 = 2
    LIGHT_3 = 3
    LIGHT_4 = 4
    LIGHT_5 = 5
    LIGHT_6 = 6
    LIGHT_7 = 7
    LIGHT_8 = 8
    LIGHT_9 = 9
