#!/usr/bin/env python3

### Q320: Spring 2012
### Cognitive Science Program, Indiana University
### Michael Gasser: gasser@cs.indiana.edu
###
### Reinforcement Learning World
### A toroidal world with diskoids that can move around in it and use reinforcement
### learning to figure out that they should be avoiding the clods and eating
### the plasmoids. This version allows things of a certain type to be clustered in
### particular regions of the world. Portions that are different from main.py
### are marked with #{ COMMENT code #}.

import random, math
from tkinter import *
from thing import *
import utils

### ADDITIONAL UTILITY FUNCTION

def some(pred, seq):
    '''Returns the first successful application of pred to elements in seq.'''
    for x in seq:
        px = pred(x)
        if px:
            return px
    return False

class WorldFrame(Frame):
    '''A Frame in which to display the world.'''

    def __init__(self, root, width=450, height=450):
        '''Give the frame a canvas, a world, and dimensions and display it.'''
        Frame.__init__(self, root)
        self.world = World(self, width=width, height=height)
        root.title('The World')
        self.step_button = Button(self, text='Step', command=self.world.step)
        self.step_button.grid(row=1, column=0)
        self.run_button = Button(self, text='Run', command=self.world.run)
        self.run_button.grid(row=1, column=1)
        self.reinit_button = Button(self, text='Reinit', command=self.world.reinit)
        self.reinit_button.grid(row=1, column=2)
        self.learn_button = Button(self, text='Learn')
        self.learn_button.grid(row=1, column=3)
        self.learn_button.bind('<Button-1>', self.world.learn)
        self.grid()

class World(Canvas):
    """The arena where everything happens, including both graphics and thing representation."""

    color = 'black'
    """Color for the Canvas background."""

    steps_per_run = 500
    """Number of steps to run when the 'Run' button is pushed."""

    thing_specs = {Clod: {'init': 4},
                   Diskoid: {'init': 16},
                   Pentoid: {"init": 5},
                   Plasmoid: {'init': 95, 'min': 80, 'max': 120,
                              # { Each tuple defines a cluster: ((center_x, center_y), radius)
                              'clusters': [((100, 100), 40), ((300, 300), 80)]
                              # }
                              }}
    """Dictionary specifying things to created and maintain. Clod must come first."""

    def __init__(self, frame, width=450, height=450):
        """Initialize dimensions and create things."""
        Canvas.__init__(self, frame, bg=World.color, width=width, height=height)
        self.frame = frame
        self.width = width
        self.height = height
        self.things = []
        self.graphic_objs = {}
        self.steps = 0
        self.init_things()
        #this will save all sounds made in the world for a certain amount of steps
        self.sounds = []
##        self.bind('<Control-Button-1>', self.add_diskoid_at)
##        self.bind('<Option-Button-1>', self.add_clod_at)
##        self.bind('<Shift-Button-1>', self.add_plasmoid_at)
        self.grid(row=0, columnspan=4)

    def init_things(self):
        """Use thing_specs to initialize the things in the world."""
        for typ, specs in World.thing_specs.items():
            if 'init' in specs:
                # An initial number of things of this type is specified
                for thing in range(specs['init']):
                    #{ Change this line to have the 'clusters' argument
                    self.add_thing(typ, clusters=specs.get('clusters', []))
                    #}
#                    self.add_thing(typ)

    def learn(self, event):
        """Handler for the Learn button.
        Binds the button to the other handler."""
        print('Starting learning')
        self.frame.learn_button.config(text="Don't learn")
        Critter.eta = 0.5
        self.frame.learn_button.bind('<Button-1>', self.dont_learn)

    def dont_learn(self, event):
        """Handler for the Learn button.
        Binds the button to the other handler."""
        print('Turning off learning')
        self.frame.learn_button.config(text="Learn")
        Critter.eta = 0.0
        self.frame.learn_button.bind('<Button-1>', self.learn)

    # Handlers for automatically adding things in event positions.

##    def add_diskoid_at(self, event):
##        """Add a diskoid to the world where the event happens."""
##        self.add_thing(Diskoid, coords=(event.x, event.y))

##    def add_clod_at(self, event):
##        """Add a clod to the world where the event happens."""
##        self.add_thing(Clod, coords=(event.x, event.y))
##
##    def add_plasmoid_at(self, event):
##        """Add a clod to the world where the event happens."""
##        self.add_thing(Plasmoid, coords=(event.x, event.y))

    #{ Replace old add_thing with this


    def add_sound(self, sound_coord, age=0):
        self.sounds.append([sound_coord, age])

    
    
    def add_thing(self, tp, clusters=[]):
        '''Create a thing of a given type and index.'''
        coords = self.get_thing_coords(clusters=clusters)
        thing = tp(self, coords)
        self.graphic_objs[thing.graphic_id] = thing
        self.things.append(thing)
        return thing
    #}

##    def add_thing(self, tp, coords=None):
##        '''Create a thing of a given type at a random location.'''
##        coords = coords or self.get_thing_coords(Clod)
##        thing = tp(self, coords)
##        self.things.append(thing)
##        self.graphic_objs[thing.graphic_id] = thing
##        return thing

    #{ Replace old get_thing_coords with this
    def get_thing_coords(self, clusters=[]):
        '''Coordinates for a new thing, using clusters if there are any.'''
        if clusters:
            cluster = random.choice(clusters)
            x, y = self.get_cluster_pos(cluster[1], cluster[0])
        else:
            x, y = (random.randint(Thing.radius,
                                   self.width - Thing.radius),
                    random.randint(Thing.radius,
                                   self.height - Thing.radius))
        if self.overlaps_with(x - Thing.radius, y - Thing.radius,
                              x + Thing.radius, y + Thing.radius,
                              Clod):
            return self.get_thing_coords(clusters=clusters)
        else:
            return x, y
    #}

    #{ Add this cluster method
    def get_cluster_pos(self, maxrad, center):
        """Return a position given a cluster center and radius."""
        c_x, c_y = center[0], center[1]
        x = random.randint(0, maxrad)
        y = random.randint(0, int(math.sqrt(maxrad * maxrad - x * x)))
        if random.random() < .5:
            x = -x
        if random.random() < .5:
            y = -y
        return c_x + x, c_y + y
    #}

    def overlaps_with(self, x1, y1, x2, y2, kind, exclude=-1):
        '''Does the region with coordinates x1, y1, x2, y2 overlap with any of type kind?'''
        return some(lambda x: isinstance(self.graphic_objs.get(x, None), kind) and x != exclude,
                   self.find_overlapping(x1, y1, x2, y2))

##    def get_thing_coords(self, overlap_constraint):
##        '''Coordinates for a new thing; can't overlap with a world edge or a Clod.'''
##        x, y = (random.randint(Thing.radius, self.width - Thing.radius),
##                random.randint(Thing.radius, self.height - Thing.radius))
##        if overlap_constraint:
##            overlapping = self.get_overlapping((x + Thing.radius, y + Thing.radius,
##                                                x - Thing.radius, y - Thing.radius), None)
##            if [o for o in overlapping if isinstance(o, overlap_constraint)]:
##                # Try again
##                return self.get_thing_coords(overlap_constraint)
##        return x, y

    def adjust_coords(self, coords):
        '''Adjust coordinates of moved critter, assuming the world wraps around.'''
        x, y = coords
        if x < 0:
            x = self.width + x
        elif x > self.width:
            x = x - self.width
        if y < 0:
            y = self.height + y
        elif y > self.height:
            y = y - self.height
        return x, y

    def get_overlapping(self, coords, except_thing_id):
        '''Things that overlap with coordinates coords other than except_thing.'''
        return [self.graphic_objs[thing_id] for thing_id in \
                self.find_overlapping(coords[0], coords[1], coords[2], coords[3]) \
                if thing_id in self.graphic_objs and thing_id != except_thing_id]

    def get_n_things(self, typ):
        '''Number of things in the world of a given type.'''
        return len([thing for thing in self.things if isinstance(thing, typ)])

    def step(self):
        """Step each of the things and do other updating (creating and destroying)."""
        # Recreate things if number has fallen below minimum for type
        for typ, specs in World.thing_specs.items():
            if 'min' in specs:
                n_things = self.get_n_things(typ)
                for thing in range(specs['min'] - n_things):
                    #{ Change this line to include the clusters argument
                    self.add_thing(typ, clusters=specs.get('clusters', []))
                    #}
#                    self.add_thing(typ)
        # Now step each of things
        for thing in self.things:
            thing.step()
        # Kill off things that have died
        self.kill_off()
        # Increment steps
        self.steps += 1
        #this ages all the sounds in the world, and removes them if they get passed four steps
        for sound in self.sounds:
            sound[1] += 1
            if sound[1] >= 4:
                self.sounds.remove(sound)
        #print(self.sounds)

    def kill_off(self, everybody=False):
        """Kill off orgs that have died or all things if everybody is True."""
        for thing in self.things[:]:
            if everybody or (isinstance(thing, Org) and not thing.alive):
                thing.kill()
                self.things.remove(thing)
 
    def run(self):
        """Run step() steps_per_run times on everything, and display the world."""
        for s in range(World.steps_per_run):
            self.step()
            self.update_idletasks()
        self.run_stats()
        print(self.sounds)

    def run_stats(self, verbose=False):
        '''Print useful statistics about the types in the population of orgs.'''
        print('POPULATION AFTER', self.steps, 'STEPS')
        for typ in list(World.thing_specs.keys()):
            if issubclass(typ, Org):
                strength_sum = 0.0
                age_sum = 0.0
                n = 0
                max_s = 0
                for t1 in [t2 for t2 in self.things if isinstance(t2, typ)]:
                    strength = t1.strength
                    strength_sum += strength
                    if strength > max_s:
                        max_s = strength
                    age_sum += t1.age
                    n += 1
                if n != 0:
                    print(typ.__name__ + ':  N', n, ' mean strength', int(strength_sum / n),\
                          ' max strength', max_s, 'mean age', int(age_sum / n))

    def reinit(self):
        """Get rid of everything and recreate initial numbers of things."""
        self.kill_off(True)
        self.init_things()
        self.steps = 0
        print('=================================== REINITIALIZING ===================================')

# Create the root 
root = Tk()
frame = WorldFrame(root)
WORLD = frame.world
root.mainloop()
