#pitchipoy simple rig
# face bones no addressed - must leave the eye bones (or add for rigify)
# globals
# ob  - armature object
# arm - armature
# 23sep15   retarget hand ik and elbow pole targets to chest

import bpy, math

setup_custom_shapes = True
# use rigify/pitchipoy shapes if you have them
use_rigify_shapes = False

ob = bpy.context.scene.objects.active
arm = ob.data
bpy.ops.object.mode_set(mode='EDIT')
print( "bone count [{0}]".format( len( arm.edit_bones)))

pitchipoy = False

# pitchipoy uses different names for some bones
# ctrlHips is created by us, hips_name is the original hip bone
head_name = "head"
hips_name = "hips"
spine_name = "spine"
chest_name = "chest"
neck_name = "neck"
if head_name not in arm.edit_bones:
    pitchipoy = True
    hips_name = "spine"
    spine_name = "spine.001"
    chest_name = "spine.003"
    neck_name = "spine.004"
    head_name = "spine.006"
else:
    if "eye.L" not in arm.edit_bones:
        print( "need to add eye bones")
        raise Exception

# bones for custom shapes
bone_names = [
"ctrlRoot","ctrlFoot.L","ctrlFoot.R","toe.L","toe.R",
"ctrlFootRoll.L","ctrlFootRoll.R","ikKnee.L","ikKnee.R",
"ctrlHips","ctrlTorso",spine_name,chest_name,neck_name,head_name,
"shoulder.L","shoulder.R","ikElbow.L","ikElbow.R","ikHand.L","ikHand.R",
"thumb.01.L","thumb.02.L","f_index.01.L","f_middle.01.L","f_ring.01.L","f_pinky.01.L",
"thumb.01.R","thumb.02.R","f_index.01.R","f_middle.01.R","f_ring.01.R","f_pinky.01.R",
"ctrlEyes","eye_target.L","eye_target.R"
]

# my custom shapes
my_shapes = [
"shapeRoot" ,"shapeFoot.L","shapeFoot.R","shapeToe","shapeToe","shapeHeel.L","shapeHeel.R",
"shapeKnee.L","shapeKnee.R",
"shapeHips","shapeTorso","shapeWaist","shapeChest","shapeNeck","shapeHead",
"shapeShoulder.L","shapeShoulder.R","shapeElbow.L","shapeElbow.R","shapeHand.L","shapeHand.R",
"shapeFinger","shapeFinger","shapeFinger","shapeFinger","shapeFinger","shapeFinger",
"shapeFinger","shapeFinger","shapeFinger","shapeFinger","shapeFinger","shapeFinger",
"shapeEyes","shapeEye.L","shapeEye.R"
]

# rigify shapes 
rigify_shapes = [
"WGT-root","WGT-foot.ik.L","WGT-foot.ik.R","WGT-toe.L","WGT-toe.R",
"WGT-foot_roll.ik.L","WGT-foot_roll.ik.L","WGT-knee_target.ik.L","WGT-knee_target.ik.R",
"WGT-hips","WGT-torso","WGT-spine","WGT-chest","WGT-neck","WGT-head","WGT-shoulder.L","WGT-shoulder.R",
"WGT-elbow_target.ik.L","WGT-elbow_target.ik.R","WGT-hand.ik.L","WGT-hand.ik.R",
"WGT-thumb.L","WGT-thumb.L","WGT-f_index.L","WGT-f_middle.L","WGT-f_ring.L","WGT-f_pinky.L",
"WGT-thumb.R","WGT-thumb.R","WGT-f_index.R","WGT-f_middle.R","WGT-f_ring.R","WGT-f_pinky.R",
"shapeEyes","shapeEye.L","shapeEye.R"
]

print( "pitchipoy armature [{0}]".format( pitchipoy))
    
# edit mode bits first, add/remove bones, parents etc

# testing 1..2..3..
def addBone():
    bone = arm.edit_bones.new('Bone')
    bone.head = (0,0,0)
    bone.tail = (0,0,1)
    return

def delBone( name):
    bone = arm.edit_bones[name]
    if bone is not None:
        arm.edit_bones.remove( bone)
    else:
        print( "@delBone:bone name [{0}] not found".format( name))
        raise SystemExit
        
    return

# edit mode functionality
def delUnusedBones():
    delBone( "heel.02.L")
    delBone( "heel.02.R")
    return

def repositionToe( name, side):
    bone = arm.edit_bones[ name+"."+side]
    bone.head[2] = 0
    bone.tail[2] = 0
    return

def setParentInherit( bone):
    bone.use_inherit_rotation = True
    bone.use_inherit_scale = True
    bone.use_local_location = True
    return

def posCtrlFootRoll( src, side):
    bone = arm.edit_bones[src+"."+side]
    blen = bone.length
    bone.tail[2] = bone.head[2]
    bone.length = blen
    bone.use_deform = False
    bone.roll = 0
    return bone

def createCtrlEyes():
    head = arm.edit_bones[ head_name]
    eye = arm.edit_bones[ "eye.L"] # either side will do
    ctrl = arm.edit_bones.new( "ctrlEyes")
    y_distance = head.length*2
    ctrl.use_deform = False
    ctrl.head = [ 0, eye.head[1]-y_distance, eye.head[2]]
    ctrl.tail = [ 0, eye.head[1]-y_distance, eye.head[2]+head.length/2]
    ctrl.use_connect = False
    ctrl.parent = head
    return

def createEyeTarget( side):
    head = arm.edit_bones[ head_name]
    eye = arm.edit_bones[ "eye."+side]
    eye.use_connect = False
    eye.parent = head
    tgt = arm.edit_bones.new( "eye_target."+side)
    tgt.use_deform = False
    y_distance = head.length*2
    tgt.head = [ eye.head[0], eye.head[1]-y_distance, eye.head[2]]
    tgt.tail = [ eye.head[0], eye.head[1]-y_distance, eye.head[2]+head.length/2]
    tgt.use_connect = False
    tgt.parent = arm.edit_bones["ctrlEyes"]
    return

def createToeRoll( side):
    bone = arm.edit_bones.new("toeRoll."+side)
    bone.use_deform = False
    refb = arm.edit_bones["toe."+side]
    yref = arm.edit_bones["heel.02."+side].head[1]
    bone.head = refb.head
    bone.tail = [refb.head[0], yref, refb.head[2]]
    return bone
    
def createHeelRoll( side):
    bone = arm.edit_bones.new( "heelRoll."+side)
    bone.use_deform = False
    refb = arm.edit_bones["toeRoll."+side]
    yref = arm.edit_bones["heel."+side].tail[1]
    bone.tail = refb.head
    bone.head = [ refb.tail[0], yref, refb.tail[2]]
    bone.tail = refb.tail
    return bone

def createFootRollCtrl( side):
    # we'll rename this ctrlFootRoll later, to fit with rigify
    bone = arm.edit_bones.new( "heel."+side)
    bone.use_deform = False
    refb = arm.edit_bones["shin."+side]
    heel = arm.edit_bones["heel.02."+side]
    bone.head = refb.tail
    bone.tail = [ refb.tail[0], heel.tail[1], heel.tail[2]]
    return

def repositionHeelRoll( side):
    bone = arm.edit_bones["heel.02."+side]
    # we rename heel to ctrlFootRoll later, compat rigify
    foot_roll = arm.edit_bones["heel."+side]
    toe = arm.edit_bones["toe."+side]
    mid_y = toe.head[1] + ( foot_roll.tail[1] - toe.head[1])/2
    bone.head[1] = mid_y
    bone.tail[1] = mid_y
    return

def createFootCtrl( side):    
    bone = arm.edit_bones.new( "ctrlFoot."+side)
    bone.use_deform = False
    refb = arm.edit_bones["foot."+side]
    bone.head = refb.head
    bone.tail = [refb.head[0], refb.head[1], -refb.head[2]]
    return bone

def createTorsoCtrl():
    print( "@createTorsoCtrl")
    bone = arm.edit_bones.new( "ctrlTorso")
    bone.use_deform = False
    head_ref = arm.edit_bones[hips_name]
    tail_ref = arm.edit_bones[chest_name]
    bone.head = head_ref.tail
    bone.tail = tail_ref.head
    bone.use_connect = False
    bone.parent = arm.edit_bones["ctrlRoot"]
    return

def createHipsCtrl():
    print( "@createHipsCtrl")
    bone = arm.edit_bones.new( "ctrlHips")
    bone.use_deform = False
    refb = arm.edit_bones[hips_name]
    bone.head = refb.tail
    bone.tail = refb.head
    bone.use_connect = False
    bone.parent = arm.edit_bones["ctrlTorso"]
    
    refb.use_connect = False
    refb.parent = bone
    return bone

def reparentWaistBone():
    waist = arm.edit_bones[ spine_name]
    waist.use_connect = False
    waist.use_inherit_rotation = True
    waist.parent = arm.edit_bones["ctrlTorso"]
    return

def createIkTarget( ik, ref, side):
    bn = ik+"."+side
    rn = ref+"."+side
    bone = arm.edit_bones.new( bn)
    bone.use_deform = False
    refb = arm.edit_bones[rn]
    if bone is not None and refb is not None:
        bone.head = refb.head
        bone.tail = refb.tail
        bone.roll = refb.roll
    else:
        print( "new ik target [{0}] side[{1}] failed",format( ik, side))
    return bone

def createKneePoleTarget( name, side):
    bone = arm.edit_bones.new( name+"."+side)
    bone.parent = arm.edit_bones["ctrlFoot."+side]
    bone.use_deform = False
    bone.use_connect = False
    refb = arm.edit_bones[ "shin."+side]
    bone.head = refb.head
    bone.head[1] -= refb.length
    bone.tail = [ bone.head[0], bone.head[1], bone.head[2]+bone.parent.length]
    return

def createElbowPoleTarget( name, side):
    bone = arm.edit_bones.new( name+"."+side)
    bone.parent = arm.edit_bones[chest_name] 
    bone.use_deform = False
    bone.use_connect = False
    refb = arm.edit_bones[ "forearm."+side]
    bone.head = refb.head
    bone.head[1] += refb.length
    bone.tail = [ bone.head[0], bone.head[1], bone.head[2]+refb.length]
    return

####################################################################### pose bits

def createIK( obj, src, side, sub, pole_sub):
    pose = obj.pose
    bone = pose.bones[ src+"."+side]
    cns = bone.constraints.new( 'IK')
    cns.name = sub
    cns.target = obj
    cns.subtarget = sub+"."+side
    cns.pole_target = obj
    cns.pole_subtarget = pole_sub+"."+side
    cns.pole_angle = -math.pi/2
    cns.chain_count = 2
    return

def addCopyRotHipsTorso():
    pose = ob.pose
    hips = pose.bones["ctrlHips"]
    cns = hips.constraints.new( 'COPY_ROTATION')
    cns.target = ob
    cns.subtarget = "ctrlTorso"
    cns.owner_space = 'LOCAL'
    cns.target_space = 'LOCAL'
    cns.use_offset = True
    cns.invert_y = True
    cns.invert_z = True
    return

def addCopyLocHipsTorso():
    hips = ob.pose.bones["ctrlHips"]
    cns = hips.constraints.new( 'COPY_LOCATION')
    cns.target = ob
    cns.subtarget = "ctrlTorso"
    cns.owner_space = 'LOCAL'
    cns.target_space = 'LOCAL'
    cns.use_offset = True
    cns.invert_z = True
    return

def addCopyRotWaistTorso():
    pose = ob.pose
    hips = pose.bones[spine_name]
    cns = hips.constraints.new( 'COPY_ROTATION')
    cns.target = ob
    cns.subtarget = "ctrlTorso"
    cns.owner_space = 'LOCAL'
    cns.target_space = 'LOCAL'
    cns.use_offset = True
    return
    
def addCopyRot( obj, name, side, sub):
    pose = obj.pose
    bone = pose.bones[name+"."+side]
    cns = bone.constraints.new( 'COPY_ROTATION')
    cns.name = 'Copy_Rotation'
    cns.target = obj
    cns.subtarget = sub+"."+side
    cns.owner_space = 'WORLD'
    cns.target_space = 'WORLD'
    return

def addCopyRotLocalX( obj, name, side, sub, invert_x, offset = False):
    pose = obj.pose
    bone = pose.bones[name+"."+side]
    cns = bone.constraints.new( 'COPY_ROTATION')
    cns.name = 'Copy_Rotation'
    cns.target = obj
    cns.subtarget = sub+"."+side
    cns.owner_space = 'LOCAL'
    cns.target_space = 'LOCAL'
    cns.use_x = True
    cns.use_y = False
    cns.use_z = False
    cns.invert_x = invert_x
    if offset:
        cns.use_offset = True
    return

def addLimitRotLocalX( ob, name, side):
    pose = ob.pose
    bone = pose.bones[name+"."+side]
    cns = bone.constraints.new( 'LIMIT_ROTATION')
    cns.name = 'Limit_Rotation'
    cns.owner_space = 'LOCAL'
    cns.use_limit_x = True
    cns.use_limit_y = False
    cns.use_limit_z = False
    cns.max_x = math.pi/4
    return

def addEyeTrackConstraint( side):
    pose = ob.pose
    eye = pose.bones["eye."+side]
    cns = eye.constraints.new( 'DAMPED_TRACK')
    cns.name = "damped track"
    cns.target = ob
    cns.subtarget = "eye_target."+side
    # I believe most of these are the default values
    cns.head_tail = 0
    cns.track_axis = "TRACK_Y"
    cns.owner_space = "WORLD"
    cns.target_space = "WORLD"
    return

########################################################## sides

def createFootCtrls( side):
    root = arm.edit_bones["ctrlRoot"]
    
    if pitchipoy:
        createFootRollCtrl( side)
        repositionHeelRoll( side)
        
    # foot_roll = arm.edit_bones["ctrlFootRoll."+side]
    foot_bone = createFootCtrl( side)
    foot_bone.parent = root
    foot_bone.use_connect = False
    setParentInherit( foot_bone)
    
    toe_bone = createToeRoll( side)
    heel_bone = createHeelRoll( side)
    toe_bone.use_connect = False
    toe_bone.parent = heel_bone
    setParentInherit( toe_bone)
    heel_bone.use_connect = False
    heel_bone.parent = foot_bone
    setParentInherit( heel_bone)
    return

def createFootCtrlBones():
    createFootCtrls( "L")
    createFootCtrls( "R")
    return

def createKneePoleTargets():
    createKneePoleTarget( "ikKnee", "L")
    createKneePoleTarget( "ikKnee", "R")
    return

def createElbowPoleTargets():
    createElbowPoleTarget( "ikElbow", "L")
    createElbowPoleTarget( "ikElbow", "R")
    return

def createEyeTargets():
    createCtrlEyes() # centre eye control bone
    createEyeTarget( "L")
    createEyeTarget( "R")
    return

######################################################### helpers

def createRoot():
    bone = arm.edit_bones.new( "ctrlRoot")
    bone.use_deform = False
    bref = arm.edit_bones["foot.L"]
    bone.head = [ 0, 0, 0]
    bone.tail = [ 0, 1, 0]
    bone.length = bref.length
    return

def createIkTargets():
    new_bone = createIkTarget( "ikFoot", "foot", "L")
    new_bone.parent = arm.edit_bones["toeRoll.L"]
    new_bone.use_connect = False
    setParentInherit( new_bone)
        
    new_bone = createIkTarget( "ikFoot", "foot", "R")
    new_bone.parent = arm.edit_bones["toeRoll.R"]
    new_bone.use_connect = False
    setParentInherit( new_bone)
    
    new_bone = createIkTarget( "ikHand", "hand", "L")
    new_bone.parent = arm.edit_bones[chest_name]
    new_bone.use_connect = False
    setParentInherit( new_bone)
    
    new_bone = createIkTarget( "ikHand", "hand", "R")
    new_bone.parent = arm.edit_bones[chest_name]
    new_bone.use_connect = False
    setParentInherit( new_bone)
    return

def repositionToes():
    repositionToe( "toe", "L")
    repositionToe( "toe", "R")
    return

def fixCtrlFootRolls():
    bone = posCtrlFootRoll( "heel", "L")
    bone.name = "ctrlFootRoll.L"
    bone.use_connect = False
    bone.parent = arm.edit_bones["ctrlFoot.L"]
    setParentInherit( bone)
    
    bone = posCtrlFootRoll( "heel", "R")
    bone.name = "ctrlFootRoll.R"
    bone.use_connect = False
    bone.parent = arm.edit_bones["ctrlFoot.R"]
    setParentInherit( bone)
    return

def initBones():
    createRoot()
    repositionToes()
    createTorsoCtrl()
    createHipsCtrl()
    reparentWaistBone()
    createFootCtrlBones()
    createIkTargets()
    createKneePoleTargets()
    createElbowPoleTargets()
    createEyeTargets()
    arm.edit_bones[head_name].use_inherit_rotation = False
        
    # we use heel tail for new heel roll bone head, so do this last
    fixCtrlFootRolls()
    delUnusedBones()
    
    arm.edit_bones[head_name].use_inherit_rotation = False
    return

def setupControls():
    bpy.ops.object.mode_set(mode='POSE')
    setupLegIk( "L")
    setupLegIk( "R")
    setupHandIk( "L")
    setupHandIk( "R")
    #setupTorsoControl()
    addEyeTrackConstraint( "L")
    addEyeTrackConstraint( "R")
    return

def setupLegIk( side):
    createIK( ob, "shin", side, "ikFoot", "ikKnee")
    addCopyRot( ob, "foot", side, "ikFoot")
    addCopyRotLocalX( ob, "toeRoll", side, "ctrlFootRoll", False)
    addLimitRotLocalX( ob, "toeRoll", side)
    addCopyRotLocalX( ob, "heelRoll", side, "ctrlFootRoll", True)
    addLimitRotLocalX( ob, "heelRoll", side)
    addCopyRotLocalX( ob, "toe", side, "toeRoll", False, True)
    return

def setupHandIk( side):
    createIK( ob, "forearm", side, "ikHand", "ikElbow")
    addCopyRot( ob, "hand", side, "ikHand")
    addCopyRotLocalX( ob, "f_index.02", side, "f_index.01", False)
    addCopyRotLocalX( ob, "f_index.03", side, "f_index.01", False)
    addCopyRotLocalX( ob, "f_middle.02", side, "f_middle.01", False)
    addCopyRotLocalX( ob, "f_middle.03", side, "f_middle.01", False)
    addCopyRotLocalX( ob, "f_ring.02", side, "f_ring.01", False)
    addCopyRotLocalX( ob, "f_ring.03", side, "f_ring.01", False)
    addCopyRotLocalX( ob, "f_pinky.02", side, "f_pinky.01", False)
    addCopyRotLocalX( ob, "f_pinky.03", side, "f_pinky.01", False)
    #addCopyRotLocalX( ob, "thumb.02", side, "thumb.01", False)
    addCopyRotLocalX( ob, "thumb.03", side, "thumb.02", False)
    return

def setupTorsoControl():
    addCopyRotHipsTorso()
    addCopyLocHipsTorso()
    addCopyRotWaistTorso()
    return

def setCustomShape( bone, shape):
    pose = ob.pose
    pose.bones[bone].custom_shape = bpy.data.objects[shape]
    arm.bones[bone].show_wire = True
    #pose.bones[bone].show_wire = True
    return

def setupCustomShapes():
    shapes = my_shapes
    if use_rigify_shapes:
        shapes = rigify_shapes
        
    for i in range( len(bone_names)):
        setCustomShape( bone_names[i], shapes[i])
    return

if ob.type is not None and ob.type == 'ARMATURE' :
    initBones()
    print( "bone count [{0}]".format( len( arm.edit_bones)))
    setupControls()
    if setup_custom_shapes:
        setupCustomShapes()
    #bpy.ops.object.mode_set(mode='OBJECT')
else:
    print( "missing object")
print( "finished")
