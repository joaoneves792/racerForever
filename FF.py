from enum import IntEnum
from threading import Timer, Lock

import sdl2

# For some reason SDL_HAPTIC_INFINITY doesnt work...
# and even if you set the time limit to lower it always stops after 25~30 seconds
SECONDS_MAX = 30000
SCHEDULE_TIME = 20


class Effects(IntEnum):
    IDLE_EFFECT = 0
    THROTTLE_EFFECT = 1
    BRAKING_EFFECT = 2


class FF:
    def __init__(self):
        sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_HAPTIC)
        self.haptic = sdl2.SDL_HapticOpen(0)

        # Figure out how many effects there are
        num_effects = 0
        for effect in Effects:
            num_effects += 1

        self.effects = [None] * num_effects
        self.playing_effects = [False] * num_effects

        self.effects[Effects.IDLE_EFFECT] = self.__create_idle_effect__()
        self.effects[Effects.THROTTLE_EFFECT] = self.__create_throttle_effect__()
        self.effects[Effects.BRAKING_EFFECT] = self.__create_braking_effect__()
        self.lock = Lock()

        # We have to periodically restart all running effects (see comment on top)
        self.timer = Timer(SCHEDULE_TIME, self.__restart_effects__)
        self.timer.start()

    def shutdown(self):
        for effect in self.effects:
            sdl2.SDL_HapticDestroyEffect(self.haptic, effect)
        sdl2.SDL_HapticClose(self.haptic)

    def __restart_effects__(self):
        with self.lock:
            for effect in Effects:
                if self.playing_effects[effect]:
                    self.__stop_effect_unsafe__(effect)
                    self.__play_effect_unsafe__(effect)

        self.timer = Timer(SCHEDULE_TIME, self.__restart_effects__)
        self.timer.start()

    def __play_effect__(self, effect):
        with self.lock:
            if not self.playing_effects[effect]:
                self.playing_effects[effect] = True
                sdl2.SDL_HapticRunEffect(self.haptic, self.effects[effect], 1)

    def __stop_effect__(self, effect):
        with self.lock:
            if self.playing_effects[effect]:
                self.playing_effects[effect] = False
                sdl2.SDL_HapticStopEffect(self.haptic, self.effects[effect])

    # Unsafe method to be used only if you already acquired the lock
    def __play_effect_unsafe__(self, effect):
        sdl2.SDL_HapticRunEffect(self.haptic, self.effects[effect], 1)

    # Unsafe method to be used only if you already acquired the lock
    def __stop_effect_unsafe__(self, effect):
        sdl2.SDL_HapticStopEffect(self.haptic, self.effects[effect])

    def play_idle(self):
        self.__play_effect__(Effects.IDLE_EFFECT)

    def stop_idle(self):
        self.__stop_effect__(Effects.IDLE_EFFECT)

    def play_throttle(self):
        self.__play_effect__(Effects.THROTTLE_EFFECT)

    def stop_throttle(self):
        self.__stop_effect__(Effects.THROTTLE_EFFECT)

    def play_brakes(self):
        self.__play_effect__(Effects.BRAKING_EFFECT)

    def stop_brakes(self):
        self.__stop_effect__(Effects.BRAKING_EFFECT)

    def __create_idle_effect__(self):
        effect = sdl2.SDL_HapticEffect()
        effect.type = sdl2.SDL_HAPTIC_CONSTANT
        effect.constant.direction.type = sdl2.SDL_HAPTIC_CARTESIAN
        effect.constant.direction.dir[0] = 0
        effect.constant.direction.dir[1] = -1
        effect.constant.direction.dir[2] = 0
        effect.constant.length = SECONDS_MAX
        effect.constant.delay = 0
        effect.constant.level = 3500
        effect.constant.attack_length = 0
        effect.constant.attack_level = 0
        effect.constant.fade_length = 0
        effect.constant.fade_level = 0
        return sdl2.SDL_HapticNewEffect(self.haptic, effect)

    def __create_throttle_effect__(self):
        effect = sdl2.SDL_HapticEffect()
        effect.type = sdl2.SDL_HAPTIC_CONSTANT
        effect.constant.direction.type = sdl2.SDL_HAPTIC_CARTESIAN
        effect.constant.direction.dir[0] = 0
        effect.constant.direction.dir[1] = -1
        effect.constant.direction.dir[2] = 0
        effect.constant.length = SECONDS_MAX
        effect.constant.delay = 0
        effect.constant.level = 10000
        effect.constant.attack_length = 0
        effect.constant.attack_level = 0
        effect.constant.fade_length = 0
        effect.constant.fade_level = 0
        return sdl2.SDL_HapticNewEffect(self.haptic, effect)

    def __create_braking_effect__(self):
        effect = sdl2.SDL_HapticEffect()
        effect.type = sdl2.SDL_HAPTIC_SAWTOOTHUP
        effect.periodic.direction.type = sdl2.SDL_HAPTIC_POLAR
        effect.periodic.direction.dir[0] = 0
        effect.periodic.period = 1000
        effect.periodic.magnitude = 20000
        effect.periodic.length = SECONDS_MAX
        effect.periodic.attack_length = 1500
        effect.periodic.attack_level = 10000
        effect.periodic.fade_length = 0
        return sdl2.SDL_HapticNewEffect(self.haptic, effect)
