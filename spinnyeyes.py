import math
import time

import pygame

TARGET_FRAME_RATE = 60        # fps
TOTAL_ROTATION_TIME_MS = 1000 # ms

NUM_POINTS = int(round((TOTAL_ROTATION_TIME_MS / 1000.0) * TARGET_FRAME_RATE))
TICK_TIME_S = 1.0 / TARGET_FRAME_RATE

SPIRAL_OUT_PCT = 0.25          # when spiralling out/in, do so over 40% of the circle
NUM_SPIRAL_POINTS = int(NUM_POINTS * SPIRAL_OUT_PCT)


PUPIL_RADIUS = 110
EYE_RADIUS = 200

SCREEN_CENTER = (200, 200)

def main():
    screen = init_screen()

    circle_points, spiral_points = precalculate_points()

    run_loop(screen, circle_points, spiral_points)

def init_screen():
    screen = pygame.display.set_mode( (400, 400) )

    pygame.display.update()
    return screen

def precalculate_points():
    # starting at the left (pi), going clockwise (down)

    total_circumference = math.pi * 2
    rad_interval = total_circumference / NUM_POINTS

    circle_points = []
    # matches indexes with circle_points
    spiral_points = []

    def add_point(relative_point, lst):
        center_x, center_y = SCREEN_CENTER

        relative_x, relative_y = relative_point
        # normalize to our center
        x = int(relative_x + center_x)
        y = int(relative_y + center_y)
        lst.append( (x, y) )

    for i in xrange(NUM_POINTS):
        phi = math.pi + (i * rad_interval)
        circle_r = EYE_RADIUS - PUPIL_RADIUS

        def get_point(r):
            return r * math.cos(phi), r * math.sin(phi)

        add_point(get_point(circle_r), circle_points)

        def get_spiral_r(pct):
            assert 0 <= pct <= 1.0
            scaled_pct = math.sqrt(pct)
            return int(circle_r * scaled_pct)

        if i < NUM_SPIRAL_POINTS:
            pct = (i / float(NUM_SPIRAL_POINTS))
            add_point(get_point(get_spiral_r(pct)), spiral_points)

        elif i >= (NUM_POINTS - NUM_SPIRAL_POINTS):
            pct = (NUM_POINTS - i) / float(NUM_SPIRAL_POINTS)
            add_point(get_point(get_spiral_r(pct)), spiral_points)

        else:
            # placeholder so we can use the circle/spiral indexes interchangeably
            spiral_points.append(None)

    return circle_points, spiral_points

def run_loop(screen, circle_points, spiral_points):

    class StateHolder(object):
        is_paused = True
        is_starting = False
        is_finishing = False

    def choose_point(idx):
        if StateHolder.is_paused:
            return spiral_points[0]

        if StateHolder.is_starting:
            if idx < NUM_SPIRAL_POINTS:
                return spiral_points[idx]
            else:
                # we're past the starting spiral
                StateHolder.is_starting = False

        if StateHolder.is_finishing:
            if idx >= (NUM_POINTS - NUM_SPIRAL_POINTS):
                return spiral_points[idx]
            elif idx == 0:
                # we're done finishing (pause)
                StateHolder.is_finishing = False
                StateHolder.is_paused = True
                return spiral_points[0]

        return circle_points[idx]

    tick_count = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if StateHolder.is_paused:
                    StateHolder.is_starting = True
                    StateHolder.is_paused = False
                else:
                    StateHolder.is_finishing = True

        now = time.time()
        if StateHolder.is_paused:
            tick_count = 0
        tick(screen, choose_point(tick_count % NUM_POINTS))
        tick_count += 1
        sleep_time_s = max(0, TICK_TIME_S - (time.time() - now))
        if sleep_time_s > 0:
            pygame.time.delay(int(sleep_time_s*1000))

def tick(screen, point):
    screen.fill( (240, 240, 240) )
    pygame.draw.circle(screen, (0, 0, 0), SCREEN_CENTER, EYE_RADIUS, 1)
    pygame.draw.circle(screen, (0, 0, 0), point, PUPIL_RADIUS, 0)
    pygame.display.update()

if __name__ == "__main__":
    main()
