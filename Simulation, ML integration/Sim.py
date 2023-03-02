import pymunk
import numpy as np
import pygame


class Rod:
    def __init__(self, pos, a, b, m, space, radius=2):
        'position of CoM, start, end, mass, radius(width)'
        self.body = pymunk.Body()
        self.body.position = pos
        self.radius = radius
        self.a = a
        self.b = b
        self.body.center_of_gravity = (0,0)
        self.shape = pymunk.Segment(self.body, self.a, self.b, radius)
        self.shape.mass = m
        self.shape.elasticity = 0
        self.shape.filter = pymunk.ShapeFilter(group=1)
        self.shape.color = (0, 255, 0, 0)
        space.add(self.body, self.shape)

class Arm:
    def __init__(self, pos, a, b, m, space, radius=2):
        'position of CoM, start, end, mass, radius(width)'
        self.body = pymunk.Body()
        self.body.position = pos
        self.radius = radius
        self.a = a
        self.b = b
        self.body.center_of_gravity = (0,0)
        self.shape = pymunk.Segment(self.body, self.a, self.b, radius)
        self.shape.mass = m
        self.shape.elasticity = 0
        self.shape.filter = pymunk.ShapeFilter(group=1)
        self.shape.color = (255, 255, 0, 0)
        space.add(self.body, self.shape)

class Leg:
    def __init__(self, pos, a1, b1, a2, b2, m1, m2, space):
        'position of CoM, leg_start, leg_end, foot_start, foot_end,'
        ' leg_mass,  foot_mass, radius(width)'
        self.body = pymunk.Body()
        self.body.position = pos
        self.a1 = a1
        self.b1 = b1
        self.a2 = a2
        self.b2 = b2
        self.body.center_of_gravity = (0,0)#needs calculation
        self.leg = pymunk.Segment(self.body, self.a1, self.b1, radius=2)
        self.leg.filter = pymunk.ShapeFilter(group = 1)
        self.leg.color = (0, 255, 0, 0)
        self.leg.mass = m1
        self.foot= pymunk.Segment(self.body, self.a2, self.b2, radius=1)
        self.foot.filter = pymunk.ShapeFilter(group = 1)
        self.leg.mass = m2
        self.foot.color = (0, 255, 0, 0)
        space.add(self.body, self.leg, self.foot)

class Simplemotor:
    'is added and removed at diffrent points to move a joint at a constant speed'
    def __init__(self, body1, body2, rate, space, switch="off"):
        'rate is angular velocity in radians'
        self.rate = rate
        self.body1 = body1
        self.body2 = body2
        self.simplemotor = pymunk.SimpleMotor(self.body1, self.body2, self.rate)
        space.add(self.simplemotor)

class Pinjoint:
    def __init__(self, body1, body2, con1, con2, space):
        'two bodies and where to connect them by on each body'
        joint = pymunk.constraints.PinJoint(body1, body2, con1, con2)
        space.add(joint)

class Pivotjoint:
    def __init__(self, body1, body2, con1, con2, space, err = pow(1-0.1,30)):
        'two bodies and where to connect them by on each body, changing error bias allows speed change for simulation'
        joint = pymunk.constraints.PivotJoint(body1, body2, con1, con2)
        joint.error_bias = pow(1-0.4, 60)
        # joint.collide_bodies = collide
        space.add(joint)

class RotaryLimitJoint:
    def __init__(self, body1, body2, min, max, space):
        'prevents joint exceeding maximum angle'
        joint = pymunk.constraints.RotaryLimitJoint(body1, body2, min, max)
        # joint.collide_bodies = collide
        space.add(joint)
        
class Swing:
    def __init__(self,pos, a1, b1, a2, b2, a3, b3, a4, b4, m1, m2, m3, m4, space):
        'position of CoM, a=start, b=end, m=mass, 1/2/3=bar/vertical/base'
        self.body = pymunk.Body()
        self.body.position = pos
        s1 = pymunk.Segment(self.body, a1, b1 , radius=2) #bar
        s1.filter = pymunk.ShapeFilter(group = 1)
        s1.mass = m1
        s2 = pymunk.Segment(self.body, a2, b2, radius=3)#vertical
        s2.filter = pymunk.ShapeFilter(group = 1)
        s2.mass = m2
        s3 = pymunk.Segment(self.body, a3, b3, radius=1)#base
        s3.filter = pymunk.ShapeFilter(group = 1)
        s3.mass = m3
        s4 = pymunk.Segment(self.body, a4, b4, radius=3)#upper leg
        s4.filter = pymunk.ShapeFilter(group = 1)
        s4.mass = m4
        s4.color = (0, 255, 0, 0)
        space.add(self.body, s1,s2,s3,s4)

class Torso:
    def __init__(self, pos, a1, b1, r2, a2, m1, m2, space):
        'position of CoM, a1= torso start, b1=torso end, r2=head radius, a2=head offset, m=mass'
        self.body = pymunk.Body()
        self.body.position = pos
        self.a1 = a1
        self.b1 = b1
        self.body.center_of_gravity = (0,0)
        self.torso = pymunk.Segment(self.body, self.a1, self.b1 , radius=2)
        self.torso.filter = pymunk.ShapeFilter(group = 1)
        self.torso.mass = m1
        self.torso.color = (255, 0, 0, 0)
        self.head = pymunk.Circle(self.body, r2, a2)
        self.head.mass = m2
        self.head.filter = pymunk.ShapeFilter(group = 1)
        self.head.color = (255, 0, 0, 0)
        space.add(self.body, self.torso, self.head)

#----------------------------------------------------------------------------------------------------------------------
# FUNCTIONS FOR USE IN THE GYM ENVIRONMENT (PREVIOUSLY WITHIN GYM WITH SIM):

def setup_simulation():
    pm_space = pymunk.Space()
    pm_space.gravity = 0, 981
    background = pm_space.static_body
    speeds = [0, 0]
step_length = 1/ 100
    
    setup = {
        "step_length": step_length,
        "phi": -np.pi/6,
        # lengths /cm - innacurate
        "rl": 151 + 7,
        "sl1": 16,
        "sl2": 19 + 5,
        "sl3": 17,
        "sl4": [8,10],
        "ll1": 14,
        "ll2": 15,
        "tl": 18.5,
        "a1": 10,
        "a2": 11,

        "bg": (400, 200),

        # masses /kg
        "rm": 1.235 + 0.381 / 2,
        "sm1": 0.381 / 2,
        "sm2": 1.026,
        "sm3": 0.131 * 2 + 0.070 + 0.390 * 2,
        "sm4": 0.603* 2 + 0.134,
        "lm1": 0.292 * 2 + 0.134,
        "lm2": 0.162 * 2 + 0.134,
        "tm": 1.050 + 0.064 + 0.075 + 0.070,
        "head": 0.605,
        "am1": 0.075 + 0.158 * 2 + 0.065,
        "am2": 0.065 + 0.078 * 2 + 0.0185 * 2
    }
    centres = {
        "rc": (setup["bg"][0] + np.sin(setup["phi"])*setup["rl"] / 2, setup["bg"][1] + np.cos(setup["phi"])*setup["rl"] / 2),
        "sc": (setup["bg"][0] + np.sin(setup["phi"])*setup["rl"], setup["bg"][1] + np.cos(setup["phi"])*setup["rl"] + setup["sl2"] / 2),
        "lc": (setup["bg"][0] + np.sin(setup["phi"])*setup["rl"] + setup["sl4"][1], setup["bg"][1] + np.cos(setup["phi"])*setup["rl"] + setup["sl2"] - setup["sl4"][0] / 2 + setup["ll1"] / 2),
        "tc": (setup["bg"][0] + np.sin(setup["phi"])*setup["rl"] - setup["sl3"] / 2, setup["bg"][1] + np.cos(setup["phi"])*setup["rl"] + setup["sl2"] - setup["tl"] / 2 -0.25),
        
        "hip": (setup["bg"][0] + np.sin(setup["phi"])*setup["rl"] , setup["bg"][1] + np.cos(setup["phi"])*setup["rl"] + setup["sl2"] - setup["sl4"][0] /2),
        # "a1c": (setup["bg"][0] + setup["a1"]*np.cos(np.pi*(90-30.74)/180) / 2, setup["bg"][1] + setup["rl"] + setup["sl2"] - setup["tl"] + setup["a1"]*np.sin(np.pi*(90-30.74)/180) / 2),
        # "a2c": (setup["bg"][0] + setup["a1"]*np.cos(np.pi*(90-30.74)/180) + setup["a2"]*np.cos(np.pi*(54.5-30.74)/180) / 2, setup["bg"][1] + setup["rl"] + setup["sl2"] - setup["tl"] + setup["a1"]*np.sin(np.pi*(90-30.74)/180) - setup["a2"]*np.sin(np.pi*(54.5-30.74)/180) / 2)
    }

    # these add the object to the simulation
    bodies = {
        "rod": Rod(centres["rc"], (-np.sin(setup["phi"])*setup["rl"] / 2, -np.cos(setup["phi"])*setup["rl"] / 2), (np.sin(setup["phi"])*setup["rl"] / 2, np.cos(setup["phi"])*setup["rl"] / 2), setup["rm"], pm_space),
        "swing": Swing(centres["sc"],
                           (0, -setup["sl2"] / 2), (setup["sl1"], -setup["sl2"] / 2),#a1,b1
                           (0, setup["sl2"] / 2), (0, -setup["sl2"] / 2),#a2,b2
                           (-setup["sl3"] / 2 - 0.5, setup["sl2"] / 2), (setup["sl3"] / 2 - 0.5, setup["sl2"] / 2),#a3,b3
                           (0 , setup["sl2"] / 2 - setup["sl4"][0] /2), (setup["sl4"][1], setup["sl2"] / 2 - setup["sl4"][0] /2),#a4,b4
                           setup["sm1"], setup["sm2"], setup["sm3"],
                           setup["sm4"], pm_space),
        "leg": Leg(centres["lc"], (0, - setup["ll1"] / 2), (0, setup["ll1"] / 2), (-5, setup["ll1"] / 2),
                       (10, setup["ll1"] / 2), setup["lm1"], setup["lm2"], pm_space),
        "torso": Torso((centres["hip"][0], centres["hip"][1]- setup["tl"] / 2 -0.25),
                       (0, -setup["tl"] / 2 +0.25), (0, setup["tl"] / 2 -0.25),#a1,b1
                       6, (0, -2 -setup["tl"] / 2 +0.25), setup["tm"], setup["head"], pm_space),
    
        # "upper_arm": Arm(centres["a1c"], (-setup["a1"]*np.cos(np.pi*(90-30.74)/180) / 2, -setup["a1"]*np.sin(np.pi*(90-30.74)/180) / 2),
        #                   (setup["a1"]*np.cos(np.pi*(90-30.74)/180) / 2, setup["a1"]*np.sin(np.pi*(90-30.74)/180) / 2),
        #                   setup["a1"], pm_space),
        # "lower_arm": Arm(centres["a2c"], (-setup["a2"]*np.cos(np.pi*(54.5-30.74)/180) / 2, setup["a2"]*np.sin(np.pi*(54.5-30.74)/180) / 2),
        #                   (setup["a2"]*np.cos(np.pi*(54.5-30.74)/180) / 2, - setup["a2"]*np.sin(np.pi*(54.5-30.74)/180) / 2),
        #                   setup["a2"], pm_space), 
    }

    # fixed joints of simulation
    joints = {
        "back": Pivotjoint(bodies["swing"].body, bodies["torso"].body, (0 , setup["sl2"] / 2 - setup["sl4"][0] /2),
                             (0, setup["tl"] / 2), pm_space),
        "front": Pivotjoint(bodies["swing"].body, bodies["leg"].body, (setup["sl4"][1], (setup["sl2"] - setup["sl4"][0]) / 2 ),
                              (0, -setup["ll1"] / 2), pm_space),
        "bottom": Pivotjoint(bodies["rod"].body, bodies["swing"].body, (np.sin(setup["phi"])*setup["rl"] / 2, np.cos(setup["phi"])*setup["rl"] / 2), (0, -setup["sl2"] / 2),
                               pm_space),
        "top": Pivotjoint(background, bodies["rod"].body, setup["bg"],
                        (-np.sin(setup["phi"])*setup["rl"] / 2, -np.cos(setup["phi"])*setup["rl"] / 2), pm_space),
        "limit": RotaryLimitJoint(bodies["rod"].body, bodies["swing"].body, -np.pi/3, np.pi/3, pm_space)
        # "shoulder": Pinjoint(bodies["torso"].body, bodies["upper_arm"].body,
        #                      (0, -setup["tl"] / 2 +0.25),
        #                      (-setup["a1"]*np.cos(np.pi*(90-30.74)/180) / 2, -setup["a1"]*np.sin(np.pi*(90-30.74)/180) / 2),
        #                      pm_space),
        # "elbow": Pinjoint(bodies["upper_arm"].body, bodies["lower_arm"].body,
        #                   (setup["a1"]*np.cos(np.pi*(90-30.74)/180) / 2, setup["a1"]*np.sin(np.pi*(90-30.74)/180) / 2),
        #                   (-setup["a2"]*np.cos(np.pi*(54.5-30.74)/180) / 2, setup["a2"]*np.sin(np.pi*(54.5-30.74)/180) / 2),
        #                   pm_space),
        # "wrist": Pinjoint(bodies["lower_arm"].body, bodies["swing"].body,
        #                   (setup["a2"]*np.cos(np.pi*(54.5-30.74)/180) / 2, - setup["a2"]*np.sin(np.pi*(54.5-30.74)/180) / 2),
        #                   (10, -setup["sl2"] / 2), pm_space)
    }
    motors = {
        "back": Simplemotor(bodies["swing"].body, bodies["leg"].body, 0, pm_space),
        "front": Simplemotor(bodies["swing"].body, bodies["torso"].body, 0, pm_space),
        # "m_shoulder": Simplemotor(bodies["torso"].body, bodies["upper_arm"].body, 0, pm_space),
        # "m_elbow": Simplemotor(bodies["upper_arm"].body, bodies["lower_arm"].body, 0, pm_space),
        # "m_wrist": Simplemotor(bodies["lower_arm"].body, bodies["swing"].body, 0, pm_space)
        
    }
    return {"pm_space": pm_space, "motors": motors, "bodies": bodies, "joints": joints, "speeds": speeds, "setup": setup}

def perform_action(environment, action, simulation_data):
    
    #get angle of leg and torso relative to the verticle in degrees
    leg_angle = - 180/np.pi * (environment.simulation_data["pm_space"].bodies[2].angle - environment.simulation_data["pm_space"].bodies[1].angle)
    torso_angle = - 180/np.pi * (environment.simulation_data["pm_space"].bodies[3].angle - environment.simulation_data["pm_space"].bodies[1].angle)
    
    #arbitrary acceleration, to be changed later (units of change in speed per tick)
    acceleration = 6
    
    #defining the sign of the leg motion so if the angle of the leg is more positive (anti-clockwise) than the target angle the motion will be a negative (clockwise rotation)
    signs = np.sign(np.array([action[0], action[2]]) - np.array([leg_angle, torso_angle])) * (np.pi / 180) * [action[1], action[3]]
    #if the angle of the leg is more clockwise this will result in anticlockwise rotation, signs is just action with direction included. 
    
    #if the leg is greater than 5 degrees from the target
    if abs(action[0] - leg_angle) >= 5:
        #if the actual rotation speed is equal to the intended speed then pass
        if environment.simulation_data["speeds"][0] == signs[0]:
            pass
        #if the actual speed is less than the intended speed increase the actual speed by a value of acceleration
        elif environment.simulation_data["speeds"][0] < signs[0]:
            environment.simulation_data["speeds"][0] += acceleration
        #if the actual speed is greater than the intended speed decrease the speed
        elif environment.simulation_data["speeds"][0] > signs[0]:
            environment.simulation_data["speeds"][0] -= acceleration
         
    #if the leg is within 5 degrees of the target angle
    else:
        #if the speed is positive (within a 0.2 range of 0) decrease it by a value of acceleration
        if environment.simulation_data["speeds"][0] > 0.1:
              environment.simulation_data["speeds"][0] -= acceleration
        #if the speed is negative (again within a threshold) increase it by acceleration
        elif environment.simulation_data["speeds"][0] < -0.1:
              environment.simulation_data["speeds"][0] += acceleration
        #if the speed is close to 0 set it to 0 to minimise overshooting through fluctuations
        else:
            environment.simulation_data["speeds"][0] = 0
        
    #add a motor to the leg each tick with a speed adjusted in the above functions
    add_motor_l(simulation_data, environment.simulation_data["speeds"][0])
    
    
    #repeat of the above but for the torso
    if abs(action[2] - torso_angle) >= 5:
        if environment.simulation_data["speeds"][1] == signs[1]:
            pass
        elif environment.simulation_data["speeds"][1] < signs[1]:
            environment.simulation_data["speeds"][1] += acceleration
        elif environment.simulation_data["speeds"][1] > signs[1]:
            environment.simulation_data["speeds"][1] -= acceleration
            
    else:
        if environment.simulation_data["speeds"][1] > 0.1:
              environment.simulation_data["speeds"][1] -= acceleration
        elif environment.simulation_data["speeds"][1] < -0.1:
              environment.simulation_data["speeds"][1] += acceleration
        else:
            environment.simulation_data["speeds"][1] = 0
         
    add_motor_t(simulation_data, environment.simulation_data["speeds"][1])
    
    return simulation_data

def add_motor_l(simulation_data, speed):
    simulation_data["motors"]["front"] = Simplemotor(simulation_data["bodies"]["swing"].body,
                                                     simulation_data["bodies"]["leg"].body, speed,
                                                     simulation_data["pm_space"])

    
def add_motor_t(simulation_data, speed):
    simulation_data["motors"]["back"] = Simplemotor(simulation_data["bodies"]["swing"].body,
                                                     simulation_data["bodies"]["torso"].body, speed,
                                                     simulation_data["pm_space"])



# ---------------------------------------------------------------------------------------------------------------------
# manual actions from keypresses:

def get_action(keytouple):
    # FOR MANUAL CONTROL OF THE SIMULATION (RETURN ACTION ARRAYS FROM KEY PRESSES)

  if keytouple[pygame.K_l]:
        leg_action = np.array([90, 360, 0, 0])

  elif keytouple[pygame.K_j]:
      leg_action = np.array([-45, 360, 0, 0])

  else:
      leg_action = np.array([0, 0, 0, 0])
        
  if keytouple[pygame.K_d]:
      torso_action = np.array([0, 0, 60, 360])

  elif keytouple[pygame.K_a]:
      torso_action = np.array([0, 0, -45, 360])

  else:
      torso_action = np.array([0, 0, 0, 0])
    
  return leg_action + torso_action

