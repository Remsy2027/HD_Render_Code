import bpy
import sys
import datetime
import math

#Get Email
email = sys.argv[5]

#Get Desired Resolution
Resolution = sys.argv[6]

try:
    # Try to convert Resolution to an integer
    resolution_integer = int(Resolution)
    print("Resolution as integer:", resolution_integer)
except ValueError:
    # If ValueError occurs, it means Resolution is not a valid integer
    print("Resolution is not an integer. Converting...")

    try:
        # Try to convert Resolution to a float
        resolution_float = float(Resolution)
        # Convert the float to an integer
        resolution_integer = int(resolution_float)
        print("Resolution as integer:", resolution_integer)
    except ValueError:
        print("Invalid resolution value. Please check your input.")

# For Delete Default Objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Replace the filepath with the location of your GLB file
filepath = "Assets/GLB_Files/" + email + ".glb"

# Import the GLB file
bpy.ops.import_scene.gltf(filepath=filepath)

def create_sss_material():
    # Check if the object exists in the scene
    object_name = "TableStand001"  # Change this to your object's name
    target_object = bpy.data.objects.get(object_name)
    
    if target_object:
        # Create a new material
        sss_material = bpy.data.materials.new(name="sssmaterial")

        # Enable 'Use nodes' for shader nodes
        sss_material.use_nodes = True

        # Clear default nodes
        for node in sss_material.node_tree.nodes:
            sss_material.node_tree.nodes.remove(node)

        # Create a Principled BSDF shader node
        principled_node = sss_material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')

        # Set material properties
        principled_node.inputs["Base Color"].default_value = (1.0, 0.62, 0.29, 1.0)  # RGB value for "FF9F4B"
        principled_node.inputs["Roughness"].default_value = 0.2
        principled_node.inputs["IOR"].default_value = 2.0

        # Create a Material Output shader node
        material_output_node = sss_material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')

        # Connect Principled BSDF shader to Material Output node
        sss_material.node_tree.links.new(principled_node.outputs["BSDF"], material_output_node.inputs["Surface"])

        # Access the "Settings" section for Transmission
        sss_material.node_tree.nodes["Principled BSDF"].inputs[17].default_value = 0.5

        # Assign the material to the active object
        bpy.context.view_layer.objects.active = target_object
        target_object.data.materials.append(sss_material)

        print("sssmaterial created and assigned.")
    else:
        print(f"Object '{object_name}' not found in the scene. Material not assigned.")

# Create sssmaterial and assign it to the mesh
create_sss_material()

def modify_material(material):
    if material.use_nodes:
        # Access the existing node tree
        node_tree = material.node_tree

        # Find or create the Principled BSDF node
        principled_bsdf = node_tree.nodes.get("Principled BSDF")
        if not principled_bsdf:
            principled_bsdf = node_tree.nodes.new('ShaderNodeBsdfPrincipled')
            principled_bsdf.location = (0, 0)

        # Find or create the Transparent BSDF node
        transparent_bsdf = node_tree.nodes.get("Transparent BSDF")
        if not transparent_bsdf:
            transparent_bsdf = node_tree.nodes.new('ShaderNodeBsdfTransparent')
            transparent_bsdf.location = (0, 200)

        # Find or create the Mix Shader node
        mix_shader = node_tree.nodes.get("Mix Shader")
        if not mix_shader:
            mix_shader = node_tree.nodes.new('ShaderNodeMixShader')
            mix_shader.location = (400, 0)

        # Find or create the Geometry node
        geometry_node = node_tree.nodes.get("Geometry")
        if not geometry_node:
            geometry_node = node_tree.nodes.new('ShaderNodeNewGeometry')
            geometry_node.location = (-200, 400)

        # Connect the shaders to the mix shader node
        node_tree.links.new(principled_bsdf.outputs['BSDF'], mix_shader.inputs[1])
        node_tree.links.new(transparent_bsdf.outputs['BSDF'], mix_shader.inputs[2])

        # Connect the Geometry node to the factor input of the mix shader
        node_tree.links.new(geometry_node.outputs['Backfacing'], mix_shader.inputs['Fac'])

        # Find or create the Material Output node
        material_output = node_tree.nodes.get("Material Output")
        if not material_output:
            material_output = node_tree.nodes.new('ShaderNodeOutputMaterial')
            material_output.location = (800, 0)

        # Connect the Mix Shader node to the Material Output node
        node_tree.links.new(mix_shader.outputs['Shader'], material_output.inputs['Surface'])
    else:
        print("Material does not have a node tree.")


# Get the material names to modify
material_names = ["Theme_1", "Theme_2", "Theme_3", "Theme_4", "Theme_5", "Wall_White_Theme","White","Fern","Leaves","Palm","Foliage","Palm_Shade","Phoenix","Wall_Variant1","Main_Wall_Stone","Main_Wall_Tile","Main_Wall_Flower","Main_Wall_Wood",]

for material_name in material_names:
    material = bpy.data.materials.get(material_name)
    if material:
        modify_material(material)
        print("Material modified: {}".format(material_name))
    else:
        print("Material not found: {}".format(material_name))

# Get the sunlight object (assuming you have only one sun lamp)
sunlight = next((lamp for lamp in bpy.data.lights if lamp.type == 'SUN'), None)

if sunlight and sunlight.energy <= 0:
    # Adding Area Light
    bpy.ops.object.light_add(type='AREA', location=(0.085354, -0.433466, 2.89785))
    arealight = bpy.context.object
    arealight.scale = (3.8592, 3.8592, 3.8592)
    arealight.rotation_euler = (math.radians(0), math.radians(0), math.radians(0))
    arealight.data.energy = 0.25

# Get all the lights from the scene
lights = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']

# Increase the power of each light
for light in lights:
    light.data.energy *= 10  # Adjust the multiplication factor as desired

    # Get the light data
    light_data = light.data

    # Set the light radius to 0.25m
    light_data.shadow_soft_size = 0.05

    # Enable nodes for the light data
    light_data.use_nodes = True

    # Get the light node tree
    tree = light_data.node_tree

    # Clear existing nodes
    tree.nodes.clear()

    # Add the Blackbody node
    blackbody_node = tree.nodes.new(type='ShaderNodeBlackbody')

    # Set the desired temperature for the blackbody color
    temperature = 5500  # Adjust the temperature as desired
    blackbody_node.inputs['Temperature'].default_value = temperature

    # Add the Emission node
    emission_node = tree.nodes.new(type='ShaderNodeEmission')
    emission_node.inputs['Strength'].default_value = 10  # Set the emission strength to 10

    # Add the Surface node
    surface_node = tree.nodes.new(type='ShaderNodeOutputWorld')

    # Connect the Blackbody node output to the Emission node input
    tree.links.new(blackbody_node.outputs['Color'], emission_node.inputs['Color'])

    # Connect the Emission node output to the Surface node input
    tree.links.new(emission_node.outputs['Emission'], surface_node.inputs['Surface'])

# Find Spot lights by name
light_names = ["Cylindrical_spot_light_1", "Cylindrical_spot_light_2", "Cylindrical_spot_light_3", "Cylindrical_spot_light_4"]
lights_to_change = [bpy.data.objects[name] for name in light_names if name in bpy.data.objects]

# Set the new shadow soft size for the lights
new_shadow_soft_size = 0.05

# Change the shadow soft size for each light
for light in lights_to_change:
    if light.type == 'LIGHT':
        light.data.shadow_soft_size = new_shadow_soft_size
def create_world():
    # Check if a world already exists, if not, create one
    if bpy.context.scene.world is None:
        bpy.context.scene.world = bpy.data.worlds.new('World')

def change_hdri_image(image_path):
    create_world()

    # Get the world environment
    world = bpy.context.scene.world

    # Check the sunlight intensity
    if sunlight and sunlight.energy > 0:
        # Clear existing environment textures
        world.use_nodes = True
        node_tree = world.node_tree
        for node in node_tree.nodes:
            node_tree.nodes.remove(node)

        # Add a new Environment Texture node
        env_texture_node = node_tree.nodes.new(type='ShaderNodeTexEnvironment')
        env_texture_node.location = (0, 0)

        # Set the HDRI image path
        env_texture_node.image = bpy.data.images.load(image_path)

        # Add a Background node to connect the Environment Texture node to the Background
        bg_node = node_tree.nodes.new(type='ShaderNodeBackground')
        bg_node.location = (400, 0)

        # Connect the Environment Texture node to the Background node
        node_tree.links.new(env_texture_node.outputs['Color'], bg_node.inputs['Color'])

        # Create the "World Output" node if it doesn't exist
        if 'World Output' not in node_tree.nodes:
            world_output = node_tree.nodes.new(type='ShaderNodeOutputWorld')
            world_output.location = (800, 0)

        # Connect the Background node to the "World Output" node
        node_tree.links.new(bg_node.outputs['Background'], node_tree.nodes['World Output'].inputs['Surface'])

        # Add Window area lights
        # bpy.ops.object.light_add(type='AREA', location=(-1.91053, -0.422077, 1.7078))
        # light1 = bpy.context.object
        # light1.scale = (1.649, 1.34947, 1.2)
        # light1.rotation_euler = (math.radians(0), math.radians(-90), math.radians(0))
        # light1.data.energy = 50

        # Set the location and scale of the cube
        cube_location = (0.078756, -0.433157, 1.5)  # (X, Y, Z) coordinates
        cube_scale = (2.08481, 2.1, 1.71725)  # (X, Y, Z) scaling factors

        # Add the cube to the scene
        bpy.ops.mesh.primitive_cube_add(location=cube_location, scale=cube_scale)

        # Get the last added object (which is the cube in this case)
        cube = bpy.context.object

        # Rename the cube
        cube.name = "Volumetric_Effect"

        # Create a new material for the cube
        cube_material = bpy.data.materials.new(name="Volumetric_Material")
        cube.data.materials.append(cube_material)

        # Set the material nodes for Volume Scatter shader
        cube_material.use_nodes = True
        nodes = cube_material.node_tree.nodes
        for node in nodes:
            cube_material.node_tree.nodes.remove(node)

        # Add Volume Scatter shader node
        volume_scatter_node = nodes.new(type='ShaderNodeVolumeScatter')

        # Connect nodes
        links = cube_material.node_tree.links

        # Create Material Output node if not exists
        material_output_node = nodes.get("Material Output")
        if material_output_node is None:
            material_output_node = nodes.new(type='ShaderNodeOutputMaterial')

        # Connect Volume Scatter shader to the volume input of the Material Output node
        volume_input = material_output_node.inputs['Volume']
        if volume_input.is_linked:
            for link in volume_input.links[:]:
                cube_material.node_tree.links.remove(link)
        links.new(volume_scatter_node.outputs['Volume'], volume_input)

        # Set Density and Anisotropy values using input sockets
        density_input = volume_scatter_node.inputs['Density']
        anisotropy_input = volume_scatter_node.inputs['Anisotropy']

        # Set Density and Anisotropy values
        density_input.default_value = 0.04
        anisotropy_input.default_value = 0.2

# Example usage
image_path = "Assets/HDRI/autumn_forest_01_4k.hdr"
change_hdri_image(image_path)

# Find the camera object by type
for obj in bpy.data.objects:
    if obj.type == 'CAMERA':
        camera_obj = obj
        break

# Assign the camera object to the active scene
bpy.context.scene.camera = camera_obj

# Set the rendering engine to Cycles
bpy.context.scene.render.engine = 'CYCLES'
cycles_prefs = bpy.context.preferences.addons['cycles'].preferences
cycles_prefs.compute_device_type = 'OPTIX'
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Set resolution and samples
bpy.context.scene.render.resolution_x = 1000*resolution_integer
bpy.context.scene.render.resolution_y = 1000*resolution_integer
bpy.context.scene.cycles.samples = 100

# Enable denoising
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.cycles.denoiser = 'OPENIMAGEDENOISE'

#Performance
bpy.context.scene.cycles.debug_use_spatial_splits = True
bpy.context.scene.render.use_persistent_data = True


# Set view settings
bpy.context.scene.view_settings.look = 'AgX - High Contrast'
bpy.context.scene.view_settings.exposure = 0
bpy.context.scene.cycles.diffuse_bounces = 6
bpy.context.scene.cycles.glossy_bounces = 6
bpy.context.scene.cycles.sample_clamp_direct = 9
bpy.context.scene.cycles.sample_clamp_indirect = 9

# Enable passes
view_layer = bpy.context.view_layer
view_layer.use_pass_ambient_occlusion = True
view_layer.use_pass_shadow = True
view_layer.use_pass_emit = True

# Render the image to a file
current_datetime = datetime.datetime.now().strftime("_%Y/%d-%m/%H-%M_")
output_filename = email.split('@')[0] + current_datetime + 'Render_Image.PNG'
output_path = 'Assets/Render_Images/' + output_filename
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)

