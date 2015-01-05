### Q320: Spring 2012
### Cognitive Science Program, Indiana University
### Michael Gasser: gasser@cs.indiana.edu
###
### Reinforcement Learning World
### The things that populate our world.

import random, math
import utils

class Thing:
    '''Things of all types.'''

    radius = 10
    """Radius of the Canvas object representing the thing."""
    n = 0
    """Number of things created."""

    color = 'red'
    """Color of the thing's Canvas object."""

    def __init__(self, world, coords):
        """Initialize location, food type, texture, solidity, id."""
        self.coords = coords
        self.world = world
        self.food = Thing
        self.id = Thing.n
        self.texture = 'empty'
        self.solid = True
        self.alive = False
        self.create_graphic()
        self.world.tag_bind(self.graphic_id, '<1>', self.describe)
        Thing.n += 1

    def __str__(self):
        """Print name for things."""
        return self.__class__.__name__ + str(self.id)

    def create_graphic(self):
        '''Create a graphic in the world for the Thing, and assign its id.'''
        x, y = self.coords
        self.graphic_id = self.world.create_oval(x - Thing.radius, y - Thing.radius,
                                                 x + Thing.radius, y + Thing.radius,
                                                 fill = self.color, outline = 'white')

    def describe(self, event):
        '''Print out useful information about the Thing.'''
        print(self, '-- coordinates:', self.coords)

    def step(self):
        """Take primitive actions, if any, and update the thing."""
        pass

    def kill(self):
        """Remove the diskoid from the world."""
        self.world.delete(self.graphic_id)
        del self.world.graphic_objs[self.graphic_id]

class Clod(Thing):
    """A mineral."""

    color = 'brown'

    def __init__(self, world, coords):
        """Just for the texture."""
        Thing.__init__(self, world, coords)
        self.texture = 'hard'

class Fog(Thing):
    """Weather."""

    color = 'yellow'

    def __init__(self, world, coords):
        Thing.__init__(self, world, coords)
        self.solid = False

class Org(Thing):
    """A living thing."""

    init_strength = 5000

    def __init__(self, world, coords):
        Thing.__init__(self, world, coords)
        self.strength = Org.init_strength
        self.alive = True
        # Number of time steps the org has been living
        self.age = 0

    def step(self):
        # Age by one
        Thing.step(self)
        self.age += 1

    def die(self):
        """The org is scheduled to be lost from the world."""
        self.alive = False
        
    def describe(self, event):
        '''Print out useful information about the Thing.'''
        Thing.describe(self, event)
        print('  strength:', self.strength)

class Plasmoid(Org):
    """A plant-like thing."""

    color = 'green'

    def __init__(self, world, coords):
        Org.__init__(self, world, coords)
        self.texture = 'soft'

class Critter(Org):
    """An animate thing; it can move, turn, take actions, and learn."""

    eta = 0.0
    """Learning rate for Q learning."""

    gamma = .8
    """Discount rate for Q learning."""

    exploitation = 1.0
    """Parameter controlling exploration-exploitation tradeoff."""

    step_cost = 0
    """Amount a critter pays just for living one time step."""

    hard_bump_cost = -3
    """Amount a critter suffers when it collides with something hard."""

    soft_bump_cost = 0
    """Amount a critter suffers when it collides with something soft (not currently used)."""

    eat_cost = -2
    """How much an attempt to eat costs."""

    move_cost = -1
    """How much it costs to move."""

    turn_cost = -1
    """How much it costs to turn."""

    food_reward = 22
    """Amount a critter gains when it eats food."""

    move_dist = 12
    """Distance critter moves."""

    bump_offset = 0
    """How far into a Clod a critter can go without actually colliding."""

    eat_range = 5
    """Distance within which something can be eated."""

    mouth_angle = 20
    """Opening of the Critter's mouth."""

    def __init__(self, world, coords, heading=None):
        """Initialize strength and heading in addition to location."""
        self.heading = (heading if heading else random.randint(0, 360))
        Org.__init__(self, world, coords)
        self.move_dist = Critter.move_dist
        self.set_actions()
        self.set_sensor()
        self.init_Q()

    def create_graphic(self):
        """Override create_graphic in Thing, to make a body with a mouth."""
        x, y = self.coords
        self.graphic_id = self.world.create_arc(x - Thing.radius, y - Thing.radius,
                                                x + Thing.radius, y + Thing.radius,
                                                # A little mouth
                                                start=self.heading + self.mouth_angle / 2,
                                                extent=360 - self.mouth_angle,
                                                fill=self.color, outline='white')

    def set_actions(self):
        """Set the critter's list of actions."""
        self.actions = [self.move, self.turn_right, self.turn_left, self.eat]
        
    def set_sensor(self):
        """Set the critter's sensor."""
        self.sensor = Sensor(self, world, [])

    def init_Q(self):
        """Make the table of Q values, using self.sensor.n_states and len(self.actions)."""
        self.Q = [[0.0 for a in range(len(self.actions))] for s in range(self.sensor.n_states)]

    def print_Q(self):
        """Pretty print Q values."""
        print('Q VALUES FOR', self)
        # Action names for c
        print(' ' * 20, end=' ')
        for action in self.actions:
            print('%12s' % action.__name__, end=' ')
        print()
        # State names and values for each row
        for state in range(self.sensor.n_states):
            print('|'.join(self.sensor.int2symbolic(state)).ljust(20), end=' ')
            for action in range(len(self.actions)):
                print('%+12.3f' % self.Q[state][action], end=' ')
            print()

    def change_strength(self, amount):
        """Change the critter's strength by the amount (pos or neg)."""
        self.strength += amount

    def describe(self, event):
        '''Print out useful information about the Thing.'''
        Org.describe(self, event)
        print('  sensed:', self.sensor.sense())
        self.print_Q()

    def destroy(self):
        '''Really get rid of the Critter.'''
        self.sensor.destroy()

    def mouth_end(self):
        '''Coordinates of the point where the mouth opens.'''
        return utils.get_endpoint(self.coords[0], self.coords[1], self.heading, Thing.radius)

    def get_edible(self):
        '''Things overlapping with the Critter.'''
        end_x, end_y = self.mouth_end()
        return self.world.get_overlapping((end_x - Critter.eat_range, end_y - Critter.eat_range,
                                           end_x + Critter.eat_range, end_y + Critter.eat_range),
                                          self.graphic_id)

    ### What the critter does on every time step
    
    def step(self):
        """Select an action, execute it, and receive the reinforcement."""
        # Age
        Org.step(self)
        # Sense and save state
        state = self.sensor.sense()
        # Decide what to do
        action_index = self.decide(state)
        action = self.actions[action_index]
        # Act, getting the new reinforcement
        reinforcement = action()
        # Update reinforcement with the cost of living
        reinforcement += Critter.step_cost
        # Learn about the last state and action, using state as "next state"
        if self.world.steps > 0:
            self.learn(state)
        # Update "last" values, to use on next time step
        self.last_reinforcement = reinforcement
        self.last_state = state
        self.last_action = action_index
        # Change strength
        self.change_strength(reinforcement)
        if self.strength <= 0:
            self.die()

    ### Deciding

    def decide(self, state):
        '''Get an action index using the exponential Luce choice rule.'''
        return utils.exp_luce_choice(self.Q[state], self.exploitation)
        # Comment out the above and uncomment below to use the simpler binary
        # exploration-exploitation rule, which does not take the Q values into account
        # but is based on age only.
##        if random.random() < 1.0 - math.exp(-self.world.steps * self.exploitation):
##            # Exploit
##            return self.get_best_action(state)
##        # Explore
##        return random.randint(0, len(self.actions) - 1)

    ### Learning

    def learn(self, current_state):
        '''Update the Q values for the last state-last action pair.'''
        # Current Q value from the table
        current_Q = self.Q[self.last_state][self.last_action]
        # Make the new value be the sum of a proportion of the current value
        # and a proportion of the new information
        # (last reinforcement + estimate of best value of current state)
        self.Q[self.last_state][self.last_action] = \
            (1.0 - self.eta) * current_Q + \
            self.eta * (self.last_reinforcement + \
                        self.gamma * self.get_best_Q(current_state))

    def get_best_Q(self, state):
        '''The highest Q value for a state.'''
        return max(self.Q[state])

    def get_best_action(self, state):
        '''The action index with the highest Q value for a state.'''
        highest = -1000
        index = 0
        for i, q in enumerate(self.Q[state]):
            if q > highest:
                highest = q
                index = i
        return index

    ### Actions that can be selected

    def move(self):
        '''Move x and y in the direction of heading by move_dist unless something is hit.'''
        x_dist, y_dist = utils.xy_dist(self.heading, self.move_dist)
        # Adjust the coords in case the critter went around one edge of the world
        x, y = self.world.adjust_coords((self.coords[0] + x_dist,
                                         self.coords[1] + y_dist))
        # Check to see whether critter is bumping into a clod
        x1 = max(0, x - Thing.radius + Critter.bump_offset)
        y1 = max(0, y - Thing.radius + Critter.bump_offset)
        x2 = min(self.world.width, x + Thing.radius - Critter.bump_offset)
        y2 = min(self.world.height, y + Thing.radius - Critter.bump_offset)
        overlapping = self.world.get_overlapping((x1, y1, x2, y2), self.graphic_id)
        if [o for o in overlapping if isinstance(o, Clod)]:
            # Fail to move and get punished for the collision with the thing
            return Critter.hard_bump_cost
        # Go ahead and move
        self.world.coords(self.graphic_id,
                          x - Thing.radius, y - Thing.radius,
                          x + Thing.radius, y + Thing.radius)
        self.coords = x, y
        self.sensor.move()
        return Critter.move_cost

    def turn(self, angle=False):
        """Change the critter's heading by angle."""
        if not angle:
            self.heading = random.randint(0, 360)
        else:
            self.heading = (self.heading + angle) % 360
        self.world.itemconfigure(self.graphic_id,
                                 start = self.heading + self.mouth_angle / 2)
        self.sensor.turn()
        return Critter.turn_cost

    def turn_left(self):
        '''Turn counterclockwise.'''
        noise = random.randint(0, 10) - 5
        return self.turn(90 + noise)

    def turn_right(self):
        '''Turn clockwise.'''
        noise = random.randint(0, 10) - 5
        return self.turn(270 + noise)

    def eat(self):
        '''Attempt to eat.'''
        cost = Critter.eat_cost
        for c in self.get_edible():
            if isinstance(c, self.food):
                cost += Critter.food_reward
                c.die()
                #when the diskoid eats a sound is made and added to the world
                self.world.add_sound(self.coords, age=0)
        return cost

    ## Dying
    def kill(self):
        """Remove the critter and its sensor from the world."""
        Org.kill(self)
        self.sensor.destroy()

class Diskoid(Critter):
    '''Critters that adapt.'''

    mouth_angle = 30
    """Angle of the diskoid's mouth."""
    color = 'magenta'
    """Color of diskoid."""

    def __init__(self, world, coords):
        """Set the coordinates, world, and heading, and create the Canvas object."""
        Critter.__init__(self, world, coords)
        self.food = Plasmoid
        self.hunger = 0

    def set_sensor(self):
        '''Feel sensor.'''
        self.sensor = Feel(self, self.world,
                           # 3 short feelers around mouth, one long one out of mouth
                           [(0, 13), (90, 13), (2, 20), (270, 13)],
                           ['hard', 'soft'])

    def set_actions(self):
        """Set the critter's list of actions."""
        self.actions = [self.move, self.turn_left, self.turn_right, self.eat]
        
    def make_graphical_object(self):
        """Create the Canvas object for the diskoid: an arc."""
        x, y = self.coords
        self.graphic_id = self.world.create_arc(x - Thing.radius, y - Thing.radius,
                                                x + Thing.radius, y + Thing.radius,
                                                # A little mouth
                                                start=self.heading + self.mouth_angle / 2,
                                                extent=360 - self.mouth_angle,
                                                fill=self.color, outline='blue')

class Pentoid(Critter):
    """critters that can hear"""
    #written by both Zach and Aaron

    mouth_angle = 35
    color = "blue"
    
    def __init__(self, world, coords):
        Critter.__init__(self, world, coords)
        self.food = Diskoid
        self.hunger = 0

    def set_sensor(self):
        """hear sensor"""
        self.sensor = Hear(self, self.world, [("near", "front"), ("near", "back"), ("near", "left"), ("near", "right"),
                                              ("medium", "front"), ("medium", "back"), ("medium", "left"), ("medium", "right"),
                                              ("far", "front"), ("far", "back"), ("far", "left"), ("far", "right")]) 

    def set_actions(self):
        """has actions which the are reinforced by q learning"""
        self.actions = [self.move, self.turn_left, self.turn_right, self.eat]

    def make_graphical_object(self):
        """creates canvas object pentoid"""
        x, y = self.coords
        self.graphic_id = self.world.create_arc(x - Thing.radius, y - Thing.radius,
                                                x + Thing.radius, y + Thing.radius,
                                                # A little mouth
                                                start=self.heading + self.mouth_angle / 2,
                                                extent=360 - self.mouth_angle,
                                                fill=self.color, outline='yellow')

class Sensor(object):

    def __init__(self, critter, world, features):
        """Give the sensor a pointer to its critter."""
        self.critter = critter
        self.world = world
        self.features = features
        self.n_features = len(features)

    def get_n_states(self):
        """Number of different states."""
        return self.n_features

    def get_n_state_features(self):
        """Number of different state features."""
        return self.n_features

    def sense(self, symbolic=False):
        """Get sensory information to be passed on to critter.
        If symbolic is True, return a list of strings.
        Otherwise return a single integer.
        """
        features = self.sense_symbolic()
        if symbolic:
            return features
        else:
            return self.symbolic2int(features)

    def sense_symbolic(self):
        '''A list of features of things sensed.'''
        return [random.choice(self.features) for i in range(random.randint(0, 5))]

    def symbolic2int(self, symbols):
        '''Convert list of features to an integer state representation.'''
        total = 0
        power = 0
        for s in symbols:
            total += self.features.index(s) * len(self.features)**power
            power += 1
        return total

    def int2symbolic(self, state):
        '''The feature name corresponding to the state index.'''
        return self.features[state]

    def move(self):
        '''Move the graphical object(s) for the Sensor.'''
        pass

    def turn(self):
        '''Turn the graphical object(s) for the Sensor.'''
        pass

    def destroy(self):
        '''Get rid of the graphical object(s).'''
        pass

class Feel(Sensor):
    '''One or more feelers that can sense textures at their ends.'''

    color = 'yellow'

    def __init__(self, critter, world, feeler_specs, textures):
        '''Create the feelers, set features to be textures.'''
        Sensor.__init__(self, critter, world, textures)
        # Feeler_specs is a list of angles and lengths for each feeler
        self.feeler_specs = feeler_specs
        self.create_feelers()
        self.n_states = (self.n_features + 1) ** len(self.feelers)

    def get_n_states(self):
        """Number of different states."""
        return (self.n_features + 1) ** len(self.feelers)

    def get_n_state_features(self):
        """Number of different state features."""
        return (self.n_features + 1) * len(self.feelers)

    def feeler_coords(self, angle, length):
        '''Coordinates of feeler with given angle and length.'''
        end_x, end_y = utils.get_endpoint(self.critter.coords[0], self.critter.coords[1],
                                          (self.critter.heading + angle) % 360, length)
        return self.critter.coords[0], self.critter.coords[1], end_x, end_y

    def create_feelers(self):
        '''Create a Canvas object for each feeler, saving them in an attribute.'''
        self.feelers = [self.create_feeler(specs) for specs in self.feeler_specs]

    def create_feeler(self, angle_length):
        '''Create a Canvas object for an angle and length.'''
        coords = self.feeler_coords(*angle_length)
        if self.world:
            feeler_id = self.world.create_line(coords[0], coords[1], coords[2], coords[3],
                                               fill = self.color)
            self.world.tag_lower(feeler_id, self.critter.graphic_id)
        else:
            feeler_id = random.randint(1, 100)
        return feeler_id

    def sense_symbolic(self):
        '''List of Org textures felt by feelers, including texture positions.'''
        found = []
        for index, feeler in enumerate(self.feelers):
            # For each feeler, get the things that its end overlaps with
            end_x, end_y = list(self.world.coords(feeler))[2:]
            features = [t.texture \
                       for t in self.world.get_overlapping((end_x-1, end_y-1, end_x+1, end_y+1), None) \
                       if t.texture in self.features]
            if features:
                if len(features) > 1:
                    # Pick just one feature per feeler
                    found.append(random.choice(features))
                else:
                    found.append(features[0])
            else:
                found.append('none')
        return found

    def symbolic2int(self, symbols):
        '''Convert list of textures to an integer state representation.'''
        total = 0
        power = 0
        textures = ['none'] + self.features
        for s in symbols:
            total += textures.index(s) * len(textures)**power
            power += 1
        return total

    def int2symbolic(self, state):
        '''Convert an integer state representation to a list of textures.'''
        remainder = state
        textures = ['none'] + self.features
        symbols = ['none' for x in range(len(self.feelers))]
        for power in reversed(range(len(self.feelers))):
            n = len(textures)**power
            div = remainder // n
            remainder = remainder % n
            symbols[power] = textures[div]
        return symbols

    ## Methods to update the graphical objects
    
    def turn(self):
        '''Adjust graphics when critter turns.  Overrides method in Sense.'''
        for i, spec in zip(self.feelers, self.feeler_specs):
            coords = self.feeler_coords(*spec)
            self.world.coords(i, coords[0], coords[1], coords[2], coords[3])

    def move(self):
        '''Adjust graphics when critter moves.   Overrides method in Sense.'''
        for i, spec in zip(self.feelers, self.feeler_specs):
            coords = self.feeler_coords(*spec)
            self.world.coords(i, coords[0], coords[1], coords[2], coords[3])

    def destroy(self):
        '''Get rid of the graphical object(s).'''
        for f in self.feelers:
            self.world.delete(f)

class Hear(Sensor):
    """allows pentoids to hear sounds made in the world"""
    #written by both zach and aaron

    color = "orange"

    def __init__(self, critter, world, orientations):
        Sensor.__init__(self, critter, world, orientations)
        self.hearing_radius = 50
        ##self.hearing_specs = hearing_specs
        self.n_states = (self.n_features + 1) **1
        #print("state count")
        #print((self.n_features + 1) ** 1)
        #print((self.n_features + 1) * 1)

    def get_n_states(self):
        """Number of different states."""
        return (self.n_features + 1) ** 1

    def get_n_state_features(self):
        """Number of different state features."""
        
        return (self.n_features + 1) * 1

##    def ear_coords(self, angle, length):
##        '''Coordinates of ears with given angle and length.'''
##        end_x, end_y = utils.get_point_angle(self.critter.coords[0], self.critter.coords[1],
##                                          (self.critter.heading + angle) % 360, length)
##        return self.critter.coords[0], self.critter.coords[1], end_x, end_y

##    def create_ear(self):
##        '''Create a Canvas object for each ear, saving them in an attribute.'''
##        self.ears = [self.create_ear(specs) for specs in self.hearing_specs]
        

##    def create_ear(self, angle_length):
##        '''Create a Canvas object for an angle and length.'''
##        coords = self.feeler_coords(*angle_length)
##        if self.world:
##            feeler_id = self.world.create_line(coords[0], coords[1], coords[2], coords[3],
##                                               fill = self.color)
##            self.world.tag_lower(feeler_id, self.critter.graphic_id)
##        else:
##            feeler_id = random.randint(1, 100)
##        return feeler_id

##    def ear_angle(self, ear_ang, heading=0):
##        ear_angone = 360 - (heading + ear_ang)
##        ear_angtwo = 360 - (heading - ear_ang)
##        return [ear_angone, ear_angtwo]

    def sense_symbolic(self):
        '''List of Org textures heard by ear, including angle and dist.'''
        final_sensed = []
        closest = []
        distantces = []
        distance_angle = []
        for sound in self.world.sounds:
            manysounds = sound[0]
            #gets information about sounds
            dist = utils.get_point_dist(self.critter.coords[0], self.critter.coords[1], manysounds[0], manysounds[1])
            angle = utils.get_point_angle(self.critter.coords[0], self.critter.coords[1], manysounds[0], manysounds[1])
            #finds sounds within its hearing radius
            if dist <= self.hearing_radius:
                distantces.append(dist)
                distance_angle.append((dist, angle))
                #finds closest sound
        distantces.sort()
        for closest_sound in distance_angle:
            #runs the closest sound through paramaters which allow the pentoid to determine how far and where the sound is
            if closest_sound[0] == distantces[0]:
                closest.append(closest_sound[0])
                closest.append(closest_sound[1])
                #print(closest)
                if closest[0] >= 34:
                    final_sensed.append("far")
                elif 17 >= closest[0] >= 33:
                    final_sensed.append("medium")
                else:
                    #closest[0] <= 16
                    final_sensed.append("near")
                #front = self.ear_angle(45, heading=self.critter.heading)
                if 45 >= closest[1] >= 135:
                    final_sensed.append("front")
                #left = self.ear_angle(44, heading=(self.critter.heading - 90))
                elif 136 >= closest[1] >= 225:
                    final_snesed.append("left")
                #back = self.ear_angle(45, heading=(self.critter.heading - 180))
                elif 226 >= closest[1] >= 314:
                    final_sensed.append("back")
                #right = self.ear_angle(44, heading=(self.critter.heading + 90))
                else:
                    #315 >= closest[1] <= 44:
                    final_sensed.append("right")
##                if len(final_sensed) == 1:
##                    final_sensed.append("none")
                nSensed = (final_sensed[0], final_sensed[1])
                #nSensed makes the returned list into a tuple
                #this makes the mapping from the sense method under pentoid direct to the symbolic functions
                print(nSensed)
                return nSensed
            if len(final_sensed) < 1:
                nSensed = ("none", "none")
                print(nSensed)
                return nSensed

##        if closest[1] >= 34:
##            final_sensed.append("far")
##        if 17 >= closest[1] >= 33:
##            final_sensed.append("medium")
##        if closest[1] <= 16:
##            final_sensed.append("near")
##        front = ear_ang(45)
##        if front[1] >= closest[1] >= front[0]:
##            final_sensed.append("front")
##        left = ear_ang(134)
##        if left[1] >= closest[1] >= left[1]:
##            final_snesed.append("left")
##        back = ear_ang(225)
##        if back[1] >= closest[1] >= back[1]:
##            final_sensed.append("back")
##        right = ear_ang(315)
##        if right[1] >= closest[1] >= right[1]:
##            final_sensed.append("right")
                
    def symbolic2int(self, symbols):
        '''Convert list of sound to an integer state representation.'''
        total = 0
        power = 0
        orientations = self.features.append(('none', "none"))
        #print(symbols)
        #index method doesnt accept tuples so we had to hard code thier indexs in the list
        if symbols == ("none", "none"):
            total = 12
        if symbols == ("far", "right"):
            total = 11
        if symbols == ("far", "left"):
            total = 10
        if symbols == ("far", "back"):
            total = 9
        if symbols == ("far", "front"):
            total = 8
        if symbols == ("medium", "right"):
            total = 7
        if symbols == ("medium", "left"):
            total = 6
        if symbols == ("medium", "back"):
            total = 5
        if symbols == ("medium", "front"):
            total = 4
        if symbols == ("near", "right"):
            total = 3
        if symbols == ("near", "left"):
            total = 2
        if symbols == ("near", "back"):
            total = 1
        if symbols == ("near", "front"):
            total = 0
            
        #total = orientations.index(symbols)
        return total

    def int2symbolic(self, state):
        '''Convert an integer state representation to a list of sound.'''
        remainder = state
        orientations =  self.features.append(('none', "none"))
        symbols = orientations[state]
##        for power in reversed(range(1)):
##            n = len(orientations)**power
##            div = remainder // n
##            remainder = remainder % n
##            symbols[power] = orientations[div]
        return symbols

    ## Methods to update the graphical objects
    
##    def turn(self):
##        '''Adjust graphics when critter turns.  Overrides method in Sense.'''
##        for i, spec in zip(self.feelers, self.feeler_specs):
##            coords = self.feeler_coords(*spec)
##            self.world.coords(i, coords[0], coords[1], coords[2], coords[3])
##
##    def move(self):
##        '''Adjust graphics when critter moves.   Overrides method in Sense.'''
##        for i, spec in zip(self.feelers, self.feeler_specs):
##            coords = self.feeler_coords(*spec)
##            self.world.coords(i, coords[0], coords[1], coords[2], coords[3])
##
##    def destroy(self):
##        '''Get rid of the graphical object(s).'''
##        for f in self.feelers:
##            self.world.delete(f)
                                                 
