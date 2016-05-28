from time import sleep
import sdl2

sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_HAPTIC)

print("Num: " + str(sdl2.SDL_NumHaptics()))

haptic = sdl2.SDL_HapticOpen(0)

#sdl2.SDL_HapticRumbleInit(haptic)

#sdl2.SDL_HapticRumblePlay(haptic, 0.5, 2000)

effect = sdl2.SDL_HapticEffect()

effect.type = sdl2.SDL_HAPTIC_CONSTANT
effect.constant.direction.type = sdl2.SDL_HAPTIC_CARTESIAN
effect.constant.direction.dir[0] = -1
effect.constant.direction.dir[1] = 0
effect.constant.direction.dir[2] = 0
effect.constant.length =  5000
effect.constant.delay = 0
effect.constant.level = 32000
effect.constant.attack_length = 2
effect.constant.attack_level = 32000
effect.constant.fade_lenght = 1
effect.constant.fade_level = 10000

effect_side = sdl2.SDL_HapticEffect()

effect_side.type = sdl2.SDL_HAPTIC_CONSTANT
effect_side.constant.direction.type = sdl2.SDL_HAPTIC_CARTESIAN
effect_side.constant.direction.dir[0] = 1
effect_side.constant.direction.dir[1] = 0
effect_side.constant.direction.dir[2] = 0
effect_side.constant.length =  5000
effect_side.constant.delay = 0
effect_side.constant.level = 32000
effect_side.constant.attack_length = 2
effect_side.constant.attack_level = 32000
effect_side.constant.fade_lenght = 1
effect_side.constant.fade_level = 10000

effect_sine = sdl2.SDL_HapticEffect()
effect_sine.type = sdl2.SDL_HAPTIC_SINE
effect_sine.periodic.direction.type = sdl2.SDL_HAPTIC_POLAR
effect_sine.periodic.direction.dir[0] = 27000
#  If type is ::SDL_HAPTIC_POLAR, direction is encoded by hundredths of a
#  degree starting north and turning clockwise.  ::SDL_HAPTIC_POLAR only uses
#  the first \c dir parameter.  The cardinal directions would be:
#   - North: 0 (0 degrees)
#   - East: 9000 (90 degrees)
#   - South: 18000 (180 degrees)
#   - West: 27000 (270 degrees)
effect_sine.periodic.period = 1000
effect_sine.periodic.magnitude = 20000
effect_sine.periodic.length = 5000 # 5 seconds long
effect_sine.periodic.attack_length = 1000 # Takes 1 second to get max strength
effect_sine.periodic.fade_length = 1000

effect_id = sdl2.SDL_HapticNewEffect(haptic, effect)
effect_id_sine = sdl2.SDL_HapticNewEffect(haptic, effect_sine)
effect_id_side = sdl2.SDL_HapticNewEffect(haptic, effect_side)


sdl2.SDL_HapticRunEffect(haptic, effect_id, 1)
sdl2.SDL_HapticRunEffect(haptic, effect_id_sine, 1)
sdl2.SDL_Delay( 5000 )

sdl2.SDL_HapticDestroyEffect(haptic, effect_id)
sdl2.SDL_HapticDestroyEffect(haptic, effect_id_sine)
sdl2.SDL_HapticDestroyEffect(haptic, effect_id_side)

sdl2.SDL_HapticClose(haptic)
